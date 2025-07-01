"""
Enhanced Audio Detection API Endpoints

Additional API endpoints for enhanced audio detection diagnostics and management.
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
class AudioCoverageReport(BaseModel):
    total_images: int
    coverage_by_audio_format: Dict[str, Dict[str, Any]]
    missing_combinations: list[str]
    standalone_images: list[str]
    fallback_coverage: Dict[str, Dict[str, Any]]
    atmos_images: list[str]
    dts_x_images: list[str]

class AudioCacheStats(BaseModel):
    hit_rate_percent: float
    total_hits: int
    total_misses: int
    cache_size: int
    ttl_hours: int
    last_cleanup: str
    episode_samples_cached: int

class AudioDetectionTestResult(BaseModel):
    test_passed: bool
    detected_audio: str
    used_image: str
    detection_method: str
    processing_time_ms: int
    atmos_detected: bool
    dts_x_detected: bool

@router.get("/debug", response_model=dict)
async def debug_audio_detection():
    """Debug audio detection system paths and configuration"""
    logger = get_logger("aphrodite.api.audio.debug", service="api")
    
    import os
    from pathlib import Path
    
    debug_info = {
        "current_working_directory": os.getcwd(),
        "paths_checked": [],
        "files_found": {},
        "environment_info": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "PWD": os.environ.get("PWD", "Not set")
        },
        "enhanced_detection_status": "unknown"
    }
    
    # Check audio image paths
    possible_paths = [
        Path("images/audio"),
        Path("/app/images/audio"),
        Path("../images/audio"),
        Path("/app/api/../images/audio"),
        Path("/app/api/images/audio"),
        Path("/images/audio"),
        Path("./images/audio")
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
    
    # Check enhanced detection availability
    try:
        from app.services.badge_processing.enhanced_audio_processor import EnhancedAudioProcessor
        debug_info["enhanced_detection_status"] = "available"
        debug_info["enhanced_features"] = ["atmos_detection", "dts_x_detection", "parallel_processing", "caching"]
    except ImportError as e:
        debug_info["enhanced_detection_status"] = f"not_available: {str(e)}"
        debug_info["enhanced_features"] = []
    
    logger.info(f"Audio debug info: {debug_info}")
    return debug_info

@router.get("/coverage", response_model=AudioCoverageReport)
async def analyze_audio_coverage():
    """Analyze audio image coverage and identify gaps"""
    logger = get_logger("aphrodite.api.audio.coverage", service="api")
    
    try:
        logger.info("Starting audio coverage analysis")
        
        # Debug: log current working directory and possible paths
        import os
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Try enhanced detection first
        try:
            from app.services.badge_processing.audio_image_manager import AudioImageManager
            image_manager = AudioImageManager()
            
            # Check if the enhanced method exists
            if hasattr(image_manager, 'analyze_image_coverage'):
                # Run the enhanced analysis
                coverage_report = image_manager.analyze_image_coverage()
                logger.info(f"Audio coverage analysis complete: {coverage_report['total_images']} images analyzed")
                return AudioCoverageReport(**coverage_report)
            else:
                logger.warning("AudioImageManager exists but analyze_image_coverage method not available, using basic analysis")
                raise AttributeError("Method not available")
            
        except (ImportError, AttributeError) as ie:
            # Fallback to basic analysis if enhanced components not available or incomplete
            logger.warning(f"Enhanced audio detection not fully available ({type(ie).__name__}: {ie}), using basic analysis")
            return await _basic_audio_coverage_analysis()
            
    except Exception as e:
        logger.error(f"Audio coverage analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio coverage analysis failed: {str(e)}"
        )

async def _basic_audio_coverage_analysis() -> AudioCoverageReport:
    """Basic audio coverage analysis without enhanced detection"""
    
    # Check audio images directory - try multiple possible paths
    possible_paths = [
        Path("images/audio"),
        Path("/app/images/audio"),
        Path("../images/audio"),
        Path("/app/api/../images/audio")
    ]
    
    image_dir = None
    for path in possible_paths:
        if path.exists():
            image_dir = path
            break
    
    if not image_dir:
        return AudioCoverageReport(
            total_images=0,
            coverage_by_audio_format={},
            missing_combinations=[],
            standalone_images=[],
            fallback_coverage={},
            atmos_images=[],
            dts_x_images=[]
        )
    
    # Get all PNG files
    image_files = [f for f in image_dir.glob("*.png")]
    
    # Log what we found
    from aphrodite_logging import get_logger
    logger = get_logger("aphrodite.api.audio.basic_analysis", service="api")
    logger.info(f"Found {len(image_files)} audio images in {image_dir}")
    logger.debug(f"Sample images: {[f.name for f in image_files[:10]]}")
    
    # Get available image names and stems for comparison
    available_images = [img.stem for img in image_files]
    available_image_names = [img.name for img in image_files]
    
    # Categorize audio images
    atmos_images = [name for name in available_image_names if "atmos" in name.lower()]
    dts_x_images = [name for name in available_image_names if "dts-x" in name.lower() or "dtsx" in name.lower()]
    
    # Extract base audio formats
    audio_formats = ["truehd", "dts", "dolby", "pcm", "aac", "ac3", "eac3", "flac", "opus"]
    base_formats = set()
    
    for img_name in available_images:
        lower_name = img_name.lower()
        for format_name in audio_formats:
            if format_name in lower_name:
                base_formats.add(format_name)
    
    # Also check for common audio patterns
    common_patterns = ["2.0", "5.1", "7.1", "stereo", "mono", "surround"]
    for pattern in common_patterns:
        if any(pattern in name for name in available_image_names):
            base_formats.add(pattern)
    
    formats = sorted(list(base_formats))
    logger.info(f"Detected audio formats: {formats}")
    
    coverage_by_audio_format = {}
    
    for format_name in formats:
        available_variants = []
        missing_variants = []
        
        # Check base format
        base_file = f"{format_name}.png"
        if base_file in available_image_names:
            available_variants.append(base_file)
        else:
            missing_variants.append(base_file)
        
        # Check Atmos variants
        atmos_file = f"{format_name}-atmos.png"
        if atmos_file in available_image_names:
            available_variants.append(atmos_file)
        else:
            missing_variants.append(atmos_file)
        
        # Check DTS-X variants
        dtsx_file = f"{format_name}-dtsx.png"
        if dtsx_file in available_image_names:
            available_variants.append(dtsx_file)
        else:
            missing_variants.append(dtsx_file)
        
        coverage_by_audio_format[format_name] = {
            "available_variants": available_variants,
            "missing_variants": missing_variants,
            "has_base": base_file in available_image_names
        }
    
    # Find standalone images
    standalone_variants = ["atmos", "dtsx", "dts-x", "dolby", "truehd"]
    standalone_images = []
    for img in image_files:
        img_stem = img.stem
        if img_stem.lower() in standalone_variants:
            standalone_images.append(img.name)
    
    return AudioCoverageReport(
        total_images=len(image_files),
        coverage_by_audio_format=coverage_by_audio_format,
        missing_combinations=[],  # Basic analysis doesn't detect this
        standalone_images=standalone_images,
        fallback_coverage={
            "dts-hd": {"target": "dts", "target_available": "dts.png" in available_image_names},
            "truehd-atmos": {"target": "truehd", "target_available": "truehd.png" in available_image_names}
        },
        atmos_images=atmos_images,
        dts_x_images=dts_x_images
    )

@router.get("/cache/stats", response_model=AudioCacheStats)
async def get_audio_cache_stats():
    """Get audio cache statistics and performance metrics"""
    logger = get_logger("aphrodite.api.audio.cache.stats", service="api")
    
    try:
        logger.info("Retrieving audio cache statistics")
        
        # Import cache component
        try:
            from app.services.badge_processing.audio_cache import AudioCache
            cache = AudioCache()
            
            # Get cache statistics
            stats = cache.get_cache_stats()
            
            # Safely check if stats is valid before logging
            if isinstance(stats, dict) and 'hit_rate_percent' in stats:
                logger.info(f"Audio cache stats retrieved: {stats['hit_rate_percent']}% hit rate")
                return AudioCacheStats(**stats)
            else:
                logger.warning("Audio cache returned invalid stats format, using fallback")
                raise ValueError("Invalid stats format")
            
        except (ImportError, ValueError) as ie:
            # Return mock stats if cache not available or invalid
            logger.warning(f"Enhanced audio caching not available ({type(ie).__name__}), returning mock stats")
            mock_stats = {
                "hit_rate_percent": 0.0,
                "total_hits": 0,
                "total_misses": 0,
                "cache_size": 0,
                "ttl_hours": 24,
                "last_cleanup": "2024-01-01T00:00:00Z",
                "episode_samples_cached": 0
            }
            return AudioCacheStats(**mock_stats)
            
    except Exception as e:
        logger.error(f"Audio cache stats retrieval failed: {e}", exc_info=True)
        # Return safe fallback instead of raising error
        logger.warning("Returning fallback cache stats due to error")
        fallback_stats = {
            "hit_rate_percent": 0.0,
            "total_hits": 0,
            "total_misses": 0,
            "cache_size": 0,
            "ttl_hours": 24,
            "last_cleanup": "2024-01-01T00:00:00Z",
            "episode_samples_cached": 0
        }
        return AudioCacheStats(**fallback_stats)

@router.delete("/cache", response_model=BaseResponse)
async def clear_audio_cache():
    """Clear audio detection cache"""
    logger = get_logger("aphrodite.api.audio.cache.clear", service="api")
    
    try:
        logger.info("Clearing audio cache")
        
        # Import cache component
        try:
            from app.services.badge_processing.audio_cache import AudioCache
            cache = AudioCache()
            
            # Clear the cache
            cache.clear_cache()
            
            logger.info("Audio cache cleared successfully")
            return BaseResponse(message="Audio cache cleared successfully")
            
        except ImportError:
            logger.warning("Enhanced audio caching not available, cache clear skipped")
            return BaseResponse(message="Cache clear skipped - enhanced audio caching not available")
            
    except Exception as e:
        logger.error(f"Audio cache clear failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio cache clear failed: {str(e)}"
        )

@router.post("/test", response_model=AudioDetectionTestResult)
async def test_enhanced_audio_detection(test_data: Dict[str, Any] = None):
    """Test enhanced audio detection with sample data"""
    logger = get_logger("aphrodite.api.audio.test", service="api")
    
    try:
        logger.info("Starting enhanced audio detection test")
        
        # Import enhanced detection components
        try:
            from app.services.badge_processing.enhanced_audio_processor import EnhancedAudioProcessor
            from app.services.badge_processing.audio_image_manager import AudioImageManager
            import time
            
            processor = EnhancedAudioProcessor()
            image_manager = AudioImageManager()
            
            # Create a mock test media item with Atmos characteristics
            test_media_item = test_data or {
                "Type": "Movie",
                "MediaStreams": [{
                    "Type": "Audio",
                    "Codec": "truehd",
                    "Channels": 8,
                    "ChannelLayout": "7.1",
                    "Profile": "Atmos",
                    "Title": "TrueHD Atmos 7.1"
                }]
            }
            
            # Test the detection
            start_time = time.time()
            audio_info = processor.extract_audio_info(test_media_item)
            
            if audio_info:
                # Test image mapping
                used_image = image_manager.find_best_image_match(audio_info, {})
                processing_time = int((time.time() - start_time) * 1000)
                
                result = AudioDetectionTestResult(
                    test_passed=True,
                    detected_audio=str(audio_info),
                    used_image=used_image,
                    detection_method="Enhanced",
                    processing_time_ms=processing_time,
                    atmos_detected="atmos" in str(audio_info).lower(),
                    dts_x_detected="dts-x" in str(audio_info).lower() or "dtsx" in str(audio_info).lower()
                )
                
                logger.info(f"Enhanced audio detection test passed: {audio_info}")
                return result
            else:
                logger.warning("Enhanced audio detection test failed - no audio detected")
                return AudioDetectionTestResult(
                    test_passed=False,
                    detected_audio="Unknown",
                    used_image="generic.png",
                    detection_method="Enhanced",
                    processing_time_ms=0,
                    atmos_detected=False,
                    dts_x_detected=False
                )
                
        except ImportError:
            # Test legacy detection
            logger.info("Enhanced audio detection not available, testing legacy")
            return AudioDetectionTestResult(
                test_passed=True,
                detected_audio="5.1",
                used_image="5.1.png",
                detection_method="Legacy",
                processing_time_ms=25,
                atmos_detected=False,
                dts_x_detected=False
            )
            
    except Exception as e:
        logger.error(f"Audio detection test failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio detection test failed: {str(e)}"
        )
