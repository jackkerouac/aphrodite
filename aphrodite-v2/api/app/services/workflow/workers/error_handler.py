"""
Error Handler

Error recovery and retry logic for failed poster processing.
"""

from typing import Optional
from datetime import datetime

from aphrodite_logging import get_logger
from app.services.workflow.database import JobRepository
from app.services.workflow.types import PosterStatus

logger = get_logger("aphrodite.worker.error")


class ErrorHandler:
    """Handles poster processing errors and retries"""
    
    MAX_RETRIES = 3
    
    async def handle_poster_error(self,
                                 job_repo: JobRepository,
                                 job_id: str,
                                 poster_id: str,
                                 error_message: str) -> bool:
        """
        Handle poster processing error with retry logic.
        
        Args:
            job_repo: Job repository instance
            job_id: Parent job ID
            poster_id: Failed poster ID
            error_message: Error description
            
        Returns:
            True if retry should be attempted, False if poster should be marked failed
        """
        logger.warning(f"Poster {poster_id} failed in job {job_id}: {error_message}")
        
        # Get current retry count
        poster_status = await job_repo.get_poster_status(job_id, poster_id)
        if not poster_status:
            # Create initial status record
            await job_repo.create_poster_status(job_id, poster_id)
            retry_count = 0
        else:
            retry_count = poster_status.retry_count
        
        # Check if we should retry
        if retry_count < self.MAX_RETRIES:
            # Increment retry count and reset to pending
            await job_repo.update_poster_retry(job_id, poster_id, retry_count + 1)
            await job_repo.update_poster_status(job_id, poster_id, PosterStatus.PENDING)
            logger.info(f"Poster {poster_id} will be retried (attempt {retry_count + 1}/{self.MAX_RETRIES})")
            return True
        else:
            # Max retries reached, mark as failed
            await job_repo.update_poster_status(
                job_id, poster_id, PosterStatus.FAILED,
                error_message=error_message
            )
            logger.error(f"Poster {poster_id} failed permanently after {self.MAX_RETRIES} retries")
            return False
    
    def categorize_error(self, error_message: str) -> str:
        """Categorize error for better handling"""
        error_lower = error_message.lower()
        
        if "file not found" in error_lower or "no such file" in error_lower:
            return "file_missing"
        elif "permission" in error_lower or "access denied" in error_lower:
            return "permission_error"
        elif "memory" in error_lower or "out of memory" in error_lower:
            return "memory_error"
        elif "timeout" in error_lower:
            return "timeout_error"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_error"
        else:
            return "unknown_error"
    
    def is_retryable_error(self, error_message: str) -> bool:
        """Determine if error type should be retried"""
        category = self.categorize_error(error_message)
        
        # Don't retry file missing or permission errors
        non_retryable = ["file_missing", "permission_error"]
        return category not in non_retryable
