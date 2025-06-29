"""
Pure V2 Audio Badge Processor

Completely V2-native audio badge processing with no V1 dependencies.
Clear logging for system differentiation.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from .renderers import UnifiedBadgeRenderer
from app.core.database import async_session_factory


class V2AudioBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 audio badge processor - no V1 dependencies"""
    
    def __init__(self):
        super().__init__("audio")
        self.logger = get_logger("aphrodite.badge.audio.v2", service="badge")
        self.renderer = UnifiedBadgeRenderer()
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with audio badge using pure V2 system"""
        try:
            self.logger.info(f"🎧 [V2 AUDIO] PROCESSOR STARTED for: {poster_path}")
            self.logger.info(f"🎧 [V2 AUDIO] Jellyfin ID: {jellyfin_id}")
            self.logger.info(f"🎧 [V2 AUDIO] Use demo data: {use_demo_data}")
            
            # Load audio badge settings from PostgreSQL
            settings = await self._load_v2_settings(db_session)
            if not settings:
                self.logger.error("❌ [V2 AUDIO] Failed to load settings from PostgreSQL")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load V2 audio badge settings"
                )
            
            self.logger.info("✅ [V2 AUDIO] Settings loaded from PostgreSQL")
            
            # Get audio codec data using pure V2 methods
            codec_data = await self._get_v2_audio_codec(jellyfin_id, use_demo_data, poster_path)
            if not codec_data:
                self.logger.warning("⚠️ [V2 AUDIO] No audio codec detected, skipping badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.info(f"📊 [V2 AUDIO] Codec detected: {codec_data}")
            
            # Create audio badge using V2 renderer
            result_path = await self._create_v2_audio_badge(
                poster_path, codec_data, settings, output_path
            )
            
            if result_path:
                self.logger.info(f"✅ [V2 AUDIO] PROCESSOR COMPLETED: {result_path}")
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["audio"],
                    success=True
                )
            else:
                self.logger.error(f"❌ [V2 AUDIO] Badge creation failed")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="V2 audio badge creation failed"
                )
                
        except Exception as e:
            self.logger.error(f"🚨 [V2 AUDIO] PROCESSOR EXCEPTION: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=f"V2 audio processor error: {str(e)}"
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
    ) -> List[PosterResult]:
        """Process multiple posters with V2 audio badges"""
        results = []
        
        self.logger.info(f"🎧 [V2 AUDIO] BULK PROCESSING {len(poster_paths)} posters")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"🎧 [V2 AUDIO] Processing {i+1}/{len(poster_paths)}: {poster_path}")
            
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
                self.logger.info(f"🎧 [V2 AUDIO] Processed {i+1}/{len(poster_paths)} badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"🎧 [V2 AUDIO] BULK COMPLETED: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_v2_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load audio badge settings from V2 PostgreSQL database only"""
        try:
            self.logger.debug("🗄️ [V2 AUDIO] Loading settings from PostgreSQL")
            
            # Load from v2 database
            if db_session:
                settings = await badge_settings_service.get_audio_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "audio"):
                    self.logger.info("✅ [V2 AUDIO] Settings loaded from PostgreSQL (provided session)")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_audio_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "audio"):
                            self.logger.info("✅ [V2 AUDIO] Settings loaded from PostgreSQL (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"⚠️ [V2 AUDIO] Database connection failed: {db_error}")
            
            # Use V2 default settings as fallback (no YAML files)
            self.logger.info("⚠️ [V2 AUDIO] Using V2 default settings (PostgreSQL unavailable)")
            return self._get_v2_default_settings()
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AUDIO] Error loading settings: {e}", exc_info=True)
            return self._get_v2_default_settings()
    
    def _get_v2_default_settings(self) -> Dict[str, Any]:
        """Get V2 default audio badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True,
                "general_badge_position": "top-right",
                "general_edge_padding": 30
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
                "image_padding": 15,
                "codec_image_directory": "images/audio"
            }
        }
    
    async def _get_v2_audio_codec(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str
    ) -> Optional[str]:
        """Get audio codec using pure V2 methods only"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [V2 AUDIO] Getting real codec for ID: {jellyfin_id}")
                codec = await self._get_v2_jellyfin_codec(jellyfin_id)
                if codec and codec != "UNKNOWN":
                    self.logger.debug(f"✅ [V2 AUDIO] Real codec found: {codec}")
                    return codec
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [V2 AUDIO] Using demo codec data")
                return self._get_v2_demo_codec(poster_path)
            
            self.logger.warning("⚠️ [V2 AUDIO] No codec source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AUDIO] Error getting codec: {e}", exc_info=True)
            return None
    
    async def _get_v2_jellyfin_codec(self, jellyfin_id: str) -> Optional[str]:
        """Get real audio codec using pure V2 Jellyfin service (NO V1 AGGREGATOR)"""
        try:
            self.logger.debug(f"🌐 [V2 AUDIO] Querying Jellyfin for ID: {jellyfin_id}")
            
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item with fallback for API compatibility
            media_item = await jellyfin_service.get_item_details(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [V2 AUDIO] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"📺 [V2 AUDIO] Media type: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"🎬 [V2 AUDIO] Movie codec: {codec}")
                return codec
            
            elif media_type in ['Series', 'Season']:
                # For TV: PURE V2 episode sampling (NO V1 AGGREGATOR)
                codec = await self._get_v2_tv_series_codec(jellyfin_id, jellyfin_service)
                self.logger.debug(f"📺 [V2 AUDIO] TV series codec: {codec}")
                return codec
            
            elif media_type == 'Episode':
                # For episodes: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"📻 [V2 AUDIO] Episode codec: {codec}")
                return codec
            
            else:
                self.logger.warning(f"⚠️ [V2 AUDIO] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AUDIO] Jellyfin codec error: {e}", exc_info=True)
            return None
    
    async def _get_v2_tv_series_codec(self, jellyfin_id: str, jellyfin_service) -> Optional[str]:
        """Get TV series dominant codec using PURE V2 methods (no V1 aggregator)"""
        try:
            self.logger.debug(f"📺 [V2 AUDIO] Sampling TV series episodes for: {jellyfin_id}")
            
            # Get series episodes using V2 Jellyfin service
            episodes = await jellyfin_service.get_series_episodes(jellyfin_id, limit=10)
            
            if not episodes:
                self.logger.warning(f"⚠️ [V2 AUDIO] No episodes found for series: {jellyfin_id}")
                return "EAC3 6.0"  # Reasonable default for TV series
            
            self.logger.debug(f"📺 [V2 AUDIO] Found {len(episodes)} episodes to sample")
            
            # Sample codecs from episodes
            codecs = []
            for i, episode in enumerate(episodes[:5]):  # Sample first 5 episodes
                try:
                    codec = await jellyfin_service.get_audio_codec_info(episode)
                    if codec and codec != "UNKNOWN":
                        codecs.append(codec)
                        self.logger.debug(f"📻 [V2 AUDIO] Episode {i+1} codec: {codec}")
                except Exception as ep_error:
                    self.logger.warning(f"⚠️ [V2 AUDIO] Episode {i+1} codec error: {ep_error}")
                    continue
            
            if not codecs:
                self.logger.warning(f"⚠️ [V2 AUDIO] No valid codecs from episodes")
                return "EAC3 6.0"  # Reasonable default
            
            # Determine dominant codec using simple frequency count
            codec_counts = {}
            for codec in codecs:
                codec_counts[codec] = codec_counts.get(codec, 0) + 1
            
            # Get most common codec
            dominant_codec = max(codec_counts.items(), key=lambda x: x[1])[0]
            
            self.logger.debug(f"📊 [V2 AUDIO] Codec frequency: {codec_counts}")
            self.logger.debug(f"🏆 [V2 AUDIO] Dominant codec: {dominant_codec}")
            
            return dominant_codec
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AUDIO] TV series codec error: {e}", exc_info=True)
            return "EAC3 6.0"  # Fallback default
    
    def _get_v2_demo_codec(self, poster_path: str) -> str:
        """Get demo audio codec using V2 consistent algorithm"""
        import hashlib
        
        # Create consistent hash from poster filename
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # V2 demo codec list
        demo_codecs = [
            "DTS-HD MA 7.1",
            "TRUEHD ATMOS",
            "DOLBY DIGITAL PLUS 5.1",
            "DTS-X",
            "TRUEHD 7.1",
            "ATMOS",
            "EAC3 6.0",
            "AC3 5.1"
        ]
        
        # Select codec based on hash (consistent for same poster)
        selected_codec = demo_codecs[hash_value % len(demo_codecs)]
        
        self.logger.debug(f"🎭 [V2 AUDIO] Demo codec for {poster_name}: {selected_codec}")
        return selected_codec
    
    async def _create_v2_audio_badge(
        self,
        poster_path: str,
        codec_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create audio badge using pure V2 renderer"""
        try:
            self.logger.debug(f"🎨 [V2 AUDIO] Creating badge for codec: {codec_data}")
            
            # Determine output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate V2 preview path
                poster_name = Path(poster_path).name
                final_output_path = f"/app/api/static/preview/{poster_name}"
            
            # Create badge using V2 renderer
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', False)
            
            if image_badges_enabled:
                # Try image badge first
                self.logger.debug(f"🖼️ [V2 AUDIO] Attempting image badge for: {codec_data}")
                badge = self.renderer.create_image_badge(
                    self._map_codec_to_image(codec_data),
                    settings,
                    "audio"
                )
                
                if not badge:
                    # Fallback to text badge
                    self.logger.debug(f"📝 [V2 AUDIO] Image failed, using text badge")
                    badge = self.renderer.create_text_badge(codec_data, settings, "audio")
            else:
                # Use text badge
                self.logger.debug(f"📝 [V2 AUDIO] Creating text badge")
                badge = self.renderer.create_text_badge(codec_data, settings, "audio")
            
            if not badge:
                self.logger.error(f"❌ [V2 AUDIO] Badge creation failed")
                return None
            
            # Apply badge to poster
            success = self.renderer.apply_badge_to_poster(
                poster_path, badge, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [V2 AUDIO] Badge applied successfully: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [V2 AUDIO] Badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [V2 AUDIO] Badge creation error: {e}", exc_info=True)
            return None
    
    def _map_codec_to_image(self, codec: str) -> str:
        """Map audio codec to image filename"""
        # Simple codec to image mapping
        codec_upper = codec.upper()
        
        if "DTS-HD MA" in codec_upper or "DTS-HD" in codec_upper:
            return "dts-hd-ma.png"
        elif "TRUEHD" in codec_upper and "ATMOS" in codec_upper:
            return "truehd-atmos.png"
        elif "TRUEHD" in codec_upper:
            return "truehd.png"
        elif "ATMOS" in codec_upper:
            return "atmos.png"
        elif "DTS-X" in codec_upper:
            return "dts-x.png"
        elif "DTS" in codec_upper:
            return "dts.png"
        elif "DOLBY" in codec_upper or "EAC3" in codec_upper:
            return "dolby-digital-plus.png"
        elif "AC3" in codec_upper:
            return "dolby-digital.png"
        else:
            return "audio-generic.png"
