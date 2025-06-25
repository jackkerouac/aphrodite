"""
Resolution Badge Processor

Handles resolution badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import json
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from app.core.database import async_session_factory


class ResolutionBadgeProcessor(BaseBadgeProcessor):
    """Resolution badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("resolution")
        self.logger = get_logger("aphrodite.badge.resolution", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with resolution badge"""
        try:
            self.logger.debug(f"Processing resolution badge for: {poster_path}")
            
            # Load resolution badge settings
            settings = await self._load_settings(db_session)
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load resolution badge settings"
                )
            
            # Get resolution data - use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"Getting real resolution for jellyfin_id: {jellyfin_id}")
                resolution_data = await self._get_resolution_from_jellyfin_id(jellyfin_id)
            elif use_demo_data:
                self.logger.debug("Using demo data for resolution (fallback)")
                resolution_data = self._get_demo_resolution(poster_path)
            else:
                self.logger.debug("No jellyfin_id provided and demo data disabled")
                resolution_data = None
            
            self.logger.debug(f"Resolution data: {resolution_data}")
            
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
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
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
            result = await self.process_single(poster_path, output_path, use_demo_data, db_session)
            results.append(result)
            
            # Log progress for bulk operations
            if (i + 1) % 10 == 0:
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} resolution badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Resolution badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load resolution badge settings from v2 PostgreSQL database only"""
        try:
            # Load from v2 database
            if db_session:
                self.logger.debug("Loading resolution settings from v2 database")
                settings = await badge_settings_service.get_resolution_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "resolution"):
                    self.logger.info("Successfully loaded resolution settings from v2 database")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_resolution_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "resolution"):
                            self.logger.info("Successfully loaded resolution settings from v2 database (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"Could not load from database: {db_error}")
            
            # Use default settings as fallback (no YAML files in v2)
            self.logger.info("Using default resolution settings (v2 database not available)")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading resolution settings: {e}", exc_info=True)
            return self._get_default_settings()
    
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
                "background-color": "#ff6b35",
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
    
    async def _get_resolution_from_jellyfin_id(self, jellyfin_id: Optional[str] = None) -> Optional[str]:
        """Get real resolution directly from Jellyfin ID (CRITICAL FIX)"""
        try:
            if not jellyfin_id:
                self.logger.warning("No jellyfin_id provided for resolution detection")
                return None
            
            self.logger.debug(f"Getting resolution for Jellyfin ID: {jellyfin_id}")
            
            # Import and get Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Query Jellyfin for media details
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"Could not retrieve media item for ID: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"Media type for {jellyfin_id}: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"Movie resolution for {jellyfin_id}: {resolution}")
                return resolution
            
            elif media_type in ['Series', 'Season']:
                # For TV: use existing v1 aggregator logic for dominant resolution
                # CRITICAL FIX: Isolate v1 aggregator from async database context
                self.logger.debug(f"Using v1 aggregator for TV series dominant resolution: {jellyfin_id}")
                
                try:
                    # Load Jellyfin settings like the aggregator expects
                    await jellyfin_service._load_jellyfin_settings()
                    
                    # ISOLATION: Run the v1 aggregator in a separate thread to avoid
                    # database connection corruption between sync and async contexts
                    import asyncio
                    import concurrent.futures
                    
                    def run_v1_aggregator():
                        """Run v1 aggregator in isolation"""
                        try:
                            # Import the v1 aggregator function
                            from aphrodite_helpers.tv_series_aggregator import get_dominant_resolution
                            
                            # Call the aggregator function in isolated context
                            resolution = get_dominant_resolution(
                                jellyfin_service.base_url,
                                jellyfin_service.api_key,
                                jellyfin_service.user_id,
                                jellyfin_id
                            )
                            
                            return resolution if resolution != "UNKNOWN" else None
                        except Exception as e:
                            self.logger.error(f"V1 aggregator error: {e}")
                            return None
                    
                    # Run in thread pool to isolate database connections
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_v1_aggregator)
                        resolution = await asyncio.wrap_future(future)
                    
                    self.logger.debug(f"TV series dominant resolution for {jellyfin_id}: {resolution}")
                    return resolution
                    
                except Exception as aggregator_error:
                    self.logger.error(f"Error using v1 aggregator: {aggregator_error}")
                    # Fallback to a reasonable default for TV series
                    self.logger.debug("Using fallback resolution for TV series: 1080p")
                    return "1080p"
            
            elif media_type == 'Episode':
                # For individual episodes: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"Episode resolution for {jellyfin_id}: {resolution}")
                return resolution
            
            else:
                self.logger.warning(f"Unsupported media type '{media_type}' for {jellyfin_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting resolution for jellyfin_id {jellyfin_id}: {e}", exc_info=True)
            return None
    
    async def _get_resolution_info(self, poster_path: str) -> Optional[str]:
        """Get real resolution info from Jellyfin metadata using modular detector"""
        from .resolution_detector import get_resolution_detector
        detector = get_resolution_detector()
        return await detector.get_resolution_info(poster_path)
    
    def _get_demo_resolution(self, poster_path: str) -> str:
        """Get demo resolution as fallback (consistent per poster)"""
        import hashlib
        
        # Create a hash of the poster filename for consistent but varied results
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # List of common resolutions to rotate through
        demo_resolutions = [
            "4K HDR",
            "4K UHD", 
            "1080p",
            "1080p HDR",
            "720p",
            "2160p"
        ]
        
        # Select resolution based on hash (consistent for same poster)
        selected_resolution = demo_resolutions[hash_value % len(demo_resolutions)]
        
        self.logger.debug(f"Demo resolution for {poster_name}: {selected_resolution}")
        return selected_resolution
    
    async def _apply_resolution_badge(
        self,
        poster_path: str,
        resolution_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply resolution badge to poster using modular applicator"""
        from .resolution_applicator import get_resolution_applicator
        applicator = get_resolution_applicator()
        return await applicator.apply_resolution_badge(
            poster_path, resolution_data, settings, output_path
        )
