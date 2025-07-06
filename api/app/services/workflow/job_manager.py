"""
Job Manager

Job lifecycle management and coordination.
"""

from typing import List, Optional, Union
from datetime import datetime
from uuid import UUID

from .types import JobStatus, BatchJobRequest
from .job_creator import JobCreator
from .priority_manager import PriorityManager
from .resource_manager import ResourceManager
from .database import JobRepository, BatchJobModel

# Import the correct Celery app from the main celery_app module
from celery_app import celery_app


class JobManager:
    """Orchestrates job lifecycle management"""
    
    def __init__(self, 
                 job_repository: JobRepository,
                 job_creator: JobCreator,
                 priority_manager: PriorityManager,
                 resource_manager: ResourceManager):
        self.job_repository = job_repository
        self.job_creator = job_creator
        self.priority_manager = priority_manager
        self.resource_manager = resource_manager
    
    async def create_job(self, 
                        user_id: str,
                        name: str,
                        poster_ids: Union[List[UUID], List[str]],
                        badge_types: List[str]) -> BatchJobModel:
        """Create new batch job and dispatch to worker"""
        
        # Convert string IDs to UUIDs if needed
        if poster_ids and isinstance(poster_ids[0], str):
            try:
                uuid_poster_ids = [UUID(str(pid)) for pid in poster_ids]
            except ValueError as e:
                raise ValueError(f"Invalid poster ID format: {e}")
        else:
            uuid_poster_ids = poster_ids
        
        # Validate request
        errors = self.job_creator.validate_job_request(uuid_poster_ids, badge_types)
        if errors:
            raise ValueError(f"Invalid job request: {', '.join(errors)}")
        
        # Create job
        job = await self.job_creator.create_batch_job(
            user_id=user_id,
            name=name,
            poster_ids=uuid_poster_ids,
            badge_types=badge_types
        )
        
        # CRITICAL: Dispatch job to Docker Celery worker
        try:
            # First, check if the task is registered
            task_name = 'app.services.workflow.workers.batch_worker.process_batch_job'
            if task_name not in celery_app.tasks:
                print(f"⚠️  Task {task_name} not found in registered tasks")
                print(f"📋 Available tasks: {list(celery_app.tasks.keys())}")
                # Try to import the task module explicitly
                try:
                    from app.services.workflow.workers.batch_worker import process_batch_job
                    print(f"✅ Task module imported successfully: {process_batch_job}")
                except Exception as import_error:
                    print(f"❌ Failed to import task module: {import_error}")
                    raise ValueError(f"Task not available: {import_error}")
            
            # Dispatch the task
            task = celery_app.send_task(task_name, args=[str(job.id)])
            print(f"Job dispatched to Docker Celery worker: {job.id} -> {task.id}")
            print(f"Task state: {task.state}")
            
            # Try to get more information about the broker connection
            try:
                inspector = celery_app.control.inspect()
                active_workers = inspector.active()
                print(f"Active workers at dispatch time: {active_workers}")
                
                # Check if workers are available to process tasks
                if not active_workers:
                    print("⚠️  WARNING: No active workers detected when dispatching job!")
                    print("This job may remain in PENDING state until a worker becomes available.")
                else:
                    print(f"✅ {len(active_workers)} worker(s) available to process jobs")
                    
            except Exception as inspect_error:
                print(f"⚠️  Could not inspect workers: {inspect_error}")
            
            # Store task_id for monitoring
            # TODO: Add task_id field to job model if needed
            
        except Exception as e:
            print(f"Failed to dispatch job {job.id}: {e}")
            import traceback
            traceback.print_exc()
            # If dispatch fails, mark job as failed
            await self.job_repository.update_job_status(str(job.id), JobStatus.FAILED)
            await self.job_repository.update_job_error(str(job.id), f"Failed to dispatch job: {e}")
            raise ValueError(f"Failed to dispatch job to worker: {e}")
        
        return job
    
    async def get_job_status(self, job_id: str) -> Optional[BatchJobModel]:
        """Get current job status"""
        return await self.job_repository.get_job_by_id(job_id)
    
    async def get_user_jobs(self, user_id: str) -> List[BatchJobModel]:
        """Get all jobs for user"""
        return await self.job_repository.get_user_jobs(user_id)
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause running job"""
        job = await self.job_repository.get_job_by_id(job_id)
        if not job or job.status != JobStatus.PROCESSING.value:
            return False
        
        return await self.job_repository.update_job_status(job_id, JobStatus.PAUSED)
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume paused job"""
        job = await self.job_repository.get_job_by_id(job_id)
        if not job or job.status != JobStatus.PAUSED.value:
            return False
        
        return await self.job_repository.update_job_status(job_id, JobStatus.QUEUED)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel job"""
        job = await self.job_repository.get_job_by_id(job_id)
        if not job or job.status in [JobStatus.COMPLETED.value, JobStatus.CANCELLED.value]:
            return False
        
        return await self.job_repository.update_job_status(job_id, JobStatus.CANCELLED)
    
    async def restart_job(self, job_id: str) -> bool:
        """Restart stuck job by re-dispatching to worker"""
        job = await self.job_repository.get_job_by_id(job_id)
        if not job:
            return False
        
        # Only restart jobs that are stuck in queued state or failed
        if job.status not in [JobStatus.QUEUED.value, JobStatus.FAILED.value]:
            return False
        
        try:
            # Reset job to queued state
            await self.job_repository.update_job_status(job_id, JobStatus.QUEUED)
            
            # Clear any previous errors
            await self.job_repository.update_job_error(job_id, None)
            
            # Re-dispatch to worker
            task_name = 'app.services.workflow.workers.batch_worker.process_batch_job'
            task = celery_app.send_task(task_name, args=[str(job.id)])
            print(f"Job re-dispatched to worker: {job.id} -> {task.id}")
            
            return True
            
        except Exception as e:
            print(f"Failed to restart job {job_id}: {e}")
            return False
