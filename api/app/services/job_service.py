"""
Job Processing Service

Handles background job creation, management, and status tracking.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime
import asyncio

from app.core.database import get_db_session
from app.models import ProcessingJobModel, MediaItemModel
from app.core.config import get_settings
from aphrodite_logging import get_logger
from shared.types import (
    ProcessingJob, ProcessingStatus, MediaType, 
    generate_id, generate_short_id
)


class JobService:
    """Service for managing background processing jobs"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("aphrodite.service.job", service="job")
        self.active_jobs: Dict[str, asyncio.Task] = {}
    
    async def create_processing_job(
        self,
        db: AsyncSession,
        media_id: str,
        job_type: str = "poster_processing",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[ProcessingJob]:
        """Create a new processing job"""
        try:
            # For library scans, we don't need to verify media item exists
            if job_type != "library_scan":
                # Verify media item exists
                media_result = await db.execute(
                    select(MediaItemModel).where(MediaItemModel.id == media_id)
                )
                media_item = media_result.scalar_one_or_none()
                
                if not media_item:
                    self.logger.error(f"Media item not found: {media_id}")
                    return None
                
                # Check for existing pending/processing jobs
                existing_job = await self._get_active_job_for_media(db, media_id, job_type)
                if existing_job:
                    self.logger.warning(f"Job already exists for media {media_id}: {existing_job.id}")
                    return self._model_to_pydantic(existing_job)
            
            # Create new job
            job_id = generate_id()
            job = ProcessingJobModel(
                id=job_id,
                media_id=media_id,
                job_type=job_type,
                status=ProcessingStatus.PENDING,
                parameters=parameters or {},
                created_at=datetime.utcnow()
            )
            
            db.add(job)
            await db.commit()
            
            self.logger.info(f"Created job {job_id} for media {media_id}")
            return self._model_to_pydantic(job)
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error creating job for media {media_id}: {e}")
            return None
    
    async def _get_active_job_for_media(
        self,
        db: AsyncSession,
        media_id: str,
        job_type: str
    ) -> Optional[ProcessingJobModel]:
        """Check for existing active job for media item"""
        result = await db.execute(
            select(ProcessingJobModel).where(
                and_(
                    ProcessingJobModel.media_id == media_id,
                    ProcessingJobModel.job_type == job_type,
                    ProcessingJobModel.status.in_([
                        ProcessingStatus.PENDING,
                        ProcessingStatus.QUEUED,
                        ProcessingStatus.PROCESSING
                    ])
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_job_by_id(self, db: AsyncSession, job_id: str) -> Optional[ProcessingJob]:
        """Get job by ID"""
        try:
            result = await db.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.id == job_id)
            )
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_pydantic(model)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting job {job_id}: {e}")
            return None
    
    async def get_jobs(
        self,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        media_id: Optional[str] = None
    ) -> Tuple[List[ProcessingJob], int]:
        """Get paginated list of jobs with media information"""
        try:
            # Build query with join to get media information
            query = select(ProcessingJobModel, MediaItemModel).join(
                MediaItemModel, ProcessingJobModel.media_id == MediaItemModel.id, isouter=True
            )
            count_query = select(func.count(ProcessingJobModel.id))
            
            # Add filters
            filters = []
            if status:
                filters.append(ProcessingJobModel.status == status)
            if media_id:
                filters.append(ProcessingJobModel.media_id == media_id)
            
            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Add pagination and ordering
            offset = (page - 1) * per_page
            query = query.order_by(desc(ProcessingJobModel.created_at)).offset(offset).limit(per_page)
            
            # Execute query
            result = await db.execute(query)
            job_and_media_pairs = result.all()
            
            # Convert to Pydantic models with media info
            jobs = []
            for job_model, media_model in job_and_media_pairs:
                job = self._model_to_pydantic(job_model)
                # Add media title to job if available
                if media_model:
                    job.title = media_model.title
                    job.media_name = media_model.title
                else:
                    # Fallback if no media found
                    job.title = f"Job {job_model.id[:8]}"
                    job.media_name = f"Job {job_model.id[:8]}"
                jobs.append(job)
            
            self.logger.debug(f"Retrieved {len(jobs)} jobs (page {page})")
            return jobs, total
            
        except Exception as e:
            self.logger.error(f"Error getting jobs: {e}")
            return [], 0
    
    async def update_job_status(
        self,
        db: AsyncSession,
        job_id: str,
        status: ProcessingStatus,
        progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        """Update job status and progress"""
        try:
            result_query = await db.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.id == job_id)
            )
            job = result_query.scalar_one_or_none()
            
            if not job:
                self.logger.error(f"Job not found: {job_id}")
                return None
            
            # Update fields
            job.status = status
            job.updated_at = datetime.utcnow()
            
            if progress is not None:
                job.progress = progress
            
            if result is not None:
                job.result = result
            
            if error_message is not None:
                job.error_message = error_message
            
            # Set timing fields
            if status == ProcessingStatus.PROCESSING and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                job.completed_at = datetime.utcnow()
            
            await db.commit()
            
            self.logger.info(f"Updated job {job_id}: {status}")
            return self._model_to_pydantic(job)
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error updating job {job_id}: {e}")
            return None
    
    async def queue_job(self, db: AsyncSession, job_id: str) -> bool:
        """Queue a job for processing"""
        try:
            # Update job status to queued
            job = await self.update_job_status(db, job_id, ProcessingStatus.QUEUED)
            if not job:
                return False
            
            # Start background processing task
            task = asyncio.create_task(self._process_job_background(job_id))
            self.active_jobs[job_id] = task
            
            self.logger.info(f"Queued job {job_id} for processing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error queuing job {job_id}: {e}")
            return False
    
    async def _process_job_background(self, job_id: str):
        """Background task to process a job"""
        try:
            async with get_db_session() as db:
                # Get fresh job data
                job = await self.get_job_by_id(db, job_id)
                if not job:
                    self.logger.error(f"Job not found for processing: {job_id}")
                    return
                
                # Update to processing status
                await self.update_job_status(db, job_id, ProcessingStatus.PROCESSING, progress=0.0)
                
                # Process based on job type
                if job.job_type == "poster_processing":
                    await self._process_poster_job(db, job)
                elif job.job_type == "library_scan":
                    await self._process_library_scan_job(db, job)
                else:
                    await self.update_job_status(
                        db, job_id, ProcessingStatus.FAILED,
                        error_message=f"Unknown job type: {job.job_type}"
                    )
                
        except Exception as e:
            self.logger.error(f"Error processing job {job_id}: {e}")
            async with get_db_session() as db:
                await self.update_job_status(
                    db, job_id, ProcessingStatus.FAILED,
                    error_message=str(e)
                )
        finally:
            # Remove from active jobs
            self.active_jobs.pop(job_id, None)
    
    async def _process_poster_job(self, db: AsyncSession, job: ProcessingJob):
        """Process a poster enhancement job"""
        from app.services.media_service import get_media_service
        
        try:
            media_service = get_media_service()
            
            # Get media item
            media_item = await media_service.get_media_by_id(db, job.media_id)
            if not media_item:
                await self.update_job_status(
                    db, job.id, ProcessingStatus.FAILED,
                    error_message="Media item not found"
                )
                return
            
            # Update progress
            await self.update_job_status(db, job.id, ProcessingStatus.PROCESSING, progress=0.2)
            
            # Download and cache poster if not already cached
            if not media_item.poster_url and media_item.jellyfin_id:
                poster_url = await media_service.download_and_cache_poster(
                    media_item.id, media_item.jellyfin_id
                )
                if poster_url:
                    await media_service.update_poster_url(db, media_item.id, poster_url)
            
            # Update progress
            await self.update_job_status(db, job.id, ProcessingStatus.PROCESSING, progress=0.6)
            
            # TODO: Apply badges (Phase 2 Week 4)
            # For now, just simulate processing
            await asyncio.sleep(2)
            
            # Complete job
            await self.update_job_status(
                db, job.id, ProcessingStatus.COMPLETED,
                progress=1.0,
                result={"poster_processed": True, "media_id": media_item.id}
            )
            
            self.logger.info(f"Completed poster processing for media {media_item.id}")
            
        except Exception as e:
            await self.update_job_status(
                db, job.id, ProcessingStatus.FAILED,
                error_message=str(e)
            )
    
    async def _process_library_scan_job(self, db: AsyncSession, job: ProcessingJob):
        """Process a library scan job"""
        from app.services.media_service import get_media_service
        
        try:
            media_service = get_media_service()
            
            # Perform library scan
            total_found, new_items, errors = await media_service.scan_jellyfin_library(db)
            
            # Complete job
            result = {
                "total_found": total_found,
                "new_items": new_items,
                "errors": errors
            }
            
            status = ProcessingStatus.COMPLETED if not errors else ProcessingStatus.FAILED
            await self.update_job_status(
                db, job.id, status,
                progress=1.0,
                result=result,
                error_message="; ".join(errors) if errors else None
            )
            
            self.logger.info(f"Completed library scan: {new_items} new items")
            
        except Exception as e:
            await self.update_job_status(
                db, job.id, ProcessingStatus.FAILED,
                error_message=str(e)
            )
    
    def _model_to_pydantic(self, model: ProcessingJobModel) -> ProcessingJob:
        """Convert SQLAlchemy model to Pydantic model"""
        return ProcessingJob(
            id=model.id,
            media_id=model.media_id,
            status=ProcessingStatus(model.status),
            progress=model.progress,
            job_type=model.job_type,
            parameters=model.parameters or {},
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            result=model.result,
            error_message=model.error_message,
            retry_count=model.retry_count
        )
    
    async def cancel_job(self, db: AsyncSession, job_id: str) -> bool:
        """Cancel a job"""
        try:
            # Cancel background task if running
            task = self.active_jobs.get(job_id)
            if task and not task.done():
                task.cancel()
                self.active_jobs.pop(job_id, None)
            
            # Update job status
            job = await self.update_job_status(db, job_id, ProcessingStatus.CANCELLED)
            return job is not None
            
        except Exception as e:
            self.logger.error(f"Error cancelling job {job_id}: {e}")
            return False


# Global service instance
_job_service: Optional[JobService] = None

def get_job_service() -> JobService:
    """Get global Job service instance"""
    global _job_service
    if _job_service is None:
        _job_service = JobService()
    return _job_service
