"""
Resolution Badge Processor

Handles resolution badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult


class ResolutionBadgeProcessor(BaseBadgeProcessor):
    """Resolution badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("resolution")
        self.logger = get_logger("aphrodite.badge.resolution", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False
    ) -> PosterResult:
        """Process a single poster with resolution badge"""
        try:
            self.logger.debug(f"Processing resolution badge for: {poster_path}")
            
            # Load resolution badge settings
            settings = await self._load_settings()
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load resolution badge settings"
                )
            
            # Get resolution data
            if use_demo_data:
                resolution_data = "4K HDR"  # Demo resolution for consistent previews
                self.logger.debug("Using demo resolution: 4K HDR")
            else:
                resolution_data = await self._get_resolution_info(poster_path)
                self.logger.debug(f"Detected resolution: {resolution_data}")
            
            if not resolution_data:
                self.logger.warning("No resolution detected, skipping resolution badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Create and apply resolution badge
            result_path = await self._apply_resolution_badge(
                poster_path, resolution_data, settings, output_path
            )
            
            if result_path:
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["resolution"],
                    success=True
                )
            else:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to apply resolution badge"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing resolution badge: {e}", exc_info=True)
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
        """Process multiple posters with resolution badges"""
        results = []
        
        self.logger.info(f"Processing {len(poster_paths)} posters with resolution badges")
        
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
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} resolution badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Resolution badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_settings(self) -> Optional[Dict[str, Any]]:
        """Load resolution badge settings from v1 YAML or v2 database"""
        try:
            # First try to load from v1 settings file for compatibility
            v1_settings_path = Path("E:/programming/aphrodite/badge_settings_resolution.yml")
            
            if v1_settings_path.exists():
                self.logger.debug(f"Loading v1 resolution settings from: {v1_settings_path}")
                with open(v1_settings_path, 'r', encoding='utf-8') as f:
                    settings = yaml.safe_load(f)
                return settings
            
            # TODO: Load from v2 database when available
            self.logger.warning("v1 resolution settings not found, using default settings")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading resolution settings: {e}", exc_info=True)
            return None
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default resolution badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True
            },
            "Text": {
                "font": "Arial.ttf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 20,
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
                "enable_image_badges": False,
                "fallback_to_text": True,
                "image_padding": 15
            }
        }
    
    async def _get_resolution_info(self, poster_path: str) -> Optional[str]:
        """Get resolution info for the media item (placeholder for real implementation)"""
        # TODO: Implement real resolution detection
        # This would involve:
        # 1. Getting media ID from poster path
        # 2. Querying Jellyfin for media info
        # 3. Extracting resolution information
        
        # For now, return demo data
        return "4K HDR"
    
    async def _apply_resolution_badge(
        self,
        poster_path: str,
        resolution_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply resolution badge to poster using v1 logic"""
        try:
            # Import v1 badge creation functions
            import sys
            sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.badge_components import (
                create_badge, 
                apply_badge_to_poster as v1_apply_badge
            )
            
            # Create resolution badge using v1 logic
            resolution_badge = create_badge(settings, resolution_data)
            if not resolution_badge:
                self.logger.error("Failed to create resolution badge")
                return None
            
            # Apply badge to poster using v1 logic
            result_path = v1_apply_badge(poster_path, resolution_badge, settings)
            
            if result_path and Path(result_path).exists():
                self.logger.debug(f"Successfully applied resolution badge: {result_path}")
                return result_path
            else:
                self.logger.error("v1 badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Error applying resolution badge: {e}", exc_info=True)
            return None
