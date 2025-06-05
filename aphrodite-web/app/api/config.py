from flask import Blueprint, jsonify, request
from app.services.config import ConfigService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('config', __name__, url_prefix='/api/config')
config_service = ConfigService()

@bp.route('/', methods=['GET'])
def get_all_configs():
    """Get a list of all available configuration files."""
    config_files = config_service.get_config_files()
    
    if not config_files:
        return jsonify({"error": "No configuration files found"}), 404
    
    return jsonify({"config_files": config_files})

@bp.route('/<file>', methods=['GET'])
def get_config(file):
    """Get the content of a specific configuration file."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"DEBUG: API received request for config file: {file}")
    
    # Extract request information for debugging
    headers = dict(request.headers)
    logger.info(f"DEBUG: Request headers: {headers}")
    logger.info(f"DEBUG: Request host: {request.host}")
    logger.info(f"DEBUG: Request remote addr: {request.remote_addr}")
    
    # Get config file content
    config = config_service.get_config(file)
    
    if config is None:
        logger.error(f"DEBUG: Configuration file '{file}' not found")
        return jsonify({"error": f"Configuration file '{file}' not found"}), 404
    
    # Log the config structure for debugging
    logger.info(f"DEBUG: Config structure: {type(config)}")
    if isinstance(config, dict) and 'api_keys' in config:
        logger.info(f"DEBUG: API keys present: {list(config['api_keys'].keys())}")
        for key in config['api_keys']:
            logger.info(f"DEBUG: API key '{key}' structure: {type(config['api_keys'][key])}")
    
    logger.info(f"DEBUG: Returning config for {file}")
    response = jsonify({"config": config})
    
    # Log the response for debugging
    logger.info(f"DEBUG: Response status: {response.status_code}")
    logger.info(f"DEBUG: Response headers: {dict(response.headers)}")
    
    return response

@bp.route('/<file>', methods=['PUT'])
def update_config(file):
    """Update the content of a specific configuration file."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    content = request.get_json().get('config')
    
    if content is None:
        return jsonify({"error": "Missing 'config' field in request"}), 400
    
    # Validate settings.yaml content
    if file == 'settings.yaml' and not config_service.validate_api_settings(content):
        return jsonify({"error": "Invalid API settings format"}), 400
    
    success = config_service.update_config(file, content)
    
    if not success:
        return jsonify({"error": f"Failed to update configuration file '{file}'"}), 500
    
    return jsonify({"message": f"Configuration file '{file}' updated successfully"})

@bp.route('/debug/migration', methods=['POST'])
def debug_migration():
    """Debug endpoint to manually trigger migration and check status"""
    try:
        # Get current database version
        current_version = config_service.settings_service.get_current_version()
        logger.info(f"DEBUG: Current database version: {current_version}")
        
        # Force check migration
        config_service._check_migration()
        
        # Get new version
        new_version = config_service.settings_service.get_current_version()
        logger.info(f"DEBUG: New database version: {new_version}")
        
        # Check what's in the database
        api_keys = config_service.settings_service.get_api_keys()
        
        return jsonify({
            "message": "Migration debug completed",
            "old_version": current_version,
            "new_version": new_version,
            "api_keys_in_db": list(api_keys.keys()) if api_keys else [],
            "migration_triggered": current_version != new_version
        })
        
    except Exception as e:
        logger.error(f"DEBUG: Error in debug migration: {e}")
        import traceback
        logger.error(f"DEBUG: Debug migration traceback: {traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
