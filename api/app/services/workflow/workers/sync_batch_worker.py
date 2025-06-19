"""
Synchronous Batch Worker

Celery task that processes batch jobs without async/await to avoid event loop conflicts.
"""

from typing import Dict, Any
from datetime import datetime

from aphrodite_logging import get_logger
from app.services.workflow.types import JobStatus, PosterStatus
from .sync_database import SyncJobRepository
from .sync_poster_processor import SyncPosterProcessor

logger = get_logger("aphrodite.worker.sync_batch")

def process_batch_job_sync(job_id: str) -> Dict[str, Any]:
    """
    Synchronous batch job processing (no async/await)
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Processing result summary
    """
    logger.info(f"Starting sync batch job processing: {job_id}")
    
    # Initialize sync components
    job_repo = SyncJobRepository()
    poster_processor = SyncPosterProcessor()
    
    try:
        # Get job details
        job = job_repo.get_job_by_id(job_id)
        if not job:
            logger.error(f"Job not found: {job_id}")
            return {"success": False, "error": "Job not found"}
        
        # Update job status to processing
        job_repo.update_job_status(job_id, JobStatus.PROCESSING)
        job_repo.update_job_started_at(job_id, datetime.utcnow())
        
        logger.info(f"Processing {job.total_posters} posters for job {job_id}")
        
        completed = 0
        failed = 0
        
        # Process each poster
        for poster_id in job.selected_poster_ids:
            logger.debug(f"Processing poster {poster_id}")
            
            # Check if job was cancelled or paused
            current_job = job_repo.get_job_by_id(job_id)
            if current_job.status in [JobStatus.CANCELLED.value, JobStatus.PAUSED.value]:
                logger.info(f"Job {job_id} was {current_job.status}, stopping processing")
                break
            
            # Update poster status to processing
            job_repo.update_poster_status(job_id, poster_id, PosterStatus.PROCESSING)
            
            try:
                # Process single poster
                result = poster_processor.process_poster(
                    poster_id=poster_id,
                    badge_types=job.badge_types,
                    job_id=job_id
                )
                
                if result["success"]:
                    job_repo.update_poster_status(
                        job_id, poster_id, PosterStatus.COMPLETED,
                        output_path=result.get("output_path")
                    )
                    completed += 1
                    logger.debug(f"Completed poster {poster_id}")
                else:
                    job_repo.update_poster_status(
                        job_id, poster_id, PosterStatus.FAILED,
                        error_message=result["error"]
                    )
                    failed += 1
                    logger.warning(f"Failed poster {poster_id}: {result['error']}")
                    
            except Exception as e:
                job_repo.update_poster_status(
                    job_id, poster_id, PosterStatus.FAILED,
                    error_message=str(e)
                )
                failed += 1
                logger.error(f"Exception processing poster {poster_id}: {e}")
            
            # Update job progress
            job_repo.update_job_progress(job_id, completed, failed)
        
        # Finalize job
        final_status = JobStatus.COMPLETED if failed == 0 else JobStatus.FAILED
        job_repo.update_job_status(job_id, final_status)
        job_repo.update_job_completed_at(job_id, datetime.utcnow())
        
        result = {
            "success": final_status == JobStatus.COMPLETED,
            "completed": completed,
            "failed": failed,
            "total": job.total_posters,
            "job_id": job_id
        }
        
        logger.info(f"Job {job_id} finished: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Critical error in job {job_id}: {e}", exc_info=True)
        try:
            job_repo.update_job_status(job_id, JobStatus.FAILED)
            job_repo.update_job_error(job_id, str(e))
        except Exception as cleanup_error:
            logger.error(f"Failed to update job status after error: {cleanup_error}")
        
        return {
            "success": False,
            "error": str(e),
            "job_id": job_id
        }
    
    finally:
        # Clean up database connections
        try:
            job_repo.close()
        except Exception as cleanup_error:
            logger.error(f"Failed to close database connections: {cleanup_error}")
