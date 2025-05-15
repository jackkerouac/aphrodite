# aphrodite_helpers/check_jellyfin_connection.py

import yaml
import requests
import os

def load_settings(path="settings.yaml"):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, path)
    with open(full_path, 'r') as f:
        return yaml.safe_load(f)

def get_jellyfin_libraries(url, api_key, user_id):
    headers = {"X-Emby-Token": api_key}
    resp = requests.get(f"{url}/Users/{user_id}/Views", headers=headers)
    resp.raise_for_status()
    return resp.json().get('Items', [])

def get_library_item_count(url, api_key, user_id, view_id):
    headers = {"X-Emby-Token": api_key}
    params = {
        "ParentId": view_id,
        "Recursive": "true",
        "StartIndex": 0,
        "Limit": 1
    }
    resp = requests.get(f"{url}/Users/{user_id}/Items", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("TotalRecordCount", 0)
