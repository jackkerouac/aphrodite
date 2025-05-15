#!/usr/bin/env python3
# test_badge_fix.py - Test the fixed badge generator

import os
import sys
import time

# Add the project's main directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aphrodite_helpers.badge_components.badge_settings import load_badge_settings
from aphrodite_helpers.badge_components.badge_generator import create_badge

def main():
    """Test if our fixes resolved the badge styling issues."""
    print("Testing badge fixes...")
    
    # Load badge settings
    settings = load_badge_settings("badge_settings_audio.yml")
    if not settings:
        print("Failed to load settings")
        return False
    
    # Verify settings
    print(f"Background color: {settings.get('Background', {}).get('background-color')}")
    print(f"Border radius: {settings.get('Border', {}).get('border-radius')}")
    
    # Create a text badge
    text_badge = create_badge(settings, "DTS-HD MA", use_image=False)
    if text_badge:
        text_badge.save("test_text_badge.png")
        print("Text badge saved as test_text_badge.png")
    
    # Create an image badge
    image_badge = create_badge(settings, "DTS-HD MA", use_image=True)
    if image_badge:
        image_badge.save("test_image_badge.png")
        print("Image badge saved as test_image_badge.png")
    
    print("\nTest complete. Please check the generated badge images to verify:")
    print("1. Yellow background color (#FFFF00) is applied to both badges")
    print("2. Border radius (130) is applied to both badges")
    print("3. Image badge shows the DTS-HD logo with proper styling")
    
    return True

if __name__ == "__main__":
    main()
