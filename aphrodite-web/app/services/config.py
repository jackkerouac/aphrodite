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
            # In Docker, settings will be in the /app directory
            if os.path.exists('/app'):
                logger.info("DEBUG: /app directory exists, checking for settings.yaml")
                if os.path.exists('/app/settings.yaml'):
                    logger.info("DEBUG: Found /app/settings.yaml, using Docker paths")
                    self.base_dir = Path('/app')
                    # Check permissions
                    try:
                        logger.info("DEBUG: Checking permissions on /app/settings.yaml")
                        st_mode = os.stat('/app/settings.yaml').st_mode
                        logger.info(f"DEBUG: File mode: {st_mode:o}")
                        # Test if we can actually read the file
                        with open('/app/settings.yaml', 'r') as f:
                            first_line = f.readline()
                            logger.info(f"DEBUG: Successfully read first line: {first_line[:50]}...")
                    except Exception as e:
                        logger.error(f"DEBUG: Error accessing /app/settings.yaml: {e}")
                else:
                    logger.error("DEBUG: /app directory exists but settings.yaml not found!")
                    # List directory contents
                    try:
                        logger.info("DEBUG: Listing /app directory contents:")
                        for entry in os.listdir('/app'):
                            logger.info(f"DEBUG: /app/{entry}")
                    except Exception as e:
                        logger.error(f"DEBUG: Error listing /app directory: {e}")
            # For local development, use parents[3] to find the root directory
            else:
                logger.info("DEBUG: No /app directory, using development paths")
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
        else:
            self.base_dir = Path(base_dir)
        
        logger.info(f"DEBUG: Config service initialized with base directory: {self.base_dir}")
        
        # List all config files in the base directory
        logger.info("DEBUG: Checking for all config files in base directory")
        for config_file in ['settings.yaml', 'badge_settings_audio.yml', 'badge_settings_resolution.yml', 'badge_settings_review.yml']:
            file_path = self.base_dir / config_file
            if file_path.exists():
                logger.info(f"DEBUG: Found {config_file} at {file_path}")
                # Check if readable
                if os.access(file_path, os.R_OK):
                    logger.info(f"DEBUG: {config_file} is readable")
                else:
                    logger.error(f"DEBUG: {config_file} exists but is NOT readable")
            else:
                logger.error(f"DEBUG: {config_file} not found at {file_path}")
                # List directory contents
                try:
                    logger.info(f"DEBUG: Listing contents of {self.base_dir}:")
                    for entry in os.listdir(self.base_dir):
                        logger.info(f"DEBUG: {self.base_dir}/{entry}")
                except Exception as e:
                    logger.error(f"DEBUG: Error listing {self.base_dir} directory: {e}")
                    break
    
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
        
        logger.info(f"DEBUG: Attempting to load config from {file_path}")
        
        if not file_path.exists():
            logger.error(f"DEBUG: Config file not found: {file_path}")
            try:
                # Try to list parent directory to see what's there
                dir_content = os.listdir(file_path.parent)
                logger.info(f"DEBUG: Parent directory contains: {dir_content}")
            except Exception as e:
                logger.error(f"DEBUG: Could not list parent directory: {e}")
            return None
        
        # Check access permissions
        try:
            access_check = {
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK),
                'exists': os.access(file_path, os.F_OK)
            }
            logger.info(f"DEBUG: File access permissions: {access_check}")
        except Exception as e:
            logger.error(f"DEBUG: Error checking file permissions: {e}")
        
        try:
            with open(file_path, 'r') as file:
                logger.info(f"DEBUG: File opened successfully: {file_path}")
                try:
                    config = yaml.safe_load(file)
                    logger.info(f"DEBUG: YAML loaded successfully")
                    logger.info(f"Raw config loaded from {file_name}: {config}")
                except Exception as e:
                    logger.error(f"DEBUG: YAML parsing error: {e}")
                    # Try to read the raw content to see if it's valid
                    file.seek(0)  # Go back to the beginning of the file
                    try:
                        raw_content = file.read(1000)  # Read first 1000 chars
                        logger.error(f"DEBUG: Raw file content preview: {raw_content}")
                    except Exception as read_err:
                        logger.error(f"DEBUG: Could not read raw content: {read_err}")
                    return None
                
                # Special handling for settings.yaml and aniDB structure
                if file_name == 'settings.yaml' and config and 'api_keys' in config and 'aniDB' in config['api_keys']:
                    anidb_settings = config['api_keys']['aniDB']
                    logger.info(f"Original aniDB settings: {anidb_settings}, type: {type(anidb_settings)}")
                    
                    if isinstance(anidb_settings, list):
                        # Combine the items into a single object
                        combined = {}
                        
                        # Process each item in the array
                        for i, item in enumerate(anidb_settings):
                            logger.info(f"Processing aniDB item {i}: {item}")
                            if isinstance(item, dict):
                                combined.update(item)
                        
                        logger.info(f"Combined aniDB settings: {combined}")
                                
                        # Replace the array with the combined object
                        config['api_keys']['aniDB'] = combined
                
                logger.info(f"Final processed config: {config}")
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
                # Create array structure - first element contains username, second element contains everything else
                first_item = {}
                second_item = {}
                
                # Extract username for the first item
                if 'username' in anidb_settings:
                    first_item['username'] = anidb_settings['username']
                
                # Everything else goes in the second item
                for key, value in anidb_settings.items():
                    if key != 'username':
                        second_item[key] = value
                
                # Update the structure in the content
                content['api_keys']['aniDB'] = [first_item, second_item]
                
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
