"""
Database Operations API for Aphrodite Web UI

Provides backup, restore, and database maintenance operations.
"""

import os
import sys
import sqlite3
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime

# Add the project root to Python path to import database_backup
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from tools.database_backup import DatabaseBackup
except ImportError as e:
    print(f"Warning: Could not import DatabaseBackup: {e}")
    DatabaseBackup = None

bp = Blueprint('database_operations', __name__)


def get_database_path():
    """Get the correct database path for current environment."""
    # Check if we're in Docker environment
    is_docker = (
        os.path.exists('/app') and 
        os.path.exists('/app/settings.yaml') and 
        os.path.exists('/.dockerenv')
    )
    
    if is_docker:
        return '/app/data/aphrodite.db'
    else:
        # Local development environment
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base_dir, 'data', 'aphrodite.db')


@bp.route('/api/database/backup/info', methods=['GET'])
def get_backup_info():
    """Get database and backup information."""
    try:
        db_path = get_database_path()
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        # Initialize backup manager
        backup_manager = DatabaseBackup(db_path)
        
        # Get database info
        db_info = {
            'exists': os.path.exists(db_path),
            'path': db_path,
            'size': 0,
            'size_formatted': '0 B'
        }
        
        if db_info['exists']:
            db_size = os.path.getsize(db_path)
            db_info['size'] = db_size
            db_info['size_formatted'] = backup_manager._format_size(db_size)
        
        # Get backup list
        backups = backup_manager.list_backups()
        
        # Get schema version if possible
        schema_version = 'Unknown'
        try:
            if db_info['exists']:
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT version FROM schema_versions WHERE component = 'item_tracking' ORDER BY version DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    schema_version = f"v{row[0]}"
                conn.close()
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'database': db_info,
            'backups': backups,
            'schema_version': schema_version,
            'backup_directory': backup_manager.backup_dir
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/backup/create', methods=['POST'])
def create_backup():
    """Create a new database backup."""
    try:
        db_path = get_database_path()
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': f'Database not found: {db_path}'
            }), 404
        
        # Get options from request
        data = request.get_json() or {}
        compress = data.get('compress', True)
        
        # Create backup
        backup_manager = DatabaseBackup(db_path)
        backup_path = backup_manager.create_full_backup(compress=compress)
        
        # Get backup info
        backup_size = os.path.getsize(backup_path)
        original_size = os.path.getsize(db_path)
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'backup_path': backup_path,
            'backup_filename': os.path.basename(backup_path),
            'original_size': original_size,
            'backup_size': backup_size,
            'compression_ratio': ((1 - backup_size / original_size) * 100) if compress else 0,
            'compressed': compress
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/backup/verify', methods=['POST'])
def verify_backup():
    """Verify a backup file integrity."""
    try:
        data = request.get_json() or {}
        backup_filename = data.get('backup_filename')
        
        if not backup_filename:
            return jsonify({
                'success': False,
                'error': 'Backup filename is required'
            }), 400
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        db_path = get_database_path()
        backup_manager = DatabaseBackup(db_path)
        backup_path = os.path.join(backup_manager.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'error': f'Backup file not found: {backup_filename}'
            }), 404
        
        # Verify backup
        is_valid = backup_manager.verify_backup(backup_path)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': 'Backup is valid' if is_valid else 'Backup verification failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/backup/restore', methods=['POST'])
def restore_backup():
    """Restore database from backup."""
    try:
        data = request.get_json() or {}
        backup_filename = data.get('backup_filename')
        
        if not backup_filename:
            return jsonify({
                'success': False,
                'error': 'Backup filename is required'
            }), 400
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        db_path = get_database_path()
        backup_manager = DatabaseBackup(db_path)
        backup_path = os.path.join(backup_manager.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'error': f'Backup file not found: {backup_filename}'
            }), 404
        
        # Restore from backup (with automatic confirmation for API)
        success = backup_manager.restore_from_backup(backup_path, confirm=True)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Database successfully restored from {backup_filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database restore failed'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/backup/cleanup', methods=['POST'])
