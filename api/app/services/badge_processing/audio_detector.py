"""
Enhanced audio detection from Jellyfin metadata.
Provides intelligent Dolby Atmos, DTS-X, and advanced format detection.
"""

import re
from typing import Dict, Any, Optional, List
from aphrodite_logging import get_logger

from .audio_types import (
    AudioInfo, AudioFormat, ChannelLayout, 
    DetectionPatterns
)


class EnhancedAudioDetector:
    """
    Advanced audio detection using comprehensive metadata analysis.
    Based on successful patterns from Enhanced Resolution Detection.
    """
    
    def __init__(self, patterns: Optional[DetectionPatterns] = None):
        self.logger = get_logger("aphrodite.audio.detector", service="badge")
        self.patterns = patterns or DetectionPatterns.get_default()
    
    def extract_audio_info(self, media_item: Dict[str, Any]) -> Optional[AudioInfo]:
        """
        Extract comprehensive audio info from Jellyfin media item.
        Mirror of resolution detector's extract_resolution_info().
        """
        try:
            # Find primary audio stream
            audio_stream = self._find_primary_audio_stream(media_item)
            if not audio_stream:
                self.logger.warning("No audio stream found in media item")
                return None
            
            # Extract basic audio properties
            codec = audio_stream.get('Codec', '').upper()
            channels = audio_stream.get('Channels', 2)
            profile = audio_stream.get('Profile', '')
            
            # Detect advanced audio properties
            audio_format = self._detect_audio_format(audio_stream)
            channel_layout = self._detect_channel_layout(channels, audio_format)
            is_lossless = self._detect_lossless(audio_stream)
            is_object_based = self._detect_object_based(audio_stream)
            
            # Extract technical metadata
            bitrate = self._extract_bitrate(audio_stream)
            sample_rate = audio_stream.get('SampleRate')
            bit_depth = audio_stream.get('BitDepth')
            
            audio_info = AudioInfo(
                codec=codec,
                format=audio_format,
                channels=channels,
                channel_layout=channel_layout,
                is_lossless=is_lossless,
                is_object_based=is_object_based,
                bitrate=bitrate,
                sample_rate=sample_rate,
                bit_depth=bit_depth,
                profile=profile
            )
            
            self.logger.debug(f"Extracted audio: {audio_info.get_technical_summary()}")
            
            # Log the selected audio stream for debugging
            stream_info = f"{codec} | {audio_format.value.lower().replace('_', ' ')} | {channels}ch"
            if channel_layout != ChannelLayout.UNKNOWN:
                stream_info += f" | {channel_layout.value}"
            if bitrate:
                stream_info += f" | {bitrate}kbps"
            if sample_rate:
                stream_info += f" | {sample_rate}Hz"
            self.logger.debug(f"Selected audio stream details: {stream_info}")
            return audio_info
            
        except Exception as e:
            self.logger.error(f"Audio extraction error: {e}", exc_info=True)
            return None
    
    def _find_primary_audio_stream(self, media_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the highest quality audio stream from media item for badge purposes"""
        media_streams = media_item.get('MediaStreams', [])
        
        # Get all audio streams
        audio_streams = [stream for stream in media_streams if stream.get('Type') == 'Audio']
        if not audio_streams:
            return None
        
        # If only one audio stream, return it
        if len(audio_streams) == 1:
            return audio_streams[0]
        
        # Find the highest quality audio stream using priority scoring
        best_stream = None
        best_score = -1
        
        for stream in audio_streams:
            score = self._calculate_audio_quality_score(stream)
            self.logger.debug(f"Audio stream quality score: {score} for {stream.get('Codec', 'Unknown')} {stream.get('Profile', '')} {stream.get('Channels', 0)}ch")
            
            if score > best_score:
                best_score = score
                best_stream = stream
        
        if best_stream:
            self.logger.debug(f"Selected highest quality audio: {best_stream.get('Codec', 'Unknown')} {best_stream.get('Profile', '')} {best_stream.get('Channels', 0)}ch (score: {best_score})")
        
        return best_stream
    
    def _calculate_audio_quality_score(self, audio_stream: Dict[str, Any]) -> int:
        """Calculate quality score for audio stream to find the best one"""
        score = 0
        
        codec = audio_stream.get('Codec', '').upper()
        profile = audio_stream.get('Profile', '').upper()
        channels = audio_stream.get('Channels', 0)
        bitrate = self._extract_bitrate(audio_stream) or 0
        
        # Codec scoring (higher is better)
        codec_scores = {
            'TRUEHD': 1000,  # Dolby TrueHD (lossless)
            'MLP': 1000,     # MLP (TrueHD alternative)
            'DTS': 800,      # DTS variants
            'DTSHD': 900,    # DTS-HD
            'DTSMA': 950,    # DTS-HD MA
            'EAC3': 600,     # Dolby Digital Plus
            'AC3': 400,      # Dolby Digital
            'AAC': 300,      # AAC
            'MP3': 200,      # MP3
            'FLAC': 850,     # FLAC (lossless)
            'PCM': 900,      # PCM (lossless)
            'LPCM': 900      # LPCM (lossless)
        }
        
        # Get base codec score
        base_codec = codec.replace('-', '').replace('_', '')
        for codec_key, codec_score in codec_scores.items():
            if codec_key in base_codec:
                score += codec_score
                break
        
        # Object-based audio bonus (Atmos, DTS-X)
        if 'ATMOS' in profile or 'ATMOS' in codec:
            score += 500  # Atmos bonus
        elif 'DTS-X' in profile or 'DTSX' in codec:
            score += 450  # DTS-X bonus
        
        # Channel count bonus
        if channels >= 8:
            score += 200  # 7.1+ channels
        elif channels >= 6:
            score += 100  # 5.1 channels
        elif channels >= 2:
            score += 50   # Stereo
        
        # High bitrate bonus (for lossy formats)
        if bitrate > 1000:
            score += 100  # Very high bitrate
        elif bitrate > 640:
            score += 50   # High bitrate
        
        # Lossless format bonus
        if self._detect_lossless(audio_stream):
            score += 300
        
        return score
    
    def _detect_audio_format(self, audio_stream: Dict[str, Any]) -> AudioFormat:
        """Enhanced audio format detection using multiple metadata fields"""
        # Check for advanced formats first (most specific)
        if self._detect_atmos(audio_stream):
            return AudioFormat.DOLBY_ATMOS
        
        if self._detect_dts_x(audio_stream):
            return AudioFormat.DTS_X
        
        # Check codec-based detection
        codec = audio_stream.get('Codec', '').upper()
        
        # TrueHD detection
        if 'TRUEHD' in codec or codec == 'MLP':
            return AudioFormat.DOLBY_TRUEHD
        
        # DTS variants
        if 'DTS' in codec:
            profile = audio_stream.get('Profile', '').upper()
            if 'MA' in profile or 'DTS-HD MA' in profile:
                return AudioFormat.DTS_HD_MA
            elif 'HD' in profile or 'DTS-HD' in profile:
                return AudioFormat.DTS_HD
            else:
                return AudioFormat.DTS
        
        # Dolby Digital variants
        if codec in ['EAC3', 'EAC-3']:
            return AudioFormat.DOLBY_DIGITAL_PLUS
        elif codec in ['AC3', 'AC-3']:
            return AudioFormat.DOLBY_DIGITAL
        
        # Other common formats
        if codec == 'AAC':
            return AudioFormat.AAC
        elif codec == 'MP3':
            return AudioFormat.MP3
        elif codec == 'FLAC':
            return AudioFormat.FLAC
        elif codec in ['PCM', 'LPCM']:
            return AudioFormat.PCM
        
        return AudioFormat.UNKNOWN
    
    def _detect_atmos(self, audio_stream: Dict[str, Any]) -> bool:
        """Enhanced Dolby Atmos detection"""
        # Check multiple fields for Atmos indicators
        check_fields = [
            audio_stream.get('Profile', ''),
            audio_stream.get('Title', ''),
            audio_stream.get('DisplayTitle', ''),
            audio_stream.get('Codec', ''),
            audio_stream.get('Language', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Check against Atmos patterns
        for pattern in self.patterns.atmos_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.debug(f"Atmos detected via pattern: {pattern}")
                return True
        
        return False
    
    def _detect_dts_x(self, audio_stream: Dict[str, Any]) -> bool:
        """Enhanced DTS-X detection"""
        # Check multiple fields for DTS-X indicators
        check_fields = [
            audio_stream.get('Profile', ''),
            audio_stream.get('Title', ''),
            audio_stream.get('DisplayTitle', ''),
            audio_stream.get('Codec', ''),
            audio_stream.get('Language', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Check against DTS-X patterns
        for pattern in self.patterns.dts_x_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.debug(f"DTS-X detected via pattern: {pattern}")
                return True
        
        return False
    
    def _detect_lossless(self, audio_stream: Dict[str, Any]) -> bool:
        """Detect if audio format is lossless"""
        codec = audio_stream.get('Codec', '').upper()
        profile = audio_stream.get('Profile', '').upper()
        
        # Known lossless formats
        lossless_codecs = ['TRUEHD', 'MLP', 'FLAC', 'PCM', 'LPCM']
        if any(lossless in codec for lossless in lossless_codecs):
            return True
        
        # DTS-HD MA is lossless
        if 'DTS' in codec and 'MA' in profile:
            return True
        
        return False
    
    def _detect_object_based(self, audio_stream: Dict[str, Any]) -> bool:
        """Detect if audio format is object-based (Atmos/DTS-X)"""
        return self._detect_atmos(audio_stream) or self._detect_dts_x(audio_stream)
    
    def _detect_channel_layout(self, channels: int, audio_format: AudioFormat) -> ChannelLayout:
        """Detect channel layout from channel count and format"""
        # Object-based formats
        if audio_format == AudioFormat.DOLBY_ATMOS:
            return ChannelLayout.ATMOS
        elif audio_format == AudioFormat.DTS_X:
            return ChannelLayout.DTS_X
        
        # Channel-based layouts
        if channels == 1:
            return ChannelLayout.MONO
        elif channels == 2:
            return ChannelLayout.STEREO
        elif channels == 6:
            return ChannelLayout.SURROUND_5_1
        elif channels == 8:
            return ChannelLayout.SURROUND_7_1
        
        return ChannelLayout.UNKNOWN
    
    def _extract_bitrate(self, audio_stream: Dict[str, Any]) -> Optional[int]:
        """Extract bitrate in kbps"""
        bitrate = audio_stream.get('BitRate')
        if bitrate and isinstance(bitrate, (int, str)):
            try:
                # Convert to kbps if in bps
                bitrate_int = int(bitrate)
                if bitrate_int > 10000:  # Likely in bps
                    return bitrate_int // 1000
                else:  # Already in kbps
                    return bitrate_int
            except (ValueError, TypeError):
                pass
        return None
