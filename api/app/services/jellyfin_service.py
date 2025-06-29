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
            self.logger.info(f"Using Jellyfin settings from environment: {self.base_url}")
        else:
            self.logger.warning("No Jellyfin settings available from database or environment")
            self.logger.warning(f"Environment variables: JELLYFIN_URL={self.env_base_url}, JELLYFIN_API_KEY={'***' if self.env_api_key else 'None'}")
        
        self._settings_loaded = True
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with proper Jellyfin headers"""
        # Always create a new session instead of reusing
        # This prevents "Event loop is closed" errors in worker environment
        timeout = aiohttp.ClientTimeout(total=30)
        # Use X-Emby-Token header like v1, not URL parameters
        headers = {
            "X-Emby-Token": self.api_key,
            "Content-Type": "application/json"
        }
        return aiohttp.ClientSession(timeout=timeout, headers=headers)
    
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
            
            url = urljoin(self.base_url, f"/Library/VirtualFolders?api_key={self.api_key}")
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
        """Get all items from a specific library"""
        try:
            url = urljoin(
                self.base_url,
                f"/Items?ParentId={library_id}&Recursive=true&api_key={self.api_key}"
            )
            
            # Add Fields parameter to include Tags for badge status detection
            params = {
                "Fields": "Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("Items", [])
                        self.logger.info(f"Found {len(items)} items in library {library_id}")
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
        """Get detailed information for a specific item (alias for get_item_metadata)"""
        # Try the user-specific API first as it's more reliable
        result = await self.get_media_item_by_id(item_id)
        if result:
            return result
        
        # Fallback to general metadata API
        return await self.get_item_metadata(item_id)
    
    async def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific item"""
        try:
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
                    else:
                        self.logger.error(f"Failed to get item metadata: HTTP {response.status}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting item metadata: {e}")
            return None
    
    async def get_poster_url(self, item_id: str) -> Optional[str]:
        """Get poster image URL for an item"""
        try:
            # Ensure settings are loaded first
            await self._load_jellyfin_settings()
            
            if not self.base_url or not self.api_key:
                self.logger.error(f"Jellyfin settings not configured when getting poster URL for {item_id}")
                return None
            
            # Primary poster image URL
            poster_url = urljoin(
                self.base_url,
                f"/Items/{item_id}/Images/Primary?api_key={self.api_key}"
            )
            
            # Verify the image exists
            session = await self._get_session()
            try:
                async with session.head(poster_url) as response:
                    if response.status == 200:
                        self.logger.debug(f"Found poster for item {item_id}")
                        return poster_url
                    else:
                        self.logger.warning(f"No poster found for item {item_id}")
                        return None
            finally:
                await session.close()
                    
        except Exception as e:
            self.logger.error(f"Error getting poster URL: {e}")
            return None
    
    async def download_poster(self, item_id: str) -> Optional[bytes]:
        """Download poster image data"""
        try:
            # Ensure settings are loaded first
            await self._load_jellyfin_settings()
            
            poster_url = await self.get_poster_url(item_id)
            if not poster_url:
                return None
            
            session = await self._get_session()
            try:
                async with session.get(poster_url) as response:
                    if response.status == 200:
                        poster_data = await response.read()
                        self.logger.debug(f"Downloaded poster for item {item_id}: {len(poster_data)} bytes")
                        return poster_data
                    else:
                        self.logger.error(f"Failed to download poster: HTTP {response.status}")
                        return None
            finally:
                await session.close()
                    
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
    
    async def get_media_item_by_id(self, jellyfin_id: str) -> Optional[Dict[str, Any]]:
        """Get media item details by Jellyfin ID using user-specific API"""
        try:
            # Use user-specific API pattern like v1: /Users/{user_id}/Items/{item_id}
            url = urljoin(self.base_url, f"/Users/{self.user_id}/Items/{jellyfin_id}")
            
            # Add MediaSources and MediaStreams fields for codec detection
            params = {
                "Fields": "MediaSources,MediaStreams"
            }
            
            session = await self._get_session()
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        media_item = await response.json()
                        self.logger.debug(f"Retrieved media item {jellyfin_id}: {media_item.get('Name', 'Unknown')}")
                        return media_item
                    else:
                        self.logger.error(f"Failed to get media item {jellyfin_id}: HTTP {response.status}")
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
    
    async def get_audio_codec_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract audio codec information from Jellyfin media item"""
        try:
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
                    return f"{codec_mapping.get(codec, codec)} ATMOS"
                else:
                    return 'ATMOS'
            
            # Check for DTS-X
            if 'DTS-X' in profile or 'DTSX' in codec:
                return 'DTS-X'
            
            # Return mapped codec or original if no mapping found
            display_codec = codec_mapping.get(codec, codec)
            
            self.logger.debug(f"Extracted audio codec for {media_item.get('Id', 'Unknown')}: {display_codec}")
            return display_codec if display_codec else None
            
        except Exception as e:
            self.logger.error(f"Error extracting audio codec info: {e}")
            return None
    
    async def get_video_resolution_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract video resolution information from Jellyfin media item"""
        try:
            # Get MediaSources from the media item
            media_sources = media_item.get('MediaSources', [])
            if not media_sources:
                self.logger.warning(f"No MediaSources found for item {media_item.get('Id', 'Unknown')}")
                return None
            
            # Use the first media source (primary file)
            media_source = media_sources[0]
            media_streams = media_source.get('MediaStreams', [])
            
            # Find the video stream
            video_streams = [stream for stream in media_streams if stream.get('Type') == 'Video']
            if not video_streams:
                self.logger.warning(f"No video streams found for item {media_item.get('Id', 'Unknown')}")
                return None
            
            # Get the first video stream
            video_stream = video_streams[0]
            height = video_stream.get('Height')
            width = video_stream.get('Width')
            
            if not height:
                self.logger.warning(f"No height information for item {media_item.get('Id', 'Unknown')}")
                return None
            
            # Check for HDR
            video_range = video_stream.get('VideoRange', '').upper()
            color_space = video_stream.get('ColorSpace', '').upper() 
            codec = video_stream.get('Codec', '').upper()
            
            is_hdr = (
                'HDR' in video_range or 
                'HDR10' in video_range or 
                'DOLBY' in video_range or
                'BT2020' in color_space or
                'HDR' in codec
            )
            
            # Determine resolution based on height
            if height >= 2160:
                base_resolution = '4K'
            elif height >= 1440:
                base_resolution = '1440p'
            elif height >= 1080:
                base_resolution = '1080p'
            elif height >= 720:
                base_resolution = '720p'
            elif height >= 480:
                base_resolution = '480p'
            else:
                base_resolution = f'{height}p'
            
            # Add HDR suffix if detected
            if is_hdr:
                resolution = f'{base_resolution} HDR'
            else:
                resolution = base_resolution
            
            self.logger.debug(f"Extracted resolution for {media_item.get('Id', 'Unknown')}: {resolution}")
            return resolution
            
        except Exception as e:
            self.logger.error(f"Error extracting video resolution info: {e}")
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
