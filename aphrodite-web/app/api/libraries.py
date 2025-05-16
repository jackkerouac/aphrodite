from flask import Blueprint, jsonify

bp = Blueprint('libraries', __name__, url_prefix='/api/libraries')

@bp.route('/', methods=['GET'])
def get_libraries():
    return jsonify({"message": "List of available libraries"})