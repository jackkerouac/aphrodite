"""
Enhanced resolution detection from Jellyfin metadata.
Provides intelligent HDR, Dolby Vision, and format detection with filename parsing.
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
    Now includes filename parsing for improved accuracy (user suggestion).
    """
    
    def __init__(self, patterns: Optional[DetectionPatterns] = None):
        self.logger = get_logger("aphrodite.resolution.detector", service="badge")
        self.patterns = patterns or DetectionPatterns.get_default()
        self.fallback_rules = FallbackRules.get_default()
    
    def extract_resolution_info(self, media_item: Dict[str, Any]) -> Optional[ResolutionInfo]:
        """Extract comprehensive resolution info from Jellyfin media item with filename parsing"""
        try:
            # Step 1: Try filename parsing first (user's suggestion)
            filename_resolution = self._parse_filename_for_resolution(media_item)
            
            # Step 2: Find primary video stream
            video_stream = self._find_primary_video_stream(media_item)
            if not video_stream:
                # If we have filename resolution but no video stream, trust the filename
                if filename_resolution:
                    self.logger.info(f"Using filename resolution (no video stream): {filename_resolution}")
                    return filename_resolution
                self.logger.warning("No video stream found in media item")
                return None
            
            # Step 3: Extract basic resolution from video stream
            width = video_stream.get('Width', 0)
            height = video_stream.get('Height', 0)
            
            if not width or not height:
                # If video stream has no dimensions, use filename if available
                if filename_resolution:
                    self.logger.info(f"Using filename resolution (no dimensions): {filename_resolution}")
                    return filename_resolution
                self.logger.warning(f"Invalid resolution: {width}x{height}")
                return None
            
            # Step 4: Cross-validate filename with video stream dimensions
            stream_resolution = self._map_dimensions_to_resolution(height, width)
            
            if filename_resolution:
                filename_base = filename_resolution.base_resolution
                if filename_base == stream_resolution:
                    # Filename and stream agree, use filename (more complete info)
                    self.logger.debug(f"Filename and stream resolution agree: {filename_base}")
                    final_resolution_info = filename_resolution
                    # Update with actual dimensions
                    final_resolution_info.width = width
                    final_resolution_info.height = height
                elif self._resolutions_compatible(filename_base, stream_resolution):
                    # Compatible resolutions, prefer stream dimensions with filename HDR info
                    self.logger.debug(f"Using stream resolution {stream_resolution} with filename HDR info")
                    final_resolution_info = filename_resolution
                    final_resolution_info.base_resolution = stream_resolution
                    final_resolution_info.width = width
                    final_resolution_info.height = height
                else:
                    # Conflict - trust video stream dimensions but log the discrepancy
                    self.logger.warning(f"Resolution conflict: filename={filename_base}, stream={stream_resolution}, using stream")
                    final_resolution_info = None  # Will be created below
            else:
                final_resolution_info = None  # Will be created below
            
            # Step 5: Create ResolutionInfo from video stream if not done above
            if not final_resolution_info:
                base_resolution = stream_resolution
                
                # Detect advanced video properties from stream
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
                
                final_resolution_info = ResolutionInfo(
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
            
            self.logger.debug(f"Final resolution: {final_resolution_info.get_technical_summary()}")
            return final_resolution_info
            
        except Exception as e:
            self.logger.error(f"Resolution extraction error: {e}", exc_info=True)
            return None
    
    def _parse_filename_for_resolution(self, media_item: Dict[str, Any]) -> Optional[ResolutionInfo]:
        """Parse filename for resolution, HDR, and Dolby Vision information (user's suggestion)"""
        try:
            # Get filename from various possible fields
            filename = (
                media_item.get('FileName', '') or 
                media_item.get('Path', '') or 
                media_item.get('Name', '')
            ).upper()
            
            if not filename:
                return None
            
            self.logger.debug(f"Parsing filename for resolution: {filename}")
            
            # Resolution patterns in filename
            resolution_patterns = {
                '8K': ['8K', '4320P', '7680X4320'],
                '4K': ['4K', '2160P', '3840X2160', 'UHD'],
                '1440P': ['1440P', '2560X1440', 'QHD'],
                '1080P': ['1080P', '1920X1080', 'FHD', 'FULLHD'],
                '720P': ['720P', '1280X720', 'HD'],
                '576P': ['576P', '720X576', 'PAL'],
                '480P': ['480P', '720X480', 'NTSC']
            }
            
            # HDR/DV patterns in filename
            hdr_patterns = ['HDR', 'HDR10', 'BT2020', 'REC2020']
            dv_patterns = ['DV', 'DOLBY.VISION', 'DOLBYVISION']
            hdr_plus_patterns = ['HDR10+', 'HDR10PLUS', 'HDR10.PLUS']  # Include literal + character
            
            # Find resolution in filename
            detected_resolution = None
            for resolution, patterns in resolution_patterns.items():
                for pattern in patterns:
                    if pattern in filename:
                        detected_resolution = resolution.lower()
                        self.logger.debug(f"Found resolution in filename: {pattern} -> {detected_resolution}")
                        break
                if detected_resolution:
                    break
            
            if not detected_resolution:
                return None
            
            # Detect HDR variants in filename
            is_dolby_vision = any(pattern in filename for pattern in dv_patterns)
            # Check HDR10+ first (more specific), then regular HDR
            is_hdr_plus = any(pattern in filename for pattern in hdr_plus_patterns)
            is_hdr = any(pattern in filename for pattern in hdr_patterns) and not is_dolby_vision and not is_hdr_plus
            
            # Map resolution to dimensions (estimated)
            dimension_map = {
                '8k': (7680, 4320),
                '4k': (3840, 2160),
                '1440p': (2560, 1440),
                '1080p': (1920, 1080),
                '720p': (1280, 720),
                '576p': (720, 576),
                '480p': (720, 480)
            }
            
            width, height = dimension_map.get(detected_resolution, (1920, 1080))
            
            filename_resolution = ResolutionInfo(
                height=height,
                width=width,
                base_resolution=detected_resolution,
                is_hdr=is_hdr,
                is_dolby_vision=is_dolby_vision,
                is_hdr_plus=is_hdr_plus
            )
            
            self.logger.debug(f"Filename resolution parsed: {filename_resolution}")
            return filename_resolution
            
        except Exception as e:
            self.logger.warning(f"Error parsing filename for resolution: {e}")
            return None
    
    def _resolutions_compatible(self, filename_res: str, stream_res: str) -> bool:
        """Check if filename and stream resolutions are compatible"""
        # Define compatibility groups
        compatibility_groups = {
            '4k': ['4k', '2160p'],
            '2160p': ['4k', '2160p'],
            '1440p': ['1440p'],
            '1080p': ['1080p', 'fhd'],
            'fhd': ['1080p', 'fhd'],
            '720p': ['720p', 'hd'],
            'hd': ['720p', 'hd'],
            '576p': ['576p'],
            '480p': ['480p']
        }
        
        filename_lower = filename_res.lower()
        stream_lower = stream_res.lower()
        
        # Check if they're in the same compatibility group
        for base_res, compatible_list in compatibility_groups.items():
            if filename_lower in compatible_list and stream_lower in compatible_list:
                return True
        
        return False
    
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
    
    def _map_dimensions_to_resolution(self, height: int, width: int = 0) -> str:
        """Map pixel dimensions to resolution string with width-primary intelligent detection"""
        # Use WIDTH as primary indicator (user's suggestion) with height as confidence meter
        # This prevents issues with letterboxed content and provides more stable readings
        
        # For portrait content, swap dimensions to use landscape logic
        if height > width and width > 0:
            width, height = height, width
        
        # Ensure we have valid dimensions
        if width <= 0:
            width = height * 16 // 9  # Assume 16:9 aspect ratio as fallback
        
        self.logger.debug(f"Resolution mapping: {width}x{height} (width-primary)")
        
        # WIDTH-BASED DETECTION (Primary method per user suggestion)
        
        # 8K UHD - Width is primary indicator
        if width >= 7680:  # 8K UHD width
            return "8k"
        elif width >= 7000 and height >= 3000:  # Wide 8K letterboxed
            return "8k"
        
        # 4K UHD - Width is primary indicator (more reliable than height)
        elif width >= 3840:  # Standard 4K width
            # Check if this might be 3D SBS content (4K width but 1080p height)
            if height <= 1200:  # Likely 3D Side-by-Side 1080p content
                return "1080p"
            return "4k"
        elif width >= 3600 and height >= 1500:  # Wide 4K letterboxed
            return "4k"
        elif width >= 3200 and height >= 1800:  # Conservative 4K threshold
            return "4k"
        
        # 1440p QHD - Width-based with confidence meter
        elif width >= 2560:  # Standard 1440p width
            if height >= 1200:  # Confidence check
                return "1440p"
            else:
                return "1080p"  # Likely ultrawide 1080p misidentified
        elif width >= 2400 and height >= 1200:  # Conservative 1440p
            return "1440p"
        
        # 1080p Full HD - Width is reliable indicator
        elif width >= 1920:  # Standard 1080p width
            return "1080p"
        elif width >= 1800 and height >= 800:  # Wide 1080p letterboxed
            return "1080p"
        elif width >= 1600 and height >= 900:  # Conservative 1080p threshold
            return "1080p"
        
        # 720p HD - Width-based detection (handles user's 1280x536 case)
        elif width >= 1280:  # Standard 720p width
            return "720p"  # This covers 1280x720 AND 1280x536 letterboxed
        elif width >= 1200 and height >= 400:  # Wide 720p letterboxed
            return "720p"
        elif width >= 1024 and height >= 576:  # Conservative 720p
            return "720p"
        
        # SD content - Width-based with fallbacks
        elif width >= 720:
            if height >= 576:
                return "576p"  # PAL DVD
            elif height >= 480:
                return "480p"  # NTSC DVD
            else:
                return "480p"  # Default SD
        elif width >= 640:
            return "480p"  # Standard SD width
        
        # Very low resolution - use height as last resort
        else:
            if height >= 576:
                return "576p"
            elif height >= 480:
                return "480p"
            else:
                return f"{height}p"  # Custom resolution for very low resolutions
    
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
            video_stream.get('Title', ''),
            video_stream.get('Comment', ''),      # NEW
            video_stream.get('PixelFormat', ''),  # NEW
            video_stream.get('Codec', ''),        # NEW
            video_stream.get('Description', '')   # NEW
        ]
        
        # Combine all fields for pattern matching
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Log what we're checking for debugging
        self.logger.debug(f"Checking for HDR in: '{combined_text}'")
        
        # Check against HDR patterns (but exclude HDR10+ which should be detected separately)
        for pattern in self.patterns.hdr_patterns:
            if re.search(pattern.upper(), combined_text):
                # Make sure this isn't HDR10+ or Dolby Vision
                if not self._detect_hdr_plus(video_stream) and not self._detect_dolby_vision(video_stream):
                    self.logger.info(f"✅ HDR detected via pattern: '{pattern}' in '{combined_text}'")
                    return True
        
        # Check bit depth (10+ bit often indicates HDR)
        bit_depth = self._extract_bit_depth(video_stream)
        if bit_depth and bit_depth >= 10:
            # Additional checks to avoid false positives
            if any(keyword in combined_text for keyword in ['BT2020', 'PQ', 'HLG', 'REC2020']):
                if not self._detect_hdr_plus(video_stream) and not self._detect_dolby_vision(video_stream):
                    self.logger.info(f"✅ HDR detected via {bit_depth}-bit + color space")
                    return True
        
        self.logger.debug(f"❌ No HDR patterns found in: '{combined_text}'")
        return False
    
    def _detect_dolby_vision(self, video_stream: Dict[str, Any]) -> bool:
        """Enhanced Dolby Vision detection with comprehensive field checking"""
        check_fields = [
            video_stream.get('VideoRange', ''),
            video_stream.get('Profile', ''),
            video_stream.get('DisplayTitle', ''),
            video_stream.get('Title', ''),
            video_stream.get('Codec', ''),
            video_stream.get('Comment', ''),      # NEW
            video_stream.get('Description', ''),  # NEW
            video_stream.get('PixelFormat', '')   # NEW
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Log what we're checking for debugging
        self.logger.debug(f"Checking for Dolby Vision in: '{combined_text}'")
        
        # Check against Dolby Vision patterns
        for pattern in self.patterns.dv_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.info(f"✅ Dolby Vision detected via pattern: '{pattern}' in '{combined_text}'")
                return True
        
        self.logger.debug(f"❌ No Dolby Vision patterns found in: '{combined_text}'")
        return False
    
    def _detect_hdr_plus(self, video_stream: Dict[str, Any]) -> bool:
        """Detect HDR10+ content with enhanced field checking"""
        check_fields = [
            video_stream.get('VideoRange', ''),
            video_stream.get('Profile', ''),
            video_stream.get('DisplayTitle', ''),
            video_stream.get('Title', ''),
            video_stream.get('Comment', ''),      # NEW
            video_stream.get('Description', ''),  # NEW
            video_stream.get('Codec', '')         # NEW
        ]
        
        combined_text = ' '.join(str(field) for field in check_fields if field).upper()
        
        # Log what we're checking for debugging
        self.logger.debug(f"Checking for HDR10+ in: '{combined_text}'")
        
        # Check against HDR10+ patterns
        for pattern in self.patterns.hdr_plus_patterns:
            if re.search(pattern.upper(), combined_text):
                self.logger.info(f"✅ HDR10+ detected via pattern: '{pattern}' in '{combined_text}'")
                return True
        
        self.logger.debug(f"❌ No HDR10+ patterns found in: '{combined_text}'")
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
