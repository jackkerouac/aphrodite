#!/usr/bin/env python3
# run_simple_test.py

import os
import sys
from aphrodite_helpers.apply_badge import save_test_badge

def main():
    print("Running simple badge test with text settings...")
    
    # Test with default settings
    success = save_test_badge("badge_settings_audio.yml", "DTS-HD MA")
    
    if success:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        test_badge_path = os.path.join(root_dir, "test_badge.png")
        print(f"✅ Test badge saved to {test_badge_path}")
        print("Please check that the text settings (font, color, size) are applied correctly.")
    else:
        print("❌ Failed to create test badge")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
