"""
Enhanced Audio Components Integration
Handles initialization and management of enhanced audio detection components.
"""

from typing import Dict, Any, Optional
from aphrodite_logging import get_logger

# Enhanced audio detection components
try:
    from .audio_types import AudioInfo, DetectionPatterns, FallbackRules
    from .audio_detector import EnhancedAudioDetector
    from .audio_image_manager import AudioImageManager
    from .audio_parallel_processor import ParallelAudioProcessor
    from .audio_cache import AudioCache
    
    ENHANCED_COMPONENTS_AVAILABLE = True
except ImportError as e:
    ENHANCED_COMPONENTS_AVAILABLE = False
    import_error = e


class EnhancedAudioComponents:
    """Manages enhanced audio detection components"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.audio.enhanced", service="badge")
        self.enabled = False
        self._init_components()
    
    def _init_components(self):
        """Initialize enhanced audio detection components"""
        if ENHANCED_COMPONENTS_AVAILABLE:
            try:
                self.detector = EnhancedAudioDetector()
                self.image_manager = AudioImageManager()
                self.parallel_processor = ParallelAudioProcessor(self.detector)
                self.cache = AudioCache()
                
                self.logger.info("🚀 [ENHANCED AUDIO] Components initialized successfully")
                self.enabled = True
                
            except Exception as e:
                self.logger.warning(f"⚠️ [ENHANCED AUDIO] Component init failed: {e}")
                self.enabled = False
        else:
            self.logger.warning(f"⚠️ [ENHANCED AUDIO] Components not available: {import_error}")
            self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of enhanced components for diagnostics"""
        if not self.enabled:
            return {
                "enhanced_enabled": False,
                "error": str(import_error) if not ENHANCED_COMPONENTS_AVAILABLE else "Initialization failed"
            }
        
        return {
            "enhanced_enabled": True,
            "detector_available": hasattr(self, 'detector'),
            "image_manager_available": hasattr(self, 'image_manager'),
            "parallel_processor_available": hasattr(self, 'parallel_processor'),
            "cache_available": hasattr(self, 'cache'),
            "cache_stats": self.cache.get_cache_stats() if hasattr(self, 'cache') else None,
            "image_coverage": self.image_manager.get_coverage_analysis() if hasattr(self, 'image_manager') else None
        }
    
    def clear_cache(self) -> bool:
        """Clear audio cache"""
        if self.enabled and hasattr(self, 'cache'):
            self.cache.clear_cache()
            return True
        return False
