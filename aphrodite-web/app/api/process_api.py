from flask import Blueprint, jsonify, request
import subprocess
import os

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
        
        # Run the command synchronously for simplicity
        # Set environment variables to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            cwd=root_dir,  # Execute in the root directory
            env=env  # Use the modified environment
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
                env=env  # Use the modified environment
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
        
    except Exception as e:
        print(f"Error processing libraries: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
