"""
Job Control API Routes

Endpoints for pausing, resuming, and cancelling jobs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.workflow import JobManager, JobCreator, PriorityManager, ResourceManager, JobRepository
from aphrodite_logging import get_logger

router = APIRouter(prefix="/api/v1/workflow/control", tags=["workflow-control"])
logger = get_logger("aphrodite.api.workflow.control")


async def get_job_manager(session: AsyncSession = Depends(get_db_session)) -> JobManager:
    """Dependency to create job manager"""
    job_repository = JobRepository(session)
    job_creator = JobCreator(job_repository)
    priority_manager = PriorityManager(job_repository)
    resource_manager = ResourceManager()
    
    return JobManager(job_repository, job_creator, priority_manager, resource_manager)


@router.post("/{job_id}/pause")
async def pause_job(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Pause running job"""
    try:
        success = await job_manager.pause_job(job_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="Job cannot be paused (not found or not running)")
        
        logger.info(f"Paused job {job_id}")
        return {"message": "Job paused successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to pause job")


@router.post("/{job_id}/resume")
async def resume_job(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Resume paused job"""
    try:
        success = await job_manager.resume_job(job_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="Job cannot be resumed (not found or not paused)")
        
        logger.info(f"Resumed job {job_id}")
        return {"message": "Job resumed successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to resume job")


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Cancel job"""
    try:
        success = await job_manager.cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="Job cannot be cancelled (not found or already completed)")
        
        logger.info(f"Cancelled job {job_id}")
        return {"message": "Job cancelled successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to cancel job")
