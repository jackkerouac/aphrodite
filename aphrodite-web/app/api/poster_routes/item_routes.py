from flask import jsonify, request
import sys
import os
import uuid
import threading
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings
from app.services.job import JobService
from app.services.settings_service import SettingsService
from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
from .utils import get_jellyfin_item_details, get_enhanced_poster_status, get_badge_history, run_aphrodite_command

def register_item_routes(bp):
    """Register individual item-related routes"""
    
    @bp.route('/item/<item_id>/details', methods=['GET'])
    def get_item_details(item_id):
        """Get detailed information about a specific item's poster"""
        try:
            # Load Jellyfin settings directly from database (preferred) or fallback to YAML
            url, api_key, user_id = None, None, None
            
            try:
                # Try to load from database first (most up-to-date)
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

    @bp.route('/item/<item_id>/reprocess', methods=['POST'])
    def reprocess_item_badges(item_id):
        """Re-apply badges to a single item (only if it doesn't already have badges)"""
        try:
            # Load Jellyfin settings with database priority
            url, api_key, user_id = None, None, None
            
            try:
                settings_service = SettingsService()
                jellyfin_keys = settings_service.get_api_keys('Jellyfin')
                
                if jellyfin_keys and len(jellyfin_keys) > 0:
                    jf = jellyfin_keys[0]
                    url, api_key, user_id = jf.get('url'), jf.get('api_key'), jf.get('user_id')
                    logger.info(f'Loaded Jellyfin settings from database for reprocess')
            except Exception:
                pass
            
            if not all([url, api_key, user_id]):
                settings = load_settings()
                if not settings or 'api_keys' not in settings or 'Jellyfin' not in settings['api_keys']:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to load Jellyfin settings'
                    }), 500
                
                jf = settings["api_keys"]["Jellyfin"][0]
                url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
            
            # Get request data for badge selection
            data = request.get_json() or {}
            selected_badges = data.get('badges', ['audio', 'resolution', 'review', 'awards'])
            
            # Validate badge types
            valid_badges = ['audio', 'resolution', 'review', 'awards']
            selected_badges = [badge for badge in selected_badges if badge in valid_badges]
            
            if not selected_badges:
                return jsonify({
                    'success': False,
                    'message': 'At least one badge type must be selected'
                }), 400
            
            # Get item information
            item_info = get_jellyfin_item_details(url, api_key, user_id, item_id)
            poster_status = get_enhanced_poster_status(item_id, item_info.get('tags', []))
            
            # Check if item already has badges (only allow reprocessing of original items)
            if poster_status.get('has_badges', False):
                return jsonify({
                    'success': False,
                    'message': 'Item already has badges. Use revert first if you want to re-apply badges.'
                }), 400
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Create job record
            job_details = {
                'id': job_id,
                'type': 'reprocess',
                'command': f'python aphrodite.py item {item_id}',
                'options': {'item_id': item_id, 'badges': selected_badges},
                'status': 'queued',
                'start_time': time.time(),
                'end_time': None,
                'result': None
            }
            
            JobService.create_job(job_details)
            
            # Start reprocessing in background thread
            def run_reprocess():
                success, result = run_aphrodite_command(item_id, selected_badges)
                
                JobService.update_job(job_id, {
                    'status': 'success' if success else 'failed',
                    'end_time': time.time(),
                    'result': result
                })
            
            thread = threading.Thread(target=run_reprocess)
            thread.daemon = True
            thread.start()
            
            badge_list = ', '.join(selected_badges)
            return jsonify({
                'success': True,
                'message': f'Reprocessing started for item {item_id} with badges: {badge_list}',
                'jobId': job_id
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error starting reprocess: {str(e)}'
            }), 500

    @bp.route('/item/<item_id>/revert', methods=['POST'])
    def revert_item_to_original(item_id):
        """Revert a single item's poster to its original state"""
        try:
            # Load Jellyfin settings with database priority
            url, api_key, user_id = None, None, None
            
            try:
                settings_service = SettingsService()
                jellyfin_keys = settings_service.get_api_keys('Jellyfin')
                
                if jellyfin_keys and len(jellyfin_keys) > 0:
                    jf = jellyfin_keys[0]
                    url, api_key, user_id = jf.get('url'), jf.get('api_key'), jf.get('user_id')
                    logger.info(f'Loaded Jellyfin settings from database for revert')
            except Exception:
                pass
            
            if not all([url, api_key, user_id]):
                settings = load_settings()
                if not settings or 'api_keys' not in settings or 'Jellyfin' not in settings['api_keys']:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to load Jellyfin settings'
                    }), 500
                
                jf = settings["api_keys"]["Jellyfin"][0]
                url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
            
            # Get item information
            item_info = get_jellyfin_item_details(url, api_key, user_id, item_id)
            poster_status = get_enhanced_poster_status(item_id, item_info.get('tags', []))
            
            # Check if revert is possible
            if not poster_status.get('can_revert', False):
                return jsonify({
                    'success': False,
                    'message': 'Cannot revert: item has no badges or original poster not found'
                }), 400
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Create job record
            job_details = {
                'id': job_id,
                'type': 'revert',
                'command': f'revert_item_{item_id}',
                'options': {'item_id': item_id},
                'status': 'queued',
                'start_time': time.time(),
                'end_time': None,
                'result': None
            }
            
            JobService.create_job(job_details)
            
            # Define function to run revert
            def run_revert():
                try:
                    # Determine base directory (Docker-aware)
                    is_docker = (
                        os.path.exists('/app') and 
                        os.path.exists('/app/settings.yaml') and 
                        os.path.exists('/.dockerenv')
                    )
                    
                    if is_docker:
                        base_dir = '/app'
                    else:
                        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
                    
                    # Find original poster with multiple extensions
                    original_path = None
                    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        test_path = os.path.join(base_dir, 'posters', 'original', f"{item_id}{ext}")
                        if os.path.exists(test_path):
                            original_path = test_path
                            break
                    
                    if not original_path:
                        raise Exception('Original poster not found')
                    
                    # Find modified poster to delete
                    modified_path = None
                    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        test_path = os.path.join(base_dir, 'posters', 'modified', f"{item_id}{ext}")
                        if os.path.exists(test_path):
                            modified_path = test_path
                            break
                    
                    # Remove modified poster if it exists
                    if modified_path and os.path.exists(modified_path):
                        logger.info(f"Removing modified poster: {modified_path}")
                        os.remove(modified_path)
                        logger.info(f"Successfully removed modified poster")
                    
                    # Upload original poster back to Jellyfin
                    try:
                        from aphrodite_helpers.poster_uploader import PosterUploader
                        logger.info(f"Uploading original poster back to Jellyfin: {original_path}")
                        uploader = PosterUploader(url, api_key, user_id)
                        upload_success = uploader.upload_poster(item_id, original_path, max_retries=3)
                        logger.info(f"Original poster upload result: {upload_success}")
                    except Exception as upload_error:
                        logger.error(f"Failed to upload original poster: {upload_error}")
                        upload_success = False
                    
                    # Remove metadata tag
                    tagging_settings = get_tagging_settings()
                    tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
                    logger.info(f"Attempting to remove metadata tag: {tag_name}")
                    tagger = MetadataTagger(url, api_key, user_id)
                    tag_removed = tagger.remove_aphrodite_tag(item_id, tag_name)
                    logger.info(f"Tag removal result: {tag_removed}")
                    
                    # Update job status
                    result = {
                        'success': True,
                        'message': 'Successfully reverted to original poster',
                        'item_id': item_id,
                        'tag_removed': tag_removed,
                        'poster_uploaded': upload_success
                    }
                    
                    JobService.update_job(job_id, {
                        'status': 'success',
                        'end_time': time.time(),
                        'result': result
                    })
                    
                    logger.info(f"Successfully reverted item {item_id} to original poster")
                    
                except Exception as e:
                    logger.error(f"Error reverting item {item_id}: {str(e)}")
                    JobService.update_job(job_id, {
                        'status': 'failed',
                        'end_time': time.time(),
                        'result': {
                            'success': False,
                            'error': str(e),
                            'item_id': item_id
                        }
                    })
            
            # Start revert in background thread
            thread = threading.Thread(target=run_revert)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Revert process started for item {item_id}',
                'jobId': job_id
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error starting revert process: {str(e)}'
            }), 500

    @bp.route('/item/<item_id>/poster-sources', methods=['GET'])
    def get_external_poster_sources(item_id):
        """Get poster options from external sources (TMDB, OMDB)"""
        try:
            from app.services.external_poster_service import ExternalPosterService
            poster_service = ExternalPosterService()
            poster_sources = poster_service.get_poster_sources(item_id)
            
            return jsonify({
                'success': True,
                'sources': poster_sources,
                'total': len(poster_sources)
            })
            
        except ImportError as e:
            logger.error(f"Import error in get_external_poster_sources: {e}")
            return jsonify({
                'success': False,
                'message': f'Import error: {str(e)}',
                'error_type': 'ImportError'
            }), 500
        except Exception as e:
            logger.error(f"General error in get_external_poster_sources: {e}")
            return jsonify({
                'success': False,
                'message': f'Error fetching poster sources: {str(e)}',
                'error_type': type(e).__name__
            }), 500

    @bp.route('/item/<item_id>/replace-poster', methods=['POST'])
    def replace_with_external_poster(item_id):
        """Replace current poster with external source"""
        try:
            from app.services.poster_replacement_service import PosterReplacementService
            
            # Get request data
            data = request.get_json() or {}
            poster_data = data.get('poster_data')
            selected_badges = data.get('badges', [])
            
            if not poster_data:
                return jsonify({
                    'success': False,
                    'message': 'Poster data is required'
                }), 400
            
            # Create service instance and validate
            replacement_service = PosterReplacementService()
            if not replacement_service.validate_poster_data(poster_data):
                return jsonify({
                    'success': False,
                    'message': 'Invalid poster data provided'
                }), 400
            
            # Start replacement process
            job_id = replacement_service.replace_poster_async(
                item_id, 
                poster_data, 
                selected_badges
            )
            
            poster_source = poster_data.get('source', 'External')
            badge_list = ', '.join(selected_badges) if selected_badges else 'none'
            
            return jsonify({
                'success': True,
                'message': f'Poster replacement started from {poster_source} with badges: {badge_list}',
                'jobId': job_id
            })
            
        except ImportError as e:
            logger.error(f"Import error in replace_with_external_poster: {e}")
            return jsonify({
                'success': False,
                'message': f'Import error: {str(e)}',
                'error_type': 'ImportError'
            }), 500
        except Exception as e:
            logger.error(f"General error in replace_with_external_poster: {e}")
            return jsonify({
                'success': False,
                'message': f'Error starting poster replacement: {str(e)}',
                'error_type': type(e).__name__
            }), 500

    @bp.route('/item/<item_id>/upload-custom', methods=['POST'])
    def upload_custom_poster(item_id):
        """Upload a custom poster for an item"""
        try:
            # Check if file is present
            if 'poster' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No poster file provided'
                }), 400
            
            file = request.files['poster']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            # Check file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }), 400
            
            # Always set apply_badges to false for custom uploads
            apply_badges = False
            
            # Import and create service
            from app.services.custom_poster_service import CustomPosterService
            poster_service = CustomPosterService()
            
            # Read file data
            file_data = file.read()
            
            # Start upload process
            job_id = poster_service.upload_custom_poster_async(
                item_id, 
                file_data, 
                apply_badges
            )
            
            return jsonify({
                'success': True,
                'message': f'Custom poster upload started (no badges applied)',
                'jobId': job_id
            })
            
        except Exception as e:
            logger.error(f"Error in upload_custom_poster: {e}")
            return jsonify({
                'success': False,
                'message': f'Error uploading custom poster: {str(e)}'
            }), 500
