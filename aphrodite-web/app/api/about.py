"""
About page API - System information and details
"""
from flask import Blueprint, jsonify
import os
import time
import hashlib
import sqlite3
import psutil
import requests
from datetime import datetime, timedelta
from packaging import version

bp = Blueprint('about', __name__, url_prefix='/api/about')

def get_database_path():
    """Get the path to the SQLite database"""
    # Determine if we're in Docker environment
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        return '/app/data/aphrodite.db'
    else:
        # Development environment - go up from aphrodite-web/app/api to aphrodite/data
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base_dir, 'data', 'aphrodite.db')

def get_current_version():
    """Get the current version from version.yml"""
    try:
        # Determine base directory
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            version_file = '/app/version.yml'
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            version_file = os.path.join(base_dir, 'version.yml')
        
        if os.path.exists(version_file):
            import yaml
            with open(version_file, 'r') as f:
                version_data = yaml.safe_load(f)
                return version_data.get('version', 'Unknown')
        else:
            return 'Unknown'
            
    except Exception as e:
        print(f"Error getting version: {e}")
        return 'Unknown'

def get_execution_mode():
    """Detect the execution mode (Docker, Development, etc.)"""
    try:
        # Check for Docker environment
        if (os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')):
            return 'Docker'
        
        # Check if running from development environment
        # Look for aphrodite.py in parent directories
        current_dir = os.path.dirname(__file__)
        
        # Go up from aphrodite-web/app/api to aphrodite/
        base_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        aphrodite_py = os.path.join(base_dir, 'aphrodite.py')
        
        if os.path.exists(aphrodite_py):
            return 'Development'
        
        # Check if we're in a git repository (another dev indicator)
        git_dir = os.path.join(base_dir, '.git')
        if os.path.exists(git_dir):
            return 'Development (Git)'
        
        # Check if Flask is running in debug mode
        from flask import current_app
        if current_app and current_app.debug:
            return 'Development (Debug)'
        
        # Check if installed as package
        try:
            import pkg_resources
            pkg_resources.get_distribution('aphrodite')
            return 'Installed Package'
        except:
            pass
        
        # Check environment variables
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == '1':
            return 'Development (Flask)'
        
        return 'Unknown'
        
    except Exception as e:
        print(f"Error detecting execution mode: {e}")
        return 'Unknown'

def get_database_schema_hash():
    """Generate a hash of the database schema structure"""
    try:
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            return 'No Database'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names and their schemas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        schema_parts = []
        for (table_name,) in tables:
            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            schema = cursor.fetchone()
            if schema:
                schema_parts.append(f"{table_name}:{schema[0]}")
        
        conn.close()
        
        # Create hash of all schemas combined
        combined_schema = '|'.join(schema_parts)
        hash_obj = hashlib.sha256(combined_schema.encode())
        return hash_obj.hexdigest()[:12]  # First 12 characters
        
    except Exception as e:
        print(f"Error getting database schema hash: {e}")
        return 'Error'

def get_server_uptime():
    """Get the server uptime"""
    try:
        # Get the current process (Flask server)
        current_process = psutil.Process()
        
        # Calculate uptime
        create_time = datetime.fromtimestamp(current_process.create_time())
        uptime = datetime.now() - create_time
        
        # Format uptime
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
            
    except Exception as e:
        print(f"Error getting uptime: {e}")
        return 'Unknown'

@bp.route('/system-info', methods=['GET'])
def get_system_info():
    """Get comprehensive system information for the About page"""
    try:
        system_info = {
            'success': True,
            'version': get_current_version(),
            'execution_mode': get_execution_mode(),
            'database_schema_hash': get_database_schema_hash(),
            'uptime': get_server_uptime(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'version': 'Unknown',
            'execution_mode': 'Unknown', 
            'database_schema_hash': 'Error',
            'uptime': 'Unknown',
            'timestamp': datetime.now().isoformat()
        }), 500

def get_latest_github_release():
    """Get the latest release from GitHub"""
    try:
        # GitHub API endpoint for latest release
        url = "https://api.github.com/repos/jackkerouac/aphrodite/releases/latest"
        
        # Make request with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        release_data = response.json()
        
        # Extract version from tag_name (remove 'v' prefix if present)
        tag_name = release_data.get('tag_name', '')
        latest_version = tag_name.lstrip('v')
        
        return {
            'version': latest_version,
            'url': release_data.get('html_url', 'https://github.com/jackkerouac/aphrodite/releases'),
            'name': release_data.get('name', f'Release {latest_version}'),
            'published_at': release_data.get('published_at', '')
        }
        
    except Exception as e:
        print(f"Error fetching GitHub release: {e}")
        return None

@bp.route('/check-updates', methods=['GET'])
def check_for_updates():
    """Check for available updates from GitHub releases"""
    try:
        current_version = get_current_version()
        
        # Get latest release from GitHub
        latest_release = get_latest_github_release()
        
        if not latest_release:
            # Fallback if GitHub API fails
            return jsonify({
                'success': True,
                'current_version': current_version,
                'latest_version': current_version,
                'update_available': False,
                'release_notes_url': 'https://github.com/jackkerouac/aphrodite/releases',
                'message': 'Unable to check for updates at this time'
            })
        
        latest_version = latest_release['version']
        
        # Compare versions using packaging.version for proper semantic versioning
        update_available = False
        try:
            if current_version != 'Unknown' and latest_version:
                # Remove 'v' prefix from current version if present
                current_clean = current_version.lstrip('v')
                update_available = version.parse(latest_version) > version.parse(current_clean)
        except Exception as e:
            print(f"Error comparing versions: {e}")
            # Fallback to string comparison
            update_available = latest_version != current_version
        
        update_info = {
            'success': True,
            'current_version': current_version,
            'latest_version': latest_version,
            'update_available': update_available,
            'release_notes_url': latest_release['url'],
            'release_name': latest_release['name'],
            'published_at': latest_release['published_at'],
            'message': 'Update available!' if update_available else 'You are running the latest version.'
        }
        
        return jsonify(update_info)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to check for updates'
        }), 500
