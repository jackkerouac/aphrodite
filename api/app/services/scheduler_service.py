"""
Scheduler Service

Manages automatic execution of scheduled tasks based on cron expressions.
Integrates with the existing job system for poster processing.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db_session
from app.models.schedules import ScheduleModel, ScheduleExecutionModel
from app.services.jellyfin_service import get_jellyfin_service
from app.services.job_service import get_job_service
from aphrodite_logging import get_logger


class SchedulerService:
    """Service for managing scheduled tasks and automatic execution"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.service.scheduler", service="scheduler")
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.check_interval = 60  # Check every minute
        
    async def start(self):
        """Start the scheduler daemon"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
            
        self.logger.info("Starting scheduler service")
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        """Stop the scheduler daemon"""
        if not self.running:
            return
            
        self.logger.info("Stopping scheduler service")
        self.running = False
        
        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
                
        self.scheduler_task = None
        
    async def _scheduler_loop(self):
        """Main scheduler loop that checks for due schedules"""
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                await self._check_and_execute_due_schedules()
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
                
        self.logger.info("Scheduler loop stopped")
        
    async def _check_and_execute_due_schedules(self):
        """Check for schedules that are due to run and execute them"""
        try:
            # Use the async generator correctly
            db_gen = get_db_session()
            db = await db_gen.__anext__()
            
            try:
                # Get all enabled schedules
                stmt = select(ScheduleModel).where(ScheduleModel.enabled == True)
                result = await db.execute(stmt)
                schedules = result.scalars().all()
                
                current_time = datetime.now(timezone.utc)
                
                for schedule in schedules:
                    try:
                        if await self._is_schedule_due(db, schedule, current_time):
                            self.logger.info(f"Schedule {schedule.name} ({schedule.id}) is due for execution")
                            await self._execute_schedule(db, schedule)
                            
                    except Exception as e:
                        self.logger.error(f"Error checking schedule {schedule.id}: {e}", exc_info=True)
                        
            finally:
                await db.close()
                        
        except Exception as e:
            self.logger.error(f"Error checking due schedules: {e}", exc_info=True)
            
    async def _is_schedule_due(self, db: AsyncSession, schedule: ScheduleModel, current_time: datetime) -> bool:
        """Check if a schedule is due to run based on its cron expression"""
        try:
            # Create croniter instance
            cron = croniter(schedule.cron_expression, current_time)
            
            # Get the previous run time that should have occurred
            prev_run_time = cron.get_prev(datetime)
            
            # Check if we have an execution for this schedule around the previous run time
            # Look for executions within the last check interval + buffer
            time_buffer = self.check_interval + 30  # 30 second buffer
            earliest_time = prev_run_time.replace(second=0, microsecond=0)
            latest_time = current_time
            
            stmt = select(ScheduleExecutionModel).where(
                and_(
                    ScheduleExecutionModel.schedule_id == schedule.id,
                    ScheduleExecutionModel.created_at >= earliest_time,
                    ScheduleExecutionModel.created_at <= latest_time
                )
            )
            result = await db.execute(stmt)
            recent_execution = result.scalar_one_or_none()
            
            # If no recent execution found, this schedule is due
            is_due = recent_execution is None
            
            if is_due:
                self.logger.debug(f"Schedule {schedule.name} is due - last run should have been at {prev_run_time}")
            
            return is_due
            
        except Exception as e:
            self.logger.error(f"Error checking if schedule {schedule.id} is due: {e}")
            return False
            
    async def _execute_schedule(self, db: AsyncSession, schedule: ScheduleModel):
        """Execute a schedule by creating jobs for target libraries"""
        try:
            # Create execution record
            execution = ScheduleExecutionModel(
                schedule_id=schedule.id,
                status="pending",
                started_at=datetime.now(timezone.utc)
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            
            self.logger.info(f"Created execution {execution.id} for schedule {schedule.name}")
            
            # Update execution to processing
            execution.status = "processing"
            await db.commit()
            
            # Process the schedule execution
            await self._process_schedule_execution(db, schedule, execution)
            
        except Exception as e:
            self.logger.error(f"Error executing schedule {schedule.id}: {e}", exc_info=True)
            # Update execution status to failed if it exists
            try:
                if 'execution' in locals():
                    execution.status = "failed"
                    execution.error_message = str(e)
                    execution.completed_at = datetime.now(timezone.utc)
                    await db.commit()
            except:
                pass
                
    async def _process_schedule_execution(self, db: AsyncSession, schedule: ScheduleModel, execution: ScheduleExecutionModel):
        """Process a schedule execution by creating jobs for poster enhancement"""
        try:
            jellyfin_service = get_jellyfin_service()
            job_service = get_job_service()
            
            total_items = 0
            processed_items = 0
            failed_items = 0
            job_ids = []
            
            # Process each target library
            for library_id in schedule.target_libraries:
                try:
                    self.logger.info(f"Processing library {library_id} for schedule {schedule.name}")
                    
                    # Get library items from Jellyfin
                    items = await jellyfin_service.get_library_items(library_id)
                    library_total = len(items)
                    total_items += library_total
                    
                    self.logger.info(f"Found {library_total} items in library {library_id}")
                    
                    # Create jobs for each item based on reprocess_all setting
                    for item in items:
                        try:
                            jellyfin_id = item.get('Id')
                            item_name = item.get('Name', 'Unknown')
                            
                            if not jellyfin_id:
                                continue
                                
                            # Check if we should process this item
                            should_process = schedule.reprocess_all
                            
                            if not should_process:
                                # Only process if not already processed with these badge types
                                # For now, we'll process all items (TODO: add tracking)
                                should_process = True
                                
                            if should_process:
                                # Create processing job
                                job = await job_service.create_processing_job(
                                    db=db,
                                    media_id=jellyfin_id,
                                    job_type="scheduled_poster_processing",
                                    parameters={
                                        "badge_types": schedule.badge_types,
                                        "schedule_id": str(schedule.id),
                                        "execution_id": str(execution.id),
                                        "library_id": library_id,
                                        "item_name": item_name
                                    }
                                )
                                
                                if job:
                                    job_ids.append(job.id)
                                    # Queue the job for processing
                                    await job_service.queue_job(db, job.id)
                                    processed_items += 1
                                    self.logger.debug(f"Created job {job.id} for item {item_name}")
                                else:
                                    failed_items += 1
                                    self.logger.warning(f"Failed to create job for item {item_name}")
                            
                        except Exception as e:
                            failed_items += 1
                            self.logger.error(f"Error processing item {item.get('Id', 'unknown')}: {e}")
                            
                except Exception as e:
                    self.logger.error(f"Error processing library {library_id}: {e}")
                    
            # Update execution with results
            execution.status = "completed" if failed_items == 0 else "failed"
            execution.completed_at = datetime.now(timezone.utc)
            execution.items_processed = {
                "total_items": total_items,
                "processed_items": processed_items,
                "failed_items": failed_items,
                "job_ids": job_ids,
                "badge_types": schedule.badge_types,
                "libraries": schedule.target_libraries
            }
            
            if failed_items > 0:
                execution.error_message = f"Failed to process {failed_items} out of {total_items} items"
                
            await db.commit()
            
            self.logger.info(f"Schedule execution {execution.id} completed: {processed_items} jobs created, {failed_items} failed")
            
        except Exception as e:
            self.logger.error(f"Error processing schedule execution {execution.id}: {e}", exc_info=True)
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            await db.commit()
            
    async def execute_schedule_manually(self, schedule_id: str) -> Optional[str]:
        """Manually execute a schedule and return execution ID"""
        try:
            # Use the async generator correctly
            db_gen = get_db_session()
            db = await db_gen.__anext__()
            
            try:
                # Get the schedule
                stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
                result = await db.execute(stmt)
                schedule = result.scalar_one_or_none()
                
                if not schedule:
                    self.logger.error(f"Schedule not found: {schedule_id}")
                    return None
                    
                self.logger.info(f"Manually executing schedule {schedule.name} ({schedule_id})")
                
                # Execute the schedule
                await self._execute_schedule(db, schedule)
                
                # Get the latest execution ID for this schedule
                stmt = select(ScheduleExecutionModel).where(
                    ScheduleExecutionModel.schedule_id == schedule_id
                ).order_by(ScheduleExecutionModel.created_at.desc()).limit(1)
                result = await db.execute(stmt)
                execution = result.scalar_one_or_none()
                
                return str(execution.id) if execution else None
                
            finally:
                await db.close()
                
        except Exception as e:
            self.logger.error(f"Error manually executing schedule {schedule_id}: {e}", exc_info=True)
            return None


# Global service instance
_scheduler_service: Optional[SchedulerService] = None

def get_scheduler_service() -> SchedulerService:
    """Get global Scheduler service instance"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
