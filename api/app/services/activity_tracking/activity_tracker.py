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
from app.models.badge_application import BadgeApplicationModel
from app.models.poster_replacement import PosterReplacementModel
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
    
    async def log_badge_details(
        self,
        activity_id: str,
        badge_types: List[str],
        badge_settings_snapshot: Optional[Dict[str, Any]] = None,
        badge_configuration_id: Optional[str] = None,
        poster_source: Optional[str] = None,
        original_poster_path: Optional[str] = None,
        output_poster_path: Optional[str] = None,
        intermediate_files: Optional[List[str]] = None,
        badges_applied: Optional[List[Dict[str, Any]]] = None,
        badges_failed: Optional[List[Dict[str, Any]]] = None,
        final_poster_dimensions: Optional[str] = None,
        final_file_size: Optional[int] = None,
        badge_generation_time_ms: Optional[int] = None,
        poster_processing_time_ms: Optional[int] = None,
        total_processing_time_ms: Optional[int] = None,
        poster_quality_score: Optional[float] = None,
        compression_ratio: Optional[float] = None,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """
        Log detailed badge application data linked to an activity.
        
        Args:
            activity_id: The parent activity ID
            badge_types: List of badge types applied
            badge_settings_snapshot: Settings used at time of application
            badge_configuration_id: Reference to settings version
            poster_source: Source of the poster ('original', 'jellyfin', 'cached', 'uploaded')
            original_poster_path: Path to original poster used
            output_poster_path: Path to final badged poster
            intermediate_files: List of paths to intermediate files
            badges_applied: Details of each badge applied
            badges_failed: Details of any badges that failed
            final_poster_dimensions: "width x height"
            final_file_size: Final file size in bytes
            badge_generation_time_ms: Time to generate badges
            poster_processing_time_ms: Time to apply badges to poster
            total_processing_time_ms: Total time including I/O
            poster_quality_score: 0.00-1.00 quality assessment
            compression_ratio: Original vs final file size ratio
            db_session: Optional database session
        """
        try:
            # Ensure activity_id is a proper UUID object
            if isinstance(activity_id, str):
                activity_uuid = uuid.UUID(activity_id)
            else:
                activity_uuid = activity_id
            
            # Verify the activity exists before creating badge application
            if db_session:
                # Check if activity exists
                activity_check = await db_session.execute(
                    select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                )
                existing_activity = activity_check.scalar_one_or_none()
                if not existing_activity:
                    raise ValueError(f"Activity {activity_uuid} not found")
                    
                # Create the badge application with proper session management
                badge_application = BadgeApplicationModel(
                    activity_id=activity_uuid,
                    badge_types=badge_types,
                    badge_settings_snapshot=badge_settings_snapshot,
                    badge_configuration_id=badge_configuration_id,
                    poster_source=poster_source,
                    original_poster_path=original_poster_path,
                    output_poster_path=output_poster_path,
                    intermediate_files=intermediate_files or [],
                    badges_applied=badges_applied or [],
                    badges_failed=badges_failed or [],
                    final_poster_dimensions=final_poster_dimensions,
                    final_file_size=final_file_size,
                    badge_generation_time_ms=badge_generation_time_ms,
                    poster_processing_time_ms=poster_processing_time_ms,
                    total_processing_time_ms=total_processing_time_ms,
                    poster_quality_score=poster_quality_score,
                    compression_ratio=compression_ratio
                )
                
                # Add to session and commit in one transaction
                db_session.add(badge_application)
                await db_session.commit()
                self.logger.info(f"Logged badge details for activity {activity_id}")
                
            else:
                # Handle case where no session is provided
                async for db in get_db_session():
                    # Check if activity exists
                    activity_check = await db.execute(
                        select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                    )
                    existing_activity = activity_check.scalar_one_or_none()
                    if not existing_activity:
                        raise ValueError(f"Activity {activity_uuid} not found")
                        
                    badge_application = BadgeApplicationModel(
                        activity_id=activity_uuid,
                        badge_types=badge_types,
                        badge_settings_snapshot=badge_settings_snapshot,
                        badge_configuration_id=badge_configuration_id,
                        poster_source=poster_source,
                        original_poster_path=original_poster_path,
                        output_poster_path=output_poster_path,
                        intermediate_files=intermediate_files or [],
                        badges_applied=badges_applied or [],
                        badges_failed=badges_failed or [],
                        final_poster_dimensions=final_poster_dimensions,
                        final_file_size=final_file_size,
                        badge_generation_time_ms=badge_generation_time_ms,
                        poster_processing_time_ms=poster_processing_time_ms,
                        total_processing_time_ms=total_processing_time_ms,
                        poster_quality_score=poster_quality_score,
                        compression_ratio=compression_ratio
                    )
                    
                    db.add(badge_application)
                    await db.commit()
                    self.logger.info(f"Logged badge details for activity {activity_id}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to log badge details for activity {activity_id}: {e}", exc_info=True)
            raise
    
    async def log_replacement_details(
        self,
        activity_id: str,
        replacement_source: str,
        source_poster_id: Optional[str] = None,
        source_poster_url: Optional[str] = None,
        search_query: Optional[str] = None,
        search_results_count: Optional[int] = None,
        original_poster_url: Optional[str] = None,
        original_poster_cached_path: Optional[str] = None,
        original_poster_dimensions: Optional[str] = None,
        original_file_size: Optional[int] = None,
        original_poster_hash: Optional[str] = None,
        new_poster_dimensions: Optional[str] = None,
        new_file_size: Optional[int] = None,
        new_poster_hash: Optional[str] = None,
        download_time_ms: Optional[int] = None,
        upload_time_ms: Optional[int] = None,
        jellyfin_upload_success: Optional[bool] = None,
        tag_operations: Optional[Dict[str, Any]] = None,
        jellyfin_response: Optional[Dict[str, Any]] = None,
        quality_improvement_score: Optional[float] = None,
        visual_similarity_score: Optional[float] = None,
        user_rating: Optional[int] = None,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """
        Log detailed poster replacement data linked to an activity.
        
        Args:
            activity_id: The parent activity ID
            replacement_source: Source of the replacement ('tmdb', 'fanart_tv', 'manual_upload', 'local_file')
            source_poster_id: External ID from source
            source_poster_url: Original URL (if applicable)
            search_query: Query used to find replacement
            search_results_count: Number of options found
            original_poster_url: Original Jellyfin poster URL
            original_poster_cached_path: Path where original was cached
            original_poster_dimensions: "width x height"
            original_file_size: Original file size in bytes
            original_poster_hash: SHA256 hash of original
            new_poster_dimensions: "width x height"
            new_file_size: New file size in bytes
            new_poster_hash: SHA256 hash of new poster
            download_time_ms: Time to download new poster
            upload_time_ms: Time to upload to Jellyfin
            jellyfin_upload_success: Successfully uploaded to Jellyfin
            tag_operations: Tag additions/removals performed
            jellyfin_response: Jellyfin API responses
            quality_improvement_score: -1.00 to 1.00 (negative = worse)
            visual_similarity_score: 0.00-1.00 similarity to original
            user_rating: 1-5 user rating (if provided)
            db_session: Optional database session
        """
        try:
            # Ensure activity_id is a proper UUID object
            if isinstance(activity_id, str):
                activity_uuid = uuid.UUID(activity_id)
            else:
                activity_uuid = activity_id
            
            # Verify the activity exists before creating poster replacement
            if db_session:
                # Check if activity exists
                activity_check = await db_session.execute(
                    select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                )
                existing_activity = activity_check.scalar_one_or_none()
                if not existing_activity:
                    raise ValueError(f"Activity {activity_uuid} not found")
                    
                # Create the poster replacement with proper session management
                poster_replacement = PosterReplacementModel(
                    activity_id=activity_uuid,
                    replacement_source=replacement_source,
                    source_poster_id=source_poster_id,
                    source_poster_url=source_poster_url,
                    search_query=search_query,
                    search_results_count=search_results_count,
                    original_poster_url=original_poster_url,
                    original_poster_cached_path=original_poster_cached_path,
                    original_poster_dimensions=original_poster_dimensions,
                    original_file_size=original_file_size,
                    original_poster_hash=original_poster_hash,
                    new_poster_dimensions=new_poster_dimensions,
                    new_file_size=new_file_size,
                    new_poster_hash=new_poster_hash,
                    download_time_ms=download_time_ms,
                    upload_time_ms=upload_time_ms,
                    jellyfin_upload_success=jellyfin_upload_success,
                    tag_operations=tag_operations or {},
                    jellyfin_response=jellyfin_response or {},
                    quality_improvement_score=quality_improvement_score,
                    visual_similarity_score=visual_similarity_score,
                    user_rating=user_rating
                )
                
                # Add to session and commit in one transaction
                db_session.add(poster_replacement)
                await db_session.commit()
                self.logger.info(f"Logged replacement details for activity {activity_id}")
                
            else:
                # Handle case where no session is provided
                async for db in get_db_session():
                    # Check if activity exists
                    activity_check = await db.execute(
                        select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                    )
                    existing_activity = activity_check.scalar_one_or_none()
                    if not existing_activity:
                        raise ValueError(f"Activity {activity_uuid} not found")
                        
                    poster_replacement = PosterReplacementModel(
                        activity_id=activity_uuid,
                        replacement_source=replacement_source,
                        source_poster_id=source_poster_id,
                        source_poster_url=source_poster_url,
                        search_query=search_query,
                        search_results_count=search_results_count,
                        original_poster_url=original_poster_url,
                        original_poster_cached_path=original_poster_cached_path,
                        original_poster_dimensions=original_poster_dimensions,
                        original_file_size=original_file_size,
                        original_poster_hash=original_poster_hash,
                        new_poster_dimensions=new_poster_dimensions,
                        new_file_size=new_file_size,
                        new_poster_hash=new_poster_hash,
                        download_time_ms=download_time_ms,
                        upload_time_ms=upload_time_ms,
                        jellyfin_upload_success=jellyfin_upload_success,
                        tag_operations=tag_operations or {},
                        jellyfin_response=jellyfin_response or {},
                        quality_improvement_score=quality_improvement_score,
                        visual_similarity_score=visual_similarity_score,
                        user_rating=user_rating
                    )
                    
                    db.add(poster_replacement)
                    await db.commit()
                    self.logger.info(f"Logged replacement details for activity {activity_id}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to log replacement details for activity {activity_id}: {e}", exc_info=True)
            raise
    
    async def log_performance_metrics(
        self,
        activity_id: str,
        cpu_usage_percent: Optional[float] = None,
        memory_usage_mb: Optional[int] = None,
        disk_io_read_mb: Optional[float] = None,
        disk_io_write_mb: Optional[float] = None,
        network_download_mb: Optional[float] = None,
        network_upload_mb: Optional[float] = None,
        network_latency_ms: Optional[int] = None,
        stage_timings: Optional[Dict[str, float]] = None,
        bottleneck_stage: Optional[str] = None,
        error_rate: Optional[float] = None,
        throughput_items_per_second: Optional[float] = None,
        server_load_average: Optional[float] = None,
        concurrent_operations: Optional[int] = None,
        db_session: Optional[AsyncSession] = None
    ) -> None:
        """
        Log detailed performance metrics data linked to an activity.
        
        Args:
            activity_id: The parent activity ID
            cpu_usage_percent: Peak CPU usage during operation
            memory_usage_mb: Peak memory usage
            disk_io_read_mb: Disk read in MB
            disk_io_write_mb: Disk write in MB
            network_download_mb: Data downloaded
            network_upload_mb: Data uploaded
            network_latency_ms: Average network latency
            stage_timings: Breakdown of time per processing stage
            bottleneck_stage: Slowest processing stage
            error_rate: 0.00-1.00 error rate if batch operation
            throughput_items_per_second: Processing throughput
            server_load_average: System load during operation
            concurrent_operations: Other operations running simultaneously
            db_session: Optional database session
        """
        try:
            from app.models.activity_performance_metric import ActivityPerformanceMetricModel
            
            # Ensure activity_id is a proper UUID object
            if isinstance(activity_id, str):
                activity_uuid = uuid.UUID(activity_id)
            else:
                activity_uuid = activity_id
            
            # Verify the activity exists before creating performance metrics
            if db_session:
                # Check if activity exists
                activity_check = await db_session.execute(
                    select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                )
                existing_activity = activity_check.scalar_one_or_none()
                if not existing_activity:
                    raise ValueError(f"Activity {activity_uuid} not found")
                    
                # Create the performance metrics with proper session management
                performance_metrics = ActivityPerformanceMetricModel(
                    activity_id=activity_uuid,
                    cpu_usage_percent=cpu_usage_percent,
                    memory_usage_mb=memory_usage_mb,
                    disk_io_read_mb=disk_io_read_mb,
                    disk_io_write_mb=disk_io_write_mb,
                    network_download_mb=network_download_mb,
                    network_upload_mb=network_upload_mb,
                    network_latency_ms=network_latency_ms,
                    stage_timings=stage_timings or {},
                    bottleneck_stage=bottleneck_stage,
                    error_rate=error_rate,
                    throughput_items_per_second=throughput_items_per_second,
                    server_load_average=server_load_average,
                    concurrent_operations=concurrent_operations
                )
                
                # Add to session and commit in one transaction
                db_session.add(performance_metrics)
                await db_session.commit()
                self.logger.info(f"Logged performance metrics for activity {activity_id}")
                
            else:
                # Handle case where no session is provided
                async for db in get_db_session():
                    # Check if activity exists
                    activity_check = await db.execute(
                        select(MediaActivityModel).where(MediaActivityModel.id == activity_uuid)
                    )
                    existing_activity = activity_check.scalar_one_or_none()
                    if not existing_activity:
                        raise ValueError(f"Activity {activity_uuid} not found")
                        
                    performance_metrics = ActivityPerformanceMetricModel(
                        activity_id=activity_uuid,
                        cpu_usage_percent=cpu_usage_percent,
                        memory_usage_mb=memory_usage_mb,
                        disk_io_read_mb=disk_io_read_mb,
                        disk_io_write_mb=disk_io_write_mb,
                        network_download_mb=network_download_mb,
                        network_upload_mb=network_upload_mb,
                        network_latency_ms=network_latency_ms,
                        stage_timings=stage_timings or {},
                        bottleneck_stage=bottleneck_stage,
                        error_rate=error_rate,
                        throughput_items_per_second=throughput_items_per_second,
                        server_load_average=server_load_average,
                        concurrent_operations=concurrent_operations
                    )
                    
                    db.add(performance_metrics)
                    await db.commit()
                    self.logger.info(f"Logged performance metrics for activity {activity_id}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to log performance metrics for activity {activity_id}: {e}", exc_info=True)
            raise


# Global service instance
_activity_tracker: Optional[ActivityTracker] = None


def get_activity_tracker() -> ActivityTracker:
    """Get the global activity tracker instance"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker
