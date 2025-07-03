"""
Job Repository

Database operations for batch jobs.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime

from .models import BatchJobModel, PosterProcessingStatusModel
from ..types import JobStatus, JobPriority, BatchJobRequest, PosterStatus


class JobRepository:
    """Database operations for batch jobs"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_batch_job(self, user_id: str, request: BatchJobRequest) -> BatchJobModel:
        """Create new batch job"""
        job = BatchJobModel(
            user_id=user_id,
            name=request.name,
            source=request.source.value,
            total_posters=len(request.poster_ids),
            priority=request.priority.value,
            badge_types=request.badge_types,
            selected_poster_ids=request.poster_ids  # No need to convert since they're already strings
        )
        
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job
    
    async def get_job_by_id(self, job_id: str) -> Optional[BatchJobModel]:
        """Get job by ID"""
        result = await self.session.execute(
            select(BatchJobModel).where(BatchJobModel.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_jobs(self, user_id: str, status: Optional[JobStatus] = None) -> List[BatchJobModel]:
        """Get jobs for user, optionally filtered by status"""
        query = select(BatchJobModel).where(BatchJobModel.user_id == user_id)
        
        if status:
            query = query.where(BatchJobModel.status == status.value)
        
        query = query.order_by(BatchJobModel.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update job status"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(status=status.value)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_next_queued_job(self) -> Optional[BatchJobModel]:
        """Get next queued job by priority"""
        result = await self.session.execute(
            select(BatchJobModel)
            .where(BatchJobModel.status == JobStatus.QUEUED.value)
            .order_by(BatchJobModel.priority, BatchJobModel.created_at)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update_job_started_at(self, job_id: str, started_at: datetime) -> bool:
        """Update job started timestamp"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(started_at=started_at)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_job_completed_at(self, job_id: str, completed_at: datetime) -> bool:
        """Update job completed timestamp"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(completed_at=completed_at)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_job_progress(self, job_id: str, completed: int, failed: int) -> bool:
        """Update job progress counters"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(completed_posters=completed, failed_posters=failed)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_job_estimated_completion(self, job_id: str, estimated_completion: datetime) -> bool:
        """Update estimated completion time"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(estimated_completion=estimated_completion)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_job_error(self, job_id: str, error_message: str) -> bool:
        """Update job error message"""
        result = await self.session.execute(
            update(BatchJobModel)
            .where(BatchJobModel.id == job_id)
            .values(error_summary=error_message)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def create_poster_status(self, job_id: str, poster_id: str) -> PosterProcessingStatusModel:
        """Create poster status record"""
        status = PosterProcessingStatusModel(
            batch_job_id=job_id,
            poster_id=poster_id,
            status=PosterStatus.PENDING.value
        )
        self.session.add(status)
        await self.session.commit()
        await self.session.refresh(status)
        return status
    
    async def update_poster_status(self, job_id: str, poster_id: str, status: str, 
                                 output_path: Optional[str] = None, 
                                 error_message: Optional[str] = None) -> bool:
        """Update poster processing status"""
        values = {"status": status}
        
        if status == PosterStatus.PROCESSING.value:
            values["started_at"] = datetime.utcnow()
        elif status in [PosterStatus.COMPLETED.value, PosterStatus.FAILED.value]:
            values["completed_at"] = datetime.utcnow()
            if output_path:
                values["output_path"] = output_path
            if error_message:
                values["error_message"] = error_message
        
        result = await self.session.execute(
            update(PosterProcessingStatusModel)
            .where(and_(
                PosterProcessingStatusModel.batch_job_id == job_id,
                PosterProcessingStatusModel.poster_id == poster_id
            ))
            .values(**values)
        )
        
        # If no existing record, create one
        if result.rowcount == 0:
            await self.create_poster_status(job_id, poster_id)
            result = await self.session.execute(
                update(PosterProcessingStatusModel)
                .where(and_(
                    PosterProcessingStatusModel.batch_job_id == job_id,
                    PosterProcessingStatusModel.poster_id == poster_id
                ))
                .values(**values)
            )
        
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_poster_status(self, job_id: str, poster_id: str) -> Optional[PosterProcessingStatusModel]:
        """Get poster status by job and poster ID"""
        result = await self.session.execute(
            select(PosterProcessingStatusModel)
            .where(and_(
                PosterProcessingStatusModel.batch_job_id == job_id,
                PosterProcessingStatusModel.poster_id == poster_id
            ))
        )
        return result.scalar_one_or_none()
    
    async def get_poster_statuses(self, job_id: str) -> List[PosterProcessingStatusModel]:
        """Get all poster statuses for a job"""
        result = await self.session.execute(
            select(PosterProcessingStatusModel)
            .where(PosterProcessingStatusModel.batch_job_id == job_id)
            .order_by(PosterProcessingStatusModel.poster_id)
        )
        return result.scalars().all()
    
    async def update_poster_retry(self, job_id: str, poster_id: str, retry_count: int) -> bool:
        """Update poster retry count"""
        result = await self.session.execute(
            update(PosterProcessingStatusModel)
            .where(and_(
                PosterProcessingStatusModel.batch_job_id == job_id,
                PosterProcessingStatusModel.poster_id == poster_id
            ))
            .values(retry_count=retry_count)
        )
        await self.session.commit()
        return result.rowcount > 0
