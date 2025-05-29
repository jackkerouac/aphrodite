from flask import Blueprint, jsonify, request
import subprocess
import uuid
import time
import os
import threading
import shutil
from pathlib import Path
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

# Clean up poster directories route
@bp.route('/cleanup', methods=['POST'])
def cleanup_posters():
    """Clean up poster directories by removing files"""
    print("Cleanup posters endpoint called!")
    
    # Get the request data
    data = request.get_json() or {}
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job_details = {
        'id': job_id,
        'type': 'cleanup',
        'command': 'cleanup_posters',
        'options': data,
        'status': 'queued',
        'start_time': time.time(),
        'end_time': None,
        'result': None
    }
    
    JobService.create_job(job_details)
    
    # Define function to clean up directories
    def cleanup_process():
        try:
            # Get poster directories (Docker-aware path detection)
            base_dir = Path('/app/posters') if os.path.exists('/app') else Path('posters')
            
            cleaned_count = 0
            errors = []
            
            # Check if base directory exists
            if not base_dir.exists():
                raise Exception(f"Posters directory not found: {base_dir}")
            
            # Clean directories based on options
            dirs_to_clean = []
            if not data.get('skipModified', False):
                dirs_to_clean.append(('modified', base_dir / 'modified'))
            if not data.get('skipWorking', False):
                dirs_to_clean.append(('working', base_dir / 'working'))
            if not data.get('skipOriginal', False):
                dirs_to_clean.append(('original', base_dir / 'original'))
            
            for dir_name, dir_path in dirs_to_clean:
                if dir_path.exists():
                    try:
                        for file_path in dir_path.glob('*'):
                            if file_path.is_file():
                                file_path.unlink()
                                cleaned_count += 1
                                print(f"Deleted: {file_path}")
                        print(f"Cleaned {dir_name} directory")
                    except Exception as e:
                        error_msg = f"Failed to clean {dir_name} directory: {str(e)}"
                        errors.append(error_msg)
                        print(error_msg)
                else:
                    print(f"Directory {dir_name} does not exist: {dir_path}")
            
            # Update job status
            result = {
                'success': len(errors) == 0,
                'cleaned_count': cleaned_count,
                'directories_processed': len(dirs_to_clean),
                'errors': errors
            }
            
            status = 'success' if len(errors) == 0 else ('partial' if cleaned_count > 0 else 'failed')
            
            JobService.update_job(job_id, {
                'status': status,
                'end_time': time.time(),
                'result': result
            })
            
            print(f"Cleanup completed. Cleaned: {cleaned_count}, Errors: {len(errors)}")
            
        except Exception as e:
            print(f"Error during cleanup process: {str(e)}")
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e),
                    'cleaned_count': 0,
                    'directories_processed': 0,
                    'errors': [str(e)]
                }
            })
    
    # Start cleanup process in background thread
    thread = threading.Thread(target=cleanup_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Cleanup process started',
        'jobId': job_id
    })

# Restore original posters route
@bp.route('/restore-originals', methods=['POST'])
def restore_originals():
    """Restore all modified posters to their original versions"""
    print("Restore originals endpoint called!")
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job_details = {
        'id': job_id,
        'type': 'restore',
        'command': 'restore_originals',
        'options': {},
        'status': 'queued',
        'start_time': time.time(),
        'end_time': None,
        'result': None
    }
    
    JobService.create_job(job_details)
    
    # Define function to restore originals
    def restore_process():
        try:
            # Get poster directories (Docker-aware path detection)
            original_dir = Path('/app/posters/original') if os.path.exists('/app') else Path('posters/original')
            modified_dir = Path('/app/posters/modified') if os.path.exists('/app') else Path('posters/modified')
            
            restored_count = 0
            errors = []
            
            # Check if directories exist
            if not original_dir.exists():
                raise Exception(f"Original posters directory not found: {original_dir}")
            
            if not modified_dir.exists():
                raise Exception(f"Modified posters directory not found: {modified_dir}")
            
            # Iterate through original posters
            for original_file in original_dir.glob('*'):
                if original_file.is_file():
                    modified_file = modified_dir / original_file.name
                    
                    # If a modified version exists, replace it with the original
                    if modified_file.exists():
                        try:
                            shutil.copy2(original_file, modified_file)
                            restored_count += 1
                            print(f"Restored: {original_file.name}")
                        except Exception as e:
                            error_msg = f"Failed to restore {original_file.name}: {str(e)}"
                            errors.append(error_msg)
                            print(error_msg)
            
            # Update job status
            result = {
                'success': len(errors) == 0,
                'restored_count': restored_count,
                'total_processed': restored_count + len(errors),
                'errors': errors
            }
            
            status = 'success' if len(errors) == 0 else ('partial' if restored_count > 0 else 'failed')
            
            JobService.update_job(job_id, {
                'status': status,
                'end_time': time.time(),
                'result': result
            })
            
            print(f"Restore completed. Restored: {restored_count}, Errors: {len(errors)}")
            
        except Exception as e:
            print(f"Error during restore process: {str(e)}")
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e),
                    'restored_count': 0,
                    'total_processed': 0,
                    'errors': [str(e)]
                }
            })
    
    # Start restore process in background thread
    thread = threading.Thread(target=restore_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Restore process started',
        'jobId': job_id
    })
