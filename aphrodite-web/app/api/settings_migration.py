from flask import Blueprint, jsonify, request
import os
import yaml
import logging
from pathlib import Path

bp = Blueprint('settings_migration', __name__, url_prefix='/api/settings/migration')
logger = logging.getLogger(__name__)

def get_paths():
    """Get the appropriate paths for the current environment"""
    # Check for Docker environment
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        base_dir = Path('/app')
        db_path = '/app/data/aphrodite.db'
    else:
        # For development environment, go up from aphrodite-web/app/api to aphrodite/
        base_dir = Path(os.path.abspath(__file__)).parents[3]
        db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
    
    return base_dir, db_path

@bp.route('/status', methods=['GET'])
def migration_status():
    """Check if settings migration is needed"""
    try:
        base_dir, db_path = get_paths()
        
        # Check if settings.yaml exists
        yaml_exists = os.path.exists(base_dir / 'settings.yaml')
        
        # Check if database already has settings
        try:
            # Import SettingsService
            import sys
            sys.path.append(str(base_dir))
            from app.services.settings_service import SettingsService
            
            settings_service = SettingsService(db_path)
            db_version = settings_service.get_current_version()
        except Exception as e:
            logger.error(f"Error checking database version: {e}")
            db_version = 0
        
        # Migration is needed if YAML exists but database is empty
        migration_needed = yaml_exists and db_version == 0
        
        # Check if database file exists
        db_exists = os.path.exists(db_path)
        
        logger.info(f"Migration status check: YAML exists: {yaml_exists}, DB version: {db_version}, Migration needed: {migration_needed}")
        
        return jsonify({
            'migrationNeeded': migration_needed,
            'yamlExists': yaml_exists,
            'databaseVersion': db_version,
            'databaseExists': db_exists,
            'basePath': str(base_dir),
            'databasePath': db_path
        })
    
    except Exception as e:
        logger.error(f"Error in migration status check: {e}")
        return jsonify({
            'error': f'Error checking migration status: {str(e)}'
        }), 500

@bp.route('/start', methods=['POST'])
def start_migration():
    """Start the migration process"""
    try:
        base_dir, db_path = get_paths()
        
        # Check if settings.yaml exists
        yaml_path = base_dir / 'settings.yaml'
        if not os.path.exists(yaml_path):
            return jsonify({
                'success': False,
                'message': 'settings.yaml not found'
            }), 404
        
        # Import required modules
        import sys
        sys.path.append(str(base_dir))
        from app.services.settings_service import SettingsService
        
        # Check if database already has settings
        settings_service = SettingsService(db_path)
        db_version = settings_service.get_current_version()
        
        if db_version > 0:
            return jsonify({
                'success': False,
                'message': 'Database already has settings'
            }), 400
        
        # Import and run migration
        try:
            from tools.migrate_settings import migrate_yaml_to_sqlite
            
            logger.info(f"Starting migration from {base_dir} to {db_path}")
            
            # Migrate settings (non-interactive mode)
            success = migrate_yaml_to_sqlite(
                str(base_dir),
                db_path,
                interactive=False
            )
            
            if success:
                logger.info("Migration completed successfully")
                return jsonify({
                    'success': True,
                    'message': 'Migration completed successfully'
                })
            else:
                logger.error("Migration failed")
                return jsonify({
                    'success': False,
                    'message': 'Migration failed'
                }), 500
                
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return jsonify({
                'success': False,
                'message': f'Error during migration: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in start_migration: {e}")
        return jsonify({
            'success': False,
            'message': f'Error starting migration: {str(e)}'
        }), 500

@bp.route('/finalize', methods=['POST'])
def finalize_migration():
    """Finalize the migration process by creating backups"""
    try:
        base_dir, db_path = get_paths()
        
        # Create backup directory
        backup_dir = base_dir / 'backups' / 'settings'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backups of YAML files
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_files = []
        
        # Backup main settings
        yaml_path = base_dir / 'settings.yaml'
        if os.path.exists(yaml_path):
            backup_name = f'settings.yaml.{timestamp}.bak'
            backup_path = backup_dir / backup_name
            shutil.copy2(yaml_path, backup_path)
            backup_files.append(str(backup_path))
            logger.info(f"Created backup: {backup_path}")
        
        # Backup badge settings
        badge_files = [
            'badge_settings_audio.yml',
            'badge_settings_resolution.yml', 
            'badge_settings_review.yml',
            'badge_settings_awards.yml'
        ]
        
        for badge_file in badge_files:
            badge_path = base_dir / badge_file
            if os.path.exists(badge_path):
                backup_name = f'{badge_file}.{timestamp}.bak'
                backup_path = backup_dir / backup_name
                shutil.copy2(badge_path, backup_path)
                backup_files.append(str(backup_path))
                logger.info(f"Created backup: {backup_path}")
        
        logger.info(f"Migration finalized with {len(backup_files)} backup files")
        
        return jsonify({
            'success': True,
            'message': 'Migration finalized successfully',
            'backupDir': str(backup_dir),
            'backupFiles': backup_files,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error finalizing migration: {e}")
        return jsonify({
            'success': False,
            'message': f'Error finalizing migration: {str(e)}'
        }), 500

@bp.route('/rollback', methods=['POST'])
def rollback_migration():
    """Rollback the migration by removing the database"""
    try:
        base_dir, db_path = get_paths()
        
        # Check if database exists
        if os.path.exists(db_path):
            # Remove the database file
            os.remove(db_path)
            logger.info(f"Removed database file: {db_path}")
            
            return jsonify({
                'success': True,
                'message': 'Migration rolled back successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No database file to remove'
            }), 404
            
    except Exception as e:
        logger.error(f"Error rolling back migration: {e}")
        return jsonify({
            'success': False,
            'message': f'Error rolling back migration: {str(e)}'
        }), 500
