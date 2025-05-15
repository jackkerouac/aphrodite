#!/usr/bin/env python3
# aphrodite_helpers/badge_components/font_utils.py

import os
from PIL import ImageFont
from .color_utils import clean_hex_color

def load_font(font_family, fallback_font, font_size):
    """Load a font with proper fallbacks and error handling."""
    # Clean font strings
    font_family = clean_hex_color(font_family)
    fallback_font = clean_hex_color(fallback_font)
    
    # Look for fonts in the system and in the local directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fonts_dir = os.path.join(root_dir, 'fonts')
    
    # Check if fonts directory exists, create if not
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir, exist_ok=True)
        print(f"Created fonts directory at {fonts_dir}")
        
    # Prioritize fonts directory for better reliability
    font_paths = [
        os.path.join(fonts_dir, font_family),  # First check fonts directory for primary font
        font_family,  # Try direct path/system font
        os.path.join(root_dir, font_family),  # Try in root directory
        os.path.join(fonts_dir, fallback_font),  # Check fonts directory for fallback
        fallback_font,  # Try direct path/system font for fallback
        os.path.join(root_dir, fallback_font)  # Try fallback in root
    ]
    
    # Try all font paths in order
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size=int(font_size))
            print(f"✅ Successfully loaded font: {font_path} at size {font_size}")
            return font
        except Exception as e:
            print(f"⚠️ Warning: Could not load font {font_path}: {e}")
            continue
    
    # If all font paths fail, use default
    print(f"⚠️ Warning: Could not load any specified fonts, using default")
    return ImageFont.load_default()
