"""
Audio data structures for enhanced detection system.
Defines the core AudioInfo class and related types.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class AudioFormat(Enum):
    """Standard audio formats"""
    DOLBY_DIGITAL = "dolby_digital"      # AC3
    DOLBY_DIGITAL_PLUS = "dolby_digital_plus"  # EAC3
    DOLBY_TRUEHD = "dolby_truehd"
    DOLBY_ATMOS = "dolby_atmos"          # TrueHD + Atmos
    DTS = "dts"
    DTS_HD = "dts_hd"
    DTS_HD_MA = "dts_hd_ma"
    DTS_X = "dts_x"
    AAC = "aac"
    MP3 = "mp3"
    FLAC = "flac"
    PCM = "pcm"
    UNKNOWN = "unknown"


class ChannelLayout(Enum):
    """Channel configurations"""
    MONO = "1.0"
    STEREO = "2.0"
    SURROUND_5_1 = "5.1"
    SURROUND_7_1 = "7.1"
    ATMOS = "atmos"  # Object-based
    DTS_X = "dts_x"  # Object-based
    UNKNOWN = "unknown"


@dataclass
class AudioInfo:
    """
    Comprehensive audio information extracted from media metadata.
    Contains all data needed for intelligent image selection.
    """
    codec: str                           # Raw codec from Jellyfin
    format: AudioFormat                  # Detected format
    channels: int                        # Number of channels
    channel_layout: ChannelLayout        # Layout type
    is_lossless: bool                   # True for TrueHD, DTS-HD MA, FLAC
    is_object_based: bool               # True for Atmos, DTS-X
    bitrate: Optional[int] = None       # kbps
    sample_rate: Optional[int] = None   # Hz
    bit_depth: Optional[int] = None     # bits
    profile: Optional[str] = None       # Additional profile info
    
    def __str__(self) -> str:
        """Human readable representation"""
        if self.is_object_based:
            if self.format == AudioFormat.DOLBY_ATMOS:
                return "Dolby Atmos"
            elif self.format == AudioFormat.DTS_X:
                return "DTS-X"
        
        if self.format == AudioFormat.DOLBY_TRUEHD:
            return "TrueHD"
        elif self.format == AudioFormat.DTS_HD_MA:
            return "DTS-HD MA"
        elif self.format == AudioFormat.DOLBY_DIGITAL_PLUS:
            return "Dolby Digital Plus"
        elif self.format == AudioFormat.DOLBY_DIGITAL:
            return "Dolby Digital"
        elif self.format == AudioFormat.DTS_HD:
            return "DTS-HD"
        elif self.format == AudioFormat.DTS:
            return "DTS"
        elif self.format == AudioFormat.AAC:
            return "AAC"
        elif self.format == AudioFormat.MP3:
            return "MP3"
        elif self.format == AudioFormat.FLAC:
            return "FLAC"
        elif self.format == AudioFormat.PCM:
            return "PCM"
        
        return self.format.value.replace("_", " ").title()
    
    def get_technical_summary(self) -> str:
        """Detailed technical summary for diagnostics"""
        parts = [
            self.codec,
            str(self.format.value),
            f"{self.channels}ch",
            str(self.channel_layout.value)
        ]
        
        if self.bitrate:
            parts.append(f"{self.bitrate}kbps")
        if self.sample_rate:
            parts.append(f"{self.sample_rate}Hz")
        if self.bit_depth:
            parts.append(f"{self.bit_depth}bit")
            
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching and API responses"""
        return {
            "codec": self.codec,
            "format": self.format.value,
            "channels": self.channels,
            "channel_layout": self.channel_layout.value,
            "is_lossless": self.is_lossless,
            "is_object_based": self.is_object_based,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "profile": self.profile
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioInfo':
        """Create AudioInfo from dictionary (for cache loading)"""
        return cls(
            codec=data["codec"],
            format=AudioFormat(data.get("format", "unknown")),
            channels=data["channels"],
            channel_layout=ChannelLayout(data.get("channel_layout", "unknown")),
            is_lossless=data.get("is_lossless", False),
            is_object_based=data.get("is_object_based", False),
            bitrate=data.get("bitrate"),
            sample_rate=data.get("sample_rate"),
            bit_depth=data.get("bit_depth"),
            profile=data.get("profile")
        )


@dataclass
class DetectionPatterns:
    """Configurable patterns for advanced audio detection"""
    atmos_patterns: List[str]
    dts_x_patterns: List[str]
    lossless_patterns: List[str]
    
    @classmethod
    def get_default(cls) -> 'DetectionPatterns':
        """Default detection patterns based on industry standards"""
        return cls(
            atmos_patterns=[
                "ATMOS", "DOLBY ATMOS", "TRUEHD ATMOS", 
                "TrueHD Atmos", "Atmos", "atmos"
            ],
            dts_x_patterns=[
                "DTS-X", "DTS:X", "DTSX", "DTS X", "dts-x"
            ],
            lossless_patterns=[
                "TrueHD", "TRUEHD", "DTS-HD MA", "DTSHDMA", "FLAC", "PCM"
            ]
        )


@dataclass 
class FallbackRules:
    """Rules for audio fallbacks when images don't exist"""
    rules: Dict[str, str]
    
    @classmethod
    def get_default(cls) -> 'FallbackRules':
        """Default fallback rules for common scenarios"""
        return cls(rules={
            "dolby_atmos": "truehd",           # Atmos → TrueHD fallback
            "dts_x": "dts_hd_ma",             # DTS-X → DTS-HD MA fallback
            "dolby_digital_plus": "dolby_digital",  # DD+ → DD fallback
            "dts_hd_ma": "dts_hd",            # DTS-HD MA → DTS-HD fallback
            "dts_hd": "dts"                   # DTS-HD → DTS fallback
        })
