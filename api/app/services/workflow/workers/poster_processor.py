"""
Poster Processor (FIXED)

Individual poster processing wrapper for workers - Fixed to properly handle unique posters.
"""

from typing import Dict, Any, List
from pathlib import Path
import uuid
import asyncio
import tempfile
import os

from aphrodite_logging import get_logger
from app.services.badge_processing.pipeline import UniversalBadgeProcessor
from app.services.badge_processing.types import SingleBadgeRequest, ProcessingMode
from app.services.jellyfin_service import get_jellyfin_service
from app.services.workflow.types import PosterStatus
from app.services.poster_management import StorageManager
from app.services.tag_management_service import get_tag_management_service

logger = get_logger("aphrodite.worker.poster")


class PosterProcessor:
    """Processes individual posters within batch jobs"""
    
    def __init__(self):
        self.badge_processor = UniversalBadgeProcessor()
        self.jellyfin_service = get_jellyfin_service()
        self.storage_manager = StorageManager()
    
    async def process_poster(self, 
                           poster_id: str, 
                           badge_types: List[str],
                           job_id: str,
                           db_session,
                           progress_tracker=None,
                           debug_logger=None) -> Dict[str, Any]:
        """
        Process single poster with badges.
        
        Args:
            poster_id: Jellyfin item ID for the poster
            badge_types: List of badge types to apply
            job_id: Parent job identifier
            db_session: Database session for badge processing
            
        Returns:
            Processing result with success status and output path
        """
        logger.debug(f"Processing poster {poster_id} for job {job_id}")
        
        # Emit progress update: starting poster processing
        if progress_tracker:
            await progress_tracker.update_poster_status(
                job_id=job_id,
                poster_id=poster_id,
                status=PosterStatus.PROCESSING.value
            )
        
        temp_poster_path = None
        
        try:
            # Download the specific poster from Jellyfin with retry logic
            logger.debug(f"Downloading poster from Jellyfin for {poster_id}")
            
            # Debug logging: Log session state before download
            if debug_logger:
                await debug_logger.log_session_state(self.jellyfin_service)
            
            # Retry logic for poster download to handle transient HTTP 400 errors
            max_retries = 3
            retry_delay = 1.0  # Start with 1 second delay
            poster_data = None
            
            for attempt in range(max_retries):
                try:
                    # Debug logging: Log attempt details
                    if debug_logger:
                        await debug_logger.log_request_attempt(poster_id, attempt + 1, {
                            "action": "download_poster",
                            "retry_delay": retry_delay,
                            "max_retries": max_retries
                        })
                    poster_data = await self.jellyfin_service.download_poster(poster_id, debug_logger)
                    if poster_data:
                        logger.debug(f"Successfully downloaded poster for {poster_id} on attempt {attempt + 1}")
                        break
                    else:
                        logger.warning(f"No poster data returned for {poster_id} on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying poster download for {poster_id} in {retry_delay}s")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                except Exception as download_error:
                    logger.warning(f"Download attempt {attempt + 1} failed for {poster_id}: {download_error}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying poster download for {poster_id} in {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise  # Re-raise on final attempt
            
            if not poster_data:
                error_msg = f"Failed to download poster for Jellyfin item after {max_retries} attempts: {poster_id}"
                logger.error(error_msg)
                
                # Emit progress update: failed to download
                if progress_tracker:
                    await progress_tracker.update_poster_status(
                        job_id=job_id,
                        poster_id=poster_id,
                        status=PosterStatus.FAILED.value,
                        error_message=error_msg
                    )
                
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Cache the original poster before processing for restore functionality
            try:
                cached_original_path = self.storage_manager.cache_original_poster(poster_data, poster_id)
                logger.debug(f"Successfully cached original poster for {poster_id}: {cached_original_path}")
            except Exception as cache_error:
                logger.warning(f"Failed to cache original poster for {poster_id}: {cache_error}")
                # Don't fail the whole operation if caching fails, but log the issue
            
            # Create a temporary path for processing using the StorageManager
            temp_poster_path = self.storage_manager.create_preview_output_path(f"{poster_id}.jpg")
            with open(temp_poster_path, 'wb') as temp_file:
                temp_file.write(poster_data)
            
            logger.debug(f"Downloaded poster for {poster_id} to {temp_poster_path}")
            
            # Generate output path
            output_path = self.storage_manager.create_processed_output_path(f"{poster_id}.jpg", job_id)
            
            # Create badge processing request for V2 pipeline
            request = SingleBadgeRequest(
                poster_path=temp_poster_path,
                badge_types=badge_types,
                output_path=output_path,
                use_demo_data=False,  # Use real Jellyfin metadata
                jellyfin_id=poster_id
            )
            
            # Process poster using V2 pipeline with batch mode context
            logger.debug(f"Processing poster {poster_id} with V2 pipeline - badges: {badge_types}")
            result = await self.badge_processor.process_single(request, db_session)
            
            if result.success and result.results:
                poster_result = result.results[0]
                
                # Upload processed poster back to Jellyfin and add aphrodite-overlay tag
                upload_success = False
                if poster_result.output_path and os.path.exists(poster_result.output_path):
                    try:
                        upload_success = await self.jellyfin_service.upload_poster_image(
                            poster_id, 
                            poster_result.output_path
                        )
                        if upload_success:
                            # Add aphrodite-overlay tag to mark as processed
                            await self._add_aphrodite_tag(poster_id)
                            logger.debug(f"Successfully uploaded processed poster to Jellyfin for {poster_id}")
                            
                            # Emit progress update: completed successfully
                            if progress_tracker:
                                await progress_tracker.update_poster_status(
                                    job_id=job_id,
                                    poster_id=poster_id,
                                    status=PosterStatus.COMPLETED.value,
                                    output_path=poster_result.output_path
                                )
                        else:
                            logger.warning(f"Failed to upload processed poster to Jellyfin for {poster_id}")
                            
                            # Emit progress update: upload failed
                            if progress_tracker:
                                await progress_tracker.update_poster_status(
                                    job_id=job_id,
                                    poster_id=poster_id,
                                    status=PosterStatus.FAILED.value,
                                    error_message="Failed to upload to Jellyfin"
                                )
                    except Exception as upload_error:
                        logger.error(f"Error uploading poster to Jellyfin for {poster_id}: {upload_error}")
                
                return {
                    "success": True,
                    "output_path": poster_result.output_path,
                    "applied_badges": poster_result.applied_badges,
                    "uploaded_to_jellyfin": upload_success
                }
            else:
                error_msg = result.error or "Unknown processing error"
                logger.error(f"Badge processing failed for {poster_id}: {error_msg}")
                
                # Emit progress update: processing failed
                if progress_tracker:
                    await progress_tracker.update_poster_status(
                        job_id=job_id,
                        poster_id=poster_id,
                        status=PosterStatus.FAILED.value,
                        error_message=error_msg
                    )
                
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing poster {poster_id}: {e}", exc_info=True)
            
            # Emit progress update: exception occurred
            if progress_tracker:
                await progress_tracker.update_poster_status(
                    job_id=job_id,
                    poster_id=poster_id,
                    status=PosterStatus.FAILED.value,
                    error_message=error_msg
                )
            
            return {
                "success": False,
                "error": error_msg
            }
        finally:
            # The StorageManager now handles temporary files, so no need for manual cleanup
            pass
    
    async def _generate_output_path(self, poster_id: str, job_id: str) -> str:
        """Generate output path for processed poster"""
        # Use StorageManager to get proper configured path
        return self.storage_manager.create_processed_output_path(f"{poster_id}.jpg", job_id)
    
    async def _add_aphrodite_tag(self, poster_id: str) -> None:
        """Add aphrodite-overlay tag to processed item"""
        try:
            tag_service = get_tag_management_service()
            result = await tag_service.add_tag_to_items([poster_id], "aphrodite-overlay")
            if result.processed_count > 0:
                logger.debug(f"Successfully added 'aphrodite-overlay' tag to item {poster_id}")
            else:
                logger.warning(f"Tag addition reported no items processed for {poster_id}")
        except Exception as e:
            logger.warning(f"Failed to add aphrodite-overlay tag to {poster_id}: {e}")
            # Don't fail the whole operation for tag addition failures
