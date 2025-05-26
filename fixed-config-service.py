import os
import yaml
import logging
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing configuration files."""
    
    def __init__(self, base_dir=None):
        """Initialize the config service with a base directory."""
        # Always use the root directory
        self.base_dir = Path("/app")
        
        # Create a writable config directory in data folder
        self.writable_config_dir = self.base_dir
        
        logger.info(f"Config service initialized with base directory: {self.base_dir}")
        logger.info(f"Writable config directory: {self.writable_config_dir}")
        
        # Debug info about directories and permissions
        logger.debug(f"Base directory exists: {self.base_dir.exists()}")
        if self.base_dir.exists():
            logger.debug(f"Base directory permissions: {oct(os.stat(self.base_dir).st_mode)}")
            logger.debug(f"Base directory is writable: {os.access(self.base_dir, os.W_OK)}")
            logger.debug(f"Base directory contents: {os.listdir(self.base_dir)}")
    
    def get_config_files(self):
        """Get a list of all available configuration files."""
        yaml_files = []
        
        # Check both base directory and writable directory
        for config_file in ['settings.yaml', 'badge_settings_audio.yml', 
                           'badge_settings_resolution.yml', 'badge_settings_review.yml']:
            if (self.base_dir / config_file).exists():
                yaml_files.append(config_file)
                # Print file permissions
                file_path = self.base_dir / config_file
                logger.debug(f"File {file_path} permissions: {oct(os.stat(file_path).st_mode)}")
                logger.debug(f"File {file_path} is writable: {os.access(file_path, os.W_OK)}")
        
        logger.debug(f"Available config files: {yaml_files}")
        return yaml_files
    
    def get_config(self, file_name):
        """Get the content of a configuration file."""
        file_path = self.base_dir / file_name
        
        logger.debug(f"Reading config from file: {file_path}")
        logger.debug(f"File exists: {file_path.exists()}")
        
        if not file_path.exists():
            logger.error(f"Config file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as file:
                logger.debug(f"Successfully opened file for reading: {file_path}")
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
        file_path = self.base_dir / file_name
        
        logger.debug(f"Updating config file: {file_path}")
        logger.debug(f"File exists: {file_path.exists()}")
        logger.debug(f"File is writable: {os.access(file_path, os.W_OK)}")
        
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
            # Try to make it writable if needed
            if file_path.exists() and not os.access(file_path, os.W_OK):
                logger.debug(f"Changing permissions for {file_path}")
                os.chmod(file_path, 0o666)
            
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
            
            return True
        except Exception as e:
            logger.error(f"Error updating config file {file_path}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def is_config_writable(self, file_name):
        """Check if a configuration file is writable."""
        file_path = self.base_dir / file_name
        if file_path.exists():
            is_writable = os.access(file_path, os.W_OK)
            logger.debug(f"File {file_path} exists and is writable: {is_writable}")
            return is_writable
        
        # If it doesn't exist, check if the directory is writable
        is_dir_writable = os.access(self.base_dir, os.W_OK)
        logger.debug(f"Directory {self.base_dir} is writable: {is_dir_writable}")
        return is_dir_writable
