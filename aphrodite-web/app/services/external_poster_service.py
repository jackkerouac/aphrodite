#!/usr/bin/env python3
# aphrodite-web/app/services/external_poster_service.py

import os
import sys
import requests
import time
import logging
import yaml
from PIL import Image
from io import BytesIO
from typing import List, Dict, Optional

# Add the parent directory to the Python path to import aphrodite_helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

try:
    from aphrodite_helpers.settings_validator import load_settings
    from aphrodite_helpers.get_media_info import get_jellyfin_item_details
    logger = logging.getLogger(__name__)
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Import error in external_poster_service: {e}")
    raise

class ExternalPosterService:
    """Service for fetching poster options from external APIs (TMDB, OMDB)"""
    
    def __init__(self):
        logger.info("ExternalPosterService.__init__ starting...")
        
        try:
            logger.info("Loading settings...")
            # Try direct YAML loading instead of load_settings() which might be hanging
            settings_path = '/app/settings.yaml' if os.path.exists('/app/settings.yaml') else 'settings.yaml'
            logger.info(f"Trying to load settings from: {settings_path}")
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.settings = yaml.safe_load(f)
                logger.info("Settings loaded directly from YAML")
            else:
                logger.warning("Settings file not found, using empty settings")
                self.settings = {'api_keys': {}}
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Use empty settings as fallback
            self.settings = {'api_keys': {}}
        
        try:
            logger.info("Extracting API settings...")
            api_keys = self.settings.get("api_keys", {})
            
            # Handle different possible settings structures
            tmdb_config = api_keys.get("TMDB", api_keys.get("tmdb", {}))
            if isinstance(tmdb_config, list) and len(tmdb_config) > 0:
                self.tmdb_settings = tmdb_config[0]
            elif isinstance(tmdb_config, dict):
                self.tmdb_settings = tmdb_config
            else:
                self.tmdb_settings = {}
                
            omdb_config = api_keys.get("OMDB", api_keys.get("omdb", {}))
            if isinstance(omdb_config, list) and len(omdb_config) > 0:
                self.omdb_settings = omdb_config[0]
            elif isinstance(omdb_config, dict):
                self.omdb_settings = omdb_config
            else:
                self.omdb_settings = {}
                
            jellyfin_config = api_keys.get("Jellyfin", api_keys.get("jellyfin", {}))
            if isinstance(jellyfin_config, list) and len(jellyfin_config) > 0:
                self.jellyfin_settings = jellyfin_config[0]
            elif isinstance(jellyfin_config, dict):
                self.jellyfin_settings = jellyfin_config
            else:
                self.jellyfin_settings = {}
                
            logger.info(f"API settings extracted - TMDB: {bool(self.tmdb_settings.get('api_key'))}, OMDB: {bool(self.omdb_settings.get('api_key'))}")
        except Exception as e:
            logger.error(f"Error extracting API settings: {e}")
            # Use empty settings as fallback
            self.tmdb_settings = {}
            self.omdb_settings = {}
            self.jellyfin_settings = {}
        
        try:
            logger.info("Initializing cache...")
            # Cache for API responses
            self.cache = {}
            self.cache_expiration = 60 * 60  # 1 hour
            logger.info("Cache initialized")
        except Exception as e:
            logger.error(f"Error initializing cache: {e}")
            raise
        
        try:
            logger.info("Setting up TMDB configuration...")
            # TMDB image configuration - start with fallback
            self.tmdb_config = {
                "base_url": "https://image.tmdb.org/t/p/",
                "poster_sizes": ["w185", "w342", "w500", "w780", "original"]
            }
            
            # Only try to load from API if we have a key
            if self.tmdb_settings.get("api_key"):
                logger.info("TMDB API key found, will load config on first use")
            else:
                logger.info("No TMDB API key found, using fallback config")
                
            logger.info("TMDB configuration setup complete")
        except Exception as e:
            logger.error(f"Error setting up TMDB configuration: {e}")
            # Fallback config
            self.tmdb_config = {
                "base_url": "https://image.tmdb.org/t/p/",
                "poster_sizes": ["w185", "w342", "w500", "w780", "original"]
            }
        
        logger.info("ExternalPosterService.__init__ completed successfully")
    
    def _load_tmdb_config(self):
        """Load TMDB configuration for image URLs"""
        logger.info("_load_tmdb_config starting...")
        
        if not self.tmdb_settings.get("api_key"):
            logger.info("No TMDB API key found, skipping TMDB config")
            return
        
        logger.info("TMDB API key found, checking cache...")
        cache_key = "tmdb_config"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                self.tmdb_config = cache_entry["data"]
                logger.info("Using cached TMDB config")
                return
        
        try:
            logger.info("Fetching TMDB config from API...")
            url = "https://api.themoviedb.org/3/configuration"
            params = {"api_key": self.tmdb_settings.get("api_key")}
            
            logger.info(f"Making request to: {url}")
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            config = response.json()
            logger.info(f"Received config: {str(config)[:200]}...")
            self.tmdb_config = config.get("images", {})
            
            # Cache the configuration
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": self.tmdb_config
            }
            
            logger.info("Successfully loaded TMDB image configuration")
            
        except Exception as e:
            logger.error(f"Error loading TMDB configuration: {e}")
            # Use fallback configuration
            self.tmdb_config = {
                "base_url": "https://image.tmdb.org/t/p/",
                "poster_sizes": ["w185", "w342", "w500", "w780", "original"]
            }
            logger.info("Using fallback TMDB configuration due to error")
    
    def get_jellyfin_item_metadata(self, item_id: str) -> Optional[Dict]:
        """Get item metadata from Jellyfin"""
        try:
            return get_jellyfin_item_details(
                self.jellyfin_settings.get('url'),
                self.jellyfin_settings.get('api_key'),
                self.jellyfin_settings.get('user_id'),
                item_id
            )
        except Exception as e:
            logger.error(f"Error fetching Jellyfin metadata for {item_id}: {e}")
            return None
    
    def get_poster_sources(self, item_id: str) -> List[Dict]:
        """Get poster options from all available external sources"""
        try:
            # Get item metadata from Jellyfin
            item_data = self.get_jellyfin_item_metadata(item_id)
            if not item_data:
                return []
            
            poster_sources = []
            
            # Get TMDB posters
            tmdb_posters = self._get_tmdb_posters(item_data)
            poster_sources.extend(tmdb_posters)
            
            # Get OMDB poster (if available)
            omdb_poster = self._get_omdb_poster(item_data)
            if omdb_poster:
                poster_sources.append(omdb_poster)
            
            # Sort by quality score (higher is better)
            poster_sources.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            return poster_sources[:20]  # Limit to top 20 results
            
        except Exception as e:
            logger.error(f"Error getting poster sources for {item_id}: {e}")
            return []
    
    def _get_tmdb_posters(self, item_data: Dict) -> List[Dict]:
        """Get poster options from TMDB"""
        if not self.tmdb_settings.get("api_key") or not self.tmdb_config:
            return []
        
        try:
            provider_ids = item_data.get("ProviderIds", {})
            tmdb_id = provider_ids.get("Tmdb")
            
            if not tmdb_id:
                return []
            
            # Determine media type
            media_type = "tv" if item_data.get("Type") == "Series" else "movie"
            
            # Cache key for this request
            cache_key = f"tmdb_images_{tmdb_id}_{media_type}"
            
            # Check cache first
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    return self._format_tmdb_posters(cache_entry["data"], item_data)
            
            # Fetch from TMDB API
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            params = {
                "api_key": self.tmdb_settings.get("api_key"),
                "include_image_language": "en,null"  # English and language-neutral posters
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return self._format_tmdb_posters(data, item_data)
            
        except Exception as e:
            logger.error(f"Error fetching TMDB posters: {e}")
            return []
    
    def _format_tmdb_posters(self, tmdb_data: Dict, item_data: Dict) -> List[Dict]:
        """Format TMDB poster data for frontend consumption"""
        posters = []
        
        for poster in tmdb_data.get("posters", []):
            file_path = poster.get("file_path")
            if not file_path:
                continue
            
            # Generate URLs for different sizes
            base_url = self.tmdb_config.get("base_url", "https://image.tmdb.org/t/p/")
            poster_sizes = self.tmdb_config.get("poster_sizes", ["w185", "w342", "w500", "w780", "original"])
            
            # Use w500 for preview and original for download
            preview_url = f"{base_url}w500{file_path}"
            download_url = f"{base_url}original{file_path}"
            
            # Calculate quality score based on resolution and vote average
            width = poster.get("width", 0)
            height = poster.get("height", 0)
            vote_average = poster.get("vote_average", 0)
            vote_count = poster.get("vote_count", 0)
            
            # Quality score: higher resolution + community rating
            quality_score = (width * height) / 1000000 + (vote_average * vote_count / 100)
            
            # Language preference: English or null gets bonus
            language = poster.get("iso_639_1")
            if language in [None, "en"]:
                quality_score += 10
            
            posters.append({
                "id": f"tmdb_{poster.get('file_path', '').replace('/', '_')}",
                "source": "TMDB",
                "preview_url": preview_url,
                "download_url": download_url,
                "width": width,
                "height": height,
                "aspect_ratio": round(width / height, 2) if height > 0 else 0,
                "language": language or "Universal",
                "vote_average": vote_average,
                "vote_count": vote_count,
                "quality_score": quality_score,
                "file_size_estimate": self._estimate_file_size(width, height),
                "metadata": {
                    "item_name": item_data.get("Name", ""),
                    "tmdb_id": item_data.get("ProviderIds", {}).get("Tmdb"),
                    "file_path": file_path
                }
            })
        
        return posters
    
    def _get_omdb_poster(self, item_data: Dict) -> Optional[Dict]:
        """Get poster from OMDB (single poster per item)"""
        if not self.omdb_settings.get("api_key"):
            return None
        
        try:
            provider_ids = item_data.get("ProviderIds", {})
            imdb_id = provider_ids.get("Imdb")
            
            if not imdb_id:
                return None
            
            # Cache key for this request
            cache_key = f"omdb_poster_{imdb_id}"
            
            # Check cache first
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    return self._format_omdb_poster(cache_entry["data"], item_data)
            
            # Fetch from OMDB API
            url = f"http://www.omdbapi.com/"
            params = {
                "i": imdb_id,
                "apikey": self.omdb_settings.get("api_key")
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return self._format_omdb_poster(data, item_data)
            
        except Exception as e:
            logger.error(f"Error fetching OMDB poster: {e}")
            return None
    
    def _format_omdb_poster(self, omdb_data: Dict, item_data: Dict) -> Optional[Dict]:
        """Format OMDB poster data for frontend consumption"""
        poster_url = omdb_data.get("Poster")
        if not poster_url or poster_url == "N/A":
            return None
        
        # OMDB doesn't provide dimensions, so we estimate
        # Most movie posters are roughly 2:3 ratio
        estimated_width = 600
        estimated_height = 900
        
        return {
            "id": f"omdb_{omdb_data.get('imdbID', 'unknown')}",
            "source": "OMDB",
            "preview_url": poster_url,
            "download_url": poster_url,
            "width": estimated_width,
            "height": estimated_height,
            "aspect_ratio": 0.67,  # 2:3 ratio
            "language": "English",
            "vote_average": 0,  # OMDB doesn't provide image ratings
            "vote_count": 0,
            "quality_score": 5,  # Medium quality score
            "file_size_estimate": self._estimate_file_size(estimated_width, estimated_height),
            "metadata": {
                "item_name": item_data.get("Name", ""),
                "imdb_id": omdb_data.get("imdbID"),
                "year": omdb_data.get("Year")
            }
        }
    
    def _estimate_file_size(self, width: int, height: int) -> str:
        """Estimate file size based on dimensions"""
        if width == 0 or height == 0:
            return "Unknown"
        
        # Rough estimation: (width * height * 3 bytes per pixel) / compression ratio
        pixels = width * height
        estimated_bytes = pixels * 3 / 8  # Assuming JPEG compression
        
        if estimated_bytes < 1024:
            return f"{int(estimated_bytes)} B"
        elif estimated_bytes < 1024 * 1024:
            return f"{int(estimated_bytes / 1024)} KB"
        else:
            return f"{estimated_bytes / (1024 * 1024):.1f} MB"
    
    def download_poster(self, poster_data: Dict, item_id: str) -> Optional[str]:
        """Download a poster from external source and prepare it for Aphrodite processing"""
        try:
            download_url = poster_data.get("download_url")
            if not download_url:
                raise ValueError("No download URL provided")
            
            # Download the image
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Open and process the image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary (removes alpha channel)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to Aphrodite standard (1000px width)
            if image.width != 1000:
                aspect_ratio = image.height / image.width
                new_height = int(1000 * aspect_ratio)
                image = image.resize((1000, new_height), Image.Resampling.LANCZOS)
            
            # Determine save path in external custom directory
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                base_dir = '/app'
            else:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
            
            # Create custom posters directory if it doesn't exist
            custom_dir = os.path.join(base_dir, 'posters', 'custom')
            os.makedirs(custom_dir, exist_ok=True)
            
            # Save the processed image
            filename = f"{item_id}.jpg"
            save_path = os.path.join(custom_dir, filename)
            
            image.save(save_path, "JPEG", quality=95, optimize=True)
            
            logger.info(f"Successfully downloaded and processed poster: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Error downloading poster: {e}")
            return None
    
    def get_poster_metadata(self, poster_id: str) -> Optional[Dict]:
        """Get detailed metadata for a specific poster"""
        # This could be expanded to fetch additional metadata if needed
        # For now, return basic information
        return {
            "id": poster_id,
            "last_accessed": time.time()
        }
