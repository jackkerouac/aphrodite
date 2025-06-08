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
    # Serve built frontend files under /static to prevent clashes with
    # application routes
    app = Flask(
        __name__,
        static_folder='../static',
        static_url_path='/static'
    )
    
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
        logger.info("Starting blueprint imports...")
        from app.api import config, jobs, jobs_extended, libraries, images, check, workflow, process_api, preview, version, poster_manager, review_sources
        logger.info("Basic blueprints imported successfully")
        
        # Import database analytics separately to catch any errors
        try:
            from app.api import database_analytics
            logger.info("✅ database_analytics imported successfully")
        except Exception as db_import_error:
            logger.error(f"❌ Failed to import database_analytics: {db_import_error}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Continue without database_analytics
            database_analytics = None
        
        # Import extended database analytics
        database_analytics_extended = None
        try:
            from app.api import database_analytics_extended
            logger.info("✅ database_analytics_extended imported successfully")
            logger.info(f"✅ Extended module object: {database_analytics_extended}")
            logger.info(f"✅ Extended blueprint: {database_analytics_extended.bp}")
        except Exception as db_ext_import_error:
            logger.error(f"❌ Failed to import database_analytics_extended: {db_ext_import_error}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            database_analytics_extended = None
        
        # Import database operations
        database_operations = None
        try:
            from app.api import database_operations
            logger.info("✅ database_operations imported successfully")
        except Exception as db_ops_import_error:
            logger.error(f"❌ Failed to import database_operations: {db_ops_import_error}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            database_operations = None
        
        app.register_blueprint(config.bp)
        app.register_blueprint(jobs.bp)
        app.register_blueprint(jobs_extended.bp)
        app.register_blueprint(libraries.bp)
        app.register_blueprint(images.bp)
        app.register_blueprint(check.bp)
        app.register_blueprint(workflow.bp)
        app.register_blueprint(process_api.bp)
        app.register_blueprint(preview.bp)
        app.register_blueprint(version.bp)
        app.register_blueprint(poster_manager.bp)
        app.register_blueprint(review_sources.bp)
        
        # Register database analytics blueprint with explicit logging
        if database_analytics:
            logger.info("Registering database_analytics blueprint...")
            app.register_blueprint(database_analytics.bp)
            logger.info("✅ Database analytics blueprint registered successfully!")
        else:
            logger.warning("⚠️ Skipping database analytics blueprint due to import error")
        
        # Register extended database analytics blueprint
        # FORCE EXTENDED BLUEPRINT REGISTRATION - Phase B Fix
        logger.info(f"🔍 CHECKING EXTENDED BLUEPRINT: database_analytics_extended = {database_analytics_extended}")
        if database_analytics_extended:
            logger.info("🔄 REGISTERING database_analytics_extended blueprint...")
            try:
                app.register_blueprint(database_analytics_extended.bp)
                logger.info("✅ EXTENDED DATABASE ANALYTICS BLUEPRINT REGISTERED SUCCESSFULLY!")
                
                # Verify registration by checking routes
                extended_routes = []
                for rule in app.url_map.iter_rules():
                    if rule.rule.startswith('/api/database/') and ('comprehensive-report' in rule.rule or 'processed-items' in rule.rule or 'libraries' in rule.rule):
                        extended_routes.append(rule.rule)
                logger.info(f"✅ VERIFIED EXTENDED ROUTES: {extended_routes}")
                
            except Exception as reg_error:
                logger.error(f"❌ FAILED TO REGISTER EXTENDED BLUEPRINT: {reg_error}")
                import traceback
                logger.error(f"Registration traceback: {traceback.format_exc()}")
        else:
            logger.error("❌ EXTENDED BLUEPRINT IS NONE - CANNOT REGISTER")
            # Try to re-import
            try:
                logger.info("🔄 ATTEMPTING RE-IMPORT...")
                from app.api import database_analytics_extended as db_ext_reimport
                if db_ext_reimport:
                    logger.info("✅ RE-IMPORT SUCCESSFUL - REGISTERING...")
                    app.register_blueprint(db_ext_reimport.bp)
                    logger.info("✅ EXTENDED BLUEPRINT REGISTERED AFTER RE-IMPORT!")
                else:
                    logger.error("❌ RE-IMPORT ALSO RETURNED NONE")
            except Exception as reimport_error:
                logger.error(f"❌ RE-IMPORT FAILED: {reimport_error}")
        
        # Register database operations blueprint
        if database_operations:
            logger.info("Registering database_operations blueprint...")
            try:
                app.register_blueprint(database_operations.database_operations)
                logger.info("✅ Database operations blueprint registered successfully!")
            except Exception as reg_error:
                logger.error(f"❌ Failed to register database operations blueprint: {reg_error}")
        else:
            logger.warning("⚠️ Skipping database operations blueprint due to import error")
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
