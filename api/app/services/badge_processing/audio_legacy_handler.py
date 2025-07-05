"""
Enhanced Audio Legacy Handler
Handles enhanced audio detection methods with comprehensive metadata analysis.
Replaces the legacy V2 audio detection with intelligent stream selection and detailed logging.
"""

from typing import Optional
from pathlib import Path
from aphrodite_logging import get_logger


class LegacyAudioHandler:
    """Handles enhanced audio detection methods with metadata analysis"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.audio.enhanced_legacy", service="badge")
    
    async def get_audio_codec(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str
    ) -> Optional[str]:
        """Get audio codec using enhanced metadata analysis"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [ENHANCED AUDIO] Getting codec for ID: {jellyfin_id}")
                codec = await self._get_jellyfin_codec_enhanced(jellyfin_id)
                if codec and codec != "UNKNOWN":
                    self.logger.debug(f"✅ [ENHANCED AUDIO] Codec found: {codec}")
                    return codec
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [ENHANCED AUDIO] Using demo codec data")
                return self._get_demo_codec(poster_path)
            
            self.logger.warning("⚠️ [ENHANCED AUDIO] No codec source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [ENHANCED AUDIO] Error getting codec: {e}", exc_info=True)
            return None
    
    async def _get_jellyfin_codec_enhanced(self, jellyfin_id: str) -> Optional[str]:
        """Get real audio codec using enhanced metadata analysis"""
        try:
            self.logger.debug(f"🌐 [ENHANCED AUDIO] Querying Jellyfin for ID: {jellyfin_id}")
            
            # Import V2 Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Get media item with enhanced metadata fields
            media_item = await jellyfin_service.get_item_details(jellyfin_id)
            if not media_item:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] Media item not found: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            media_name = media_item.get('Name', 'Unknown')
            self.logger.info(f"📺 [ENHANCED AUDIO] Analyzing: {media_name} (Type: {media_type})") 
            
            if media_type == 'Movie':
                # For movies: get enhanced audio info directly
                audio_info = await jellyfin_service.get_enhanced_audio_info(media_item)
                if audio_info:
                    codec = audio_info.get('display_codec')
                    self.logger.info(f"🎬 [ENHANCED AUDIO] Movie codec: {codec}")
                    return codec
                else:
                    # Fallback to legacy method
                    codec = await jellyfin_service.get_audio_codec_info(media_item)
                    self.logger.info(f"🎬 [ENHANCED AUDIO] Movie codec (fallback): {codec}")
                    return codec
            
            elif media_type in ['Series', 'Season']:
                # For TV: enhanced episode sampling
                codec = await self._get_tv_series_codec_enhanced(jellyfin_id, jellyfin_service, media_name)
                self.logger.info(f"📺 [ENHANCED AUDIO] TV series codec: {codec}")
                return codec
            
            elif media_type == 'Episode':
                # For episodes: get enhanced audio info directly
                audio_info = await jellyfin_service.get_enhanced_audio_info(media_item)
                if audio_info:
                    codec = audio_info.get('display_codec')
                    self.logger.info(f"📻 [ENHANCED AUDIO] Episode codec: {codec}")
                    return codec
                else:
                    # Fallback to legacy method
                    codec = await jellyfin_service.get_audio_codec_info(media_item)
                    self.logger.info(f"📻 [ENHANCED AUDIO] Episode codec (fallback): {codec}")
                    return codec
            
            else:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] Unsupported media type: {media_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ [ENHANCED AUDIO] Jellyfin codec error: {e}", exc_info=True)
            return None
    
    async def _get_tv_series_codec_enhanced(self, jellyfin_id: str, jellyfin_service, series_name: str) -> Optional[str]:
        """Get TV series dominant codec using enhanced metadata analysis"""
        try:
            self.logger.info(f"📺 [ENHANCED AUDIO] Analyzing TV series episodes for: {series_name}")
            
            # Get series episodes using V2 Jellyfin service
            episodes = await jellyfin_service.get_series_episodes(jellyfin_id, limit=10)
            
            if not episodes:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] No episodes found for series: {series_name}")
                return "Dolby Digital Plus"  # Better default for modern TV series
            
            self.logger.info(f"📺 [ENHANCED AUDIO] Found {len(episodes)} episodes to sample")
            
            # Sample audio info from episodes using enhanced analysis
            audio_infos = []
            codecs = []
            
            for i, episode in enumerate(episodes[:5]):  # Sample first 5 episodes
                try:
                    episode_name = episode.get('Name', f'Episode {i+1}')
                    self.logger.debug(f"🔍 [ENHANCED AUDIO] Analyzing episode: {episode_name}")
                    
                    # Try enhanced analysis first
                    audio_info = await jellyfin_service.get_enhanced_audio_info(episode)
                    if audio_info:
                        codec = audio_info.get('display_codec')
                        if codec:
                            audio_infos.append(audio_info)
                            codecs.append(codec)
                            
                            # Log detailed episode analysis
                            channels = audio_info.get('channels', 'N/A')
                            is_atmos = audio_info.get('is_atmos', False)
                            is_dts_x = audio_info.get('is_dts_x', False)
                            is_lossless = audio_info.get('is_lossless', False)
                            bitrate = audio_info.get('bitrate', 0)
                            
                            special_flags = []
                            if is_atmos: special_flags.append('Atmos')
                            if is_dts_x: special_flags.append('DTS-X')
                            if is_lossless: special_flags.append('Lossless')
                            
                            special_info = f" [{', '.join(special_flags)}]" if special_flags else ""
                            bitrate_info = f" @{bitrate//1000}kbps" if bitrate > 0 else ""
                            
                            self.logger.info(f"📻 [ENHANCED AUDIO] Episode {i+1}: {codec} {channels}ch{special_info}{bitrate_info}")
                            continue
                    
                    # Fallback to legacy method if enhanced fails
                    codec = await jellyfin_service.get_audio_codec_info(episode)
                    if codec and codec != "UNKNOWN":
                        codecs.append(codec)
                        self.logger.info(f"📻 [ENHANCED AUDIO] Episode {i+1}: {codec} (fallback method)")
                        
                except Exception as ep_error:
                    self.logger.warning(f"⚠️ [ENHANCED AUDIO] Episode {i+1} analysis error: {ep_error}")
                    continue
            
            if not codecs:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] No valid codecs from episodes")
                return "Dolby Digital Plus"  # Modern default
            
            # Determine dominant codec using quality-weighted frequency count
            codec_scores = {}
            for codec in codecs:
                # Weight higher quality codecs more heavily
                weight = self._get_codec_quality_weight(codec)
                codec_scores[codec] = codec_scores.get(codec, 0) + weight
            
            # Get highest-scoring codec
            dominant_codec = max(codec_scores.items(), key=lambda x: x[1])[0]
            
            self.logger.info(f"📊 [ENHANCED AUDIO] Series codec analysis for {series_name}:")
            self.logger.info("=" * 60)
            for codec, score in sorted(codec_scores.items(), key=lambda x: x[1], reverse=True):
                count = codecs.count(codec)
                self.logger.info(f"  🎵 {codec}: {count} episodes, quality score: {score}")
            self.logger.info("=" * 60)
            
            self.logger.info(f"🏆 [ENHANCED AUDIO] Selected dominant codec for {series_name}: {dominant_codec}")
            
            return dominant_codec
            
        except Exception as e:
            self.logger.error(f"❌ [ENHANCED AUDIO] TV series codec error: {e}", exc_info=True)
            return "Dolby Digital Plus"  # Fallback default
    
    def _get_codec_quality_weight(self, codec: str) -> int:
        """Get quality weight for codec scoring in TV series analysis"""
        codec_upper = codec.upper()
        
        # Premium formats get highest weights
        if 'ATMOS' in codec_upper:
            return 10
        elif 'DTS-X' in codec_upper:
            return 9
        elif 'TRUEHD' in codec_upper:
            return 8
        elif 'DTS-HD' in codec_upper:
            return 7
        elif 'DTS' in codec_upper:
            return 6
        elif 'DOLBY DIGITAL PLUS' in codec_upper or 'EAC3' in codec_upper:
            return 5
        elif 'DOLBY DIGITAL' in codec_upper or 'AC3' in codec_upper:
            return 4
        elif 'AAC' in codec_upper:
            return 3
        elif 'FLAC' in codec_upper:
            return 7  # Lossless but uncommon for TV
        else:
            return 2  # Unknown/other codecs
    
    def _get_demo_codec(self, poster_path: str) -> str:
        """Get demo audio codec using enhanced V2 algorithm"""
        import hashlib
        
        # Create consistent hash from poster filename
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # Enhanced demo codec list with modern formats
        demo_codecs = [
            "TrueHD Atmos",
            "DTS-X",
            "DTS-HD MA", 
            "TrueHD",
            "DTS-HD",
            "Dolby Digital Plus",
            "DTS",
            "Dolby Digital",
            "AAC"
        ]
        
        # Select codec based on hash (consistent for same poster)
        selected_codec = demo_codecs[hash_value % len(demo_codecs)]
        
        self.logger.info(f"🎭 [ENHANCED AUDIO] Demo codec for {poster_name}: {selected_codec}")
        return selected_codec
    
    def map_codec_to_image(self, codec: str) -> str:
        """Map audio codec to image filename with enhanced mapping"""
        # Enhanced codec to image mapping
        codec_upper = codec.upper()
        
        # Special formats first (most specific)
        if "TRUEHD" in codec_upper and "ATMOS" in codec_upper:
            return "TrueHD-Atmos.png"
        elif "ATMOS" in codec_upper:
            return "TrueHD-Atmos.png"  # Use TrueHD-Atmos for any Atmos
        elif "DTS-X" in codec_upper:
            return "DTS-X.png"
        
        # Lossless formats
        elif "TRUEHD" in codec_upper:
            return "TrueHD.png"
        elif "DTS-HD MA" in codec_upper:
            return "DTS-HD.png"
        elif "DTS-HD" in codec_upper:
            return "DTS-HD.png"
        
        # Standard formats
        elif "DTS" in codec_upper:
            return "DTS-HD.png"  # Use DTS-HD image for standard DTS
        elif "DOLBY DIGITAL PLUS" in codec_upper or "EAC3" in codec_upper:
            return "DigitalPlus.png"
        elif "DOLBY DIGITAL" in codec_upper or "AC3" in codec_upper:
            return "dolby-digital.png"
        elif "AAC" in codec_upper:
            return "aac.png"
        elif "FLAC" in codec_upper:
            return "flac.png"  # If available
        elif "PCM" in codec_upper or "LPCM" in codec_upper:
            return "pcm.png"   # If available
        else:
            self.logger.debug(f"Unknown codec for image mapping: {codec}, using AAC fallback")
            return "aac.png"   # Default fallback
