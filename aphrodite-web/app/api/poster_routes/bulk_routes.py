from flask import jsonify, request
import sys
import os
import json
import uuid
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings
from app.services.job import JobService
from app.services.settings_service import SettingsService
from .utils import get_jellyfin_item_details, get_enhanced_poster_status, run_aphrodite_command
from aphrodite_helpers.metadata_tagger import MetadataTagger

def register_bulk_routes(bp):
    """Register bulk processing routes"""
    
    @bp.route('/bulk/reprocess', methods=['POST'])
    def bulk_reprocess_posters():
        """Process multiple posters with selected badge types"""
        try:
            # Get request data
            data = request.get_json() or {}
            item_ids = data.get('item_ids', [])
            selected_badges = data.get('badge_types', ['audio', 'resolution', 'review', 'awards'])
            
            if not item_ids:
                return jsonify({
                    'success': False,
                    'message': 'No items provided for processing'
                }), 400
            
            # Validate badge types
            valid_badges = ['audio', 'resolution', 'review', 'awards']
            selected_badges = [badge for badge in selected_badges if badge in valid_badges]
            
            if not selected_badges:
                return jsonify({
                    'success': False,
                    'message': 'At least one badge type must be selected'
                }), 400
            
            # Load Jellyfin settings with database priority
            url, api_key, user_id = None, None, None
            
            try:
                settings_service = SettingsService()
                jellyfin_keys = settings_service.get_api_keys('Jellyfin')
                
                if jellyfin_keys and len(jellyfin_keys) > 0:
                    jf = jellyfin_keys[0]
                    url, api_key, user_id = jf.get('url'), jf.get('api_key'), jf.get('user_id')
                    logger.info(f'Loaded Jellyfin settings from database for bulk processing')
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
            
            # Create batch ID
            batch_id = str(uuid.uuid4())
            
            # Filter items - only process items without existing badges
            valid_items = []
            skipped_items = []
            
            for item_id in item_ids:
                try:
                    item_info = get_jellyfin_item_details(url, api_key, user_id, item_id)
                    poster_status = get_enhanced_poster_status(item_id, item_info.get('tags', []))
                    
                    if poster_status.get('has_badges', False):
                        skipped_items.append({
                            'item_id': item_id,
                            'item_name': item_info.get('name', 'Unknown'),
                            'reason': 'Already has badges'
                        })
                    else:
                        valid_items.append({
                            'item_id': item_id,
                            'item_name': item_info.get('name', 'Unknown')
                        })
                except Exception as e:
                    logger.error(f"Error checking item {item_id}: {e}")
                    skipped_items.append({
                        'item_id': item_id,
                        'item_name': 'Unknown',
                        'reason': f'Error: {str(e)}'
                    })
            
            # Create individual jobs for valid items
            jobs = []
            for item in valid_items:
                job_id = str(uuid.uuid4())
                job_details = {
                    'id': job_id,
                    'type': 'bulk_reprocess',
                    'command': f'python aphrodite.py item {item["item_id"]}',
                    'options': {
                        'item_id': item['item_id'],
                        'item_name': item['item_name'],
                        'badges': selected_badges,
                        'batch_id': batch_id
                    },
                    'status': 'queued',
                    'start_time': time.time(),
                    'end_time': None,
                    'result': None
                }
                
                JobService.create_job(job_details)
                jobs.append({
                    'job_id': job_id,
                    'item_id': item['item_id'],
                    'item_name': item['item_name']
                })
            
            # Store batch information
            batch_info = {
                'batch_id': batch_id,
                'total_items': len(item_ids),
                'valid_items': len(valid_items),
                'skipped_items': len(skipped_items),
                'selected_badges': selected_badges,
                'jobs': jobs,
                'skipped': skipped_items,
                'created_at': time.time()
            }
            
            # Store batch info in a simple file-based approach
            batch_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'batch_jobs.json')
            try:
                if os.path.exists(batch_file):
                    with open(batch_file, 'r') as f:
                        all_batches = json.load(f)
                else:
                    all_batches = {}
                
                all_batches[batch_id] = batch_info
                
                with open(batch_file, 'w') as f:
                    json.dump(all_batches, f, indent=2)
            except Exception as e:
                logger.error(f"Error storing batch info: {e}")
            
            # Start processing jobs in background
            def process_batch():
                for job_info in jobs:
                    try:
                        # Start individual job processing
                        process_single_item_job(job_info['job_id'], job_info['item_id'], selected_badges)
                    except Exception as e:
                        logger.error(f"Error starting job {job_info['job_id']}: {e}")
                        JobService.update_job(job_info['job_id'], {
                            'status': 'failed',
                            'end_time': time.time(),
                            'result': {
                                'success': False,
                                'error': f'Failed to start job: {str(e)}',
                                'item_id': job_info['item_id']
                            }
                        })
            
            # Start batch processing in background
            thread = threading.Thread(target=process_batch)
            thread.daemon = True
            thread.start()
            
            badge_list = ', '.join(selected_badges)
            return jsonify({
                'success': True,
                'message': f'Batch processing started for {len(valid_items)} items with badges: {badge_list}',
                'batch_id': batch_id,
                'total_items': len(item_ids),
                'processing_items': len(valid_items),
                'skipped_items': len(skipped_items),
                'skipped_details': skipped_items
            })
            
        except Exception as e:
            logger.error(f"Error in bulk_reprocess_posters: {e}")
            return jsonify({
                'success': False,
                'message': f'Error starting bulk processing: {str(e)}'
            }), 500

    @bp.route('/bulk/status/<batch_id>', methods=['GET'])
    def get_bulk_status(batch_id):
        """Get status of a bulk processing batch"""
        try:
            # Load batch info
            batch_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'batch_jobs.json')
            batch_info = None
            
            if os.path.exists(batch_file):
                with open(batch_file, 'r') as f:
                    all_batches = json.load(f)
                    batch_info = all_batches.get(batch_id)
            
            if not batch_info:
                return jsonify({
                    'success': False,
                    'message': 'Batch not found'
                }), 404
            
            # Get job statuses
            job_statuses = []
            completed_count = 0
            
            for job_info in batch_info.get('jobs', []):
                try:
                    job_data = JobService.get_job(job_info['job_id'])
                    if job_data:
                        status = {
                            'job_id': job_info['job_id'],
                            'item_id': job_info['item_id'],
                            'item_name': job_info['item_name'],
                            'status': job_data.get('status', 'unknown')
                        }
                        
                        if job_data.get('status') in ['success', 'failed']:
                            completed_count += 1
                        
                        if job_data.get('status') == 'failed' and job_data.get('result', {}).get('error'):
                            status['error'] = job_data['result']['error']
                        
                        job_statuses.append(status)
                    else:
                        # Job not found, mark as failed
                        job_statuses.append({
                            'job_id': job_info['job_id'],
                            'item_id': job_info['item_id'],
                            'item_name': job_info['item_name'],
                            'status': 'failed',
                            'error': 'Job not found'
                        })
                        completed_count += 1
                except Exception as e:
                    logger.error(f"Error getting job status for {job_info['job_id']}: {e}")
                    job_statuses.append({
                        'job_id': job_info['job_id'],
                        'item_id': job_info['item_id'],
                        'item_name': job_info['item_name'],
                        'status': 'failed',
                        'error': str(e)
                    })
                    completed_count += 1
            
            total_jobs = len(batch_info.get('jobs', []))
            is_complete = completed_count >= total_jobs
            
            return jsonify({
                'success': True,
                'batch_id': batch_id,
                'total': total_jobs,
                'completed': completed_count,
                'is_complete': is_complete,
                'jobs': job_statuses,
                'batch_info': {
                    'selected_badges': batch_info.get('selected_badges', []),
                    'total_items': batch_info.get('total_items', 0),
                    'valid_items': batch_info.get('valid_items', 0),
                    'skipped_items': batch_info.get('skipped_items', 0)
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting bulk status: {e}")
            return jsonify({
                'success': False,
                'message': f'Error getting batch status: {str(e)}'
            }), 500

    @bp.route('/bulk/tags', methods=['POST'])
    def bulk_manage_tags():
        """Add or remove aphrodite-overlay tags from multiple items"""
        try:
            # Get request data
            data = request.get_json() or {}
            item_ids = data.get('item_ids', [])
            action = data.get('action', 'add')  # 'add' or 'remove'
            
            if not item_ids:
                return jsonify({
                    'success': False,
                    'message': 'No items provided for tag management'
                }), 400
            
            if action not in ['add', 'remove']:
                return jsonify({
                    'success': False,
                    'message': 'Action must be "add" or "remove"'
                }), 400
            
            # Load Jellyfin settings
            url, api_key, user_id = None, None, None
            
            try:
                settings_service = SettingsService()
                jellyfin_keys = settings_service.get_api_keys('Jellyfin')
                
                if jellyfin_keys and len(jellyfin_keys) > 0:
                    jf = jellyfin_keys[0]
                    url, api_key, user_id = jf.get('url'), jf.get('api_key'), jf.get('user_id')
                    logger.info(f'Loaded Jellyfin settings from database for tag management')
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
            
            # Initialize metadata tagger
            tagger = MetadataTagger(url, api_key, user_id)
            
            # Process each item
            results = []
            success_count = 0
            
            for item_id in item_ids:
                try:
                    # Get item details for name
                    item_info = get_jellyfin_item_details(url, api_key, user_id, item_id)
                    item_name = item_info.get('name', 'Unknown') if item_info else 'Unknown'
                    
                    if action == 'add':
                        success = tagger.add_aphrodite_tag(item_id)
                        action_text = 'added'
                    else:  # remove
                        success = tagger.remove_aphrodite_tag(item_id)
                        action_text = 'removed'
                    
                    if success:
                        success_count += 1
                        logger.info(f"Successfully {action_text} tag for item {item_id} ({item_name})")
                    
                    results.append({
                        'item_id': item_id,
                        'item_name': item_name,
                        'success': success,
                        'action': action
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing tag {action} for item {item_id}: {e}")
                    results.append({
                        'item_id': item_id,
                        'item_name': 'Unknown',
                        'success': False,
                        'error': str(e),
                        'action': action
                    })
            
            action_text = 'added' if action == 'add' else 'removed'
            return jsonify({
                'success': True,
                'message': f'Tag {action} completed: {success_count}/{len(item_ids)} items processed successfully',
                'action': action,
                'total_items': len(item_ids),
                'successful_items': success_count,
                'failed_items': len(item_ids) - success_count,
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error in bulk_manage_tags: {e}")
            return jsonify({
                'success': False,
                'message': f'Error managing tags: {str(e)}'
            }), 500


def process_single_item_job(job_id, item_id, selected_badges):
    """Process a single item job (used by bulk processing)"""
    def run_job():
        try:
            # Update job status to running
            JobService.update_job(job_id, {'status': 'running'})
            
            # Run the aphrodite command
            success, result = run_aphrodite_command(item_id, selected_badges)
            
            # Update job status
            JobService.update_job(job_id, {
                'status': 'success' if success else 'failed',
                'end_time': time.time(),
                'result': result
            })
            
            if success:
                logger.info(f"Successfully processed bulk job {job_id} for item {item_id}")
            else:
                logger.error(f"Failed to process bulk job {job_id} for item {item_id}")
            
        except Exception as e:
            logger.error(f"Error processing bulk job {job_id}: {str(e)}")
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e),
                    'item_id': item_id
                }
            })
    
    # Start job in background thread
    thread = threading.Thread(target=run_job)
    thread.daemon = True
    thread.start()
