"""
Job Manager

Job lifecycle management and coordination.
"""

from typing import List, Optional
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
                        poster_ids: List[UUID],
                        badge_types: List[str]) -> BatchJobModel:
        """Create new batch job and dispatch to worker"""
        
        # Validate request
        errors = self.job_creator.validate_job_request(poster_ids, badge_types)
        if errors:
            raise ValueError(f"Invalid job request: {', '.join(errors)}")
        
        # Create job
        job = await self.job_creator.create_batch_job(
            user_id=user_id,
            name=name,
            poster_ids=poster_ids,
            badge_types=badge_types
        )
        
        # CRITICAL: Dispatch job to Docker Celery worker
        try:
            task = celery_app.send_task('app.services.workflow.workers.batch_worker.process_batch_job', args=[str(job.id)])
            print(f"Job dispatched to Docker Celery worker: {job.id} -> {task.id}")
            # TODO: Store task_id for monitoring
        except Exception as e:
            print(f"Failed to dispatch job {job.id}: {e}")
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
