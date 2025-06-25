"""
Color Utilities

Pure V2 color processing functions.
"""

from typing import Tuple, Union
import colorsys
from aphrodite_logging import get_logger


class ColorUtils:
    """Pure V2 color processing utilities"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.color", service="badge")
    
    def hex_to_rgba(self, hex_color: str, opacity: int = 100) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple with opacity"""
        try:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Parse hex color
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
            elif len(hex_color) == 3:
                r = int(hex_color[0] * 2, 16)
                g = int(hex_color[1] * 2, 16)
                b = int(hex_color[2] * 2, 16)
            else:
                raise ValueError(f"Invalid hex color format: {hex_color}")
            
            # Calculate alpha from opacity percentage
            alpha = int((opacity / 100) * 255)
            
            return (r, g, b, alpha)
            
        except Exception as e:
            self.logger.error(f"Error converting hex color {hex_color}: {e}")
            # Return default color (black with specified opacity)
            alpha = int((opacity / 100) * 255)
            return (0, 0, 0, alpha)
    
    def rgba_to_hex(self, rgba: Tuple[int, int, int, int]) -> str:
        """Convert RGBA tuple to hex color string"""
        r, g, b, a = rgba
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def adjust_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust brightness of hex color by factor (0.0 to 2.0)"""
        try:
            # Convert to RGB
            rgba = self.hex_to_rgba(hex_color, 100)
            r, g, b = rgba[:3]
            
            # Convert to HSV for brightness adjustment
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            # Adjust brightness
            v = max(0.0, min(1.0, v * factor))
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except Exception as e:
            self.logger.error(f"Error adjusting brightness for {hex_color}: {e}")
            return hex_color
    
    def get_contrasting_color(self, hex_color: str) -> str:
        """Get contrasting color (black or white) for given background color"""
        try:
            rgba = self.hex_to_rgba(hex_color, 100)
            r, g, b = rgba[:3]
            
            # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Return white for dark backgrounds, black for light backgrounds
            return "#FFFFFF" if luminance < 0.5 else "#000000"
            
        except Exception as e:
            self.logger.error(f"Error getting contrasting color for {hex_color}: {e}")
            return "#FFFFFF"  # Default to white
    
    def blend_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Blend two hex colors with given ratio (0.0 = color1, 1.0 = color2)"""
        try:
            rgba1 = self.hex_to_rgba(color1, 100)[:3]
            rgba2 = self.hex_to_rgba(color2, 100)[:3]
            
            # Blend each channel
            r = int(rgba1[0] * (1 - ratio) + rgba2[0] * ratio)
            g = int(rgba1[1] * (1 - ratio) + rgba2[1] * ratio)
            b = int(rgba1[2] * (1 - ratio) + rgba2[2] * ratio)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except Exception as e:
            self.logger.error(f"Error blending colors {color1} and {color2}: {e}")
            return color1
