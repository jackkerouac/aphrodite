#!/usr/bin/env python3
# aphrodite_helpers/get_resolution_info.py

import os
import sys
import yaml
import requests
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_settings(path="settings.yaml"):
    """Load settings from the settings file."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, path)
    try:
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: Settings file {path} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing settings: {e}")
        return None

def get_jellyfin_item_details(url, api_key, user_id, item_id):
    """Get detailed information about a Jellyfin item."""
    headers = {"X-Emby-Token": api_key}
    endpoint = f"{url}/Users/{user_id}/Items/{item_id}"
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching item details: {e}")
        return None

def get_media_resolution_info(url, api_key, user_id, item_id):
    """Get media resolution information from Jellyfin."""
    item_details = get_jellyfin_item_details(url, api_key, user_id, item_id)
    if not item_details:
        return None
    
    # Extract media streams
    media_streams = item_details.get('MediaStreams', [])
    
    # Initialize result dictionary
    result = {
        'id': item_id,
        'name': item_details.get('Name', 'Unknown'),
        'type': item_details.get('Type', 'Unknown'),
        'resolution': 'Unknown',
        'height': 0,
        'width': 0,
        'dv': False,  # Dolby Vision
        'hdr': False,  # HDR
        'has_plus': False  # Enhanced version indicator
    }
    
    # Process video streams to find resolution info
    for stream in media_streams:
        if stream.get('Type', '').lower() == 'video':
            # Get resolution details
            height = stream.get('Height', 0)
            width = stream.get('Width', 0)
            result['height'] = height
            result['width'] = width
            
            # Check for HDR and Dolby Vision in tags or profiles
            tags = stream.get('Tags', [])
            codec_tag = stream.get('CodecTag', '').lower()
            codec_profile = stream.get('Profile', '').lower()
            
            # Special case for 4K resolution
            if height >= 2160 or width >= 3840:
                result['resolution'] = '4k'
            elif height >= 1080 or width >= 1920:
                result['resolution'] = '1080p'
            elif height >= 720 or width >= 1280:
                result['resolution'] = '720p'
            elif height >= 576 or width >= 720:
                result['resolution'] = '576p'
            elif height >= 480 or width >= 640:
                result['resolution'] = '480p'
            else:
                result['resolution'] = f"{height}p"
            
            # Check for HDR and Dolby Vision
            if any(tag.lower() in ['dolby vision', 'dv', 'dolbyvision'] for tag in tags) or 'dolby vision' in codec_profile:
                result['dv'] = True
            
            if any(tag.lower() in ['hdr', 'hdr10', 'hdr10+'] for tag in tags) or 'hdr' in codec_profile:
                result['hdr'] = True
            
            # Check for "plus" version (could be customized based on your needs)
            # For example, high bitrate or enhanced audio might trigger this
            if stream.get('BitRate', 0) > 15000000:  # Example: Bitrate > 15Mbps
                result['has_plus'] = True
            
            break  # Stop after processing the first video stream
    
    return result

def get_resolution_badge_text(media_info):
    """Generate the appropriate badge text based on resolution info."""
    if not media_info:
        return "UNKNOWN"
    
    # Start with base resolution
    badge_text = media_info['resolution']
    
    # Add suffixes based on features
    if media_info['dv'] and media_info['hdr'] and media_info['has_plus']:
        badge_text += "dvhdrplus"
    elif media_info['dv'] and media_info['hdr']:
        badge_text += "dvhdr"
    elif media_info['dv'] and media_info['has_plus']:
        badge_text += "dvplus"
    elif media_info['hdr'] and media_info['has_plus']:
        badge_text += "hdrplus"
    elif media_info['dv']:
        badge_text += "dv"
    elif media_info['hdr']:
        badge_text += "hdr"
    elif media_info['has_plus']:
        badge_text += "plus"
    
    return badge_text

def fetch_item_and_create_resolution_badge(jellyfin_url, api_key, user_id, item_id, output_dir="posters/modified"):
    """Fetch item information and create a badge with the resolution."""
    # Import here to avoid circular imports
    from aphrodite_helpers.apply_resolution_badge import download_and_badge_poster
    
    # Get resolution info
    media_info = get_media_resolution_info(jellyfin_url, api_key, user_id, item_id)
    if not media_info:
        print(f"❌ Could not retrieve media information for item {item_id}")
        return False
    
    # Get the resolution badge text
    resolution_text = get_resolution_badge_text(media_info)
    print(f"📏 Found resolution: {resolution_text} for {media_info['name']}")
    
    # Create badge and apply to poster
    success = download_and_badge_poster(
        jellyfin_url=jellyfin_url,
        api_key=api_key,
        item_id=item_id, 
        badge_text=resolution_text,
        output_dir=output_dir,
        use_image=True  # Enable image-based badges
    )
    
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch resolution information from Jellyfin and create badges.")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--output", default="posters/modified", help="Output directory for modified posters")
    parser.add_argument("--info-only", action="store_true", help="Only display information, don't create badge")
    
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    if not settings:
        sys.exit(1)
    
    jellyfin_settings = settings['api_keys']['Jellyfin'][0]
    url = jellyfin_settings['url']
    api_key = jellyfin_settings['api_key']
    user_id = jellyfin_settings['user_id']
    
    if args.info_only:
        # Just display information
        media_info = get_media_resolution_info(url, api_key, user_id, args.itemid)
        if media_info:
            print(f"\n📋 Resolution Information for {media_info['name']}:")
            print(f"  ID: {media_info['id']}")
            print(f"  Type: {media_info['type']}")
            print(f"  Resolution: {media_info['resolution']} ({media_info['width']}x{media_info['height']})")
            print(f"  Dolby Vision: {'Yes' if media_info['dv'] else 'No'}")
            print(f"  HDR: {'Yes' if media_info['hdr'] else 'No'}")
            print(f"  Enhanced Version: {'Yes' if media_info['has_plus'] else 'No'}")
            
            badge_text = get_resolution_badge_text(media_info)
            print(f"\n🏷️ Badge Text: {badge_text}")
        else:
            print(f"❌ Failed to retrieve resolution information for item ID: {args.itemid}")
            sys.exit(1)
    else:
        # Create badge with resolution
        success = fetch_item_and_create_resolution_badge(url, api_key, user_id, args.itemid, args.output)
        if not success:
            print(f"❌ Failed to create resolution badge for item ID: {args.itemid}")
            sys.exit(1)