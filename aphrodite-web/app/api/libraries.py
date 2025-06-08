from flask import Blueprint, jsonify
import sys
import os
import logging

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from aphrodite_helpers.check_jellyfin_connection import (
    load_settings,
    get_jellyfin_libraries
)
from app.api.jellyfin_helpers import get_library_parent_items_count
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

bp = Blueprint('libraries', __name__, url_prefix='/api/libraries')

@bp.route('/', methods=['GET'])
def get_libraries():
    """Get list of available Jellyfin libraries"""
    try:
        # Load Jellyfin settings directly from database (preferred) or fallback to YAML
        url, api_key, user_id = None, None, None
        
        try:
            # Try to load from database first (most up-to-date)
            logger.info('Attempting to load Jellyfin settings from database...')
            settings_service = SettingsService()
            jellyfin_keys = settings_service.get_api_keys('Jellyfin')
            
            if jellyfin_keys and len(jellyfin_keys) > 0:
                jf = jellyfin_keys[0]
                url = jf.get('url')
                api_key = jf.get('api_key') 
                user_id = jf.get('user_id')
                logger.info(f'Successfully loaded Jellyfin settings from database: {url}')
            else:
                logger.warning('No Jellyfin settings found in database')
        except Exception as db_error:
            logger.warning(f'Failed to load from database: {db_error}')
        
        # Fallback to YAML if database load failed or returned empty
        if not all([url, api_key, user_id]):
            logger.info('Falling back to YAML settings...')
            settings = load_settings()
            if not settings or 'api_keys' not in settings or 'Jellyfin' not in settings['api_keys']:
                return jsonify({
                    'success': False,
                    'message': 'Failed to load Jellyfin settings from database or YAML'
                }), 500
            
            jf = settings["api_keys"]["Jellyfin"][0]
            url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
            logger.info(f'Successfully loaded Jellyfin settings from YAML: {url}')
        
        # Validate that we have all required settings
        if not all([url, api_key, user_id]):
            return jsonify({
                'success': False,
                'message': 'Incomplete Jellyfin configuration (missing URL, API key, or user ID)'
            }), 500
        
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
