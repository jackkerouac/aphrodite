#!/usr/bin/env python3
# aphrodite_helpers/get_media_info.py

import os
import sys
import yaml
import json # Though json is imported, it's not explicitly used in this file. Could be removed if not needed.
import requests
from pathlib import Path # Path is imported but not used. Could be removed.

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

# MODIFIED: Changed endpoint to include user_id
def get_jellyfin_item_details(url, api_key, user_id, item_id):
    """Get detailed information about a Jellyfin item."""
    headers = {"X-Emby-Token": api_key}
    # CHANGED: Use the /Users/{UserId}/Items/{ItemId} endpoint structure
    endpoint = f"{url}/Users/{user_id}/Items/{item_id}"
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching item details: {e}")
        return None

# MODIFIED: Added user_id as a parameter
def get_media_stream_info(url, api_key, user_id, item_id):
    """Get media streams (audio, video, subtitle) information from Jellyfin."""
    # Now user_id is correctly passed from this function's arguments
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
        'audio_codecs': [],
        'video_codecs': [],
        'subtitles': []
    }
    
    # Process streams
    for stream in media_streams:
        stream_type = stream.get('Type', '').lower()
        
        if stream_type == 'audio':
            codec = stream.get('Codec', 'Unknown')
            channels = stream.get('Channels', 0)
            result['audio_codecs'].append({
                'codec': codec,
                'channels': channels,
                'display_name': f"{codec.upper()} {channels}.0" if channels else codec.upper()
            })
        
        elif stream_type == 'video':
            codec = stream.get('Codec', 'Unknown')
            result['video_codecs'].append({
                'codec': codec,
                'display_name': codec.upper()
            })
        
        elif stream_type == 'subtitle':
            language = stream.get('Language', 'Unknown')
            result['subtitles'].append(language)
    
    return result

def get_primary_audio_codec(media_info):
    """Extract the primary audio codec from media info."""
    if not media_info or not media_info.get('audio_codecs'):
        return "UNKNOWN"
    
    # Get the first audio codec
    primary_audio = media_info['audio_codecs'][0]
    return primary_audio.get('display_name', 'UNKNOWN')

# MODIFIED: Added user_id as a parameter and pass it to get_media_stream_info
def fetch_item_and_create_badge(jellyfin_url, api_key, user_id, item_id, output_dir="posters/modified"):
    """Fetch item information and create a badge with the audio codec."""
    # Import here to avoid circular imports
    from aphrodite_helpers.apply_badge import download_and_badge_poster # Assuming this doesn't need user_id directly or gets it another way
    
    # Pass user_id to get_media_stream_info
    media_info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
    if not media_info:
        print(f"❌ Could not retrieve media information for item {item_id}")
        return False
    
    # Get the primary audio codec
    audio_codec = get_primary_audio_codec(media_info)
    print(f"📢 Found audio codec: {audio_codec} for {media_info['name']}")
    
    # Create badge and apply to poster
    # If download_and_badge_poster needs user_id, you might need to pass it here too.
    # For now, assuming it primarily uses item_id for poster fetching as per its name.
    success = download_and_badge_poster(
        jellyfin_url=jellyfin_url,
        api_key=api_key,
        item_id=item_id, 
        badge_text=audio_codec,
        output_dir=output_dir,
        use_image=True  # Enable image-based badges
    )
    
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch media information from Jellyfin and create badges.")
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
    # MODIFIED: Load user_id from settings
    user_id = jellyfin_settings['user_id'] # Make sure 'user_id' exists in your settings.yaml for Jellyfin
    
    if args.info_only:
        # Just display information
        # MODIFIED: Pass user_id to get_media_stream_info
        media_info = get_media_stream_info(url, api_key, user_id, args.itemid)
        if media_info:
            print(f"\n📋 Media Information for {media_info['name']}:")
            print(f"  ID: {media_info['id']}")
            print(f"  Type: {media_info['type']}")
            
            if media_info['audio_codecs']:
                print("\n🔊 Audio Codecs:")
                for i, codec_info in enumerate(media_info['audio_codecs'], 1): # Renamed codec to codec_info to avoid confusion
                    print(f"  {i}. {codec_info['display_name']} ({codec_info['codec']}, {codec_info['channels']} channels)")
            
            if media_info['video_codecs']:
                print("\n🎬 Video Codecs:")
                for i, codec_info in enumerate(media_info['video_codecs'], 1): # Renamed codec to codec_info
                    print(f"  {i}. {codec_info['display_name']}")
            
            if media_info['subtitles']:
                print("\n📄 Subtitles:")
                for i, lang in enumerate(media_info['subtitles'], 1):
                    print(f"  {i}. {lang}")
        else:
            print(f"❌ Failed to retrieve media information for item ID: {args.itemid}")
            sys.exit(1)
    else:
        # Create badge with audio codec
        # MODIFIED: Pass user_id to fetch_item_and_create_badge
        success = fetch_item_and_create_badge(url, api_key, user_id, args.itemid, args.output)
        if not success:
            print(f"❌ Failed to create badge for item ID: {args.itemid}")
            sys.exit(1)