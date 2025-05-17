import os
import json
import uuid
import time
from datetime import datetime
import threading
import subprocess
from app.services.job_history import create_job, update_job_status

WORKFLOW_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'workflow_queue.json')

def ensure_workflow_file():
    """Ensure that the workflow queue file exists"""
    if not os.path.exists(WORKFLOW_FILE):
        with open(WORKFLOW_FILE, 'w') as f:
            json.dump({
                "active_workflows": {},
                "queue": [],
                "completed": []
            }, f)

def get_workflow_status():
    """Get the current status of all workflows"""
    ensure_workflow_file()
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    return data

def add_workflow(workflow_type, options):
    """Add a new workflow to the queue"""
    ensure_workflow_file()
    
    workflow_id = str(uuid.uuid4())
    
    new_workflow = {
        'id': workflow_id,
        'type': workflow_type,
        'status': 'Queued',
        'options': options,
        'created_at': datetime.now().isoformat(),
        'queue_position': 0  # Will be updated when added to queue
    }
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Add to queue
    new_workflow['queue_position'] = len(data['queue']) + 1
    data['queue'].append(new_workflow)
    
    with open(WORKFLOW_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Start processing the queue if not already running
    check_and_process_queue()
    
    return workflow_id

def update_workflow_status(workflow_id, status, result=None):
    """Update workflow status and optionally add result data"""
    ensure_workflow_file()
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Check active workflows
    updated = False
    if workflow_id in data['active_workflows']:
        workflow = data['active_workflows'][workflow_id]
        workflow['status'] = status
        
        if status in ['Success', 'Failed', 'Completed']:
            workflow['end_time'] = datetime.now().isoformat()
            
            # Move from active to completed
            data['completed'].append(workflow)
            del data['active_workflows'][workflow_id]
        
        if result:
            if 'result' not in workflow:
                workflow['result'] = {}
            workflow['result'].update(result)
        
        updated = True
    
    # Check queue
    if not updated:
        for i, workflow in enumerate(data['queue']):
            if workflow['id'] == workflow_id:
                workflow['status'] = status
                
                if status in ['Success', 'Failed', 'Completed']:
                    workflow['end_time'] = datetime.now().isoformat()
                    
                    # Move from queue to completed
                    data['completed'].append(workflow)
                    data['queue'].pop(i)
                    
                    # Update queue positions
                    for j, queued in enumerate(data['queue']):
                        queued['queue_position'] = j + 1
                
                if result:
                    if 'result' not in workflow:
                        workflow['result'] = {}
                    workflow['result'].update(result)
                
                updated = True
                break
    
    if updated:
        with open(WORKFLOW_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    return updated

def process_library_item(workflow_id, library_id, options):
    """Process a single library as part of a workflow"""
    job_id = None
    try:
        print(f"Processing library {library_id} for workflow {workflow_id}")
        
        # Create a job for this library processing
        job_id = create_job('library', {
            'libraryId': library_id,
            'workflow_id': workflow_id,
            'badgeTypes': options.get('badgeTypes', []),
            'limit': options.get('limit'),
            'skipUpload': options.get('skipUpload', False)
        })
        
        # Get the root directory - this should be the directory that contains aphrodite.py
        # We're in app/services, so we need to go up multiple levels
        app_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        root_dir = os.path.abspath(os.path.join(app_dir, '..'))
        script_path = os.path.join(root_dir, 'aphrodite.py')
        
        print(f"Using script at: {script_path}")
        if not os.path.exists(script_path):
            error_msg = f"Script file not found at {script_path}"
            print(error_msg)
            update_job_status(job_id, 'Failed', {'error': error_msg})
            return {
                'libraryId': library_id,
                'success': False,
                'error': error_msg,
                'job_id': job_id
            }
        
        # Build the command
        cmd = ['python', script_path, 'library', library_id]
        
        # Add limit if provided
        if options.get('limit'):
            cmd.extend(['--limit', str(options.get('limit'))])
        
        # Add retries if provided
        if options.get('retries'):
            cmd.extend(['--retries', str(options.get('retries'))])
        
        # Add badge type flags
        all_badge_types = ['audio', 'resolution', 'review']
        for badge_type in all_badge_types:
            if badge_type not in options.get('badgeTypes', []):
                # Note: the script uses --no-reviews (not --no-review)
                flag_name = f"--no-{badge_type}s" if badge_type == 'review' else f"--no-{badge_type}"
                cmd.append(flag_name)
        
        # Add skip upload flag if requested
        if options.get('skipUpload'):
            cmd.append('--no-upload')
        
        # Set environment variables for Unicode
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        print(f"Executing command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            cwd=root_dir,  # Execute in the root directory where aphrodite.py is
            env=env,  # Use the modified environment
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        
        print(f"Command completed with return code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error output: {result.stderr}")
        
        # Update job status
        update_job_status(job_id, 'Success' if result.returncode == 0 else 'Failed', {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returnCode': result.returncode
        })
        
        return {
            'libraryId': library_id,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returnCode': result.returncode,
            'job_id': job_id
        }
        
    except Exception as e:
        # Log the error
        error_message = f"Exception processing library {library_id}: {str(e)}"
        print(error_message)
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        
        # Update job status if job was created
        if job_id:
            update_job_status(job_id, 'Failed', {
                'error': error_message,
                'traceback': traceback_str
            })
        
        return {
            'libraryId': library_id,
            'success': False,
            'error': error_message,
            'traceback': traceback_str
        }

def process_workflow(workflow_id):
    """Process a workflow in a separate thread"""
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Find the workflow
    workflow = None
    for queued in data['queue']:
        if queued['id'] == workflow_id:
            workflow = queued
            break
    
    if not workflow:
        return False
    
    # Move from queue to active
    data['queue'] = [w for w in data['queue'] if w['id'] != workflow_id]
    workflow['status'] = 'Running'
    workflow['start_time'] = datetime.now().isoformat()
    data['active_workflows'][workflow_id] = workflow
    
    # Update queue positions
    for i, queued in enumerate(data['queue']):
        queued['queue_position'] = i + 1
    
    with open(WORKFLOW_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Start processing in a separate thread
    def process_thread():
        try:
            print(f"Starting workflow {workflow_id} of type {workflow['type']}")
            
            if workflow['type'] == 'library_batch':
                results = []
                
                for library_id in workflow['options'].get('libraryIds', []):
                    print(f"Processing library {library_id} in workflow {workflow_id}")
                    library_result = process_library_item(workflow_id, library_id, workflow['options'])
                    results.append(library_result)
                    print(f"Library {library_id} processing completed: success={library_result['success']}")
                
                # Check overall success
                all_success = all(result.get('success', False) for result in results)
                
                # Update workflow status
                print(f"Workflow {workflow_id} completed with overall success: {all_success}")
                update_workflow_status(workflow_id, 'Success' if all_success else 'Completed', {
                    'results': results,
                    'success': all_success
                })
            else:
                # Unknown workflow type
                error_msg = f"Unknown workflow type: {workflow['type']}"
                print(error_msg)
                update_workflow_status(workflow_id, 'Failed', {
                    'error': error_msg
                })
            
        except Exception as e:
            # Log the error
            error_message = f"Exception in workflow {workflow_id}: {str(e)}"
            print(error_message)
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Traceback: {traceback_str}")
            
            # Update workflow status
            update_workflow_status(workflow_id, 'Failed', {
                'error': error_message,
                'traceback': traceback_str
            })
        
        # Process next item in queue
        print(f"Checking for next workflow after completing {workflow_id}")
        check_and_process_queue()
    
    t = threading.Thread(target=process_thread)
    t.daemon = True
    t.start()
    
    return True

def check_and_process_queue():
    """Check the queue and process the next workflow if available"""
    # Add a little delay to ensure file operations are complete
    time.sleep(1)
    
    try:
        with open(WORKFLOW_FILE, 'r') as f:
            data = json.load(f)
        
        # If there are active workflows, don't start new ones
        if data['active_workflows']:
            return False
        
        # If there are queued workflows, process the first one
        if data['queue']:
            next_workflow = data['queue'][0]
            return process_workflow(next_workflow['id'])
        
        return False
    except Exception as e:
        print(f"Error checking workflow queue: {str(e)}")
        return False

def delete_workflow(workflow_id):
    """Delete a workflow from any status (queue, active, completed)"""
    ensure_workflow_file()
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Check and remove from active workflows
    if workflow_id in data['active_workflows']:
        del data['active_workflows'][workflow_id]
        with open(WORKFLOW_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    
    # Check and remove from queue
    queue_updated = False
    for i, workflow in enumerate(data['queue']):
        if workflow['id'] == workflow_id:
            data['queue'].pop(i)
            queue_updated = True
            
            # Update queue positions
            for j, queued in enumerate(data['queue']):
                queued['queue_position'] = j + 1
            
            break
    
    # Check and remove from completed
    completed_updated = False
    data['completed'] = [w for w in data['completed'] if w['id'] != workflow_id]
    completed_updated = True
    
    # If anything was updated, save the file
    if queue_updated or completed_updated:
        with open(WORKFLOW_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    
    return False


def get_workflow(workflow_id):
    """Get a specific workflow by ID"""
    ensure_workflow_file()
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Check active workflows
    if workflow_id in data['active_workflows']:
        return data['active_workflows'][workflow_id]
    
    # Check queue
    for workflow in data['queue']:
        if workflow['id'] == workflow_id:
            return workflow
    
    # Check completed
    for workflow in data['completed']:
        if workflow['id'] == workflow_id:
            return workflow
    
    return None

def clear_completed_workflows(max_to_keep=20):
    """Clear completed workflows, keeping only the most recent ones"""
    ensure_workflow_file()
    
    with open(WORKFLOW_FILE, 'r') as f:
        data = json.load(f)
    
    # Keep only the most recent completed workflows
    data['completed'] = sorted(
        data['completed'], 
        key=lambda x: x.get('end_time', ''), 
        reverse=True
    )[:max_to_keep]
    
    with open(WORKFLOW_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return True
