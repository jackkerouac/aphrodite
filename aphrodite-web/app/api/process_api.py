from flask import Blueprint, jsonify, request
import subprocess
import os
import sys
import shutil
from pathlib import Path

# Add the parent directory to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the cleanup function from aphrodite_helpers
from aphrodite_helpers.cleanup.poster_cleanup import clean_poster_directories

# Create blueprint for process endpoint
bp = Blueprint('process_api', __name__, url_prefix='/api/process')

@bp.route('/item', methods=['POST'])
def process_item():
    """Process a single Jellyfin item by ID"""
    print("Process item endpoint called with POST")
    print(f"Request data: {request.get_json()}")
    
    try:
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Basic validation
        if not data.get('itemId'):
            return jsonify({
                'success': False,
                'message': 'Item ID is required'
            }), 400
        
        if not data.get('badgeTypes') or len(data.get('badgeTypes')) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one badge type must be selected'
            }), 400
        
        # Get the root directory (parent of the aphrodite-web directory)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        script_path = os.path.join(root_dir, 'aphrodite.py')
        
        print(f"Using aphrodite.py at: {script_path}")
        
        # Build the command with the correct argument structure
        cmd = ['python', script_path, 'item', data['itemId']]
        
        # Add badge type flags (if a badge type is not in badgeTypes, add --no-{badge_type})
        all_badge_types = ['audio', 'resolution', 'review']
        for badge_type in all_badge_types:
            if badge_type not in data.get('badgeTypes', []):
                # Note: the script uses --no-reviews (not --no-review)
                flag_name = f"--no-{badge_type}s" if badge_type == 'review' else f"--no-{badge_type}"
                cmd.append(flag_name)
        
        # Add skip upload flag if requested
        if data.get('skipUpload'):
            cmd.append('--no-upload')
        
        print(f"Executing command: {' '.join(cmd)}")
        
        # Set environment variables to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Run the command synchronously for simplicity
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            cwd=root_dir,  # Execute in the root directory
            env=env,  # Use the modified environment
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        
        success = result.returncode == 0
        
        return jsonify({
            'success': success,
            'message': 'Processing completed successfully' if success else 'Processing failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returnCode': result.returncode
        })
        
    except Exception as e:
        print(f"Error processing item: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/library', methods=['POST'])
def process_library():
    """Process Jellyfin libraries"""
    print("Process library endpoint called with POST")
    print(f"Request data: {request.get_json()}")
    
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
        
        # If processing multiple libraries, suggest using the workflow API
        if len(data.get('libraryIds', [])) > 1:
            # Continue with synchronous processing if explicitly requested
            if not data.get('useWorkflow', True):
                return process_libraries_synchronously(data)
            
            # Otherwise, suggest using the workflow API
            return jsonify({
                'success': False,
                'message': 'For processing multiple libraries, please use the /api/workflow/library-batch endpoint.',
                'useWorkflow': True
            }), 400
        
        # For single library, process synchronously
        return process_libraries_synchronously(data)
        
    except Exception as e:
        print(f"Error processing libraries: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def process_libraries_synchronously(data):
    """Process libraries synchronously (old method)"""
    # Get the root directory (parent of the aphrodite-web directory)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    script_path = os.path.join(root_dir, 'aphrodite.py')
    
    print(f"Using aphrodite.py at: {script_path}")
    
    # Process each library
    results = []
    
    for library_id in data.get('libraryIds', []):
        # Build the command with the correct argument structure
        cmd = ['python', script_path, 'library', library_id]
        
        # Add limit if provided
        if data.get('limit'):
            cmd.extend(['--limit', str(data.get('limit'))])
        
        # Add retries if provided
        if data.get('retries'):
            cmd.extend(['--retries', str(data.get('retries'))])
        
        # Add badge type flags (if a badge type is not in badgeTypes, add --no-{badge_type})
        all_badge_types = ['audio', 'resolution', 'review']
        for badge_type in all_badge_types:
            if badge_type not in data.get('badgeTypes', []):
                # Note: the script uses --no-reviews (not --no-review)
                flag_name = f"--no-{badge_type}s" if badge_type == 'review' else f"--no-{badge_type}"
                cmd.append(flag_name)
        
        # Add skip upload flag if requested
        if data.get('skipUpload'):
            cmd.append('--no-upload')
        
        print(f"Executing command: {' '.join(cmd)}")
        
        # Set environment variables to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Run the command synchronously for simplicity
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            cwd=root_dir,  # Execute in the root directory
            env=env,  # Use the modified environment
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        
        results.append({
            'libraryId': library_id,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returnCode': result.returncode
        })
    
    # Check overall success
    all_success = all(result['success'] for result in results)
    
    return jsonify({
        'success': all_success,
        'message': 'All libraries processed successfully' if all_success else 'Some libraries failed to process',
        'results': results
    })


@bp.route('/cleanup', methods=['POST'])
def cleanup_posters():
    """Clean up poster directories"""
    print("Cleanup endpoint called with POST")
    
    try:
        # Get the request data
        data = request.get_json() or {}
        
        # Default is to clean all directories unless specified not to
        clean_modified = not data.get('skipModified', False)
        clean_working = not data.get('skipWorking', False)
        clean_original = not data.get('skipOriginal', False)
        
        # Call the cleanup function
        success, message = clean_poster_directories(
            clean_modified=clean_modified,
            clean_working=clean_working,
            clean_original=clean_original,
            verbose=True
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/restore-originals', methods=['POST'])
def restore_originals():
    """Restore all modified posters to their original versions"""
    print("Restore originals endpoint called!")
    
    try:
        # Get poster directories (Docker-aware path detection)
        if os.path.exists('/app/posters'):
            # Running in Docker
            original_dir = Path('/app/posters/original')
            modified_dir = Path('/app/posters/modified')
        else:
            # Running in development
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            original_dir = Path(root_dir) / 'posters' / 'original'
            modified_dir = Path(root_dir) / 'posters' / 'modified'
        
        print(f"Original directory: {original_dir}")
        print(f"Modified directory: {modified_dir}")
        
        restored_count = 0
        errors = []
        
        # Check if directories exist
        if not original_dir.exists():
            return jsonify({
                'success': False,
                'message': f'Original posters directory not found: {original_dir}'
            }), 400
        
        if not modified_dir.exists():
            return jsonify({
                'success': False,
                'message': f'Modified posters directory not found: {modified_dir}'
            }), 400
        
        # Iterate through original posters
        for original_file in original_dir.glob('*'):
            if original_file.is_file():
                modified_file = modified_dir / original_file.name
                
                # If a modified version exists, replace it with the original
                if modified_file.exists():
                    try:
                        shutil.copy2(original_file, modified_file)
                        restored_count += 1
                        print(f"Restored: {original_file.name}")
                    except Exception as e:
                        error_msg = f"Failed to restore {original_file.name}: {str(e)}"
                        errors.append(error_msg)
                        print(error_msg)
        
        success = len(errors) == 0
        
        return jsonify({
            'success': success,
            'message': f'Restore completed. Restored {restored_count} posters.' + (f' {len(errors)} errors occurred.' if errors else ''),
            'restored_count': restored_count,
            'total_processed': restored_count + len(errors),
            'errors': errors
        })
        
    except Exception as e:
        print(f"Error during restore process: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'restored_count': 0,
            'total_processed': 0,
            'errors': [str(e)]
        }), 500
