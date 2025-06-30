"""
Enhanced resolution detection from Jellyfin metadata.
Provides intelligent HDR, Dolby Vision, and format detection.
"""

import re
from typing import Dict, Any, Optional, List
from aphrodite_logging import get_logger

from .resolution_types import (
    ResolutionInfo, ColorSpace, VideoRange, 
    DetectionPatterns, FallbackRules
)


class EnhancedResolutionDetector:
    """
    Advanced resolution detection using comprehensive metadata analysis.
    Handles HDR, Dolby Vision, HDR10+, and complex resolution scenarios.
    """
    
    def __init__(self, patterns: Optional[DetectionPatterns] = None):
        self.logger = get_logger("aphrodite.resolution.detector", service="badge")
        self.patterns = patterns or DetectionPatterns.get_default()
        self.fallback_rules = FallbackRules.get_default()
    
    def extract_resolution_info(self, media_item: Dict[str, Any]) -> Optional[ResolutionInfo]:
        """
        Extract comprehensive resolution info from Jellyfin media item.
        
        Args:
            media_item: Jellyfin media item with MediaStreams
            
        Returns:
            ResolutionInfo object or None if no video stream found
        """
        try:
            # Find primary video stream
            video_stream = self._find_primary_video_stream(media_item)
            if not video_stream:
                self.logger.warning("No video stream found in media item")
                return None
            
            # Extract basic resolution
            width = video_stream.get('Width', 0)
            height = video_stream.get('Height', 0)
            
            if not width or not height:
                self.logger.warning(f"Invalid resolution: {width}x{height}")
                return None
            
            # Map to base resolution string
            base_resolution = self._map_height_to_resolution(height, width)
            
            # Detect advanced video properties
            is_hdr = self._detect_hdr(video_stream)
            is_dolby_vision = self._detect_dolby_vision(video_stream)
            is_hdr_plus = self._detect_hdr_plus(video_stream)
            
            # Extract technical metadata
            codec = self._extract_codec(video_stream)
            color_space = self._extract_color_space(video_stream)
            video_range = self._extract_video_range(video_stream)
            bit_depth = self._extract_bit_depth(video_stream)
            bitrate = self._extract_bitrate(video_stream)
            profile = video_stream.get('Profile', '')
            
            resolution_info = ResolutionInfo(
                height=height,
                width=width,
                base_resolution=base_resolution,
                is_hdr=is_hdr,
                is_dolby_vision=is_dolby_vision,
                is_hdr_plus=is_hdr_plus,
                codec=codec,
                color_space=color_space,
                video_range=video_range,
                bit_depth=bit_depth,
                bitrate=bitrate,
                profile=profile
            )
            
            self.logger.debug(f"Extracted resolution: {resolution_info.get_technical_summary()}")
            return resolution_info
            
        except Exception as e:
            self.logger.error(f"Resolution extraction error: {e}", exc_info=True)
            return None
    
    def _find_primary_video_stream(self, media_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the primary video stream from media item"""
        media_streams = media_item.get('MediaStreams', [])
        
        # Look for primary video stream first
        for stream in media_streams:
            if stream.get('Type') == 'Video' and stream.get('IsDefault', False):
                return stream
        
        # Fallback to first video stream
        for stream in media_streams:
            if stream.get('Type') == 'Video':
                return stream
        
        return None
    
    def _map_height_to_resolution(self, height: int, width: int = 0) -> str:
        """Map pixel dimensions to resolution string with comprehensive coverage"""
        # For widescreen/ultrawide content, use both width and height for better accuracy
        # This fixes issues where widescreen content was incorrectly classified to lower resolutions
        
        if height >= 4320:
            return "8k"      # 8K UHD (7680×4320)
        elif height >= 2160:
            return "4k"      # 4K UHD (3840×2160)
        elif height >= 1440:
            return "1440p"   # QHD (2560×1440)
        elif height >= 1080:
            return "1080p"   # Full HD (1920×1080)
        elif height >= 720:
            # Handle widescreen 1080p content (e.g., 1928×820, 2048×858)
            # Only upgrade to 1080p if:
            # 1. Width suggests 1080p content (≥1800px) AND
            # 2. Height is above standard 720p (>720) to avoid misclassifying 1920×720
            if width >= 1800 and height > 720:
                return "1080p"
            else:
                return "720p"    # HD (1280×720)
        elif height >= 576:
            # Handle widescreen 720p content (rare but possible)
            # If width suggests 720p content (≥1200px), keep as 720p
            if width >= 1200:  # Threshold for widescreen 720p
                return "720p"
            else:
                return "576p"    # PAL DVD (720×576)
        elif height >= 480:
            # Handle widescreen 576p content
            if width >= 1000:  # Threshold for widescreen 576p
                return "576p"
            else:
                return "480p"    # NTSC DVD (720×480)
        else:
            return f"{height}p"  # Custom resolution
    
    def _detect_hdr(self, video_stream: Dict[str, Any]) -> bool:
        """Enhanced HDR detection using multiple metadata fields"""
        # Check multiple fields for HDR indicators
        check_fields = [
            video_stream.get('VideoRange', ''),
            video_stream.get('ColorSpace', ''),
            video_stream.get('ColorTransfer', ''),
            video_stream.get('ColorPrimaries', ''),
            video_stream.get('Profile', ''),
            video_stream.get('DisplayTitle', ''),
            video_stream.get('Title', '')
        ]
        
        # Combine all fields for pattern matching
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Check against HDR patterns
        for pattern in self.patterns.hdr_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.debug(f"HDR detected via pattern: {pattern}")
                return True
        
        # Check bit depth (10+ bit often indicates HDR)
        bit_depth = self._extract_bit_depth(video_stream)
        if bit_depth and bit_depth >= 10:
            # Additional checks to avoid false positives
            if any(keyword in combined_text for keyword in ['BT2020', 'PQ', 'HLG']):
                self.logger.debug(f"HDR detected via {bit_depth}-bit + color space")
                return True
        
        return False
    
    def _detect_dolby_vision(self, video_stream: Dict[str, Any]) -> bool:
        """Enhanced Dolby Vision detection"""
        check_fields = [
            video_stream.get('VideoRange', ''),
            video_stream.get('Profile', ''),
            video_stream.get('DisplayTitle', ''),
            video_stream.get('Title', ''),
            video_stream.get('Codec', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Check against Dolby Vision patterns
        for pattern in self.patterns.dv_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.debug(f"Dolby Vision detected via pattern: {pattern}")
                return True
        
        return False
    
    def _detect_hdr_plus(self, video_stream: Dict[str, Any]) -> bool:
        """Detect HDR10+ content"""
        check_fields = [
            video_stream.get('VideoRange', ''),
            video_stream.get('Profile', ''),
            video_stream.get('DisplayTitle', ''),
            video_stream.get('Title', '')
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Check against HDR10+ patterns
        for pattern in self.patterns.hdr_plus_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.debug(f"HDR10+ detected via pattern: {pattern}")
                return True
        
        return False
    
    def _extract_codec(self, video_stream: Dict[str, Any]) -> Optional[str]:
        """Extract video codec information"""
        codec = video_stream.get('Codec', '')
        if codec:
            # Normalize common codec names
            codec_lower = codec.lower()
            if 'h264' in codec_lower or 'avc' in codec_lower:
                return 'h264'
            elif 'h265' in codec_lower or 'hevc' in codec_lower:
                return 'hevc'
            elif 'av1' in codec_lower:
                return 'av1'
            else:
                return codec_lower
        return None
    
    def _extract_color_space(self, video_stream: Dict[str, Any]) -> ColorSpace:
        """Extract color space information"""
        color_space = video_stream.get('ColorSpace', '').upper()
        color_primaries = video_stream.get('ColorPrimaries', '').upper()
        
        combined = f"{color_space} {color_primaries}"
        
        if 'BT2020' in combined or 'BT.2020' in combined:
            return ColorSpace.BT2020
        elif 'BT709' in combined or 'BT.709' in combined:
            return ColorSpace.BT709
        else:
            return ColorSpace.UNKNOWN
    
    def _extract_video_range(self, video_stream: Dict[str, Any]) -> VideoRange:
        """Extract video range information"""
        video_range = video_stream.get('VideoRange', '').upper()
        
        if 'HDR' in video_range:
            return VideoRange.HDR
        elif video_range in ['LIMITED', 'TV', 'BROADCAST']:
            return VideoRange.SDR
        elif video_range in ['FULL', 'PC']:
            return VideoRange.SDR
        else:
            return VideoRange.UNKNOWN
    
    def _extract_bit_depth(self, video_stream: Dict[str, Any]) -> Optional[int]:
        """Extract bit depth from video stream"""
        bit_depth = video_stream.get('BitDepth')
        if bit_depth and isinstance(bit_depth, (int, str)):
            try:
                return int(bit_depth)
            except (ValueError, TypeError):
                pass
        
        # Try to extract from profile or other fields
        profile = video_stream.get('Profile', '')
        if '10bit' in profile.lower() or '10-bit' in profile.lower():
            return 10
        elif '8bit' in profile.lower() or '8-bit' in profile.lower():
            return 8
        elif '12bit' in profile.lower() or '12-bit' in profile.lower():
            return 12
        
        return None
    
    def _extract_bitrate(self, video_stream: Dict[str, Any]) -> Optional[int]:
        """Extract bitrate in kbps"""
        bitrate = video_stream.get('BitRate')
        if bitrate and isinstance(bitrate, (int, str)):
            try:
                # Convert to kbps if in bps
                bitrate_int = int(bitrate)
                if bitrate_int > 100000:  # Likely in bps
                    return bitrate_int // 1000
                else:  # Already in kbps
                    return bitrate_int
            except (ValueError, TypeError):
                pass
        return None
