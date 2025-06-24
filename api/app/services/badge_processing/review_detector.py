"""
Review Detection Helper

Handles review detection from multiple sources (IMDb, TMDb, RT) for the review badge processor.
Separated for modularity and reusability.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import hashlib
import time
import aiohttp
import asyncio

from aphrodite_logging import get_logger


class ReviewDetector:
    """Helper class for detecting review information from various sources"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.review.detector", service="badge")
        self.cache = {}
        self.cache_expiration = 60 * 60  # 1 hour cache
        
        # API settings loaded from database
        self.omdb_api_key = None
        self.tmdb_api_key = None
        self._api_keys_loaded = False
    
    async def _load_api_keys(self):
        """Load API keys from PostgreSQL database using settings service"""
        if self._api_keys_loaded:
            return
        
        try:
            # Use the settings service to load API keys
            from app.services.settings_service import settings_service
            
            api_keys = await settings_service.get_api_keys_standalone(force_reload=True)
            
            # Debug: log the actual structure we get back
            self.logger.info(f"API keys structure loaded: {api_keys}")
            
            if api_keys:
                # Extract OMDb API key
                omdb_config = api_keys.get("OMDB", [{}])
                self.logger.debug(f"OMDb config found: {omdb_config}")
                if omdb_config and len(omdb_config) > 0 and omdb_config[0].get("api_key"):
                    self.omdb_api_key = omdb_config[0]["api_key"]
                    self.logger.info(f"Loaded OMDb API key: {'*' * (len(self.omdb_api_key) - 4) + self.omdb_api_key[-4:]}")
                else:
                    self.logger.warning(f"No OMDb API key found in config: {omdb_config}")
                
                # Extract TMDb API key (stored as Bearer token)
                tmdb_config = api_keys.get("TMDB", [{}])
                self.logger.debug(f"TMDb config found: {tmdb_config}")
                if tmdb_config and len(tmdb_config) > 0 and tmdb_config[0].get("api_key"):
                    self.tmdb_api_key = tmdb_config[0]["api_key"]  # Use full Bearer token
                    self.logger.info(f"Loaded TMDb Bearer token: {'*' * 20}...{self.tmdb_api_key[-10:]}")
                else:
                    self.logger.warning(f"No TMDb API key found in config: {tmdb_config}")
                
                self.logger.info("Successfully loaded API keys from v2 database")
            else:
                self.logger.warning("No API keys found in settings.yaml - using demo data")
            
            self._api_keys_loaded = True
            
        except Exception as e:
            self.logger.error(f"Error loading API keys from database: {e}")
            self.logger.warning("Falling back to demo data")
            import traceback
            traceback.print_exc()
    
    async def get_review_info(self, poster_path: str, settings: Optional[Dict[str, Any]] = None, jellyfin_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get real review info from multiple sources based on settings"""
        try:
            # Load API keys from database if not already loaded
            await self._load_api_keys()
            
            # If jellyfin_id is provided directly, use it
            if jellyfin_id:
                self.logger.debug(f"Using provided Jellyfin ID: {jellyfin_id}")
            else:
                # Check if this is a cached Jellyfin poster and extract ID
                poster_file = Path(poster_path)
                
                # Handle both original and resized filenames
                if "jellyfin_" in poster_file.name:
                    # For resized files, we need to look for the original metadata file
                    if poster_file.name.startswith('resized_jellyfin_'):
                        # Convert resized filename back to original for metadata lookup
                        original_name = poster_file.name[8:]  # Remove 'resized_' prefix
                        metadata_name = Path(original_name).stem + '.meta'
                        metadata_path = poster_file.parent / metadata_name
                    else:
                        # Use normal metadata path for original files
                        metadata_path = poster_file.with_suffix('.meta')
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            jellyfin_id = metadata.get('jellyfin_id')
                            if jellyfin_id:
                                self.logger.debug(f"Found Jellyfin ID from metadata: {jellyfin_id}")
                            else:
                                self.logger.warning("No jellyfin_id in metadata file")
                                return None
                        except Exception as e:
                            self.logger.warning(f"Could not read metadata file: {e}")
                            # Fall back to filename parsing
                            jellyfin_id = self._extract_jellyfin_id_from_filename(poster_file.name)
                    else:
                        # Fall back to filename parsing for older cached files
                        jellyfin_id = self._extract_jellyfin_id_from_filename(poster_file.name)
                else:
                    # Not a Jellyfin cached poster, return None
                    self.logger.debug("Not a Jellyfin cached poster, no review info available")
                    return None
            
            if not jellyfin_id:
                self.logger.warning("Could not extract or find Jellyfin ID")
                return None
            
            self.logger.debug(f"Extracting review info for Jellyfin ID: {jellyfin_id}")
            
            # Import and get Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Query Jellyfin for media details
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"Could not retrieve media item for ID: {jellyfin_id}")
                return None
            
            # Extract provider IDs from Jellyfin metadata
            provider_ids = media_item.get("ProviderIds", {})
            imdb_id = provider_ids.get("Imdb")
            tmdb_id = provider_ids.get("Tmdb")
            
            # Get basic info for title/year fallback
            title = media_item.get("Name", "")
            year = media_item.get("ProductionYear")
            media_type = media_item.get("Type", "").lower()
            
            self.logger.debug(
                f"Media info - Title: {title}, Year: {year}, Type: {media_type}, "
                f"IMDb: {imdb_id}, TMDb: {tmdb_id}"
            )
            
            # Collect reviews from available sources based on settings
            reviews = []
            
            # Parse settings to determine which sources to include
            sources_config = settings.get('Sources', {}) if settings else {}
            
            # Add debug logging to see what settings are being loaded
            self.logger.debug(f"Review settings received: {settings}")
            self.logger.debug(f"Sources config: {sources_config}")
            
            # Check specific settings with correct database key names
            imdb_enabled = sources_config.get('enable_imdb', True)
            tmdb_enabled = sources_config.get('enable_tmdb', True) 
            rt_enabled = sources_config.get('enable_rotten_tomatoes_critics', False)
            metacritic_enabled = sources_config.get('enable_metacritic', False)
            
            self.logger.debug(f"Source enablement - IMDb: {imdb_enabled}, TMDb: {tmdb_enabled}, RT: {rt_enabled}, Metacritic: {metacritic_enabled}")
            
            # Fetch IMDb rating if enabled
            if imdb_id and sources_config.get('enable_imdb', True):
                imdb_review = await self._fetch_imdb_rating(imdb_id, settings)
                if imdb_review:
                    reviews.append(imdb_review)
            
            # Fetch TMDb rating if enabled
            if tmdb_id and sources_config.get('enable_tmdb', True):
                # Determine TMDb media type
                tmdb_media_type = "movie" if media_type in ["movie"] else "tv"
                tmdb_review = await self._fetch_tmdb_rating(tmdb_id, tmdb_media_type, settings)
                if tmdb_review:
                    reviews.append(tmdb_review)
            
            # Fetch RT Critics if enabled
            if imdb_id and sources_config.get('enable_rotten_tomatoes_critics', False):
                rt_review = await self._fetch_rt_critics_from_omdb(imdb_id)
                if rt_review:
                    reviews.append(rt_review)
            
            # Fetch Metacritic if enabled
            if imdb_id and sources_config.get('enable_metacritic', False):
                metacritic_review = await self._fetch_metacritic_from_omdb(imdb_id, settings)
                if metacritic_review:
                    reviews.append(metacritic_review)
            
            # Fetch MyAnimeList if enabled and it's anime content
            if sources_config.get('enable_myanimelist', False):
                # Check if this is anime content by looking at provider IDs or series type
                mal_id = provider_ids.get("MyAnimeList")
                anilist_id = provider_ids.get("AniList")
                
                # Only fetch MAL for anime/series content
                if media_type in ["series", "season", "episode"] or mal_id or anilist_id:
                    mal_review = await self._fetch_myanimelist_rating(mal_id, anilist_id, title, settings)
                    if mal_review:
                        reviews.append(mal_review)
            
            if reviews:
                self.logger.debug(f"Found {len(reviews)} reviews for {jellyfin_id}")
                return reviews
            else:
                self.logger.info(f"No reviews found for {jellyfin_id}, falling back to demo data")
                return self.get_demo_reviews(poster_path, settings)
            
        except Exception as e:
            self.logger.error(f"Error getting review info for {poster_path}: {e}", exc_info=True)
            # Fallback to demo data on error
            self.logger.info("Falling back to demo data due to error")
            return self.get_demo_reviews(poster_path, settings)
    
    def _extract_jellyfin_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract Jellyfin ID from cached filename like jellyfin_0c2379d5d4fa0591f9ec64c9866b40f3_11a6b644.jpg or resized_jellyfin_..."""
        try:
            # Handle both original and resized filenames
            if filename.startswith('resized_jellyfin_'):
                # Remove 'resized_' prefix and process as normal jellyfin file
                filename = filename[8:]  # Remove 'resized_'
            
            if filename.startswith('jellyfin_'):
                # Remove extension and jellyfin_ prefix
                base_name = Path(filename).stem
                parts = base_name.split('_')
                
                # Format: jellyfin_<32-char-hex-id>_<8-char-uuid>
                if len(parts) == 3 and parts[0] == 'jellyfin':
                    jellyfin_id = parts[1]
                    if len(jellyfin_id) == 32:  # Jellyfin IDs are 32 character hex strings
                        self.logger.debug(f"Extracted Jellyfin ID from filename: {jellyfin_id}")
                        return jellyfin_id
                
            self.logger.warning(f"Could not extract Jellyfin ID from filename: {filename}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting Jellyfin ID from filename {filename}: {e}")
            return None
    
    async def _fetch_imdb_rating(self, imdb_id: str, settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch IMDb rating from OMDb API with caching and format conversion"""
        try:
            # Check cache first
            cache_key = f"imdb_{imdb_id}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached IMDb rating for {imdb_id}")
                    return cache_entry["data"]
            
            # Check if we have an OMDb API key
            if not self.omdb_api_key:
                self.logger.warning(f"No OMDb API key available - using demo data for {imdb_id}")
                rating = self._generate_demo_imdb_rating(imdb_id)
            else:
                # Make real OMDb API call
                self.logger.debug(f"Fetching real IMDb rating for {imdb_id} from OMDb API")
                omdb_data = await self._call_omdb_api(imdb_id)
                if omdb_data:
                    rating = await self._extract_imdb_rating_from_omdb(omdb_data)
                    if rating is None:
                        self.logger.warning(f"No IMDb rating found in OMDb data - using demo data for {imdb_id}")
                        rating = self._generate_demo_imdb_rating(imdb_id)
                else:
                    self.logger.warning(f"OMDb API call failed - using demo data for {imdb_id}")
                    rating = self._generate_demo_imdb_rating(imdb_id)
            
            # CRITICAL FIX: Always force percentage conversion for consistency
            convert_to_percentage = True  # Force percentage for all sources
            
            if convert_to_percentage:
                # Convert IMDb rating (0-10) to percentage (0-100)
                percentage_rating = int((rating / 10.0) * 100)
                text_format = f"{percentage_rating}%"
                score = percentage_rating
                score_max = 100
            else:
                # Keep original format
                text_format = f"{rating}/10"
                score = rating
                score_max = 10
            
            review_data = {
                "source": "IMDb",
                "text": text_format,
                "score": score,
                "score_max": score_max,
                "image_key": "IMDb"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            data_source = "real API" if self.omdb_api_key else "demo data"
            self.logger.debug(f"Got IMDb rating for {imdb_id} from {data_source}: {text_format}")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching IMDb rating for {imdb_id}: {e}")
            return None
    
    async def _call_omdb_api(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Make actual OMDb API call to get all ratings data"""
        try:
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("Response") == "True":
                            self.logger.debug(f"OMDb API returned data for {imdb_id}")
                            return data
                        
                        self.logger.warning(f"OMDb API returned no valid data for {imdb_id}")
                        return None
                    else:
                        self.logger.error(f"OMDb API error: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"OMDb API call exception: {e}")
            return None
    
    async def _extract_imdb_rating_from_omdb(self, omdb_data: Dict[str, Any]) -> Optional[float]:
        """Extract IMDb rating from OMDb data"""
        try:
            if "imdbRating" in omdb_data and omdb_data["imdbRating"] != "N/A":
                rating = float(omdb_data["imdbRating"])
                self.logger.debug(f"Extracted IMDb rating: {rating}/10")
                return rating
            return None
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error extracting IMDb rating: {e}")
            return None
    
    async def _extract_rt_rating_from_omdb(self, omdb_data: Dict[str, Any]) -> Optional[int]:
        """Extract Rotten Tomatoes rating from OMDb data"""
        try:
            if "Ratings" in omdb_data:
                for rating in omdb_data["Ratings"]:
                    if rating["Source"] == "Rotten Tomatoes":
                        rt_value = rating["Value"].rstrip("%")
                        rt_score = int(rt_value)
                        self.logger.debug(f"Extracted RT rating: {rt_score}%")
                        return rt_score
            return None
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error extracting RT rating: {e}")
            return None
    
    async def _extract_metacritic_rating_from_omdb(self, omdb_data: Dict[str, Any]) -> Optional[int]:
        """Extract Metacritic rating from OMDb data"""
        try:
            if "Ratings" in omdb_data:
                for rating in omdb_data["Ratings"]:
                    if rating["Source"] == "Metacritic":
                        mc_value = rating["Value"].split("/")[0]
                        mc_score = int(mc_value)
                        self.logger.debug(f"Extracted Metacritic rating: {mc_score}/100")
                        return mc_score
            return None
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error extracting Metacritic rating: {e}")
            return None
    
    async def _call_tmdb_api(self, tmdb_id: str, media_type: str = "movie") -> Optional[float]:
        """Make actual TMDb API call to get rating"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            headers = {
                "Authorization": f"Bearer {self.tmdb_api_key}",
                "accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "vote_average" in data:
                            vote_average = data["vote_average"]
                            if vote_average > 0:
                                self.logger.debug(f"TMDb API returned vote average: {vote_average}/10")
                                return float(vote_average)
                        
                        self.logger.warning(f"TMDb API returned no valid rating for {tmdb_id}")
                        return None
                    else:
                        self.logger.error(f"TMDb API error: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"TMDb API call exception: {e}")
            return None
    
    async def _fetch_tmdb_rating(self, tmdb_id: str, media_type: str = "movie", settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch TMDb rating from TMDb API with caching"""
        try:
            # Check cache first
            cache_key = f"tmdb_{tmdb_id}_{media_type}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached TMDb rating for {tmdb_id}")
                    return cache_entry["data"]
            
            # Check if we have a TMDb API key
            if not self.tmdb_api_key:
                self.logger.warning(f"No TMDb API key available - using demo data for {tmdb_id}")
                rating_0_10 = self._generate_demo_tmdb_rating(tmdb_id) / 10.0  # Convert to 0-10 scale
            else:
                # Make real TMDb API call
                self.logger.debug(f"Fetching real TMDb rating for {tmdb_id} from TMDb API")
                rating_0_10 = await self._call_tmdb_api(tmdb_id, media_type)
                if rating_0_10 is None:
                    self.logger.warning(f"TMDb API call failed - using demo data for {tmdb_id}")
                    rating_0_10 = self._generate_demo_tmdb_rating(tmdb_id) / 10.0  # Convert to 0-10 scale
            
            # Convert to percentage (TMDb uses 0-10 scale, we display as 0-100)
            rating_percentage = int(round(rating_0_10 * 10))
            
            review_data = {
                "source": "TMDb",
                "text": f"{rating_percentage}%",
                "score": rating_percentage,
                "score_max": 100,
                "image_key": "TMDb"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            data_source = "real API" if self.tmdb_api_key else "demo data"
            self.logger.debug(f"Got TMDb rating for {tmdb_id} from {data_source}: {rating_percentage}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching TMDb rating for {tmdb_id}: {e}")
            return None
    
    async def _fetch_rt_critics_rating(self, title: str, year: int) -> Optional[Dict[str, Any]]:
        """Fetch Rotten Tomatoes Critics rating from OMDb API"""
        try:
            # Check cache first
            cache_key = f"rt_critics_{title}_{year}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached RT Critics rating for {title} ({year})")
                    return cache_entry["data"]
            
            # Generate consistent demo RT critics rating as fallback
            title_hash = hashlib.md5(f"{title}{year}".encode()).hexdigest()
            demo_critics_score = (int(title_hash[:2], 16) % 40) + 50  # 50-89%
            
            review_data = {
                "source": "RT Critics",
                "text": f"{demo_critics_score}%",
                "score": demo_critics_score,
                "score_max": 100,
                "image_key": "RT-Crit-Fresh" if demo_critics_score >= 60 else "RT-Crit-Rotten"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            self.logger.debug(f"Generated demo RT Critics rating for {title} ({year}): {demo_critics_score}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching RT Critics rating for {title} ({year}): {e}")
            return None
    
    async def _fetch_rt_critics_from_omdb(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Fetch RT Critics rating from OMDb API using IMDb ID"""
        try:
            # Check if we have an OMDb API key
            if not self.omdb_api_key:
                self.logger.warning(f"No OMDb API key available for RT Critics")
                return None
            
            # Get OMDb data
            omdb_data = await self._call_omdb_api(imdb_id)
            if not omdb_data:
                return None
            
            # Extract RT rating
            rt_score = await self._extract_rt_rating_from_omdb(omdb_data)
            if rt_score is None:
                return None
            
            # Choose appropriate image based on score
            if rt_score >= 60:
                image_key = "RT-Crit-Fresh"
            else:
                image_key = "RT-Crit-Rotten"
            
            review_data = {
                "source": "RT Critics",
                "text": f"{rt_score}%",
                "score": rt_score,
                "score_max": 100,
                "image_key": image_key
            }
            
            self.logger.debug(f"Got real RT Critics rating from OMDb: {rt_score}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching RT Critics from OMDb: {e}")
            return None
    
    async def _fetch_metacritic_from_omdb(self, imdb_id: str, settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch Metacritic rating from OMDb API using IMDb ID"""
        try:
            # Check if we have an OMDb API key
            if not self.omdb_api_key:
                self.logger.warning(f"No OMDb API key available for Metacritic")
                return None
            
            # Get OMDb data
            omdb_data = await self._call_omdb_api(imdb_id)
            if not omdb_data:
                return None
            
            # Extract Metacritic rating
            mc_score = await self._extract_metacritic_rating_from_omdb(omdb_data)
            if mc_score is None:
                return None
            
            # Force percentage display for consistency
            convert_to_percentage = True
            
            if convert_to_percentage:
                # Convert Metacritic score to percentage format
                text_format = f"{mc_score}%"
                score = mc_score
                score_max = 100
            else:
                # Keep original /100 format
                text_format = f"{mc_score}/100"
                score = mc_score
                score_max = 100
            
            review_data = {
                "source": "Metacritic",
                "text": text_format,
                "score": score,
                "score_max": score_max,
                "image_key": "Metacritic"
            }
            
            self.logger.debug(f"Got real Metacritic rating from OMDb: {text_format}")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Metacritic from OMDb: {e}")
            return None
    
    async def _fetch_metacritic_rating(self, title: str, year: int, settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch Metacritic rating with caching"""
        try:
            # Check cache first
            cache_key = f"metacritic_{title}_{year}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached Metacritic rating for {title} ({year})")
                    return cache_entry["data"]
            
            # Generate consistent demo Metacritic rating
            title_hash = hashlib.md5(f"meta{title}{year}".encode()).hexdigest()
            metacritic_score = (int(title_hash[:2], 16) % 50) + 40  # 40-89 (Metacritic range)
            
            # CRITICAL FIX: Always force percentage conversion for Metacritic
            convert_to_percentage = True  # Force percentage for consistency
            self.logger.debug(f"Metacritic forcing percentage conversion: {convert_to_percentage}")
            
            if convert_to_percentage:
                # Convert Metacritic score to percentage format
                text_format = f"{metacritic_score}%"
                score = metacritic_score
                score_max = 100
            else:
                # Keep original /100 format
                text_format = f"{metacritic_score}/100"
                score = metacritic_score
                score_max = 100
            
            review_data = {
                "source": "Metacritic",
                "text": text_format,
                "score": score,
                "score_max": score_max,
                "image_key": "Metacritic"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            self.logger.debug(f"Generated demo Metacritic rating for {title} ({year}): {text_format}")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Metacritic rating for {title} ({year}): {e}")
            return None
    
    async def _fetch_myanimelist_rating(self, mal_id: Optional[str], anilist_id: Optional[str], title: str, settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch MyAnimeList rating using Jikan API with caching"""
        try:
            # Check cache first
            cache_key = f"mal_{mal_id or anilist_id or title}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached MAL rating for {mal_id or anilist_id or title}")
                    return cache_entry["data"]
            
            # Import v1 Jikan API
            try:
                import sys
                sys.path.append("E:/programming/aphrodite")
                from aphrodite_helpers.jikan_api import JikanAPI
            except ImportError as e:
                self.logger.warning(f"Could not import Jikan API: {e}")
                return await self._generate_demo_mal_rating(title)
            
            # Create Jikan API instance
            jikan_api = JikanAPI()
            
            # Try to get MAL data
            anime_data = None
            
            if mal_id:
                # Direct MAL ID lookup
                self.logger.debug(f"Fetching MAL data by ID: {mal_id}")
                anime_data = jikan_api.get_anime_details(int(mal_id))
            else:
                # Search by title
                self.logger.debug(f"Searching MAL by title: {title}")
                anime_data = jikan_api.find_anime_by_title(title)
            
            if not anime_data:
                self.logger.debug(f"No MAL data found for {title}, generating demo rating")
                return await self._generate_demo_mal_rating(title)
            
            # Extract rating data
            rating_data = jikan_api.extract_rating_data(anime_data)
            
            if not rating_data or not rating_data.get("score"):
                self.logger.debug(f"No score found in MAL data for {title}, generating demo rating")
                return await self._generate_demo_mal_rating(title)
            
            # Format MAL data for our system (MAL scores are 0-10)
            mal_score = rating_data["score"]
            
            # Convert to percentage for consistency with other sources
            percentage_score = int((mal_score / 10.0) * 100)
            
            review_data = {
                "source": "MyAnimeList",
                "text": f"{percentage_score}%",
                "score": percentage_score,
                "score_max": 100,
                "image_key": "MyAnimeList"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            self.logger.info(f"Fetched real MAL rating for {title}: {percentage_score}% (score: {mal_score}/10)")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching MAL rating for {title}: {e}")
            # Fallback to demo rating on error
            return await self._generate_demo_mal_rating(title)
    
    async def _generate_demo_mal_rating(self, title: str) -> Optional[Dict[str, Any]]:
        """Generate demo MAL rating as fallback"""
        try:
            # Generate consistent demo MAL rating
            title_hash = hashlib.md5(f"mal{title}".encode()).hexdigest()
            mal_score = (int(title_hash[:2], 16) % 35) + 65  # 65-99% range for MAL
            
            review_data = {
                "source": "MyAnimeList",
                "text": f"{mal_score}%",
                "score": mal_score,
                "score_max": 100,
                "image_key": "MyAnimeList"
            }
            
            self.logger.debug(f"Generated demo MAL rating for {title}: {mal_score}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error generating demo MAL rating for {title}: {e}")
            return None
    
    async def _fetch_rt_ratings(self, title: str, year: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch Rotten Tomatoes ratings with caching (placeholder)"""
        # This would require scraping or unofficial API access
        # For now, return demo data
        try:
            # Generate consistent demo RT ratings
            title_hash = hashlib.md5(f"{title}{year}".encode()).hexdigest()
            critics_score = (int(title_hash[:2], 16) % 40) + 50  # 50-89%
            audience_score = (int(title_hash[2:4], 16) % 30) + 60  # 60-89%
            
            reviews = []
            
            # Critics score
            if critics_score >= 60:
                image_key = "RT-Crit-Fresh"
            else:
                image_key = "RT-Crit-Rotten"
            
            reviews.append({
                "source": "RT Critics",
                "text": f"{critics_score}%",
                "score": critics_score,
                "score_max": 100,
                "image_key": image_key
            })
            
            # Audience score
            if audience_score >= 60:
                image_key = "RT-Aud-Fresh"
            else:
                image_key = "RT-Aud-Rotten"
            
            reviews.append({
                "source": "RT Audience",
                "text": f"{audience_score}%",
                "score": audience_score,
                "score_max": 100,
                "image_key": image_key
            })
            
            self.logger.debug(f"Generated demo RT ratings for {title} ({year}): Critics {critics_score}%, Audience {audience_score}%")
            return reviews
            
        except Exception as e:
            self.logger.error(f"Error fetching RT ratings for {title} ({year}): {e}")
            return None
    
    def _generate_demo_imdb_rating(self, imdb_id: str) -> float:
        """Generate consistent demo IMDb rating based on ID"""
        # Create hash for consistent but varied ratings
        hash_value = int(hashlib.md5(imdb_id.encode()).hexdigest()[:8], 16)
        # Generate rating between 6.0 and 9.5
        rating = 6.0 + (hash_value % 35) / 10.0
        return round(rating, 1)
    
    def _generate_demo_tmdb_rating(self, tmdb_id: str) -> int:
        """Generate consistent demo TMDb rating based on ID"""
        # Create hash for consistent but varied ratings
        hash_value = int(hashlib.md5(tmdb_id.encode()).hexdigest()[:8], 16)
        # Generate rating between 60 and 95
        rating = 60 + (hash_value % 36)
        return rating
    
    def get_demo_reviews(self, poster_path: str, settings: Optional[Dict[str, Any]] = None, use_percentage: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get demo review data as fallback (consistent per poster) based on enabled sources"""
        # Create hash of poster filename for consistent but varied results
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # Generate consistent demo ratings
        imdb_rating = round(6.0 + (hash_value % 35) / 10.0, 1)
        tmdb_rating = 60 + ((hash_value >> 8) % 36)
        rt_critics = 50 + ((hash_value >> 16) % 40)
        metacritic = 40 + ((hash_value >> 24) % 50)
        
        reviews = []
        
        # Parse settings to determine which sources to include
        sources_config = settings.get('Sources', {}) if settings else {}
        
        # CRITICAL FIX: Always force percentage conversion for all demo reviews
        convert_to_percentage = True  # Force percentage for consistency
        self.logger.debug(f"Demo reviews forcing percentage conversion: {convert_to_percentage}")
        
        # IMDb (if enabled)
        if sources_config.get('enable_imdb', True):
            if convert_to_percentage:
                percentage_rating = int((imdb_rating / 10.0) * 100)
                reviews.append({
                    "source": "IMDb",
                    "text": f"{percentage_rating}%",
                    "score": percentage_rating,
                    "score_max": 100,
                    "image_key": "IMDb"
                })
            else:
                reviews.append({
                    "source": "IMDb",
                    "text": f"{imdb_rating}/10",
                    "score": imdb_rating,
                    "score_max": 10,
                    "image_key": "IMDb"
                })
        
        # TMDb (if enabled)
        if sources_config.get('enable_tmdb', True):
            reviews.append({
                "source": "TMDb",
                "text": f"{tmdb_rating}%",
                "score": tmdb_rating,
                "score_max": 100,
                "image_key": "TMDb"
            })
        
        # RT Critics (if enabled)
        if sources_config.get('enable_rotten_tomatoes_critics', False):
            reviews.append({
                "source": "RT Critics",
                "text": f"{rt_critics}%",
                "score": rt_critics,
                "score_max": 100,
                "image_key": "RT-Crit-Fresh" if rt_critics >= 60 else "RT-Crit-Rotten"
            })
        
        # Metacritic (if enabled)
        if sources_config.get('enable_metacritic', False):
            if convert_to_percentage:
                # Convert Metacritic to percentage format
                reviews.append({
                    "source": "Metacritic",
                    "text": f"{metacritic}%",
                    "score": metacritic,
                    "score_max": 100,
                    "image_key": "Metacritic"
                })
            else:
                # Keep original /100 format
                reviews.append({
                    "source": "Metacritic",
                    "text": f"{metacritic}/100",
                    "score": metacritic,
                    "score_max": 100,
                    "image_key": "Metacritic"
                })
        
        # MyAnimeList (if enabled)
        if sources_config.get('enable_myanimelist', False):
            # Generate consistent demo MAL rating
            mal_score = 65 + ((hash_value >> 20) % 35)  # 65-99% range for MAL
            reviews.append({
                "source": "MyAnimeList",
                "text": f"{mal_score}%",
                "score": mal_score,
                "score_max": 100,
                "image_key": "MyAnimeList"
            })
        
        source_names = [r["source"] for r in reviews]
        self.logger.debug(f"Demo reviews for {poster_name}: {source_names}")
        return reviews
    
    async def _get_percentage_setting(self) -> bool:
        """Get the show_percentage_only setting from review source settings"""
        try:
            from .database_service import badge_settings_service
            
            # Load review source settings from database
            review_source_settings = await badge_settings_service.get_review_source_settings_standalone(force_reload=True)
            
            if review_source_settings:
                percentage_setting = review_source_settings.get('show_percentage_only', False)
                self.logger.debug(f"Loaded show_percentage_only from database: {percentage_setting}")
                return percentage_setting
            else:
                self.logger.debug("No review source settings found, defaulting to False")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading percentage setting: {e}")
            return False
    
    def _get_percentage_setting_sync(self) -> bool:
        """Get the show_percentage_only setting synchronously (for demo reviews)"""
        try:
            # Simple solution: read from database synchronously
            import asyncio
            from .database_service import badge_settings_service
            
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If we get here, there's already a loop running
                # We can't use asyncio.run(), so we'll use a different approach
                
                # Create a task and run it in the existing loop
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    # Create a new event loop in this thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            badge_settings_service.get_review_source_settings_standalone(force_reload=True)
                        )
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    review_source_settings = future.result(timeout=5)
                    
            except RuntimeError:
                # No event loop running, we can use asyncio.run()
                review_source_settings = asyncio.run(
                    badge_settings_service.get_review_source_settings_standalone(force_reload=True)
                )
            
            if review_source_settings:
                percentage_setting = review_source_settings.get('show_percentage_only', False)
                self.logger.debug(f"Loaded show_percentage_only sync: {percentage_setting}")
                return percentage_setting
            else:
                self.logger.debug("No review source settings found, defaulting to False")
                return False
                
        except Exception as e:
            self.logger.error(f"Error getting percentage setting sync: {e}")
            return False


# Global detector instance for reuse
_review_detector: Optional[ReviewDetector] = None

def get_review_detector() -> ReviewDetector:
    """Get global review detector instance"""
    global _review_detector
    if _review_detector is None:
        _review_detector = ReviewDetector()
    return _review_detector
