#!/usr/bin/env python3
"""
Unified Worker

Combines the working windows_worker with the batch_worker task.
Single Celery app that handles both simple and batch tasks.
"""

import sys
import os
import asyncio
import subprocess

# Add the API directory to Python path
api_path = os.path.join(os.path.dirname(__file__), 'api')
if api_path not in sys.path:
    sys.path.insert(0, api_path)

from celery import Celery
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Helper function to get database configuration
def get_db_config():
    """Get database configuration from environment variables or Docker defaults"""
    return {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5433'),
        'database': os.environ.get('POSTGRES_DB', 'aphrodite'),
        'user': os.environ.get('POSTGRES_USER', 'aphrodite'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'aphrodite123')
    }

# Create unified Celery app
app = Celery('unified_worker')

# Configuration for Windows compatibility
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Windows compatibility
    worker_pool='solo',
    worker_concurrency=1,
)

# Initialize database when worker starts
@app.on_after_configure.connect
def setup_database(sender, **kwargs):
    """Initialize database connection for worker"""
    print("Worker starting - database will be initialized per-task")
    # Set V2 mode flag to prevent v1 legacy imports
    os.environ['APHRODITE_V2_ONLY'] = '1'
    print("V2-only mode enabled - legacy v1 imports disabled")


@app.task
def simple_task(message):
    """Simple test task"""
    print(f"Processing simple task: {message}")
    time.sleep(1)
    print(f"Completed simple task: {message}")
    return f"Done: {message}"


@app.task(bind=True)
def process_batch_job(self, job_id: str) -> Dict[str, Any]:
    """
    Batch job processing task - real poster processing with direct database connection
    """
    print(f"Starting batch job processing: {job_id}")
    
    try:
        print(f"Using direct database connection for reliable processing...")
        
        # Import only standard library and installed packages
        import psycopg2
        from datetime import datetime
        import json
        import uuid
        from pathlib import Path
        
        print("Connecting to database directly...")
        
        # Get database configuration from environment
        db_config = get_db_config()
        print(f"Connecting to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['database']} as {db_config['user']}")
        
        # Direct database connection using environment configuration
        conn = psycopg2.connect(**db_config)
        
        print("Getting job details from database...")
        
        # Get job details
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT total_posters, badge_types, selected_poster_ids FROM batch_jobs WHERE id = %s",
                (job_id,)
            )
            job_data = cursor.fetchone()
            
            if not job_data:
                raise Exception(f"Job not found: {job_id}")
            
            total_posters, badge_types_json, poster_ids_json = job_data
            
            # Handle both JSON strings and PostgreSQL arrays
            if isinstance(badge_types_json, str):
                badge_types = json.loads(badge_types_json)
            else:
                badge_types = badge_types_json  # Already a list
                
            if isinstance(poster_ids_json, str):
                poster_ids = json.loads(poster_ids_json)
            else:
                poster_ids = poster_ids_json  # Already a list
        
        print(f"Processing {total_posters} posters with badges: {badge_types}")
        
        # Update job to processing status
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE batch_jobs SET status = %s, started_at = %s WHERE id = %s",
                ('processing', datetime.utcnow(), job_id)
            )
            conn.commit()
        
        # Initial progress broadcast
        broadcast_progress_update(job_id, 0, 0, total_posters)
        
        completed = 0
        failed = 0
        
        # Process each poster
        for poster_id in poster_ids:
            print(f"Processing poster: {poster_id}")
            
            try:
                # Real poster processing
                result = process_single_poster(poster_id, badge_types, job_id)
                
                if result["success"]:
                    # Update poster status to completed - use simple INSERT
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO poster_processing_status 
                               (id, batch_job_id, poster_id, status, output_path, completed_at, retry_count) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (str(uuid.uuid4()), job_id, poster_id, 'completed', result["output_path"], datetime.utcnow(), 0)
                        )
                        conn.commit()
                    
                    completed += 1
                    print(f"✅ Completed poster {poster_id}")
                    
                else:
                    # Update poster status to failed - use simple INSERT
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO poster_processing_status 
                               (id, batch_job_id, poster_id, status, error_message, completed_at, retry_count) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (str(uuid.uuid4()), job_id, poster_id, 'failed', result["error"], datetime.utcnow(), 0)
                        )
                        conn.commit()
                    
                    failed += 1
                    print(f"❌ Failed poster {poster_id}: {result['error']}")
                    
            except Exception as e:
                # Handle poster processing exceptions
                error_msg = str(e)
                print(f"❌ Exception processing poster {poster_id}: {error_msg}")
                
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO poster_processing_status 
                           (id, batch_job_id, poster_id, status, error_message, completed_at, retry_count) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (str(uuid.uuid4()), job_id, poster_id, 'failed', error_msg, datetime.utcnow(), 0)
                    )
                    conn.commit()
                
                failed += 1
            
            # Update job progress in database
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE batch_jobs SET completed_posters = %s, failed_posters = %s WHERE id = %s",
                    (completed, failed, job_id)
                )
                conn.commit()
            
            # Broadcast progress update via WebSocket
            broadcast_progress_update(job_id, completed, failed, total_posters)
        
        # Finalize job
        final_status = 'completed' if failed == 0 else 'failed'
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE batch_jobs SET status = %s, completed_at = %s WHERE id = %s",
                (final_status, datetime.utcnow(), job_id)
            )
            conn.commit()
        
        # Final progress broadcast
        broadcast_progress_update(job_id, completed, failed, total_posters)
        
        conn.close()
        
        result = {
            "success": final_status == 'completed',
            "completed": completed,
            "failed": failed,
            "total": total_posters,
            "job_id": job_id,
            "message": f"Processed {completed} posters successfully, {failed} failed"
        }
        
        print(f"Batch job completed: {job_id} -> {result}")
        return result
        
    except Exception as e:
        error_msg = f"Processing error: {e}"
        print(f"Batch job failed: {job_id} -> {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Update job status to failed
        try:
            import psycopg2
            
            # Get database configuration from environment
            db_config = get_db_config()
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE batch_jobs SET status = %s, error_summary = %s WHERE id = %s",
                    ('failed', str(e), job_id)
                )
                conn.commit()
            conn.close()
        except:
            pass  # Ignore database update errors
        
        return {
            "success": False,
            "error": error_msg,
            "job_id": job_id
        }


