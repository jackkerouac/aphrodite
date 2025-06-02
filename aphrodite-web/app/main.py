from flask import Flask, send_from_directory, jsonify, request
import os
import logging
from waitress import serve

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../static', static_url_path='/')
    
    # Enable CORS for all domains and routes
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    logger.info("Created Flask app with CORS enabled for all origins")
    
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
        return jsonify({'message': 'API is working!'})
    
    # Simple health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint"""
        return "Aphrodite Web is healthy!"
    
    # Debugging route to show environment details
    @app.route('/debug', methods=['GET'])
    def debug_info():
        """Debug route to show environment details"""
        static_folder = app.static_folder
        static_files = []
        if os.path.exists(static_folder):
            static_files = os.listdir(static_folder)
        
        return jsonify({
            'static_folder': static_folder,
            'static_folder_exists': os.path.exists(static_folder),
            'static_files': static_files,
            'cwd': os.getcwd(),
            'static_url_path': app.static_url_path
        })
    
    # Explicitly set CORS headers for config API
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response
    
    # Import and register blueprints
    try:
        from app.api import config, jobs, libraries, images, check, workflow, process_api, preview
        app.register_blueprint(config.bp)
        app.register_blueprint(jobs.bp)
        app.register_blueprint(libraries.bp)
        app.register_blueprint(images.bp)
        app.register_blueprint(check.bp)
        app.register_blueprint(workflow.bp)
        app.register_blueprint(process_api.bp)
        app.register_blueprint(preview.bp)
    except Exception as e:
        logger.error(f"Error registering blueprints: {e}")
        # Add a fallback route if blueprints fail to load
        @app.route('/error')
        def error_info():
            return f"Error loading application components: {str(e)}"
    
    # Serve static images (for badges, etc.)
    @app.route('/images/<path:filename>')
    def serve_images(filename):
        """Serve badge images and other static assets"""
        # Determine the base directory (same logic as ConfigService)
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            base_dir = '/app'
        else:
            # For local development
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        images_dir = os.path.join(base_dir, 'images')
        file_path = os.path.join(images_dir, filename)
        
        # Security check: ensure path is within images directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(images_dir)):
            logger.warning(f"Attempted to access file outside images directory: {filename}")
            return jsonify({'error': 'Invalid path'}), 403
        
        if os.path.exists(file_path):
            directory = os.path.dirname(file_path)
            basename = os.path.basename(file_path)
            return send_from_directory(directory, basename)
        else:
            logger.warning(f"Image not found: {file_path}")
            return jsonify({'error': 'Image not found'}), 404
    
    # Serve the frontend's index.html for all other routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            # Check if index.html exists
            index_path = os.path.join(app.static_folder, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(app.static_folder, 'index.html')
            else:
                return f"Frontend not found. Static folder: {app.static_folder}, Path requested: {path}"
    
    return app

if __name__ == '__main__':
    # Print startup information
    print("=" * 50)
    print("Aphrodite Web Wrapper")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print("Starting server on http://0.0.0.0:5000")
    print("=" * 50)
    
    app = create_app()
    
    # Use Waitress instead of Flask's development server
    logger.info("Starting Waitress production server...")
    serve(app, host='0.0.0.0', port=5000)
