import os
import re
import datetime
from flask import Flask, send_from_directory, jsonify, request, url_for, Response, stream_with_context
from pathlib import Path
import logging
import urllib.parse
import requests
import yaml
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application"""
    # Set up logging to be more verbose
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    
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
    
    # Add a proxy route to fix CORS issues for frontend
    @app.route('/api-proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_api(path):
        """Proxy API requests to avoid CORS issues"""
        app.logger.info(f"DEBUG: Proxying request to path: {path}")
        
        # Get the host from the request
        host = request.headers.get('Host', 'localhost:5000')
        app.logger.info(f"DEBUG: Request host: {host}")
        
        # Extract internal port for Docker
        internal_port = os.environ.get('WEB_PORT', '5000')
        app.logger.info(f"DEBUG: Internal port: {internal_port}")
        
        # Build the internal URL
        internal_url = f"http://localhost:{internal_port}/api/{path}"
        app.logger.info(f"DEBUG: Proxying to internal URL: {internal_url}")
        
        # Copy the request headers
        headers = {key: value for key, value in request.headers if key != 'Host'}
        
        # Forward the request to the internal API
        try:
            if request.method == 'GET':
                resp = requests.get(
                    internal_url, 
                    params=request.args,
                    headers=headers,
                    stream=True
                )
            elif request.method == 'POST':
                resp = requests.post(
                    internal_url, 
                    json=request.get_json() if request.is_json else None,
                    data=request.form if not request.is_json else None,
                    headers=headers,
                    stream=True
                )
            elif request.method == 'PUT':
                resp = requests.put(
                    internal_url, 
                    json=request.get_json() if request.is_json else None,
                    data=request.form if not request.is_json else None,
                    headers=headers,
                    stream=True
                )
            elif request.method == 'DELETE':
                resp = requests.delete(
                    internal_url, 
                    headers=headers,
                    stream=True
                )
            else:
                return jsonify({"error": "Method not supported"}), 405
            
            app.logger.info(f"DEBUG: Proxy response status: {resp.status_code}")
            
            # Create a generator function for the response content
            def generate():
                for chunk in resp.iter_content(chunk_size=1024):
                    yield chunk
            
            # Stream the response back to the client without stream_with_context
            return Response(
                generate(),
                status=resp.status_code,
                headers=dict(resp.headers)
            )
            
        except Exception as e:
            app.logger.error(f"DEBUG: Proxy error: {str(e)}")
            return jsonify({"error": f"Proxy error: {str(e)}"}), 500
    
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
    from app.api import config, jobs, libraries, images, check, workflow, schedules
    app.register_blueprint(config.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(libraries.bp)
    app.register_blueprint(images.bp)
    app.register_blueprint(check.bp)
    app.register_blueprint(workflow.bp)
    app.register_blueprint(schedules.bp)
    
    # Try to register the proxy blueprint if it exists
    try:
        from app.api import proxy
        app.register_blueprint(proxy.bp)
        app.logger.info("DEBUG: Registered proxy blueprint")
    except ImportError:
        app.logger.warning("DEBUG: Proxy blueprint not found, skipping")
    
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
        return jsonify({'status': 'ok'})
        
    # Serve static images from the images directory
    @app.route('/images/<path:path>')
    def serve_images(path):
        # First check if we're running in a Docker container (look for /app directory)
        if os.path.exists('/app/images'):
            # We're in Docker, use Docker paths
            images_dir = '/app/images'
        else:
            # We're in development, use relative paths
            base_dir = Path(os.path.abspath(__file__)).parents[3]
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
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            # Inject the base URL into the index.html
            index_path = os.path.join(app.static_folder, 'index.html')
            with open(index_path, 'r') as file:
                content = file.read()
                
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
    
    return app
