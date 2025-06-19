"""
Notification Service

User notification system for job updates.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from aphrodite_logging import get_logger
from .types import JobStatus, ProgressInfo

logger = get_logger("aphrodite.workflow.notifications")


class NotificationService:
    """Handles user notifications for job events"""
    
    def __init__(self):
        self.notification_handlers = []
    
    async def notify_job_started(self, job_id: str, job_name: str, user_id: str) -> None:
        """Notify user that job has started processing"""
        await self._send_notification(
            user_id=user_id,
            title="Job Started",
            message=f"Processing started for '{job_name}'",
            notification_type="job_started",
            job_id=job_id
        )
    
    async def notify_job_completed(self, 
                                  job_id: str, 
                                  job_name: str, 
                                  user_id: str,
                                  completed: int,
                                  failed: int) -> None:
        """Notify user that job has completed"""
        if failed == 0:
            message = f"Successfully processed {completed} posters in '{job_name}'"
            notification_type = "job_completed"
        else:
            message = f"Job '{job_name}' completed with {completed} successes and {failed} failures"
            notification_type = "job_completed_with_errors"
        
        await self._send_notification(
            user_id=user_id,
            title="Job Completed",
            message=message,
            notification_type=notification_type,
            job_id=job_id
        )
    
    async def notify_job_failed(self, 
                               job_id: str, 
                               job_name: str, 
                               user_id: str,
                               error_message: str) -> None:
        """Notify user that job has failed"""
        await self._send_notification(
            user_id=user_id,
            title="Job Failed",
            message=f"Job '{job_name}' failed: {error_message}",
            notification_type="job_failed",
            job_id=job_id
        )
    
    async def notify_progress_milestone(self,
                                       job_id: str,
                                       job_name: str,
                                       user_id: str,
                                       progress: ProgressInfo) -> None:
        """Notify user at progress milestones (25%, 50%, 75%)"""
        percentage = progress.progress_percentage
        
        # Only notify at specific milestones
        milestones = [25, 50, 75]
        milestone = None
        for ms in milestones:
            if percentage >= ms and percentage < ms + 5:  # 5% tolerance
                milestone = ms
                break
        
        if milestone:
            await self._send_notification(
                user_id=user_id,
                title=f"Progress Update",
                message=f"'{job_name}' is {milestone}% complete ({progress.completed_posters}/{progress.total_posters})",
                notification_type="progress_milestone",
                job_id=job_id
            )
    
    async def _send_notification(self,
                                user_id: str,
                                title: str,
                                message: str,
                                notification_type: str,
                                job_id: str) -> None:
        """Send notification through available channels"""
        notification = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log notification (Phase 2 implementation)
        logger.info(f"Notification for user {user_id}: {title} - {message}")
        
        # TODO: Implement additional notification channels in Phase 3:
        # - WebSocket push notifications
        # - Email notifications
        # - Browser push notifications
        
        # For now, store in memory for potential frontend polling
        # In production, this would use a proper notification queue/database
