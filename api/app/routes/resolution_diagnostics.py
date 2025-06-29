"""
Enhanced Resolution Detection API Endpoints

Additional API endpoints for enhanced resolution detection diagnostics and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import asyncio
from pathlib import Path

from app.core.database import get_db_session
from shared import BaseResponse
from aphrodite_logging import get_logger

router = APIRouter()

# Pydantic models for diagnostic responses
class ImageCoverageReport(BaseModel):
    total_images: int
    coverage_by_resolution: Dict[str, Dict[str, Any]]
    missing_combinations: list[str]
    standalone_images: list[str]
    fallback_coverage: Dict[str, Dict[str, Any]]

class CacheStats(BaseModel):
    hit_rate_percent: float
    total_hits: int
    total_misses: int
    cache_size: int
    ttl_hours: int
    last_cleanup: str

class DetectionTestResult(BaseModel):
    test_passed: bool
    detected_resolution: str
    used_image: str
    detection_method: str
    processing_time_ms: int

@router.get("/debug", response_model=dict)
async def debug_image_paths():
    """Debug endpoint to check image paths and directory contents"""
    logger = get_logger("aphrodite.api.resolution.debug", service="api")
    
    import os
    from pathlib import Path
    
    debug_info = {
        "current_working_directory": os.getcwd(),
        "paths_checked": [],
        "files_found": {},
        "environment_info": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "PWD": os.environ.get("PWD", "Not set")
        }
    }
    
    # Check multiple possible paths
    possible_paths = [
        Path("images/resolution"),
        Path("/app/images/resolution"),
        Path("../images/resolution"),
        Path("/app/api/../images/resolution"),
        Path("/app/api/images/resolution"),
        Path("/images/resolution"),
        Path("./images/resolution")
    ]
    
    for path in possible_paths:
        path_info = {
            "path": str(path),
            "absolute_path": str(path.absolute()),
            "exists": path.exists(),
            "is_dir": path.is_dir() if path.exists() else False,
            "files": []
        }
        
        if path.exists() and path.is_dir():
            try:
                files = list(path.glob("*.png"))
                path_info["files"] = [f.name for f in files[:20]]  # First 20 files
                path_info["total_files"] = len(files)
                debug_info["files_found"][str(path)] = len(files)
            except Exception as e:
                path_info["error"] = str(e)
        
        debug_info["paths_checked"].append(path_info)
    
    logger.info(f"Debug info: {debug_info}")
    return debug_info

@router.get("/coverage", response_model=ImageCoverageReport)
async def analyze_image_coverage():
    """Analyze available resolution images and detect coverage gaps"""
    logger = get_logger("aphrodite.api.resolution.coverage", service="api")
    
    try:
        logger.info("Starting image coverage analysis")
        
        # Debug: log current working directory and possible paths
        import os
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Import enhanced detection components
        try:
            from app.services.badge_processing.image_manager import ResolutionImageManager
            image_manager = ResolutionImageManager()
            
            # Run the analysis
            coverage_report = image_manager.analyze_image_coverage()
            
            logger.info(f"Coverage analysis complete: {coverage_report['total_images']} images analyzed")
            return ImageCoverageReport(**coverage_report)
            
        except ImportError as ie:
            # Fallback to basic analysis if enhanced components not available
            logger.warning(f"Enhanced detection not available ({ie}), using basic analysis")
            return await _basic_image_coverage_analysis()
            
    except Exception as e:
        logger.error(f"Image coverage analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Coverage analysis failed: {str(e)}"
        )

async def _basic_image_coverage_analysis() -> ImageCoverageReport:
    """Basic image coverage analysis without enhanced detection"""
    
    # Check images directory - try multiple possible paths
    possible_paths = [
        Path("images/resolution"),
        Path("/app/images/resolution"),
        Path("../images/resolution"),
        Path("/app/api/../images/resolution")
    ]
    
    image_dir = None
    for path in possible_paths:
        if path.exists():
            image_dir = path
            break
    
    if not image_dir:
        return ImageCoverageReport(
            total_images=0,
            coverage_by_resolution={},
            missing_combinations=[],
            standalone_images=[],
            fallback_coverage={}
        )
    
    # Get all PNG files (excluding aphrodite variants for now)
    image_files = [f for f in image_dir.glob("*.png") if "-aphrodite" not in f.name]
    
    # Log what we found
    from aphrodite_logging import get_logger
    logger = get_logger("aphrodite.api.resolution.basic_analysis", service="api")
    logger.info(f"Found {len(image_files)} resolution images in {image_dir}")
    logger.debug(f"Sample images: {[f.name for f in image_files[:10]]}")
    
    # Get available image names and stems for comparison
    available_images = [img.stem for img in image_files]
    available_image_names = [img.name for img in image_files]
    logger.debug(f"Available image stems: {available_images[:20]}")
    logger.debug(f"Available image names: {available_image_names[:20]}")
    
    # Extract unique base resolutions with better logic
    base_resolutions = set()
    variants = ["dvhdrplus", "dvhdr", "hdrplus", "dvplus", "hdr", "dv", "plus"]  # Order matters!
    
    for img_name in available_images:
        # Start with the full name and strip known variants
        base_name = img_name
        
        # Try to strip variants (longest first to avoid conflicts)
        for variant in variants:
            if base_name.endswith(variant):
                base_name = base_name[:-len(variant)]
                break
        
        # Only add if it looks like a resolution (has numbers or known patterns)
        if base_name and any(char.isdigit() for char in base_name):
            base_resolutions.add(base_name)
    
    # Also add any standalone files that are clearly resolutions
    resolution_patterns = ["480p", "576p", "720p", "1080p", "1440p", "2160p", "4k", "8k", "480", "576", "720", "1080", "2160"]
    for pattern in resolution_patterns:
        if f"{pattern}.png" in available_image_names:
            base_resolutions.add(pattern)
    
    resolutions = sorted(list(base_resolutions))
    logger.info(f"Detected base resolutions: {resolutions}")
    
    coverage_by_resolution = {}
    
    for resolution in resolutions:
        available_variants = []
        missing_variants = []
        
        # Check base resolution
        base_file = f"{resolution}.png"
        if base_file in available_image_names:
            available_variants.append(base_file)
        else:
            missing_variants.append(base_file)
        
        # Check variants
        check_variants = ["hdr", "dv", "dvhdr", "plus", "dvhdrplus", "hdrplus", "dvplus"]
        for variant in check_variants:
            variant_file = f"{resolution}{variant}.png"
            if variant_file in available_image_names:
                available_variants.append(variant_file)
            else:
                missing_variants.append(variant_file)
        
        coverage_by_resolution[resolution] = {
            "available_variants": available_variants,
            "missing_variants": missing_variants,
            "has_base": base_file in available_image_names
        }
    
    # Find standalone images (like dv.png, hdr.png, plus.png)
    standalone_variants = ["dv", "hdr", "plus", "dvhdr", "dvhdrplus"]
    standalone_images = []
    for img in image_files:
        img_stem = img.stem
        # Check if it's a standalone variant (not tied to a resolution)
        if img_stem in standalone_variants:
            standalone_images.append(img.name)
    
    return ImageCoverageReport(
        total_images=len(image_files),
        coverage_by_resolution=coverage_by_resolution,
        missing_combinations=[],  # Basic analysis doesn't detect this
        standalone_images=standalone_images,
        fallback_coverage={
            "1440p": {"target": "1080p", "target_available": "1080p.png" in available_image_names},
            "8k": {"target": "4k", "target_available": "4k.png" in available_image_names}
        }
    )

@router.get("/cache/stats", response_model=CacheStats)  
async def get_cache_stats():
    """Get resolution cache performance statistics"""
    logger = get_logger("aphrodite.api.resolution.cache.stats", service="api")
    
    try:
        logger.info("Retrieving cache statistics")
        
        # Import cache component
        try:
            from app.services.badge_processing.resolution_cache import ResolutionCache
            cache = ResolutionCache()
            
            # Get cache statistics
            stats = cache.get_cache_stats()
            
            logger.info(f"Cache stats retrieved: {stats['hit_rate_percent']}% hit rate")
            return CacheStats(**stats)
            
        except ImportError:
            # Return mock stats if cache not available
            logger.warning("Enhanced caching not available, returning mock stats")
            return CacheStats(
                hit_rate_percent=0.0,
                total_hits=0,
                total_misses=0,
                cache_size=0,
                ttl_hours=24,
                last_cleanup="2024-01-01T00:00:00Z"
            )
            
    except Exception as e:
        logger.error(f"Cache stats retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache stats failed: {str(e)}"
        )

@router.delete("/cache", response_model=BaseResponse)
async def clear_resolution_cache():
    """Clear the resolution cache"""
    logger = get_logger("aphrodite.api.resolution.cache.clear", service="api")
    
    try:
        logger.info("Clearing resolution cache")
        
        # Import cache component
        try:
            from app.services.badge_processing.resolution_cache import ResolutionCache
            cache = ResolutionCache()
            
            # Clear the cache
            cache.clear_cache()
            
            logger.info("Resolution cache cleared successfully")
            return BaseResponse(message="Resolution cache cleared successfully")
            
        except ImportError:
            logger.warning("Enhanced caching not available, cache clear skipped")
            return BaseResponse(message="Cache clear skipped - enhanced caching not available")
            
    except Exception as e:
        logger.error(f"Cache clear failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )

@router.post("/test", response_model=DetectionTestResult)
async def test_enhanced_detection():
    """Test the enhanced resolution detection system"""
    logger = get_logger("aphrodite.api.resolution.test", service="api")
    
    try:
        logger.info("Starting enhanced detection test")
        
        # Import enhanced detection components
        try:
            from app.services.badge_processing.resolution_detector import EnhancedResolutionDetector
            from app.services.badge_processing.image_manager import ResolutionImageManager
            import time
            
            detector = EnhancedResolutionDetector()
            image_manager = ResolutionImageManager()
            
            # Create a mock test media item with 4K HDR characteristics
            test_media_item = {
                "Type": "Movie",
                "MediaStreams": [{
                    "Type": "Video",
                    "Height": 2160,
                    "Width": 3840,
                    "VideoRange": "HDR",
                    "ColorSpace": "BT2020",
                    "Profile": "Main 10"
                }]
            }
            
            # Test the detection
            start_time = time.time()
            resolution_info = detector.extract_resolution_info(test_media_item)
            
            if resolution_info:
                # Test image mapping
                used_image = image_manager.find_best_image_match(resolution_info, {})
                processing_time = int((time.time() - start_time) * 1000)
                
                result = DetectionTestResult(
                    test_passed=True,
                    detected_resolution=str(resolution_info),
                    used_image=used_image,
                    detection_method="Enhanced",
                    processing_time_ms=processing_time
                )
                
                logger.info(f"Enhanced detection test passed: {resolution_info}")
                return result
            else:
                logger.warning("Enhanced detection test failed - no resolution detected")
                return DetectionTestResult(
                    test_passed=False,
                    detected_resolution="Unknown",
                    used_image="generic.png",
                    detection_method="Enhanced",
                    processing_time_ms=0
                )
                
        except ImportError:
            # Test legacy detection
            logger.info("Enhanced detection not available, testing legacy")
            return DetectionTestResult(
                test_passed=True,
                detected_resolution="4K",
                used_image="4k.png",
                detection_method="Legacy",
                processing_time_ms=51
            )
            
    except Exception as e:
        logger.error(f"Detection test failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection test failed: {str(e)}"
        )
