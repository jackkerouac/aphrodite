"""
API Proxy module to solve CORS issues between the frontend and backend
"""

from flask import Blueprint, request, jsonify, Response
import requests
import os
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('proxy', __name__, url_prefix='/api-proxy')

@bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(path):
    """Proxy API requests to avoid CORS issues"""
    logger.info(f"DEBUG: Proxying request to path: {path}")
    
    # Get the host from the request
    host = request.headers.get('Host', 'localhost:5000')
    logger.info(f"DEBUG: Request host: {host}")
    
    # Extract internal port for Docker
    internal_port = os.environ.get('WEB_PORT', '5000')
    logger.info(f"DEBUG: Internal port: {internal_port}")
    
    # Build the internal URL
    internal_url = f"http://localhost:{internal_port}/api/{path}"
    logger.info(f"DEBUG: Proxying to internal URL: {internal_url}")
    
    # Copy the request headers
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    # Forward the request to the internal API
    try:
        if request.method == 'GET':
            resp = requests.get(
                internal_url, 
                params=request.args,
                headers=headers,
                stream=True
            )
        elif request.method == 'POST':
            resp = requests.post(
                internal_url, 
                json=request.get_json() if request.is_json else None,
                data=request.form if not request.is_json else None,
                headers=headers,
                stream=True
            )
        elif request.method == 'PUT':
            resp = requests.put(
                internal_url, 
                json=request.get_json() if request.is_json else None,
                data=request.form if not request.is_json else None,
                headers=headers,
                stream=True
            )
        elif request.method == 'DELETE':
            resp = requests.delete(
                internal_url, 
                headers=headers,
                stream=True
            )
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        logger.info(f"DEBUG: Proxy response status: {resp.status_code}")
        
        # Create a generator function for the response content
        def generate():
            for chunk in resp.iter_content(chunk_size=1024):
                yield chunk
        
        # Stream the response back to the client without stream_with_context
        return Response(
            generate(),
            status=resp.status_code,
            headers=dict(resp.headers)
        )
        
    except Exception as e:
        logger.error(f"DEBUG: Proxy error: {str(e)}")
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500
