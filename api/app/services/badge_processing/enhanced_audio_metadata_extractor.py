"""
Enhanced Audio Metadata Extractor

Extracts comprehensive audio information from Jellyfin metadata using the approach
demonstrated in the jellyfin_audio_info.py script. Provides intelligent audio
stream selection and detailed logging for user visibility.
"""

from typing import Dict, Any, Optional, List
from aphrodite_logging import get_logger


class EnhancedAudioMetadataExtractor:
    """Enhanced audio metadata extraction with intelligent stream selection"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.audio.metadata", service="badge")
    
    def extract_audio_info(self, media_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive audio information from Jellyfin media item.
        
        Returns enriched audio info dict with:
        - Selected stream details
        - All available streams for logging
        - Selection reasoning
        - Badge mapping recommendation
        """
        try:
            item_id = media_item.get('Id', 'Unknown')
            item_name = media_item.get('Name', 'Unknown')
            
            self.logger.info(f"🎧 [AUDIO METADATA] Analyzing audio for: {item_name} (ID: {item_id})")
            
            # Step 1: Extract all audio streams from metadata
            audio_streams = self._extract_all_audio_streams(media_item)
            
            if not audio_streams:
                self.logger.warning(f"❌ [AUDIO METADATA] No audio streams found for: {item_name}")
                return None
            
            # Step 2: Log all available audio streams for user visibility
            self._log_all_audio_streams(audio_streams, item_name)
            
            # Step 3: Select the best audio stream for badge
            selected_stream = self._select_primary_audio_stream(audio_streams)
            
            if not selected_stream:
                self.logger.warning(f"❌ [AUDIO METADATA] Failed to select audio stream for: {item_name}")
                return None
            
            # Step 4: Extract detailed information from selected stream
            audio_info = self._analyze_selected_stream(selected_stream, item_name)
            
            # Step 5: Log selection reasoning and badge mapping
            self._log_selection_summary(audio_info, len(audio_streams), item_name)
            
            return audio_info
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error extracting audio info: {e}", exc_info=True)
            return None
    
    def _extract_all_audio_streams(self, media_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all audio streams from MediaStreams in media item"""
        try:
            # Get MediaStreams directly from media item (most reliable)
            media_streams = media_item.get('MediaStreams', [])
            
            # If no MediaStreams, try MediaSources approach
            if not media_streams:
                media_sources = media_item.get('MediaSources', [])
                if media_sources:
                    media_streams = media_sources[0].get('MediaStreams', [])
            
            # Filter for audio streams only
            audio_streams = [
                stream for stream in media_streams 
                if stream.get('Type') == 'Audio'
            ]
            
            return audio_streams
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error extracting audio streams: {e}")
            return []
    
    def _log_all_audio_streams(self, audio_streams: List[Dict[str, Any]], item_name: str) -> None:
        """Log all available audio streams for user visibility"""
        try:
            self.logger.info(f"🎵 [AUDIO METADATA] Found {len(audio_streams)} audio stream(s) for: {item_name}")
            self.logger.info("=" * 80)
            
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
            return "aac.png"   # Default fallback i, stream in enumerate(audio_streams, 1):
                self.logger.info(f"📻 [AUDIO METADATA] Stream {i}:")
                self.logger.info(f"  └─ Index: {stream.get('Index', 'N/A')}")
                self.logger.info(f"  └─ Codec: {stream.get('Codec', 'N/A')}")
                self.logger.info(f"  └─ Language: {stream.get('Language', 'N/A')}")
                self.logger.info(f"  └─ Display Title: {stream.get('DisplayTitle', 'N/A')}")
                self.logger.info(f"  └─ Channels: {stream.get('Channels', 'N/A')}")
                self.logger.info(f"  └─ Channel Layout: {stream.get('ChannelLayout', 'N/A')}")
                self.logger.info(f"  └─ Is Default: {stream.get('IsDefault', False)}")
                self.logger.info(f"  └─ Is Forced: {stream.get('IsForced', False)}")
                
                # Log additional technical details if available
                if stream.get('BitRate'):
                    bitrate_kbps = int(stream.get('BitRate', 0)) // 1000
                    self.logger.info(f"  └─ Bit Rate: {bitrate_kbps} kbps")
                if stream.get('SampleRate'):
                    self.logger.info(f"  └─ Sample Rate: {stream.get('SampleRate')} Hz")
                if stream.get('Profile'):
                    self.logger.info(f"  └─ Profile: {stream.get('Profile')}")
                if stream.get('Title'):
                    self.logger.info(f"  └─ Title: {stream.get('Title')}")
                    
                self.logger.info("")  # Blank line between streams
            
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error logging audio streams: {e}")
    
    def _select_primary_audio_stream(self, audio_streams: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the best audio stream for badge generation using intelligent scoring.
        Priority: Quality > Default status > Channel count > Bitrate
        """
        try:
            if len(audio_streams) == 1:
                self.logger.info(f"🎯 [AUDIO METADATA] Only one audio stream available, selecting it")
                return audio_streams[0]
            
            self.logger.info(f"🎯 [AUDIO METADATA] Evaluating {len(audio_streams)} audio streams for best quality...")
            
            best_stream = None
            best_score = -1
            
            for i, stream in enumerate(audio_streams):
                score = self._calculate_audio_quality_score(stream)
                
                codec = stream.get('Codec', 'Unknown').upper()
                channels = stream.get('Channels', 0)
                is_default = stream.get('IsDefault', False)
                display_title = stream.get('DisplayTitle', 'N/A')
                
                self.logger.info(f"📊 [AUDIO METADATA] Stream {i+1} evaluation:")
                self.logger.info(f"  └─ Codec: {codec}, Channels: {channels}, Default: {is_default}")
                self.logger.info(f"  └─ Display Title: {display_title}")
                self.logger.info(f"  └─ Quality Score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_stream = stream
                    self.logger.info(f"  └─ ⭐ NEW BEST STREAM (Score: {score})")
                else:
                    self.logger.info(f"  └─ Score {score} < current best {best_score}")
            
            if best_stream:
                selected_codec = best_stream.get('Codec', 'Unknown').upper()
                selected_channels = best_stream.get('Channels', 0)
                selected_title = best_stream.get('DisplayTitle', 'N/A')
                
                self.logger.info(f"🏆 [AUDIO METADATA] SELECTED: {selected_codec} {selected_channels}ch - {selected_title}")
                self.logger.info(f"🏆 [AUDIO METADATA] Final quality score: {best_score}")
            
            return best_stream
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error selecting primary audio stream: {e}")
            return None
    
    def _calculate_audio_quality_score(self, stream: Dict[str, Any]) -> int:
        """
        Calculate quality score for audio stream prioritization.
        Higher score = better quality for badge representation.
        """
        score = 0
        
        codec = stream.get('Codec', '').upper()
        profile = stream.get('Profile', '').upper()
        channels = stream.get('Channels', 0)
        bitrate = stream.get('BitRate', 0)
        is_default = stream.get('IsDefault', False)
        
        # Codec quality scoring (lossless > high-quality lossy > standard lossy)
        codec_scores = {
            'TRUEHD': 1000,     # Dolby TrueHD (lossless)
            'MLP': 1000,        # MLP (TrueHD alternative)
            'DTSMA': 950,       # DTS-HD MA (lossless)
            'DTSHD': 900,       # DTS-HD HR
            'DTS': 800,         # DTS
            'FLAC': 850,        # FLAC (lossless)
            'PCM': 900,         # PCM (lossless)
            'LPCM': 900,        # LPCM (lossless)
            'EAC3': 600,        # Dolby Digital Plus
            'AC3': 400,         # Dolby Digital
            'AAC': 300,         # AAC
            'MP3': 200          # MP3
        }
        
        # Get base codec score
        base_codec = codec.replace('-', '').replace('_', '')
        for codec_key, codec_score in codec_scores.items():
            if codec_key in base_codec:
                score += codec_score
                break
        else:
            # Unknown codec gets low score
            score += 100
        
        # Object-based audio bonuses (premium formats)
        if 'ATMOS' in profile or 'ATMOS' in codec:
            score += 500  # Major Atmos bonus
        elif 'DTS-X' in profile or 'DTSX' in codec or 'DTS:X' in profile:
            score += 450  # Major DTS-X bonus
        
        # Channel count scoring (more channels usually better for home theater)
        if channels >= 8:
            score += 200      # 7.1+ surround
        elif channels >= 6:
            score += 150      # 5.1 surround
        elif channels >= 3:
            score += 75       # 3.0 or 3.1
        elif channels == 2:
            score += 50       # Stereo
        # Mono gets no bonus
        
        # Bitrate bonus (for lossy formats, higher bitrate = better quality)
        if bitrate:
            bitrate_kbps = bitrate // 1000 if bitrate > 1000 else bitrate
            if bitrate_kbps > 1000:
                score += 100  # Very high bitrate
            elif bitrate_kbps > 640:
                score += 50   # High bitrate
            elif bitrate_kbps > 320:
                score += 25   # Medium bitrate
        
        # Default stream bonus (slight preference for default)
        if is_default:
            score += 25
        
        # Lossless format detection bonus
        lossless_indicators = ['TRUEHD', 'MLP', 'FLAC', 'PCM', 'LPCM']
        if any(indicator in codec for indicator in lossless_indicators):
            score += 300
        elif 'DTSMA' in codec or ('DTS' in codec and 'MA' in profile):
            score += 300  # DTS-HD MA is lossless
        
        return score
    
    def _analyze_selected_stream(self, stream: Dict[str, Any], item_name: str) -> Dict[str, Any]:
        """Analyze the selected audio stream and prepare comprehensive info"""
        try:
            # Extract basic properties
            codec = stream.get('Codec', '').upper()
            channels = stream.get('Channels', 2)
            channel_layout = stream.get('ChannelLayout', '').lower()
            profile = stream.get('Profile', '')
            display_title = stream.get('DisplayTitle', '')
            bitrate = stream.get('BitRate', 0)
            sample_rate = stream.get('SampleRate', 0)
            
            # Detect special audio formats
            is_atmos = self._detect_atmos(stream)
            is_dts_x = self._detect_dts_x(stream)
            is_lossless = self._detect_lossless(stream)
            
            # Determine display codec for badge
            display_codec = self._determine_display_codec(codec, profile, is_atmos, is_dts_x)
            
            # Determine badge image mapping
            badge_image = self._map_codec_to_badge_image(display_codec, codec, is_atmos, is_dts_x)
            
            audio_info = {
                'raw_codec': codec,
                'display_codec': display_codec,
                'channels': channels,
                'channel_layout': channel_layout,
                'profile': profile,
                'display_title': display_title,
                'bitrate': bitrate,
                'sample_rate': sample_rate,
                'is_atmos': is_atmos,
                'is_dts_x': is_dts_x,
                'is_lossless': is_lossless,
                'badge_image': badge_image,
                'stream_index': stream.get('Index', 0),
                'is_default': stream.get('IsDefault', False),
                'item_name': item_name
            }
            
            return audio_info
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error analyzing selected stream: {e}")
            return None
    
    def _detect_atmos(self, stream: Dict[str, Any]) -> bool:
        """Detect Dolby Atmos from various metadata fields"""
        check_fields = [
            stream.get('Profile', ''),
            stream.get('Title', ''),
            stream.get('DisplayTitle', ''),
            stream.get('Codec', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        atmos_patterns = ['ATMOS', 'DOLBY ATMOS', 'TRUEHD ATMOS']
        return any(pattern in combined_text for pattern in atmos_patterns)
    
    def _detect_dts_x(self, stream: Dict[str, Any]) -> bool:
        """Detect DTS-X from various metadata fields"""
        check_fields = [
            stream.get('Profile', ''),
            stream.get('Title', ''),
            stream.get('DisplayTitle', ''),
            stream.get('Codec', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        dts_x_patterns = ['DTS-X', 'DTS:X', 'DTSX', 'DTS X']
        return any(pattern in combined_text for pattern in dts_x_patterns)
    
    def _detect_lossless(self, stream: Dict[str, Any]) -> bool:
        """Detect if codec is lossless"""
        codec = stream.get('Codec', '').upper()
        profile = stream.get('Profile', '').upper()
        
        # Known lossless formats
        lossless_codecs = ['TRUEHD', 'MLP', 'FLAC', 'PCM', 'LPCM']
        if any(lossless in codec for lossless in lossless_codecs):
            return True
        
        # DTS-HD MA is lossless
        if 'DTS' in codec and 'MA' in profile:
            return True
        
        return False
    
    def _determine_display_codec(self, codec: str, profile: str, is_atmos: bool, is_dts_x: bool) -> str:
        """Determine the display codec string for badge"""
        # Handle special formats first
        if is_atmos:
            if 'TRUEHD' in codec:
                return 'TrueHD Atmos'
            else:
                return 'Dolby Atmos'
        
        if is_dts_x:
            return 'DTS-X'
        
        # Standard codec mapping
        codec_mapping = {
            'DCA': 'DTS',
            'DTSHD': 'DTS-HD',
            'DTSMA': 'DTS-HD MA',
            'TRUEHD': 'TrueHD',
            'AC3': 'Dolby Digital',
            'EAC3': 'Dolby Digital Plus',
            'AAC': 'AAC',
            'MP3': 'MP3',
            'FLAC': 'FLAC',
            'PCM': 'PCM',
            'LPCM': 'LPCM'
        }
        
        # Check for DTS variants with profile
        if codec == 'DTS' or 'DTS' in codec:
            profile_upper = profile.upper()
            if 'MA' in profile_upper:
                return 'DTS-HD MA'
            elif 'HD' in profile_upper:
                return 'DTS-HD'
            else:
                return 'DTS'
        
        return codec_mapping.get(codec, codec)
    
    def _map_codec_to_badge_image(self, display_codec: str, raw_codec: str, is_atmos: bool, is_dts_x: bool) -> str:
        """Map audio codec to badge image filename based on available images"""
        # Special format mappings (highest priority)
        if is_atmos:
            return "TrueHD-Atmos.png"
        
        if is_dts_x:
            return "DTS-X.png"
        
        # Standard codec mappings
        codec_upper = display_codec.upper()
        
        if "TRUEHD" in codec_upper:
            return "TrueHD.png"
        elif "DTS-HD" in codec_upper:
            return "DTS-HD.png"
        elif "DTS" in codec_upper:
            return "DTS-HD.png"  # Use DTS-HD image for DTS
        elif "DOLBY DIGITAL PLUS" in codec_upper or "EAC3" in raw_codec:
            return "DigitalPlus.png"
        elif "DOLBY DIGITAL" in codec_upper or "AC3" in raw_codec:
            return "dolby-digital.png"
        elif "AAC" in codec_upper:
            return "aac.png"
        elif "FLAC" in codec_upper:
            return "flac.png"  # If available
        elif "PCM" in codec_upper or "LPCM" in codec_upper:
            return "pcm.png"   # If available
        else:
            return "aac.png"   # Default fallback
    
    def _log_selection_summary(self, audio_info: Dict[str, Any], total_streams: int, item_name: str) -> None:
        """Log final selection summary and badge mapping for user visibility"""
        try:
            self.logger.info("🎯 [AUDIO METADATA] FINAL SELECTION SUMMARY:")
            self.logger.info("=" * 80)
            self.logger.info(f"📺 Item: {item_name}")
            self.logger.info(f"🔍 Evaluated: {total_streams} audio stream(s)")
            self.logger.info(f"🎵 Selected Stream Index: {audio_info.get('stream_index', 'N/A')}")
            self.logger.info(f"🎧 Raw Codec: {audio_info.get('raw_codec', 'N/A')}")
            self.logger.info(f"🏷️  Display Codec: {audio_info.get('display_codec', 'N/A')}")
            self.logger.info(f"🔊 Channels: {audio_info.get('channels', 'N/A')} ({audio_info.get('channel_layout', 'N/A')})")
            
            if audio_info.get('bitrate'):
                bitrate_kbps = audio_info.get('bitrate', 0) // 1000
                self.logger.info(f"📊 Bitrate: {bitrate_kbps} kbps")
            
            if audio_info.get('sample_rate'):
                self.logger.info(f"🎼 Sample Rate: {audio_info.get('sample_rate')} Hz")
            
            # Special format indicators
            special_formats = []
            if audio_info.get('is_atmos'):
                special_formats.append('Dolby Atmos')
            if audio_info.get('is_dts_x'):
                special_formats.append('DTS-X')
            if audio_info.get('is_lossless'):
                special_formats.append('Lossless')
            
            if special_formats:
                self.logger.info(f"⭐ Special Formats: {', '.join(special_formats)}")
            
            self.logger.info(f"🖼️  Badge Image: {audio_info.get('badge_image', 'N/A')}")
            self.logger.info(f"✅ Is Default Stream: {audio_info.get('is_default', False)}")
            
            # Log the display title for reference
            display_title = audio_info.get('display_title', 'N/A')
            if display_title != 'N/A':
                self.logger.info(f"📋 Jellyfin Display Title: {display_title}")
            
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO METADATA] Error logging selection summary: {e}")
