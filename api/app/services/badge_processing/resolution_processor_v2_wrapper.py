"""
V2 Resolution Processor Compatibility Wrapper
"""

from .v2_resolution_processor import V2ResolutionBadgeProcessor

# Backward compatibility
class ResolutionBadgeProcessor(V2ResolutionBadgeProcessor):
    """Compatibility wrapper for V2ResolutionBadgeProcessor"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("⚠️ [COMPATIBILITY] Using V2 resolution processor through compatibility wrapper")
