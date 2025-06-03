import sys
import os

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings
import requests

def get_library_parent_items_count(url, api_key, user_id, view_id):
    """Get the number of parent-level items in a library (not including child items like episodes)."""
    headers = {"X-Emby-Token": api_key}
    params = {
        "ParentId": view_id,
        "Recursive": "false",  # Only get direct children of the library
        "IncludeItemTypes": "Series,Movie,MusicAlbum",  # Only count parent-level items
        "StartIndex": 0,
        "Limit": 1
    }
    try:
        resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=params)
        resp.raise_for_status()
        return resp.json().get("TotalRecordCount", 0)
    except requests.RequestException as e:
        print(f"Error: Error getting parent item count: {e}")
        return 0

def get_library_items_with_posters(url, api_key, user_id, library_id):
    """Helper function to get library items with poster URLs"""
    # Get items from the library with metadata tags
    items_url = f"{url}/Users/{user_id}/Items"
    params = {
        'ParentId': library_id,
        'Recursive': 'true',
        'IncludeItemTypes': 'Movie,Series',
        'Fields': 'PrimaryImageAspectRatio,ImageTags,Tags',  # Added Tags field
        'api_key': api_key
    }
    
    response = requests.get(items_url, params=params)
    response.raise_for_status()
    
    data = response.json()
    items = []
    
    # Determine base directory for poster file checks
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        base_dir = '/app'
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    
    for item in data.get('Items', []):
        poster_url = None
        if item.get('ImageTags', {}).get('Primary'):
            poster_url = f"{url}/Items/{item['Id']}/Images/Primary?api_key={api_key}"
        
        # Check if item has aphrodite-overlay metadata tag
        tags = item.get('Tags', [])
        has_aphrodite_tag = 'aphrodite-overlay' in tags
        
        # Check if original poster file exists (check multiple extensions)
        item_id = item['Id']
        has_original_poster = False
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            original_poster_path = os.path.join(base_dir, 'posters', 'original', f"{item_id}{ext}")
            if os.path.exists(original_poster_path):
                has_original_poster = True
                break
        
        items.append({
            'id': item['Id'],
            'name': item['Name'],
            'type': item['Type'],
            'poster_url': poster_url,
            'year': item.get('ProductionYear'),
            'overview': item.get('Overview', '')[:200] + '...' if item.get('Overview', '') else '',
            'has_badges': has_aphrodite_tag,  # Based on metadata tag
            'has_original_poster': has_original_poster  # Based on file existence
        })
    
    return items
