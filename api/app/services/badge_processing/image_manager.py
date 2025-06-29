"""
Dynamic image discovery and intelligent fallback system.
Manages resolution image selection with priority-based matching.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List, Set
from aphrodite_logging import get_logger

from .resolution_types import ResolutionInfo, FallbackRules


class ResolutionImageManager:
    """
    Manages resolution image discovery and intelligent fallback selection.
    Dynamically scans available images and provides priority-based matching.
    """
    
    def __init__(self, image_directory: str = None):
        self.logger = get_logger("aphrodite.resolution.images", service="badge")
        
        # Auto-detect the correct image directory path
        if image_directory is None:
            possible_paths = [
                Path("images/resolution"),
                Path("/app/images/resolution"),
                Path("../images/resolution"),
                Path("/app/api/../images/resolution")
            ]
            
            # Find the first existing path
            for path in possible_paths:
                if path.exists():
                    self.image_directory = path
                    break
            else:
                # Default to first path if none exist (for error logging)
                self.image_directory = possible_paths[0]
        else:
            self.image_directory = Path(image_directory)
            
        self.fallback_rules = FallbackRules.get_default()
        
        # Image cache
        self._available_images: Optional[Set[str]] = None
        self._image_priority_order = [
            "dvhdrplus", "dvhdr", "dvplus", "hdrplus", 
            "dv", "hdr", "plus", "base"
        ]
    
    def discover_available_images(self) -> Set[str]:
        """
        Dynamically discover all available resolution images.
        Returns set of available image names (without .png extension).
        """
        if self._available_images is not None:
            return self._available_images
        
        available_images = set()
        
        if not self.image_directory.exists():
            self.logger.warning(f"Image directory not found: {self.image_directory}")
            return available_images
        
        # Scan for PNG files
        for image_file in self.image_directory.glob("*.png"):
            # Skip aphrodite variant files
            if "-aphrodite" not in image_file.stem:
                available_images.add(image_file.stem)
        
        self.logger.info(f"Discovered {len(available_images)} resolution images")
        self.logger.debug(f"Available images: {sorted(available_images)}")
        
        self._available_images = available_images
        return available_images
    
    def find_best_image_match(
        self, 
        resolution_info: ResolutionInfo,
        user_mappings: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Find the best matching image with intelligent fallback hierarchy.
        
        Priority order:
        1. User-defined mappings (highest priority)
        2. Enhanced detection with available images
        3. Fallback rules for missing base resolutions
        4. Generic fallback (lowest priority)
        
        Args:
            resolution_info: Detected resolution information
            user_mappings: User-defined resolution mappings
            
        Returns:
            Image filename to use
        """
        try:
            # Refresh available images
            available_images = self.discover_available_images()
            
            # 1. Check user-defined mappings first
            if user_mappings:
                user_image = self._check_user_mappings(resolution_info, user_mappings)
                if user_image:
                    self.logger.debug(f"Using user mapping: {resolution_info} -> {user_image}")
                    return user_image
            
            # 2. Enhanced automatic detection
            enhanced_image = self._find_enhanced_match(resolution_info, available_images)
            if enhanced_image:
                self.logger.debug(f"Enhanced match: {resolution_info} -> {enhanced_image}")
                return enhanced_image
            
            # 3. Apply fallback rules
            fallback_image = self._apply_fallback_rules(resolution_info, available_images)
            if fallback_image:
                self.logger.debug(f"Fallback match: {resolution_info} -> {fallback_image}")
                return fallback_image
            
            # 4. Generic fallback
            generic_image = self._get_generic_fallback()
            self.logger.warning(f"Using generic fallback: {resolution_info} -> {generic_image}")
            return generic_image
            
        except Exception as e:
            self.logger.error(f"Image matching error: {e}", exc_info=True)
            return self._get_generic_fallback()
    
    def _check_user_mappings(
        self, 
        resolution_info: ResolutionInfo, 
        user_mappings: Dict[str, str]
    ) -> Optional[str]:
        """Check user-defined mappings for exact matches"""
        resolution_str = str(resolution_info)
        
        # Check exact match first
        if resolution_str in user_mappings:
            return user_mappings[resolution_str]
        
        # Check base resolution
        if resolution_info.base_resolution in user_mappings:
            return user_mappings[resolution_info.base_resolution]
        
        return None
    
    def _find_enhanced_match(
        self, 
        resolution_info: ResolutionInfo, 
        available_images: Set[str]
    ) -> Optional[str]:
        """Find best match using enhanced detection logic"""
        base_res = resolution_info.base_resolution
        
        # Generate candidate image names in priority order
        candidates = self._generate_image_candidates(resolution_info)
        
        # Find first available candidate
        for candidate in candidates:
            if candidate in available_images:
                return f"{candidate}.png"
        
        return None
    
    def _generate_image_candidates(self, resolution_info: ResolutionInfo) -> List[str]:
        """Generate candidate image names in priority order"""
        base_res = resolution_info.base_resolution
        candidates = []
        
        # Complex combinations (highest priority)
        if resolution_info.is_dolby_vision and resolution_info.is_hdr and resolution_info.is_hdr_plus:
            candidates.append(f"{base_res}dvhdrplus")
        
        # Two-way combinations
        if resolution_info.is_dolby_vision and resolution_info.is_hdr:
            candidates.append(f"{base_res}dvhdr")
        elif resolution_info.is_dolby_vision and resolution_info.is_hdr_plus:
            candidates.append(f"{base_res}dvplus")
        elif resolution_info.is_hdr and resolution_info.is_hdr_plus:
            candidates.append(f"{base_res}hdrplus")
        
        # Single enhancements
        if resolution_info.is_dolby_vision:
            candidates.append(f"{base_res}dv")
        elif resolution_info.is_hdr:
            candidates.append(f"{base_res}hdr")
        elif resolution_info.is_hdr_plus:
            candidates.append(f"{base_res}plus")
        
        # Base resolution (always included)
        candidates.append(base_res)
        
        return candidates
    
    def _apply_fallback_rules(
        self, 
        resolution_info: ResolutionInfo, 
        available_images: Set[str]
    ) -> Optional[str]:
        """Apply fallback rules for missing base resolutions"""
        base_res = resolution_info.base_resolution
        
        # Check if we need fallback
        if base_res in available_images:
            return f"{base_res}.png"
        
        # Apply fallback rules
        fallback_res = self.fallback_rules.rules.get(base_res)
        if fallback_res and fallback_res in available_images:
            self.logger.info(f"Applied fallback rule: {base_res} -> {fallback_res}")
            
            # Generate candidates with fallback resolution
            fallback_info = ResolutionInfo(
                height=resolution_info.height,
                width=resolution_info.width,
                base_resolution=fallback_res,
                is_hdr=resolution_info.is_hdr,
                is_dolby_vision=resolution_info.is_dolby_vision,
                is_hdr_plus=resolution_info.is_hdr_plus
            )
            
            fallback_candidates = self._generate_image_candidates(fallback_info)
            for candidate in fallback_candidates:
                if candidate in available_images:
                    return f"{candidate}.png"
        
        return None
    
    def _get_generic_fallback(self) -> str:
        """Get generic fallback image"""
        # Check for common fallbacks in order of preference
        fallback_names = [
            "resolution-generic.png",
            "unknown.png", 
            "1080p.png",
            "720p.png"
        ]
        
        available_images = self.discover_available_images()
        
        for fallback in fallback_names:
            fallback_stem = fallback.replace('.png', '')
            if fallback_stem in available_images:
                return fallback
        
        # Ultimate fallback
        return "resolution-generic.png"
    
    def analyze_image_coverage(self) -> Dict[str, any]:
        """
        Analyze available image coverage for diagnostics.
        Returns comprehensive coverage report.
        """
        available_images = self.discover_available_images()
        
        # Base resolutions to check
        base_resolutions = ["480p", "576p", "720p", "1080p", "1440p", "4k", "8k"]
        
        # Enhancement types to check
        enhancements = ["", "hdr", "dv", "plus", "dvhdr", "dvplus", "hdrplus", "dvhdrplus"]
        
        coverage_report = {
            "total_images": len(available_images),
            "coverage_by_resolution": {},
            "missing_combinations": [],
            "standalone_images": [],
            "fallback_coverage": {}
        }
        
        # Check coverage for each base resolution
        for base_res in base_resolutions:
            coverage_report["coverage_by_resolution"][base_res] = {
                "available_variants": [],
                "missing_variants": [],
                "has_base": base_res in available_images
            }
            
            for enhancement in enhancements:
                variant_name = f"{base_res}{enhancement}" if enhancement else base_res
                
                if variant_name in available_images:
                    coverage_report["coverage_by_resolution"][base_res]["available_variants"].append(enhancement or "base")
                else:
                    coverage_report["coverage_by_resolution"][base_res]["missing_variants"].append(enhancement or "base")
                    coverage_report["missing_combinations"].append(variant_name)
        
        # Check standalone enhancement images
        standalone_names = ["dv", "hdr", "plus", "dvhdr", "dvplus", "hdrplus", "dvhdrplus"]
        for standalone in standalone_names:
            if standalone in available_images:
                coverage_report["standalone_images"].append(standalone)
        
        # Check fallback rule coverage
        for source, target in self.fallback_rules.rules.items():
            coverage_report["fallback_coverage"][source] = {
                "target": target,
                "target_available": target in available_images
            }
        
        return coverage_report
    
    def clear_image_cache(self):
        """Clear the image cache to force re-discovery"""
        self._available_images = None
        self.logger.info("Image cache cleared")
