#!/usr/bin/env python3
"""
Custom Poster Upload Service
Handles uploading custom posters, resizing them, and replacing in Jellyfin.
"""

import os
import sys
import uuid
import shutil
import logging
import threading
from pathlib import Path
from PIL import Image

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from aphrodite_helpers.poster_uploader import PosterUploader
from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
from aphrodite_helpers.check_jellyfin_connection import load_settings
from app.services.job import JobService

logger = logging.getLogger(__name__)

class CustomPosterService:
    """Service for handling custom poster uploads"""
    
    def __init__(self):
        self.settings = load_settings()
        if not self.settings:
            raise Exception("Failed to load settings")
        
        # Get Jellyfin connection details
        jf = self.settings["api_keys"]["Jellyfin"][0]
        self.url = jf["url"]
        self.api_key = jf["api_key"]
        self.user_id = jf["user_id"]
        
        # Initialize services
        self.poster_uploader = PosterUploader(self.url, self.api_key, self.user_id)
        self.metadata_tagger = MetadataTagger(self.url, self.api_key, self.user_id)
        
        # Get base directory
        self.base_dir = self._get_base_directory()
        
        # Ensure directories exist
        self.original_dir = os.path.join(self.base_dir, 'posters', 'original')
        self.modified_dir = os.path.join(self.base_dir, 'posters', 'modified')
        os.makedirs(self.original_dir, exist_ok=True)
        os.makedirs(self.modified_dir, exist_ok=True)
    
    def _get_base_directory(self):
        """Get base directory (Docker-aware)"""
        is_docker = (
            os.path.exists('/app') and 
            os.path.exists('/app/settings.yaml') and 
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            return '/app'
        else:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    
    def validate_image_file(self, file_path):
        """Validate that the uploaded file is a valid image"""
        try:
            with Image.open(file_path) as img:
                # Check if it's a valid image
                img.verify()
                return True
        except Exception as e:
            logger.error(f"Invalid image file {file_path}: {e}")
            return False
    
    def resize_poster(self, input_path, output_path, target_width=1000):
        """Resize poster to Aphrodite standards (1000px width)"""
        try:
            with Image.open(input_path) as img:
                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = img.height / img.width
                target_height = int(target_width * aspect_ratio)
                
                # Resize with high quality
                resized_img = img.resize((target_width, target_height), Image.LANCZOS)
                
                # Convert to RGB for JPEG (removes alpha channel if present)
                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    resized_img = resized_img.convert('RGB')
                
                # Save with high quality
                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    resized_img.save(output_path, 'JPEG', quality=95)
                else:
                    resized_img.save(output_path)
                
                logger.info(f"Successfully resized poster to {target_width}px width")
                return True
                
        except Exception as e:
            logger.error(f"Error resizing poster: {e}")
            return False
    
    def upload_custom_poster_async(self, item_id, file_data, apply_badges=True):
        """Upload custom poster asynchronously"""
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job record
        job_details = {
            'id': job_id,
            'type': 'custom_upload',
            'command': f'upload_custom_poster_{item_id}',
            'options': {
                'item_id': item_id,
                'apply_badges': apply_badges
            },
            'status': 'queued',
            'start_time': None,
            'end_time': None,
            'result': None
        }
        
        JobService.create_job(job_details)
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_custom_upload,
            args=(job_id, item_id, file_data, apply_badges)
        )
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def _process_custom_upload(self, job_id, item_id, file_data, apply_badges):
        """Process custom poster upload in background"""
        try:
            import time
            JobService.update_job(job_id, {
                'status': 'running',
                'start_time': time.time()
            })
            
            # Create temporary file to store uploaded data
            temp_path = os.path.join(self.base_dir, f"temp_upload_{item_id}_{uuid.uuid4().hex}")
            
            try:
                # Write uploaded file data to temp file
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                # Validate image
                if not self.validate_image_file(temp_path):
                    raise Exception("Invalid image file")
                
                # Determine output filename (always save as .jpg for consistency)
                output_filename = f"{item_id}.jpg"
                original_path = os.path.join(self.original_dir, output_filename)
                
                # Resize and save to original directory
                if not self.resize_poster(temp_path, original_path):
                    raise Exception("Failed to resize poster")
                
                # Upload to Jellyfin
                upload_success = self.poster_uploader.upload_poster(
                    item_id, original_path, max_retries=3
                )
                
                if not upload_success:
                    raise Exception("Failed to upload poster to Jellyfin")
                
                # Handle metadata tagging based on badge application
                tag_result = self._handle_metadata_tagging(item_id, apply_badges)
                
                # Clean up any existing modified poster if not applying badges
                if not apply_badges:
                    self._remove_modified_poster(item_id)
                
                # Success result
                result = {
                    'success': True,
                    'message': 'Custom poster uploaded successfully',
                    'item_id': item_id,
                    'apply_badges': apply_badges,
                    'poster_uploaded': upload_success,
                    'metadata_updated': tag_result['success'],
                    'tag_action': tag_result['action']
                }
                
                JobService.update_job(job_id, {
                    'status': 'success',
                    'end_time': time.time(),
                    'result': result
                })
                
                logger.info(f"Successfully uploaded custom poster for item {item_id}")
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            logger.error(f"Error processing custom upload for item {item_id}: {e}")
            import time
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e),
                    'item_id': item_id
                }
            })
    
    def _handle_metadata_tagging(self, item_id, apply_badges):
        """Handle metadata tag based on badge application choice"""
        tagging_settings = get_tagging_settings()
        tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
        
        try:
            # Get current tags to check if tag exists
            current_tags = self.metadata_tagger.get_item_tags(item_id)
            has_tag = tag_name in current_tags
            
            if apply_badges and not has_tag:
                # Add tag if applying badges and tag doesn't exist
                success = self.metadata_tagger.add_aphrodite_tag(item_id, tag_name)
                return {'success': success, 'action': 'added_tag'}
            elif not apply_badges and has_tag:
                # Remove tag if not applying badges and tag exists
                success = self.metadata_tagger.remove_aphrodite_tag(item_id, tag_name)
                return {'success': success, 'action': 'removed_tag'}
            else:
                # No action needed
                return {'success': True, 'action': 'no_change'}
                
        except Exception as e:
            logger.error(f"Error handling metadata tag for {item_id}: {e}")
            return {'success': False, 'action': 'error', 'error': str(e)}
    
    def _remove_modified_poster(self, item_id):
        """Remove modified poster file if it exists"""
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            modified_path = os.path.join(self.modified_dir, f"{item_id}{ext}")
            if os.path.exists(modified_path):
                try:
                    os.remove(modified_path)
                    logger.info(f"Removed modified poster: {modified_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to remove modified poster {modified_path}: {e}")
