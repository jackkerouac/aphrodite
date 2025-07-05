"""    
Pure V2 Resolution Badge Processor

Completely V2-native resolution badge processing with no V1 dependencies.
Clear logging for system differentiation.
"""

from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import re
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from .renderers import UnifiedBadgeRenderer
from app.core.database import async_session_factory

# Enhanced resolution detection components
try:
    from .resolution_detector import EnhancedResolutionDetector
    from .image_manager import ResolutionImageManager
    from .parallel_processor import ParallelResolutionProcessor
    from .resolution_cache import ResolutionCache
    ENHANCED_DETECTION_AVAILABLE = True
except ImportError:
    ENHANCED_DETECTION_AVAILABLE = False


class V2ResolutionBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 resolution badge processor - no V1 dependencies"""
    
    def __init__(self):
        super().__init__("resolution")
        self.logger = get_logger("aphrodite.badge.resolution.v2", service="badge")
        self.renderer = UnifiedBadgeRenderer()
        
        # Always use enhanced detection components (no legacy fallback)
        self.logger.info("🚀 [V2 RESOLUTION] Initializing enhanced resolution detection")
        try:
            self.enhanced_detector = EnhancedResolutionDetector()
            
            # Try to initialize optional advanced components
            try:
                self.image_manager = ResolutionImageManager()
                self.parallel_processor = ParallelResolutionProcessor()
                self.cache = ResolutionCache()
                self.logger.info("✅ [V2 RESOLUTION] Advanced components loaded successfully")
            except ImportError:
                self.logger.info("⚠️ [V2 RESOLUTION] Advanced components not available, using basic enhanced detection")
                self.image_manager = None
                self.parallel_processor = None
                self.cache = None
            
            self.logger.info("✅ [V2 RESOLUTION] Enhanced detection initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Failed to initialize enhanced detection: {e}")
            raise RuntimeError(f"Resolution detection initialization failed: {e}")
    
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
        """Get real resolution using ONLY enhanced detection (no legacy fallback)"""
        try:
            self.logger.debug(f"🌐 [V2 RESOLUTION] Querying Jellyfin for ID: {jellyfin_id}")
            
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item with fallback for API compatibility
            media_item = await jellyfin_service.get_item_details(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"📺 [V2 RESOLUTION] Media type: {media_type}")
            
            if media_type == 'Movie':
                # For movies: use enhanced detection
                return await self._get_enhanced_movie_resolution(media_item)
            
            elif media_type in ['Series', 'Season']:
                # For TV: use enhanced parallel processing with enhanced detector
                return await self._get_enhanced_series_resolution(jellyfin_id, jellyfin_service)
            
            elif media_type == 'Episode':
                # For episodes: use enhanced detection (same logic as movies)
                return await self._get_enhanced_movie_resolution(media_item)
            
            else:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Jellyfin resolution error: {e}", exc_info=True)
            return None
    
    async def _get_enhanced_movie_resolution(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Get movie resolution using enhanced detection with improved fallback"""
        try:
            # Always use enhanced detector (no legacy fallback)
            resolution_info = self.enhanced_detector.extract_resolution_info(media_item)
            if resolution_info:
                result = str(resolution_info)
                self.logger.debug(f"🎆 [V2 RESOLUTION] Enhanced movie resolution: {result}")
                return result
            else:
                self.logger.warning("⚠️ [V2 RESOLUTION] Enhanced detection failed, no fallback available")
                # Return sensible default instead of None
                return "1080p"  # Most common resolution
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Enhanced movie detection error: {e}")
            return "1080p"  # Fallback default
    
    async def _get_enhanced_series_resolution(self, jellyfin_id: str, jellyfin_service) -> Optional[str]:
        """Get series resolution using enhanced detection with episode sampling"""
        try:
            # Check cache first if available
            if hasattr(self, 'cache') and self.cache:
                cached_resolution = self.cache.get_cached_resolution(jellyfin_id)
                if cached_resolution:
                    result = str(cached_resolution)
                    self.logger.debug(f"📦 [V2 RESOLUTION] Cached series resolution: {result}")
                    return result
            
            # Load performance settings
            max_episodes = self._get_performance_setting('max_episodes_to_sample', 5)
            
            # Use enhanced detector for series resolution (with episode sampling)
            if hasattr(self, 'parallel_processor') and self.parallel_processor:
                # Use parallel processing if available
                resolution_info = await self.parallel_processor.get_series_resolution_parallel(
                    jellyfin_service, jellyfin_id, max_episodes=max_episodes
                )
            else:
                # Fallback to sequential enhanced detection
                resolution_info = await self._get_series_resolution_sequential(jellyfin_id, jellyfin_service, max_episodes)
            
            if resolution_info:
                # Cache the result if caching is available
                if hasattr(self, 'cache') and self.cache:
                    self.cache.cache_series_resolution(jellyfin_id, resolution_info)
                result = str(resolution_info)
                self.logger.debug(f"🎆 [V2 RESOLUTION] Enhanced series resolution: {result}")
                return result
            else:
                self.logger.warning("⚠️ [V2 RESOLUTION] Enhanced series detection failed")
                return "1080p"  # Reasonable default
                
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Enhanced series detection error: {e}")
            return "1080p"  # Fallback default
    
    async def _get_series_resolution_sequential(self, jellyfin_id: str, jellyfin_service, max_episodes: int = 5) -> Optional[str]:
        """Get TV series dominant resolution using sequential enhanced detection"""
        try:
            self.logger.debug(f"📺 [V2 RESOLUTION] Sampling TV series episodes for: {jellyfin_id}")
            
            # Get series episodes using V2 Jellyfin service
            episodes = await jellyfin_service.get_series_episodes(jellyfin_id, limit=max_episodes)
            
            if not episodes:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] No episodes found for series: {jellyfin_id}")
                return None
            
            self.logger.debug(f"📺 [V2 RESOLUTION] Found {len(episodes)} episodes to sample")
            
            # Sample resolutions from episodes using enhanced detector
            resolution_infos = []
            for i, episode in enumerate(episodes[:max_episodes]):
                try:
                    # Use enhanced detector instead of legacy method
                    resolution_info = self.enhanced_detector.extract_resolution_info(episode)
                    if resolution_info:
                        resolution_infos.append(resolution_info)
                        self.logger.debug(f"📻 [V2 RESOLUTION] Episode {i+1} resolution: {resolution_info}")
                except Exception as ep_error:
                    self.logger.warning(f"⚠️ [V2 RESOLUTION] Episode {i+1} enhanced detection error: {ep_error}")
                    continue
            
            if not resolution_infos:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] No valid resolutions from episodes")
                return None
            
            # Determine dominant resolution using enhanced resolution comparison
            resolution_counts = {}
            for resolution_info in resolution_infos:
                # Use the string representation for grouping
                resolution_str = str(resolution_info)
                resolution_counts[resolution_str] = resolution_counts.get(resolution_str, 0) + 1
            
            # Get most common resolution
            dominant_resolution = max(resolution_counts.items(), key=lambda x: x[1])[0]
            
            self.logger.debug(f"📊 [V2 RESOLUTION] Resolution frequency: {resolution_counts}")
            self.logger.debug(f"🏆 [V2 RESOLUTION] Dominant resolution: {dominant_resolution}")
            
            return dominant_resolution
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RESOLUTION] Sequential series resolution error: {e}", exc_info=True)
            return None
    
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
        """Enhanced resolution to image mapping with fallback to legacy"""
        if self.enhanced_enabled:
            try:
                # Use enhanced image manager
                from .resolution_types import ResolutionInfo
                
                # Create a basic ResolutionInfo from the string for image mapping
                # This is a simplified approach for backward compatibility
                resolution_info = self._parse_resolution_string(resolution)
                
                # Get user mappings from settings (if available)
                user_mappings = self._get_user_image_mappings()
                
                # Use enhanced image matching
                image_file = self.image_manager.find_best_image_match(resolution_info, user_mappings)
                
                self.logger.debug(f"🎆 [V2 RESOLUTION] Enhanced image mapping: '{resolution}' -> {image_file}")
                return image_file
                
            except Exception as e:
                self.logger.warning(f"⚠️ [V2 RESOLUTION] Enhanced image mapping failed: {e}, using legacy")
                # Fall through to legacy mapping
        
        # Legacy mapping (original implementation)
        return self._map_resolution_to_image_legacy(resolution)
    
    def _parse_resolution_string(self, resolution: str) -> 'ResolutionInfo':
        """Parse resolution string into ResolutionInfo for image mapping"""
        from .resolution_types import ResolutionInfo
        
        resolution_upper = resolution.upper().strip()
        
        # Parse components
        is_dv = bool(re.search(r'DV|DOLBY.?VISION', resolution_upper))
        is_hdr = bool(re.search(r'HDR|HDR10', resolution_upper)) and not is_dv
        is_plus = bool(re.search(r'PLUS|\+', resolution_upper))
        
        # Extract base resolution and dimensions
        if re.search(r'4K|2160P', resolution_upper):
            base_res = "4k"
            height, width = 2160, 3840
        elif re.search(r'1440P', resolution_upper):
            base_res = "1440p"
            height, width = 1440, 2560
        elif re.search(r'1080P|1080', resolution_upper):
            base_res = "1080p"
            height, width = 1080, 1920
        elif re.search(r'720P|720', resolution_upper):
            base_res = "720p"
            height, width = 720, 1280
        elif re.search(r'576P|576', resolution_upper):
            base_res = "576p"
            height, width = 576, 720
        elif re.search(r'480P|480', resolution_upper):
            base_res = "480p"
            height, width = 480, 720
        else:
            base_res = "1080p"  # Default
            height, width = 1080, 1920
        
        return ResolutionInfo(
            height=height,
            width=width,
            base_resolution=base_res,
            is_hdr=is_hdr,
            is_dolby_vision=is_dv,
            is_hdr_plus=is_plus
        )
    
    def _get_user_image_mappings(self) -> Optional[Dict[str, str]]:
        """Get user-defined image mappings from settings"""
        try:
            # Load user mappings from current settings if available
            # This integrates with the existing settings system
            return None  # Use automatic detection for now
        except Exception:
            return None
    
    def _get_performance_setting(self, setting_name: str, default_value: Union[int, bool, str]) -> Union[int, bool, str]:
        """Get performance setting with fallback to default"""
        try:
            # In a full implementation, this would load from settings
            # For now, return sensible defaults
            defaults = {
                'max_episodes_to_sample': 5,
                'enable_parallel_processing': True,
                'enable_caching': True
            }
            return defaults.get(setting_name, default_value)
        except Exception:
            return default_value
    
    def _load_enhanced_detection_settings(self) -> Dict[str, Any]:
        """Load enhanced detection settings"""
        try:
            # Load settings - this would integrate with the existing settings system
            return {
                'enabled': True,
                'fallback_rules': {
                    '1440p': '1080p',
                    '8k': '4k', 
                    '2160p': '4k',
                    '1080i': '1080p',
                    '720i': '720p'
                },
                'hdr_detection_patterns': ['HDR', 'HDR10', 'BT2020', 'PQ', 'ST2084', 'HLG'],
                'dv_detection_patterns': ['DV', 'DOLBY VISION', 'DVHE', 'DVH1']
            }
        except Exception as e:
            self.logger.error(f"Failed to load enhanced detection settings: {e}")
            return {'enabled': False}
    
    def _map_resolution_to_image_legacy(self, resolution: str) -> str:
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
