from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Import and register blueprints
    from app.api import config, jobs, libraries, images
    app.register_blueprint(config.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(libraries.bp)
    app.register_blueprint(images.bp)
    
    return app