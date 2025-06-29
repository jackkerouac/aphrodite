"""
Resolution data structures for enhanced detection system.
Defines the core ResolutionInfo class and related types.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ColorSpace(Enum):
    """Standard color spaces for video content"""
    BT709 = "bt709"      # Standard HD
    BT2020 = "bt2020"    # HDR standard
    UNKNOWN = "unknown"


class VideoRange(Enum):
    """Video dynamic range types"""
    SDR = "sdr"          # Standard Dynamic Range
    HDR = "hdr"          # High Dynamic Range
    HDR10 = "hdr10"      # HDR10
    HDR10_PLUS = "hdr10plus"  # HDR10+
    DOLBY_VISION = "dolby_vision"  # Dolby Vision
    HLG = "hlg"          # Hybrid Log-Gamma
    UNKNOWN = "unknown"


@dataclass
class ResolutionInfo:
    """
    Comprehensive resolution information extracted from media metadata.
    Contains all data needed for intelligent image selection.
    """
    height: int
    width: int
    base_resolution: str          # "4k", "1080p", etc.
    
    # HDR and advanced video properties
    is_hdr: bool = False
    is_dolby_vision: bool = False
    is_hdr_plus: bool = False
    
    # Technical metadata
    codec: Optional[str] = None          # "hevc", "h264", "av1"
    color_space: ColorSpace = ColorSpace.UNKNOWN
    video_range: VideoRange = VideoRange.UNKNOWN
    bit_depth: Optional[int] = None      # 8, 10, 12 bit
    
    # Quality indicators
    bitrate: Optional[int] = None        # kbps
    profile: Optional[str] = None        # codec profile
    
    def __str__(self) -> str:
        """Human readable representation for logging"""
        result = self.base_resolution
        
        if self.is_dolby_vision:
            result += " DV"
        if self.is_hdr:
            result += " HDR"
        if self.is_hdr_plus:
            result += " Plus"
            
        return result
    
    def get_technical_summary(self) -> str:
        """Detailed technical summary for diagnostics"""
        parts = [
            f"{self.width}x{self.height}",
            self.base_resolution,
            f"codec:{self.codec or 'unknown'}",
            f"range:{self.video_range.value}",
            f"space:{self.color_space.value}"
        ]
        
        if self.bit_depth:
            parts.append(f"{self.bit_depth}bit")
        if self.bitrate:
            parts.append(f"{self.bitrate}kbps")
            
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching and API responses"""
        return {
            "height": self.height,
            "width": self.width,
            "base_resolution": self.base_resolution,
            "is_hdr": self.is_hdr,
            "is_dolby_vision": self.is_dolby_vision,
            "is_hdr_plus": self.is_hdr_plus,
            "codec": self.codec,
            "color_space": self.color_space.value,
            "video_range": self.video_range.value,
            "bit_depth": self.bit_depth,
            "bitrate": self.bitrate,
            "profile": self.profile
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResolutionInfo':
        """Create ResolutionInfo from dictionary (for cache loading)"""
        return cls(
            height=data["height"],
            width=data["width"],
            base_resolution=data["base_resolution"],
            is_hdr=data.get("is_hdr", False),
            is_dolby_vision=data.get("is_dolby_vision", False),
            is_hdr_plus=data.get("is_hdr_plus", False),
            codec=data.get("codec"),
            color_space=ColorSpace(data.get("color_space", "unknown")),
            video_range=VideoRange(data.get("video_range", "unknown")),
            bit_depth=data.get("bit_depth"),
            bitrate=data.get("bitrate"),
            profile=data.get("profile")
        )


@dataclass
class DetectionPatterns:
    """Configurable patterns for HDR and Dolby Vision detection"""
    hdr_patterns: list[str]
    dv_patterns: list[str]
    hdr_plus_patterns: list[str]
    
    @classmethod
    def get_default(cls) -> 'DetectionPatterns':
        """Default detection patterns based on industry standards"""
        return cls(
            hdr_patterns=[
                "HDR", "HDR10", "BT2020", "BT.2020",
                "PQ", "ST2084", "ST.2084", "HLG", "ARIB"
            ],
            dv_patterns=[
                "DV", "DOLBY VISION", "DVHE", "DVH1", 
                "DOLBY.VISION", "DV.PROFILE"
            ],
            hdr_plus_patterns=[
                "HDR10+", "HDR10PLUS", "PLUS", "ST2094"
            ]
        )


@dataclass 
class FallbackRules:
    """Rules for resolution fallbacks when images don't exist"""
    rules: Dict[str, str]
    
    @classmethod
    def get_default(cls) -> 'FallbackRules':
        """Default fallback rules for common scenarios"""
        return cls(rules={
            "1440p": "1080p",    # 1440p content uses 1080p images
            "8k": "4k",          # 8K content uses 4K images  
            "2160p": "4k",       # Alternative 4K naming
            "1080i": "1080p",    # Interlaced uses progressive images
            "720i": "720p"       # Interlaced uses progressive images
        })
