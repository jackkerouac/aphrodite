from flask import Blueprint, jsonify, request, send_file
import subprocess
import uuid
import time
import os
import threading
import shutil
# random import removed - no longer needed for preview
from pathlib import Path
from app.services.job import JobService

# Add the parent directory to the Python path to import aphrodite_helpers
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from aphrodite_helpers.check_jellyfin_connection import load_settings

# Create blueprint for preview endpoints
bp = Blueprint('preview', __name__, url_prefix='/api/preview')

# Function removed - previews now always use the example poster for consistency

# Generate preview poster route
@bp.route('/generate', methods=['POST'])
def generate_preview():
    """Generate a preview poster with selected badges using a random Jellyfin poster"""
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
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Always use the example poster for previews for consistency and reliability
    random_poster = None  # Skip Jellyfin poster lookup for previews
    
    # Determine base directory using consistent Docker-aware path detection
    def get_base_directory():
        """Get the base directory using the same logic as ConfigService."""
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        return '/app' if is_docker else os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    base_dir = get_base_directory()
    print(f"Using base directory: {base_dir}")
    original_dir = Path(base_dir) / 'posters' / 'original'
    modified_dir = Path(base_dir) / 'posters' / 'modified'
    working_dir = Path(base_dir) / 'posters' / 'working'
    
    # Ensure directories exist
    original_dir.mkdir(parents=True, exist_ok=True)
    modified_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)
    
    example_poster_filename = f"preview_{job_id}.png"
    dest_path = original_dir / example_poster_filename
    
    use_random_poster = False
    jellyfin_item_id = None
    jellyfin_item_name = "Example Poster"
    
    # Always use example poster for previews
    print("Using example_poster_light.png for consistent preview experience")
    source_path = os.path.join(base_dir, 'images', 'example_poster_light.png')
    print(f"Source path: {source_path}")
    print(f"Destination path: {dest_path}")
    print(f"Source exists: {os.path.exists(source_path)}")
    try:
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
        'command': f'preview generation with {badge_types} on {jellyfin_item_name}',
        'options': data,
        'status': 'queued',
        'start_time': time.time(),
        'end_time': None,
        'result': None,
        'poster_filename': example_poster_filename,
        'use_random_poster': use_random_poster,
        'jellyfin_item_id': jellyfin_item_id,
        'jellyfin_item_name': jellyfin_item_name
    }
    
    JobService.create_job(job_details)
    
    # Define function to generate the preview
    def generate_preview_poster():
        nonlocal base_dir  # Access the base_dir from the outer scope
        try:
            # Import Aphrodite modules directly
            from aphrodite_helpers.resize_posters import resize_image
            from aphrodite_helpers.apply_badge import load_badge_settings, create_badge, apply_badge_to_poster
            from aphrodite_helpers.poster_fetcher import download_poster
            from aphrodite_helpers.get_media_info import get_media_stream_info, get_primary_audio_codec
            from aphrodite_helpers.get_resolution_info import get_media_resolution_info, get_resolution_badge_text
            
            # Step 1: Poster is already in place (example poster copied earlier)
            print(f"Using example poster at {dest_path}")
            if not dest_path.exists():
                raise Exception(f"Example poster not found at {dest_path}")
            
            # Step 2: Resize the poster
            working_poster_path = working_dir / example_poster_filename
            resize_success = resize_image(str(dest_path), str(working_poster_path), target_width=1000)
            
            if not resize_success:
                print("Failed to resize poster, using original")
                working_poster_path = dest_path
            else:
                print("✅ Resized poster to 1000px width")
            
            current_poster_path = str(working_poster_path)
            
            # Verify we have a valid poster path
            if not current_poster_path or not os.path.exists(current_poster_path):
                raise Exception(f"No valid poster available at path: {current_poster_path}")
            
            # Step 3: Use realistic demo data for preview badges
            print("Using demo data for consistent preview experience")
            
            # Step 4: Apply badges based on selection
            
            # Audio badge
            if 'audio' in badge_types:
                try:
                    audio_settings = load_badge_settings("badge_settings_audio.yml")
                    # Use demo codec for consistent preview
                    demo_codec = "DTS-HD MA"
                    audio_badge = create_badge(audio_settings, demo_codec)
                    result_path = apply_badge_to_poster(current_poster_path, audio_badge, audio_settings)
                    if result_path:
                        current_poster_path = result_path
                        print(f"✅ Applied audio badge: {demo_codec}")
                    else:
                        print(f"⚠️ Audio badge application returned None, keeping current path")
                except Exception as e:
                    print(f"⚠️ Failed to apply audio badge: {e}")
            
            # Resolution badge
            if 'resolution' in badge_types:
                try:
                    resolution_settings = load_badge_settings("badge_settings_resolution.yml")
                    # Use demo resolution for consistent preview
                    demo_resolution = "4K HDR"
                    resolution_badge = create_badge(resolution_settings, demo_resolution)
                    result_path = apply_badge_to_poster(current_poster_path, resolution_badge, resolution_settings)
                    if result_path:
                        current_poster_path = result_path
                        print(f"✅ Applied resolution badge: {demo_resolution}")
                    else:
                        print(f"⚠️ Resolution badge application returned None, keeping current path")
                except Exception as e:
                    print(f"⚠️ Failed to apply resolution badge: {e}")
            
            # Awards badge
            if 'awards' in badge_types:
                try:
                    awards_settings = load_badge_settings("badge_settings_awards.yml")
                    awards_badge = create_badge(awards_settings, "oscars")  # Mock award
                    result_path = apply_badge_to_poster(current_poster_path, awards_badge, awards_settings)
                    if result_path:
                        current_poster_path = result_path
                        print("✅ Applied awards badge")
                    else:
                        print(f"⚠️ Awards badge application returned None, keeping current path")
                except Exception as e:
                    print(f"⚠️ Failed to apply awards badge: {e}")
            
            # Review badges
            if 'review' in badge_types:
                try:
                    # For previews, create realistic mock review data that matches the real format
                    print("📊 Adding review badge (using realistic mock data for preview)...")
                    
                    # Import the review functions to use the same creation logic
                    from aphrodite_helpers.apply_review_badges import create_review_container
                    
                    # Load review settings
                    review_settings = load_badge_settings("badge_settings_review.yml")
                    
                    # Create mock reviews in the same format as real reviews
                    mock_reviews = [
                        {
                            "source": "IMDb",
                            "text": "85%",
                            "image_key": "IMDb"
                        },
                        {
                            "source": "TMDb",
                            "text": "82%",
                            "image_key": "TMDb"
                        },
                        {
                            "source": "Rotten Tomatoes",
                            "text": "78%",
                            "image_key": "RT-Crit-Fresh"
                        }
                    ]
                    
                    # Create the review container using the same function as real reviews
                    review_container = create_review_container(mock_reviews, review_settings)
                    
                    if review_container:
                        # Apply the review container to the poster using the same logic as other badges
                        from aphrodite_helpers.apply_review_badges import apply_badge_to_poster as apply_review_badge
                        
                        print(f"📍 Current poster path before review: {current_poster_path}")
                        print(f"📍 Working dir: {working_dir}")
                        print(f"📍 Modified dir: {modified_dir}")
                        
                        # Use a temporary filename with .jpg extension for the review badge function
                        temp_filename = example_poster_filename.replace('.png', '.jpg')
                        temp_current_path = current_poster_path
                        
                        # If current poster is a PNG, we need to convert it temporarily for the review function
                        if current_poster_path and current_poster_path.endswith('.png'):
                            temp_jpg_path = current_poster_path.replace('.png', '.jpg')
                            try:
                                from PIL import Image
                                img = Image.open(current_poster_path)
                                img.convert('RGB').save(temp_jpg_path, 'JPEG')
                                temp_current_path = temp_jpg_path
                                print(f"🔄 Converted PNG to JPG for review processing: {temp_jpg_path}")
                            except Exception as e:
                                print(f"⚠️ Failed to convert PNG to JPG: {e}")
                        
                        result_path = apply_review_badge(
                            poster_path=temp_current_path,
                            badge=review_container,
                            settings=review_settings,
                            working_dir=str(working_dir),
                            output_dir=str(modified_dir)
                        )
                        
                        print(f"📍 Review badge result path: {result_path}")
                        
                        if result_path and os.path.exists(result_path):
                            # Convert the result back to PNG if needed
                            if result_path.endswith('.jpg') and example_poster_filename.endswith('.png'):
                                final_png_path = result_path.replace('.jpg', '.png')
                                try:
                                    from PIL import Image
                                    img = Image.open(result_path)
                                    img.save(final_png_path, 'PNG')
                                    os.remove(result_path)  # Remove the JPG version
                                    result_path = final_png_path
                                    print(f"🔄 Converted result back to PNG: {final_png_path}")
                                except Exception as e:
                                    print(f"⚠️ Failed to convert result back to PNG: {e}")
                            
                            current_poster_path = result_path
                            print(f"✅ Applied realistic mock review badges to {result_path}")
                        else:
                            print(f"⚠️ Failed to apply review container - result path: {result_path}")
                    else:
                        print("⚠️ Failed to create review container")
                        
                except Exception as e:
                    print(f"⚠️ Failed to apply review badge: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            # Ensure final poster is in modified directory
            final_path = modified_dir / example_poster_filename
            
            # Only copy if the current poster path is different from the final path
            # and the final path doesn't already exist (to avoid file locking issues)
            if current_poster_path and current_poster_path != str(final_path):
                if not final_path.exists():
                    try:
                        shutil.copy2(current_poster_path, final_path)
                        current_poster_path = str(final_path)
                        print(f"✅ Copied final poster to {final_path}")
                    except PermissionError as e:
                        print(f"⚠️ Could not copy to final location due to file lock: {e}")
                        print(f"ℹ️ Using existing file at {current_poster_path}")
                        # Check if the current path is already in modified directory
                        if str(modified_dir) in current_poster_path:
                            # File is already in the right place, just update the path reference
                            final_path = Path(current_poster_path)
                else:
                    print(f"ℹ️ Final poster already exists at {final_path}")
                    current_poster_path = str(final_path)
            
            # Check if final poster exists - use the actual current path if it's already in modified directory
            if current_poster_path and str(modified_dir) in current_poster_path:
                final_poster_path = Path(current_poster_path)
            else:
                final_poster_path = modified_dir / example_poster_filename
                
            success = final_poster_path.exists()
            
            result = {
                'success': success,
                'poster_url': f'/api/images/modified/{final_poster_path.name}' if success else None,
                'badges_applied': badge_types,
                'source_poster': jellyfin_item_name,
                'use_random_poster': use_random_poster
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
        'message': f"Preview generation started using {jellyfin_item_name}",
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
