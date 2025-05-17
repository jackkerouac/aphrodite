import os
import yaml
import logging
import shutil
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing configuration files."""
    
    def __init__(self, base_dir=None):
        """Initialize the config service with a base directory."""
        # If no base directory is provided, use the current working directory
        # This makes it more Docker-friendly
        if base_dir is None:
            self.base_dir = Path(os.getcwd())
        else:
            self.base_dir = Path(base_dir)
        
        # Create a writable config directory in data folder
        self.writable_config_dir = self.base_dir / 'data' / 'config'
        self.writable_config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Config service initialized with base directory: {self.base_dir}")
        logger.info(f"Writable config directory: {self.writable_config_dir}")
        
        # Debug info about directories and permissions
        logger.debug(f"Base directory exists: {self.base_dir.exists()}")
        logger.debug(f"Writable directory exists: {self.writable_config_dir.exists()}")
        if self.writable_config_dir.exists():
            logger.debug(f"Writable directory permissions: {oct(os.stat(self.writable_config_dir).st_mode)}")
            logger.debug(f"Writable directory is writable: {os.access(self.writable_config_dir, os.W_OK)}")
        
        # Create default config files if they don't exist
        self._ensure_default_configs()
    
    def _ensure_default_configs(self):
        """Ensure default configuration files exist."""
        default_config_files = [
            'settings.yaml',
            'badge_settings_audio.yml',
            'badge_settings_resolution.yml',
            'badge_settings_review.yml'
        ]
        
        for config_file in default_config_files:
            # First check if a writable version exists
            writable_file = self.writable_config_dir / config_file
            
            # If not, try to create one from the base directory
            if not writable_file.exists():
                base_file = self.base_dir / config_file
                if base_file.exists():
                    logger.info(f"Creating writable copy of {config_file}")
                    try:
                        shutil.copy(base_file, writable_file)
                        logger.debug(f"Successfully copied {base_file} to {writable_file}")
                        # Set permissions explicitly
                        os.chmod(writable_file, 0o666)
                        logger.debug(f"Set permissions on {writable_file} to 666")
                    except Exception as e:
                        logger.error(f"Error copying {config_file} to writable directory: {e}")
                        logger.error(traceback.format_exc())
                # If base file doesn't exist, try from default_configs
                else:
                    default_file = self.base_dir / 'default_configs' / config_file
                    if default_file.exists():
                        logger.info(f"Creating {config_file} from default template")
                        try:
                            shutil.copy(default_file, writable_file)
                            logger.debug(f"Successfully copied {default_file} to {writable_file}")
                            # Set permissions explicitly
                            os.chmod(writable_file, 0o666)
                            logger.debug(f"Set permissions on {writable_file} to 666")
                        except Exception as e:
                            logger.error(f"Error copying default {config_file}: {e}")
                            logger.error(traceback.format_exc())
    
    def get_config_files(self):
        """Get a list of all available configuration files."""
        yaml_files = []
        
        # Check both base directory and writable directory
        for config_file in ['settings.yaml', 'badge_settings_audio.yml', 
                           'badge_settings_resolution.yml', 'badge_settings_review.yml']:
            if (self.writable_config_dir / config_file).exists() or (self.base_dir / config_file).exists():
                yaml_files.append(config_file)
        
        logger.debug(f"Available config files: {yaml_files}")
        return yaml_files
    
    def get_config(self, file_name):
        """Get the content of a configuration file."""
        # First try the writable directory
        writable_file = self.writable_config_dir / file_name
        if writable_file.exists():
            file_path = writable_file
            logger.debug(f"Reading config from writable file: {file_path}")
        else:
            # Otherwise use the base directory
            file_path = self.base_dir / file_name
            logger.debug(f"Reading config from base file: {file_path}")
        
        if not file_path.exists():
            logger.error(f"Config file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.debug(f"Successfully loaded config from {file_path}")
                
                # Special handling for settings.yaml and aniDB structure
                if file_name == 'settings.yaml' and config and 'api_keys' in config and 'aniDB' in config['api_keys']:
                    anidb_settings = config['api_keys']['aniDB']
                    
                    if isinstance(anidb_settings, list):
                        # Combine the items into a single object
                        combined = {}
                        
                        # Process each item in the array
                        for i, item in enumerate(anidb_settings):
                            if isinstance(item, dict):
                                combined.update(item)
                        
                        # Replace the array with the combined object
                        config['api_keys']['aniDB'] = combined
                
                return config
        except Exception as e:
            logger.error(f"Error reading config file {file_path}: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def update_config(self, file_name, content):
        """Update the content of a configuration file."""
        # Always write to the writable directory
        file_path = self.writable_config_dir / file_name
        
        logger.debug(f"Updating config file: {file_path}")
        logger.debug(f"Directory exists: {file_path.parent.exists()}")
        logger.debug(f"Directory is writable: {os.access(file_path.parent, os.W_OK)}")
        
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
            # Create the file if it doesn't exist
            if not file_path.exists():
                # Touch the file to create it
                with open(file_path, 'w') as f:
                    f.write('')
                # Set permissions
                os.chmod(file_path, 0o666)
                logger.debug(f"Created empty file: {file_path} with permissions 666")
            
            # Check if the file is writable
            if not os.access(file_path, os.W_OK):
                logger.error(f"File is not writable: {file_path}")
                # Try to make it writable
                try:
                    os.chmod(file_path, 0o666)
                    logger.debug(f"Changed permissions to 666 for {file_path}")
                except Exception as e:
                    logger.error(f"Failed to make file writable: {e}")
                    logger.error(traceback.format_exc())
                    return False
            
            # Write to a temporary file first to avoid corrupting the original if the process fails
            temp_path = file_path.with_suffix('.tmp')
            logger.debug(f"Writing to temporary file: {temp_path}")
            
            with open(temp_path, 'w') as file:
                yaml.safe_dump(content, file, default_flow_style=False, sort_keys=False)
                logger.debug(f"Successfully wrote to temporary file")
            
            # Set permissions on temp file
            os.chmod(temp_path, 0o666)
            
            # Replace the original file with the temporary file
            logger.debug(f"Replacing {file_path} with {temp_path}")
            os.replace(temp_path, file_path)
            logger.info(f"Config file updated: {file_path}")
            
            # If this is settings.yaml, also try to update the original file for compatibility
            if file_name == 'settings.yaml':
                original_path = self.base_dir / file_name
                if original_path.exists() and os.access(original_path, os.W_OK):
                    try:
                        temp_path = original_path.with_suffix('.tmp')
                        with open(temp_path, 'w') as file:
                            yaml.safe_dump(content, file, default_flow_style=False, sort_keys=False)
                        os.replace(temp_path, original_path)
                        logger.info(f"Also updated original config file: {original_path}")
                    except Exception as e:
                        logger.warning(f"Could not update original config file: {e}")
                        logger.warning(traceback.format_exc())
            
            return True
        except Exception as e:
            logger.error(f"Error updating config file {file_path}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def validate_api_settings(self, settings):
        """Validate the API settings structure."""
        if not isinstance(settings, dict):
            logger.error("Settings is not a dictionary")
            return False
        
        if 'api_keys' not in settings:
            logger.error("api_keys not in settings")
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
            logger.error("Jellyfin is not a list or is empty")
            return False
        
        # Check first Jellyfin entry
        jellyfin_entry = jellyfin[0]
        if not isinstance(jellyfin_entry, dict):
            logger.error("First Jellyfin entry is not a dictionary")
            return False
        
        required_jellyfin_keys = ['url', 'api_key', 'user_id']
        for key in required_jellyfin_keys:
            if key not in jellyfin_entry:
                logger.warning(f"Missing required key in Jellyfin settings: {key}")
                return False
        
        return True
    
    def is_config_writable(self, file_name):
        """Check if a configuration file is writable."""
        # Check if it exists and is writable in writable directory
        writable_file = self.writable_config_dir / file_name
        if writable_file.exists():
            is_writable = os.access(writable_file, os.W_OK)
            logger.debug(f"File {writable_file} exists and is writable: {is_writable}")
            return is_writable
        
        # If it doesn't exist in writable directory, check if writable dir is writable
        is_dir_writable = os.access(self.writable_config_dir, os.W_OK)
        logger.debug(f"Directory {self.writable_config_dir} is writable: {is_dir_writable}")
        return is_dir_writable
