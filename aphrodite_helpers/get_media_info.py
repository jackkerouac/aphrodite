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

def _extract_audio_codec_from_display_title(display_title):
    """Extract clean audio codec name from Jellyfin's DisplayTitle.
    
    Examples:
    'AAC - Stereo - Default' -> 'AAC'
    'DTS-HD MA 7.1 - Default' -> 'DTS-HD MA'
    'TrueHD Atmos 7.1' -> 'TrueHD Atmos'
    'AC3 5.1' -> 'AC3'
    """
    if not display_title:
        return 'UNKNOWN'
    
    # Remove common suffixes
    clean_title = display_title.replace(' - Default', '').replace(' - External', '')
    
    # Handle specific codec patterns
    title_lower = clean_title.lower()
    
    # DTS variants (order matters - check specific variants first)
    if 'dts-x' in title_lower or 'dtsx' in title_lower:
        return 'DTS-X'
    elif 'dts-hd ma' in title_lower or 'dts-hd master' in title_lower:
        return 'DTS-HD MA'
    elif 'dts-hd hr' in title_lower or 'dts-hd high' in title_lower:
        return 'DTS-HD HR'
    elif 'dts-hd' in title_lower:
        return 'DTS-HD'
    elif 'dts' in title_lower:
        return 'DTS'
    
    # TrueHD and Atmos
    if 'truehd' in title_lower and 'atmos' in title_lower:
        return 'TrueHD Atmos'
    elif 'truehd' in title_lower:
        return 'TrueHD'
    elif 'atmos' in title_lower:
        return 'Atmos'
    
    # Common codecs
    if 'aac' in title_lower:
        return 'AAC'
    elif 'ac3' in title_lower or 'ac-3' in title_lower:
        return 'AC3'
    elif 'eac3' in title_lower or 'e-ac3' in title_lower or 'eac-3' in title_lower:
        return 'EAC3'
    elif 'flac' in title_lower:
        return 'FLAC'
    elif 'pcm' in title_lower:
        return 'PCM'
    elif 'mp3' in title_lower:
        return 'MP3'
    elif 'opus' in title_lower:
        return 'Opus'
    elif 'vorbis' in title_lower:
        return 'Vorbis'
    
    # If no specific codec found, try to extract the first word/segment
    # Split by common delimiters and take the first meaningful part
    parts = clean_title.replace(' - ', ' ').split()
    if parts:
        first_part = parts[0].strip()
        # Return first part if it looks like a codec name (contains letters)
        if any(c.isalpha() for c in first_part):
            return first_part.upper()
    
    # Last resort: return the whole cleaned title
    return clean_title.strip()

def load_settings(path="settings.yaml"):
    """Load settings from the database or YAML file via compatibility layer."""
    try:
        from aphrodite_helpers.settings_compat import load_settings as compat_load_settings
        return compat_load_settings(path)
    except ImportError:
        # Fallback to direct YAML loading if compatibility layer is not available
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
            # PRIMARY: Use Jellyfin's pre-computed DisplayTitle if available
            display_title = stream.get('DisplayTitle', '')
            
            if display_title:
                # Use Jellyfin's human-readable audio description
                display_name = _extract_audio_codec_from_display_title(display_title)
            else:
                # FALLBACK: Manual construction from individual fields
                codec = stream.get('Codec', 'Unknown')
                channels = stream.get('Channels', 0)
                display_name = f"{codec.upper()} {channels}.0" if channels else codec.upper()
            
            result['audio_codecs'].append({
                'codec': stream.get('Codec', 'Unknown'),
                'channels': stream.get('Channels', 0),
                'display_title': display_title,
                'display_name': display_name
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
    try:
        # Import here to avoid circular imports
        from aphrodite_helpers.apply_badge import download_and_badge_poster
        
        # Pass user_id to get_media_stream_info
        media_info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
        if not media_info:
            print(f"❌ Could not retrieve media information for item {item_id}")
            return False
        
        # Get the primary audio codec
        audio_codec = get_primary_audio_codec(media_info)
        print(f"📢 Found audio codec: {audio_codec} for {media_info['name']}")
        
        # Skip if audio codec is UNKNOWN
        if audio_codec.upper() == "UNKNOWN":
            print(f"⚠️ Skipping audio badge as codec is unknown")
            return False
        
        # Create badge and apply to poster
        success = download_and_badge_poster(
            jellyfin_url=jellyfin_url,
            api_key=api_key,
            item_id=item_id, 
            badge_text=audio_codec,
            output_dir=output_dir,
            use_image=True  # Enable image-based badges
        )
        
        return success
    except Exception as e:
        print(f"❌ Error creating audio badge: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

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