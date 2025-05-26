#!/usr/bin/env python3
# aphrodite_helpers/badge_components/color_utils.py

def clean_hex_color(hex_color):
    """Clean a hex color string from any wrapping characters (like backticks)."""
    if not isinstance(hex_color, str):
        return hex_color
    
    # Remove any backticks or quotes around the color
    cleaned = hex_color.replace('`', '').replace('"', '').replace("'", '').strip()
    return cleaned

def hex_to_rgba(hex_color, opacity=100):
    """Convert hex color to RGBA tuple."""
    # Clean the hex color string
    hex_color = clean_hex_color(hex_color)
        
    if not isinstance(hex_color, str) or not hex_color.startswith('#'):
        print(f"⚠️ Warning: Invalid hex color format: {hex_color}, using default red")
        return (255, 0, 0, int(255 * opacity / 100))  # Default red with opacity
    
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, int(255 * opacity / 100))
    elif len(hex_color) == 3:
        r, g, b = tuple(int(hex_color[i] + hex_color[i], 16) for i in range(3))
        return (r, g, b, int(255 * opacity / 100))
    else:
        print(f"⚠️ Warning: Invalid hex color length: {hex_color}, using default red")
        return (255, 0, 0, int(255 * opacity / 100))  # Default red with opacity
