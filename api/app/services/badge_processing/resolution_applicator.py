"""
Resolution Badge Applicator

Handles resolution badge creation and application using v1 logic.
Separated for modularity and reusability.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json

from aphrodite_logging import get_logger


class ResolutionBadgeApplicator:
    """Helper class for applying resolution badges to posters"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.resolution.applicator", service="badge")
    
    async def apply_resolution_badge(
        self,
        poster_path: str,
        resolution_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply resolution badge to poster using v1 logic with v2 output path control"""
        try:
            # Import v1 badge creation functions
            import sys
            import shutil
            from PIL import Image
            # Remove hardcoded Windows path - let Python find the modules
            # sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.badge_components.badge_generator import create_badge
            from aphrodite_helpers.badge_components.badge_applicator import calculate_dynamic_padding
            
            # Create resolution badge using v1 logic
            self.logger.debug(f"Creating badge with settings - Badge Size: {settings.get('General', {}).get('general_badge_size')}, Image Badges: {settings.get('ImageBadges', {}).get('enable_image_badges')}, Use Dynamic: {settings.get('General', {}).get('use_dynamic_sizing')}")
            
            # Log the exact settings being passed to create_badge
            self.logger.debug(f"Full settings being passed to create_badge: {json.dumps(settings, indent=2)}")
            
            # Modify settings to respect database settings properly
            modified_settings = settings.copy()
            
            # Handle badge sizing based on what the user actually wants
            general_settings = modified_settings.get('General', {})
            badge_size = general_settings.get('general_badge_size', 100)
            use_dynamic = general_settings.get('use_dynamic_sizing', True)
            
            self.logger.debug(f"Original settings - Badge size: {badge_size}, Dynamic sizing: {use_dynamic}")
            
            # The v1 code treats general_badge_size as pixel dimensions for square badges
            # Most users probably want dynamic sizing (badges that fit their content)
            # Only disable dynamic sizing if the user set a VERY different size from default
            
            if badge_size == 100:  # Default size
                # Keep dynamic sizing for default
                general_settings['use_dynamic_sizing'] = True
                self.logger.debug("Using dynamic sizing for default badge size")
            elif badge_size < 150:  # Small to medium custom sizes (50-149)
                # Keep dynamic sizing but these will affect minimum dimensions
                general_settings['use_dynamic_sizing'] = True
                self.logger.debug(f"Using dynamic sizing with custom base size: {badge_size}")
            else:  # Large sizes (150+) - user probably wants fixed large badges
                # Use fixed sizing but limit to reasonable maximum
                max_reasonable_size = 120  # Reasonable max for square badges
                if badge_size > max_reasonable_size:
                    general_settings['general_badge_size'] = max_reasonable_size
                    self.logger.debug(f"Limited large badge size from {badge_size} to {max_reasonable_size}")
                general_settings['use_dynamic_sizing'] = False
                self.logger.debug(f"Using fixed sizing for large badge: {general_settings['general_badge_size']}")
            
            # Force image badges setting by modifying the use_image parameter
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', True)
            use_image_for_badge = image_badges_enabled
            
            self.logger.debug(f"Final settings - Badge size: {general_settings.get('general_badge_size')}, Dynamic sizing: {general_settings.get('use_dynamic_sizing')}, Will use images: {use_image_for_badge}")
            
            resolution_badge = create_badge(modified_settings, resolution_data, use_image=use_image_for_badge)
            if not resolution_badge:
                self.logger.error("Failed to create resolution badge")
                return None
            
            self.logger.debug(f"Created badge dimensions: {resolution_badge.size} (Dynamic: {general_settings.get('use_dynamic_sizing')})")
            
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
            position = settings.get('General', {}).get('general_badge_position', 'top-right')
            base_edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
            
            # Calculate dynamic padding based on aspect ratio
            edge_padding = calculate_dynamic_padding(poster.width, poster.height, base_edge_padding)
            
            # Calculate position coordinates
            if position == 'top-left':
                coords = (edge_padding, edge_padding)
            elif position == 'top-right':
                coords = (poster.width - resolution_badge.width - edge_padding, edge_padding)
            elif position == 'bottom-left':
                coords = (edge_padding, poster.height - resolution_badge.height - edge_padding)
            elif position == 'bottom-right':
                coords = (poster.width - resolution_badge.width - edge_padding, poster.height - resolution_badge.height - edge_padding)
            elif position == 'top-center':
                coords = ((poster.width - resolution_badge.width) // 2, edge_padding)
            elif position == 'center-left':
                coords = (edge_padding, (poster.height - resolution_badge.height) // 2)
            elif position == 'center':
                coords = ((poster.width - resolution_badge.width) // 2, (poster.height - resolution_badge.height) // 2)
            elif position == 'center-right':
                coords = (poster.width - resolution_badge.width - edge_padding, (poster.height - resolution_badge.height) // 2)
            elif position == 'bottom-center':
                coords = ((poster.width - resolution_badge.width) // 2, poster.height - resolution_badge.height - edge_padding)
            elif position == 'bottom-right-flush':
                coords = (poster.width - resolution_badge.width, poster.height - resolution_badge.height)
            else:
                # Default to top-right
                coords = (poster.width - resolution_badge.width - edge_padding, edge_padding)
            
            # Paste the badge onto the poster
            poster.paste(resolution_badge, coords, resolution_badge)
            
            # Save the modified poster to the specified output path
            poster.convert("RGB").save(final_output_path, "JPEG")
            
            self.logger.debug(f"Successfully applied resolution badge: {final_output_path}")
            return final_output_path
                
        except Exception as e:
            self.logger.error(f"Error applying resolution badge: {e}", exc_info=True)
            return None


# Global applicator instance for reuse
_resolution_applicator: Optional[ResolutionBadgeApplicator] = None

def get_resolution_applicator() -> ResolutionBadgeApplicator:
    """Get global resolution badge applicator instance"""
    global _resolution_applicator
    if _resolution_applicator is None:
        _resolution_applicator = ResolutionBadgeApplicator()
    return _resolution_applicator
