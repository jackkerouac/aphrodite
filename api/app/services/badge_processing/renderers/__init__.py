"""
Badge Rendering Engine

Pure V2 badge rendering components - no V1 dependencies.
"""

from .badge_renderer import UnifiedBadgeRenderer
from .font_manager import FontManager
from .color_utils import ColorUtils
from .positioning import BadgePositioning

__all__ = [
    'UnifiedBadgeRenderer',
    'FontManager', 
    'ColorUtils',
    'BadgePositioning'
]
