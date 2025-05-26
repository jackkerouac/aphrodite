from flask import Blueprint, jsonify, send_file, request, abort
import os
from app.services.image_service import get_image_path, get_image_as_base64, get_image_pairs

bp = Blueprint('images', __name__, url_prefix='/api/images')

@bp.route('/list', methods=['GET'])
def list_images():
    """Get a paginated list of image pairs (original and modified)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    image_data = get_image_pairs(page, per_page)
    
    return jsonify({
        'success': True,
        'images': image_data['images'],
        'total': image_data['total'],
        'page': image_data['page'],
        'per_page': image_data['per_page'],
        'total_pages': image_data['total_pages']
    })

@bp.route('/original/<file>', methods=['GET'])
def get_original_image(file):
    """Get an original poster image"""
    try:
        image_path = get_image_path('original', file)
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'Image not found: {file}'
            }), 404
        
        return send_file(image_path)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/modified/<file>', methods=['GET'])
def get_modified_image(file):
    """Get a modified poster image"""
    try:
        image_path = get_image_path('modified', file)
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'Image not found: {file}'
            }), 404
        
        return send_file(image_path)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/download/<file>', methods=['GET'])
def download_image(file):
    """Download a modified poster image"""
    try:
        image_path = get_image_path('modified', file)
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'Image not found: {file}'
            }), 404
        
        # Set Content-Disposition header to trigger download
        return send_file(
            image_path,
            as_attachment=True,
            download_name=file
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/base64/<type>/<file>', methods=['GET'])
def get_image_base64(type, file):
    """Get an image as a base64 string for embedding in HTML"""
    if type not in ['original', 'modified']:
        return jsonify({
            'success': False,
            'message': f'Invalid image type: {type}'
        }), 400
    
    try:
        image_path = get_image_path(type, file)
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'Image not found: {file}'
            }), 404
        
        base64_data = get_image_as_base64(image_path)
        if not base64_data:
            return jsonify({
                'success': False,
                'message': 'Failed to convert image to base64'
            }), 500
        
        return jsonify({
            'success': True,
            'base64': base64_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/serve', methods=['GET'])
def serve_image():
    """Serve an image from a given path"""
    path = request.args.get('path')
    if not path:
        return jsonify({
            'success': False,
            'message': 'No path provided'
        }), 400
    
    # Security check: ensure path is within allowed directories
    if not (path.startswith(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'posters'))):
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        }), 403
    
    if not os.path.exists(path):
        return jsonify({
            'success': False,
            'message': 'Image not found'
        }), 404
    
    try:
        return send_file(path)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
