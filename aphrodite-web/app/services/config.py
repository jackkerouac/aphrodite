import os
import yaml
import logging
from pathlib import Path
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing configuration files."""
    
    def __init__(self, base_dir=None):
        """Initialize the config service with a base directory."""
        # Initialize base_dir first
        self.base_dir = None
        
        # If no base directory is provided, use the parent directory of the web app
        if base_dir is None:
            # Check for Docker environment more reliably
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')  # Docker creates this file
            )
            
            if is_docker:
                logger.info("DEBUG: Found Docker environment, using /app paths")
                self.base_dir = Path('/app')
                db_path = '/app/data/aphrodite.db'
            else:
                # For local development, use parents[3] to find the root directory
                logger.info("DEBUG: Using development paths")
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
                db_path = os.path.join(self.base_dir, 'data', 'aphrodite.db')
        else:
            self.base_dir = Path(base_dir)
            db_path = os.path.join(self.base_dir, 'data', 'aphrodite.db')
        
        logger.info(f"DEBUG: Config service initialized with base directory: {self.base_dir}")
        logger.info(f"DEBUG: Using database at: {db_path}")
        
        # Initialize settings service
        self.settings_service = SettingsService(db_path)
        
        # Check if settings need to be migrated
        self._check_migration()
        
    def _check_migration(self):
        """Check if settings need to be migrated from YAML to SQLite"""
        # Check if database has any settings
        version = self.settings_service.get_current_version()
        
        if version == 0:
            # Database is empty, check if YAML files exist
            settings_path = self.base_dir / 'settings.yaml'
            
            if settings_path.exists():
                logger.info("DEBUG: Found settings.yaml, attempting migration")
                try:
                    # Import migration script
                    import sys
                    sys.path.append(str(self.base_dir))
                    from tools.migrate_settings import migrate_yaml_to_sqlite
                    
                    # Migrate settings
                    success = migrate_yaml_to_sqlite(
                        str(self.base_dir),
                        self.settings_service.db_path,
                        interactive=False
                    )
                    
                    if success:
                        logger.info("DEBUG: Settings migration successful")
                    else:
                        logger.error("DEBUG: Settings migration failed")
                except Exception as e:
                    logger.error(f"DEBUG: Error during settings migration: {e}")
    
    def get_config_files(self):
        """Get a list of all available configuration files."""
        yaml_files = []
        
        # Check if settings exist in database
        version = self.settings_service.get_current_version()
        if version > 0:
            # Database has settings, return the virtual files
            yaml_files.append('settings.yaml')
            
            # Check which badge settings exist
            badge_types = ['audio', 'resolution', 'review', 'awards']
            for badge_type in badge_types:
                settings = self.settings_service.get_badge_settings(badge_type)
                if settings:
                    yaml_files.append(f'badge_settings_{badge_type}.yml')
        else:
            # Check for actual files
            settings_file = self.base_dir / 'settings.yaml'
            if settings_file.exists():
                yaml_files.append('settings.yaml')
            
            # Look for badge settings files in the root directory
            for badge_file in ['badge_settings_audio.yml', 'badge_settings_resolution.yml', 'badge_settings_review.yml', 'badge_settings_awards.yml']:
                file_path = self.base_dir / badge_file
                if file_path.exists():
                    yaml_files.append(badge_file)
        
        return yaml_files
    
    def get_config(self, file_name):
        """Get the content of a configuration file."""
        logger.info(f"DEBUG: Getting config for {file_name}")
        
        # Check if database has settings
        version = self.settings_service.get_current_version()
        
        if version > 0:
            # Load from database
            if file_name == 'settings.yaml':
                # Export settings to YAML format
                settings, _ = self.settings_service.export_to_yaml()
                return settings
            elif file_name.startswith('badge_settings_'):
                # Extract badge type from filename
                badge_type = file_name.replace('badge_settings_', '').replace('.yml', '')
                return self.settings_service.get_badge_settings(badge_type)
        
        # Fall back to loading from YAML file
        file_path = self.base_dir / file_name
        
        logger.info(f"DEBUG: Attempting to load config from {file_path}")
        
        if not file_path.exists():
            logger.error(f"DEBUG: Config file not found: {file_path}")
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
        logger.info(f"DEBUG: Updating config for {file_name}")
        
        # Determine if we're using SQLite
        version = self.settings_service.get_current_version()
        
        if version > 0:
            # Save to database
            if file_name == 'settings.yaml':
                # Handle API keys
                if 'api_keys' in content:
                    api_keys = content['api_keys']
                    for service, service_keys in api_keys.items():
                        if isinstance(service_keys, list):
                            self.settings_service.update_api_keys(service, service_keys)
                        else:
                            # Convert single dict to list format
                            self.settings_service.update_api_keys(service, [service_keys])
                
                # Handle other categories
                categories = {
                    'tv_series': 'tv_series',
                    'metadata_tagging': 'metadata_tagging',
                    'scheduler': 'scheduler'
                }
                
                for yaml_key, category in categories.items():
                    if yaml_key in content:
                        # Clear existing settings for this category
                        self.settings_service.delete_settings_by_category(category)
                        
                        # Add new settings
                        category_data = content[yaml_key]
                        for key, value in category_data.items():
                            full_key = f"{category}.{key}"
                            self.settings_service.set_setting(full_key, value, category)
                
                return True
            elif file_name.startswith('badge_settings_'):
                # Extract badge type from filename
                badge_type = file_name.replace('badge_settings_', '').replace('.yml', '')
                self.settings_service.update_badge_settings(badge_type, content)
                return True
        
        # Fall back to saving to YAML file
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