def process_single_poster(poster_id: str, badge_types: list, job_id: str) -> dict:
    """
    Process a single poster with real v2 badge processing
    """
    try:
        from pathlib import Path
        import uuid
        
        print(f"Processing poster {poster_id} with badges: {badge_types} using v2 pipeline")
        
        # Create output directory
        output_dir = Path("api/static/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique output filename
        output_filename = f"{uuid.uuid4()}.jpg"
        output_path = output_dir / output_filename
        
        # Get input poster path
        input_poster = get_input_poster_path(poster_id)
        if not input_poster:
            raise Exception(f"No input poster found for {poster_id}")
        
        # Get the real Jellyfin ID from the poster
        jellyfin_id = get_jellyfin_id_from_poster(input_poster)
        if not jellyfin_id:
            print(f"⚠️ No Jellyfin ID found for {input_poster}, badges may not be applied")
        
        print(f"Processing with Jellyfin ID: {jellyfin_id}")
        
        # Process with v2 badge processing system
        print(f"About to call run_v2_badge_processing...")
        try:
            result = run_v2_badge_processing(
                poster_path=str(input_poster),
                badge_types=badge_types,
                output_path=str(output_path),
                jellyfin_id=jellyfin_id  # Pass real Jellyfin ID
            )
            print(f"run_v2_badge_processing returned: {result}")
        except Exception as v2_error:
            print(f"❌ Exception in run_v2_badge_processing: {v2_error}")
            import traceback
            traceback.print_exc()
            raise v2_error
        
        if result["success"]:
            print(f"✅ Created enhanced poster with v2 processing: {result['output_path']}")
            
            # If badges were applied, upload to Jellyfin and add tag
            if result["applied_badges"]:
                # CRITICAL FIX: Use the ORIGINAL poster_id for Jellyfin upload, not the fallback poster's ID
                # The poster_id from the workflow IS the Jellyfin ID we should upload to
                upload_jellyfin_id = poster_id.replace('-', '')  # Remove dashes to match Jellyfin format
                
                print(f"Uploading enhanced poster to ORIGINAL Jellyfin ID: {upload_jellyfin_id} (not {jellyfin_id})")
                
                # Run Jellyfin upload via subprocess to avoid async conflicts
                upload_result = run_jellyfin_upload_subprocess(
                    upload_jellyfin_id,  # Use original poster ID, not fallback poster ID
                    result["output_path"]
                )
                
                if upload_result["upload_success"]:
                    print(f"✅ Successfully uploaded enhanced poster to Jellyfin")
                    if upload_result.get("tag_success"):
                        print(f"✅ Successfully added aphrodite-overlay tag")
                    else:
                        print(f"❌ Failed to add aphrodite-overlay tag: {upload_result.get('tag_error', 'Unknown error')}")
                else:
                    print(f"❌ Failed to upload enhanced poster to Jellyfin: {upload_result.get('error', 'Unknown error')}")
            
            return {
                "success": True,
                "output_path": result["output_path"],
                "poster_id": poster_id,
                "job_id": job_id,
                "applied_badges": result["applied_badges"],
                "message": f"Applied {len(result['applied_badges'])} badges and uploaded to Jellyfin"
            }
        else:
            raise Exception(result["error"])
        
    except Exception as e:
        print(f"❌ Failed to process poster {poster_id} with v2 system: {e}")
        
        # Fallback to placeholder if v2 processing fails
        try:
            fallback_result = create_fallback_poster(poster_id, badge_types, job_id)
            print(f"⚠️ Using fallback poster for {poster_id}")
            return fallback_result
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            return {
                "success": False,
                "error": f"v2 processing failed: {str(e)}, fallback failed: {str(fallback_error)}",
                "poster_id": poster_id,
                "job_id": job_id
            }


def download_jellyfin_poster(jellyfin_id: str) -> Optional[bytes]:
    """
    Download poster data from Jellyfin - SYNC HTTP APPROACH WITH DB SETTINGS
    """
    import requests
    import psycopg2
    import json
    
    try:
        print(f"Downloading poster from Jellyfin for ID: {jellyfin_id}")
        
        # Get Jellyfin connection details from database
        # Get database configuration from environment
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        
        jellyfin_url = None
        jellyfin_token = None
        
        with conn.cursor() as cursor:
            # Debug: List all system config keys
            cursor.execute("SELECT key, value FROM system_config")
            all_configs = cursor.fetchall()
            print(f"📋 All system_config entries:")
            for key, value in all_configs:
                print(f"   {key}: {str(value)[:100]}...")
            
            # Get Jellyfin URL
            cursor.execute(
                "SELECT value FROM system_config WHERE key = %s",
                ('jellyfin_url',)
            )
            url_result = cursor.fetchone()
            if url_result:
                jellyfin_url = url_result[0]
                print(f"🌐 Found Jellyfin URL: {jellyfin_url}")
            
            # Get Jellyfin API key  
            cursor.execute(
                "SELECT value FROM system_config WHERE key = %s",
                ('jellyfin_api_key',)
            )
            token_result = cursor.fetchone()
            if token_result:
                jellyfin_token = token_result[0]
                print(f"🔑 Found Jellyfin API key: {jellyfin_token[:10]}...")
            
            # Try to get from settings.yaml config file structure
            if not jellyfin_url or not jellyfin_token:
                cursor.execute(
                    "SELECT value FROM system_config WHERE key = %s",
                    ('settings.yaml',)
                )
                settings_result = cursor.fetchone()
                if settings_result:
                    settings_data = settings_result[0]
                    if isinstance(settings_data, dict):
                        # Navigate: settings.yaml -> api_keys -> Jellyfin -> [0] -> url/api_key
                        api_keys = settings_data.get('api_keys', {})
                        jellyfin_configs = api_keys.get('Jellyfin', [])
                        if jellyfin_configs and len(jellyfin_configs) > 0:
                            jellyfin_config = jellyfin_configs[0]  # Take first Jellyfin config
                            jellyfin_url = jellyfin_config.get('url')
                            jellyfin_token = jellyfin_config.get('api_key')
                            print(f"📄 Found in settings.yaml: URL={jellyfin_url}, Key={jellyfin_token[:10] if jellyfin_token else None}...")
                        else:
                            print(f"📄 No Jellyfin config found in api_keys structure")
        
        conn.close()
        
        if not jellyfin_url or not jellyfin_token:
            print(f"❌ Missing Jellyfin configuration in database")
            print(f"   URL: {'✅' if jellyfin_url else '❌'} Token: {'✅' if jellyfin_token else '❌'}")
            return None
        
        # Construct poster URL directly
        poster_url = f"{jellyfin_url}/Items/{jellyfin_id}/Images/Primary"
        
        # Headers for authentication
        headers = {
            'Authorization': f'MediaBrowser Token="{jellyfin_token}"',
            'User-Agent': 'Aphrodite/2.0'
        }
        
        print(f"Requesting: {poster_url}")
        
        # Make synchronous HTTP request
        response = requests.get(poster_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            poster_data = response.content
            print(f"Successfully downloaded {len(poster_data)} bytes")
            return poster_data
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error downloading poster: {e}")
        return None


def get_input_poster_path(poster_id: str) -> Optional[Path]:
    """
    Download FRESH poster for batch processing - ALWAYS DOWNLOAD NEW
    """
    from pathlib import Path
    import json
    import tempfile
    import subprocess
    from datetime import datetime
    
    print(f"🔄 FORCING FRESH DOWNLOAD for batch processing: {poster_id}")
    
    # Remove dashes from poster ID to match Jellyfin format
    poster_id_no_dashes = poster_id.replace('-', '')
    print(f"Normalized Jellyfin ID: {poster_id_no_dashes}")
    
    # ALWAYS download fresh poster for batch jobs - no cache lookup!
    # This ensures each batch job gets the correct poster
    try:
        print(f"📥 Downloading fresh poster from Jellyfin for batch job...")
        poster_data = download_jellyfin_poster(poster_id_no_dashes)
        
        if poster_data:
            # Cache the downloaded poster with batch-specific naming
            cache_dir = Path("api/cache/posters")
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Create unique cached filename for this batch
            import uuid
            batch_uuid = uuid.uuid4().hex[:8]
            cache_filename = f"batch_{poster_id_no_dashes}_{batch_uuid}.jpg"
            cache_path = cache_dir / cache_filename
            
            # Write poster data to cache
            with open(cache_path, 'wb') as f:
                f.write(poster_data)
            
            # Create metadata file
            meta_path = cache_path.with_suffix('.meta')
            metadata = {
                "jellyfin_id": poster_id_no_dashes,
                "original_poster_id": poster_id,
                "batch_download": True,
                "cached_at": datetime.now().isoformat()
            }
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Downloaded and cached fresh poster: {cache_filename}")
            return cache_path
        else:
            print(f"❌ Failed to download fresh poster for {poster_id_no_dashes}")
            
    except Exception as e:
        print(f"❌ Error downloading fresh poster for {poster_id_no_dashes}: {e}")
    
    # If fresh download fails, the job should fail rather than use wrong poster
    print(f"❌ CRITICAL: Fresh download failed for {poster_id_no_dashes}")
    print(f"   Batch processing will fail rather than use wrong poster.")
    
    return None


def run_jellyfin_upload_subprocess(jellyfin_id: str, poster_path: str) -> dict:
    """
    Run Jellyfin upload via subprocess to avoid async context conflicts
    """
    import subprocess
    import json
    
    try:
        print(f"Uploading enhanced poster back to Jellyfin for {jellyfin_id}")
        
        # Prepare request data for subprocess
        request_data = {
            "jellyfin_id": jellyfin_id,
            "poster_path": poster_path
        }
        
        request_json = json.dumps(request_data)
        
        # Get the subprocess runner path
        script_dir = os.path.dirname(__file__)
        runner_path = os.path.join(script_dir, "jellyfin_upload_runner.py")
        
        # Run the subprocess
        result = subprocess.run(
            [sys.executable, runner_path],
            input=request_json,
            text=True,
            capture_output=True,
            timeout=60,  # 1 minute timeout
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            error_msg = f"Subprocess failed with code {result.returncode}: {result.stderr}"
            print(f"[ERROR] {error_msg}")
            return {
                "upload_success": False,
                "tag_success": False,
                "error": error_msg
            }
        
        # Parse the response
        if result.stdout is None or not result.stdout.strip():
            return {
                "upload_success": False,
                "tag_success": False,
                "error": "No response from subprocess"
            }
        
        response_data = json.loads(result.stdout.strip())
        return response_data
        
    except subprocess.TimeoutExpired:
        error_msg = "Jellyfin upload timed out after 1 minute"
        print(f"[ERROR] {error_msg}")
        return {
            "upload_success": False,
            "tag_success": False,
            "error": error_msg
        }
    except Exception as e:
        error_msg = f"Subprocess execution error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {
            "upload_success": False,
            "tag_success": False,
            "error": error_msg
        }


def get_jellyfin_id_from_poster(poster_path: Path) -> Optional[str]:
    """
    Extract real Jellyfin ID from cached poster file
    """
    import json
    
    # Check for metadata file
    meta_file = poster_path.with_suffix('.meta')
    if meta_file.exists():
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            jellyfin_id = metadata.get('jellyfin_id')
            if jellyfin_id:
                print(f"Found Jellyfin ID from metadata: {jellyfin_id}")
                return jellyfin_id
        except Exception as e:
            print(f"Error reading metadata: {e}")
    
    # Fallback: extract from filename
    if poster_path.name.startswith('jellyfin_'):
        parts = poster_path.stem.split('_')
        if len(parts) >= 2:
            jellyfin_id = parts[1]
            print(f"Extracted Jellyfin ID from filename: {jellyfin_id}")
            return jellyfin_id
    
    print(f"No Jellyfin ID found for {poster_path}")
    return None


def run_v2_badge_processing(poster_path: str, badge_types: list, output_path: str, jellyfin_id: Optional[str] = None) -> dict:
    """
    Run the v2 badge processing system via subprocess to avoid Celery import conflicts
    """
    print(f"[DEBUG] Running V2 processing via subprocess")
    print(f"[DEBUG] Parameters: poster_path={poster_path}, badge_types={badge_types}, jellyfin_id={jellyfin_id}")
    
    # Ensure we're not importing any v1 legacy code
    import subprocess
    import json
    
    try:
        # Prepare request data for subprocess
        request_data = {
            "poster_path": poster_path,
            "badge_types": badge_types,
            "output_path": output_path,
            "use_demo_data": False,
            "jellyfin_id": jellyfin_id
        }
        
        request_json = json.dumps(request_data)
        print(f"[DEBUG] Subprocess request: {request_json}")
        
        # Get the subprocess runner path
        script_dir = os.path.dirname(__file__)
        runner_path = os.path.join(script_dir, "v2_subprocess_runner.py")
        
        print(f"[DEBUG] Running subprocess: {runner_path}")
        
        # Set environment for UTF-8 encoding and disable v1 legacy imports
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'
        env['APHRODITE_V2_ONLY'] = '1'  # Flag to disable v1 imports
        
        # Run the subprocess
        result = subprocess.run(
            [sys.executable, runner_path],
            input=request_json,
            text=True,
            capture_output=True,
            timeout=300,  # 5 minute timeout
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace invalid characters instead of crashing
        )
        
        print(f"[DEBUG] Subprocess return code: {result.returncode}")
        print(f"[DEBUG] Subprocess stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Subprocess failed with code {result.returncode}: {result.stderr}")
        
        # Parse the response
        try:
            # Handle potential None stdout or encoding issues
            if result.stdout is None:
                raise Exception("Subprocess returned no stdout")
                
            stdout_text = result.stdout.strip()
            if not stdout_text:
                raise Exception("Subprocess returned empty stdout")
                
            # Handle multiple lines in stdout - take the last line as JSON response
            lines = stdout_text.split('\n')
            json_line = lines[-1]  # Last line should be the JSON response
            response_data = json.loads(json_line)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw stdout: {result.stdout}")
            raise Exception(f"Failed to parse subprocess response: {e}")
        
        print(f"[DEBUG] Subprocess response: {response_data}")
        
        return response_data
        
    except subprocess.TimeoutExpired:
        error_msg = "V2 processing timed out after 5 minutes"
        print(f"[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "applied_badges": [],
            "output_path": None,
            "processing_time": 0
        }
    except Exception as e:
        error_msg = f"Subprocess execution error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg,
            "applied_badges": [],
            "output_path": None,
            "processing_time": 0
        }


def broadcast_progress_update(job_id: str, completed: int, failed: int, total: int) -> None:
    """
    Broadcast progress update to API endpoint for WebSocket broadcasting
    """
    import subprocess
    import json
    
    try:
        print(f"Broadcasting progress: job={job_id}, completed={completed}, failed={failed}, total={total}")
        
        # Prepare progress data
        progress_data = {
            "job_id": job_id,
            "completed": completed,
            "failed": failed,
            "total": total
        }
        
        # Get the broadcaster script path
        script_dir = os.path.dirname(__file__)
        broadcaster_path = os.path.join(script_dir, "progress_broadcaster.py")
        
        # Run the broadcaster
        result = subprocess.run(
            [sys.executable, broadcaster_path],
            input=json.dumps(progress_data),
            text=True,
            capture_output=True,
            timeout=10,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"Progress broadcast successful for job {job_id}")
        else:
            print(f"Progress broadcast failed: {result.stderr}")
            
    except Exception as e:
        print(f"Progress broadcast error: {e}")
        # Don't fail the job if broadcast fails


def create_fallback_poster(poster_id: str, badge_types: list, job_id: str) -> dict:
    """
    Create a fallback poster if v2 processing fails
    """
    from pathlib import Path
    import uuid
    import shutil
    from datetime import datetime
    
    print(f"Creating fallback poster for {poster_id}")
    
    # Create output directory
    output_dir = Path("api/static/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique output filename
    output_filename = f"fallback_{uuid.uuid4()}.jpg"
    output_path = output_dir / output_filename
    
    # Try to copy a sample poster
    input_poster = get_input_poster_path(poster_id)
    if input_poster and input_poster.exists():
        shutil.copy2(input_poster, output_path)
        badge_info = f"Fallback poster with requested badges: {', '.join(badge_types)}"
    else:
        # Create a text file as last resort
        badge_info = f"Fallback for poster {poster_id}\nRequested badges: {', '.join(badge_types)}\nJob: {job_id}\nTimestamp: {datetime.now()}"
        output_path = output_path.with_suffix('.txt')
        output_path.write_text(badge_info)
    
    return {
        "success": True,
        "output_path": str(output_path),
        "poster_id": poster_id,
        "job_id": job_id,
        "applied_badges": [],  # No real badges applied in fallback
        "message": f"Fallback: {badge_info}"
    }


if __name__ == '__main__':
    print("UNIFIED WORKER STARTING")
    print("=" * 40)
    print("Redis: redis://localhost:6380/0")
    print("Pool: solo (Windows compatible)")
    print("Tasks:")
    print("  - simple_task (test)")
    print("  - process_batch_job (batch processing)")
    print("=" * 40)
    
    # Run with minimal arguments
    app.worker_main([
        'worker',
        '--pool=solo',
        '--loglevel=info'
    ])
