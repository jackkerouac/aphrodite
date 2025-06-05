# aphrodite_helpers/check_jellyfin_connection.py

import yaml
import requests
import os
import sys

# Import the compatibility layer
from aphrodite_helpers.settings_compat import load_settings

def get_jellyfin_libraries(url, api_key, user_id):
    """Get all libraries (views) from Jellyfin for a specific user."""
    headers = {"X-Emby-Token": api_key}
    try:
        resp = requests.get(f"{url}/Users/{user_id}/Views", headers=headers)
        resp.raise_for_status()
        return resp.json().get('Items', [])
    except requests.RequestException as e:
        print(f"Error: Error connecting to Jellyfin: {e}")
        return []

def get_library_item_count(url, api_key, user_id, view_id):
    """Get the total number of items in a Jellyfin library."""
    headers = {"X-Emby-Token": api_key}
    params = {
        "ParentId": view_id,
        "Recursive": "true",
        "StartIndex": 0,
        "Limit": 1
    }
    
    try:
        resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=params)
        resp.raise_for_status()
        
        return resp.json().get("TotalRecordCount", 0)
    except requests.RequestException as e:
        print(f"Error: Error getting library item count: {e}")
        return 0


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

def get_library_items(url, api_key, user_id, view_id, limit=None):
    """Get all items in a specific Jellyfin library (view)."""
    headers = {"X-Emby-Token": api_key}
    
    # First, determine the library type (Movies, TV Shows, etc.)
    library_info_resp = requests.get(f"{url}/Users/{user_id}/Views", headers=headers)
    library_info_resp.raise_for_status()
    libraries = library_info_resp.json().get('Items', [])
    
    library_info = next((lib for lib in libraries if lib.get('Id') == view_id), None)
    library_type = library_info.get('CollectionType', '') if library_info else ''
    
    print(f"Library type detected: {library_type}")
    
    # Setup appropriate parameters based on library type
    params = {
        "ParentId": view_id,
        "StartIndex": 0,
        "Limit": 1
    }
    
    # For TV libraries (Series, Anime, etc.), we only want series, not episodes
    if library_type in ['tvshows', 'homevideos']:
        params["IncludeItemTypes"] = "Series"
        params["Recursive"] = "true"
    else:
        # For movies, we can use standard parameters
        params["Recursive"] = "true"
    
    # Get total count with the appropriate filters
    count_resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=params)
    count_resp.raise_for_status()
    total_count = count_resp.json().get("TotalRecordCount", 0)
    
    if total_count == 0:
        return []
    
    # If limit is specified, use it; otherwise, get all items
    if limit:
        total_count = min(total_count, limit)
    
    items = []
    batch_size = 100  # Jellyfin API fetches results in batches
    
    # Remove Limit parameter and prepare for batch fetching
    params.pop("Limit")
    
    # Fetch items in batches
    for start_index in range(0, total_count, batch_size):
        batch_params = params.copy()
        batch_params["StartIndex"] = start_index
        batch_params["Limit"] = min(batch_size, total_count - start_index)
        
        try:
            resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=batch_params)
            resp.raise_for_status()
            
            batch_items = resp.json().get('Items', [])
            items.extend(batch_items)
            
            # Print progress for large libraries
            if total_count > batch_size:
                items_fetched = min(start_index + batch_size, total_count)
                print(f"Fetched {items_fetched}/{total_count} items...")
            
        except requests.RequestException as e:
            print(f"Error: Error fetching items (batch starting at {start_index}): {e}")
            continue
    
    return items

def check_jellyfin_connection(url, api_key, user_id=None):
    """Check if we can connect to the Jellyfin server."""
    headers = {"X-Emby-Token": api_key}
    try:
        # First, check if the server is responding at all
        resp = requests.get(f"{url}/System/Info", headers=headers)
        resp.raise_for_status()
        
        server_info = resp.json()
        server_name = server_info.get('ServerName', 'Unknown')
        version = server_info.get('Version', 'Unknown')
        
        print(f"Success: Connected to Jellyfin server: {server_name} (Version {version})")
        
        # If user_id is provided, check if we can access the user's data
        if user_id:
            resp = requests.get(f"{url}/Users/{user_id}", headers=headers)
            resp.raise_for_status()
            
            user_info = resp.json()
            user_name = user_info.get('Name', 'Unknown')
            
            print(f"Success: Authenticated as user: {user_name}")
        
        return True
    except requests.RequestException as e:
        print(f"Error: Error connecting to Jellyfin: {e}")
        return False

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Jellyfin connection.")
    parser.add_argument("--url", help="Jellyfin server URL")
    parser.add_argument("--api-key", help="Jellyfin API key")
    parser.add_argument("--user-id", help="Jellyfin user ID")
    
    args = parser.parse_args()
    
    if args.url and args.api_key:
        # Use provided arguments
        url = args.url
        api_key = args.api_key
        user_id = args.user_id
    else:
        # Load from settings.yaml
        settings = load_settings()
        if not settings:
            sys.exit(1)
        
        jellyfin_settings = settings['api_keys']['Jellyfin'][0]
        url = jellyfin_settings['url']
        api_key = jellyfin_settings['api_key']
        user_id = jellyfin_settings.get('user_id')
    
    # Check connection
    if check_jellyfin_connection(url, api_key, user_id):
        print("\nAvailable libraries:")
        libraries = get_jellyfin_libraries(url, api_key, user_id)
        
        if not libraries:
            print("  None found")
        else:
            for lib in libraries:
                lib_name = lib.get('Name', 'Unnamed')
                lib_id = lib.get('Id')
                count = get_library_item_count(url, api_key, user_id, lib_id)
                print(f"  - {lib_name} (ID: {lib_id}): {count} items")
    else:
        sys.exit(1)
