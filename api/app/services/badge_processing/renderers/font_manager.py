"""
Font Management

Pure V2 font loading and text measurement utilities.
"""

from typing import Optional, Dict, Tuple
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image
from aphrodite_logging import get_logger


class FontManager:
    """Pure V2 font management utilities"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.fonts", service="badge")
        self._font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
        
        # Standard font paths in Docker container
        self.font_paths = [
            "/app/assets/fonts",
            "/app/fonts", 
            "/usr/share/fonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/TTF",
            "/System/Library/Fonts",  # macOS
            "C:/Windows/Fonts"       # Windows
        ]
    
    def load_font(self, font_name: str, size: int, fallback_font: str = "DejaVuSans.ttf") -> ImageFont.FreeTypeFont:
        """Load font with fallback support"""
        cache_key = f"{font_name}_{size}"
        
        # Check cache first
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Try to load primary font
        font = self._load_font_file(font_name, size)
        
        # Try fallback font if primary fails
        if not font and fallback_font != font_name:
            self.logger.debug(f"Primary font {font_name} failed, trying fallback: {fallback_font}")
            font = self._load_font_file(fallback_font, size)
        
        # Use default system font if all else fails
        if not font:
            self.logger.warning(f"All fonts failed, using default system font at size {size}")
            try:
                font = ImageFont.load_default()
            except Exception as e:
                self.logger.error(f"Even default font failed: {e}")
                # Create a minimal working font
                font = ImageFont.load_default()
        
        # Cache and return
        self._font_cache[cache_key] = font
        return font
    
    def _load_font_file(self, font_name: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load font file from various paths"""
        try:
            # Try each font path
            for font_path in self.font_paths:
                font_file_path = Path(font_path) / font_name
                
                if font_file_path.exists():
                    self.logger.debug(f"Loading font: {font_file_path}")
                    return ImageFont.truetype(str(font_file_path), size)
            
            # Try loading directly by name (system font)
            try:
                return ImageFont.truetype(font_name, size)
            except OSError:
                pass
            
            self.logger.warning(f"Font file not found: {font_name}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading font {font_name}: {e}")
            return None
    
    def measure_text(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Measure text dimensions with given font"""
        try:
            # Create temporary image for measurement
            temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
            draw = ImageDraw.Draw(temp_img)
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            return (width, height)
            
        except Exception as e:
            self.logger.error(f"Error measuring text '{text}': {e}")
            # Return reasonable fallback dimensions
            return (len(text) * 12, 16)
    
    def get_text_size_for_width(self, text: str, font_name: str, max_width: int, 
                                fallback_font: str = "DejaVuSans.ttf") -> ImageFont.FreeTypeFont:
        """Find the largest font size that fits text within max_width"""
        try:
            # Start with reasonable size and adjust
            for size in range(40, 8, -2):  # Try sizes from 40 down to 8
                font = self.load_font(font_name, size, fallback_font)
                text_width, _ = self.measure_text(text, font)
                
                if text_width <= max_width:
                    self.logger.debug(f"Text '{text}' fits at size {size} (width: {text_width}/{max_width})")
                    return font
            
            # If nothing fits, use minimum size
            self.logger.warning(f"Text '{text}' doesn't fit in {max_width}px, using minimum size")
            return self.load_font(font_name, 8, fallback_font)
            
        except Exception as e:
            self.logger.error(f"Error finding font size for text '{text}': {e}")
            return self.load_font(font_name, 12, fallback_font)
    
    def clear_cache(self):
        """Clear font cache"""
        self._font_cache.clear()
        self.logger.debug("Font cache cleared")
