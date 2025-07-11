"""
Jellyfin Integration Service

Handles communication with Jellyfin media server API.
"""

import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin
import asyncio
from datetime import datetime, timedelta

from app.core.config import get_settings
from aphrodite_logging import get_logger

# Define MediaType enum locally to avoid shared module dependency
from enum import Enum

class MediaType(Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    SEASON = "season"
    EPISODE = "episode"

def generate_id() -> str:
    """Generate a simple ID"""
    import uuid
    return str(uuid.uuid4())


class JellyfinService:
    """Service for interacting with Jellyfin API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("aphrodite.service.jellyfin", service="jellyfin")
        
        # Try to load from database first, then fallback to environment variables
        self.base_url = None
        self.api_key = None
        self.user_id = None
        
        # Load settings asynchronously when needed
        self._settings_loaded = False
        
        # Environment variable fallbacks
        self.env_base_url = self.settings.jellyfin_url
        self.env_api_key = self.settings.jellyfin_api_key
        self.env_user_id = getattr(self.settings, 'jellyfin_user_id', None)
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting for batch processing
        self._last_request_time = None
        self._min_request_interval = 0.1  # Minimum 100ms between requests
        self._request_lock = asyncio.Lock()
    
    async def _load_jellyfin_settings(self):
        """Load Jellyfin settings from database or environment variables"""
        if self._settings_loaded:
            return
        
        try:
            # Try to load from database first using proper async session
            from app.core.database import async_session_factory
            from app.models.config import SystemConfigModel
            from sqlalchemy import select
            
            # Check if global session factory is available, otherwise create a temporary one
            session_factory = async_session_factory
            temporary_engine = None
            
            if session_factory is None:
                self.logger.warning("Global database session factory not available, creating temporary one")
                
                # Create temporary database engine like the worker does
                from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
                
                temporary_engine = create_async_engine(
                    self.settings.database_url,
                    echo=False,
                    pool_size=1,
                    max_overflow=0,
                    pool_pre_ping=True
                )
                
                session_factory = async_sessionmaker(
                    temporary_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            
            try:
                async with session_factory() as db:
                    # Query the system_config table for settings using proper ORM
                    stmt = select(SystemConfigModel).where(SystemConfigModel.key == "settings.yaml")
                    result = await db.execute(stmt)
                    config_model = result.scalar_one_or_none()
                    
                    if config_model and config_model.value:
                        settings_data = config_model.value
                        
                        # Parse YAML string if it's a string
                        if isinstance(settings_data, str):
                            try:
                                import yaml
                                settings_data = yaml.safe_load(settings_data)
                                self.logger.debug("Parsed settings.yaml from string format")
                            except Exception as yaml_error:
                                self.logger.error(f"Failed to parse settings.yaml: {yaml_error}")
                                settings_data = None
                        
                        if settings_data and isinstance(settings_data, dict):
                            # Extract Jellyfin settings from api_keys
                            api_keys = settings_data.get('api_keys', {})
                            jellyfin_settings = api_keys.get('Jellyfin', [])
                            
                            if jellyfin_settings and len(jellyfin_settings) > 0:
                                jellyfin_config = jellyfin_settings[0]  # Use first config
                                
                                self.base_url = jellyfin_config.get('url')
                                self.api_key = jellyfin_config.get('api_key')
                                self.user_id = jellyfin_config.get('user_id')
                                
                                if self.base_url and self.api_key:
                                    self.logger.info(f"Loaded Jellyfin settings from database: {self.base_url}")
                                    self._settings_loaded = True
                                    return
                                else:
                                    self.logger.warning("Incomplete Jellyfin settings in database")
                            else:
                                self.logger.info("No Jellyfin settings found in database")
                        else:
                            self.logger.warning("Settings data is not a valid dictionary after parsing")
                    else:
                        self.logger.info("No settings found in database")
            finally:
                # Clean up temporary engine if created
                if temporary_engine is not None:
                    await temporary_engine.dispose()
        
        except Exception as e:
            self.logger.warning(f"Failed to load settings from database: {e}")
            # Clean up temporary engine if created
            if 'temporary_engine' in locals() and temporary_engine is not None:
                try:
                    await temporary_engine.dispose()
                except Exception:
                    pass  # Ignore cleanup errors
        
        # Fallback to environment variables
        self.base_url = self.env_base_url
        self.api_key = self.env_api_key
        self.user_id = self.env_user_id
        
        # Debug logging to trace the issue
        self.logger.debug(f"Final Jellyfin settings: base_url={self.base_url}, api_key={'***' if self.api_key else 'None'}, user_id={self.user_id}")
        
        if self.base_url and self.api_key:
            self.logger.info(f"Using Jellyfin settings: {self.base_url}")
        else:
            self.logger.error("No Jellyfin settings available from database or environment")
            self.logger.error(f"Environment variables: JELLYFIN_URL={self.env_base_url}, JELLYFIN_API_KEY={'***' if self.env_api_key else 'None'}")
            self.logger.error("This will cause poster downloads to fail!")
            
        # Always log the connection details for debugging
        self.logger.info(f"Jellyfin configuration check: base_url={bool(self.base_url)}, api_key={bool(self.api_key)}, user_id={self.user_id}")
        
        self._settings_loaded = True
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with proper Jellyfin headers"""
        # Always create a new session instead of reusing
        # This prevents "Event loop is closed" errors in worker environment
        # and avoids session conflicts during batch processing
        timeout = aiohttp.ClientTimeout(total=30)
        # Use X-Emby-Token header like v1, not URL parameters
        headers = {
            "X-Emby-Token": self.api_key,
            "Content-Type": "application/json"
        }
        return aiohttp.ClientSession(timeout=timeout, headers=headers)
    
    async def _throttle_request(self):
        """Throttle API requests to prevent overwhelming Jellyfin during batch processing"""
        async with self._request_lock:
            if self._last_request_time is not None:
                time_since_last = datetime.now() - self._last_request_time
                min_interval = timedelta(seconds=self._min_request_interval)
                
                if time_since_last < min_interval:
                    sleep_time = (min_interval - time_since_last).total_seconds()
                    self.logger.debug(f"Throttling request: sleeping {sleep_time:.3f}s")
                    await asyncio.sleep(sleep_time)
            
            self._last_request_time = datetime.now()
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test connection to Jellyfin server"""
        try:
            # Load settings first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error("Jellyfin configuration missing - check database settings or environment variables")
                return False, "Jellyfin not configured - missing URL or API key"
            
            # Use the correct API pattern like v1
            url = urljoin(self.base_url, "/System/Info")
            session = await self._get_session()
            
            try:
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
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Jellyfin connection error: {e}")
            return False, str(e)
    
    async def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all libraries from Jellyfin"""
        try:
            # Load settings first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error("Jellyfin not configured")
                return []
            
            url = urljoin(self.base_url, "/Library/VirtualFolders")
            session = await self._get_session()
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        libraries = await response.json()
                        self.logger.info(f"Found {len(libraries)} libraries")
                        return libraries
                    else:
                        self.logger.error(f"Failed to get libraries: HTTP {response.status}")
                        return []
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting libraries: {e}")
            return []
    
    async def get_library_items(self, library_id: str) -> List[Dict[str, Any]]:
        """Get all items from a specific library using user-specific API for reliability"""
        try:
            # Load settings first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error("Jellyfin not configured")
                return []
            
            # Use user-specific API if available (more reliable than general /Items endpoint)
            if self.user_id:
                url = urljoin(
                    self.base_url,
                    f"/Users/{self.user_id}/Items"
                )
                
                # Add Fields parameter to include Tags for badge status detection
                params = {
                    "ParentId": library_id,
                    "Recursive": "true",
                    "Fields": "Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
                }
                
                session = await self._get_session()
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get("Items", [])
                            self.logger.info(f"Found {len(items)} items in library {library_id} via user API")
                            return items
                        else:
                            self.logger.warning(f"User API failed for library items: HTTP {response.status}, falling back to general API")
                finally:
                    await session.close()
            
            # Fallback to general API
            url = urljoin(
                self.base_url,
                f"/Items"
            )
            
            # Add Fields parameter to include Tags for badge status detection
            params = {
                "ParentId": library_id,
                "Recursive": "true",
                "Fields": "Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("Items", [])
                        self.logger.info(f"Found {len(items)} items in library {library_id} via general API")
                        return items
                    else:
                        self.logger.error(f"Failed to get library items: HTTP {response.status}")
                        return []
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting library items: {e}")
            return []
    
    async def get_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific item (uses user-specific API first as it's more reliable)"""
        # Try the user-specific API first as it's more reliable
        result = await self.get_media_item_by_id(item_id)
        if result:
            return result
        
        # Fallback to general metadata API (though this often fails with HTTP 400)
        self.logger.warning(f"User-specific API failed for {item_id}, trying general metadata API")
        return await self.get_item_metadata(item_id)
    
    async def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific item"""
        try:
            # Ensure settings are loaded
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error(f"Jellyfin not configured when getting metadata for {item_id}")
                return None
            
            # Use consistent header-based authentication like other methods
            url = urljoin(self.base_url, f"/Items/{item_id}")
            
            # Add MediaSources and MediaStreams fields for badge compatibility
            params = {
                "Fields": "MediaSources,MediaStreams,ProviderIds,Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        metadata = await response.json()
                        self.logger.debug(f"Retrieved metadata for item {item_id}")
                        return metadata
                    elif response.status == 400:
                        self.logger.error(f"Jellyfin item not found or invalid: {item_id} (HTTP 400)")
                        self.logger.error(f"This usually means the item ID is invalid or the item was deleted from Jellyfin")
                        return None
                    elif response.status == 401:
                        self.logger.error(f"Jellyfin authentication failed (HTTP 401) - check API key configuration")
                        return None
                    elif response.status == 404:
                        self.logger.error(f"Jellyfin item not found: {item_id} (HTTP 404)")
                        return None
                    else:
                        response_text = await response.text()
                        self.logger.error(f"Failed to get item metadata: HTTP {response.status} - {response_text}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting item metadata for {item_id}: {e}")
            return None
    
    async def get_poster_url(self, item_id: str) -> Optional[str]:
        """Get poster image URL for an item with enhanced error handling"""
        try:
            # Ensure settings are loaded first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error(f"Jellyfin settings not configured when getting poster URL for {item_id}")
                return None
            
            # Primary poster image URL - use header-based auth instead of URL params
            poster_url = urljoin(
                self.base_url,
                f"/Items/{item_id}/Images/Primary"
            )
            
            # Verify the image exists
            session = await self._get_session()
            try:
                async with session.head(poster_url) as response:
                    if response.status == 200:
                        self.logger.debug(f"Found poster for item {item_id}")
                        return poster_url
                    elif response.status == 400:
                        # HTTP 400 is common for this endpoint, but poster might still exist
                        # Try a GET request to see if the image is actually available
                        self.logger.debug(f"HEAD request returned 400 for {item_id}, trying GET")
                        async with session.get(poster_url) as get_response:
                            if get_response.status == 200:
                                self.logger.debug(f"Found poster for item {item_id} via GET (HEAD failed)")
                                return poster_url
                            else:
                                self.logger.warning(f"No poster found for item {item_id} (GET: HTTP {get_response.status})")
                                return None
                    else:
                        self.logger.warning(f"No poster found for item {item_id} (HTTP {response.status})")
                        # Log more details for debugging
                        response_text = await response.text() if response.status != 404 else "Not Found"
                        self.logger.debug(f"Poster check failed for {item_id}: {response_text}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting poster URL for {item_id}: {e}")
            return None
    
    async def download_poster(self, item_id: str, debug_logger=None) -> Optional[bytes]:
        """Download poster image data"""
        try:
            # Throttle requests to prevent overwhelming Jellyfin during batch processing
            await self._throttle_request()
            
            # Ensure settings are loaded first
            await self._load_jellyfin_settings()
            
            self.logger.debug(f"Attempting to get poster URL for item {item_id}")
            poster_url = await self.get_poster_url(item_id)
            if not poster_url:
                self.logger.warning(f"No poster found for item {item_id}")
                return None
            
            self.logger.debug(f"Downloading poster from URL: {poster_url}")
            session = await self._get_session()
            try:
                # Debug logging: Log session creation
                if debug_logger:
                    await debug_logger.log_session_creation("download_poster", {
                        "poster_url": poster_url,
                        "session_id": id(session),
                        "item_id": item_id
                    })
                async with session.get(poster_url) as response:
                    # Debug logging: Log response details
                    if debug_logger:
                        await debug_logger.log_response_analysis(item_id, response)
                        
                    if response.status == 200:
                        poster_data = await response.read()
                        # Debug logging: Log successful download
                        if debug_logger:
                            await debug_logger.log_response_analysis(item_id, response, poster_data)
                        self.logger.debug(f"Downloaded poster for item {item_id}: {len(poster_data)} bytes")
                        return poster_data
                    else:
                        # Debug logging: Log failed download
                        if debug_logger:
                            await debug_logger.log_response_analysis(item_id, response)
                        self.logger.error(f"Failed to download poster for {item_id}: HTTP {response.status}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error downloading poster for {item_id}: {e}")
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
    
    async def get_media_item_by_id(self, jellyfin_id: str) -> Optional[Dict[str, Any]]:
        """Get media item details by Jellyfin ID using user-specific API"""
        try:
            # Throttle requests to prevent overwhelming Jellyfin during batch processing
            await self._throttle_request()
            
            # Ensure settings are loaded
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error(f"Jellyfin not configured when getting media item {jellyfin_id}")
                self.logger.error(f"Missing: base_url={not self.base_url}, api_key={not self.api_key}")
                return None
            
            # Try user-specific API first if user_id is available
            if self.user_id:
                url = urljoin(self.base_url, f"/Users/{self.user_id}/Items/{jellyfin_id}")
                params = {
                    "Fields": "MediaSources,MediaStreams"
                }
                
                session = await self._get_session()
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            media_item = await response.json()
                            self.logger.debug(f"Retrieved media item via user API {jellyfin_id}: {media_item.get('Name', 'Unknown')}")
                            return media_item
                        elif response.status == 400:
                            self.logger.warning(f"User API returned 400 for {jellyfin_id}, trying general API")
                        elif response.status == 401:
                            self.logger.error(f"Jellyfin authentication failed (HTTP 401) - check API key and user ID")
                            return None
                        elif response.status == 404:
                            self.logger.warning(f"Item not found via user API: {jellyfin_id}, trying general API")
                        else:
                            response_text = await response.text()
                            self.logger.warning(f"User API failed for {jellyfin_id}: HTTP {response.status} - {response_text}")
                finally:
                    await session.close()
            
            # Fallback to general API endpoint
            url = urljoin(self.base_url, f"/Items/{jellyfin_id}")
            params = {
                "Fields": "MediaSources,MediaStreams,ProviderIds,Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        media_item = await response.json()
                        self.logger.debug(f"Retrieved media item via general API {jellyfin_id}: {media_item.get('Name', 'Unknown')}")
                        return media_item
                    elif response.status == 400:
                        self.logger.error(f"Invalid Jellyfin item ID: {jellyfin_id} (HTTP 400)")
                        self.logger.error(f"This item may have been deleted from Jellyfin or the ID is corrupted")
                        return None
                    elif response.status == 401:
                        self.logger.error(f"Jellyfin authentication failed (HTTP 401) - check API key configuration")
                        return None
                    elif response.status == 404:
                        self.logger.error(f"Jellyfin item not found: {jellyfin_id} (HTTP 404)")
                        return None
                    else:
                        response_text = await response.text()
                        self.logger.error(f"Failed to get media item {jellyfin_id}: HTTP {response.status} - {response_text}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting media item {jellyfin_id}: {e}")
            return None
    
    async def upload_poster_image(self, item_id: str, image_path: str) -> bool:
        """Upload processed poster back to Jellyfin to replace original (v1 method)"""
        try:
            # Ensure settings are loaded first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error(f"Jellyfin settings not configured when uploading poster for {item_id}")
                return False
            
            # Read the image file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Base64 encode the image data (v1 method)
            import base64
            b64_data = base64.b64encode(image_data)
            
            # Determine content type from file extension
            from pathlib import Path
            ext = Path(image_path).suffix.lower()
            if ext in (".jpg", ".jpeg"):
                content_type = "image/jpeg"
            elif ext == ".png":
                content_type = "image/png"
            else:
                content_type = "image/jpeg"  # Default
            
            content_type += "; charset=utf-8"  # v1 format
            
            # Jellyfin API endpoint for setting primary image
            url = urljoin(self.base_url, f"/Items/{item_id}/Images/Primary")
            
            # Headers for Base64 upload (v1 method)
            headers = {
                "X-Emby-Token": self.api_key,
                "Content-Type": content_type
            }
            
            # Upload using Base64 body (not multipart form data)
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.post(url, headers=headers, data=b64_data) as response:
                    if response.status in [200, 204]:
                        self.logger.info(f"Successfully uploaded poster for item {item_id}")
                        
                        # Verify upload like v1 does
                        await asyncio.sleep(1)  # Brief delay
                        verification_success = await self._verify_upload(item_id)
                        
                        if verification_success:
                            self.logger.info(f"Upload verification successful for {item_id}")
                            return True
                        else:
                            self.logger.warning(f"Upload verification failed for {item_id}")
                            return False
                    else:
                        response_text = await response.text()
                        self.logger.error(f"Failed to upload poster for item {item_id}: HTTP {response.status} - {response_text}")
                        return False
                    
        except Exception as e:
            self.logger.error(f"Error uploading poster for item {item_id}: {e}")
            return False
    
    async def get_enhanced_audio_info(self, media_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get enhanced audio information including badge mapping (for V2 badge system)"""
        try:
            from .badge_processing.enhanced_audio_metadata_extractor import EnhancedAudioMetadataExtractor
            
            extractor = EnhancedAudioMetadataExtractor()
            return extractor.extract_audio_info(media_item)
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced audio info: {e}")
            return None
    
    async def get_audio_codec_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract audio codec information from Jellyfin media item using enhanced metadata analysis"""
        try:
            # Use enhanced metadata extractor for better analysis
            from .badge_processing.enhanced_audio_metadata_extractor import EnhancedAudioMetadataExtractor
            
            extractor = EnhancedAudioMetadataExtractor()
            audio_info = extractor.extract_audio_info(media_item)
            
            if audio_info:
                display_codec = audio_info.get('display_codec')
                self.logger.debug(f"Enhanced audio extraction for {media_item.get('Id', 'Unknown')}: {display_codec}")
                return display_codec
            else:
                self.logger.warning(f"Enhanced audio extraction failed for {media_item.get('Id', 'Unknown')}, using fallback")
                return self._fallback_audio_codec_extraction(media_item)
                
        except Exception as e:
            self.logger.error(f"Error in enhanced audio extraction: {e}")
            return self._fallback_audio_codec_extraction(media_item)
    
    def _fallback_audio_codec_extraction(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Fallback audio codec extraction method (original logic)"""
        try:
            self.logger.info(f"🔄 [AUDIO FALLBACK] Using legacy audio extraction for {media_item.get('Id', 'Unknown')}")
            
            # Get MediaSources from the media item
            media_sources = media_item.get('MediaSources', [])
            if not media_sources:
                self.logger.warning(f"No MediaSources found for item {media_item.get('Id', 'Unknown')}")
                return None
            
            # Use the first media source (primary file)
            media_source = media_sources[0]
            media_streams = media_source.get('MediaStreams', [])
            
            # Find the primary audio stream
            audio_streams = [stream for stream in media_streams if stream.get('Type') == 'Audio']
            if not audio_streams:
                self.logger.warning(f"No audio streams found for item {media_item.get('Id', 'Unknown')}")
                return None
            
            # Get the first audio stream (usually the primary one)
            audio_stream = audio_streams[0]
            codec = audio_stream.get('Codec', '').upper()
            
            # Map Jellyfin codec names to display names
            codec_mapping = {
                'DCA': 'DTS',
                'DTSHD': 'DTS-HD',
                'DTSMA': 'DTS-HD MA',
                'TRUEHD': 'TRUEHD',
                'AC3': 'DOLBY DIGITAL',
                'EAC3': 'DOLBY DIGITAL PLUS',
                'AAC': 'AAC',
                'MP3': 'MP3',
                'FLAC': 'FLAC'
            }
            
            # Check for Atmos in the audio stream profile or codec
            profile = audio_stream.get('Profile', '').upper()
            if 'ATMOS' in profile or 'ATMOS' in codec:
                if codec in ['TRUEHD', 'DTSMA']:
                    result = f"{codec_mapping.get(codec, codec)} ATMOS"
                else:
                    result = 'ATMOS'
                self.logger.info(f"🔄 [AUDIO FALLBACK] Detected Atmos: {result}")
                return result
            
            # Check for DTS-X
            if 'DTS-X' in profile or 'DTSX' in codec:
                self.logger.info(f"🔄 [AUDIO FALLBACK] Detected DTS-X")
                return 'DTS-X'
            
            # Return mapped codec or original if no mapping found
            display_codec = codec_mapping.get(codec, codec)
            
            self.logger.info(f"🔄 [AUDIO FALLBACK] Extracted codec: {display_codec}")
            return display_codec if display_codec else None
            
        except Exception as e:
            self.logger.error(f"❌ [AUDIO FALLBACK] Error in fallback extraction: {e}")
            return None
    
    async def get_video_resolution_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract video resolution using enhanced width-based detection (replaces legacy height-only logic)"""
        try:
            # Import enhanced detector for consistent resolution detection
            from app.services.badge_processing.resolution_detector import EnhancedResolutionDetector
            
            # Use the enhanced detector for all resolution detection
            detector = EnhancedResolutionDetector()
            resolution_info = detector.extract_resolution_info(media_item)
            
            if resolution_info:
                # Convert ResolutionInfo to string representation
                resolution_string = str(resolution_info)
                self.logger.debug(f"Enhanced resolution detection for {media_item.get('Id', 'Unknown')}: {resolution_string}")
                return resolution_string
            else:
                self.logger.warning(f"Enhanced resolution detection failed for {media_item.get('Id', 'Unknown')}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error in enhanced resolution detection: {e}")
            return None
    
    async def get_series_episodes(self, series_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get episodes for a TV series, limited to specified count"""
        try:
            # Use the same pattern as other methods - user-specific API
            url = urljoin(self.base_url, f"/Shows/{series_id}/Episodes")
            
            params = {
                "Fields": "MediaSources,MediaStreams",
                "Limit": limit,
                "UserId": self.user_id
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        episodes = data.get("Items", [])
                        self.logger.debug(f"Retrieved {len(episodes)} episodes for series {series_id}")
                        return episodes
                    else:
                        self.logger.error(f"Failed to get series episodes {series_id}: HTTP {response.status}")
                        return []
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting series episodes {series_id}: {e}")
            return []
    
    async def _verify_upload(self, item_id: str) -> bool:
        """Verify that the uploaded image is retrievable (v1 method)"""
        try:
            url = urljoin(self.base_url, f"/Items/{item_id}/Images/Primary")
            headers = {"X-Emby-Token": self.api_key}
            
            session = await self._get_session()
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return False
                    
                    # Check first 256 bytes for valid image signature
                    chunk = await response.content.read(256)
                    
                    # Check for valid image signatures
                    return (
                        chunk.startswith(b"\xff\xd8\xff") or  # JPEG
                        chunk.startswith(b"\x89PNG\r\n\x1a\n") or  # PNG
                        chunk.startswith(b"GIF")  # GIF
                    )
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"Error verifying upload for {item_id}: {e}")
            return False


# Global service instance  
_jellyfin_service: Optional[JellyfinService] = None

def get_jellyfin_service() -> JellyfinService:
    """Get global Jellyfin service instance"""
    global _jellyfin_service
    if _jellyfin_service is None:
        _jellyfin_service = JellyfinService()
    return _jellyfin_service
