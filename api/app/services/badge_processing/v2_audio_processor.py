"""
Pure V2 Audio Badge Processor - Enhanced with Advanced Detection

Completely V2-native audio badge processing with enhanced detection capabilities.
Modularized for maintainability and enhanced with Dolby Atmos, DTS-X detection.
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

# Enhanced audio components
from .audio_enhanced_components import EnhancedAudioComponents
from .audio_enhanced_data import EnhancedAudioDataHandler
from .audio_legacy_handler import LegacyAudioHandler
from .audio_badge_creator import AudioBadgeCreator


class V2AudioBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 audio badge processor with enhanced detection capabilities"""
    
    def __init__(self):
        super().__init__("audio")
        self.logger = get_logger("aphrodite.badge.audio.v2", service="badge")
        self.renderer = UnifiedBadgeRenderer()
        
        # Initialize modular components
        self.enhanced_components = EnhancedAudioComponents()
        self.enhanced_data_handler = EnhancedAudioDataHandler(self.enhanced_components)
        self.legacy_handler = LegacyAudioHandler()
        self.badge_creator = AudioBadgeCreator(
            self.renderer, 
            self.enhanced_components, 
            self.legacy_handler
        )
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with audio badge using enhanced V2 system"""
        try:
            self.logger.info(f"🎧 [V2 AUDIO] PROCESSOR STARTED for: {poster_path}")
            self.logger.info(f"🎧 [V2 AUDIO] Jellyfin ID: {jellyfin_id}")
            self.logger.info(f"🎧 [V2 AUDIO] Use demo data: {use_demo_data}")
            
            if self.enhanced_components.enabled:
                self.logger.info("🚀 [V2 AUDIO] ✅ Enhanced detection enabled")
            else:
                self.logger.info("⚠️ [V2 AUDIO] Using legacy detection")
            
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
            
            # Get audio data using enhanced or legacy methods
            audio_data = await self._get_audio_data(jellyfin_id, use_demo_data, poster_path, settings)
            
            if not audio_data:
                self.logger.warning("⚠️ [V2 AUDIO] No audio data detected, skipping badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.info(f"📊 [V2 AUDIO] Audio detected: {audio_data}")
            
            # Create audio badge
            result_path = await self.badge_creator.create_badge(
                poster_path, audio_data, settings, output_path
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
    
    async def _get_audio_data(self, jellyfin_id, use_demo_data, poster_path, settings):
        """Get audio data using enhanced or legacy methods"""
        # Try enhanced detection first
        if self.enhanced_components.enabled:
            audio_data = await self.enhanced_data_handler.get_audio_info(
                jellyfin_id, use_demo_data, poster_path, settings
            )
            if audio_data:
                return audio_data
        
        # Fallback to legacy detection
        return await self.legacy_handler.get_audio_codec(
            jellyfin_id, use_demo_data, poster_path
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
        """Get V2 default audio badge settings with enhanced detection"""
        base_settings = {
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
                "enable_image_badges": True,
                "fallback_to_text": True,
                "image_padding": 15,
                "codec_image_directory": "images/codec",
                "image_mapping": {
                    "Dolby Atmos": "TrueHD-Atmos.png",
                    "DTS-X": "DTS-X.png",
                    "TrueHD": "TrueHD.png",
                    "DTS-HD MA": "DTS-HD.png",
                    "Dolby Digital Plus": "DigitalPlus.png",
                    "Dolby Digital": "dolby-digital.png",
                    "DTS": "DTS-HD.png",
                    "AAC": "aac.png"
                }
            }
        }
        
        # Add enhanced detection settings if components available
        if self.enhanced_components.enabled:
            base_settings["enhanced_detection"] = {
                "enabled": True,
                "fallback_rules": {
                    "dolby_atmos": "truehd",
                    "dts_x": "dts_hd_ma",
                    "dolby_digital_plus": "dolby_digital",
                    "dts_hd_ma": "dts_hd",
                    "dts_hd": "dts"
                },
                "atmos_detection_patterns": [
                    "ATMOS", "DOLBY ATMOS", "TRUEHD ATMOS", "Atmos"
                ],
                "dts_x_detection_patterns": [
                    "DTS-X", "DTS:X", "DTSX", "DTS X"
                ],
                "performance": {
                    "enable_parallel_processing": True,
                    "enable_caching": True,
                    "cache_ttl_hours": 24,
                    "max_episodes_to_sample": 5
                }
            }
        
        return base_settings
    
    # Enhanced component access methods for diagnostics
    def get_enhanced_components_status(self) -> Dict[str, Any]:
        """Get status of enhanced components for diagnostics"""
        return self.enhanced_components.get_status()
    
    def clear_audio_cache(self) -> bool:
        """Clear audio cache (for diagnostics)"""
        return self.enhanced_components.clear_cache()
