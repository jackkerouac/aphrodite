"""
Jellyfin Integration Service

Handles communication with Jellyfin media server API.
"""

import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin
import asyncio

from app.core.config import get_settings
from aphrodite_logging import get_logger
from shared.types import MediaType, generate_id


class JellyfinService:
    """Service for interacting with Jellyfin API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("aphrodite.service.jellyfin", service="jellyfin")
        self.base_url = self.settings.jellyfin_url
        self.api_key = self.settings.jellyfin_api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test connection to Jellyfin server"""
        try:
            url = urljoin(self.base_url, f"/System/Info?api_key={self.api_key}")
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    server_name = data.get("ServerName", "Unknown")
                    version = data.get("Version", "Unknown")
                    self.logger.info(f"Connected to Jellyfin: {server_name} v{version}")
                    return True, f"Connected to {server_name} v{version}"
                else:
                    self.logger.error(f"Jellyfin connection failed: HTTP {response.status}")
                    return False, f"HTTP {response.status}: {await response.text()}"
                    
        except Exception as e:
            self.logger.error(f"Jellyfin connection error: {e}")
            return False, str(e)
    
    async def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all libraries from Jellyfin"""
        try:
            url = urljoin(self.base_url, f"/Library/VirtualFolders?api_key={self.api_key}")
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    libraries = await response.json()
                    self.logger.info(f"Found {len(libraries)} libraries")
                    return libraries
                else:
                    self.logger.error(f"Failed to get libraries: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting libraries: {e}")
            return []
    
    async def get_library_items(self, library_id: str) -> List[Dict[str, Any]]:
        """Get all items from a specific library"""
        try:
            url = urljoin(
                self.base_url,
                f"/Items?ParentId={library_id}&Recursive=true&api_key={self.api_key}"
            )
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("Items", [])
                    self.logger.info(f"Found {len(items)} items in library {library_id}")
                    return items
                else:
                    self.logger.error(f"Failed to get library items: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting library items: {e}")
            return []
    
    async def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific item"""
        try:
            url = urljoin(self.base_url, f"/Items/{item_id}?api_key={self.api_key}")
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    metadata = await response.json()
                    self.logger.debug(f"Retrieved metadata for item {item_id}")
                    return metadata
                else:
                    self.logger.error(f"Failed to get item metadata: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting item metadata: {e}")
            return None
    
    async def get_poster_url(self, item_id: str) -> Optional[str]:
        """Get poster image URL for an item"""
        try:
            # Primary poster image URL
            poster_url = urljoin(
                self.base_url,
                f"/Items/{item_id}/Images/Primary?api_key={self.api_key}"
            )
            
            # Verify the image exists
            session = await self._get_session()
            async with session.head(poster_url) as response:
                if response.status == 200:
                    self.logger.debug(f"Found poster for item {item_id}")
                    return poster_url
                else:
                    self.logger.warning(f"No poster found for item {item_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting poster URL: {e}")
            return None
    
    async def download_poster(self, item_id: str) -> Optional[bytes]:
        """Download poster image data"""
        try:
            poster_url = await self.get_poster_url(item_id)
            if not poster_url:
                return None
            
            session = await self._get_session()
            async with session.get(poster_url) as response:
                if response.status == 200:
                    poster_data = await response.read()
                    self.logger.debug(f"Downloaded poster for item {item_id}: {len(poster_data)} bytes")
                    return poster_data
                else:
                    self.logger.error(f"Failed to download poster: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error downloading poster: {e}")
            return None
    
    def _map_jellyfin_type(self, jellyfin_type: str) -> MediaType:
        """Map Jellyfin item type to our MediaType enum"""
        type_mapping = {
            "Movie": MediaType.MOVIE,
            "Series": MediaType.TV_SHOW,
            "Season": MediaType.SEASON,
            "Episode": MediaType.EPISODE
        }
        return type_mapping.get(jellyfin_type, MediaType.MOVIE)
    
    def parse_jellyfin_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Jellyfin item into our format"""
        return {
            "id": generate_id(),
            "title": item.get("Name", "Unknown"),
            "media_type": self._map_jellyfin_type(item.get("Type", "Movie")),
            "year": item.get("ProductionYear"),
            "jellyfin_id": item.get("Id"),
            "tmdb_id": self._extract_provider_id(item, "Tmdb"),
            "imdb_id": self._extract_provider_id(item, "Imdb"),
            "overview": item.get("Overview"),
            "genres": item.get("Genres", []),
            "runtime": item.get("RunTimeTicks", 0) // 10000000 if item.get("RunTimeTicks") else None,
            "community_rating": item.get("CommunityRating"),
            "official_rating": item.get("OfficialRating"),
            "premiere_date": item.get("PremiereDate"),
            "series_name": item.get("SeriesName"),
            "season_number": item.get("ParentIndexNumber"),
            "episode_number": item.get("IndexNumber")
        }
    
    def _extract_provider_id(self, item: Dict[str, Any], provider: str) -> Optional[str]:
        """Extract external provider ID from Jellyfin item"""
        provider_ids = item.get("ProviderIds", {})
        return provider_ids.get(provider)


# Global service instance
_jellyfin_service: Optional[JellyfinService] = None

def get_jellyfin_service() -> JellyfinService:
    """Get global Jellyfin service instance"""
    global _jellyfin_service
    if _jellyfin_service is None:
        _jellyfin_service = JellyfinService()
    return _jellyfin_service
