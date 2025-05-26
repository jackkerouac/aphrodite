from flask import Blueprint, jsonify, request
import sys
import os
import subprocess
from pathlib import Path
import logging # Import the logging module

logger = logging.getLogger(__name__) # Get a logger instance

bp = Blueprint('check', __name__, url_prefix='/api/check')

@bp.route('/', methods=['POST'])
def check_jellyfin_connection():
    """Check if we can connect to Jellyfin with the provided credentials."""
    if not request.is_json:
        logger.warning("Received non-JSON request for Jellyfin connection check") # Added logging
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Log received data
    logger.info(f"Received data for Jellyfin connection check: {data}")

    # Get connection parameters
    url = data.get('url')
    api_key = data.get('api_key')
    user_id = data.get('user_id')

    # Validate parameters
    if not url or not api_key or not user_id:
        logger.warning("Missing required parameters for Jellyfin connection check")
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

        # Log the command being executed
        logger.info(f"Executing command: {' '.join(cmd)}")

        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit code
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )

        # Log the script output and return code
        logger.info(f"Script stdout: {result.stdout.strip()}")
        logger.error(f"Script stderr: {result.stderr.strip()}") # Use error level for stderr
        logger.info(f"Script return code: {result.returncode}")

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
        logger.exception("Error during Jellyfin connection check") # Log the exception traceback
        return jsonify({
            "success": False,
            "error": f"Error checking Jellyfin connection: {str(e)}"
        }), 500
