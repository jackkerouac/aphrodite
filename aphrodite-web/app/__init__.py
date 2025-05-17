import os
from flask import Flask, send_from_directory, jsonify, request

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    
    # Enable CORS
    from flask_cors import CORS
    CORS(app)
    
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
    
    # Import and register blueprints
    from app.api import config, jobs, libraries, images, check, workflow
    app.register_blueprint(config.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(libraries.bp)
    app.register_blueprint(images.bp)
    app.register_blueprint(check.bp)
    app.register_blueprint(workflow.bp)
    
    # Register the simplified process API
    from app.api import process_api
    app.register_blueprint(process_api.bp)
    
    # Serve the frontend's index.html for all other routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app
