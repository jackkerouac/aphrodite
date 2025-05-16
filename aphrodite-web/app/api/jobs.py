from flask import Blueprint, jsonify, request

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.route('/', methods=['GET'])
def get_all_jobs():
    return jsonify({"message": "List of all jobs"})

@bp.route('/<id>', methods=['GET'])
def get_job(id):
    return jsonify({"message": f"Job details for {id}"})

@bp.route('/<id>', methods=['DELETE'])
def delete_job(id):
    return jsonify({"message": f"Deleted job {id}"})