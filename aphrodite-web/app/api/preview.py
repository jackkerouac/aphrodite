from flask import Blueprint, jsonify, request, send_file
import subprocess
import uuid
import time
import os
import threading
import shutil
import random
from pathlib import Path
from app.services.job import JobService

# Create blueprint for preview endpoints
bp = Blueprint('preview', __name__, url_prefix='/api/preview')

# Generate preview poster route
@bp.route('/generate', methods=['POST'])
def generate_preview():
    """Generate a preview poster with selected badges using example poster"""
    print("Generate preview endpoint called!")
    
    # Get the request data
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    print(f"Received data: {data}")
    
    # Validate badge types
    badge_types = data.get('badgeTypes', [])
    if not badge_types:
        return jsonify({
            'success': False,
            'message': 'At least one badge type must be selected'
        }), 400
    
    # Validate poster type
    poster_type = data.get('posterType', 'light')
    if poster_type not in ['light', 'dark']:
        return jsonify({
            'success': False,
            'message': 'Invalid poster type. Must be "light" or "dark"'
        }), 400
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Copy the example poster to the original directory with a unique name
    example_poster_filename = f"preview_{job_id}.png"
    source_path = f"E:\\programming\\aphrodite\\images\\example_poster_{poster_type}.png"
    
    # Determine poster directories (Docker-aware path detection)
    original_dir = Path('/app/posters/original') if os.path.exists('/app') else Path('posters/original')
    modified_dir = Path('/app/posters/modified') if os.path.exists('/app') else Path('posters/modified')
    working_dir = Path('/app/posters/working') if os.path.exists('/app') else Path('posters/working')
    
    # Ensure directories exist
    original_dir.mkdir(parents=True, exist_ok=True)
    modified_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = original_dir / example_poster_filename
    
    try:
        # Copy example poster to original directory
        shutil.copy2(source_path, dest_path)
        print(f"Copied example poster from {source_path} to {dest_path}")
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to copy example poster: {str(e)}'
        }), 500
    
    # Create job record
    job_details = {
        'id': job_id,
        'type': 'preview',
        'command': f'preview generation with {badge_types} on {poster_type} poster',
        'options': data,
        'status': 'queued',
        'start_time': time.time(),
        'end_time': None,
        'result': None,
        'poster_filename': example_poster_filename
    }
    
    JobService.create_job(job_details)
    
    # Define function to generate the preview
    def generate_preview_poster():
        try:
            # Import Aphrodite modules directly
            from aphrodite_helpers.resize_posters import resize_image
            from aphrodite_helpers.apply_badge import load_badge_settings, create_badge, apply_badge_to_poster
            
            # Step 1: Resize the poster
            working_poster_path = working_dir / example_poster_filename
            resize_success = resize_image(str(dest_path), str(working_poster_path), target_width=1000)
            
            if not resize_success:
                print("Failed to resize poster, using original")
                working_poster_path = dest_path
            else:
                print("✅ Resized poster to 1000px width")
            
            current_poster_path = str(working_poster_path)
            
            # Step 2: Apply badges based on selection
            
            # Audio badge
            if 'audio' in badge_types:
                try:
                    audio_settings = load_badge_settings("badge_settings_audio.yml")
                    audio_badge = create_badge(audio_settings, "DTS-HD MA")  # Mock codec
                    current_poster_path = apply_badge_to_poster(current_poster_path, audio_badge, audio_settings)
                    print("✅ Applied audio badge")
                except Exception as e:
                    print(f"⚠️ Failed to apply audio badge: {e}")
            
            # Resolution badge
            if 'resolution' in badge_types:
                try:
                    resolution_settings = load_badge_settings("badge_settings_resolution.yml")
                    resolution_badge = create_badge(resolution_settings, "1080p")  # Mock resolution
                    current_poster_path = apply_badge_to_poster(current_poster_path, resolution_badge, resolution_settings)
                    print("✅ Applied resolution badge")
                except Exception as e:
                    print(f"⚠️ Failed to apply resolution badge: {e}")
            
            # Awards badge
            if 'awards' in badge_types:
                try:
                    awards_settings = load_badge_settings("badge_settings_awards.yml")
                    awards_badge = create_badge(awards_settings, "oscars")  # Mock award
                    current_poster_path = apply_badge_to_poster(current_poster_path, awards_badge, awards_settings)
                    print("✅ Applied awards badge")
                except Exception as e:
                    print(f"⚠️ Failed to apply awards badge: {e}")
            
            # Review badges
            if 'review' in badge_types:
                try:
                    review_settings = load_badge_settings("badge_settings_review.yml")
                    
                    # Create a simple mock review badge
                    review_badge = create_badge(review_settings, "8.5")  # Mock IMDb score
                    current_poster_path = apply_badge_to_poster(current_poster_path, review_badge, review_settings)
                    print("✅ Applied review badge")
                except Exception as e:
                    print(f"⚠️ Failed to apply review badge: {e}")
            
            # Ensure final poster is in modified directory
            final_path = modified_dir / example_poster_filename
            if current_poster_path != str(final_path):
                shutil.copy2(current_poster_path, final_path)
                current_poster_path = str(final_path)
            
            # Check if final poster exists
            final_poster_path = modified_dir / example_poster_filename
            success = final_poster_path.exists()
            
            result = {
                'success': success,
                'poster_url': f'/api/images/modified/{example_poster_filename}' if success else None,
                'badges_applied': badge_types,
                'poster_type': poster_type
            }
            
            JobService.update_job(job_id, {
                'status': 'success' if success else 'failed',
                'end_time': time.time(),
                'result': result
            })
            
            print(f"Preview generation completed with status: {'success' if success else 'failed'}")
            
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e)
                }
            })
        
        finally:
            # Clean up temporary files
            try:
                if dest_path.exists():
                    dest_path.unlink()
                    print(f"Cleaned up original poster: {dest_path}")
                
                working_poster_path = working_dir / example_poster_filename
                if working_poster_path.exists():
                    working_poster_path.unlink()
                    print(f"Cleaned up working poster: {working_poster_path}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temporary files: {cleanup_error}")
    
    # Start generation in background thread
    thread = threading.Thread(target=generate_preview_poster)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f"Preview generation started with {poster_type} poster",
        'jobId': job_id
    })

# Get available badge types route
@bp.route('/badge-types', methods=['GET'])
def get_badge_types():
    """Get all available badge types"""
    return jsonify({
        'success': True,
        'badgeTypes': [
            {'id': 'audio', 'name': 'Audio', 'description': 'Audio codec badges (DTS-X, Atmos, etc.)'},
            {'id': 'resolution', 'name': 'Resolution', 'description': 'Resolution badges (4K, 1080p, etc.)'},
            {'id': 'review', 'name': 'Review', 'description': 'Review/rating badges (IMDb, TMDb, etc.)'},
            {'id': 'awards', 'name': 'Awards', 'description': 'Awards badges (Oscars, Emmys, etc.)'}
        ]
    })

# Get poster types route
@bp.route('/poster-types', methods=['GET'])
def get_poster_types():
    """Get available poster types"""
    return jsonify({
        'success': True,
        'posterTypes': [
            {'id': 'light', 'name': 'Light', 'description': 'Light colored example poster'},
            {'id': 'dark', 'name': 'Dark', 'description': 'Dark colored example poster'}
        ]
    })
