#!/usr/bin/env python3
# aphrodite_helpers/tv_series_aggregator.py

import os
import sys
import yaml
import requests
from collections import Counter

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.get_media_info import get_primary_audio_codec
from aphrodite_helpers.get_resolution_info import get_resolution_badge_text

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

def get_jellyfin_item_details(url, api_key, user_id, item_id, timeout=30):
    """Get detailed information about a Jellyfin item."""
    headers = {"X-Emby-Token": api_key}
    endpoint = f"{url}/Users/{user_id}/Items/{item_id}"
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print(f"⏰ Timeout fetching item details for {item_id} (waited {timeout}s)")
        return None
    except requests.RequestException as e:
        print(f"❌ Error fetching item details: {e}")
        return None

def get_series_episodes(url, api_key, user_id, series_id, max_episodes=None):
    """Get all episodes for a TV series with improved timeout and limits."""
    headers = {"X-Emby-Token": api_key}
    
    # Get episodes recursively from the series
    params = {
        "ParentId": series_id,
        "IncludeItemTypes": "Episode",
        "Recursive": "true",
        "StartIndex": 0
    }
    
    episodes = []
    batch_size = 50  # Reduced batch size for better performance
    timeout = 30  # Increased timeout
    
    # First, get the total count
    count_params = params.copy()
    count_params["Limit"] = 1
    
    try:
        print("📊 Getting episode count...")
        count_resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=count_params, timeout=timeout)
        count_resp.raise_for_status()
        total_count = count_resp.json().get("TotalRecordCount", 0)
        
        if total_count == 0:
            return []
        
        # Apply episode limit if specified
        if max_episodes and total_count > max_episodes:
            print(f"⚠️ Series has {total_count} episodes, limiting analysis to first {max_episodes} episodes")
            total_count = max_episodes
        
        print(f"📺 Fetching {total_count} episodes in batches of {batch_size}...")
        
        # Fetch episodes in batches
        for start_index in range(0, total_count, batch_size):
            batch_params = params.copy()
            batch_params["StartIndex"] = start_index
            batch_params["Limit"] = min(batch_size, total_count - start_index)
            
            print(f"📦 Fetching episodes {start_index + 1}-{min(start_index + batch_size, total_count)} of {total_count}...")
            
            resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=batch_params, timeout=timeout)
            resp.raise_for_status()
            
            batch_episodes = resp.json().get('Items', [])
            episodes.extend(batch_episodes)
            
            # Small delay between batches to avoid overwhelming the server
            if len(episodes) < total_count:
                import time
                time.sleep(0.5)
            
        print(f"✅ Successfully fetched {len(episodes)} episodes")
        return episodes
        
    except requests.Timeout:
        print(f"⏰ Timeout fetching episodes for series {series_id}. Try reducing episode count or check server performance.")
        return []
    except requests.RequestException as e:
        print(f"❌ Error fetching episodes for series {series_id}: {e}")
        return []

def is_tv_series(item_details):
    """Check if an item is a TV series."""
    return item_details and item_details.get('Type', '').lower() == 'series'

