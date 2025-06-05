from flask import Blueprint, jsonify, request
import sys
import os
import subprocess
from pathlib import Path
import logging
import requests

logger = logging.getLogger(__name__)

bp = Blueprint('check', __name__, url_prefix='/api/check')

@bp.route('/', methods=['POST'])
def check_api_connection():
    """Check if we can connect to various APIs with the provided credentials."""
    if not request.is_json:
        logger.warning("Received non-JSON request for API connection check")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    logger.info(f"Received data for API connection check: {data}")

    # Check if this is the old Jellyfin format or new API type format
    api_type = data.get('api_type')
    
    if api_type:
        # New format with api_type
        return handle_api_test(api_type, data)
    else:
        # Legacy Jellyfin format
        return handle_jellyfin_test(data)

def handle_jellyfin_test(data):
    """Handle Jellyfin connection test (legacy format)."""
    url = data.get('url')
    api_key = data.get('api_key')
    user_id = data.get('user_id')

    if not url or not api_key or not user_id:
        logger.warning("Missing required parameters for Jellyfin connection check")
        return jsonify({"error": "Missing required parameters"}), 400

    # Get the base directory and use the existing Jellyfin check script
    base_dir = Path(os.path.abspath(__file__)).parents[3]
    script_path = base_dir / 'aphrodite_helpers' / 'check_jellyfin_connection.py'

    try:
        cmd = [
            sys.executable,
            str(script_path),
            "--url", url,
            "--api-key", api_key,
            "--user-id", user_id
        ]

        logger.info(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )

        logger.info(f"Script stdout: {result.stdout.strip()}")
        logger.error(f"Script stderr: {result.stderr.strip()}")
        logger.info(f"Script return code: {result.returncode}")

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
        logger.exception("Error during Jellyfin connection check")
        return jsonify({
            "success": False,
            "error": f"Error checking Jellyfin connection: {str(e)}"
        }), 500

def handle_api_test(api_type, data):
    """Handle API connection tests for different providers."""
    try:
        if api_type == 'jellyfin':
            return test_jellyfin_direct(data)
        elif api_type == 'omdb':
            return test_omdb_connection(data)
        elif api_type == 'tmdb':
            return test_tmdb_connection(data)
        elif api_type == 'mdblist':
            return test_mdblist_connection(data)
        elif api_type == 'anidb':
            return test_anidb_connection(data)
        else:
            return jsonify({"error": f"Unknown API type: {api_type}"}), 400
    except Exception as e:
        logger.exception(f"Error during {api_type} connection check")
        return jsonify({
            "success": False,
            "error": f"Error checking {api_type} connection: {str(e)}"
        }), 500

def test_jellyfin_direct(data):
    """Test Jellyfin connection directly."""
    url = data.get('url')
    api_key = data.get('api_key')
    user_id = data.get('user_id')
    
    if not url or not api_key or not user_id:
        return jsonify({"error": "Missing required Jellyfin parameters"}), 400
    
    try:
        headers = {"X-Emby-Token": api_key}
        
        # Test server info endpoint
        response = requests.get(f"{url}/System/Info", headers=headers, timeout=10)
        response.raise_for_status()
        
        server_info = response.json()
        server_name = server_info.get('ServerName', 'Unknown')
        version = server_info.get('Version', 'Unknown')
        
        # Test user access
        user_response = requests.get(f"{url}/Users/{user_id}", headers=headers, timeout=10)
        user_response.raise_for_status()
        
        user_info = user_response.json()
        user_name = user_info.get('Name', 'Unknown')
        
        return jsonify({
            "success": True,
            "message": f"Connected to {server_name} (v{version}) as {user_name}"
        })
        
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"Jellyfin connection failed: {str(e)}"
        }), 400

def test_omdb_connection(data):
    """Test OMDB API connection."""
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({"error": "Missing OMDB API key"}), 400
    
    try:
        # Test with a simple movie query
        response = requests.get(
            "http://www.omdbapi.com/",
            params={
                'apikey': api_key,
                'i': 'tt0111161',  # The Shawshank Redemption
                't': None
            },
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('Response') == 'True':
            return jsonify({
                "success": True,
                "message": "OMDB API connection successful"
            })
        elif result.get('Error') == 'Invalid API key!':
            return jsonify({
                "success": False,
                "error": "Invalid OMDB API key"
            }), 400
        else:
            return jsonify({
                "success": False,
                "error": f"OMDB API error: {result.get('Error', 'Unknown error')}"
            }), 400
            
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"OMDB connection failed: {str(e)}"
        }), 400

def test_tmdb_connection(data):
    """Test TMDB API connection."""
    api_key = data.get('api_key')
    language = data.get('language', 'en')
    
    if not api_key:
        return jsonify({"error": "Missing TMDB API key"}), 400
    
    try:
        # Test with configuration endpoint
        response = requests.get(
            "https://api.themoviedb.org/3/configuration",
            params={
                'api_key': api_key,
                'language': language
            },
            timeout=10
        )
        
        if response.status_code == 401:
            return jsonify({
                "success": False,
                "error": "Invalid TMDB API key"
            }), 400
        
        response.raise_for_status()
        result = response.json()
        
        if 'images' in result:
            return jsonify({
                "success": True,
                "message": "TMDB API connection successful"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Unexpected TMDB API response"
            }), 400
            
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"TMDB connection failed: {str(e)}"
        }), 400

def test_mdblist_connection(data):
    """Test MDBList API connection."""
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({"error": "Missing MDBList API key"}), 400
    
    try:
        # Test with a simple movie query using TMDB ID
        response = requests.get(
            "https://api.mdblist.com/",
            params={
                'apikey': api_key,
                'i': '111161'  # The Shawshank Redemption TMDB ID
            },
            timeout=10
        )
        
        if response.status_code == 401:
            return jsonify({
                "success": False,
                "error": "Invalid MDBList API key"
            }), 400
        
        response.raise_for_status()
        result = response.json()
        
        # Check if we got a valid response with movie data
        if result and not result.get('error'):
            return jsonify({
                "success": True,
                "message": "MDBList API connection successful"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"MDBList API error: {result.get('error', 'Unknown error')}"
            }), 400
            
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"MDBList connection failed: {str(e)}"
        }), 400

def test_anidb_connection(data):
    """Test AniDB API connection."""
    username = data.get('username')
    password = data.get('password')
    version = data.get('version', 1)
    client_name = data.get('client_name', 'aphroditetest')
    
    if not username or not password:
        return jsonify({"error": "Missing AniDB username or password"}), 400
    
    try:
        # Note: AniDB UDP API is complex and requires careful implementation
        # For now, we'll do a basic validation that doesn't actually connect
        # to avoid potential issues with the AniDB API rate limiting
        
        # Basic validation of credentials format
        if len(username.strip()) == 0 or len(password.strip()) == 0:
            return jsonify({
                "success": False,
                "error": "Invalid AniDB credentials format"
            }), 400
        
        # For now, we'll return a warning that this is a basic check
        return jsonify({
            "success": True,
            "message": "AniDB credentials format validated (full connection test not implemented)"
        })
        
        # TODO: Implement actual AniDB UDP API connection test
        # This would require:
        # 1. UDP socket connection to api.anidb.net:9000
        # 2. AUTH command with username/password
        # 3. LOGOUT command
        # 4. Proper session management
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AniDB connection test failed: {str(e)}"
        }), 400
