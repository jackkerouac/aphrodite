#!/usr/bin/env python3
# aphrodite_helpers/apply_badge.py

import os
import sys
import argparse

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import badge components
from aphrodite_helpers.badge_components import (
    load_badge_settings,
    create_badge,
    apply_badge_to_poster,
    process_all_posters,
    save_test_badge
)

def main():
    """Main entry point for the apply_badge script."""
    parser = argparse.ArgumentParser(description="Apply badges to poster images.")
    parser.add_argument(
        "--input", 
        default="posters/original", 
        help="Directory containing original posters"
    )
    parser.add_argument(
        "--working", 
        default="posters/working", 
        help="Working directory for temporary files"
    )
    parser.add_argument(
        "--output", 
        default="posters/modified", 
        help="Output directory for modified posters"
    )
    parser.add_argument(
        "--settings", 
        default="badge_settings_audio.yml", 
        help="Badge settings file"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Generate a test badge without processing posters"
    )
    parser.add_argument(
        "--text",
        help="Text to display in badge"
    )
    parser.add_argument(
        "--use-image",
        action="store_true",
        help="Use image-based badges instead of text where possible"
    )
    parser.add_argument(
        "--force-text",
        action="store_true",
        help="Force text-based badges even when images are available"
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = save_test_badge(args.settings, args.text, not args.force_text)
    else:
        success = process_all_posters(
            poster_dir=args.input,
            working_dir=args.working,
            output_dir=args.output,
            settings_file=args.settings,
            badge_text=args.text,
            use_image=not args.force_text
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