def get_dominant_audio_codec(url, api_key, user_id, series_id):
    """Get the most common audio codec across all episodes of a TV series."""
    # Get configuration values
    settings = load_settings()
    tv_settings = settings.get('tv_series', {}) if settings else {}
    max_episodes_to_analyze = tv_settings.get('max_episodes_to_analyze', 50)
    episode_timeout = tv_settings.get('episode_timeout', 15)
    episodes = get_series_episodes(url, api_key, user_id, series_id)
    
    if not episodes:
        print(f"⚠️ No episodes found for series {series_id}")
        return "UNKNOWN"
    
    # Limit episode analysis for performance
    if len(episodes) > max_episodes_to_analyze:
        print(f"📊 Series has {len(episodes)} episodes, analyzing first {max_episodes_to_analyze} for performance")
        episodes = episodes[:max_episodes_to_analyze]
    else:
        print(f"📊 Found {len(episodes)} episodes, analyzing audio codecs...")
    
    codec_counter = Counter()
    processed_episodes = 0
    failed_episodes = 0
    
    for i, episode in enumerate(episodes, 1):
        episode_id = episode.get('Id')
        if not episode_id:
            continue
            
        print(f"🔍 Analyzing episode {i}/{len(episodes)}...", end="")
        
        # Get episode media info with configurable timeout for individual episodes
        episode_details = get_jellyfin_item_details(url, api_key, user_id, episode_id, timeout=episode_timeout)
        if not episode_details:
            failed_episodes += 1
            print(" ❌ Failed")
            continue
            
        # Extract media streams for this episode
        media_streams = episode_details.get('MediaStreams', [])
        episode_info = {
            'id': episode_id,
            'name': episode_details.get('Name', 'Unknown'),
            'type': episode_details.get('Type', 'Unknown'),
            'audio_codecs': []
        }
        
        # Process audio streams
        for stream in media_streams:
            if stream.get('Type', '').lower() == 'audio':
                codec = stream.get('Codec', 'Unknown')
                channels = stream.get('Channels', 0)
                episode_info['audio_codecs'].append({
                    'codec': codec,
                    'channels': channels,
                    'display_name': f"{codec.upper()} {channels}.0" if channels else codec.upper()
                })
        
        # Get primary codec for this episode
        if episode_info['audio_codecs']:
            primary_codec = episode_info['audio_codecs'][0]['display_name']
            codec_counter[primary_codec] += 1
            processed_episodes += 1
            print(f" ✓ {primary_codec}")
        else:
            print(" ⚠️ No audio codec found")
    
    if not codec_counter:
        print("⚠️ No valid audio codecs found in any episodes")
        return "UNKNOWN"
    
    # Find the most common codec
    dominant_codec = codec_counter.most_common(1)[0][0]
    dominant_count = codec_counter[dominant_codec]
    
    print(f"\n📢 Dominant audio codec: {dominant_codec} ({dominant_count}/{processed_episodes} episodes)")
    if failed_episodes > 0:
        print(f"⚠️ {failed_episodes} episodes failed to analyze")
    
    # Show distribution for debugging
    print("📊 Audio codec distribution:")
    for codec, count in codec_counter.most_common():
        percentage = (count / processed_episodes) * 100
        print(f"  - {codec}: {count} episodes ({percentage:.1f}%)")
    
    return dominant_codec

def get_dominant_resolution(url, api_key, user_id, series_id):
    """Get the most common resolution across all episodes of a TV series."""
    # Get configuration values
    settings = load_settings()
    tv_settings = settings.get('tv_series', {}) if settings else {}
    max_episodes_to_analyze = tv_settings.get('max_episodes_to_analyze', 50)
    episode_timeout = tv_settings.get('episode_timeout', 15)
    episodes = get_series_episodes(url, api_key, user_id, series_id)
    
    if not episodes:
        print(f"⚠️ No episodes found for series {series_id}")
        return "UNKNOWN"
    
    # Limit episode analysis for performance
    if len(episodes) > max_episodes_to_analyze:
        print(f"📊 Series has {len(episodes)} episodes, analyzing first {max_episodes_to_analyze} for performance")
        episodes = episodes[:max_episodes_to_analyze]
    else:
        print(f"📊 Found {len(episodes)} episodes, analyzing resolutions...")
    
    resolution_counter = Counter()
    processed_episodes = 0
    failed_episodes = 0
    
    for i, episode in enumerate(episodes, 1):
        episode_id = episode.get('Id')
        if not episode_id:
            continue
            
        print(f"🔍 Analyzing episode {i}/{len(episodes)} resolution...", end="")
        
        # Get episode media info with configurable timeout  
        episode_details = get_jellyfin_item_details(url, api_key, user_id, episode_id, timeout=episode_timeout)
        if not episode_details:
            failed_episodes += 1
            print(" ❌ Failed")
            continue
            
        # Extract media streams for this episode  
        media_streams = episode_details.get('MediaStreams', [])
        episode_resolution_info = {
            'id': episode_id,
            'name': episode_details.get('Name', 'Unknown'),
            'type': episode_details.get('Type', 'Unknown'),
            'resolution': 'Unknown',
            'height': 0,
            'width': 0,
            'dv': False,
            'hdr': False,
            'has_plus': False
        }
        
        # Process video streams to find resolution info
        for stream in media_streams:
            if stream.get('Type', '').lower() == 'video':
                # Get resolution details
                height = stream.get('Height', 0)
                width = stream.get('Width', 0)
                episode_resolution_info['height'] = height
                episode_resolution_info['width'] = width
                
                # Check for HDR and Dolby Vision in tags or profiles
                tags = stream.get('Tags', [])
                codec_profile = stream.get('Profile', '').lower()
                
                # Determine resolution
                if height >= 2160 or width >= 3840:
                    episode_resolution_info['resolution'] = '4k'
                elif height >= 1080 or width >= 1920:
                    episode_resolution_info['resolution'] = '1080p'
                elif height >= 720 or width >= 1280:
                    episode_resolution_info['resolution'] = '720p'
                elif height >= 576 or width >= 720:
                    episode_resolution_info['resolution'] = '576p'
                elif height >= 480 or width >= 640:
                    episode_resolution_info['resolution'] = '480p'
                else:
                    episode_resolution_info['resolution'] = f"{height}p"
                
                # Check for HDR and Dolby Vision
                if any(tag.lower() in ['dolby vision', 'dv', 'dolbyvision'] for tag in tags) or 'dolby vision' in codec_profile:
                    episode_resolution_info['dv'] = True
                
                if any(tag.lower() in ['hdr', 'hdr10', 'hdr10+'] for tag in tags) or 'hdr' in codec_profile:
                    episode_resolution_info['hdr'] = True
                
                # Check for "plus" version
                if stream.get('BitRate', 0) > 15000000:  # Bitrate > 15Mbps
                    episode_resolution_info['has_plus'] = True
                
                break  # Stop after processing the first video stream
        
        # Generate resolution badge text for this episode
        resolution_text = get_resolution_badge_text(episode_resolution_info)
        if resolution_text.upper() != "UNKNOWN":
            resolution_counter[resolution_text] += 1
            processed_episodes += 1
            print(f" ✓ {resolution_text}")
        else:
            print(" ⚠️ No resolution found")
    
    if not resolution_counter:
        print("⚠️ No valid resolutions found in any episodes")
        return "UNKNOWN"
    
    # Find the most common resolution
    dominant_resolution = resolution_counter.most_common(1)[0][0]
    dominant_count = resolution_counter[dominant_resolution]
    
    print(f"\n📏 Dominant resolution: {dominant_resolution} ({dominant_count}/{processed_episodes} episodes)")
    if failed_episodes > 0:
        print(f"⚠️ {failed_episodes} episodes failed to analyze")
    
    # Show distribution for debugging
    print("📊 Resolution distribution:")
    for resolution, count in resolution_counter.most_common():
        percentage = (count / processed_episodes) * 100
        print(f"  - {resolution}: {count} episodes ({percentage:.1f}%)")
    
    return dominant_resolution

