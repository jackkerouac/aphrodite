from flask import Blueprint, jsonify, request
from app.services.job import JobService

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.route('/', methods=['GET'])
def get_all_jobs():
    # Get pagination parameters
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get jobs from database
    jobs = JobService.get_all_jobs(limit, offset)
    
    return jsonify({
        'success': True,
        'jobs': jobs
    })

@bp.route('/<id>', methods=['GET'])
def get_job(id):
    # Get job from database
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
def delete_job(id):
    # Delete job from database
    deleted = JobService.delete_job(id)
    
    if not deleted:
        return jsonify({
            'success': False,
            'message': f'Job {id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'message': f'Job {id} deleted successfully'
    })
