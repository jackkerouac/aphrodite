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

logger = get_logger("aphrodite.worker.poster")


class PosterProcessor:
    """Processes individual posters within batch jobs"""
    
    def __init__(self):
        self.badge_processor = UniversalBadgeProcessor()
        self.jellyfin_service = get_jellyfin_service()
    
    async def process_poster(self, 
                           poster_id: str, 
                           badge_types: List[str],
                           job_id: str,
                           db_session,
                           progress_tracker=None) -> Dict[str, Any]:
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
            
            # Retry logic for poster download to handle transient HTTP 400 errors
            max_retries = 3
            retry_delay = 1.0  # Start with 1 second delay
            poster_data = None
            
            for attempt in range(max_retries):
                try:
                    poster_data = await self.jellyfin_service.download_poster(poster_id)
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
            
            # Create temporary file for the downloaded poster
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(poster_data)
                temp_poster_path = temp_file.name
            
            logger.debug(f"Downloaded poster for {poster_id} to {temp_poster_path}")
            
            # Generate output path
            output_path = await self._generate_output_path(poster_id, job_id)
            
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
            # Clean up temporary file
            if temp_poster_path and os.path.exists(temp_poster_path):
                try:
                    os.unlink(temp_poster_path)
                    logger.debug(f"Cleaned up temporary poster file: {temp_poster_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up temporary file {temp_poster_path}: {cleanup_error}")
    
    async def _generate_output_path(self, poster_id: str, job_id: str) -> str:
        """Generate output path for processed poster"""
        processed_dir = Path("E:/programming/aphrodite/aphrodite-v2/api/static/posters/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename with job and poster ID
        filename = f"job_{job_id}_poster_{poster_id}_{uuid.uuid4().hex[:8]}.jpg"
        return str(processed_dir / filename)
    
    async def _add_aphrodite_tag(self, poster_id: str) -> None:
        """Add aphrodite-overlay tag to processed item"""
        try:
            # This would need to be implemented in JellyfinService
            # For now, just log the intent
            logger.debug(f"Would add 'aphrodite-overlay' tag to item {poster_id}")
        except Exception as e:
            logger.warning(f"Failed to add aphrodite-overlay tag to {poster_id}: {e}")
