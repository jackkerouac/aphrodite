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
from app.services.badge_processing import UniversalBadgeProcessor
from app.services.badge_processing.types import SingleBadgeRequest
from app.services.jellyfin_service import get_jellyfin_service

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
                           db_session) -> Dict[str, Any]:
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
        
        temp_poster_path = None
        
        try:
            # Download the specific poster from Jellyfin
            poster_data = await self.jellyfin_service.download_poster(poster_id)
            if not poster_data:
                return {
                    "success": False,
                    "error": f"Failed to download poster for Jellyfin item: {poster_id}"
                }
            
            # Create temporary file for the downloaded poster
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(poster_data)
                temp_poster_path = temp_file.name
            
            logger.debug(f"Downloaded poster for {poster_id} to {temp_poster_path}")
            
            # Generate output path
            output_path = await self._generate_output_path(poster_id, job_id)
            
            # Create badge processing request
            request = SingleBadgeRequest(
                poster_path=temp_poster_path,
                badge_types=badge_types,
                output_path=output_path,
                use_demo_data=False,  # Use real Jellyfin metadata
                jellyfin_id=poster_id
            )
            
            # Process poster using existing badge processing pipeline
            result = await self.badge_processor.process_single(request, db_session)
            
            if result.success and result.results:
                poster_result = result.results[0]
                
                # Upload processed poster back to Jellyfin
                upload_success = False
                if poster_result.output_path and os.path.exists(poster_result.output_path):
                    try:
                        upload_success = await self.jellyfin_service.upload_poster_image(
                            poster_id, 
                            poster_result.output_path
                        )
                        if upload_success:
                            logger.debug(f"Successfully uploaded processed poster to Jellyfin for {poster_id}")
                        else:
                            logger.warning(f"Failed to upload processed poster to Jellyfin for {poster_id}")
                    except Exception as upload_error:
                        logger.error(f"Error uploading poster to Jellyfin for {poster_id}: {upload_error}")
                
                return {
                    "success": True,
                    "output_path": poster_result.output_path,
                    "applied_badges": poster_result.applied_badges,
                    "uploaded_to_jellyfin": upload_success
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "Unknown processing error"
                }
                
        except Exception as e:
            logger.error(f"Error processing poster {poster_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
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