def cleanup_backups():
    """Clean up old backup files."""
    try:
        data = request.get_json() or {}
        keep_count = data.get('keep_count', 5)
        
        if not isinstance(keep_count, int) or keep_count < 1:
            return jsonify({
                'success': False,
                'error': 'keep_count must be a positive integer'
            }), 400
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        db_path = get_database_path()
        backup_manager = DatabaseBackup(db_path)
        
        # Clean up old backups
        removed_count = backup_manager.cleanup_old_backups(keep_count=keep_count)
        
        return jsonify({
            'success': True,
            'message': f'Cleanup completed. Removed {removed_count} old backups.',
            'removed_count': removed_count,
            'kept_count': keep_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/export', methods=['POST'])
def export_database():
    """Export database to JSON format and return download URL."""
    try:
        data = request.get_json() or {}
        include_sensitive = data.get('include_sensitive', False)
        
        if not DatabaseBackup:
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': f'Database not found: {db_path}'
            }), 404
        
        # Create backup manager with correct working directory
        # Get the base directory (same as get_database_path logic)
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            base_dir = '/app'
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        print(f"DEBUG EXPORT: Base directory: {base_dir}")
        print(f"DEBUG EXPORT: Current working directory: {os.getcwd()}")
        print(f"DEBUG EXPORT: Database path: {db_path}")
        
        # Change to the correct working directory before creating backup manager
        original_cwd = os.getcwd()
        os.chdir(base_dir)
        print(f"DEBUG EXPORT: Changed to working directory: {os.getcwd()}")
        
        try:
            backup_manager = DatabaseBackup(db_path)
            print(f"DEBUG EXPORT: Backup manager backup_dir: {backup_manager.backup_dir}")
            print(f"DEBUG EXPORT: Absolute backup_dir: {os.path.abspath(backup_manager.backup_dir)}")
            
            export_path = backup_manager.export_to_json(include_sensitive=include_sensitive)
            print(f"DEBUG EXPORT: Export path returned: {export_path}")
            print(f"DEBUG EXPORT: Absolute export path: {os.path.abspath(export_path)}")
            print(f"DEBUG EXPORT: Export file exists: {os.path.exists(export_path)}")
            
            # Convert to absolute path before changing back to original directory
            export_path = os.path.abspath(export_path)
            print(f"DEBUG EXPORT: Converted to absolute path: {export_path}")
            
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            print(f"DEBUG EXPORT: Restored working directory: {os.getcwd()}")
        
        # Get export file info
        export_size = os.path.getsize(export_path)
        export_filename = os.path.basename(export_path)
        
        return jsonify({
            'success': True,
            'message': 'Database exported to JSON successfully',
            'export_path': export_path,
            'export_filename': export_filename,
            'export_size': export_size,
            'export_size_formatted': backup_manager._format_size(export_size),
            'include_sensitive': include_sensitive,
            'download_url': f'/api/database/download/{export_filename}'
        })
        
    except Exception as e:
        # Restore working directory in case of error
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        print(f"ERROR EXPORT: Exception in export_database: {e}")
        import traceback
        print(f"TRACEBACK EXPORT: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/download/<filename>', methods=['GET'])
def download_export_file(filename):
    """Download an exported database file."""
    try:
        print(f"DEBUG: Download request for file: {filename}")
        
        if not DatabaseBackup:
            print("ERROR: DatabaseBackup not available")
            return jsonify({
                'success': False,
                'error': 'Database backup functionality not available'
            }), 500
        
        db_path = get_database_path()
        print(f"DEBUG: Database path: {db_path}")
        
        # Create backup manager with correct paths
        backup_manager = DatabaseBackup(db_path)
        
        # The backup manager uses relative paths, but we need absolute paths
        # Get the base directory (same as get_database_path logic)
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            base_dir = '/app'
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # Construct the correct export directory path
        export_dir = os.path.join(base_dir, 'data', 'backups')
        file_path = os.path.join(export_dir, filename)
        
        print(f"DEBUG: Base directory: {base_dir}")
        print(f"DEBUG: Export directory: {export_dir}")
        print(f"DEBUG: Looking for file: {file_path}")
        print(f"DEBUG: File exists: {os.path.exists(file_path)}")
        
        # Security check: ensure the file is actually an export file
        if not filename.startswith('aphrodite_export_') or not filename.endswith('.json'):
            print(f"ERROR: Invalid filename format: {filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid export filename'
            }), 400
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            # List files in directory for debugging
            if os.path.exists(export_dir):
                files = os.listdir(export_dir)
                print(f"DEBUG: Files in export directory: {files}")
            else:
                print(f"DEBUG: Export directory does not exist: {export_dir}")
                # Try the backup manager's directory
                manager_dir = backup_manager.backup_dir
                abs_manager_dir = os.path.abspath(manager_dir)
                print(f"DEBUG: Backup manager directory (relative): {manager_dir}")
                print(f"DEBUG: Backup manager directory (absolute): {abs_manager_dir}")
                if os.path.exists(abs_manager_dir):
                    files = os.listdir(abs_manager_dir)
                    print(f"DEBUG: Files in manager directory: {files}")
                    # Try using the manager's directory instead
                    file_path = os.path.join(abs_manager_dir, filename)
                    print(f"DEBUG: Trying manager directory file path: {file_path}")
                    if os.path.exists(file_path):
                        print(f"DEBUG: Found file in manager directory!")
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Export file not found: {filename}'
                        }), 404
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Export file not found: {filename}'
                    }), 404
        
        print(f"DEBUG: Sending file: {file_path}")
        
        # Send the file as a download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"ERROR: Exception in download_export_file: {e}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/database/integrity-check', methods=['GET'])
def check_database_integrity():
    """Check database integrity."""
    try:
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': f'Database not found: {db_path}'
            }), 404
        
        # Perform integrity check
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            # Get additional database info
            cursor = conn.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor = conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            # Get table count
            cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            is_ok = result == "ok"
            
            return jsonify({
                'success': True,
                'integrity_ok': is_ok,
                'result': result,
                'database_info': {
                    'page_count': page_count,
                    'page_size': page_size,
                    'table_count': table_count,
                    'total_size': page_count * page_size
                }
            })
            
        except Exception as db_error:
            return jsonify({
                'success': False,
                'integrity_ok': False,
                'error': f'Database integrity check failed: {str(db_error)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Register the blueprint (will be imported in main.py)
