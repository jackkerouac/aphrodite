"""
Enhanced system information and versioning utilities.
Provides GitHub integration for version checking and proper version management.
"""

import os
import requests
import logging
from packaging import version
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VersionManager:
    """Manages application versioning and GitHub release checking."""
    
    def __init__(self):
        self.github_repo = "jackkerouac/aphrodite"
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.current_version = self._get_current_version()
    
    def _get_current_version(self) -> str:
        """Get the current application version from various sources."""
        try:
            # 1. Try to read from VERSION file - multiple possible locations
            possible_paths = [
                # Relative to this script
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'VERSION'),
                # From current working directory
                'VERSION',
                # From root if in Docker
                '/app/VERSION',
                # Alternative Docker location
                '/aphrodite/VERSION'
            ]
            
            for version_file in possible_paths:
                version_file = os.path.normpath(version_file)
                if os.path.exists(version_file):
                    try:
                        with open(version_file, 'r') as f:
                            file_version = f.read().strip()
                            if file_version:
                                logger.info(f"Version loaded from VERSION file at {version_file}: {file_version}")
                                return file_version
                    except Exception as e:
                        logger.warning(f"Could not read VERSION file at {version_file}: {e}")
                        continue
            
            # 2. Try environment variable
            env_version = os.getenv('APHRODITE_VERSION')
            if env_version:
                logger.info(f"Version loaded from environment: {env_version}")
                return env_version
            
            # 3. Try package version (if installed)
            try:
                import pkg_resources
                pkg_version = pkg_resources.get_distribution("aphrodite").version
                logger.info(f"Version loaded from package: {pkg_version}")
                return pkg_version
            except Exception:
                pass
            
            # 4. Fallback to development version
            logger.warning("No version source found, using development fallback")
            return '2.0.0-dev'
            
        except Exception as e:
            logger.error(f"Error getting current version: {e}")
            return '2.0.0-dev'
    
    def check_github_releases(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check GitHub for the latest release and compare with current version.
        
        Returns:
            Tuple[bool, Dict]: (success, update_info)
        """
        try:
            logger.info(f"Checking GitHub releases for {self.github_repo}")
            
            # Make request to GitHub API
            headers = {
                'Accept': 'application/vnd.github+json',
                'User-Agent': f'Aphrodite/{self.current_version}'
            }
            
            response = requests.get(
                self.github_api_url, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 404:
                logger.warning("Repository not found or no releases available")
                return True, {
                    'update_available': False,
                    'current_version': self.current_version,
                    'message': 'No releases found in repository'
                }
            
            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code}")
                return False, {
                    'error': f'GitHub API returned {response.status_code}',
                    'current_version': self.current_version
                }
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if not latest_version:
                logger.warning("No tag_name found in latest release")
                return True, {
                    'update_available': False,
                    'current_version': self.current_version,
                    'message': 'Latest release has no version tag'
                }
            
            # Compare versions
            update_available = self._is_update_available(
                self.current_version, 
                latest_version
            )
            
            update_info = {
                'update_available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'release_notes_url': release_data.get('html_url'),
                'release_date': release_data.get('published_at'),
                'release_name': release_data.get('name', f'v{latest_version}')
            }
            
            if update_available:
                update_info['message'] = f'Update available: v{latest_version}'
                logger.info(f"Update available: {self.current_version} -> {latest_version}")
            else:
                update_info['message'] = 'You are running the latest version!'
                logger.info(f"Running latest version: {self.current_version}")
            
            return True, update_info
            
        except requests.exceptions.Timeout:
            logger.error("GitHub API request timed out")
            return False, {
                'error': 'Request timed out',
                'current_version': self.current_version
            }
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to GitHub API")
            return False, {
                'error': 'Cannot connect to GitHub',
                'current_version': self.current_version
            }
        except Exception as e:
            logger.error(f"Error checking GitHub releases: {e}")
            return False, {
                'error': str(e),
                'current_version': self.current_version
            }
    
    def _is_update_available(self, current: str, latest: str) -> bool:
        """
        Compare two version strings to determine if an update is available.
        
        Args:
            current: Current version string
            latest: Latest version string
            
        Returns:
            bool: True if latest > current
        """
        try:
            # Clean version strings
            current_clean = self._clean_version(current)
            latest_clean = self._clean_version(latest)
            
            # Parse versions
            current_ver = version.parse(current_clean)
            latest_ver = version.parse(latest_clean)
            
            return latest_ver > current_ver
            
        except Exception as e:
            logger.error(f"Error comparing versions {current} vs {latest}: {e}")
            # If we can't parse versions, assume no update to be safe
            return False
    
    def _clean_version(self, version_str: str) -> str:
        """
        Clean version string for parsing.
        
        Args:
            version_str: Raw version string
            
        Returns:
            str: Cleaned version string
        """
        # Remove 'v' prefix
        cleaned = version_str.lstrip('v')
        
        # Handle development versions
        if '-dev' in cleaned:
            cleaned = cleaned.replace('-dev', '.dev0')
        
        return cleaned
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Get comprehensive version information.
        
        Returns:
            Dict: Version information
        """
        return {
            'version': self.current_version,
            'clean_version': self._clean_version(self.current_version),
            'is_development': '-dev' in self.current_version or '.dev' in self.current_version
        }

# Global instance
version_manager = VersionManager()

def get_version() -> str:
    """Get the current application version."""
    return version_manager.current_version
