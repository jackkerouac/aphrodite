#!/usr/bin/env python3
# test_text_settings.py

import os
import sys
import argparse
import yaml
from aphrodite_helpers.apply_badge import save_test_badge, load_badge_settings

def main():
    parser = argparse.ArgumentParser(description="Test text settings in badge creation.")
    parser.add_argument(
        "--text", 
        default="DTS-HD MA", 
        help="Text to display in the badge"
    )
    parser.add_argument(
        "--settings",
        default="badge_settings_audio.yml",
        help="Badge settings file"
    )
    parser.add_argument(
        "--font",
        help="Override font name for testing"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        help="Override font size for testing"
    )
    parser.add_argument(
        "--text-color",
        help="Override text color for testing (hex format)"
    )
    
    args = parser.parse_args()
    
    print(f"Testing badge with text: '{args.text}'")
    print(f"Using settings file: {args.settings}")
    
    # Load settings to override if needed
    root_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(root_dir, args.settings)
    
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)
            
        # Apply any overrides
        if args.font:
            print(f"Overriding font: {args.font}")
            settings['Text']['font'] = args.font
            
        if args.font_size:
            print(f"Overriding font size: {args.font_size}")
            settings['Text']['text-size'] = args.font_size
            
        if args.text_color:
            print(f"Overriding text color: {args.text_color}")
            settings['Text']['text-color'] = args.text_color
            
        # Save the modified settings to a temporary file
        temp_settings_path = os.path.join(root_dir, "temp_settings.yml")
        with open(temp_settings_path, 'w') as f:
            yaml.dump(settings, f)
            
        # Use the temporary settings file
        success = save_test_badge(temp_settings_path, args.text)
        
        # Clean up
        if os.path.exists(temp_settings_path):
            os.remove(temp_settings_path)
            
    except Exception as e:
        print(f"Error: {e}")
        success = False
    
    print("Test completed successfully" if success else "Test failed")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
