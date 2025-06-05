import requests
import logging
import json
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

class VersionService:
    """Service for managing version checking and GitHub release notifications."""
    
    # GitHub repository information
    GITHUB_REPO = "jackkerouac/aphrodite"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    # Cache settings
    CACHE_DURATION_HOURS = 24
    
    def __init__(self, base_dir=None):
        """Initialize the version service."""
        if base_dir is None:
            # Use same logic as ConfigService for consistency
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                self.base_dir = Path('/app')
                db_path = '/app/data/aphrodite.db'
            else:
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
                db_path = os.path.join(self.base_dir, 'data', 'aphrodite.db')
        else:
            self.base_dir = Path(base_dir)
            db_path = os.path.join(self.base_dir, 'data', 'aphrodite.db')
            
        # Initialize settings service for database operations
        self.settings_service = SettingsService(db_path)
        
        # Initialize current version from YAML file if not in database
        self._initialize_current_version()
        
        logger.info(f"VersionService initialized with base directory: {self.base_dir}")
    
    def _initialize_current_version(self):
        """Initialize current version from YAML file if not in database"""
        try:
            # Check if we have version info in database
            db_version_info = self.settings_service.get_app_version_info()
            
            if not db_version_info:
                # Try to get version from YAML file
                version_file = self.base_dir / 'version.yml'
                if version_file.exists():
                    with open(version_file, 'r') as f:
                        version_data = yaml.safe_load(f)
                        current_version = version_data.get('version', '2.2.5')
                else:
                    # Fallback version
                    current_version = '2.2.5'
                
                # Store in database
                self.settings_service.set_current_app_version(current_version)
                logger.info(f"Initialized current version in database: {current_version}")
            
        except Exception as e:
            logger.error(f"Error initializing current version: {e}")
    
    def get_current_version(self):
        """Get the current version of Aphrodite from database or YAML fallback."""
        try:
            # Try database first
            version_info = self.settings_service.get_app_version_info()
            if version_info and version_info['current_version']:
                return version_info['current_version']
            
            # Fallback to YAML file
            version_file = self.base_dir / 'version.yml'
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version_data = yaml.safe_load(f)
                    version = version_data.get('version', '2.2.5')
                    
                    # Store in database for future use
                    self.settings_service.set_current_app_version(version)
                    return version
            
            logger.warning(f"Version file not found: {version_file}")
            return '2.2.5'  # Fallback version
            
        except Exception as e:
            logger.error(f"Error reading version: {e}")
            return '2.2.5'  # Fallback version
    
    def _is_cache_valid(self, last_checked):
        """Check if the cached data is still valid"""
        try:
            if not last_checked:
                return False
            
            cache_time = datetime.fromisoformat(last_checked)
            return datetime.now() - cache_time < timedelta(hours=self.CACHE_DURATION_HOURS)
        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False
    
    def _fetch_latest_release(self):
        """Fetch the latest release information from GitHub."""
        try:
            logger.info(f"Fetching latest release from: {self.GITHUB_API_URL}")
            
            # Set a reasonable timeout and user agent
            headers = {
                'User-Agent': 'Aphrodite-Python-App',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(
                self.GITHUB_API_URL, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                release_data = response.json()
                
                # Extract relevant information
                latest_version = release_data.get('tag_name', '').lstrip('v')
                release_notes = release_data.get('body', '')
                release_url = release_data.get('html_url', '')
                published_at = release_data.get('published_at', '')
                
                result = {
                    'success': True,
                    'latest_version': latest_version,
                    'release_notes': release_notes,
                    'release_url': release_url,
                    'published_at': published_at,
                    'error': None
                }
                
                logger.info(f"Successfully fetched latest release: {latest_version}")
                return result
                
            else:
                logger.warning(f"GitHub API returned status {response.status_code}")
                return {
                    'success': False,
                    'error': f"GitHub API error: {response.status_code}",
                    'latest_version': None,
                    'release_notes': None,
                    'release_url': None,
                    'published_at': None
                }
                
        except requests.exceptions.Timeout:
            logger.warning("Timeout while fetching GitHub release data")
            return {
                'success': False,
                'error': "Request timeout",
                'latest_version': None,
                'release_notes': None,
                'release_url': None,
                'published_at': None
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Network error while fetching GitHub release data: {e}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}",
                'latest_version': None,
                'release_notes': None,
                'release_url': None,
                'published_at': None
            }
        except Exception as e:
            logger.error(f"Unexpected error while fetching GitHub release data: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'latest_version': None,
                'release_notes': None,
                'release_url': None,
                'published_at': None
            }
    
    def _compare_versions(self, current, latest):
        """Compare version strings to determine if an update is available."""
        try:
            # Simple version comparison assuming semantic versioning (x.y.z)
            def version_tuple(v):
                # Remove 'v' prefix if present and split by dots
                clean_v = v.lstrip('v')
                return tuple(map(int, clean_v.split('.')))
            
            current_tuple = version_tuple(current)
            latest_tuple = version_tuple(latest)
            
            return latest_tuple > current_tuple
            
        except Exception as e:
            logger.warning(f"Error comparing versions {current} vs {latest}: {e}")
            # If we can't parse versions, assume no update to be safe
            return False
    
    def check_for_updates(self, force_check=False):
        """Check for available updates, using database cache if available."""
        try:
            # Get current version
            current_version = self.get_current_version()
            
            # Try to load from database cache first (unless forced)
            if not force_check:
                cached_data = self.settings_service.get_app_version_info()
                if cached_data and self._is_cache_valid(cached_data.get('last_checked')):
                    logger.info("Using cached version data from database")
                    return cached_data
            
            # Fetch fresh data from GitHub
            release_info = self._fetch_latest_release()
            
            if release_info['success'] and release_info['latest_version']:
                # Check if update is available
                update_available = self._compare_versions(
                    current_version, 
                    release_info['latest_version']
                )
                
                result = {
                    'current_version': current_version,
                    'latest_version': release_info['latest_version'],
                    'update_available': update_available,
                    'release_notes': release_info['release_notes'],
                    'release_url': release_info['release_url'],
                    'published_at': release_info['published_at'],
                    'check_successful': True,
                    'error': None,
                    'last_checked': datetime.now().isoformat()
                }
                
                # Store the successful result in database
                self.settings_service.update_app_version_info(result)
                
            else:
                # GitHub API failed, return error state
                result = {
                    'current_version': current_version,
                    'latest_version': None,
                    'update_available': False,
                    'release_notes': None,
                    'release_url': None,
                    'published_at': None,
                    'check_successful': False,
                    'error': release_info['error'],
                    'last_checked': datetime.now().isoformat()
                }
                
                # Store the error state in database
                self.settings_service.update_app_version_info(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in check_for_updates: {e}")
            current_version = self.get_current_version()
            result = {
                'current_version': current_version,
                'latest_version': None,
                'update_available': False,
                'release_notes': None,
                'release_url': None,
                'published_at': None,
                'check_successful': False,
                'error': f"Unexpected error: {str(e)}",
                'last_checked': datetime.now().isoformat()
            }
            
            # Store the error state in database
            try:
                self.settings_service.update_app_version_info(result)
            except Exception as db_error:
                logger.error(f"Failed to store error state in database: {db_error}")
            
            return result
    
    def get_version_info(self):
        """Get complete version information including update status."""
        return self.check_for_updates()
    
    def update_current_version(self, version):
        """Update the current version in the database."""
        try:
            self.settings_service.set_current_app_version(version)
            logger.info(f"Updated current version to: {version}")
            return True
        except Exception as e:
            logger.error(f"Error updating current version: {e}")
            return False
