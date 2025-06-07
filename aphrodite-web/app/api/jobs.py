from flask import Blueprint, jsonify, request
import json
import os
import time
from app.services.job import JobService
from app.services.job_history import get_job_history, get_job_by_id, get_job_items, delete_job

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.route('/', methods=['GET'])
def get_all_jobs():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    job_type = request.args.get('type')
    
    # Try to get jobs from the database first (newer approach)
    limit = per_page
    offset = (page - 1) * per_page
    jobs = JobService.get_all_jobs(limit, offset)
    
    if jobs:
        total_count = JobService.get_job_count()
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        })
    
    # Fall back to job history file if no jobs in database
    job_history = get_job_history(page, per_page, job_type)
    
    return jsonify({
        'success': True,
        'jobs': job_history['jobs'],
        'total': job_history['total'],
        'page': job_history['page'],
        'per_page': job_history['per_page'],
        'total_pages': job_history['total_pages']
    })

@bp.route('/<id>', methods=['GET'])
def get_job(id):
    # Try to get job from database first
    job = JobService.get_job(id)
    
    if job:
        return jsonify({
            'success': True,
            'job': job
        })
    
    # Fall back to history file
    job = get_job_by_id(id)
    
    if not job:
        return jsonify({
            'success': False,
            'message': f'Job {id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'job': job
    })

@bp.route('/<id>', methods=['DELETE'])
def delete_job_by_id(id):
    # Try to delete from database first
    deleted_from_db = JobService.delete_job(id)
    
    # Always try to delete from history file too (in case it exists in both places)
    deleted_from_history = delete_job(id)
    
    if not deleted_from_db and not deleted_from_history:
        return jsonify({
            'success': False,
            'message': f'Job {id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'message': f'Job {id} deleted successfully'
    })

@bp.route('/<id>/items', methods=['GET'])
def get_job_items_endpoint(id):
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get items for the job
    items_data = get_job_items(id, page, per_page)
    
    return jsonify({
        'success': True,
        'items': items_data['items'],
        'total': items_data['total'],
        'page': items_data['page'],
        'per_page': items_data['per_page'],
        'total_pages': items_data['total_pages']
    })

import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

@bp.route('/active-badge-jobs', methods=['GET'])
def get_active_badge_jobs():
    """Get active badge processing jobs from batch_jobs.json"""
    try:
        batch_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'batch_jobs.json')
        
        if not os.path.exists(batch_file):
            return jsonify({
                'success': True,
                'active_batches': [],
                'total_active_jobs': 0
            })
        
        with open(batch_file, 'r') as f:
            all_batches = json.load(f)
        
        logger.info(f"DEBUG: Found {len(all_batches)} total batches in batch_jobs.json")
        
        active_batches = []
        total_active_jobs = 0
        
        for batch_id, batch_info in all_batches.items():
            # Check if any jobs in this batch are still active
            active_jobs_in_batch = 0
            completed_jobs_in_batch = 0
            failed_jobs_in_batch = 0
            
            logger.info(f"DEBUG: Checking batch {batch_id} with {len(batch_info.get('jobs', []))} jobs")
            
            for job_info in batch_info.get('jobs', []):
                job_id = job_info['job_id']
                job_data = JobService.get_job(job_id)
                
                if job_data:
                    status = job_data.get('status', 'unknown')
                    logger.info(f"DEBUG: Job {job_id[:8]}... status: {status}")
                    
                    if status in ['queued', 'running']:
                        active_jobs_in_batch += 1
                    elif status == 'success':
                        completed_jobs_in_batch += 1
                    elif status == 'failed':
                        failed_jobs_in_batch += 1
                else:
                    # Job not found in database - check age of batch
                    batch_age_hours = (time.time() - batch_info.get('created_at', 0)) / 3600
                    logger.info(f"DEBUG: Job {job_id[:8]}... not found in DB, batch age: {batch_age_hours:.1f}h")
                    
                    # If batch is recent (< 2 hours), consider jobs as potentially running
                    # If batch is old (> 2 hours), consider jobs as completed
                    if batch_age_hours < 2.0:
                        active_jobs_in_batch += 1  # Assume still running
                    else:
                        completed_jobs_in_batch += 1  # Assume completed
            
            total_jobs_in_batch = len(batch_info.get('jobs', []))
            batch_age_hours = (time.time() - batch_info.get('created_at', 0)) / 3600
            
            logger.info(f"DEBUG: Batch summary - Active: {active_jobs_in_batch}, Completed: {completed_jobs_in_batch}, Failed: {failed_jobs_in_batch}, Age: {batch_age_hours:.1f}h")
            
            # Consider batch active if:
            # 1. Has active jobs, OR
            # 2. Is recent (< 2 hours) and not all jobs are accounted for, OR 
            # 3. Is recent (< 1 hour) to show completed batches for user convenience
            is_recent = batch_age_hours < 2.0
            is_very_recent = batch_age_hours < 1.0  # Show recent batches for 1 hour
            all_jobs_accounted = (active_jobs_in_batch + completed_jobs_in_batch + failed_jobs_in_batch) >= total_jobs_in_batch
            
            should_show_batch = (
                active_jobs_in_batch > 0 or
                (is_recent and not all_jobs_accounted) or
                is_very_recent  # Show recent batches regardless of completion status
            )
            
            if should_show_batch:
                is_complete = (completed_jobs_in_batch + failed_jobs_in_batch >= total_jobs_in_batch) and active_jobs_in_batch == 0
                
                active_batches.append({
                    'batch_id': batch_id,
                    'total_jobs': total_jobs_in_batch,
                    'active_jobs': active_jobs_in_batch,
                    'completed_jobs': completed_jobs_in_batch,
                    'failed_jobs': failed_jobs_in_batch,
                    'selected_badges': batch_info.get('selected_badges', []),
                    'created_at': batch_info.get('created_at'),
                    'batch_age_hours': batch_age_hours,
                    'is_complete': is_complete
                })
                total_active_jobs += active_jobs_in_batch
                
                logger.info(f"DEBUG: Including batch {batch_id[:8]}... (complete: {is_complete})")
            else:
                logger.info(f"DEBUG: Excluding batch {batch_id[:8]}... (too old or complete)")
        
        return jsonify({
            'success': True,
            'active_batches': active_batches,
            'total_active_jobs': total_active_jobs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting active badge jobs: {str(e)}',
            'active_batches': [],
            'total_active_jobs': 0
        }), 500

