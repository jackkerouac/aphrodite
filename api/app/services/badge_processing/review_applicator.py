"""
Review Badge Applicator

Handles review badge creation and application using v1 logic.
Separated for modularity and reusability.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from aphrodite_logging import get_logger


class ReviewBadgeApplicator:
    """Helper class for applying review badges to posters"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.review.applicator", service="badge")
    
    async def apply_review_badge(
        self,
        poster_path: str,
        review_data: List[Dict[str, Any]],
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply review badge to poster using v1 logic with v2 output path control"""
        try:
            # Import v1 review badge creation functions
            import sys
            import shutil
            from PIL import Image
            # Remove hardcoded Windows path - let Python find the modules
            # sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.apply_review_badges import create_review_container
            from aphrodite_helpers.badge_components.badge_applicator import calculate_dynamic_padding
            
            # Create review container using v1 logic
            self.logger.debug(f"Creating review container with {len(review_data)} reviews")
            self.logger.debug(f"Review settings: {json.dumps(settings, indent=2)}")
            
            review_container = create_review_container(review_data, settings)
            if not review_container:
                self.logger.error("Failed to create review container")
                return None
            
            self.logger.debug(f"Created review container dimensions: {review_container.size}")
            
            # Determine the final output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate output path in v2 preview directory (Docker-compatible)
                poster_name = Path(poster_path).name
                final_output_path = f"/app/api/static/preview/{poster_name}"
            
            # Ensure output directory exists
            output_dir = Path(final_output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Apply badge using v2-compatible logic (based on v1 badge_applicator.py)
            poster = Image.open(poster_path).convert("RGBA")
            
            # Get badge position from settings
            position = settings.get('General', {}).get('general_badge_position', 'bottom-left')
            base_edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
            
            # Calculate dynamic padding based on aspect ratio
            edge_padding = calculate_dynamic_padding(poster.width, poster.height, base_edge_padding)
            
            # Calculate position coordinates
            if position == 'top-left':
                coords = (edge_padding, edge_padding)
            elif position == 'top-right':
                coords = (poster.width - review_container.width - edge_padding, edge_padding)
            elif position == 'bottom-left':
                coords = (edge_padding, poster.height - review_container.height - edge_padding)
            elif position == 'bottom-right':
                coords = (poster.width - review_container.width - edge_padding, poster.height - review_container.height - edge_padding)
            elif position == 'top-center':
                coords = ((poster.width - review_container.width) // 2, edge_padding)
            elif position == 'center-left':
                coords = (edge_padding, (poster.height - review_container.height) // 2)
            elif position == 'center':
                coords = ((poster.width - review_container.width) // 2, (poster.height - review_container.height) // 2)
            elif position == 'center-right':
                coords = (poster.width - review_container.width - edge_padding, (poster.height - review_container.height) // 2)
            elif position == 'bottom-center':
                coords = ((poster.width - review_container.width) // 2, poster.height - review_container.height - edge_padding)
            elif position == 'bottom-right-flush':
                coords = (poster.width - review_container.width, poster.height - review_container.height)
            else:
                # Default to bottom-left for reviews
                coords = (edge_padding, poster.height - review_container.height - edge_padding)
            
            # Paste the review container onto the poster
            poster.paste(review_container, coords, review_container)
            
            # Save the modified poster to the specified output path
            poster.convert("RGB").save(final_output_path, "JPEG")
            
            self.logger.debug(f"Successfully applied review badge: {final_output_path}")
            return final_output_path
                
        except Exception as e:
            self.logger.error(f"Error applying review badge: {e}", exc_info=True)
            return None


# Global applicator instance for reuse
_review_applicator: Optional[ReviewBadgeApplicator] = None

def get_review_applicator() -> ReviewBadgeApplicator:
    """Get global review badge applicator instance"""
    global _review_applicator
    if _review_applicator is None:
        _review_applicator = ReviewBadgeApplicator()
    return _review_applicator
