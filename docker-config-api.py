from flask import Blueprint, jsonify, request
from app.services.config import ConfigService
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('config', __name__, url_prefix='/api/config')
config_service = ConfigService()

@bp.route('/', methods=['GET'])
def get_all_configs():
    """Get a list of all available configuration files."""
    try:
        config_files = config_service.get_config_files()
        
        if not config_files:
            logger.warning("No configuration files found")
            return jsonify({"error": "No configuration files found"}), 404
        
        # Check write permissions for each file
        writable_status = {}
        for file in config_files:
            writable_status[file] = config_service.is_config_writable(file)
        
        return jsonify({
            "config_files": config_files,
            "writable_status": writable_status
        })
    except Exception as e:
        logger.error(f"Error in get_all_configs: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@bp.route('/<file>', methods=['GET'])
def get_config(file):
    """Get the content of a specific configuration file."""
    try:
        config = config_service.get_config(file)
        
        if config is None:
            logger.warning(f"Configuration file '{file}' not found")
            return jsonify({"error": f"Configuration file '{file}' not found"}), 404
        
        # Check if file is writable
        writable = config_service.is_config_writable(file)
        
        return jsonify({
            "config": config,
            "writable": writable
        })
    except Exception as e:
        logger.error(f"Error in get_config for {file}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@bp.route('/<file>', methods=['PUT'])
def update_config(file):
    """Update the content of a specific configuration file."""
    try:
        if not request.is_json:
            logger.warning("Request must be JSON")
            return jsonify({"error": "Request must be JSON"}), 400
        
        content = request.get_json().get('config')
        
        if content is None:
            logger.warning("Missing 'config' field in request")
            return jsonify({"error": "Missing 'config' field in request"}), 400
        
        # Debug the content
        logger.debug(f"Received content for {file}: {content}")
        
        # Check if file is writable
        if not config_service.is_config_writable(file):
            error_msg = f"Configuration file '{file}' is not writable. Check permissions."
            logger.error(error_msg)
            return jsonify({
                "error": error_msg,
                "dockerHelp": "Add this to your docker-compose.yml:\n- ./your_local_path/{file}:/app/{file}",
                "permissionError": True
            }), 403
        
        # Validate settings.yaml content
        if file == 'settings.yaml':
            if not config_service.validate_api_settings(content):
                logger.warning("Invalid API settings format")
                return jsonify({"error": "Invalid API settings format"}), 400
        
        logger.debug(f"About to update config file {file}")
        success = config_service.update_config(file, content)
        
        if not success:
            logger.error(f"Failed to update configuration file '{file}'")
            return jsonify({"error": f"Failed to update configuration file '{file}'"}), 500
        
        logger.info(f"Configuration file '{file}' updated successfully")
        return jsonify({"message": f"Configuration file '{file}' updated successfully"})
    except Exception as e:
        logger.error(f"Error in update_config for {file}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
