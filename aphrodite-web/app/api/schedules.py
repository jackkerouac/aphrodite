import logging
from flask import Blueprint, jsonify, request
from app.services.scheduler_service import SchedulerService
from app.services.schedule_config_service import ScheduleConfigService
import uuid

logger = logging.getLogger(__name__)

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

# Initialize services (will be properly initialized when the app starts)
scheduler_service = None
schedule_config_service = ScheduleConfigService()

def init_scheduler_service():
    """Initialize the scheduler service. Called from app initialization."""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService()
        scheduler_service.start()
        
        # Load existing schedules from config
        try:
            schedules = schedule_config_service.get_schedules()
            for schedule in schedules:
                if schedule.get('enabled', True):
                    try:
                        scheduler_service.add_schedule(schedule)
                        logger.info(f"Loaded schedule: {schedule.get('name', schedule.get('id'))}")
                    except Exception as e:
                        logger.error(f"Failed to load schedule {schedule.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Failed to load schedules from config: {e}")

def shutdown_scheduler():
    """Shutdown the scheduler service. Called during app shutdown."""
    global scheduler_service
    if scheduler_service:
        scheduler_service.stop()
        scheduler_service = None

@bp.route('/', methods=['GET'])
def get_schedules():
    """Get all schedules."""
    try:
        # Get schedules from config
        config_schedules = schedule_config_service.get_schedules()
        
        # Get runtime status from scheduler if available
        if scheduler_service and scheduler_service.is_running:
            runtime_schedules = scheduler_service.get_schedules()
            runtime_dict = {s['id']: s for s in runtime_schedules}
            
            # Merge config and runtime data
            for schedule in config_schedules:
                schedule_id = schedule.get('id')
                if schedule_id in runtime_dict:
                    runtime_info = runtime_dict[schedule_id]
                    schedule['next_run'] = runtime_info.get('next_run')
                    schedule['pending'] = runtime_info.get('pending', False)
                else:
                    schedule['next_run'] = None
                    schedule['pending'] = False
        
        return jsonify({
            'schedules': config_schedules,
            'scheduler_status': scheduler_service.get_status() if scheduler_service else {'running': False}
        })
    
    except Exception as e:
        logger.error(f"Error getting schedules: {e}")
        return jsonify({'error': f'Failed to get schedules: {str(e)}'}), 500

