from flask import jsonify, request
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings
from app.api.jellyfin_helpers import get_library_items_with_posters
from app.services.settings_service import SettingsService

def register_library_routes(bp):
    """Register library-related routes"""
    
    @bp.route('/library/<library_id>', methods=['GET'])
    def get_library_posters(library_id):
        """Get all items with poster information for a specific library"""
        try:
            # Load Jellyfin settings directly from database (preferred) or fallback to YAML
            url, api_key, user_id = None, None, None
            
            try:
                # Try to load from database first (most up-to-date)
                logger.info(f'Loading Jellyfin settings from database for library {library_id}...')
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
            
            # Get search query parameters
            search_query = request.args.get('search', '').lower()
            media_type = request.args.get('type', '')  # 'movie', 'series', etc.
            badge_status = request.args.get('badges', '')  # 'badged', 'original'
            
            # Get library items with poster information
            items = get_library_items_with_posters(url, api_key, user_id, library_id)
            
            # Apply filters
            filtered_items = []
            for item in items:
                # Search filter
                if search_query and search_query not in item['name'].lower():
                    continue
                    
                # Media type filter
                if media_type and item.get('type', '').lower() != media_type.lower():
                    continue
                    
                # Badge status filter (using aphrodite-overlay metadata tag)
                if badge_status:
                    has_badges = item.get('has_badges', False)
                    if badge_status == 'badged' and not has_badges:
                        continue
                    elif badge_status == 'original' and has_badges:
                        continue
                
                # Add poster status information
                item['poster_status'] = {
                    'has_original': item.get('has_original_poster', False),
                    'has_badges': item.get('has_badges', False),
                    'has_modified': item.get('has_badges', False),  # Frontend compatibility
                    'current_source': 'badged' if item.get('has_badges', False) else 'original'
                }
                filtered_items.append(item)
            
            return jsonify({
                'success': True,
                'items': filtered_items,
                'total': len(filtered_items)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error fetching library posters: {str(e)}'
            }), 500
