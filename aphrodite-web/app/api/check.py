from flask import Blueprint, jsonify, request
import sys
import os
import subprocess
from pathlib import Path

bp = Blueprint('check', __name__, url_prefix='/api/check')

@bp.route('/', methods=['POST'])
def check_jellyfin_connection():
    """Check if we can connect to Jellyfin with the provided credentials."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    
    # Get connection parameters
    url = data.get('url')
    api_key = data.get('api_key')
    user_id = data.get('user_id')
    
    # Validate parameters
    if not url or not api_key or not user_id:
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Get the base directory (where the aphrodite script is located)
    base_dir = Path(os.path.abspath(__file__)).parents[3]
    script_path = base_dir / 'aphrodite_helpers' / 'check_jellyfin_connection.py'
    
    # Create a temporary settings file if not testing with the real one
    # This helps to test the connection without modifying the user's actual settings
    temp_settings = {
        "api_keys": {
            "Jellyfin": [
                {
                    "url": url,
                    "api_key": api_key,
                    "user_id": user_id
                }
            ]
        }
    }
    
    # Call the script to check the connection
    try:
        # Create Python command to run the check script
        cmd = [
            sys.executable,
            str(script_path),
            "--url", url,
            "--api-key", api_key,
            "--user-id", user_id
        ]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit code
        )
        
        # Check if connection was successful
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": "Successfully connected to Jellyfin server",
                "details": result.stdout.strip()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to connect to Jellyfin server",
                "details": result.stderr.strip() or result.stdout.strip()
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error checking Jellyfin connection: {str(e)}"
        }), 500
