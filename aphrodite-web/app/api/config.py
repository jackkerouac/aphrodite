from flask import Blueprint, jsonify, request
from app.services.config import ConfigService

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
    config = config_service.get_config(file)
    
    if config is None:
        return jsonify({"error": f"Configuration file '{file}' not found"}), 404
    
    return jsonify({"config": config})

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