def should_use_dominant_badges():
    """Check if dominant badges are enabled in settings."""
    settings = load_settings()
    if not settings:
        return False
    
    tv_settings = settings.get('tv_series', {})
    return tv_settings.get('show_dominant_badges', False)

def get_series_dominant_badge_info(url, api_key, user_id, item_id):
    """
    Get dominant badge info for a TV series.
    Returns a dict with 'audio_codec' and 'resolution' or None if not applicable.
    """
    # Check if dominant badges are enabled
    if not should_use_dominant_badges():
        return None
    
    # Get item details to check if it's a series
    item_details = get_jellyfin_item_details(url, api_key, user_id, item_id)
    if not is_tv_series(item_details):
        return None
    
    series_name = item_details.get('Name', 'Unknown Series')
    print(f"📺 Processing TV series: {series_name}")
    
    # Get dominant audio codec and resolution
    dominant_audio = get_dominant_audio_codec(url, api_key, user_id, item_id)
    dominant_resolution = get_dominant_resolution(url, api_key, user_id, item_id)
    
    return {
        'audio_codec': dominant_audio,
        'resolution': dominant_resolution,
        'is_series': True,
        'name': series_name
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test TV series dominant badge functionality.")
    parser.add_argument("--series-id", required=True, help="TV series ID to analyze")
    parser.add_argument("--audio-only", action="store_true", help="Only analyze audio codecs")
    parser.add_argument("--resolution-only", action="store_true", help="Only analyze resolutions")
    
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    if not settings:
        sys.exit(1)
    
    jellyfin_settings = settings['api_keys']['Jellyfin'][0]
    url = jellyfin_settings['url']
    api_key = jellyfin_settings['api_key']
    user_id = jellyfin_settings['user_id']
    
    print(f"🔍 Analyzing series {args.series_id}")
    
    if args.audio_only:
        dominant_audio = get_dominant_audio_codec(url, api_key, user_id, args.series_id)
        print(f"\n🎵 Result: {dominant_audio}")
    elif args.resolution_only:
        dominant_resolution = get_dominant_resolution(url, api_key, user_id, args.series_id)
        print(f"\n📐 Result: {dominant_resolution}")
    else:
        # Full analysis
        result = get_series_dominant_badge_info(url, api_key, user_id, args.series_id)
        if result:
            print(f"\n✅ TV Series Badge Info for {result['name']}:")
            print(f"   🎵 Dominant Audio Codec: {result['audio_codec']}")
            print(f"   📐 Dominant Resolution: {result['resolution']}")
        else:
            print("\n❌ No dominant badge info available (not a series or feature disabled)")
