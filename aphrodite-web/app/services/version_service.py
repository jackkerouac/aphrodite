import requests
import logging
import json
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path

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
            else:
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
        else:
            self.base_dir = Path(base_dir)
            
        self.cache_file = self.base_dir / 'version_cache.json'
        self.version_file = self.base_dir / 'version.yml'
        logger.info(f"VersionService initialized with base directory: {self.base_dir}")
    
    def get_current_version(self):
        """Get the current version of Aphrodite from version.yml."""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r') as f:
                    version_data = yaml.safe_load(f)
                    return version_data.get('version', '1.4.3')  # Fallback to 1.4.3
            else:
                logger.warning(f"Version file not found: {self.version_file}")
                return '1.4.3'  # Fallback version
        except Exception as e:
            logger.error(f"Error reading version file: {e}")
            return '1.4.3'  # Fallback version
    
    def _load_cache(self):
        """Load cached version check data."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                if datetime.now() - cache_time < timedelta(hours=self.CACHE_DURATION_HOURS):
                    logger.info("Using cached version data")
                    return cache_data
                else:
                    logger.info("Cache expired, will fetch new data")
            else:
                logger.info("No cache file found")
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        
        return None
    
    def _save_cache(self, data):
        """Save version check data to cache."""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info("Version data cached successfully")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
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
        """Check for available updates, using cache if available."""
        try:
            # Try to load from cache first (unless forced)
            if not force_check:
                cached_data = self._load_cache()
                if cached_data:
                    return cached_data['data']
            
            # Get current version
            current_version = self.get_current_version()
            
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
                
                # Cache the successful result
                self._save_cache(result)
                
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
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in check_for_updates: {e}")
            current_version = self.get_current_version()
            return {
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
    
    def get_version_info(self):
        """Get complete version information including update status."""
        return self.check_for_updates()
