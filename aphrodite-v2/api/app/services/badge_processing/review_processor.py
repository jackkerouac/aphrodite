"""
Review Badge Processor

Handles review badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult


class ReviewBadgeProcessor(BaseBadgeProcessor):
    """Review badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("review")
        self.logger = get_logger("aphrodite.badge.review", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False
    ) -> PosterResult:
        """Process a single poster with review badge"""
        try:
            self.logger.debug(f"Processing review badge for: {poster_path}")
            
            # Load review badge settings
            settings = await self._load_settings()
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load review badge settings"
                )
            
            # Get review data
            if use_demo_data:
                review_data = self._get_demo_reviews()
                self.logger.debug("Using demo review data")
            else:
                review_data = await self._get_review_info(poster_path)
                self.logger.debug(f"Retrieved {len(review_data)} reviews" if review_data else "No reviews found")
            
            if not review_data:
                self.logger.warning("No reviews found, skipping review badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Create and apply review badge
            result_path = await self._apply_review_badge(
                poster_path, review_data, settings, output_path
            )
            
            if result_path:
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["review"],
                    success=True
                )
            else:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to apply review badge"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing review badge: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=str(e)
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False
    ) -> List[PosterResult]:
        """Process multiple posters with review badges"""
        results = []
        
        self.logger.info(f"Processing {len(poster_paths)} posters with review badges")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"Processing poster {i+1}/{len(poster_paths)}: {poster_path}")
            
            # Calculate output path for bulk processing
            output_path = None
            if output_directory:
                poster_name = Path(poster_path).name
                output_path = str(Path(output_directory) / poster_name)
            
            # Process single poster
            result = await self.process_single(poster_path, output_path, use_demo_data)
            results.append(result)
            
            # Log progress for bulk operations
            if (i + 1) % 10 == 0:
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} review badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Review badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    def _get_demo_reviews(self) -> List[Dict[str, Any]]:
        """Get realistic demo review data for consistent previews"""
        return [
            {
                "source": "IMDb",
                "text": "85%",
                "image_key": "IMDb"
            },
            {
                "source": "TMDb",
                "text": "82%",
                "image_key": "TMDb"
            },
            {
                "source": "Rotten Tomatoes",
                "text": "78%",
                "image_key": "RT-Crit-Fresh"
            }
        ]
    
    async def _load_settings(self) -> Optional[Dict[str, Any]]:
        """Load review badge settings from v1 YAML or v2 database"""
        try:
            # First try to load from v1 settings file for compatibility
            v1_settings_path = Path("E:/programming/aphrodite/badge_settings_review.yml")
            
            if v1_settings_path.exists():
                self.logger.debug(f"Loading v1 review settings from: {v1_settings_path}")
                with open(v1_settings_path, 'r', encoding='utf-8') as f:
                    settings = yaml.safe_load(f)
                return settings
            
            # TODO: Load from v2 database when available
            self.logger.warning("v1 review settings not found, using default settings")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading review settings: {e}", exc_info=True)
            return None
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default review badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True
            },
            "Text": {
                "font": "Arial.ttf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 16,
                "text-color": "#FFFFFF"
            },
            "Background": {
                "background-color": "#fe019a",
                "background_opacity": 60
            },
            "Border": {
                "border-color": "#000000",
                "border_width": 1,
                "border-radius": 10
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 5,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,  # Reviews use logos
                "fallback_to_text": True,
                "image_padding": 15
            },
            "Review": {
                "layout": "horizontal",
                "spacing": 10,
                "max_reviews": 3
            }
        }
    
    async def _get_review_info(self, poster_path: str) -> Optional[List[Dict[str, Any]]]:
        """Get review info for the media item (placeholder for real implementation)"""
        # TODO: Implement real review fetching
        # This would involve:
        # 1. Getting media ID from poster path
        # 2. Querying Jellyfin for media info
        # 3. Fetching reviews from various sources (IMDb, TMDb, etc.)
        
        # For now, return demo data
        return self._get_demo_reviews()
    
    async def _apply_review_badge(
        self,
        poster_path: str,
        review_data: List[Dict[str, Any]],
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply review badge to poster using v1 logic"""
        try:
            # Import v1 review badge functions
            import sys
            sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.apply_review_badges import (
                create_review_container, 
                apply_badge_to_poster as apply_review_badge
            )
            
            # Create review container using v1 logic
            review_container = create_review_container(review_data, settings)
            if not review_container:
                self.logger.error("Failed to create review container")
                return None
            
            # Determine working and output directories
            poster_path_obj = Path(poster_path)
            working_dir = poster_path_obj.parent / "working"
            modified_dir = poster_path_obj.parent / "modified"
            
            # Ensure directories exist
            working_dir.mkdir(exist_ok=True)
            modified_dir.mkdir(exist_ok=True)
            
            # Handle PNG to JPG conversion for review processing
            temp_current_path = poster_path
            if poster_path.endswith('.png'):
                temp_jpg_path = poster_path.replace('.png', '.jpg')
                try:
                    from PIL import Image
                    img = Image.open(poster_path)
                    img.convert('RGB').save(temp_jpg_path, 'JPEG')
                    temp_current_path = temp_jpg_path
                    self.logger.debug(f"Converted PNG to JPG for review processing: {temp_jpg_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to convert PNG to JPG: {e}")
            
            # Apply review badge to poster using v1 logic
            result_path = apply_review_badge(
                poster_path=temp_current_path,
                badge=review_container,
                settings=settings,
                working_dir=str(working_dir),
                output_dir=str(modified_dir)
            )
            
            # Clean up temporary JPG file if created
            if temp_current_path != poster_path and Path(temp_current_path).exists():
                try:
                    Path(temp_current_path).unlink()
                except Exception as e:
                    self.logger.warning(f"Failed to clean up temp file: {e}")
            
            # Convert result back to PNG if needed
            if result_path and result_path.endswith('.jpg') and poster_path.endswith('.png'):
                final_png_path = result_path.replace('.jpg', '.png')
                try:
                    from PIL import Image
                    img = Image.open(result_path)
                    img.save(final_png_path, 'PNG')
                    Path(result_path).unlink()  # Remove JPG version
                    result_path = final_png_path
                    self.logger.debug(f"Converted result back to PNG: {final_png_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to convert result back to PNG: {e}")
            
            if result_path and Path(result_path).exists():
                self.logger.debug(f"Successfully applied review badge: {result_path}")
                return result_path
            else:
                self.logger.error("v1 review badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Error applying review badge: {e}", exc_info=True)
            return None
