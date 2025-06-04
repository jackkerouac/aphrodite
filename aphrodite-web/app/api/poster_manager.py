from flask import Blueprint, jsonify, request
import sys
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from aphrodite_helpers.check_jellyfin_connection import load_settings
    from app.api.jellyfin_helpers import get_library_items_with_posters
    from app.services.job import JobService
    logger.info("Successfully imported dependencies for poster_manager")
except ImportError as e:
    logger.error(f"Import error in poster_manager: {e}")
    raise

# Import modular route handlers
from .poster_routes.library_routes import register_library_routes
from .poster_routes.item_routes import register_item_routes
from .poster_routes.bulk_routes import register_bulk_routes

bp = Blueprint('poster_manager', __name__, url_prefix='/api/poster-manager')
logger.info("Poster manager blueprint created")

# Test route to verify the blueprint is working
@bp.route('/test', methods=['GET'])
def test_poster_manager():
    """Test route to verify poster manager API is working"""
    return jsonify({
        'success': True,
        'message': 'Poster Manager API is working',
        'blueprint': 'poster_manager'
    })

@bp.route('/test-services', methods=['GET'])
def test_services():
    """Test route to verify services can be imported"""
    results = {
        'external_poster_service': False,
        'poster_replacement_service': False,
        'errors': []
    }
    
    # Test ExternalPosterService
    try:
        from app.services.external_poster_service import ExternalPosterService
        service = ExternalPosterService()
        results['external_poster_service'] = True
        logger.info("Successfully imported and created ExternalPosterService")
    except Exception as e:
        error_msg = f"ExternalPosterService error: {str(e)}"
        results['errors'].append(error_msg)
        logger.error(error_msg)
    
    # Test PosterReplacementService
    try:
        from app.services.poster_replacement_service import PosterReplacementService
        service = PosterReplacementService()
        results['poster_replacement_service'] = True
        logger.info("Successfully imported and created PosterReplacementService")
    except Exception as e:
        error_msg = f"PosterReplacementService error: {str(e)}"
        results['errors'].append(error_msg)
        logger.error(error_msg)
    
    return jsonify({
        'success': len(results['errors']) == 0,
        'results': results
    })

# Register modular routes
register_library_routes(bp)
register_item_routes(bp)
register_bulk_routes(bp)
