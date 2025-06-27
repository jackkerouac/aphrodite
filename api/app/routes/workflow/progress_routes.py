"""
Progress Routes

API endpoints for job progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from aphrodite_logging import get_logger
from app.core.database import get_db_session
from app.services.workflow import JobRepository, ProgressTracker

logger = get_logger("aphrodite.api.progress")

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/", response_model=dict)
async def progress_root():
    """Progress API root endpoint"""
    return {
        "success": True,
        "message": "Progress API endpoints",
        "endpoints": [
            "/{job_id}",
            "/{job_id}/posters"
        ]
    }

@router.get("/{job_id}")
async def get_job_progress(
    job_id: str,
    db_session=Depends(get_db_session)
) -> Dict[str, Any]:
    """Get current progress for a job"""
    try:
        job_repo = JobRepository(db_session)
        progress_tracker = ProgressTracker(job_repo)
        
        # Get job to verify it exists
        job = await job_repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate progress
        progress = await progress_tracker.calculate_progress(job_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not available")
        
        return {
            "job_id": job_id,
            "status": job.status,
            "progress": {
                "total_posters": progress.total_posters,
                "completed_posters": progress.completed_posters,
                "failed_posters": progress.failed_posters,
                "progress_percentage": progress.progress_percentage,
                "estimated_completion": progress.estimated_completion.isoformat() if progress.estimated_completion else None
            },
            "timing": {
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting progress for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/posters")
async def get_poster_statuses(
    job_id: str,
    db_session=Depends(get_db_session)
) -> Dict[str, Any]:
    """Get detailed status for all posters in a job"""
    try:
        job_repo = JobRepository(db_session)
        
        # Verify job exists
        job = await job_repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get poster statuses
        poster_statuses = await job_repo.get_poster_statuses(job_id)
        
        return {
            "job_id": job_id,
            "total_posters": len(poster_statuses),
            "posters": [
                {
                    "poster_id": status.poster_id,
                    "status": status.status,
                    "started_at": status.started_at.isoformat() if status.started_at else None,
                    "completed_at": status.completed_at.isoformat() if status.completed_at else None,
                    "output_path": status.output_path,
                    "error_message": status.error_message,
                    "retry_count": status.retry_count
                }
                for status in poster_statuses
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting poster statuses for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
