#!/usr/bin/env python3
"""
Standalone Enhanced Audio Test

Tests the enhanced audio extraction without any complex dependencies.
"""

from typing import Dict, Any, Optional, List


class StandaloneEnhancedAudioExtractor:
    """Standalone version of enhanced audio metadata extractor for testing"""
    
    def __init__(self):
        self.name = "Standalone Enhanced Audio Extractor"
    
    def extract_audio_info(self, media_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract comprehensive audio information from Jellyfin media item"""
        try:
            item_id = media_item.get('Id', 'Unknown')
            item_name = media_item.get('Name', 'Unknown')
            
            print(f"🎧 [AUDIO METADATA] Analyzing audio for: {item_name} (ID: {item_id})")
            
            # Extract all audio streams from metadata
            audio_streams = self._extract_all_audio_streams(media_item)
            
            if not audio_streams:
                print(f"❌ [AUDIO METADATA] No audio streams found for: {item_name}")
                return None
            
            # Log all available audio streams
            self._log_all_audio_streams(audio_streams, item_name)
            
            # Select the best audio stream
            selected_stream = self._select_primary_audio_stream(audio_streams)
            
            if not selected_stream:
                print(f"❌ [AUDIO METADATA] Failed to select audio stream for: {item_name}")
                return None
            
            # Extract detailed information from selected stream
            audio_info = self._analyze_selected_stream(selected_stream, item_name)
            
            # Log selection summary
            self._log_selection_summary(audio_info, len(audio_streams), item_name)
            
            return audio_info
            
        except Exception as e:
            print(f"❌ [AUDIO METADATA] Error extracting audio info: {e}")
            return None
    
    def _extract_all_audio_streams(self, media_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all audio streams from MediaStreams in media item"""
        try:
            # Get MediaStreams directly from media item
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
            print(f"❌ [AUDIO METADATA] Error extracting audio streams: {e}")
            return []
    
    def _log_all_audio_streams(self, audio_streams: List[Dict[str, Any]], item_name: str) -> None:
        """Log all available audio streams for user visibility"""
        try:
            print(f"🎵 [AUDIO METADATA] Found {len(audio_streams)} audio stream(s) for: {item_name}")
            print("=" * 80)
            
            for i, stream in enumerate(audio_streams, 1):
                print(f"📻 [AUDIO METADATA] Stream {i}:")
                print(f"  └─ Index: {stream.get('Index', 'N/A')}")
                print(f"  └─ Codec: {stream.get('Codec', 'N/A')}")
                print(f"  └─ Language: {stream.get('Language', 'N/A')}")
                print(f"  └─ Display Title: {stream.get('DisplayTitle', 'N/A')}")
                print(f"  └─ Channels: {stream.get('Channels', 'N/A')}")
                print(f"  └─ Channel Layout: {stream.get('ChannelLayout', 'N/A')}")
                print(f"  └─ Is Default: {stream.get('IsDefault', False)}")
                print(f"  └─ Is Forced: {stream.get('IsForced', False)}")
                
                # Log additional technical details if available
                if stream.get('BitRate'):
                    bitrate_kbps = int(stream.get('BitRate', 0)) // 1000
                    print(f"  └─ Bit Rate: {bitrate_kbps} kbps")
                if stream.get('SampleRate'):
                    print(f"  └─ Sample Rate: {stream.get('SampleRate')} Hz")
                if stream.get('Profile'):
                    print(f"  └─ Profile: {stream.get('Profile')}")
                if stream.get('Title'):
                    print(f"  └─ Title: {stream.get('Title')}")
                    
                print()  # Blank line between streams
            
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ [AUDIO METADATA] Error logging audio streams: {e}")
    
    def _select_primary_audio_stream(self, audio_streams: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best audio stream for badge generation using intelligent scoring"""
        try:
            if len(audio_streams) == 1:
                print(f"🎯 [AUDIO METADATA] Only one audio stream available, selecting it")
                return audio_streams[0]
            
            print(f"🎯 [AUDIO METADATA] Evaluating {len(audio_streams)} audio streams for best quality...")
            
            best_stream = None
            best_score = -1
            
            for i, stream in enumerate(audio_streams):
                score = self._calculate_audio_quality_score(stream)
                
                codec = stream.get('Codec', 'Unknown').upper()
                channels = stream.get('Channels', 0)
                is_default = stream.get('IsDefault', False)
                display_title = stream.get('DisplayTitle', 'N/A')
                
                print(f"📊 [AUDIO METADATA] Stream {i+1} evaluation:")
                print(f"  └─ Codec: {codec}, Channels: {channels}, Default: {is_default}")
                print(f"  └─ Display Title: {display_title}")
                print(f"  └─ Quality Score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_stream = stream
                    print(f"  └─ ⭐ NEW BEST STREAM (Score: {score})")
                else:
                    print(f"  └─ Score {score} < current best {best_score}")
            
            if best_stream:
                selected_codec = best_stream.get('Codec', 'Unknown').upper()
                selected_channels = best_stream.get('Channels', 0)
                selected_title = best_stream.get('DisplayTitle', 'N/A')
                
                print(f"🏆 [AUDIO METADATA] SELECTED: {selected_codec} {selected_channels}ch - {selected_title}")
                print(f"🏆 [AUDIO METADATA] Final quality score: {best_score}")
            
            return best_stream
            
        except Exception as e:
            print(f"❌ [AUDIO METADATA] Error selecting primary audio stream: {e}")
            return None
    
    def _calculate_audio_quality_score(self, stream: Dict[str, Any]) -> int:
        """Calculate quality score for audio stream prioritization"""
        score = 0
        
        codec = stream.get('Codec', '').upper()
        profile = stream.get('Profile', '').upper()
        channels = stream.get('Channels', 0)
        bitrate = stream.get('BitRate', 0)
        is_default = stream.get('IsDefault', False)
        
        # Codec quality scoring
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
            score += 100
        
        # Object-based audio bonuses
        if 'ATMOS' in profile or 'ATMOS' in codec:
            score += 500  # Major Atmos bonus
        elif 'DTS-X' in profile or 'DTSX' in codec or 'DTS:X' in profile:
            score += 450  # Major DTS-X bonus
        
        # Channel count scoring
        if channels >= 8:
            score += 200      # 7.1+ surround
        elif channels >= 6:
            score += 150      # 5.1 surround
        elif channels >= 3:
            score += 75       # 3.0 or 3.1
        elif channels == 2:
            score += 50       # Stereo
        
        # Bitrate bonus
        if bitrate:
            bitrate_kbps = bitrate // 1000 if bitrate > 1000 else bitrate
            if bitrate_kbps > 1000:
                score += 100  # Very high bitrate
            elif bitrate_kbps > 640:
                score += 50   # High bitrate
            elif bitrate_kbps > 320:
                score += 25   # Medium bitrate
        
        # Default stream bonus
        if is_default:
            score += 25
        
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
            print(f"❌ [AUDIO METADATA] Error analyzing selected stream: {e}")
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
        """Map audio codec to badge image filename"""
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
            print("🎯 [AUDIO METADATA] FINAL SELECTION SUMMARY:")
            print("=" * 80)
            print(f"📺 Item: {item_name}")
            print(f"🔍 Evaluated: {total_streams} audio stream(s)")
            print(f"🎵 Selected Stream Index: {audio_info.get('stream_index', 'N/A')}")
            print(f"🎧 Raw Codec: {audio_info.get('raw_codec', 'N/A')}")
            print(f"🏷️  Display Codec: {audio_info.get('display_codec', 'N/A')}")
            print(f"🔊 Channels: {audio_info.get('channels', 'N/A')} ({audio_info.get('channel_layout', 'N/A')})")
            
            if audio_info.get('bitrate'):
                bitrate_kbps = audio_info.get('bitrate', 0) // 1000
                print(f"📊 Bitrate: {bitrate_kbps} kbps")
            
            if audio_info.get('sample_rate'):
                print(f"🎼 Sample Rate: {audio_info.get('sample_rate')} Hz")
            
            # Special format indicators
            special_formats = []
            if audio_info.get('is_atmos'):
                special_formats.append('Dolby Atmos')
            if audio_info.get('is_dts_x'):
                special_formats.append('DTS-X')
            if audio_info.get('is_lossless'):
                special_formats.append('Lossless')
            
            if special_formats:
                print(f"⭐ Special Formats: {', '.join(special_formats)}")
            
            print(f"🖼️  Badge Image: {audio_info.get('badge_image', 'N/A')}")
            print(f"✅ Is Default Stream: {audio_info.get('is_default', False)}")
            
            # Log the display title for reference
            display_title = audio_info.get('display_title', 'N/A')
            if display_title != 'N/A':
                print(f"📋 Jellyfin Display Title: {display_title}")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ [AUDIO METADATA] Error logging selection summary: {e}")


def test_basic_extraction():
    """Test basic audio extraction functionality"""
    print("🧪 Testing Standalone Enhanced Audio Extractor...")
    print("=" * 50)
    
    # Test with AAC audio data (from your script output)
    aac_media = {
        "Id": "test-aac",
        "Name": "Test AAC Media",
        "Type": "Movie",
        "MediaStreams": [
            {
                "Codec": "aac",
                "Language": "eng",
                "DisplayTitle": "Sound Media Handler - English - AAC - Stereo - Default",
                "ChannelLayout": "stereo",
                "BitRate": 192000,
                "Channels": 2,
                "SampleRate": 48000,
                "IsDefault": True,
                "Profile": "LC",
                "Type": "Audio",
                "Index": 1
            }
        ]
    }
    
    # Test with DTS audio data (from your script output)
    dts_media = {
        "Id": "test-dts",
        "Name": "Test DTS Media", 
        "Type": "Movie",
        "MediaStreams": [
            {
                "Codec": "dts",
                "Language": "eng",
                "DisplayTitle": "English - DTS - 5.1 - Default",
                "ChannelLayout": "5.1",
                "BitRate": 1536000,
                "Channels": 6,
                "SampleRate": 48000,
                "IsDefault": True,
                "Profile": "DTS",
                "Type": "Audio",
                "Index": 2
            }
        ]
    }
    
    extractor = StandaloneEnhancedAudioExtractor()
    
    # Test AAC
    print("🎵 Testing AAC extraction...")
    aac_result = extractor.extract_audio_info(aac_media)
    if aac_result:
        print(f"✅ AAC Result: {aac_result.get('display_codec')} → {aac_result.get('badge_image')}")
    else:
        print("❌ AAC extraction failed")
    
    print("\n" + "="*50 + "\n")
    
    # Test DTS
    print("🎵 Testing DTS extraction...")
    dts_result = extractor.extract_audio_info(dts_media)
    if dts_result:
        print(f"✅ DTS Result: {dts_result.get('display_codec')} → {dts_result.get('badge_image')}")
    else:
        print("❌ DTS extraction failed")
    
    print()
    print("✅ Standalone extraction test completed!")
    
    return True


if __name__ == "__main__":
    test_basic_extraction()
