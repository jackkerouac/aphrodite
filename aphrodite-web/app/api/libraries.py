from flask import Blueprint, jsonify
import sys
import os

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from aphrodite_helpers.check_jellyfin_connection import (
    load_settings,
    get_jellyfin_libraries
)
from app.api.jellyfin_helpers import get_library_parent_items_count

bp = Blueprint('libraries', __name__, url_prefix='/api/libraries')

@bp.route('/', methods=['GET'])
def get_libraries():
    """Get list of available Jellyfin libraries"""
    try:
        # Load Jellyfin settings
        settings = load_settings()
        if not settings:
            return jsonify({
                'success': False,
                'message': 'Failed to load settings'
            }), 500
        
        # Get Jellyfin connection details
        jf = settings["api_keys"]["Jellyfin"][0]
        url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
        
        # Get libraries from Jellyfin
        libraries = get_jellyfin_libraries(url, api_key, user_id)
        
        # Get item count for each library (only parent items)
        libraries_with_count = []
        for lib in libraries:
            # Get parent-level item count (series, movies, not episodes)
            item_count = get_library_parent_items_count(url, api_key, user_id, lib['Id'])
            libraries_with_count.append({
                'id': lib['Id'],
                'name': lib['Name'],
                'itemCount': item_count
            })
        
        return jsonify({
            'success': True,
            'libraries': libraries_with_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching libraries: {str(e)}'
        }), 500
