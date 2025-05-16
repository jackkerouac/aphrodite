from flask import Blueprint, jsonify, send_file

bp = Blueprint('images', __name__, url_prefix='/api/images')

@bp.route('/original/<file>', methods=['GET'])
def get_original_image(file):
    return jsonify({"message": f"Original image for {file}"})

@bp.route('/modified/<file>', methods=['GET'])
def get_modified_image(file):
    return jsonify({"message": f"Modified image for {file}"})

@bp.route('/download/<file>', methods=['GET'])
def download_image(file):
    return jsonify({"message": f"Download image for {file}"})