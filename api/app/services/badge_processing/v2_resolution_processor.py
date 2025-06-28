"""    
Pure V2 Resolution Badge Processor

Completely V2-native resolution badge processing with no V1 dependencies.
Clear logging for system differentiation.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import re
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from .renderers import UnifiedBadgeRenderer
from app.core.database import async_session_factory


class V2ResolutionBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 resolution badge processor - no V1 dependencies"""
    
    def __init__(self):
        super().__init__("resolution")
        self.logger = get_logger("aphrodite.badge.resolution.v2", service="badge")
        self.renderer = UnifiedBadgeRenderer()
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with resolution badge using pure V2 system"""
        try:
            self.logger.info(f"📐 [V2 RESOLUTION] PROCESSOR STARTED for: {poster_path}")
            self.logger.info(f"📐 [V2 RESOLUTION] Jellyfin ID: {jellyfin_id}")
            self.logger.info(f"📐 [V2 RESOLUTION] Use demo data: {use_demo_data}")
            
            # Load resolution badge settings from PostgreSQL
            settings = await self._load_v2_settings(db_session)
            if not settings:
                self.logger.error("❌ [V2 RESOLUTION] Failed to load settings from PostgreSQL")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load V2 resolution badge settings"
                )
            
            self.logger.info("✅ [V2 RESOLUTION] Settings loaded from PostgreSQL")
            
            # Get resolution data using pure V2 methods
            resolution_data = await self._get_v2_resolution(jellyfin_id, use_demo_data, poster_path)
            if not resolution_data:
                self.logger.warning("⚠️ [V2 RESOLUTION] No resolution detected, skipping badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.info(f"📊 [V2 RESOLUTION] Resolution detected: {resolution_data}")
            
            # Create resolution badge using V2 renderer
            result_path = await self._create_v2_resolution_badge(
                poster_path, resolution_data, settings, output_path
            )
            
            if result_path:
                self.logger.info(f"✅ [V2 RESOLUTION] PROCESSOR COMPLETED: {result_path}")
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["resolution"],
                    success=True
                )
            else:
                self.logger.error(f"❌ [V2 RESOLUTION] Badge creation failed")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="V2 resolution badge creation failed"
                )
                
        except Exception as e:
            self.logger.error(f"🚨 [V2 RESOLUTION] PROCESSOR EXCEPTION: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=f"V2 resolution processor error: {str(e)}"
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
    ) -> List[PosterResult]:
        """Process multiple posters with V2 resolution badges"""
        results = []
        
        self.logger.info(f"📐 [V2 RESOLUTION] BULK PROCESSING {len(poster_paths)} posters")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"📐 [V2 RESOLUTION] Processing {i+1}/{len(poster_paths)}: {poster_path}")
            
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
                self.logger.info(f"📐 [V2 RESOLUTION] Processed {i+1}/{len(poster_paths)} badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"📐 [V2 RESOLUTION] BULK COMPLETED: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_v2_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load resolution badge settings from V2 PostgreSQL database only"""
        try:
            self.logger.debug("🗄️ [V2 RESOLUTION] Loading settings from PostgreSQL")
            
            # Load from v2 database
            if db_session:
                settings = await badge_settings_service.get_resolution_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "resolution"):
                    self.logger.info("✅ [V2 RESOLUTION] Settings loaded from PostgreSQL (provided session)")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_resolution_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "resolution"):
                            self.logger.info("✅ [V2 RESOLUTION] Settings loaded from PostgreSQL (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"⚠️ [V2 RESOLUTION] Database connection failed: {db_error}")
            
            # Use V2 default settings as fallback (no YAML files)
            self.logger.info("⚠️ [V2 RESOLUTION] Using V2 default settings (PostgreSQL unavailable)")
            return self._get_v2_default_settings()
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Error loading settings: {e}", exc_info=True)
            return self._get_v2_default_settings()
    
    def _get_v2_default_settings(self) -> Dict[str, Any]:
        """Get V2 default resolution badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True,
                "general_badge_position": "top-left",
                "general_edge_padding": 30
            },
            "Text": {
                "font": "Arial.ttf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 24,
                "text-color": "#FFFFFF"
            },
            "Background": {
                "background-color": "#1f77b4",
                "background_opacity": 80
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
                "enable_image_badges": True,
                "fallback_to_text": True,
                "image_padding": 10,
                "codec_image_directory": "images/resolution"
            }
        }
    
    async def _get_v2_resolution(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str
    ) -> Optional[str]:
        """Get resolution using pure V2 methods only"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [V2 RESOLUTION] Getting real resolution for ID: {jellyfin_id}")
                resolution = await self._get_v2_jellyfin_resolution(jellyfin_id)
                if resolution and resolution != "UNKNOWN":
                    self.logger.debug(f"✅ [V2 RESOLUTION] Real resolution found: {resolution}")
                    return resolution
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [V2 RESOLUTION] Using demo resolution data")
                return self._get_v2_demo_resolution(poster_path)
            
            self.logger.warning("⚠️ [V2 RESOLUTION] No resolution source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Error getting resolution: {e}", exc_info=True)
            return None
    
    async def _get_v2_jellyfin_resolution(self, jellyfin_id: str) -> Optional[str]:
        """Get real resolution using pure V2 Jellyfin service (NO V1 AGGREGATOR)"""
        try:
            self.logger.debug(f"🌐 [V2 RESOLUTION] Querying Jellyfin for ID: {jellyfin_id}")
            
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"📺 [V2 RESOLUTION] Media type: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"🎬 [V2 RESOLUTION] Movie resolution: {resolution}")
                return resolution
            
            elif media_type in ['Series', 'Season']:
                # For TV: PURE V2 episode sampling (NO V1 AGGREGATOR)
                resolution = await self._get_v2_tv_series_resolution(jellyfin_id, jellyfin_service)
                self.logger.debug(f"📺 [V2 RESOLUTION] TV series resolution: {resolution}")
                return resolution
            
            elif media_type == 'Episode':
                # For episodes: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"📻 [V2 RESOLUTION] Episode resolution: {resolution}")
                return resolution
            
            else:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Jellyfin resolution error: {e}", exc_info=True)
            return None
    
    async def _get_v2_tv_series_resolution(self, jellyfin_id: str, jellyfin_service) -> Optional[str]:
        """Get TV series dominant resolution using PURE V2 methods (no V1 aggregator)"""
        try:
            self.logger.debug(f"📺 [V2 RESOLUTION] Sampling TV series episodes for: {jellyfin_id}")
            
            # Get series episodes using V2 Jellyfin service
            episodes = await jellyfin_service.get_series_episodes(jellyfin_id, limit=10)
            
            if not episodes:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] No episodes found for series: {jellyfin_id}")
                return "1080p"  # Reasonable default for TV series
            
            self.logger.debug(f"📺 [V2 RESOLUTION] Found {len(episodes)} episodes to sample")
            
            # Sample resolutions from episodes
            resolutions = []
            for i, episode in enumerate(episodes[:5]):  # Sample first 5 episodes
                try:
                    resolution = await jellyfin_service.get_video_resolution_info(episode)
                    if resolution and resolution != "UNKNOWN":
                        resolutions.append(resolution)
                        self.logger.debug(f"📻 [V2 RESOLUTION] Episode {i+1} resolution: {resolution}")
                except Exception as ep_error:
                    self.logger.warning(f"⚠️ [V2 RESOLUTION] Episode {i+1} resolution error: {ep_error}")
                    continue
            
            if not resolutions:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] No valid resolutions from episodes")
                return "1080p"  # Reasonable default
            
            # Determine dominant resolution using simple frequency count
            resolution_counts = {}
            for resolution in resolutions:
                resolution_counts[resolution] = resolution_counts.get(resolution, 0) + 1
            
            # Get most common resolution
            dominant_resolution = max(resolution_counts.items(), key=lambda x: x[1])[0]
            
            self.logger.debug(f"📊 [V2 RESOLUTION] Resolution frequency: {resolution_counts}")
            self.logger.debug(f"🏆 [V2 RESOLUTION] Dominant resolution: {dominant_resolution}")
            
            return dominant_resolution
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] TV series resolution error: {e}", exc_info=True)
            return "1080p"  # Fallback default
    
    def _get_v2_demo_resolution(self, poster_path: str) -> str:
        """Get demo resolution using V2 consistent algorithm"""
        import hashlib
        
        # Create consistent hash from poster filename
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # V2 demo resolution list
        demo_resolutions = [
            "4K",
            "2160p",
            "1080p",
            "720p",
            "480p"
        ]
        
        # Select resolution based on hash (consistent for same poster)
        selected_resolution = demo_resolutions[hash_value % len(demo_resolutions)]
        
        self.logger.debug(f"🎭 [V2 RESOLUTION] Demo resolution for {poster_name}: {selected_resolution}")
        return selected_resolution
    
    async def _create_v2_resolution_badge(
        self,
        poster_path: str,
        resolution_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create resolution badge using pure V2 renderer"""
        try:
            self.logger.debug(f"🎨 [V2 RESOLUTION] Creating badge for resolution: {resolution_data}")
            
            # Determine output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate V2 preview path
                poster_name = Path(poster_path).name
                final_output_path = f"/app/api/static/preview/{poster_name}"
            
            # Create badge using V2 renderer
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', True)
            
            if image_badges_enabled:
                # Try image badge first
                self.logger.debug(f"🖼️ [V2 RESOLUTION] Attempting image badge for: {resolution_data}")
                badge = self.renderer.create_image_badge(
                    self._map_resolution_to_image(resolution_data),
                    settings,
                    "resolution"
                )
                
                if not badge:
                    # Fallback to text badge
                    self.logger.debug(f"📝 [V2 RESOLUTION] Image failed, using text badge")
                    badge = self.renderer.create_text_badge(resolution_data, settings, "resolution")
            else:
                # Use text badge
                self.logger.debug(f"📝 [V2 RESOLUTION] Creating text badge")
                badge = self.renderer.create_text_badge(resolution_data, settings, "resolution")
            
            if not badge:
                self.logger.error(f"❌ [V2 RESOLUTION] Badge creation failed")
                return None
            
            # Apply badge to poster
            success = self.renderer.apply_badge_to_poster(
                poster_path, badge, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [V2 RESOLUTION] Badge applied successfully: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [V2 RESOLUTION] Badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Badge creation error: {e}", exc_info=True)
            return None
    
    def _map_resolution_to_image(self, resolution: str) -> str:
        """Improved resolution to image mapping with HDR/DV support"""
        resolution_upper = resolution.upper().strip()
        
        # Parse components
        is_dv = bool(re.search(r'DV|DOLBY.?VISION', resolution_upper))
        is_hdr = bool(re.search(r'HDR|HDR10', resolution_upper)) and not is_dv
        is_plus = bool(re.search(r'PLUS|\+', resolution_upper))
        
        # Extract base resolution
        if re.search(r'4K|2160P', resolution_upper):
            base_res = "4k"
        elif re.search(r'1440P', resolution_upper):
            base_res = "1080p"  # Fallback since 1440p images don't exist
            self.logger.debug("1440p detected, using 1080p images")
        elif re.search(r'1080P|1080', resolution_upper):
            base_res = "1080p"
        elif re.search(r'720P|720', resolution_upper):
            base_res = "720p"
        elif re.search(r'576P|576', resolution_upper):
            base_res = "576p"
        elif re.search(r'480P|480', resolution_upper):
            base_res = "480p"
        else:
            self.logger.warning(f"Unknown resolution format: {resolution}")
            return "resolution-generic.png"
        
        # Build image name with priority order
        image_name = base_res
        
        if is_dv and is_hdr:
            image_name += "dvhdr"
        elif is_dv:
            image_name += "dv"
        elif is_hdr:
            image_name += "hdr"
        elif is_plus:
            image_name += "plus"
        
        image_file = f"{image_name}.png"
        
        # Verify image exists, fallback if needed
        image_path = Path("images/resolution") / image_file
        if not image_path.exists():
            fallback = f"{base_res}.png"
            self.logger.warning(f"Image {image_file} not found, using fallback: {fallback}")
            return fallback
        
        self.logger.debug(f"Resolution '{resolution}' mapped to image: {image_file}")
        return image_file
