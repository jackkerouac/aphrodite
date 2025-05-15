#!/usr/bin/env python3
# test_download_and_badge.py

import os
import sys
import argparse
import yaml
from aphrodite_helpers.apply_badge import download_and_badge_poster

def main():
    parser = argparse.ArgumentParser(description="Test downloading and badging a poster from Jellyfin.")
    parser.add_argument(
        "--itemid", 
        required=True,
        help="Jellyfin item ID"
    )
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
        "--output",
        default="posters/modified",
        help="Output directory for modified posters"
    )
    
    args = parser.parse_args()
    
    # Load settings to get the API info
    root_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(root_dir, "settings.yaml")
    
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)
        
        # Get the Jellyfin connection info
        jellyfin_url = settings['api_keys']['Jellyfin'][0]['url']
        api_key = settings['api_keys']['Jellyfin'][0]['api_key']
        
        print(f"Connecting to Jellyfin server: {jellyfin_url}")
        print(f"Downloading and badging poster for item: {args.itemid}")
        print(f"Badge text: {args.text}")
        
        # Download and badge the poster
        success = download_and_badge_poster(
            jellyfin_url=jellyfin_url,
            api_key=api_key,
            item_id=args.itemid,
            badge_text=args.text,
            output_dir=args.output,
            settings_file=args.settings
        )
        
    except Exception as e:
        print(f"Error: {e}")
        success = False
    
    print("Process completed successfully" if success else "Process failed")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
