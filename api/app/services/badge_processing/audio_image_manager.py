"""
Dynamic audio image discovery and intelligent matching.
Based on successful ResolutionImageManager pattern.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from aphrodite_logging import get_logger

from .audio_types import AudioInfo, FallbackRules


class AudioImageManager:
    """
    Dynamic audio image discovery and intelligent matching.
    Based on successful ResolutionImageManager pattern.
    """
    
    def __init__(self, image_directory: str = "images/codec"):
        self.logger = get_logger("aphrodite.audio.images", service="badge")
        self.image_directory = image_directory
        self.available_images = self.discover_available_images()
        self.fallback_rules = FallbackRules.get_default()
        
        self.logger.info(f"Discovered {len(self.available_images)} audio images")
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Available images: {list(self.available_images.keys())}")
    
    def discover_available_images(self) -> Dict[str, str]:
        """Dynamically discover all available audio images"""
        images = {}
        
        # Try multiple possible base paths
        base_paths = [
            Path("/app") / self.image_directory,
            Path("./") / self.image_directory,
            Path("../") / self.image_directory,
            Path("../../") / self.image_directory
        ]
        
        image_path = None
        for base_path in base_paths:
            if base_path.exists():
                image_path = base_path
                break
        
        if not image_path:
            self.logger.warning(f"Audio image directory not found: {self.image_directory}")
            return images
        
        # Discover all image files
        for image_file in image_path.glob("*.png"):
            # Remove extension and normalize name
            image_key = image_file.stem.lower().replace("-", "_")
            images[image_key] = str(image_file)
            
        return images
    
    def find_best_image_match(self, 
                            audio_info: AudioInfo, 
                            user_mappings: Optional[Dict[str, str]] = None) -> str:
        """
        Find the best matching image with fallback hierarchy.
        Priority: User mappings → Enhanced detection → Legacy fallback
        """
        try:
            # 1. Check user-defined mappings first (highest priority)
            if user_mappings:
                user_image = self._check_user_mappings(audio_info, user_mappings)
                if user_image:
                    self.logger.debug(f"User mapping: {audio_info} -> {user_image}")
                    return user_image
            
            # 2. Enhanced automatic detection
            enhanced_image = self._enhanced_audio_mapping(audio_info)
            if enhanced_image:
                self.logger.debug(f"Enhanced match: {audio_info} -> {enhanced_image}")
                return enhanced_image
            
            # 3. Legacy fallback
            fallback_image = self._legacy_audio_mapping(str(audio_info))
            self.logger.debug(f"Legacy fallback: {audio_info} -> {fallback_image}")
            return fallback_image
            
        except Exception as e:
            self.logger.error(f"Audio image matching error: {e}")
            return "aac.png"  # Final fallback
    
    def _check_user_mappings(self, audio_info: AudioInfo, user_mappings: Dict[str, str]) -> Optional[str]:
        """Check user-defined mappings"""
        # Try exact string match first
        audio_str = str(audio_info)
        if audio_str in user_mappings:
            image_file = user_mappings[audio_str]
            if self._image_exists(image_file):
                return image_file
        
        # Try codec match
        if audio_info.codec in user_mappings:
            image_file = user_mappings[audio_info.codec]
            if self._image_exists(image_file):
                return image_file
        
        return None
    
    def _enhanced_audio_mapping(self, audio_info: AudioInfo) -> Optional[str]:
        """Enhanced audio mapping with intelligent fallbacks"""
        # Build priority list of image candidates
        candidates = self._build_audio_candidates(audio_info)
        
        # Find first available image
        for candidate in candidates:
            if candidate in self.available_images:
                return self.available_images[candidate]
        
        return None
    
    def _build_audio_candidates(self, audio_info: AudioInfo) -> List[str]:
        """Build prioritized list of image candidates"""
        candidates = []
        
        # Primary candidates based on detected format
        if audio_info.format.value == "dolby_atmos":
            candidates.extend([
                "truehd_atmos", "atmos", "truehd", "dolby_digital_plus", "dolby_digital"
            ])
        elif audio_info.format.value == "dts_x":
            candidates.extend([
                "dts_x", "dts_hd_ma", "dts_hd", "dts"
            ])
        elif audio_info.format.value == "dolby_truehd":
            candidates.extend([
                "truehd", "dolby_digital_plus", "dolby_digital"
            ])
        elif audio_info.format.value == "dts_hd_ma":
            candidates.extend([
                "dts_hd_ma", "dts_hd", "dts"
            ])
        elif audio_info.format.value == "dts_hd":
            candidates.extend([
                "dts_hd", "dts"
            ])
        elif audio_info.format.value == "dolby_digital_plus":
            candidates.extend([
                "dolby_digital_plus", "digitalplus", "dolby_digital"
            ])
        elif audio_info.format.value == "dolby_digital":
            candidates.extend([
                "dolby_digital", "ac3"
            ])
        elif audio_info.format.value == "dts":
            candidates.append("dts")
        elif audio_info.format.value == "aac":
            candidates.append("aac")
        elif audio_info.format.value == "mp3":
            candidates.append("mp3")
        elif audio_info.format.value == "flac":
            candidates.append("flac")
        elif audio_info.format.value == "pcm":
            candidates.append("pcm")
        
        # Apply fallback rules
        enhanced_candidates = []
        for candidate in candidates:
            enhanced_candidates.append(candidate)
            if candidate in self.fallback_rules.rules:
                enhanced_candidates.append(self.fallback_rules.rules[candidate])
        
        return enhanced_candidates
    
    def _legacy_audio_mapping(self, audio_str: str) -> str:
        """Legacy audio mapping for backward compatibility"""
        audio_upper = audio_str.upper()
        
        # Legacy mapping logic (simplified)
        if "ATMOS" in audio_upper:
            return "Atmos.png"
        elif "DTS-X" in audio_upper:
            return "DTS-X.png"
        elif "TRUEHD" in audio_upper:
            return "TrueHD.png"
        elif "DTS-HD" in audio_upper:
            return "DTS-HD.png"
        elif "DOLBY DIGITAL PLUS" in audio_upper or "DIGITALPLUS" in audio_upper:
            return "DigitalPlus.png"
        elif "DOLBY DIGITAL" in audio_upper:
            return "dolby-digital.png"
        elif "DTS" in audio_upper:
            return "DTS-HD.png"  # Default to DTS-HD for DTS
        elif "AAC" in audio_upper:
            return "aac.png"
        else:
            return "aac.png"  # Final fallback
    
    def _image_exists(self, image_file: str) -> bool:
        """Check if image file exists"""
        if not image_file:
            return False
            
        # Check in available images (by filename)
        image_name = Path(image_file).stem.lower().replace("-", "_")
        if image_name in self.available_images:
            return True
        
        # Check direct file existence
        image_path = Path("/app") / self.image_directory / image_file
        return image_path.exists()
    
    def get_coverage_analysis(self) -> Dict[str, any]:
        """Analyze audio image coverage for diagnostics"""
        return {
            "total_images": len(self.available_images),
            "available_images": list(self.available_images.keys()),
            "image_directory": self.image_directory,
            "fallback_rules": self.fallback_rules.rules
        }
