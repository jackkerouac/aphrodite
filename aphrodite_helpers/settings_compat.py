# aphrodite_helpers/settings_compat.py

import os
import yaml
import json
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Add parent directory to path to import settings service
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir / "aphrodite-web"))

try:
    from app.services.settings_service import SettingsService
except ImportError:
    # Fallback for different paths
    try:
        sys.path.append(str(parent_dir))
        from aphrodite_web.app.services.settings_service import SettingsService
    except ImportError:
        logger.error("Could not import SettingsService")
        SettingsService = None

class SettingsCompat:
    """Compatibility layer for YAML settings"""
    
    def __init__(self, db_path=None):
        """Initialize with optional database path"""
        if db_path is None:
            # Determine default path
            is_docker = os.path.exists('/.dockerenv')
            if is_docker:
                db_path = '/app/data/aphrodite.db'
            else:
                db_path = os.path.join(parent_dir, 'data', 'aphrodite.db')
        
        self.db_path = db_path
        self.settings_service = None
        self._cached_settings = None
        
        # Try to initialize the settings service
        if SettingsService:
            try:
                self.settings_service = SettingsService(db_path)
            except Exception as e:
                logger.warning(f"Could not initialize SettingsService: {e}")
    
    def _get_yaml_path(self, path=None):
        """Get the path to the YAML file"""
        if path is None:
            path = "settings.yaml"
        
        # If it's already an absolute path, use it
        if os.path.isabs(path):
            return path
        
        # Otherwise, construct path relative to project root
        root_dir = parent_dir
        return os.path.join(root_dir, path)
    
    def load_settings(self, path=None):
        """Load settings in YAML-compatible format"""
        # If a specific path is provided and it exists, try to load from YAML first
        if path is not None:
            yaml_path = self._get_yaml_path(path)
            if os.path.exists(yaml_path):
                try:
                    with open(yaml_path, 'r') as f:
                        yaml_settings = yaml.safe_load(f)
                        logger.info(f"Loaded settings from YAML file: {yaml_path}")
                        return yaml_settings
                except Exception as e:
                    logger.warning(f"Error loading YAML settings from {yaml_path}: {e}")
        
        # Try to load from database if settings service is available
        if self.settings_service:
            try:
                # Check if database has settings
                version = self.settings_service.get_current_version()
                if version > 0:
                    logger.info("Loading settings from SQLite database")
                    return self._load_from_database()
            except Exception as e:
                logger.warning(f"Error loading from database: {e}")
        
        # Fall back to YAML file
        yaml_path = self._get_yaml_path(path or "settings.yaml")
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    yaml_settings = yaml.safe_load(f)
                    logger.info(f"Loaded settings from fallback YAML file: {yaml_path}")
                    return yaml_settings
            except Exception as e:
                logger.error(f"Error loading fallback YAML settings: {e}")
        
        logger.error("Could not load settings from database or YAML file")
        return None
    
    def _load_from_database(self):
        """Load settings from database and convert to YAML format"""
        if self._cached_settings is not None:
            return self._cached_settings
        
        # Get all settings organized by category
        result = {}
        
        # Get API keys
        api_keys = self.settings_service.get_api_keys()
        if api_keys:
            result['api_keys'] = api_keys
        
        # Get TV series settings
        tv_settings = self.settings_service.get_settings_by_category('tv_series')
        if tv_settings:
            result['tv_series'] = {}
            for key, value in tv_settings.items():
                # Remove category prefix
                short_key = key.replace('tv_series.', '')
                result['tv_series'][short_key] = value
        
        # Get metadata tagging settings
        metadata_settings = self.settings_service.get_settings_by_category('metadata_tagging')
        if metadata_settings:
            result['metadata_tagging'] = {}
            for key, value in metadata_settings.items():
                # Remove category prefix
                short_key = key.replace('metadata_tagging.', '')
                result['metadata_tagging'][short_key] = value
        
        # Get scheduler settings
        scheduler_settings = self.settings_service.get_settings_by_category('scheduler')
        if scheduler_settings:
            result['scheduler'] = {}
            for key, value in scheduler_settings.items():
                # Remove category prefix
                short_key = key.replace('scheduler.', '')
                result['scheduler'][short_key] = value
        
        self._cached_settings = result
        return result
    
    def load_badge_settings(self, badge_file):
        """Load badge settings in YAML-compatible format"""
        # Determine badge type from filename
        badge_type = None
        if 'audio' in badge_file.lower():
            badge_type = 'audio'
        elif 'resolution' in badge_file.lower():
            badge_type = 'resolution'
        elif 'review' in badge_file.lower():
            badge_type = 'review'
        elif 'awards' in badge_file.lower():
            badge_type = 'awards'
        
        # Try to load from database first if we have a badge type and settings service
        if badge_type and self.settings_service:
            try:
                version = self.settings_service.get_current_version()
                if version > 0:
                    badge_settings = self.settings_service.get_badge_settings(badge_type)
                    if badge_settings:
                        logger.info(f"Loaded {badge_type} badge settings from database")
                        return badge_settings
            except Exception as e:
                logger.warning(f"Error loading badge settings from database: {e}")
        
        # Fall back to loading from YAML file
        if not os.path.isabs(badge_file):
            badge_file = os.path.join(parent_dir, badge_file)
        
        if os.path.exists(badge_file):
            try:
                with open(badge_file, 'r') as f:
                    badge_settings = yaml.safe_load(f)
                    logger.info(f"Loaded badge settings from YAML file: {badge_file}")
                    return badge_settings
            except Exception as e:
                logger.error(f"Error loading badge settings from {badge_file}: {e}")
        
        logger.error(f"Could not load badge settings for {badge_file}")
        return None

# Global instance for backward compatibility
_settings_compat = SettingsCompat()

def load_settings(path="settings.yaml"):
    """Global function for backward compatibility"""
    return _settings_compat.load_settings(path)

def load_badge_settings(badge_file):
    """Global function for backward compatibility"""
    return _settings_compat.load_badge_settings(badge_file)
