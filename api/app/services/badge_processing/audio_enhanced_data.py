"""
Enhanced Audio Data Handling
Handles getting enhanced audio info from various sources.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from aphrodite_logging import get_logger

from .audio_enhanced_components import EnhancedAudioComponents


class EnhancedAudioDataHandler:
    """Handles enhanced audio data retrieval and processing"""
    
    def __init__(self, components: EnhancedAudioComponents):
        self.logger = get_logger("aphrodite.audio.data", service="badge")
        self.components = components
    
    async def get_audio_info(
        self,
        jellyfin_id: Optional[str],
        use_demo_data: bool,
        poster_path: str,
        settings: Dict[str, Any]
    ):
        """Get audio info using enhanced detection system"""
        try:
            if not self.components.enabled:
                self.logger.debug("🔄 [ENHANCED AUDIO] Components disabled, using legacy")
                return None
            
            # Check enhanced detection settings
            enhanced_settings = settings.get('enhanced_detection', {})
            if not enhanced_settings.get('enabled', True):
                self.logger.debug("🔄 [ENHANCED AUDIO] Enhanced detection disabled in settings")
                return None
            
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [ENHANCED AUDIO] Getting enhanced audio for ID: {jellyfin_id}")
                return await self._get_jellyfin_audio(jellyfin_id)
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [ENHANCED AUDIO] Using enhanced demo audio data")
                return self._get_demo_audio(poster_path)
            
            self.logger.warning("⚠️ [ENHANCED AUDIO] No audio source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [ENHANCED AUDIO] Audio detection error: {e}", exc_info=True)
            return None
    
    async def _get_jellyfin_audio(self, jellyfin_id: str):
        """Get enhanced audio info from Jellyfin"""
        try:
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item
            media_item = await jellyfin_service.get_item_details(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"📺 [ENHANCED AUDIO] Media type: {media_type}")
            
            if media_type == 'Movie':
                # For movies: extract audio directly
                audio_info = self.components.detector.extract_audio_info(media_item)
                self.logger.debug(f"🎬 [ENHANCED AUDIO] Movie audio: {audio_info}")
                return audio_info
            
            elif media_type in ['Series', 'Season']:
                # For TV: check cache first, then use parallel processing
                cached_audio = self.components.cache.get_series_audio(jellyfin_id)
                if cached_audio:
                    self.logger.debug(f"💾 [ENHANCED AUDIO] Cache hit for series: {jellyfin_id}")
                    return cached_audio
                
                # Use parallel processing for series
                audio_info = await self.components.parallel_processor.get_series_audio_parallel(
                    jellyfin_service, jellyfin_id, max_episodes=5
                )
                
                if audio_info:
                    # Cache the result
                    self.components.cache.cache_series_audio(jellyfin_id, audio_info)
                    self.logger.debug(f"📺 [ENHANCED AUDIO] TV series audio (parallel): {audio_info}")
                
                return audio_info
            
            elif media_type == 'Episode':
                # For episodes: extract audio directly
                audio_info = self.components.detector.extract_audio_info(media_item)
                self.logger.debug(f"📻 [ENHANCED AUDIO] Episode audio: {audio_info}")
                return audio_info
            
            else:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [ENHANCED AUDIO] Jellyfin audio error: {e}", exc_info=True)
            return None
    
    def _get_demo_audio(self, poster_path: str):
        """Get enhanced demo audio info"""
        import hashlib
        from .audio_types import AudioFormat, ChannelLayout, AudioInfo
        
        # Create consistent hash from poster filename
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # Enhanced demo audio list with AudioInfo objects
        demo_audio_configs = [
            ("TRUEHD", AudioFormat.DOLBY_ATMOS, 8, ChannelLayout.ATMOS, True, True),
            ("DTS", AudioFormat.DTS_X, 8, ChannelLayout.DTS_X, True, True),
            ("TRUEHD", AudioFormat.DOLBY_TRUEHD, 8, ChannelLayout.SURROUND_7_1, True, False),
            ("DTS", AudioFormat.DTS_HD_MA, 8, ChannelLayout.SURROUND_7_1, True, False),
            ("EAC3", AudioFormat.DOLBY_DIGITAL_PLUS, 6, ChannelLayout.SURROUND_5_1, False, False),
            ("DTS", AudioFormat.DTS_HD, 6, ChannelLayout.SURROUND_5_1, False, False),
            ("AC3", AudioFormat.DOLBY_DIGITAL, 6, ChannelLayout.SURROUND_5_1, False, False),
            ("AAC", AudioFormat.AAC, 2, ChannelLayout.STEREO, False, False)
        ]
        
        # Select config based on hash
        codec, format_type, channels, layout, lossless, object_based = demo_audio_configs[hash_value % len(demo_audio_configs)]
        
        audio_info = AudioInfo(
            codec=codec,
            format=format_type,
            channels=channels,
            channel_layout=layout,
            is_lossless=lossless,
            is_object_based=object_based,
            bitrate=768 if lossless else 640,
            sample_rate=48000,
            bit_depth=24 if lossless else 16
        )
        
        self.logger.debug(f"🎭 [ENHANCED AUDIO] Demo audio for {poster_name}: {audio_info}")
        return audio_info
