import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing configuration files."""
    
    def __init__(self, base_dir=None):
        """Initialize the config service with a base directory."""
        # If no base directory is provided, use the parent directory of the web app
        if base_dir is None:
            self.base_dir = Path(os.path.abspath(__file__)).parents[3]
        else:
            self.base_dir = Path(base_dir)
        
        logger.info(f"Config service initialized with base directory: {self.base_dir}")
    
    def get_config_files(self):
        """Get a list of all available configuration files."""
        yaml_files = []
        
        # Look for settings.yaml in the root directory
        settings_file = self.base_dir / 'settings.yaml'
        if settings_file.exists():
            yaml_files.append('settings.yaml')
        
        # Look for badge settings files in the root directory
        for badge_file in ['badge_settings_audio.yml', 'badge_settings_resolution.yml', 'badge_settings_review.yml']:
            file_path = self.base_dir / badge_file
            if file_path.exists():
                yaml_files.append(badge_file)
        
        return yaml_files
    
    def get_config(self, file_name):
        """Get the content of a configuration file."""
        file_path = self.base_dir / file_name
        
        if not file_path.exists():
            logger.error(f"Config file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                
                # Special handling for settings.yaml and aniDB structure
                if file_name == 'settings.yaml' and config and 'api_keys' in config and 'aniDB' in config['api_keys']:
                    anidb_settings = config['api_keys']['aniDB']
                    if isinstance(anidb_settings, list) and len(anidb_settings) >= 2:
                        # Combine the two array items into a single object
                        combined = {}
                        
                        # Get username from first item
                        if isinstance(anidb_settings[0], dict):
                            combined.update(anidb_settings[0])
                            
                        # Get other settings from second item
                        if len(anidb_settings) > 1 and isinstance(anidb_settings[1], dict):
                            combined.update(anidb_settings[1])
                            
                        config['api_keys']['aniDB'] = combined
                
                return config
        except Exception as e:
            logger.error(f"Error reading config file {file_path}: {e}")
            return None
    
    def update_config(self, file_name, content):
        """Update the content of a configuration file."""
        file_path = self.base_dir / file_name
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Special handling for settings.yaml and aniDB structure
        if file_name == 'settings.yaml' and 'api_keys' in content and 'aniDB' in content['api_keys']:
            # Convert a single object structure to the array structure expected in the YAML
            anidb_settings = content['api_keys']['aniDB']
            if isinstance(anidb_settings, dict):
                # Extract the username into first array item
                username = anidb_settings.pop('username', None)
                content['api_keys']['aniDB'] = [
                    {'username': username} if username else {},
                    anidb_settings
                ]
                
        try:
            with open(file_path, 'w') as file:
                yaml.safe_dump(content, file, default_flow_style=False, sort_keys=False)
            logger.info(f"Config file updated: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error updating config file {file_path}: {e}")
            return False
    
    def validate_api_settings(self, settings):
        """Validate the API settings structure."""
        if not isinstance(settings, dict):
            return False
        
        if 'api_keys' not in settings:
            return False
        
        api_keys = settings.get('api_keys', {})
        
        # Check if required sections exist
        required_sections = ['Jellyfin', 'OMDB', 'TMDB', 'aniDB']
        for section in required_sections:
            if section not in api_keys:
                logger.warning(f"Missing required section in API settings: {section}")
                return False
                
        # Validate Jellyfin section
        jellyfin = api_keys.get('Jellyfin', [])
        if not isinstance(jellyfin, list) or not jellyfin:
            return False
        
        # Check first Jellyfin entry
        jellyfin_entry = jellyfin[0]
        if not isinstance(jellyfin_entry, dict):
            return False
        
        required_jellyfin_keys = ['url', 'api_key', 'user_id']
        for key in required_jellyfin_keys:
            if key not in jellyfin_entry:
                logger.warning(f"Missing required key in Jellyfin settings: {key}")
                return False
        
        return True
