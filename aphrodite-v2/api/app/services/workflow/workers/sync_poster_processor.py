"""
Synchronous Poster Processor for Celery Worker

Processes single posters without async/await to avoid event loop conflicts.
"""

from typing import Dict, Any, List
from pathlib import Path
import uuid

from aphrodite_logging import get_logger

logger = get_logger("aphrodite.worker.poster_processor")

class SyncPosterProcessor:
    """Synchronous poster processor for Celery workers"""
    
    def process_poster(
        self, 
        poster_id: str, 
        badge_types: List[str], 
        job_id: str
    ) -> Dict[str, Any]:
        """
        Process a single poster with badges
        
        Args:
            poster_id: Poster identifier
            badge_types: List of badge types to apply
            job_id: Job identifier for tracking
            
        Returns:
            Processing result
        """
        logger.info(f"Processing poster {poster_id} for job {job_id}")
        
        try:
            # Simple placeholder processing (no external dependencies)
            # TODO: Replace with real badge processing once pipeline is fixed
            
            # Generate output path - use correct API static directory
            output_dir = Path("api/static/processed")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"{uuid.uuid4()}.jpg"
            output_path = output_dir / output_filename
            
            # Placeholder: Create a simple test file
            # In real implementation, this would process the actual poster
            badge_text = f"Processed poster {poster_id} with badges: {', '.join(badge_types)}"
            output_path.write_text(badge_text)
            
            logger.info(f"Completed poster {poster_id} -> {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "poster_id": poster_id,
                "job_id": job_id,
                "applied_badges": badge_types
            }
            
        except Exception as e:
            logger.error(f"Failed to process poster {poster_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "poster_id": poster_id,
                "job_id": job_id
            }