@bp.route('/', methods=['POST'])
def create_schedule():
    """Create a new schedule."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        schedule_data = request.get_json()
        
        # Generate ID if not provided
        if 'id' not in schedule_data:
            schedule_data['id'] = str(uuid.uuid4())
        
        # Add timestamps
        from datetime import datetime
        import pytz
        schedule_data['created_at'] = datetime.now(pytz.UTC).isoformat()
        schedule_data['last_run'] = None
        
        # Save to config
        schedule = schedule_config_service.add_schedule(schedule_data)
        
        # Add to scheduler if enabled and scheduler is running
        if schedule.get('enabled', True) and scheduler_service and scheduler_service.is_running:
            try:
                updated_schedule = scheduler_service.add_schedule(schedule)
                # Update config with next_run time
                schedule['next_run'] = updated_schedule.get('next_run')
                schedule_config_service.update_schedule(schedule['id'], schedule)
            except Exception as e:
                logger.error(f"Failed to add schedule to scheduler: {e}")
                # Schedule is saved in config but not active in scheduler
                schedule['next_run'] = None
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify({'error': f'Failed to create schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Get a specific schedule."""
    try:
        schedule = schedule_config_service.get_schedule(schedule_id)
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Add runtime information if scheduler is running
        if scheduler_service and scheduler_service.is_running:
            runtime_schedules = scheduler_service.get_schedules()
            for runtime_schedule in runtime_schedules:
                if runtime_schedule['id'] == schedule_id:
                    schedule['next_run'] = runtime_schedule.get('next_run')
                    schedule['pending'] = runtime_schedule.get('pending', False)
                    break
        
        return jsonify({'schedule': schedule})
    
    except Exception as e:
        logger.error(f"Error getting schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to get schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update an existing schedule."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        schedule_data = request.get_json()
        
        # Update in config
        schedule = schedule_config_service.update_schedule(schedule_id, schedule_data)
        
        # Update in scheduler if running
        if scheduler_service and scheduler_service.is_running:
            try:
                # Remove old schedule
                scheduler_service.remove_schedule(schedule_id)
                
                # Add updated schedule if enabled
                if schedule.get('enabled', True):
                    updated_schedule = scheduler_service.add_schedule(schedule)
                    schedule['next_run'] = updated_schedule.get('next_run')
                    schedule_config_service.update_schedule(schedule_id, schedule)
            except Exception as e:
                logger.error(f"Failed to update schedule in scheduler: {e}")
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'schedule': schedule
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to update schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a schedule."""
    try:
        # Remove from scheduler if running
        if scheduler_service and scheduler_service.is_running:
            scheduler_service.remove_schedule(schedule_id)
        
        # Remove from config
        schedule_config_service.remove_schedule(schedule_id)
        
        return jsonify({'message': 'Schedule deleted successfully'})
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to delete schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>/run', methods=['POST'])
def run_schedule(schedule_id):
    """Manually trigger a schedule to run now."""
    try:
        if not scheduler_service or not scheduler_service.is_running:
            return jsonify({'error': 'Scheduler is not running'}), 503
        
        success = scheduler_service.run_schedule_now(schedule_id)
        
        if success:
            return jsonify({'message': 'Schedule triggered successfully'})
        else:
            return jsonify({'error': 'Failed to trigger schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error triggering schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to trigger schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>/pause', methods=['POST'])
def pause_schedule(schedule_id):
    """Pause a schedule."""
    try:
        if not scheduler_service or not scheduler_service.is_running:
            return jsonify({'error': 'Scheduler is not running'}), 503
        
        success = scheduler_service.pause_schedule(schedule_id)
        
        if success:
            return jsonify({'message': 'Schedule paused successfully'})
        else:
            return jsonify({'error': 'Failed to pause schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error pausing schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to pause schedule: {str(e)}'}), 500

@bp.route('/<schedule_id>/resume', methods=['POST'])
def resume_schedule(schedule_id):
    """Resume a schedule."""
    try:
        if not scheduler_service or not scheduler_service.is_running:
            return jsonify({'error': 'Scheduler is not running'}), 503
        
        success = scheduler_service.resume_schedule(schedule_id)
        
        if success:
            return jsonify({'message': 'Schedule resumed successfully'})
        else:
            return jsonify({'error': 'Failed to resume schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error resuming schedule {schedule_id}: {e}")
        return jsonify({'error': f'Failed to resume schedule: {str(e)}'}), 500

@bp.route('/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status."""
    try:
        if scheduler_service:
            status = scheduler_service.get_status()
        else:
            status = {'running': False, 'scheduler_state': 'NOT_INITIALIZED', 'job_count': 0}
        
        return jsonify({'status': status})
    
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return jsonify({'error': f'Failed to get scheduler status: {str(e)}'}), 500

@bp.route('/history', methods=['GET'])
def get_job_history():
    """Get job execution history."""
    try:
        if not scheduler_service:
            return jsonify({'history': []})
        
        schedule_id = request.args.get('schedule_id')
        limit = request.args.get('limit', type=int)
        
        history = scheduler_service.get_job_history(schedule_id=schedule_id, limit=limit)
        
        return jsonify({'history': history})
    
    except Exception as e:
        logger.error(f"Error getting job history: {e}")
        return jsonify({'error': f'Failed to get job history: {str(e)}'}), 500

@bp.route('/patterns', methods=['GET'])
def get_cron_patterns():
    """Get common cron patterns."""
    try:
        patterns = schedule_config_service.get_common_cron_patterns()
        return jsonify({'patterns': patterns})
    
    except Exception as e:
        logger.error(f"Error getting cron patterns: {e}")
        return jsonify({'error': f'Failed to get cron patterns: {str(e)}'}), 500

@bp.route('/validate-cron', methods=['POST'])
def validate_cron():
    """Validate a cron expression."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        cron_expr = data.get('cron')
        
        if not cron_expr:
            return jsonify({'error': 'Missing cron expression'}), 400
        
        error = schedule_config_service.validate_cron_expression(cron_expr)
        
        if error:
            return jsonify({
                'valid': False,
                'error': error
            })
        else:
            description = schedule_config_service.cron_to_description(cron_expr)
            return jsonify({
                'valid': True,
                'description': description
            })
    
    except Exception as e:
        logger.error(f"Error validating cron expression: {e}")
        return jsonify({'error': f'Failed to validate cron expression: {str(e)}'}), 500

@bp.route('/jellyfin-libraries', methods=['GET'])
def get_jellyfin_libraries():
    """Get available Jellyfin libraries."""
    try:
        import requests
        from app.services.config import ConfigService
        
        config_service = ConfigService()
        config = config_service.get_config('settings.yaml')
        
        # Get Jellyfin configuration
        jellyfin_configs = config.get('api_keys', {}).get('Jellyfin', [])
        if not jellyfin_configs:
            return jsonify({'error': 'No Jellyfin configuration found'}), 404
        
        jellyfin_config = jellyfin_configs[0]  # Use first configuration
        url = jellyfin_config.get('url')
        api_key = jellyfin_config.get('api_key')
        user_id = jellyfin_config.get('user_id')
        
        if not all([url, api_key, user_id]):
            return jsonify({'error': 'Incomplete Jellyfin configuration'}), 400
        
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
        libraries = []
        
        for item in data.get('Items', []):
            library = {
                'id': item.get('Id'),
                'name': item.get('Name'),
                'type': item.get('CollectionType'),
                'path': item.get('Path', '')
            }
            libraries.append(library)
        
        return jsonify({
            'libraries': libraries,
            'server_url': url
        })
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to Jellyfin: {e}")
        return jsonify({'error': f'Failed to connect to Jellyfin: {str(e)}'}), 503
    except Exception as e:
        logger.error(f"Error getting Jellyfin libraries: {e}")
        return jsonify({'error': f'Failed to get Jellyfin libraries: {str(e)}'}), 500
