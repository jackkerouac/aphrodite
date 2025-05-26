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
