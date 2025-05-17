from flask import Blueprint, jsonify, request
from app.services.workflow_manager import (
    add_workflow, 
    get_workflow_status, 
    get_workflow,
    update_workflow_status,
    delete_workflow
)

bp = Blueprint('workflow', __name__, url_prefix='/api/workflow')

@bp.route('/', methods=['GET'])
def get_workflows():
    """Get all workflows"""
    workflow_status = get_workflow_status()
    
    return jsonify({
        'success': True,
        'active': list(workflow_status['active_workflows'].values()),
        'queue': workflow_status['queue'],
        'completed': workflow_status['completed']
    })

@bp.route('/<id>', methods=['GET'])
def get_workflow_by_id(id):
    """Get a workflow by ID"""
    workflow = get_workflow(id)
    
    if not workflow:
        return jsonify({
            'success': False,
            'message': f'Workflow {id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'workflow': workflow
    })

@bp.route('/library-batch', methods=['POST'])
def create_library_batch_workflow():
    """Create a new library batch workflow"""
    try:
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Basic validation
        if not data.get('libraryIds') or len(data.get('libraryIds')) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one library ID is required'
            }), 400
        
        if not data.get('badgeTypes') or len(data.get('badgeTypes')) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one badge type must be selected'
            }), 400
        
        # Create workflow
        workflow_id = add_workflow('library_batch', {
            'libraryIds': data.get('libraryIds'),
            'badgeTypes': data.get('badgeTypes'),
            'limit': data.get('limit'),
            'retries': data.get('retries', 3),
            'skipUpload': data.get('skipUpload', False),
            'cleanup': data.get('cleanup', False)
        })
        
        return jsonify({
            'success': True,
            'message': 'Workflow added to queue',
            'workflowId': workflow_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/<id>/cancel', methods=['POST'])
def cancel_workflow(id):
    """Cancel a workflow"""
    workflow = get_workflow(id)
    
    if not workflow:
        return jsonify({
            'success': False,
            'message': f'Workflow {id} not found'
        }), 404
    
    # Only allow cancelling queued workflows
    if workflow['status'] != 'Queued':
        return jsonify({
            'success': False,
            'message': f'Cannot cancel workflow with status {workflow["status"]}'
        }), 400
    
    # Update status to cancelled
    result = update_workflow_status(id, 'Cancelled')
    
    return jsonify({
        'success': result,
        'message': 'Workflow cancelled successfully' if result else 'Failed to cancel workflow'
    })


@bp.route('/<id>', methods=['DELETE'])
def delete_workflow_endpoint(id):
    """Delete a workflow"""
    workflow = get_workflow(id)
    
    if not workflow:
        return jsonify({
            'success': False,
            'message': f'Workflow {id} not found'
        }), 404
    
    # Delete the workflow
    result = delete_workflow(id)
    
    return jsonify({
        'success': result,
        'message': 'Workflow deleted successfully' if result else 'Failed to delete workflow'
    })
