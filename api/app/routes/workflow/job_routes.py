"""
Job Management API Routes

Endpoints for job creation, status, and management.
"""

from typing import List, Optional, Union, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db_session
from app.services.workflow import (
    JobManager, JobCreator, PriorityManager, ResourceManager,
    JobRepository, BatchJobRequest, BatchJobModel, ProgressTracker
)
from aphrodite_logging import get_logger

router = APIRouter(prefix="/workflow/jobs", tags=["workflow"])
logger = get_logger("aphrodite.api.workflow.jobs")


async def get_job_manager(session: AsyncSession = Depends(get_db_session)) -> JobManager:
    """Dependency to create job manager with all dependencies"""
    try:
        job_repository = JobRepository(session)
        job_creator = JobCreator(job_repository)
        priority_manager = PriorityManager(job_repository)
        resource_manager = ResourceManager()
        
        return JobManager(job_repository, job_creator, priority_manager, resource_manager)
    except Exception as e:
        logger.error(f"Failed to create job manager: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to initialize job manager")


@router.post("/batch", response_model=dict)
async def create_batch_job(
    request: BatchJobRequest,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Create new batch processing job(s) - automatically splits large batches"""
    try:
        logger.info(f"Received batch job request: {request.dict()}")
        logger.info(f"Creating batch job: {request.name} with {len(request.poster_ids)} posters")
        
        # Debug the poster IDs being received
        logger.info(f"Poster IDs received: {request.poster_ids[:5]}{'...' if len(request.poster_ids) > 5 else ''}")
        
        # Validate that poster IDs are not empty
        if not request.poster_ids:
            logger.error("No poster IDs provided in batch job request")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No poster IDs provided")
        
        # Validate that poster IDs are valid strings after conversion
        invalid_ids = []
        for poster_id in request.poster_ids:
            if not poster_id or not isinstance(poster_id, str) or len(poster_id.strip()) == 0:
                invalid_ids.append(poster_id)
        
        if invalid_ids:
            logger.error(f"Invalid poster IDs found: {invalid_ids}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid poster IDs: {invalid_ids}")
        
        # Handle large batches by splitting them
        MAX_POSTERS_PER_JOB = 1000
        total_posters = len(request.poster_ids)
        
        if total_posters <= MAX_POSTERS_PER_JOB:
            # Single job for small batches
            job = await job_manager.create_job(
                user_id=request.user_id,
                name=request.name, 
                poster_ids=request.poster_ids, 
                badge_types=request.badge_types
            )
            
            logger.info(f"Created batch job {job.id} successfully")
            logger.info(f"Job stored with {len(job.selected_poster_ids)} poster IDs: {job.selected_poster_ids[:3]}{'...' if len(job.selected_poster_ids) > 3 else ''}")
            return {
                "job_id": job.id,
                "name": job.name,
                "status": job.status,
                "total_posters": job.total_posters,
                "created_at": job.created_at.isoformat()
            }
        else:
            # Split into multiple jobs for large batches
            num_jobs = (total_posters + MAX_POSTERS_PER_JOB - 1) // MAX_POSTERS_PER_JOB
            logger.info(f"Large batch detected ({total_posters} posters), splitting into {num_jobs} jobs")
            
            created_jobs = []
            for job_index in range(num_jobs):
                start_idx = job_index * MAX_POSTERS_PER_JOB
                end_idx = min(start_idx + MAX_POSTERS_PER_JOB, total_posters)
                batch_poster_ids = request.poster_ids[start_idx:end_idx]
                
                job_name = f"{request.name} (Batch {job_index + 1}/{num_jobs})"
                
                job = await job_manager.create_job(
                    user_id=request.user_id,
                    name=job_name,
                    poster_ids=batch_poster_ids,
                    badge_types=request.badge_types
                )
                
                created_jobs.append({
                    "job_id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "total_posters": job.total_posters,
                    "created_at": job.created_at.isoformat(),
                    "batch_number": job_index + 1
                })
                
                logger.info(f"Created batch job {job.id} ({job_index + 1}/{num_jobs}) for {len(batch_poster_ids)} posters")
            
            logger.info(f"Successfully created {len(created_jobs)} jobs for {total_posters} total posters")
            return {
                "split_into_multiple_jobs": True,
                "total_jobs_created": len(created_jobs),
                "total_posters": total_posters,
                "jobs": created_jobs
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except ValueError as e:
        logger.warning(f"Invalid job request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create batch job: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Failed to create job")


@router.get("/{job_id}", response_model=dict)
async def get_job_status(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Get job status and progress"""
    try:
        job = await job_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                              detail="Job not found")
        
        progress_percentage = 0.0
        if job.total_posters > 0:
            progress_percentage = (job.completed_posters / job.total_posters) * 100
        
        return {
            "job_id": job.id,
            "name": job.name,
            "status": job.status,
            "progress": {
                "total_posters": job.total_posters,
                "completed_posters": job.completed_posters,
                "failed_posters": job.failed_posters,
                "progress_percentage": progress_percentage
            },
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to get job status")


@router.get("/", response_model=list)
async def get_user_jobs(
    user_id: str = "default_user",  # TODO: Get from auth
    job_manager: JobManager = Depends(get_job_manager)
):
    """Get all jobs for user"""
    try:
        jobs = await job_manager.get_user_jobs(user_id)
        
        return [
            {
                "job_id": job.id,
                "name": job.name,
                "status": job.status,
                "total_posters": job.total_posters,
                "completed_posters": job.completed_posters,
                "failed_posters": job.failed_posters,
                "badge_types": job.badge_types,  # Add badge_types to response
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user jobs: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to get jobs")


class ProgressBroadcastRequest(BaseModel):
    """Request model for progress broadcast"""
    total_posters: int
    completed_posters: int
    failed_posters: int
    progress_percentage: float
    estimated_completion: Optional[str] = None
    current_poster: Optional[str] = None


@router.post("/broadcast-progress/{job_id}")
async def broadcast_progress(
    job_id: str,
    progress_data: ProgressBroadcastRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Broadcast progress update via WebSocket - called by worker"""
    try:
        logger.info(f"Broadcasting progress for job {job_id}: {progress_data.dict()}")
        
        # Create progress tracker and broadcast
        job_repository = JobRepository(session)
        progress_tracker = ProgressTracker(job_repository)
        
        # Import the progress info type
        from app.services.workflow.types import ProgressInfo
        
        # Create progress info object
        progress_info = ProgressInfo(
            total_posters=progress_data.total_posters,
            completed_posters=progress_data.completed_posters,
            failed_posters=progress_data.failed_posters,
            progress_percentage=progress_data.progress_percentage,
            estimated_completion=progress_data.estimated_completion,
            current_poster=progress_data.current_poster
        )
        
        # Broadcast to WebSocket connections
        await progress_tracker.broadcast_progress(job_id, progress_info)
        
        logger.info(f"Successfully broadcast progress for job {job_id}")
        return {"success": True, "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Failed to broadcast progress for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to broadcast progress")
