import os
import yaml
from flask import Blueprint, jsonify
from pathlib import Path

bp = Blueprint('changes', __name__, url_prefix='/api/changes')

@bp.route('/', methods=['GET'])
def get_changes():
    """Get the changes from changes.yml file"""
    try:
        # Determine base directory (Docker vs. development)
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            base_dir = '/app'
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        changes_file = os.path.join(base_dir, 'changes.yml')
        
        if not os.path.exists(changes_file):
            return jsonify({
                'success': False,
                'message': f'Changes file not found at {changes_file}',
                'changes': []
            }), 404
        
        with open(changes_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Data is already in newest-first order from the YAML file
        changes = data.get('changes', [])
        
        return jsonify({
            'success': True,
            'changes': changes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading changes file: {str(e)}',
            'changes': []
        }), 500
