from flask import jsonify, request
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings
from app.api.jellyfin_helpers import get_library_items_with_posters

def register_library_routes(bp):
    """Register library-related routes"""
    
    @bp.route('/library/<library_id>', methods=['GET'])
    def get_library_posters(library_id):
        """Get all items with poster information for a specific library"""
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
