from flask import Blueprint, jsonify, request
import subprocess
import uuid
import time
import os
import threading
from app.services.job import JobService

# Create blueprint for process endpoints
bp = Blueprint('process', __name__, url_prefix='/api/process')

# Process a single item route
@bp.route('/item', methods=['POST'])
def process_item():
    """Process a single Jellyfin item by ID"""
    print("Process item endpoint called!")
    
    # Get the request data
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    print(f"Received data: {data}")
    
    # Basic validation
    if not data.get('itemId'):
        return jsonify({
            'success': False,
            'message': 'Item ID is required'
        }), 400
    
    if not data.get('badgeTypes') or len(data.get('badgeTypes')) == 0:
        return jsonify({
            'success': False,
            'message': 'At least one badge type must be selected'
        }), 400
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Build the command
    cmd = ['python', os.path.join(os.getcwd(), 'aphrodite.py'), '--itemid', data['itemId']]
    
    # Add badge type flags (if a badge type is not in badgeTypes, add --no-{badge_type})
    all_badge_types = ['audio', 'resolution', 'review']
    for badge_type in all_badge_types:
        if badge_type not in data.get('badgeTypes', []):
            cmd.append(f'--no-{badge_type}')
    
    # Add skip upload flag if requested
    if data.get('skipUpload'):
        cmd.append('--skip-upload')
    
    print(f"Command: {' '.join(cmd)}")
    
    # Create job record
    job_details = {
        'id': job_id,
        'type': 'item',
        'command': ' '.join(cmd),
        'options': data,
        'status': 'queued',
        'start_time': time.time(),
        'end_time': None,
        'result': None
    }
    
    JobService.create_job(job_details)
    
    # Define function to run the script
    def run_script():
        try:
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()  # Use current working directory
            )
            
            stdout, stderr = process.communicate()
            
            # Update job status
            success = process.returncode == 0
            status = 'success' if success else 'failed'
            
            result = {
                'success': success,
                'stdout': stdout,
                'stderr': stderr,
                'returncode': process.returncode
            }
            
            JobService.update_job(job_id, {
                'status': status,
                'end_time': time.time(),
                'result': result
            })
            
            print(f"Script completed with status: {status}")
            
        except Exception as e:
            print(f"Error running script: {str(e)}")
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e)
                }
            })
    
    # Start script in background thread
    thread = threading.Thread(target=run_script)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f"Processing started for item {data['itemId']}",
        'jobId': job_id
    })

# Process a library route (placeholder)
@bp.route('/library', methods=['POST'])
def process_library():
    """Process a Jellyfin library"""
    return jsonify({
        'success': False,
        'message': 'Library processing not yet implemented'
    }), 501
