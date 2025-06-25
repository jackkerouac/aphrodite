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

# Try multiple import paths for SettingsService
SettingsService = None

# First try the full Flask-based SettingsService
try:
    sys.path.insert(0, str(parent_dir / "aphrodite-web"))
    from app.services.settings_service import SettingsService
    logger.info("Successfully imported SettingsService from aphrodite-web/app/services")
except ImportError as e:
    logger.warning(f"Failed to import from aphrodite-web/app/services: {e}")
    try:
        sys.path.insert(0, str(parent_dir))
        from aphrodite_web.app.services.settings_service import SettingsService
        logger.info("Successfully imported SettingsService from aphrodite_web.app.services")
    except ImportError as e2:
        logger.warning(f"Failed to import from aphrodite_web.app.services: {e2}")
        try:
            # Try direct import if we're running from the right context
            from app.services.settings_service import SettingsService
            logger.info("Successfully imported SettingsService from app.services")
        except ImportError as e3:
            logger.warning(f"Failed to import from app.services: {e3}")
            # Try standalone version as fallback
            try:
                from aphrodite_helpers.standalone_settings_service import StandaloneSettingsService
                SettingsService = StandaloneSettingsService
                logger.info("Successfully imported StandaloneSettingsService as fallback")
            except ImportError as e4:
                logger.warning(f"Failed to import StandaloneSettingsService: {e4}")
                logger.warning("Could not import any SettingsService - falling back to YAML-only mode")
                SettingsService = None
except Exception as e:
    logger.error(f"Unexpected error importing SettingsService: {e}")
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
                logger.info(f"Successfully initialized SettingsService with db_path: {db_path}")
            except Exception as e:
                logger.warning(f"Could not initialize SettingsService: {e}")
        else:
            logger.warning("SettingsService not available - using YAML-only mode")
    
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
        """Load settings in YAML-compatible format (prioritize database over YAML)"""
        logger.info(f"load_settings called with path: {path}")
        
        # First, try to load from database if settings service is available
        if self.settings_service:
            try:
                logger.info("Attempting to load settings from database...")
                # Check if database has settings
                version = self.settings_service.get_current_version()
                logger.info(f"Database version: {version}")
                if version > 0:
                    logger.info("Loading settings from SQLite database")
                    settings = self._load_from_database()
                    if settings:
                        logger.info("Successfully loaded settings from database")
                        return settings
                    else:
                        logger.warning("Database version > 0 but no settings returned")
                else:
                    logger.info("Database exists but has no settings (version 0)")
            except Exception as e:
                logger.warning(f"Error checking database version: {e}")
                import traceback
                logger.warning(f"Database error traceback: {traceback.format_exc()}")
        else:
            logger.info("No settings service available - falling back to YAML")
        
        # Fall back to YAML file
        yaml_path = self._get_yaml_path(path or "settings.yaml")
        logger.info(f"Attempting to load settings from YAML: {yaml_path}")
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    yaml_settings = yaml.safe_load(f)
                    logger.info(f"Loaded settings from YAML file: {yaml_path}")
                    return yaml_settings
            except Exception as e:
                logger.error(f"Error loading YAML settings: {e}")
        
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
    
    def load_badge_settings(self, badge_file, force_reload=False):
        """Load badge settings in YAML-compatible format (prioritize database over YAML)"""
        # Clear cached settings if force_reload is requested
        if force_reload:
            self._cached_settings = None
        
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
        
        # Try to load from database first using async session approach
        if badge_type:
            try:
                import asyncio
                from api.app.services.settings_service import settings_service
                from api.app.core.database import async_session_factory
                
                async def get_from_db():
                    async with async_session_factory() as db:
                        return await settings_service.get_settings(badge_file, db, force_reload=force_reload)
                
                # Try to get the running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # If we're in an async context, create a task
                    if loop.is_running():
                        # Use run_in_executor to avoid "cannot be called from a running event loop" error
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, get_from_db())
                            badge_settings = future.result(timeout=10)
                    else:
                        badge_settings = asyncio.run(get_from_db())
                except RuntimeError:
                    # No event loop running, safe to use asyncio.run
                    badge_settings = asyncio.run(get_from_db())
                
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

# Global instance for backward compatibility - DISABLED to prevent connection issues
# try:
#     _settings_compat = SettingsCompat()
#     logger.info("Successfully created global SettingsCompat instance")
# except Exception as e:
#     logger.error(f"Error creating global SettingsCompat instance: {e}")
#     _settings_compat = None
_settings_compat = None  # Disabled to prevent async connection conflicts

def load_settings(path="settings.yaml"):
    """Global function for backward compatibility"""
    if _settings_compat:
        return _settings_compat.load_settings(path)
    else:
        # Fallback to direct YAML loading
        logger.warning("Using fallback YAML loading due to SettingsCompat initialization failure")
        yaml_path = path
        if not os.path.isabs(yaml_path):
            yaml_path = os.path.join(parent_dir, path)
        
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Error loading fallback YAML: {e}")
        return None

def load_badge_settings(badge_file, force_reload=False):
    """Global function for backward compatibility"""
    if _settings_compat:
        return _settings_compat.load_badge_settings(badge_file, force_reload=force_reload)
    else:
        # Fallback to direct YAML loading
        logger.warning("Using fallback badge YAML loading due to SettingsCompat initialization failure")
        yaml_path = badge_file
        if not os.path.isabs(yaml_path):
            yaml_path = os.path.join(parent_dir, yaml_path)
        
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Error loading fallback badge YAML: {e}")
        return None
