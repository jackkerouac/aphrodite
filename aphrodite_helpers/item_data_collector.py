"""
Item Data Collector for Aphrodite Database Tracking

Gathers all item metadata during processing for database storage.
Extracts Jellyfin metadata, file information, and generates settings hashes.
"""

import hashlib
import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class ItemDataCollector:
    """
    Helper to gather all item metadata during processing.
    
    Collects:
    - Jellyfin metadata (title, year, type, external IDs)
    - File information (path, size, modification date)
    - Processing settings for change detection
    """
    
    def __init__(self, jellyfin_url: str, api_key: str, user_id: str):
        self.jellyfin_url = jellyfin_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'MediaBrowser Token="{api_key}"',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def collect_item_metadata(self, item_id: str) -> Dict[str, Any]:
        """
        Gather comprehensive metadata for an item.
        
        Args:
            item_id: Jellyfin item ID
            
        Returns:
            Dictionary containing all collected metadata
        """
        try:
            # Get item details from Jellyfin
            item_data = self._get_jellyfin_item_details(item_id)
            if not item_data:
                return {}
            
            # Extract basic information
            metadata = {
                'jellyfin_item_id': item_id,
                'jellyfin_library_id': item_data.get('ParentId', ''),
                'jellyfin_user_id': self.user_id,
                'item_type': item_data.get('Type', 'Unknown'),
                'title': item_data.get('Name', 'Unknown'),
                'year': item_data.get('ProductionYear'),
                'parent_item_id': item_data.get('SeriesId'),  # For episodes/seasons
            }
            
            # Extract external IDs
            external_ids = self.extract_external_ids(item_data)
            metadata['external_ids'] = external_ids
            
            # Get file information if available
            file_info = self._get_file_information(item_data)
            metadata.update(file_info)
            
            # Add processing timestamp
            metadata['metadata_last_updated'] = datetime.now().isoformat()
            metadata['metadata_sources_used'] = ['jellyfin']
            
            return metadata
            
        except Exception as e:
            print(f"⚠️ Error collecting metadata for item {item_id}: {e}")
            return {
                'jellyfin_item_id': item_id,
                'jellyfin_user_id': self.user_id,
                'item_type': 'Unknown',
                'title': 'Unknown',
                'metadata_last_updated': datetime.now().isoformat(),
                'last_error_message': str(e)
            }
    
    def _get_jellyfin_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed item information from Jellyfin API."""
        try:
            url = urljoin(self.jellyfin_url, f'/Users/{self.user_id}/Items/{item_id}')
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Failed to get Jellyfin item details: {e}")
            return None
    
    def extract_external_ids(self, jellyfin_item_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse external IDs from Jellyfin provider IDs.
        
        Args:
            jellyfin_item_data: Raw Jellyfin item data
            
        Returns:
            Dictionary of external IDs (tmdb, tvdb, imdb, etc.)
        """
        external_ids = {}
        
        # Get provider IDs from Jellyfin
        provider_ids = jellyfin_item_data.get('ProviderIds', {})
        
        # Map Jellyfin provider names to our standard names
        provider_mapping = {
            'Tmdb': 'tmdb',
            'Tvdb': 'tvdb', 
            'Imdb': 'imdb',
            'AniDB': 'anidb',
            'MyAnimeList': 'mal',
            'TheMovieDb': 'tmdb',
            'TheTVDB': 'tvdb'
        }
        
        for jellyfin_key, our_key in provider_mapping.items():
            if jellyfin_key in provider_ids and provider_ids[jellyfin_key]:
                external_ids[our_key] = str(provider_ids[jellyfin_key])
        
        return external_ids
    
    def _get_file_information(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file information from Jellyfin item data."""
        file_info = {}
        
        try:
            # Get media sources for file information
            media_sources = item_data.get('MediaSources', [])
            if media_sources:
                media_source = media_sources[0]  # Use first media source
                
                # File path
                file_path = media_source.get('Path')
                if file_path:
                    file_info['file_path'] = file_path
                    
                    # File size from Jellyfin
                    size = media_source.get('Size')
                    if size:
                        file_info['file_size'] = size
                    
                    # Try to get file modification time if file is accessible
                    try:
                        if os.path.exists(file_path):
                            mtime = os.path.getmtime(file_path)
                            file_info['file_modified_date'] = datetime.fromtimestamp(mtime).isoformat()
                    except Exception:
                        # File not accessible, that's okay
                        pass
                        
        except Exception as e:
            # File information is optional, continue without it
            pass
        
        return file_info
    
    def generate_settings_hash(self, processing_options: Dict[str, Any]) -> str:
        """
        Create hash of relevant settings for change detection.
        
        Args:
            processing_options: Dictionary of processing settings to hash
            
        Returns:
            SHA256 hash of the settings (first 16 characters)
        """
        # Include relevant settings that would affect processing
        settings_to_hash = {
            'badges_requested': processing_options.get('badges_requested', {}),
            'aphrodite_version': processing_options.get('aphrodite_version', 'unknown'),
            # Add other settings that would require reprocessing if changed
        }
        
        # Sort keys for consistent hashing
        settings_str = json.dumps(settings_to_hash, sort_keys=True)
        return hashlib.sha256(settings_str.encode()).hexdigest()[:16]
    
    def get_poster_info(self, item_id: str) -> Dict[str, str]:
        """Get poster URL information from Jellyfin."""
        poster_info = {}
        
        try:
            # Build poster URL
            poster_url = urljoin(
                self.jellyfin_url, 
                f'/Items/{item_id}/Images/Primary'
            )
            
            # Test if poster exists
            response = self.session.head(poster_url, timeout=5)
            if response.status_code == 200:
                poster_info['poster_original_url'] = poster_url
                
        except Exception as e:
            # Poster info is optional
            pass
        
        return poster_info
