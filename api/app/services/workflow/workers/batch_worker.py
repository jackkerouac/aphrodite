"""
Batch Worker (FIXED)

Main Celery task for processing batch jobs.
Fixed to properly handle unique posters per job.
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from aphrodite_logging import get_logger
from app.core.database import async_session_factory
from app.services.workflow.database import JobRepository
from app.services.workflow.types import JobStatus, PosterStatus
from app.services.diagnostics.batch_debug_logger import BatchDebugLogger
from .poster_processor import PosterProcessor
from .error_handler import ErrorHandler
from .progress_updater import ProgressUpdater

logger = get_logger("aphrodite.worker.batch")


# Import Celery app for task decorator
from celery_app import celery_app

@celery_app.task(name='app.services.workflow.workers.batch_worker.process_batch_job', bind=False)
def process_batch_job(job_id: str) -> Dict[str, Any]:
    """
    Main Celery task for processing batch jobs.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Processing result summary
    """
    logger.info(f"Starting batch job processing: {job_id}")
    
    # Create new event loop for this worker task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(_process_batch_job_async(job_id))
    finally:
        loop.close()


async def _process_batch_job_async(job_id: str) -> Dict[str, Any]:
    """Async implementation of batch job processing"""
    
    # Create fresh database engine and session factory for worker
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.config import get_settings
    import asyncio
    
    settings = get_settings()
    
    # Get database URL with proper error handling
    try:
        database_url = settings.get_database_url()
        logger.info(f"Worker using database URL: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")
    except Exception as e:
        logger.error(f"Failed to get database URL: {e}")
        return {"success": False, "error": f"Database configuration error: {e}"}
    
    # Create new engine specifically for this worker task with retries
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            worker_engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "server_settings": {
                        "application_name": "aphrodite_worker",
                        "jit": "off"
                    }
                }
            )
            
            # Test the connection
            from sqlalchemy import text
            async with worker_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info(f"Worker database connection successful on attempt {attempt + 1}")
            break
            
        except Exception as e:
            logger.warning(f"Worker database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying database connection in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"All database connection attempts failed for worker")
                return {"success": False, "error": f"Database connection failed: {e}"}
    
    # Create session factory
    session_factory = async_sessionmaker(
        worker_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    try:
        async with session_factory() as db_session:
            job_repo = JobRepository(db_session)
            poster_processor = PosterProcessor()
            error_handler = ErrorHandler()
            progress_updater = ProgressUpdater(job_repo)
            
            # Initialize debug logger for this job
            debug_logger = BatchDebugLogger(job_id)
            
            # Get job details
            job = await job_repo.get_job_by_id(job_id)
            if not job:
                logger.error(f"Job not found: {job_id}")
                return {"success": False, "error": "Job not found"}
            
            # Debug the poster IDs being processed
            logger.info(f"Job {job_id} details:")
            logger.info(f"  - Total posters: {job.total_posters}")
            logger.info(f"  - Badge types: {job.badge_types}")
            logger.info(f"  - Selected poster IDs: {job.selected_poster_ids[:5]}{'...' if len(job.selected_poster_ids) > 5 else ''}")
            
            # Validate that we have poster IDs
            if not job.selected_poster_ids:
                error_msg = "No poster IDs found in job"
                logger.error(error_msg)
                await job_repo.update_job_status(job_id, JobStatus.FAILED)
                await job_repo.update_job_error(job_id, error_msg)
                return {"success": False, "error": error_msg}
            
            # Update job status to processing
            await job_repo.update_job_status(job_id, JobStatus.PROCESSING)
            await job_repo.update_job_started_at(job_id, datetime.utcnow())
            
            logger.info(f"📋 Processing {job.total_posters} posters for job {job_id}")
            logger.info(f"📋 Selected poster IDs: {job.selected_poster_ids}")
            
            completed = 0
            failed = 0
            
            try:
                # Process each poster with robust error handling
                for i, poster_id in enumerate(job.selected_poster_ids):
                    try:
                        logger.info(f"Processing poster {poster_id} ({i + 1}/{job.total_posters})")
                        
                        # Debug logging: Start poster processing
                        await debug_logger.log_poster_processing_start(poster_id, job.badge_types)
                        
                        # Check if job was cancelled or paused
                        current_job = await job_repo.get_job_by_id(job_id)
                        if current_job.status in [JobStatus.CANCELLED.value, JobStatus.PAUSED.value]:
                            logger.info(f"Job {job_id} was {current_job.status}, stopping processing")
                            break
                        
                        # Update poster status to processing
                        await job_repo.update_poster_status(job_id, poster_id, PosterStatus.PROCESSING)
                        
                        try:
                            # Process single poster with progress tracking and debug logging
                            result = await poster_processor.process_poster(
                                poster_id=poster_id,
                                badge_types=job.badge_types,
                                job_id=job_id,
                                db_session=db_session,
                                progress_tracker=progress_updater.progress_tracker,
                                debug_logger=debug_logger
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
                                        logger.info(f"Attempting to add aphrodite-overlay tag to {poster_id}")
                                        from app.services.tag_management_service import get_tag_management_service
                                        tag_service = get_tag_management_service()
                                        await tag_service.add_tag_to_items([poster_id], "aphrodite-overlay")
                                        logger.info(f"✅ Successfully added aphrodite-overlay tag to {poster_id}")
                                    except Exception as tag_error:
                                        logger.error(f"❌ Failed to add tag to {poster_id}: {tag_error}", exc_info=True)
                                else:
                                    logger.warning(f"Skipping tag addition for {poster_id} - not uploaded to Jellyfin")
                                
                                logger.info(f"✅ Completed poster {poster_id} successfully")
                                # Debug logging: Success
                                await debug_logger.log_poster_processing_end(poster_id, True)
                            else:
                                error_msg = result["error"]
                                logger.error(f"❌ Failed to process poster {poster_id}: {error_msg}")
                                # Debug logging: Failure
                                await debug_logger.log_poster_processing_end(poster_id, False, error_msg)
                                await error_handler.handle_poster_error(
                                    job_repo, job_id, poster_id, error_msg
                                )
                                failed += 1
                                
                        except Exception as poster_exception:
                            error_msg = str(poster_exception)
                            logger.error(f"❌ Exception processing poster {poster_id}: {error_msg}", exc_info=True)
                            # Debug logging: Exception
                            await debug_logger.log_poster_processing_end(poster_id, False, error_msg)
                            await error_handler.handle_poster_error(
                                job_repo, job_id, poster_id, error_msg
                            )
                            failed += 1
                        
                        # Update job progress after each poster
                        try:
                            await progress_updater.update_job_progress(job_id, completed, failed)
                            logger.info(f"📊 Progress updated: {completed + failed}/{job.total_posters} posters processed")
                        except Exception as progress_error:
                            logger.warning(f"Failed to update progress: {progress_error}")
                        
                        # Add a small delay between posters to prevent overwhelming the system
                        if i < len(job.selected_poster_ids) - 1:  # Don't delay after the last poster
                            await asyncio.sleep(0.1)
                        
                    except Exception as loop_exception:
                        logger.error(f"🚨 CRITICAL: Exception in main processing loop for poster {poster_id}: {loop_exception}", exc_info=True)
                        # Try to update status and continue with next poster
                        try:
                            await job_repo.update_poster_status(job_id, poster_id, PosterStatus.FAILED, error_message=str(loop_exception))
                            failed += 1
                            await debug_logger.log_poster_processing_end(poster_id, False, str(loop_exception))
                        except Exception as status_error:
                            logger.error(f"Failed to update status for failed poster {poster_id}: {status_error}")
                        
                        # Continue processing the next poster
                        logger.info(f"🔄 Continuing to next poster despite error with {poster_id}")
                        continue
                
                logger.info(f"📋 Batch processing completed: {completed} successful, {failed} failed out of {job.total_posters} total")
                logger.info(f"📋 Processing loop finished normally - all {len(job.selected_poster_ids)} posters were attempted")
            
            except Exception as critical_error:
                logger.error(f"🚨 CRITICAL ERROR in job {job_id}: {critical_error}", exc_info=True)
                try:
                    await job_repo.update_job_status(job_id, JobStatus.FAILED)
                    await job_repo.update_job_error(job_id, str(critical_error))
                except Exception as status_update_error:
                    logger.error(f"Failed to update job status after critical error: {status_update_error}")
                return {"success": False, "error": str(critical_error)}
            
            # Finalize job
            final_status = JobStatus.COMPLETED if failed == 0 else JobStatus.FAILED
            await job_repo.update_job_status(job_id, final_status)
            await job_repo.update_job_completed_at(job_id, datetime.utcnow())
            
            # Generate debug summary if debug mode was enabled
            debug_summary = await debug_logger.generate_debug_summary()
            
            result = {
                "success": final_status == JobStatus.COMPLETED,
                "completed": completed,
                "failed": failed,
                "total": job.total_posters,
                "debug_summary": debug_summary if debug_summary.get("debug_enabled") else None
            }
            
            logger.info(f"Job {job_id} finished: {result}")
            return result
            
    finally:
        # Clean up the worker engine
        await worker_engine.dispose()