@bp.route('/clear-completed-batches', methods=['POST'])
def clear_completed_batches():
    """Clear all completed badge processing batches"""
    try:
        batch_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'batch_jobs.json')
        
        if not os.path.exists(batch_file):
            return jsonify({
                'success': True,
                'message': 'No batches found to clear',
                'cleared_count': 0
            })
        
        with open(batch_file, 'r') as f:
            all_batches = json.load(f)
        
        cleared_count = 0
        remaining_batches = {}
        
        for batch_id, batch_info in all_batches.items():
            # Check if this batch has any active jobs
            has_active_jobs = False
            
            for job_info in batch_info.get('jobs', []):
                job_data = JobService.get_job(job_info['job_id'])
                if job_data and job_data.get('status') in ['queued', 'running']:
                    has_active_jobs = True
                    break
            
            # Keep batches that have active jobs, remove completed ones
            if has_active_jobs:
                remaining_batches[batch_id] = batch_info
            else:
                cleared_count += 1
                logger.info(f"Cleared completed batch {batch_id[:8]}...")
        
        # Save the updated batches file
        with open(batch_file, 'w') as f:
            json.dump(remaining_batches, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} completed batch{"es" if cleared_count != 1 else ""}',
            'cleared_count': cleared_count,
            'remaining_count': len(remaining_batches)
        })
        
    except Exception as e:
        logger.error(f"Error clearing completed batches: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/debug-badge-jobs', methods=['GET'])
def debug_badge_jobs():
    """Debug endpoint to see raw batch job data"""
    try:
        batch_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'batch_jobs.json')
        
        if not os.path.exists(batch_file):
            return jsonify({
                'success': False,
                'message': 'batch_jobs.json not found',
                'file_path': batch_file
            })
        
        with open(batch_file, 'r') as f:
            all_batches = json.load(f)
        
        debug_info = {
            'batch_file_path': batch_file,
            'total_batches': len(all_batches),
            'batches': {}
        }
        
        for batch_id, batch_info in all_batches.items():
            batch_age_hours = (time.time() - batch_info.get('created_at', 0)) / 3600
            
            job_details = []
            for job_info in batch_info.get('jobs', []):
                job_id = job_info['job_id']
                job_data = JobService.get_job(job_id)
                
                job_details.append({
                    'job_id': job_id,
                    'item_name': job_info.get('item_name', 'Unknown'),
                    'found_in_db': job_data is not None,
                    'status': job_data.get('status') if job_data else 'not_found'
                })
            
            debug_info['batches'][batch_id] = {
                'created_at': batch_info.get('created_at'),
                'age_hours': round(batch_age_hours, 2),
                'total_jobs': len(batch_info.get('jobs', [])),
                'selected_badges': batch_info.get('selected_badges', []),
                'jobs': job_details
            }
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
