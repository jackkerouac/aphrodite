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
        # Add user_id from settings - this was missing!
        self.user_id = getattr(self.settings, 'jellyfin_user_id', None)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # If user_id is not in settings, use the v1 value as fallback
        if not self.user_id:
            self.user_id = "484068279393441885f9272eba479ccd"  # From v1 settings.yaml
            self.logger.debug(f"Using fallback user_id: {self.user_id}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with proper Jellyfin headers"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            # Use X-Emby-Token header like v1, not URL parameters
            headers = {
                "X-Emby-Token": self.api_key,
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test connection to Jellyfin server"""
        try:
            # Use the correct API pattern like v1
            url = urljoin(self.base_url, "/System/Info")
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
            
            # Add Fields parameter to include Tags for badge status detection
            params = {
                "Fields": "Tags,Genres,Overview,ProductionYear,CommunityRating,OfficialRating"
            }
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
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
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    media_item = await response.json()
                    self.logger.debug(f"Retrieved media item {jellyfin_id}: {media_item.get('Name', 'Unknown')}")
                    return media_item
                else:
                    self.logger.error(f"Failed to get media item {jellyfin_id}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting media item {jellyfin_id}: {e}")
            return None
    
    async def get_audio_codec_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract audio codec information from media item"""
        try:
            media_sources = media_item.get("MediaSources", [])
            if not media_sources:
                self.logger.warning(f"No media sources found for item {media_item.get('Id')}")
                return None
            
            # Get the first media source (usually the main file)
            media_source = media_sources[0]
            media_streams = media_source.get("MediaStreams", [])
            
            # Find audio streams
            audio_streams = [stream for stream in media_streams if stream.get("Type") == "Audio"]
            
            if not audio_streams:
                self.logger.warning(f"No audio streams found for item {media_item.get('Id')}")
                return None
            
            # Get the first (primary) audio stream
            primary_audio = audio_streams[0]
            
            # Extract codec information with fallback chain
            codec = (
                primary_audio.get("DisplayTitle") or  # Often has full description like "DTS-HD MA 7.1"
                primary_audio.get("Title") or          # Sometimes has codec info
                primary_audio.get("Profile") or        # Profile like "DTS-HD MA"
                primary_audio.get("Codec", "").upper() # Base codec like "DTS"
            )
            
            if codec:
                # Clean up and standardize the codec name
                codec = self._standardize_audio_codec(codec)
                self.logger.debug(f"Detected audio codec for {media_item.get('Id')}: {codec}")
                return codec
            
            self.logger.warning(f"Could not determine audio codec for item {media_item.get('Id')}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting audio codec: {e}")
            return None
    
    def _standardize_audio_codec(self, raw_codec: str) -> str:
        """Standardize audio codec names to match badge system expectations"""
        if not raw_codec:
            return ""
        
        # Convert to uppercase for consistent matching
        codec = raw_codec.upper()
        
        # Common codec mappings to standardized names
        codec_mappings = {
            # DTS variants
            "DTS-HD MA": "DTS-HD MA",
            "DTS-HD MASTER AUDIO": "DTS-HD MA",
            "DTS-HD": "DTS-HD MA",
            "DTS-X": "DTS-X",
            "DTSX": "DTS-X",
            "DTS": "DTS",
            
            # Dolby variants
            "TRUEHD ATMOS": "TRUEHD ATMOS",
            "TRUEHD": "TRUEHD",
            "DOLBY TRUEHD": "TRUEHD",
            "ATMOS": "ATMOS",
            "DOLBY ATMOS": "ATMOS",
            "DOLBY DIGITAL PLUS": "DOLBY DIGITAL PLUS",
            "DOLBY DIGITAL+": "DOLBY DIGITAL PLUS",
            "EAC3": "DOLBY DIGITAL PLUS",
            "E-AC-3": "DOLBY DIGITAL PLUS",
            "DOLBY DIGITAL": "DOLBY DIGITAL",
            "AC3": "DOLBY DIGITAL",
            "AC-3": "DOLBY DIGITAL",
            
            # Other formats
            "FLAC": "FLAC",
            "PCM": "PCM",
            "AAC": "AAC",
            "MP3": "MP3"
        }
        
        # Try direct mapping first
        if codec in codec_mappings:
            return codec_mappings[codec]
        
        # Try partial matching for complex descriptions
        for pattern, standard in codec_mappings.items():
            if pattern in codec:
                return standard
        
        # If no mapping found, return cleaned version of original
        return codec.strip()
    
    async def get_tv_series_dominant_codec(self, series_id: str) -> Optional[str]:
        """Get dominant audio codec by sampling first 5 episodes of a TV series"""
        try:
            # Use user-specific API pattern for getting episodes
            url = urljoin(
                self.base_url,
                f"/Users/{self.user_id}/Items"
            )
            
            # Get episodes for the series
            params = {
                "ParentId": series_id,
                "IncludeItemTypes": "Episode",
                "Fields": "MediaSources,MediaStreams",
                "Limit": 5,
                "Recursive": "true"
            }
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to get episodes for series {series_id}: HTTP {response.status}")
                    return None
                
                data = await response.json()
                episodes = data.get("Items", [])
                
                if not episodes:
                    self.logger.warning(f"No episodes found for series {series_id}")
                    return None
                
                # Collect codecs from episodes
                codecs = []
                for episode in episodes:
                    codec = await self.get_audio_codec_info(episode)
                    if codec:
                        codecs.append(codec)
                
                if not codecs:
                    self.logger.warning(f"No audio codecs found in episodes for series {series_id}")
                    return None
                
                # Find the most common codec
                from collections import Counter
                codec_counts = Counter(codecs)
                dominant_codec = codec_counts.most_common(1)[0][0]
                
                self.logger.debug(
                    f"Dominant codec for series {series_id}: {dominant_codec} "
                    f"(from {len(codecs)} episodes: {dict(codec_counts)})"
                )
                
                return dominant_codec
                
        except Exception as e:
            self.logger.error(f"Error getting dominant codec for series {series_id}: {e}")
            return None
    
    async def get_video_resolution_info(self, media_item: Dict[str, Any]) -> Optional[str]:
        """Extract resolution and HDR information from media item"""
        try:
            media_sources = media_item.get("MediaSources", [])
            if not media_sources:
                self.logger.warning(f"No media sources found for item {media_item.get('Id')}")
                return None
            
            # Get the first media source (usually the main file)
            media_source = media_sources[0]
            media_streams = media_source.get("MediaStreams", [])
            
            # Find video streams
            video_streams = [stream for stream in media_streams if stream.get("Type") == "Video"]
            
            if not video_streams:
                self.logger.warning(f"No video streams found for item {media_item.get('Id')}")
                return None
            
            # Get the first (primary) video stream
            primary_video = video_streams[0]
            
            # Extract resolution information
            width = primary_video.get("Width")
            height = primary_video.get("Height")
            video_range = primary_video.get("VideoRange", "").upper()
            video_range_type = primary_video.get("VideoRangeType", "").upper()
            
            if not width or not height:
                self.logger.warning(f"No resolution information found for item {media_item.get('Id')}")
                return None
            
            # Determine resolution category
            resolution_info = self._categorize_resolution(width, height, video_range, video_range_type)
            
            if resolution_info:
                self.logger.debug(f"Detected resolution for {media_item.get('Id')}: {resolution_info}")
                return resolution_info
            
            self.logger.warning(f"Could not determine resolution category for item {media_item.get('Id')}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting resolution info: {e}")
            return None
    
    def _categorize_resolution(self, width: int, height: int, video_range: str, video_range_type: str) -> Optional[str]:
        """Categorize resolution and HDR information into standard badge format"""
        try:
            # Determine base resolution using more intelligent logic
            # Many movies have non-standard aspect ratios, so we need to be smarter
            
            # Calculate total pixels for better resolution detection
            total_pixels = width * height
            
            # 4K: 3840x2160 = 8,294,400 pixels (allow some variance for different aspect ratios)
            # But also check width since that's more reliable for widescreen content
            if width >= 3840 or total_pixels >= 7_000_000:  # ~7M pixels = roughly 4K
                base_resolution = "4K"
            # 1080p: 1920x1080 = 2,073,600 pixels 
            # Check if width is 1920+ OR if total pixels suggest 1080p content
            elif width >= 1920 or total_pixels >= 1_800_000:  # ~1.8M pixels = roughly 1080p
                base_resolution = "1080p"
            # 720p: 1280x720 = 921,600 pixels
            elif width >= 1280 or total_pixels >= 800_000:  # ~800K pixels = roughly 720p  
                base_resolution = "720p"
            # Everything else is SD
            else:
                base_resolution = "SD"
            
            # Determine HDR type
            hdr_suffix = ""
            if video_range == "HDR" or video_range_type:
                if "DOLBY" in video_range_type or "DV" in video_range_type:
                    hdr_suffix = " DV"  # Dolby Vision
                elif "HDR10+" in video_range_type or "HDR10PLUS" in video_range_type:
                    hdr_suffix = " HDR10+"
                elif "HDR10" in video_range_type or video_range == "HDR":
                    hdr_suffix = " HDR"
                elif "HDR" in video_range:
                    hdr_suffix = " HDR"
            
            final_resolution = f"{base_resolution}{hdr_suffix}"
            
            self.logger.debug(
                f"Resolution categorization: {width}x{height} ({total_pixels:,} pixels) + range='{video_range}' + type='{video_range_type}' → {final_resolution}"
            )
            
            return final_resolution
            
        except Exception as e:
            self.logger.error(f"Error categorizing resolution: {e}")
            return None
    
    async def get_tv_series_dominant_resolution(self, series_id: str) -> Optional[str]:
        """Get dominant resolution by sampling first 5 episodes of a TV series"""
        try:
            # Use user-specific API pattern for getting episodes
            url = urljoin(
                self.base_url,
                f"/Users/{self.user_id}/Items"
            )
            
            # Get episodes for the series
            params = {
                "ParentId": series_id,
                "IncludeItemTypes": "Episode",
                "Fields": "MediaSources,MediaStreams",
                "Limit": 5,
                "Recursive": "true"
            }
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to get episodes for series {series_id}: HTTP {response.status}")
                    return None
                
                data = await response.json()
                episodes = data.get("Items", [])
                
                if not episodes:
                    self.logger.warning(f"No episodes found for series {series_id}")
                    return None
                
                # Collect resolutions from episodes
                resolutions = []
                for episode in episodes:
                    resolution = await self.get_video_resolution_info(episode)
                    if resolution:
                        resolutions.append(resolution)
                
                if not resolutions:
                    self.logger.warning(f"No resolutions found in episodes for series {series_id}")
                    return None
                
                # Find the most common resolution
                from collections import Counter
                resolution_counts = Counter(resolutions)
                dominant_resolution = resolution_counts.most_common(1)[0][0]
                
                self.logger.debug(
                    f"Dominant resolution for series {series_id}: {dominant_resolution} "
                    f"(from {len(resolutions)} episodes: {dict(resolution_counts)})"
                )
                
                return dominant_resolution
                
        except Exception as e:
            self.logger.error(f"Error getting dominant resolution for series {series_id}: {e}")
            return None
    
    async def upload_poster_image(self, item_id: str, image_path: str) -> bool:
        """Upload processed poster back to Jellyfin to replace original (v1 method)"""
        try:
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
    
    async def _verify_upload(self, item_id: str) -> bool:
        """Verify that the uploaded image is retrievable (v1 method)"""
        try:
            url = urljoin(self.base_url, f"/Items/{item_id}/Images/Primary")
            headers = {"X-Emby-Token": self.api_key}
            
            session = await self._get_session()
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
