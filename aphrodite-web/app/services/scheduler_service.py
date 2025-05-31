import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import pytz
import uuid
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing scheduled jobs using APScheduler."""
    
    def __init__(self, base_dir=None):
        """Initialize the scheduler service."""
        self.scheduler = None
        self.is_running = False
        
        # Set up base directory for job history storage
        if base_dir is None:
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                self.base_dir = Path('/app')
            else:
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
        else:
            self.base_dir = Path(base_dir)
        
        # Create scheduler data directory
        self.scheduler_dir = self.base_dir / 'data' / 'scheduler'
        self.scheduler_dir.mkdir(parents=True, exist_ok=True)
        
        # Job history file
        self.job_history_file = self.scheduler_dir / 'job_history.json'
        
        # Load job history
        self.job_history = self._load_job_history()
        
        logger.info(f"Scheduler service initialized with base directory: {self.base_dir}")
    
    def start(self):
        """Start the scheduler."""
        if self.scheduler is not None:
            logger.warning("Scheduler is already running")
            return
        
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(max_workers=1)  # Limit to 1 concurrent job
        }
        
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.UTC
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler is not None:
            self.scheduler.shutdown(wait=True)
            self.scheduler = None
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def add_schedule(self, schedule_config):
        """Add a new schedule."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        # Generate unique ID if not provided
        schedule_id = schedule_config.get('id', str(uuid.uuid4()))
        
        # Validate required fields
        if not schedule_config.get('cron'):
            raise ValueError("Schedule must have a cron expression")
        
        if not schedule_config.get('processing_options'):
            raise ValueError("Schedule must have processing options")
        
        # Create cron trigger
        try:
            cron_parts = schedule_config['cron'].split()
            if len(cron_parts) != 5:
                raise ValueError("Cron expression must have 5 parts")
            
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4],
                timezone=pytz.timezone(schedule_config.get('timezone', 'UTC'))
            )
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}")
        
        # Add job to scheduler
        job = self.scheduler.add_job(
            func=self._execute_processing_job,
            trigger=trigger,
            id=schedule_id,
            name=schedule_config.get('name', schedule_id),
            args=[schedule_config],
            replace_existing=True
        )
        
        # Update schedule config with next run time
        schedule_config['id'] = schedule_id
        schedule_config['next_run'] = job.next_run_time.isoformat() if job.next_run_time else None
        schedule_config['last_run'] = None
        schedule_config['created_at'] = datetime.now(pytz.UTC).isoformat()
        
        logger.info(f"Added schedule '{schedule_id}' with next run: {schedule_config['next_run']}")
        
        return schedule_config
    
    def remove_schedule(self, schedule_id):
        """Remove a schedule."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        try:
            self.scheduler.remove_job(schedule_id)
            logger.info(f"Removed schedule '{schedule_id}'")
            return True
        except Exception as e:
            logger.error(f"Error removing schedule '{schedule_id}': {e}")
            return False
    
    def pause_schedule(self, schedule_id):
        """Pause a schedule."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        try:
            self.scheduler.pause_job(schedule_id)
            logger.info(f"Paused schedule '{schedule_id}'")
            return True
        except Exception as e:
            logger.error(f"Error pausing schedule '{schedule_id}': {e}")
            return False
    
    def resume_schedule(self, schedule_id):
        """Resume a schedule."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        try:
            self.scheduler.resume_job(schedule_id)
            logger.info(f"Resumed schedule '{schedule_id}'")
            return True
        except Exception as e:
            logger.error(f"Error resuming schedule '{schedule_id}': {e}")
            return False
    
    def get_schedules(self):
        """Get all current schedules."""
        if not self.is_running:
            return []
        
        schedules = []
        for job in self.scheduler.get_jobs():
            schedule_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending
            }
            schedules.append(schedule_info)
        
        return schedules
    
    def run_schedule_now(self, schedule_id):
        """Manually trigger a schedule to run now."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        try:
            job = self.scheduler.get_job(schedule_id)
            if job is None:
                raise ValueError(f"Schedule '{schedule_id}' not found")
            
            # Trigger the job immediately
            self.scheduler.modify_job(schedule_id, next_run_time=datetime.now(pytz.UTC))
            logger.info(f"Manually triggered schedule '{schedule_id}'")
            return True
        except Exception as e:
            logger.error(f"Error triggering schedule '{schedule_id}': {e}")
            return False
    
    def get_status(self):
        """Get scheduler status."""
        return {
            'running': self.is_running,
            'scheduler_state': str(self.scheduler.state) if self.scheduler else 'STOPPED',
            'job_count': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'timezone': str(pytz.UTC)
        }
    
    def _execute_processing_job(self, schedule_config):
        """Execute a processing job."""
        schedule_id = schedule_config.get('id', 'unknown')
        
        logger.info(f"Starting scheduled job '{schedule_id}'")
        
        start_time = datetime.now(pytz.UTC)
        
        try:
            # Import workflow manager functions
            from app.services.workflow_manager import add_workflow, get_workflow, get_workflow_status
            import time
            
            # Extract processing options
            processing_options = schedule_config.get('processing_options', {})
            
            # Get target directories/libraries
            target_directories = processing_options.get('target_directories', [])
            if not target_directories:
                # If no specific directories, we'll need to get all libraries
                # For now, we'll create a placeholder workflow that indicates all libraries
                target_directories = ['all']
            
            # Convert badge settings to badgeTypes format
            badge_types = []
            if processing_options.get('audio_badges', True):
                badge_types.append('audio')
            if processing_options.get('resolution_badges', True):
                badge_types.append('resolution')
            if processing_options.get('review_badges', True):
                badge_types.append('review')
            
            # Build workflow options
            workflow_options = {
                'libraryIds': target_directories,
                'badgeTypes': badge_types,
                'skipUpload': False,  # Always upload for scheduled jobs
                'skipProcessed': not processing_options.get('force_refresh', False),
                'limit': processing_options.get('limit'),
                'retries': processing_options.get('retries', 3)
            }
            
            # Add workflow to the queue
            workflow_id = add_workflow('library_batch', workflow_options)
            
            logger.info(f"Created workflow {workflow_id} for scheduled job '{schedule_id}'")
            
            # Wait for workflow to complete (with timeout)
            timeout = 3600  # 1 hour timeout
            start_wait = time.time()
            
            while time.time() - start_wait < timeout:
                # Check workflow status
                workflow = get_workflow(workflow_id)
                
                if workflow is None:
                    raise Exception(f"Workflow {workflow_id} not found")
                
                status = workflow.get('status', 'Unknown')
                
                if status in ['Success', 'Completed', 'Failed']:
                    break
                
                # Wait before checking again
                time.sleep(30)  # Check every 30 seconds
            else:
                # Timeout occurred
                raise Exception(f"Workflow {workflow_id} timed out after {timeout} seconds")
            
            # Get final workflow result
            final_workflow = get_workflow(workflow_id)
            final_status = final_workflow.get('status', 'Unknown')
            
            success = final_status in ['Success', 'Completed']
            result = {
                'workflow_id': workflow_id,
                'workflow_status': final_status,
                'workflow_result': final_workflow.get('result', {})
            }
            
            # Record execution
            self._record_job_execution(schedule_id, start_time, success, result)
            
            if success:
                logger.info(f"Scheduled job '{schedule_id}' completed successfully")
            else:
                logger.error(f"Scheduled job '{schedule_id}' failed with status: {final_status}")
            
        except Exception as e:
            # Record failed execution
            self._record_job_execution(schedule_id, start_time, False, str(e))
            
            logger.error(f"Scheduled job '{schedule_id}' failed: {e}")
            raise
    
    def _job_executed(self, event):
        """Handle job execution event."""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """Handle job error event."""
        logger.error(f"Job {event.job_id} failed with exception: {event.exception}")
    
    def _record_job_execution(self, schedule_id, start_time, success, result):
        """Record job execution in history."""
        end_time = datetime.now(pytz.UTC)
        duration = (end_time - start_time).total_seconds()
        
        execution_record = {
            'schedule_id': schedule_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'success': success,
            'result': result
        }
        
        # Add to history (keep last 50 executions)
        self.job_history.append(execution_record)
        if len(self.job_history) > 50:
            self.job_history = self.job_history[-50:]
        
        # Save to file
        self._save_job_history()
    
    def _load_job_history(self):
        """Load job history from file."""
        if self.job_history_file.exists():
            try:
                with open(self.job_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading job history: {e}")
        
        return []
    
    def _save_job_history(self):
        """Save job history to file."""
        try:
            with open(self.job_history_file, 'w') as f:
                json.dump(self.job_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving job history: {e}")
    
    def get_job_history(self, schedule_id=None, limit=None):
        """Get job execution history."""
        history = self.job_history
        
        # Filter by schedule_id if provided
        if schedule_id:
            history = [record for record in history if record.get('schedule_id') == schedule_id]
        
        # Apply limit if provided
        if limit:
            history = history[-limit:]
        
        return history
