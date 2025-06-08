"""
Extended jobs API to include scheduled workflow tracking and fix library ID issue
"""
from flask import Blueprint, jsonify, request
import json
import os
import time
import requests
from app.services.job import JobService
from app.services.workflow_manager import get_workflow_status, get_workflow

bp = Blueprint('jobs_extended', __name__, url_prefix='/api/jobs')

def get_library_name_to_id_mapping():
    """Get mapping of library names to IDs from Jellyfin"""
    try:
        from app.services.config import ConfigService
        
        config_service = ConfigService()
        config = config_service.get_config('settings.yaml')
        
        # Get Jellyfin configuration
        jellyfin_configs = config.get('api_keys', {}).get('Jellyfin', [])
        if not jellyfin_configs:
            return {}
        
        jellyfin_config = jellyfin_configs[0]  # Use first configuration
        url = jellyfin_config.get('url')
        api_key = jellyfin_config.get('api_key')
        user_id = jellyfin_config.get('user_id')
        
        if not all([url, api_key, user_id]):
            return {}
        
        # Fetch libraries from Jellyfin
        headers = {
            'X-Emby-Authorization': f'MediaBrowser Client="Aphrodite", Device="Server", DeviceId="aphrodite-server", Version="1.0", Token="{api_key}"'
        }
        
        # Get user's library folders
        libraries_url = f"{url.rstrip('/')}/Users/{user_id}/Items"
        params = {
            'ParentId': '',
            'IncludeItemTypes': 'CollectionFolder',
            'Recursive': False
        }
        
        response = requests.get(libraries_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        name_to_id = {}
        
        for item in data.get('Items', []):
            name = item.get('Name')
            lib_id = item.get('Id')
            if name and lib_id:
                name_to_id[name] = lib_id
        
        return name_to_id
        
    except Exception as e:
        print(f"Error getting library mapping: {e}")
        return {}

@bp.route('/active-jobs-with-workflows', methods=['GET'])
def get_active_jobs_with_workflows():
    """Get both active badge jobs and active scheduled workflows"""
    try:
        from app.api.jobs import get_active_badge_jobs as get_badge_jobs_func
        
        # Get existing badge jobs response
        badge_response = get_badge_jobs_func()
        if hasattr(badge_response, 'get_json'):
            badge_data = badge_response.get_json()
        elif isinstance(badge_response, tuple):
            badge_data = badge_response[0].get_json() if hasattr(badge_response[0], 'get_json') else badge_response[0]
        else:
            badge_data = badge_response
        
        # Get workflow data
        workflow_data = get_workflow_status()
        
        # Get library name to ID mapping for proper display
        library_mapping = get_library_name_to_id_mapping()
        
        # Convert active workflows to job format
        active_workflows = []
        
        # Process active workflows
        for workflow_id, workflow_info in workflow_data.get('active_workflows', {}).items():
            workflow_type = workflow_info.get('type', 'unknown')
            options = workflow_info.get('options', {})
            library_ids = options.get('libraryIds', [])
            
            # Convert library names to proper display format
            library_display = []
            for lib in library_ids:
                if lib in library_mapping.values():
                    # Already an ID, get the name
                    for name, lib_id in library_mapping.items():
                        if lib_id == lib:
                            library_display.append(f"{name} ({lib_id[:8]}...)")
                            break
                    else:
                        library_display.append(f"Library {lib_id[:8]}...")
                elif lib in library_mapping:
                    # It's a name, show name and ID
                    lib_id = library_mapping[lib]
                    library_display.append(f"{lib} ({lib_id[:8]}...)")
                else:
                    # Unknown library
                    library_display.append(lib)
            
            # Create job-like entry for workflow
            workflow_job = {
                'workflow_id': workflow_id,
                'type': 'scheduled_workflow',
                'workflow_type': workflow_type,
                'status': workflow_info.get('status', 'Running'),
                'library_ids': library_ids,
                'badge_types': options.get('badgeTypes', []),
                'created_at': workflow_info.get('created_at'),
                'started_at': workflow_info.get('start_time'),
                'name': f"Scheduled: {', '.join(library_display) if library_display else 'Unknown Libraries'}"
            }
            
            active_workflows.append(workflow_job)
        
        # Process queued workflows  
        for workflow_info in workflow_data.get('queue', []):
            workflow_id = workflow_info.get('id')
            workflow_type = workflow_info.get('type', 'unknown')
            options = workflow_info.get('options', {})
            library_ids = options.get('libraryIds', [])
            
            # Convert library names to proper display format
            library_display = []
            for lib in library_ids:
                if lib in library_mapping.values():
                    # Already an ID, get the name
                    for name, lib_id in library_mapping.items():
                        if lib_id == lib:
                            library_display.append(f"{name} ({lib_id[:8]}...)")
                            break
                    else:
                        library_display.append(f"Library {lib_id[:8]}...")
                elif lib in library_mapping:
                    # It's a name, show name and ID
                    lib_id = library_mapping[lib]
                    library_display.append(f"{lib} ({lib_id[:8]}...)")
                else:
                    # Unknown library
                    library_display.append(lib)
            
            workflow_job = {
                'workflow_id': workflow_id,
                'type': 'scheduled_workflow',
                'workflow_type': workflow_type,
                'status': 'Queued',
                'library_ids': library_ids,
                'badge_types': options.get('badgeTypes', []),
                'created_at': workflow_info.get('created_at'),
                'queue_position': workflow_info.get('queue_position', 0),
                'name': f"Queued: {', '.join(library_display) if library_display else 'Unknown Libraries'}"
            }
            
            active_workflows.append(workflow_job)
        
        # Combine badge jobs and workflows
        combined_response = {
            'success': True,
            'active_batches': badge_data.get('active_batches', []),
            'active_workflows': active_workflows,
            'total_active_jobs': badge_data.get('total_active_jobs', 0),
            'total_active_workflows': len(active_workflows)
        }
        
        return jsonify(combined_response)
        
    except Exception as e:
        import traceback
        print(f"Error getting active jobs with workflows: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error getting active jobs with workflows: {str(e)}',
            'active_batches': [],
            'active_workflows': [],
            'total_active_jobs': 0,
            'total_active_workflows': 0
        }), 500

@bp.route('/workflow-details/<workflow_id>', methods=['GET'])
def get_workflow_details(workflow_id):
    """Get detailed information about a specific workflow"""
    try:
        workflow = get_workflow(workflow_id)
        
        if not workflow:
            return jsonify({
                'success': False,
                'message': f'Workflow {workflow_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'workflow': workflow
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting workflow details: {str(e)}'
        }), 500
