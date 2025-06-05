import os
import subprocess
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_jellyfin_item_details(url, api_key, user_id, item_id):
    """Get detailed item information from Jellyfin"""
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
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    
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
        'has_modified': has_badges,  # Frontend compatibility - use metadata tag instead of file existence
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

def get_badge_history(item_id):
    """Get badge application history for an item"""
    # This is a placeholder for future badge history tracking
    # For now, return basic information
    return {
        'last_processed': None,
        'badges_applied': [],
        'processing_count': 0
    }

def run_aphrodite_command(item_id, selected_badges):
    """Run the aphrodite.py command for badge processing"""
    try:
        # Determine base directory (Docker-aware)
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            working_dir = '/app'
            cmd = ['python', '/app/aphrodite.py', 'item', item_id]
        else:
            working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
            cmd = ['python', os.path.join(working_dir, 'aphrodite.py'), 'item', item_id]
        
        # Add badge type flags based on selection
        all_badge_types = ['audio', 'resolution', 'review', 'awards']
        for badge_type in all_badge_types:
            if badge_type not in selected_badges:
                cmd.append(f'--no-{badge_type}')
        
        # Run the aphrodite.py command
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Set environment to ensure UTF-8 encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace problematic characters instead of failing
            cwd=working_dir,
            env=env
        )
        
        stdout, stderr = process.communicate()
        
        # Log the output for debugging
        logger.info(f"Command stdout: {stdout}")
        if stderr:
            logger.warning(f"Command stderr: {stderr}")
        
        # Determine success
        success = process.returncode == 0
        
        badge_list = ', '.join(selected_badges)
        result = {
            'success': success,
            'message': f'Badges ({badge_list}) successfully applied' if success else 'Failed to apply badges',
            'item_id': item_id,
            'badges_applied': selected_badges,
            'stdout': stdout[:1000] if stdout else '',  # Limit output size
            'stderr': stderr[:1000] if stderr else '',
            'returncode': process.returncode
        }
        
        if not success and stderr:
            result['error'] = stderr[:500]  # Include error for UI display
        
        return success, result
        
    except Exception as e:
        logger.error(f"Error running aphrodite command for item {item_id}: {str(e)}")
        return False, {
            'success': False,
            'error': str(e),
            'item_id': item_id
        }
