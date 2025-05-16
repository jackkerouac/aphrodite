import os
from flask import Flask, send_from_directory
from flask_cors import CORS

def create_app():
    # Set the static folder to the frontend build directory
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    CORS(app)

    # Import and register blueprints
    from app.api import config, jobs, libraries, images, check
    app.register_blueprint(config.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(libraries.bp)
    app.register_blueprint(images.bp)
    app.register_blueprint(check.bp)

    # Serve the frontend's index.html for all other routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app