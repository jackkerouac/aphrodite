"""
Simple quotes API endpoint for dashboard feature.
"""
import json
import random
import os
from flask import Blueprint, jsonify

quotes_bp = Blueprint('quotes', __name__)

def get_quotes_file_path():
    """Get the path to quotes.json file."""
    # Check if running in Docker
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        return '/app/data/quotes.json'
    else:
        # Local development - go up from app/api to project root, then to data
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base_dir, 'data', 'quotes.json')

@quotes_bp.route('/random', methods=['GET'])
def get_random_quote():
    """Get a random quote from quotes.json file."""
    try:
        quotes_file = get_quotes_file_path()
        
        if not os.path.exists(quotes_file):
            return jsonify({
                'error': 'Quotes file not found',
                'quote': 'Welcome to Aphrodite - enhancing your media experience!'
            }), 200  # Return 200 with fallback quote
        
        with open(quotes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        quotes_list = data.get('quotes', [])
        if not quotes_list:
            return jsonify({
                'error': 'No quotes available',
                'quote': 'Welcome to Aphrodite - enhancing your media experience!'
            }), 200
        
        # Select random quote
        random_quote = random.choice(quotes_list)
        
        return jsonify({
            'quote': random_quote,
            'total_quotes': len(quotes_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to load quotes: {str(e)}',
            'quote': 'Welcome to Aphrodite - enhancing your media experience!'
        }), 200  # Always return 200 with fallback
