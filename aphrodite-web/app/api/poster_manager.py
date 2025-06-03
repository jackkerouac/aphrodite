from flask import Blueprint, jsonify, request
import sys
import os
import json
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from aphrodite_helpers.check_jellyfin_connection import (
        load_settings,
        get_jellyfin_libraries
    )
    from app.api.jellyfin_helpers import get_library_items_with_posters
    logger.info("Successfully imported dependencies for poster_manager")
except ImportError as e:
    logger.error(f"Import error in poster_manager: {e}")
    raise

bp = Blueprint('poster_manager', __name__, url_prefix='/api/poster-manager')
logger.info("Poster manager blueprint created")

# Test route to verify the blueprint is working
@bp.route('/test', methods=['GET'])
def test_poster_manager():
    """Test route to verify poster manager API is working"""
    return jsonify({
        'success': True,
        'message': 'Poster Manager API is working',
        'blueprint': 'poster_manager'
    })

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

@bp.route('/item/<item_id>/details', methods=['GET'])
def get_item_details(item_id):
    """Get detailed information about a specific item's poster"""
    try:
        # Load settings to get paths
        settings = load_settings()
        if not settings:
            return jsonify({
                'success': False,
                'message': 'Failed to load settings'
            }), 500
        
        # Get Jellyfin connection details
        jf = settings["api_keys"]["Jellyfin"][0]
        url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
        
        # Get item information from Jellyfin (with metadata tags)
        item_info = get_jellyfin_item_details(url, api_key, user_id, item_id)
        
        # Get poster file information
        poster_status = get_enhanced_poster_status(item_id, item_info.get('tags', []))
        
        # Get badge history if available
        badge_history = get_badge_history(item_id)
        
        return jsonify({
            'success': True,
            'item': item_info,
            'poster_status': poster_status,
            'badge_history': badge_history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching item details: {str(e)}'
        }), 500

def get_jellyfin_item_details(url, api_key, user_id, item_id):
    """Get detailed item information from Jellyfin"""
    import requests
    
    item_url = f"{url}/Users/{user_id}/Items/{item_id}"
    params = {
        'Fields': 'PrimaryImageAspectRatio,ImageTags,Overview,ProductionYear,Genres,Tags',
        'api_key': api_key
    }
    
    response = requests.get(item_url, params=params)
    response.raise_for_status()
    
    item = response.json()
    poster_url = None
    if item.get('ImageTags', {}).get('Primary'):
        poster_url = f"{url}/Items/{item['Id']}/Images/Primary?api_key={api_key}"
    
    return {
        'id': item['Id'],
        'name': item['Name'],
        'type': item['Type'],
        'poster_url': poster_url,
        'year': item.get('ProductionYear'),
        'overview': item.get('Overview', ''),
        'genres': item.get('Genres', []),
        'tags': item.get('Tags', [])
    }

def get_enhanced_poster_status(item_id, tags):
    """Get poster status based on metadata tags and file existence"""
    # Check if item has aphrodite-overlay metadata tag
    has_badges = 'aphrodite-overlay' in tags
    
    # Determine the base directory
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        base_dir = '/app'
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    
    # Check for original poster with multiple extensions
    original_path = None
    has_original = False
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        test_path = os.path.join(base_dir, 'posters', 'original', f"{item_id}{ext}")
        if os.path.exists(test_path):
            original_path = test_path
            has_original = True
            break
    
    # Check for modified poster with multiple extensions
    modified_path = None
    has_modified = False
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        test_path = os.path.join(base_dir, 'posters', 'modified', f"{item_id}{ext}")
        if os.path.exists(test_path):
            modified_path = test_path
            has_modified = True
            break
    
    status = {
        'has_original': has_original,
        'has_modified': has_modified,
        'has_badges': has_badges,  # Based on metadata tag
        'current_source': 'badged' if has_badges else 'original',
        'can_revert': has_original and has_badges  # Only allow revert if original exists and has badges
    }
    
    # Get file timestamps if they exist
    if status['has_original'] and original_path:
        status['original_modified'] = datetime.fromtimestamp(
            os.path.getmtime(original_path)
        ).isoformat()
    
    if status['has_modified'] and modified_path:
        status['modified_created'] = datetime.fromtimestamp(
            os.path.getmtime(modified_path)
        ).isoformat()
    
    return status

def get_poster_status(item_id):
    """Legacy function - kept for backward compatibility"""
    # This function is kept for any legacy code that might still call it
    # New code should use get_enhanced_poster_status instead
    return get_enhanced_poster_status(item_id, [])

def get_badge_history(item_id):
    """Get badge application history for an item"""
    # This is a placeholder for future badge history tracking
    # For now, return basic information
    return {
        'last_processed': None,
        'badges_applied': [],
        'processing_count': 0
    }
