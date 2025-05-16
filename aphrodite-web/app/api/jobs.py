from flask import Blueprint, jsonify, request
from app.services.job import JobService
from app.services.job_history import get_job_history, get_job_by_id, get_job_items, delete_job

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.route('/', methods=['GET'])
def get_all_jobs():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    job_type = request.args.get('type')
    
    # Try to get jobs from the job history file first (newer approach)
    job_history = get_job_history(page, per_page, job_type)
    
    if job_history['total'] > 0:
        return jsonify({
            'success': True,
            'jobs': job_history['jobs'],
            'total': job_history['total'],
            'page': job_history['page'],
            'per_page': job_history['per_page'],
            'total_pages': job_history['total_pages']
        })
    
    # Fall back to database if no jobs in history file
    limit = per_page
    offset = (page - 1) * per_page
    jobs = JobService.get_all_jobs(limit, offset)
    
    return jsonify({
        'success': True,
        'jobs': jobs,
        'total': len(jobs),  # This is not accurate for total count, but it's a fallback
        'page': page,
        'per_page': per_page,
        'total_pages': 1 if jobs else 0
    })

@bp.route('/<id>', methods=['GET'])
def get_job(id):
    # Try to get job from history file first
    job = get_job_by_id(id)
    
    if job:
        return jsonify({
            'success': True,
            'job': job
        })
    
    # Fall back to database
    job = JobService.get_job(id)
    
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
    # Try to delete from history file first
    deleted_from_history = delete_job(id)
    
    # Always try to delete from database too (in case it exists in both places)
    deleted_from_db = JobService.delete_job(id)
    
    if not deleted_from_history and not deleted_from_db:
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
