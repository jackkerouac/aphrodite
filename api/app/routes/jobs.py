"""
Job Management Routes

API endpoints for managing background processing jobs.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.job_service import get_job_service
from shared.types import BaseResponse, ProcessingJob, CreateJobRequest, JobStatusResponse
from aphrodite_logging import get_logger

router = APIRouter()

@router.get("/", response_model=List[ProcessingJob])
async def list_jobs(
    status: Optional[str] = None,
    media_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    """List processing jobs with optional filters"""
    logger = get_logger("aphrodite.api.jobs.list", service="api")
    job_service = get_job_service()
    
    logger.info(f"Listing jobs: status={status}, page={page}, per_page={per_page}")
    
    try:
        jobs, total = await job_service.get_jobs(
            db, page=page, per_page=per_page, 
            status=status, media_id=media_id
        )
        return jobs
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get status of a specific job"""
    logger = get_logger("aphrodite.api.jobs.get", service="api", job_id=job_id)
    job_service = get_job_service()
    
    logger.info(f"Getting job status: {job_id}")
    
    try:
        job = await job_service.get_job_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            job=job,
            message="Job status retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=JobStatusResponse)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new processing job"""
    logger = get_logger("aphrodite.api.jobs.create", service="api")
    job_service = get_job_service()
    
    logger.info(f"Creating job: type={request.job_type}, media_count={len(request.media_ids)}")
    
    try:
        if not request.media_ids:
            raise HTTPException(status_code=400, detail="At least one media ID required")
        
        # For now, create job for the first media item
        # TODO: Support batch job creation
        media_id = request.media_ids[0]
        
        job = await job_service.create_processing_job(
            db,
            media_id=media_id,
            job_type=request.job_type,
            parameters=request.parameters
        )
        
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        # Queue the job for processing
        await job_service.queue_job(db, job.id)
        
        return JobStatusResponse(
            job=job,
            message="Job created and queued successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Cancel a running job"""
    logger = get_logger("aphrodite.api.jobs.cancel", service="api", job_id=job_id)
    job_service = get_job_service()
    
    logger.info(f"Cancelling job: {job_id}")
    
    try:
        success = await job_service.cancel_job(db, job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
        
        return BaseResponse(message=f"Job {job_id} cancelled successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a completed job"""
    logger = get_logger("aphrodite.api.jobs.delete", service="api", job_id=job_id)
    
    # TODO: Implement job deletion from database
    logger.info(f"Deleting job: {job_id}")
    
    return BaseResponse(message=f"Job {job_id} deletion not yet implemented")
