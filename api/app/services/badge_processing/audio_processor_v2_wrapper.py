"""
V2 Audio Processor Compatibility Wrapper
"""

from .v2_audio_processor import V2AudioBadgeProcessor

# Backward compatibility
class AudioBadgeProcessor(V2AudioBadgeProcessor):
    """Compatibility wrapper for V2AudioBadgeProcessor"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("⚠️ [COMPATIBILITY] Using V2 audio processor through compatibility wrapper")
