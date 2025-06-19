#!/usr/bin/env python3
"""
Progress Broadcaster

Standalone script to send progress updates via HTTP to trigger WebSocket broadcasts.
This is called by the unified_worker to broadcast progress updates without complex async/SQLAlchemy imports.
"""

import sys
import json
import requests


def broadcast_progress_update(job_id: str, completed: int, failed: int, total: int) -> bool:
    """
    Send progress update to API endpoint that will broadcast via WebSocket
    
    Args:
        job_id: Job identifier
        completed: Number of completed posters
        failed: Number of failed posters
        total: Total number of posters
        
    Returns:
        True if broadcast was successful
    """
    try:
        # Calculate progress percentage
        processed = completed + failed
        progress_percentage = (processed / total * 100.0) if total > 0 else 0.0
        
        # Calculate simple ETA based on current progress
        estimated_completion = None
        if completed > 0:  # Only calculate ETA if we have some progress
            from datetime import datetime, timedelta
            
            # Simple ETA calculation: assume each poster takes the same time
            # Get current time and estimate remaining time
            remaining_posters = total - (completed + failed)
            if remaining_posters > 0:
                # Estimate 30 seconds per poster as average
                estimated_seconds = remaining_posters * 30
                estimated_completion_time = datetime.now() + timedelta(seconds=estimated_seconds)
                estimated_completion = estimated_completion_time.isoformat()  # Convert to string!
        
        # Prepare progress data
        progress_data = {
            "total_posters": total,
            "completed_posters": completed,
            "failed_posters": failed,
            "progress_percentage": progress_percentage,
            "estimated_completion": estimated_completion,
            "current_poster": None
        }
        
        # Send to internal API endpoint
        url = f"http://localhost:8000/api/v1/workflow/jobs/broadcast-progress/{job_id}"
        
        response = requests.post(
            url,
            json=progress_data,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Don't print success message here - only return JSON result
            return True
        else:
            print(f"Progress broadcast failed: HTTP {response.status_code}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Progress broadcast error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    """
    Called by unified_worker with progress data
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        
        job_id = data["job_id"]
        completed = data["completed"]
        failed = data["failed"]
        total = data["total"]
        
        success = broadcast_progress_update(job_id, completed, failed, total)
        
        # Return result
        result = {
            "success": success,
            "job_id": job_id
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
