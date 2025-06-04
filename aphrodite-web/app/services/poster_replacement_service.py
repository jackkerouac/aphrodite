#!/usr/bin/env python3
# aphrodite-web/app/services/poster_replacement_service.py

import os
import sys
import logging
import shutil
import threading
import time
import uuid
import yaml
from typing import Dict, Optional

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

try:
    from aphrodite_helpers.settings_validator import load_settings
    from aphrodite_helpers.poster_uploader import PosterUploader
    from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
    from app.services.job import JobService
    from app.services.external_poster_service import ExternalPosterService
    logger = logging.getLogger(__name__)
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Import error in poster_replacement_service: {e}")
    raise

class PosterReplacementService:
    """Service for replacing posters with external sources"""
    
    def __init__(self):
        logger.info("PosterReplacementService.__init__ starting...")
        
        try:
            logger.info("Loading settings...")
            # Try direct YAML loading instead of load_settings() which might be hanging
            settings_path = '/app/settings.yaml' if os.path.exists('/app/settings.yaml') else 'settings.yaml'
            logger.info(f"Trying to load settings from: {settings_path}")
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.settings = yaml.safe_load(f)
                logger.info("Settings loaded directly from YAML")
            else:
                logger.warning("Settings file not found, using empty settings")
                self.settings = {'api_keys': {}}
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.settings = {'api_keys': {}}
        
        try:
            logger.info("Extracting Jellyfin settings...")
            api_keys = self.settings.get("api_keys", {})
            jellyfin_config = api_keys.get("Jellyfin", api_keys.get("jellyfin", {}))
            
            if isinstance(jellyfin_config, list) and len(jellyfin_config) > 0:
                self.jellyfin_settings = jellyfin_config[0]
            elif isinstance(jellyfin_config, dict):
                self.jellyfin_settings = jellyfin_config
            else:
                self.jellyfin_settings = {}
                
            logger.info(f"Jellyfin settings extracted: {bool(self.jellyfin_settings.get('url'))}")
        except Exception as e:
            logger.error(f"Error extracting Jellyfin settings: {e}")
            self.jellyfin_settings = {}
        
        try:
            logger.info("Creating ExternalPosterService instance...")
            self.external_poster_service = ExternalPosterService()
            logger.info("ExternalPosterService created successfully")
        except Exception as e:
            logger.error(f"Error creating ExternalPosterService: {e}")
            raise
        
        logger.info("PosterReplacementService.__init__ completed successfully")
    
    def replace_poster_async(self, item_id: str, poster_data: Dict, selected_badges: list = None) -> str:
        """Start poster replacement process in background and return job ID"""
        try:
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Create job record
            job_details = {
                'id': job_id,
                'type': 'poster_replacement',
                'command': f'replace_poster_{item_id}',
                'options': {
                    'item_id': item_id,
                    'poster_data': poster_data,
                    'badges': selected_badges or []
                },
                'status': 'queued',
                'start_time': time.time(),
                'end_time': None,
                'result': None
            }
            
            JobService.create_job(job_details)
            
            # Start replacement in background thread
            thread = threading.Thread(
                target=self._replace_poster_background,
                args=(job_id, item_id, poster_data, selected_badges)
            )
            thread.daemon = True
            thread.start()
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error starting poster replacement: {e}")
            raise
    
    def _replace_poster_background(self, job_id: str, item_id: str, poster_data: Dict, selected_badges: list):
        """Background task to replace poster"""
        try:
            # Update job status to running
            JobService.update_job(job_id, {'status': 'running'})
            
            # Step 1: Download and process the external poster
            logger.info(f"Downloading poster from {poster_data.get('source')} for item {item_id}")
            custom_poster_path = self.external_poster_service.download_poster(poster_data, item_id)
            
            if not custom_poster_path:
                raise Exception("Failed to download external poster")
            
            # Step 2: Backup current poster state if needed
            self._backup_current_poster(item_id)
            
            # Step 3: Apply badges if requested
            final_poster_path = custom_poster_path
            
            if selected_badges and len(selected_badges) > 0:
                logger.info(f"Applying badges: {', '.join(selected_badges)}")
                final_poster_path = self._apply_badges_to_poster(
                    item_id, 
                    custom_poster_path, 
                    selected_badges
                )
                
                if not final_poster_path:
                    raise Exception("Failed to apply badges to poster")
            
            # Step 4: Upload to Jellyfin
            logger.info(f"Uploading final poster to Jellyfin")
            upload_success = self._upload_to_jellyfin(item_id, final_poster_path)
            
            if not upload_success:
                raise Exception("Failed to upload poster to Jellyfin")
            
            # Step 5: Update metadata tags if badges were applied
            tag_updated = False
            if selected_badges and len(selected_badges) > 0:
                tag_updated = self._update_metadata_tag(item_id)
            
            # Success result
            result = {
                'success': True,
                'message': 'Poster successfully replaced',
                'item_id': item_id,
                'poster_source': poster_data.get('source'),
                'badges_applied': selected_badges or [],
                'tag_updated': tag_updated,
                'final_poster_path': final_poster_path
            }
            
            JobService.update_job(job_id, {
                'status': 'success',
                'end_time': time.time(),
                'result': result
            })
            
            logger.info(f"Successfully replaced poster for item {item_id}")
            
        except Exception as e:
            logger.error(f"Error in poster replacement background task: {e}")
            JobService.update_job(job_id, {
                'status': 'failed',
                'end_time': time.time(),
                'result': {
                    'success': False,
                    'error': str(e),
                    'item_id': item_id
                }
            })
    
    def _backup_current_poster(self, item_id: str):
        """Backup current poster state before replacement"""
        try:
            # Determine base directory
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                base_dir = '/app'
            else:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
            
            # Create backup directory
            backup_dir = os.path.join(base_dir, 'posters', 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Check for existing posters to backup
            for poster_type in ['original', 'modified']:
                poster_dir = os.path.join(base_dir, 'posters', poster_type)
                
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    poster_path = os.path.join(poster_dir, f"{item_id}{ext}")
                    
                    if os.path.exists(poster_path):
                        backup_filename = f"{item_id}_{poster_type}_{int(time.time())}{ext}"
                        backup_path = os.path.join(backup_dir, backup_filename)
                        shutil.copy2(poster_path, backup_path)
                        logger.info(f"Backed up {poster_type} poster: {backup_path}")
            
        except Exception as e:
            logger.warning(f"Error backing up current poster: {e}")
            # Don't fail the whole operation for backup errors
    
    def _apply_badges_to_poster(self, item_id: str, poster_path: str, selected_badges: list) -> Optional[str]:
        """Apply selected badges to the poster using Aphrodite's badge system"""
        try:
            # Determine base directory
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                working_dir = '/app'
                base_command = ['python', '/app/aphrodite.py', 'item', item_id]
            else:
                working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
                base_command = ['python', os.path.join(working_dir, 'aphrodite.py'), 'item', item_id]
            
            # Copy custom poster to working directory so Aphrodite can process it
            working_poster_dir = os.path.join(working_dir, 'posters', 'working')
            os.makedirs(working_poster_dir, exist_ok=True)
            
            working_poster_path = os.path.join(working_poster_dir, f"{item_id}.jpg")
            shutil.copy2(poster_path, working_poster_path)
            
            # Build command with badge selection flags
            cmd = base_command.copy()
            
            # Add flags to disable badges not selected
            all_badge_types = ['audio', 'resolution', 'review', 'awards']
            for badge_type in all_badge_types:
                if badge_type not in selected_badges:
                    cmd.append(f'--no-{badge_type}')
            
            # Add flag to skip poster download (use existing working poster)
            cmd.append('--no-download')
            
            # Execute Aphrodite processing
            import subprocess
            logger.info(f"Executing badge application: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Badge application failed: {stderr}")
                return None
            
            # Check if modified poster was created
            modified_poster_dir = os.path.join(working_dir, 'posters', 'modified')
            modified_poster_path = os.path.join(modified_poster_dir, f"{item_id}.jpg")
            
            if os.path.exists(modified_poster_path):
                logger.info(f"Successfully applied badges to poster: {modified_poster_path}")
                return modified_poster_path
            else:
                logger.warning("Badge application completed but no modified poster found")
                return poster_path  # Return original if badges didn't create modified version
            
        except Exception as e:
            logger.error(f"Error applying badges to poster: {e}")
            return None
    
    def _upload_to_jellyfin(self, item_id: str, poster_path: str) -> bool:
        """Upload poster to Jellyfin"""
        try:
            uploader = PosterUploader(
                self.jellyfin_settings.get("url"),
                self.jellyfin_settings.get("api_key"),
                self.jellyfin_settings.get("user_id")
            )
            
            success = uploader.upload_poster(item_id, poster_path, max_retries=3)
            
            if success:
                logger.info(f"Successfully uploaded poster to Jellyfin for item {item_id}")
            else:
                logger.error(f"Failed to upload poster to Jellyfin for item {item_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error uploading poster to Jellyfin: {e}")
            return False
    
    def _update_metadata_tag(self, item_id: str) -> bool:
        """Update Jellyfin metadata tag to indicate poster has badges"""
        try:
            tagging_settings = get_tagging_settings()
            tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
            
            tagger = MetadataTagger(
                self.jellyfin_settings.get("url"),
                self.jellyfin_settings.get("api_key"),
                self.jellyfin_settings.get("user_id")
            )
            
            success = tagger.add_aphrodite_tag(item_id, tag_name)
            
            if success:
                logger.info(f"Successfully updated metadata tag for item {item_id}")
            else:
                logger.warning(f"Failed to update metadata tag for item {item_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating metadata tag: {e}")
            return False
    
    def validate_poster_data(self, poster_data: Dict) -> bool:
        """Validate poster data before processing"""
        required_fields = ['download_url', 'source', 'id']
        
        for field in required_fields:
            if field not in poster_data:
                logger.error(f"Missing required field in poster data: {field}")
                return False
        
        # Validate URL format
        download_url = poster_data.get('download_url', '')
        if not download_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid download URL format: {download_url}")
            return False
        
        return True
