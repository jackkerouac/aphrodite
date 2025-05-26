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