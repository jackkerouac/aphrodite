"""
Legacy Audio Handling
Handles legacy V2 audio detection methods for fallback.
"""

from typing import Optional
from pathlib import Path
from aphrodite_logging import get_logger


class LegacyAudioHandler:
    """Handles legacy V2 audio detection methods"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.audio.legacy", service="badge")
    
    async def get_audio_codec(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str
    ) -> Optional[str]:
        """Get audio codec using legacy V2 methods"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [LEGACY AUDIO] Getting codec for ID: {jellyfin_id}")
                codec = await self._get_jellyfin_codec(jellyfin_id)
                if codec and codec != "UNKNOWN":
                    self.logger.debug(f"✅ [LEGACY AUDIO] Codec found: {codec}")
                    return codec
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [LEGACY AUDIO] Using demo codec data")
                return self._get_demo_codec(poster_path)
            
            self.logger.warning("⚠️ [LEGACY AUDIO] No codec source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [LEGACY AUDIO] Error getting codec: {e}", exc_info=True)
            return None
    
    async def _get_jellyfin_codec(self, jellyfin_id: str) -> Optional[str]:
        """Get real audio codec using legacy V2 Jellyfin service"""
        try:
            self.logger.debug(f"🌐 [LEGACY AUDIO] Querying Jellyfin for ID: {jellyfin_id}")
            
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item with fallback for API compatibility
            media_item = await jellyfin_service.get_item_details(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [LEGACY AUDIO] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"📺 [LEGACY AUDIO] Media type: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"🎬 [LEGACY AUDIO] Movie codec: {codec}")
                return codec
            
            elif media_type in ['Series', 'Season']:
                # For TV: legacy episode sampling
                codec = await self._get_tv_series_codec(jellyfin_id, jellyfin_service)
                self.logger.debug(f"📺 [LEGACY AUDIO] TV series codec: {codec}")
                return codec
            
            elif media_type == 'Episode':
                # For episodes: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"📻 [LEGACY AUDIO] Episode codec: {codec}")
                return codec
            
            else:
                self.logger.warning(f"⚠️ [LEGACY AUDIO] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [LEGACY AUDIO] Jellyfin codec error: {e}", exc_info=True)
            return None
    
    async def _get_tv_series_codec(self, jellyfin_id: str, jellyfin_service) -> Optional[str]:
        """Get TV series dominant codec using legacy V2 methods"""
        try:
            self.logger.debug(f"📺 [LEGACY AUDIO] Sampling TV series episodes for: {jellyfin_id}")
            
            # Get series episodes using V2 Jellyfin service
            episodes = await jellyfin_service.get_series_episodes(jellyfin_id, limit=10)
            
            if not episodes:
                self.logger.warning(f"⚠️ [LEGACY AUDIO] No episodes found for series: {jellyfin_id}")
                return "EAC3 6.0"  # Reasonable default for TV series
            
            self.logger.debug(f"📺 [LEGACY AUDIO] Found {len(episodes)} episodes to sample")
            
            # Sample codecs from episodes
            codecs = []
            for i, episode in enumerate(episodes[:5]):  # Sample first 5 episodes
                try:
                    codec = await jellyfin_service.get_audio_codec_info(episode)
                    if codec and codec != "UNKNOWN":
                        codecs.append(codec)
                        self.logger.debug(f"📻 [LEGACY AUDIO] Episode {i+1} codec: {codec}")
                except Exception as ep_error:
                    self.logger.warning(f"⚠️ [LEGACY AUDIO] Episode {i+1} codec error: {ep_error}")
                    continue
            
            if not codecs:
                self.logger.warning(f"⚠️ [LEGACY AUDIO] No valid codecs from episodes")
                return "EAC3 6.0"  # Reasonable default
            
            # Determine dominant codec using simple frequency count
            codec_counts = {}
            for codec in codecs:
                codec_counts[codec] = codec_counts.get(codec, 0) + 1
            
            # Get most common codec
            dominant_codec = max(codec_counts.items(), key=lambda x: x[1])[0]
            
            self.logger.debug(f"📊 [LEGACY AUDIO] Codec frequency: {codec_counts}")
            self.logger.debug(f"🏆 [LEGACY AUDIO] Dominant codec: {dominant_codec}")
            
            return dominant_codec
            
        except Exception as e:
            self.logger.error(f"❌ [LEGACY AUDIO] TV series codec error: {e}", exc_info=True)
            return "EAC3 6.0"  # Fallback default
    
    def _get_demo_codec(self, poster_path: str) -> str:
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
        
        self.logger.debug(f"🎭 [LEGACY AUDIO] Demo codec for {poster_name}: {selected_codec}")
        return selected_codec
    
    def map_codec_to_image(self, codec: str) -> str:
        """Map audio codec to image filename (legacy mapping)"""
        # Simple codec to image mapping
        codec_upper = codec.upper()
        
        if "DTS-HD MA" in codec_upper or "DTS-HD" in codec_upper:
            return "DTS-HD.png"
        elif "TRUEHD" in codec_upper and "ATMOS" in codec_upper:
            return "TrueHD-Atmos.png"
        elif "TRUEHD" in codec_upper:
            return "TrueHD.png"
        elif "ATMOS" in codec_upper:
            return "Atmos.png"
        elif "DTS-X" in codec_upper:
            return "DTS-X.png"
        elif "DTS" in codec_upper:
            return "DTS-HD.png"
        elif "DOLBY" in codec_upper or "EAC3" in codec_upper:
            return "DigitalPlus.png"
        elif "AC3" in codec_upper:
            return "dolby-digital.png"
        else:
            return "aac.png"
