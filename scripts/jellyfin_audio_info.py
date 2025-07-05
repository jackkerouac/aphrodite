#!/usr/bin/env python3
"""
Jellyfin Audio Information Extractor

This script fetches audio stream information for a specific media item from Jellyfin.
Used for analyzing audio metadata before refactoring the audio badge process.

Usage:
    python jellyfin_audio_info.py <media_item_id>

Example:
    python jellyfin_audio_info.py 12345
"""

import sys
import json
import requests
from typing import Dict, List, Optional

# =============================================================================
# CONFIGURATION - Update these values for your Jellyfin instance
# =============================================================================

JELLYFIN_URL = "https://jellyfin.okaymedia.ca"  # Your Jellyfin server URL
JELLYFIN_API_KEY = "16dc3768e2754ff8b445a4728323a5e8"  # Your Jellyfin API key
JELLYFIN_USER_ID = "484068279393441885f9272eba479ccd"  # Your Jellyfin User ID

# =============================================================================
# Script Logic - No need to modify below this line
# =============================================================================

def get_media_info(media_id: str) -> Optional[Dict]:
    """
    Fetch media information from Jellyfin for the specified media item.
    
    Args:
        media_id: The Jellyfin media item ID
        
    Returns:
        Dict containing media information or None if failed
    """
    url = f"{JELLYFIN_URL}/Items/{media_id}"
    
    headers = {
        "X-Emby-Token": JELLYFIN_API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "UserId": JELLYFIN_USER_ID,
        "Fields": "MediaStreams,MediaSources"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching media info: {e}")
        return None

def extract_audio_streams(media_info: Dict) -> List[Dict]:
    """
    Extract only audio streams from the media information.
    
    Args:
        media_info: Full media information from Jellyfin
        
    Returns:
        List of audio stream dictionaries
    """
    if not media_info:
        return []
    
    media_streams = media_info.get("MediaStreams", [])
    audio_streams = [
        stream for stream in media_streams 
        if stream.get("Type") == "Audio"
    ]
    
    return audio_streams

def format_audio_info(audio_streams: List[Dict]) -> None:
    """
    Print formatted audio stream information.
    
    Args:
        audio_streams: List of audio stream dictionaries
    """
    if not audio_streams:
        print("No audio streams found.")
        return
    
    print(f"\nFound {len(audio_streams)} audio stream(s):")
    print("=" * 60)
    
    for i, stream in enumerate(audio_streams, 1):
        print(f"\nAudio Stream {i}:")
        print(f"  Index: {stream.get('Index', 'N/A')}")
        print(f"  Codec: {stream.get('Codec', 'N/A')}")
        print(f"  Language: {stream.get('Language', 'N/A')}")
        print(f"  Display Title: {stream.get('DisplayTitle', 'N/A')}")
        print(f"  Channels: {stream.get('Channels', 'N/A')}")
        print(f"  Is Default: {stream.get('IsDefault', False)}")
        print(f"  Is Forced: {stream.get('IsForced', False)}")
        
        # Additional useful fields for badge generation
        if stream.get('BitRate'):
            print(f"  Bit Rate: {stream.get('BitRate')} bps")
        if stream.get('SampleRate'):
            print(f"  Sample Rate: {stream.get('SampleRate')} Hz")
        if stream.get('Profile'):
            print(f"  Profile: {stream.get('Profile')}")

def print_raw_json(audio_streams: List[Dict]) -> None:
    """
    Print raw JSON for debugging purposes.
    
    Args:
        audio_streams: List of audio stream dictionaries
    """
    print("\n" + "=" * 60)
    print("RAW JSON OUTPUT:")
    print("=" * 60)
    print(json.dumps(audio_streams, indent=2))

def main():
    """Main script execution."""
    if len(sys.argv) != 2:
        print("Usage: python jellyfin_audio_info.py <media_item_id>")
        print("Example: python jellyfin_audio_info.py 12345")
        sys.exit(1)
    
    media_id = sys.argv[1]
    
    # Validate configuration
    if JELLYFIN_API_KEY == "your_api_key_here" or JELLYFIN_USER_ID == "your_user_id_here":
        print("ERROR: Please update JELLYFIN_API_KEY and JELLYFIN_USER_ID in the script.")
        sys.exit(1)
    
    print(f"Fetching audio information for media ID: {media_id}")
    print(f"Jellyfin URL: {JELLYFIN_URL}")
    
    # Fetch media information
    media_info = get_media_info(media_id)
    if not media_info:
        print("Failed to fetch media information.")
        sys.exit(1)
    
    # Extract and display audio streams
    audio_streams = extract_audio_streams(media_info)
    format_audio_info(audio_streams)
    
    # Print raw JSON for reference
    print_raw_json(audio_streams)
    
    print(f"\nMedia Title: {media_info.get('Name', 'N/A')}")
    print(f"Media Type: {media_info.get('Type', 'N/A')}")

if __name__ == "__main__":
    main()
