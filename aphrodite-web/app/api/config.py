from flask import Blueprint, jsonify, request

bp = Blueprint('config', __name__, url_prefix='/api/config')

@bp.route('/', methods=['GET'])
def get_all_configs():
    return jsonify({"message": "List of all configurations"})

@bp.route('/<file>', methods=['GET'])
def get_config(file):
    return jsonify({"message": f"Configuration for {file}"})

@bp.route('/<file>', methods=['PUT'])
def update_config(file):
    return jsonify({"message": f"Updated configuration for {file}"})