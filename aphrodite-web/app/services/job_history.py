import os
import json
import uuid
from datetime import datetime

JOB_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'job_history.json')

def ensure_job_history_file():
    """Ensure that the job history file exists"""
    if not os.path.exists(JOB_HISTORY_FILE):
        with open(JOB_HISTORY_FILE, 'w') as f:
            json.dump([], f)

def get_job_history(page=1, per_page=20, job_type=None):
    """Get paginated job history"""
    ensure_job_history_file()
    
    with open(JOB_HISTORY_FILE, 'r') as f:
        all_jobs = json.load(f)
    
    # Apply filters if specified
    if job_type:
        all_jobs = [job for job in all_jobs if job.get('type') == job_type]
    
    # Sort by timestamp (newest first)
    all_jobs.sort(key=lambda x: x.get('start_time', ''), reverse=True)
    
    # Calculate total pages
    total = len(all_jobs)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # Apply pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_jobs = all_jobs[start:end]
    
    return {
        'jobs': paginated_jobs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_job_by_id(job_id):
    """Get a specific job by ID"""
    ensure_job_history_file()
    
    with open(JOB_HISTORY_FILE, 'r') as f:
        jobs = json.load(f)
    
    for job in jobs:
        if job.get('id') == job_id:
            return job
    
    return None

def get_job_items(job_id, page=1, per_page=20):
    """Get paginated items for a specific job"""
    job = get_job_by_id(job_id)
    
    if job and 'items' in job:
        items = job['items']
        
        # Calculate pagination
        total = len(items)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = items[start:end]
        
        return {
            'items': paginated_items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
    
    return {
        'items': [],
        'total': 0,
        'page': page,
        'per_page': per_page,
        'total_pages': 0
    }

def create_job(job_type, options=None):
    """Create a new job and add it to history"""
    ensure_job_history_file()
    
    job_id = str(uuid.uuid4())
    
    new_job = {
        'id': job_id,
        'type': job_type,
        'status': 'Running',
        'options': options or {},
        'start_time': datetime.now().isoformat(),
        'items': []
    }
    
    with open(JOB_HISTORY_FILE, 'r') as f:
        jobs = json.load(f)
    
    jobs.append(new_job)
    
    with open(JOB_HISTORY_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)
    
    return job_id

def add_job_item(job_id, item_info):
    """Add a processed item to a job (no-op in simplified version)"""
    # This is a no-op in the simplified version
    # We'll keep job items tracking to a minimum to avoid breaking anything
    return True

def update_job_status(job_id, status, result=None):
    """Update job status and optionally add result data"""
    ensure_job_history_file()
    
    with open(JOB_HISTORY_FILE, 'r') as f:
        jobs = json.load(f)
    
    updated = False
    for job in jobs:
        if job.get('id') == job_id:
            job['status'] = status
            
            if status in ['Success', 'Failed', 'Completed']:
                job['end_time'] = datetime.now().isoformat()
            
            if result:
                if 'result' not in job:
                    job['result'] = {}
                job['result'].update(result)
            
            updated = True
            break
    
    if updated:
        with open(JOB_HISTORY_FILE, 'w') as f:
            json.dump(jobs, f, indent=2)
    
    return updated

def delete_job(job_id):
    """Delete a job from history"""
    ensure_job_history_file()
    
    with open(JOB_HISTORY_FILE, 'r') as f:
        jobs = json.load(f)
    
    updated_jobs = [job for job in jobs if job.get('id') != job_id]
    
    with open(JOB_HISTORY_FILE, 'w') as f:
        json.dump(updated_jobs, f, indent=2)
    
    return len(jobs) != len(updated_jobs)  # Return True if a job was removed
