import os
import re
import datetime
from flask import Flask, send_from_directory, jsonify, request, url_for
from pathlib import Path
import logging
import urllib.parse
import yaml
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application"""
    # Determine if we're in Docker environment
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    # Set static folder path based on environment
    if is_docker:
        # In Docker, the built frontend is at /app/aphrodite-web/frontend/dist
        static_folder_path = '/app/aphrodite-web/frontend/dist'
    else:
        # In development, use relative path
        static_folder_path = '../frontend/dist'
    
    # Set up logging to be more verbose

    app = Flask(__name__, static_folder=static_folder_path, static_url_path='/static')
    
    # Add early debug logging about static folder
    print(f"DEBUG: Flask app created with static_folder='{static_folder_path}'")
    print(f"DEBUG: Static folder exists: {os.path.exists(static_folder_path)}")
    if os.path.exists(static_folder_path):
        print(f"DEBUG: Static folder contents: {os.listdir(static_folder_path)}")
    
    # Auto-repair settings before anything else
    try:
        # Determine base directory for settings
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            settings_path = '/app/settings.yaml'
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            settings_path = os.path.join(base_dir, 'settings.yaml')
        
        # Import and run auto-repair
        import sys
        sys.path.append('/app' if is_docker else base_dir)
        from aphrodite_helpers.config_auto_repair import validate_and_repair_settings
        
        print(f"🔧 Web app auto-repairing settings: {settings_path}")
        validate_and_repair_settings(settings_path)
        print("✅ Settings auto-repair completed for web app")
        
    except Exception as e:
        print(f"⚠️ Settings auto-repair failed in web app: {e}")
        # Continue anyway - the app should still work with existing settings
    
    # Configure logging
    from flask.logging import create_logger
    logger = create_logger(app)
    app.logger.setLevel(logging.DEBUG)
    
    # Add a stream handler to ensure logs are visible
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    
    # Debug log about environment
    app.logger.info("DEBUG: Flask application starting up")
    
    # Check config files readability
    app.logger.info("DEBUG: Checking configuration files")
    config_files = [
        'settings.yaml',
        'badge_settings_audio.yml',
        'badge_settings_resolution.yml',
        'badge_settings_review.yml'
    ]
    
    # Determine base directory (Docker vs. development)
    # Check for Docker environment more reliably
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')  # Docker creates this file
    )
    
    if is_docker:
        base_dir = '/app'
        app.logger.info("DEBUG: Running in Docker environment, base dir: /app")
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        app.logger.info(f"DEBUG: Running in development environment, base dir: {base_dir}")
    
    # Log version information for debugging
    app.logger.info("=" * 50)
    app.logger.info("🚀 APHRODITE VERSION DEBUG INFO")
    app.logger.info("=" * 50)
    try:
        version_file = os.path.join(base_dir, 'version.yml')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                version_data = yaml.safe_load(f)
                current_version = version_data.get('version', 'unknown')
            app.logger.info(f"📋 Current version from version.yml: {current_version}")
            app.logger.info(f"📁 Version file location: {version_file}")
        else:
            app.logger.info(f"❌ Version file not found at {version_file}")
            current_version = 'unknown'
        
        # Check version cache
        cache_file = os.path.join(base_dir, 'version_cache.json')
        if os.path.exists(cache_file):
            import json
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                if 'data' in cache_data and 'current_version' in cache_data['data']:
                    cached_version = cache_data['data']['current_version']
                    app.logger.info(f"💾 Cached version: {cached_version}")
                else:
                    app.logger.info("💾 Version cache exists but no version data found")
            except Exception as e:
                app.logger.info(f"⚠️ Failed to read version cache: {e}")
        else:
            app.logger.info("💾 No version cache found")
            
        # Test VersionService
        try:
            import sys
            sys.path.append(base_dir)
            from app.services.version_service import VersionService
            vs = VersionService(base_dir)
            service_version = vs.get_current_version()
            app.logger.info(f"🔧 VersionService reports: {service_version}")
        except Exception as e:
            app.logger.info(f"⚠️ Failed to load VersionService: {e}")
            
    except Exception as e:
        app.logger.error(f"❌ Error checking version: {e}")
    
    app.logger.info("=" * 50)
    
    # Check each config file
    for config_file in config_files:
        file_path = os.path.join(base_dir, config_file)
        try:
            app.logger.info(f"DEBUG: Attempting to read {file_path}")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    try:
                        config_content = yaml.safe_load(f)
                        app.logger.info(f"DEBUG: Successfully read {config_file}")
                        app.logger.info(f"DEBUG: Content preview: {str(config_content)[:500]}...")
                    except Exception as e:
                        app.logger.error(f"DEBUG: Error parsing {config_file}: {str(e)}")
            else:
                app.logger.error(f"DEBUG: File not found: {file_path}")
        except Exception as e:
            app.logger.error(f"DEBUG: Error accessing {file_path}: {str(e)}")
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Simple test route
    @app.route('/api/test', methods=['GET', 'POST'])
    def test_route():
        """Test route to verify API is working"""
        if request.method == 'POST':
            data = request.get_json() or {}
            return jsonify({
                'message': 'POST request received',
                'data': data
            })
        return jsonify({
            'message': 'API is working!',
            'config_files': os.listdir('/app') if os.path.exists('/app') else [],
            'current_time': str(datetime.datetime.now())
        })
    

    
    # Add a simple debug endpoint to check config reading
    @app.route('/api/debug/config')
    def debug_config():
        """Debug endpoint to verify config reading"""
        from app.services.config import ConfigService
        config_service = ConfigService()
        
        try:
            # Get all available config files
            config_files = config_service.get_config_files()
            
            # Read each config file
            configs = {}
            for file_name in config_files:
                configs[file_name] = config_service.get_config(file_name)
            
            return jsonify({
                'success': True,
                'message': 'Config files read successfully',
                'config_files': config_files,
                'configs': configs,
                'base_url': request.base_url,
                'host': request.host
            })
        except Exception as e:
            app.logger.error(f"DEBUG: Error in debug endpoint: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error reading config files: {str(e)}',
                'base_url': request.base_url,
                'host': request.host
            }), 500
    
    # Import and register blueprints - including our proxy blueprint
    from app.api import config, jobs, libraries, images, check, workflow, schedules, preview, version, changes, poster_manager, settings_migration
    app.register_blueprint(config.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(libraries.bp)
    app.register_blueprint(images.bp)
    app.register_blueprint(check.bp)
    app.register_blueprint(workflow.bp)
    app.register_blueprint(schedules.bp)
    app.register_blueprint(preview.bp)
    app.register_blueprint(version.bp)
    app.register_blueprint(changes.bp)
    app.register_blueprint(poster_manager.bp)
    app.register_blueprint(settings_migration.bp)
    
    # Proxy blueprint removed - using direct API calls
    
    # Register the simplified process API
    from app.api import process_api
    app.register_blueprint(process_api.bp)
    
    # Initialize scheduler service
    try:
        from app.api.schedules import init_scheduler_service, shutdown_scheduler
        init_scheduler_service()
        app.logger.info("DEBUG: Scheduler service initialized")
        
        # Register shutdown handler
        import atexit
        atexit.register(shutdown_scheduler)
        
    except Exception as e:
        app.logger.error(f"DEBUG: Failed to initialize scheduler: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Aphrodite API is running',
            'version': '1.0',
            'proxy_removed': True
        })
        
    # Serve static images from the images directory
    @app.route('/images/<path:path>')
    def serve_images(path):
        # First check if we're running in a Docker container (look for /app directory)
        if os.path.exists('/app/images'):
            # We're in Docker, use Docker paths
            images_dir = '/app/images'
        else:
            # We're in development, use relative paths
            # From aphrodite-web/app/__init__.py, go up 2 levels to reach aphrodite/
            base_dir = Path(os.path.abspath(__file__)).parents[2]
            images_dir = os.path.join(base_dir, 'images')
        
        app.logger.info(f"Looking for image {path} in {images_dir}")
        
        if os.path.exists(os.path.join(images_dir, path)):
            return send_from_directory(images_dir, path)
        else:
            app.logger.error(f"Image not found: {path} in {images_dir}")
            return jsonify({
                'success': False,
                'message': f'Image not found: {path}'
            }), 404
    
    # API endpoint to serve the base URL to the frontend
    @app.route('/api/base-url')
    def base_url():
        host = request.headers.get('Host', 'localhost:5000')
        
        # Ensure we use the same port that the user is connecting with
        if os.path.exists('/app'):
            # In Docker environment
            if ':' in host:
                docker_host = host.split(':')[0]
                port = host.split(':')[1]  # Use the actual port from the request
            else:
                docker_host = host
                port = '2125'  # Default fallback
                
            # Use the actual request port to avoid CORS issues
            host = f"{docker_host}:{port}"
        
        protocol = request.headers.get('X-Forwarded-Proto', 'http')
        base_url = f'{protocol}://{host}'
        
        app.logger.info(f"DEBUG: Returning base URL: {base_url}")
        
        return jsonify({
            'baseUrl': base_url
        })
    
    # Serve the frontend's index.html for all other routes
    # This MUST be registered last to act as a catch-all
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Log the requested path for debugging
        app.logger.info(f"Serving frontend route: '{path}'")
        app.logger.info(f"Static folder: {app.static_folder}")
        app.logger.info(f"Static folder exists: {os.path.exists(app.static_folder)}")
        
        # Check if this is an API route - these should not be handled by the frontend
        if path.startswith('api/'):
            app.logger.info(f"API route requested: {path}")
            return jsonify({'error': 'API route not found'}), 404
        
        # Check if this is a static asset (has file extension and exists)
        if path != "" and '.' in path:
            static_file_path = os.path.join(app.static_folder, path)
            if os.path.exists(static_file_path):
                app.logger.info(f"Serving static file: {path}")
                return send_from_directory(app.static_folder, path)
            else:
                app.logger.warning(f"Static file not found: {path}")
                # Return 404 for missing static files
                return jsonify({'error': f'Static file not found: {path}'}), 404
        
        # For all other routes (SPA routes), serve index.html
        app.logger.info(f"Serving SPA route: '{path}'")
        index_path = os.path.join(app.static_folder, 'index.html')
        
        # Check if index.html exists
        if not os.path.exists(index_path):
            app.logger.error(f"index.html not found at {index_path}")
            return jsonify({'error': 'Frontend not built. Run npm run build in the frontend directory.'}), 404
            
        try:
            with open(index_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            app.logger.error(f"Error reading index.html: {e}")
            return jsonify({'error': 'Error reading frontend files'}), 500
                
        # Get the current host and protocol
        host = request.headers.get('Host', 'localhost:5000')
        # Check if we're running in Docker - if so, use the appropriate host
        if os.path.exists('/app'):
            # In Docker, we want to get the actual host that's being used by the client
            # This ensures we avoid CORS issues
            app.logger.info(f"DEBUG: Original host: {host}")
            
            # Extract the host part (without port)
            if ':' in host:
                docker_host = host.split(':')[0]
            else:
                docker_host = host
                
            # Get the port from the environment or use the actual request port
            # The key is to ensure frontend and backend use the same port
            port = request.headers.get('X-Forwarded-Port', host.split(':')[1] if ':' in host else '2125')
            
            app.logger.info(f"DEBUG: Docker host: {docker_host}, port: {port}")
            host = f"{docker_host}:{port}"
            app.logger.info(f"DEBUG: Using host: {host}")
            
        protocol = request.headers.get('X-Forwarded-Proto', 'http')
        base_url = f'{protocol}://{host}'
        app.logger.info(f"DEBUG: Injecting base URL: {base_url}")
        
        # Inject the base URL as a global variable
        script_tag = f"<script>window.APHRODITE_BASE_URL = '{base_url}';</script>"
        
        # Insert the script tag after the <head> tag
        pattern = re.compile(r'<head>')
        content = pattern.sub(f'<head>\n    {script_tag}', content)
        
        return content
    
    # Initialize scheduler service
    try:
        from app.api.schedules import init_scheduler_service, shutdown_scheduler
        init_scheduler_service()
        app.logger.info("DEBUG: Scheduler service initialized")
        
        # Register shutdown handler
        import atexit
        atexit.register(shutdown_scheduler)
        
    except Exception as e:
        app.logger.error(f"DEBUG: Failed to initialize scheduler: {e}")
    
    # Debug: Print all registered routes
    def debug_routes():
        app.logger.info("=== REGISTERED ROUTES ===")
        for rule in app.url_map.iter_rules():
            app.logger.info(f"Route: {rule.rule} -> {rule.endpoint} (methods: {rule.methods})")
        app.logger.info("=== END ROUTES ===")
    
    # Call debug routes function immediately
    debug_routes()
    
    return app
