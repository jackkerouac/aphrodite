"""
Progress Updater

Progress reporting and status updates for workers.
"""

from typing import Optional
from datetime import datetime, timedelta

from aphrodite_logging import get_logger
from app.services.workflow.database import JobRepository
from app.services.workflow.types import JobStatus
from app.services.workflow.progress_tracker import ProgressTracker

logger = get_logger("aphrodite.worker.progress")


class ProgressUpdater:
    """Updates job progress and estimates completion time"""
    
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo
        self.progress_tracker = ProgressTracker(job_repo)
    
    async def update_job_progress(self, 
                                 job_id: str, 
                                 completed: int, 
                                 failed: int) -> None:
        """
        Update job progress counters and estimate completion.
        
        Args:
            job_id: Job identifier
            completed: Number of completed posters
            failed: Number of failed posters
        """
        # Update progress counters
        await self.job_repo.update_job_progress(job_id, completed, failed)
        
        # Calculate and update estimated completion
        estimated_completion = await self._calculate_estimated_completion(job_id)
        if estimated_completion:
            await self.job_repo.update_job_estimated_completion(job_id, estimated_completion)
        
        # Broadcast progress update via WebSocket
        progress = await self.progress_tracker.calculate_progress(job_id)
        if progress:
            await self.progress_tracker.broadcast_progress(job_id, progress)
        
        logger.debug(f"Updated progress for job {job_id}: {completed} completed, {failed} failed")
    
    async def _calculate_estimated_completion(self, job_id: str) -> Optional[datetime]:
        """Calculate estimated completion time based on current progress"""
        job = await self.job_repo.get_job_by_id(job_id)
        if not job or not job.started_at:
            return None
        
        processed = job.completed_posters + job.failed_posters
        if processed == 0:
            return None
        
        # Calculate average time per poster
        elapsed = datetime.utcnow() - job.started_at
        avg_time_per_poster = elapsed / processed
        
        # Estimate remaining time
        remaining_posters = job.total_posters - processed
        estimated_remaining_time = avg_time_per_poster * remaining_posters
        
        return datetime.utcnow() + estimated_remaining_time
    
    async def calculate_progress_percentage(self, job_id: str) -> float:
        """Calculate current progress as percentage"""
        job = await self.job_repo.get_job_by_id(job_id)
        if not job or job.total_posters == 0:
            return 0.0
        
        processed = job.completed_posters + job.failed_posters
        return (processed / job.total_posters) * 100.0
