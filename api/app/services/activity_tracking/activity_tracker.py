"""
Activity Tracker Service

Core service for managing activity lifecycle (start, complete, fail).
Provides centralized tracking for all poster and media-related operations.
"""

import time
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.media_activity import MediaActivityModel
from app.core.database import get_db_session
from app.utils.version_manager import get_version
from aphrodite_logging import get_logger


class ActivityTracker:
    """Central service for tracking media activity lifecycle"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.activity_tracker", service="activity")
    
    async def start_activity(
        self,
        media_id: str,
        activity_type: str,
        initiated_by: str = "system",
        jellyfin_id: Optional[str] = None,
        activity_subtype: Optional[str] = None,
        user_id: Optional[str] = None,
        batch_job_id: Optional[str] = None,
        parent_activity_id: Optional[str] = None,
        input_parameters: Optional[Dict[str, Any]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> str:
        """
        Create a new activity record with status='processing' and return the activity_id.
        
        Args:
            media_id: ID of the media item being processed
            activity_type: Type of activity ('badge_application', 'poster_replacement', etc.)
            initiated_by: Who initiated the activity ('user', 'scheduled_job', 'batch_operation', 'api_call')
            jellyfin_id: Jellyfin ID for reference
            activity_subtype: Subtype of activity ('single_badge', 'multi_badge', etc.)
            user_id: User who initiated (if applicable)
            batch_job_id: FK to batch_jobs.id (if part of batch)
            parent_activity_id: FK to parent activity (for related operations)
            input_parameters: Original request parameters
            additional_metadata: Extensible metadata field
            db_session: Optional database session (will create one if not provided)
            
        Returns:
            str: The activity ID
        """
        activity_id = str(uuid.uuid4())
        
        try:
            # Create activity record
            activity = MediaActivityModel(
                id=activity_id,
                media_id=media_id,
                jellyfin_id=jellyfin_id,
                activity_type=activity_type,
                activity_subtype=activity_subtype,
                status='processing',
                initiated_by=initiated_by,
                user_id=user_id,
                batch_job_id=batch_job_id,
                parent_activity_id=parent_activity_id,
                started_at=datetime.now(timezone.utc),
                input_parameters=input_parameters,
                system_version=get_version(),
                additional_metadata=additional_metadata
            )
            
            # Use provided session or create a new one
            if db_session:
                db_session.add(activity)
                await db_session.commit()
                self.logger.info(f"Started activity {activity_id}: {activity_type} for media {media_id}")
            else:
                async for db in get_db_session():
                    db.add(activity)
                    await db.commit()
                    self.logger.info(f"Started activity {activity_id}: {activity_type} for media {media_id}")
                    break
            
            return activity_id
            
        except Exception as e:
            self.logger.error(f"Failed to start activity: {e}", exc_info=True)
            raise
    
    async def complete_activity(
        self,
        activity_id: str,
        success: bool,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """
        Update the activity record to status='completed', log the result, and calculate processing_duration_ms.
        
        Args:
            activity_id: The activity ID to complete
            success: Whether the activity succeeded
            result_data: Operation results, file paths, etc.
            error_message: Error details if failed
            db_session: Optional database session
        """
        try:
            completion_time = datetime.now(timezone.utc)
            
            # Update activity record
            if db_session:
                await self._update_activity_completion(
                    db_session, activity_id, success, result_data, error_message, completion_time
                )
            else:
                async for db in get_db_session():
                    await self._update_activity_completion(
                        db, activity_id, success, result_data, error_message, completion_time
                    )
                    break
            
            status = "succeeded" if success else "failed"
            self.logger.info(f"Completed activity {activity_id}: {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to complete activity {activity_id}: {e}", exc_info=True)
            raise
    
    async def fail_activity(
        self,
        activity_id: str,
        error_message: str,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """
        Update the activity record to status='failed' and log the error message.
        
        Args:
            activity_id: The activity ID to mark as failed
            error_message: Error details
            db_session: Optional database session
        """
        await self.complete_activity(
            activity_id=activity_id,
            success=False,
            error_message=error_message,
            db_session=db_session
        )
    
    async def _update_activity_completion(
        self,
        db: AsyncSession,
        activity_id: str,
        success: bool,
        result_data: Optional[Dict[str, Any]],
        error_message: Optional[str],
        completion_time: datetime
    ) -> None:
        """Internal method to update activity completion"""
        
        # Get the activity record
        result = await db.execute(
            select(MediaActivityModel).where(MediaActivityModel.id == activity_id)
        )
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise ValueError(f"Activity {activity_id} not found")
        
        # Calculate processing duration
        processing_duration = None
        if activity.started_at:
            duration_seconds = (completion_time - activity.started_at).total_seconds()
            processing_duration = int(duration_seconds * 1000)  # Convert to milliseconds
        
        # Update the record
        activity.status = 'completed'
        activity.success = success
        activity.completed_at = completion_time
        activity.processing_duration_ms = processing_duration
        activity.result_data = result_data
        activity.error_message = error_message
        
        await db.commit()
    
    async def get_activity_history(
        self,
        media_id: str,
        limit: int = 50,
        offset: int = 0,
        activity_type: Optional[str] = None,
        db_session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Get activity history for a media item.
        
        Args:
            media_id: The media ID to get history for
            limit: Maximum number of records to return
            offset: Number of records to skip
            activity_type: Optional filter by activity type
            db_session: Optional database session
            
        Returns:
            List of activity records as dictionaries
        """
        try:
            if db_session:
                return await self._query_activity_history(
                    db_session, media_id, limit, offset, activity_type
                )
            else:
                async for db in get_db_session():
                    return await self._query_activity_history(
                        db, media_id, limit, offset, activity_type
                    )
        except Exception as e:
            self.logger.error(f"Failed to get activity history for {media_id}: {e}", exc_info=True)
            return []
    
    async def _query_activity_history(
        self,
        db: AsyncSession,
        media_id: str,
        limit: int,
        offset: int,
        activity_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Internal method to query activity history"""
        
        query = select(MediaActivityModel).where(MediaActivityModel.media_id == media_id)
        
        if activity_type:
            query = query.where(MediaActivityModel.activity_type == activity_type)
        
        query = query.order_by(MediaActivityModel.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return [activity.to_dict() for activity in activities]


# Global service instance
_activity_tracker: Optional[ActivityTracker] = None


def get_activity_tracker() -> ActivityTracker:
    """Get the global activity tracker instance"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker
