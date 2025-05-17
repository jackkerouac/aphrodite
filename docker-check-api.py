from flask import Blueprint, jsonify, request
import sys
import os
import subprocess
from pathlib import Path
import logging
import traceback

logger = logging.getLogger(__name__)

bp = Blueprint('check', __name__, url_prefix='/api/check')

@bp.route('/', methods=['POST'])
def check_jellyfin_connection():
    """Check if we can connect to Jellyfin with the provided credentials."""
    if not request.is_json:
        logger.warning("Received non-JSON request for Jellyfin connection check")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Log received data (masking sensitive information)
    safe_data = data.copy() if data else {}
    if 'api_key' in safe_data:
        safe_data['api_key'] = '*' * len(safe_data['api_key'])
    logger.info(f"Received data for Jellyfin connection check: {safe_data}")

    # Get connection parameters
    url = data.get('url')
    api_key = data.get('api_key')
    user_id = data.get('user_id')

    # Validate parameters
    if not url or not api_key or not user_id:
        missing = []
        if not url: missing.append('url')
        if not api_key: missing.append('api_key')
        if not user_id: missing.append('user_id')
        
        error_msg = f"Missing required parameters: {', '.join(missing)}"
        logger.warning(error_msg)
        return jsonify({"error": error_msg}), 400

    # Try to find the appropriate script path - check both the Docker path and regular path
    base_dir = Path(os.getcwd())
    
    # First try the Docker-specific script
    script_path = base_dir / 'aphrodite_helpers' / 'docker_check_jellyfin_connection.py'
    
    # If it doesn't exist, fall back to the original script
    if not script_path.exists():
        script_path = base_dir / 'aphrodite_helpers' / 'check_jellyfin_connection.py'
    
    if not script_path.exists():
        error_msg = f"Could not find Jellyfin connection check script at {script_path}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

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

        # Log the command being executed (masking the API key)
        safe_cmd = cmd.copy()
        api_key_index = safe_cmd.index('--api-key') + 1
        if api_key_index < len(safe_cmd):
            safe_cmd[api_key_index] = '*' * len(safe_cmd[api_key_index])
        logger.info(f"Executing command: {' '.join(safe_cmd)}")

        # Run the command with a timeout to prevent hanging
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit code
            encoding='utf-8',  # Explicitly set UTF-8 encoding
            timeout=15  # 15 second timeout to prevent hanging
        )

        # Log the script output and return code
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        logger.info(f"Script stdout: {stdout}")
        if stderr:
            logger.error(f"Script stderr: {stderr}")
        logger.info(f"Script return code: {result.returncode}")

        # Check if connection was successful
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": "Successfully connected to Jellyfin server",
                "details": stdout
            })
        else:
            error_details = stderr or stdout or "No output from connection check script"
            return jsonify({
                "success": False,
                "error": "Failed to connect to Jellyfin server",
                "details": error_details
            }), 400

    except subprocess.TimeoutExpired:
        error_msg = "Connection check timed out after 15 seconds"
        logger.error(error_msg)
        return jsonify({
            "success": False,
            "error": error_msg,
            "details": "The connection to the Jellyfin server may be blocked or the server is not responding."
        }), 408
    except Exception as e:
        logger.error(f"Error during Jellyfin connection check: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Error checking Jellyfin connection: {str(e)}",
            "details": traceback.format_exc()
        }), 500
