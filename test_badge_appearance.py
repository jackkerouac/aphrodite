#!/usr/bin/env python3
# test_badge_appearance.py

import os
import sys
import argparse
import yaml
from aphrodite_helpers.apply_badge import save_test_badge

def main():
    parser = argparse.ArgumentParser(description="Test badge appearance with different settings.")
    parser.add_argument(
        "--text", 
        default="DTS-HD MA", 
        help="Text to display in the badge"
    )
    parser.add_argument(
        "--bg-color",
        help="Background color (hex format, e.g. #FF0000)"
    )
    parser.add_argument(
        "--bg-opacity",
        type=int,
        help="Background opacity (0-100)"
    )
    parser.add_argument(
        "--text-color",
        help="Text color (hex format, e.g. #FFFFFF)"
    )
    parser.add_argument(
        "--text-size",
        type=int,
        help="Text size in pixels"
    )
    parser.add_argument(
        "--font",
        help="Font name or file"
    )
    
    args = parser.parse_args()
    
    # Load the default settings
    root_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(root_dir, "badge_settings_audio.yml")
    
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)
        
        # Apply any overrides
        changes_made = False
        
        if args.bg_color:
            print(f"Setting background color to: {args.bg_color}")
            settings['Background']['background-color'] = args.bg_color
            changes_made = True
            
        if args.bg_opacity is not None:
            print(f"Setting background opacity to: {args.bg_opacity}")
            settings['Background']['background_opacity'] = args.bg_opacity
            changes_made = True
            
        if args.text_color:
            print(f"Setting text color to: {args.text_color}")
            settings['Text']['text-color'] = args.text_color
            changes_made = True
            
        if args.text_size:
            print(f"Setting text size to: {args.text_size}")
            settings['Text']['text-size'] = args.text_size
            changes_made = True
            
        if args.font:
            print(f"Setting font to: {args.font}")
            settings['Text']['font'] = args.font
            changes_made = True
        
        # Save the modified settings to a temporary file if changes were made
        if changes_made:
            temp_settings_path = os.path.join(root_dir, "temp_badge_settings.yml")
            with open(temp_settings_path, 'w') as f:
                yaml.dump(settings, f)
            
            # Use the temporary settings file
            success = save_test_badge(temp_settings_path, args.text)
            
            # Clean up
            if os.path.exists(temp_settings_path):
                os.remove(temp_settings_path)
        else:
            # Use the default settings file
            success = save_test_badge("badge_settings_audio.yml", args.text)
        
    except Exception as e:
        print(f"Error: {e}")
        success = False
    
    if success:
        print(f"✅ Test badge saved to {os.path.join(root_dir, 'test_badge.png')}")
    else:
        print("❌ Failed to create test badge")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
