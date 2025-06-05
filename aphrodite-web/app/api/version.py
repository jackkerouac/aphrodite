from flask import Blueprint, jsonify, request
from app.services.version_service import VersionService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('version', __name__, url_prefix='/api/version')

@bp.route('/current', methods=['GET'])
def get_current_version():
    """Get the current version of Aphrodite."""
    try:
        version_service = VersionService()
        current_version = version_service.get_current_version()
        
        return jsonify({
            'success': True,
            'current_version': current_version
        })
        
    except Exception as e:
        logger.error(f"Error getting current version: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/check', methods=['GET'])
def check_for_updates():
    """Check for available updates."""
    try:
        # Check if forced refresh is requested
        force_check = request.args.get('force', 'false').lower() == 'true'
        
        version_service = VersionService()
        version_info = version_service.check_for_updates(force_check=force_check)
        
        return jsonify({
            'success': True,
            'data': version_info
        })
        
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/info', methods=['GET'])
def get_version_info():
    """Get complete version information including update status."""
    try:
        version_service = VersionService()
        version_info = version_service.get_version_info()
        
        return jsonify({
            'success': True,
            'data': version_info
        })
        
    except Exception as e:
        logger.error(f"Error getting version info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/update', methods=['POST'])
def update_current_version():
    """Update the current application version."""
    try:
        data = request.get_json()
        if not data or 'version' not in data:
            return jsonify({
                'success': False,
                'error': 'Version is required'
            }), 400
        
        version = data['version']
        version_service = VersionService()
        success = version_service.update_current_version(version)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Current version updated to {version}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update version'
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating current version: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
