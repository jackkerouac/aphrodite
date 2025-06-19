"""
Poster Processor

Individual poster processing wrapper for workers.
"""

from typing import Dict, Any, List
from pathlib import Path
import uuid
import asyncio

from aphrodite_logging import get_logger
from app.core.database import async_session_factory
from app.services.badge_processing import UniversalBadgeProcessor
from app.services.badge_processing.types import SingleBadgeRequest

logger = get_logger("aphrodite.worker.poster")


class PosterProcessor:
    """Processes individual posters within batch jobs"""
    
    def __init__(self):
        self.badge_processor = UniversalBadgeProcessor()
    
    async def process_poster(self, 
                           poster_id: str, 
                           badge_types: List[str],
                           job_id: str) -> Dict[str, Any]:
        """
        Process single poster with badges.
        
        Args:
            poster_id: Poster identifier
            badge_types: List of badge types to apply
            job_id: Parent job identifier
            
        Returns:
            Processing result with success status and output path
        """
        logger.debug(f"Processing poster {poster_id} for job {job_id}")
        
        try:
            # Get poster path (this would normally come from database)
            # For now, using demo poster system from Phase 1
            poster_path = await self._get_poster_path(poster_id)
            if not poster_path:
                return {
                    "success": False,
                    "error": f"Poster not found: {poster_id}"
                }
            
            # Generate output path
            output_path = await self._generate_output_path(poster_id, job_id)
            
            # Create badge processing request
            request = SingleBadgeRequest(
                poster_path=poster_path,
                badge_types=badge_types,
                output_path=output_path,
                use_demo_data=True,  # Use demo data for workers
                jellyfin_id=poster_id
            )
            
            # Process poster using existing badge processing pipeline
            async with async_session_factory() as db_session:
                result = await self.badge_processor.process_single(request, db_session)
            
            if result.success and result.results:
                poster_result = result.results[0]
                return {
                    "success": True,
                    "output_path": poster_result.output_path,
                    "applied_badges": poster_result.applied_badges
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
    
    async def _get_poster_path(self, poster_id: str) -> str:
        """Get poster file path from poster ID"""
        # This would normally query the database for the poster path
        # For Phase 2, using the demo poster system from Phase 1
        static_dir = Path("E:/programming/aphrodite/aphrodite-v2/api/static/posters/originals")
        if static_dir.exists():
            poster_files = list(static_dir.glob("*.jpg"))
            if poster_files:
                # Use consistent poster for demo
                return str(poster_files[0])
        
        # Fallback - this should not happen in production
        logger.warning(f"Could not find poster path for {poster_id}")
        return None
    
    async def _generate_output_path(self, poster_id: str, job_id: str) -> str:
        """Generate output path for processed poster"""
        processed_dir = Path("E:/programming/aphrodite/aphrodite-v2/api/static/posters/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename with job and poster ID
        filename = f"job_{job_id}_poster_{poster_id}_{uuid.uuid4().hex[:8]}.jpg"
        return str(processed_dir / filename)
