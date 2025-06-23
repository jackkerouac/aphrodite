"""
Batch Worker (FIXED)

Main Celery task for processing batch jobs.
Fixed to properly handle unique posters per job.
"""

from celery import Celery
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from aphrodite_logging import get_logger
from app.core.database import async_session_factory
from app.core.config import get_settings
from app.services.workflow.database import JobRepository
from app.services.workflow.types import JobStatus, PosterStatus
from .poster_processor import PosterProcessor
from .error_handler import ErrorHandler
from .progress_updater import ProgressUpdater

logger = get_logger("aphrodite.worker.batch")

# Get configuration
settings = get_settings()

# Initialize Celery app
celery_app = Celery('aphrodite_worker')
celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Windows compatibility
    worker_pool='solo',  # Use solo pool for Windows
    worker_concurrency=1,
)


@celery_app.task(bind=True)
def process_batch_job(self, job_id: str) -> Dict[str, Any]:
    """
    Main Celery task for processing batch jobs.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Processing result summary
    """
    logger.info(f"Starting batch job processing: {job_id}")
    
    # Run async processing in event loop
    return asyncio.run(_process_batch_job_async(job_id, self))


async def _process_batch_job_async(job_id: str, task_instance) -> Dict[str, Any]:
    """Async implementation of batch job processing"""
    
    # Initialize database for this task
    from app.core.database import init_db
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database in worker: {e}")
        return {"success": False, "error": f"Database initialization failed: {e}"}
    
    # Import after database initialization
    from app.core.database import async_session_factory
    
    async with async_session_factory() as db_session:
        job_repo = JobRepository(db_session)
        poster_processor = PosterProcessor()
        error_handler = ErrorHandler()
        progress_updater = ProgressUpdater(job_repo)
        
        # Get job details
        job = await job_repo.get_job_by_id(job_id)
        if not job:
            logger.error(f"Job not found: {job_id}")
            return {"success": False, "error": "Job not found"}
        
        # Update job status to processing
        await job_repo.update_job_status(job_id, JobStatus.PROCESSING)
        await job_repo.update_job_started_at(job_id, datetime.utcnow())
        
        logger.info(f"Processing {job.total_posters} posters for job {job_id}")
        
        completed = 0
        failed = 0
        
        try:
            # Process each poster
            for poster_id in job.selected_poster_ids:
                # Check if job was cancelled or paused
                current_job = await job_repo.get_job_by_id(job_id)
                if current_job.status in [JobStatus.CANCELLED.value, JobStatus.PAUSED.value]:
                    logger.info(f"Job {job_id} was {current_job.status}, stopping processing")
                    break
                
                # Update poster status to processing
                await job_repo.update_poster_status(job_id, poster_id, PosterStatus.PROCESSING)
                
                try:
                    # Process single poster
                    result = await poster_processor.process_poster(
                        poster_id=poster_id,
                        badge_types=job.badge_types,
                        job_id=job_id
                    )
                    
                    if result["success"]:
                        await job_repo.update_poster_status(
                            job_id, poster_id, PosterStatus.COMPLETED,
                            output_path=result.get("output_path")
                        )
                        completed += 1
                        
                        # Add aphrodite-overlay tag if successfully uploaded to Jellyfin
                        if result.get("uploaded_to_jellyfin", False):
                            try:
                                from app.services.tag_management_service import get_tag_management_service
                                tag_service = get_tag_management_service()
                                await tag_service.add_tag_to_items([poster_id], "aphrodite-overlay")
                                logger.debug(f"Added aphrodite-overlay tag to {poster_id}")
                            except Exception as tag_error:
                                logger.warning(f"Failed to add tag to {poster_id}: {tag_error}")
                        
                        logger.debug(f"Completed poster {poster_id}")
                    else:
                        await error_handler.handle_poster_error(
                            job_repo, job_id, poster_id, result["error"]
                        )
                        failed += 1
                        
                except Exception as e:
                    await error_handler.handle_poster_error(
                        job_repo, job_id, poster_id, str(e)
                    )
                    failed += 1
                
                # Update job progress
                await progress_updater.update_job_progress(job_id, completed, failed)
        
        except Exception as e:
            logger.error(f"Critical error in job {job_id}: {e}", exc_info=True)
            await job_repo.update_job_status(job_id, JobStatus.FAILED)
            await job_repo.update_job_error(job_id, str(e))
            return {"success": False, "error": str(e)}
        
        # Finalize job
        final_status = JobStatus.COMPLETED if failed == 0 else JobStatus.FAILED
        await job_repo.update_job_status(job_id, final_status)
        await job_repo.update_job_completed_at(job_id, datetime.utcnow())
        
        result = {
            "success": final_status == JobStatus.COMPLETED,
            "completed": completed,
            "failed": failed,
            "total": job.total_posters
        }
        
        logger.info(f"Job {job_id} finished: {result}")
        return result
