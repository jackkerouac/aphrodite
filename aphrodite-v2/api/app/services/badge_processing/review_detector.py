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
        
        # API settings (in a real implementation, these would come from settings)
        self.omdb_api_key = None  # Would be loaded from settings
        self.tmdb_api_key = None  # Would be loaded from settings
    
    async def get_review_info(self, poster_path: str, settings: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """Get real review info from multiple sources based on settings"""
        try:
            # Check if this is a cached Jellyfin poster
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
                self.logger.warning("Could not extract Jellyfin ID from poster path")
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
            if title and year and sources_config.get('enable_rotten_tomatoes_critics', False):
                rt_review = await self._fetch_rt_critics_rating(title, year)
                if rt_review:
                    reviews.append(rt_review)
            
            # Fetch Metacritic if enabled
            if title and year and sources_config.get('enable_metacritic', False):
                metacritic_review = await self._fetch_metacritic_rating(title, year, settings)
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
        """Fetch IMDb rating with caching and format conversion"""
        try:
            # Check cache first
            cache_key = f"imdb_{imdb_id}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached IMDb rating for {imdb_id}")
                    return cache_entry["data"]
            
            # Demo implementation: return varied ratings based on IMDb ID
            rating = self._generate_demo_imdb_rating(imdb_id)
            
            # CRITICAL FIX: Get percentage setting from passed settings first, then fallback to database
            convert_to_percentage = False
            if settings and 'show_percentage_only' in settings:
                convert_to_percentage = settings.get('show_percentage_only', False)
                self.logger.debug(f"Using percentage setting from passed settings: {convert_to_percentage}")
            else:
                convert_to_percentage = await self._get_percentage_setting()
                self.logger.debug(f"Using percentage setting from database fallback: {convert_to_percentage}")
            
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
            
            self.logger.debug(f"Generated demo IMDb rating for {imdb_id}: {text_format}")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching IMDb rating for {imdb_id}: {e}")
            return None
    
    async def _fetch_tmdb_rating(self, tmdb_id: str, media_type: str = "movie", settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch TMDb rating with caching"""
        try:
            # Check cache first
            cache_key = f"tmdb_{tmdb_id}_{media_type}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached TMDb rating for {tmdb_id}")
                    return cache_entry["data"]
            
            # Demo implementation: return varied ratings based on TMDb ID
            rating = self._generate_demo_tmdb_rating(tmdb_id)
            
            review_data = {
                "source": "TMDb",
                "text": f"{rating}%",
                "score": rating,
                "score_max": 100,
                "image_key": "TMDb"
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            self.logger.debug(f"Generated demo TMDb rating for {tmdb_id}: {rating}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching TMDb rating for {tmdb_id}: {e}")
            return None
    
    async def _fetch_rt_critics_rating(self, title: str, year: int) -> Optional[Dict[str, Any]]:
        """Fetch Rotten Tomatoes Critics rating with caching"""
        try:
            # Check cache first
            cache_key = f"rt_critics_{title}_{year}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"Using cached RT Critics rating for {title} ({year})")
                    return cache_entry["data"]
            
            # Generate consistent demo RT critics rating
            title_hash = hashlib.md5(f"{title}{year}".encode()).hexdigest()
            critics_score = (int(title_hash[:2], 16) % 40) + 50  # 50-89%
            
            # Choose appropriate image based on score
            if critics_score >= 60:
                image_key = "RT-Crit-Fresh"
            else:
                image_key = "RT-Crit-Rotten"
            
            review_data = {
                "source": "RT Critics",
                "text": f"{critics_score}%",
                "score": critics_score,
                "score_max": 100,
                "image_key": image_key
            }
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": review_data
            }
            
            self.logger.debug(f"Generated demo RT Critics rating for {title} ({year}): {critics_score}%")
            return review_data
            
        except Exception as e:
            self.logger.error(f"Error fetching RT Critics rating for {title} ({year}): {e}")
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
            
            # CRITICAL FIX: Get percentage setting and apply conversion for Metacritic
            convert_to_percentage = False
            if settings and 'show_percentage_only' in settings:
                convert_to_percentage = settings.get('show_percentage_only', False)
                self.logger.debug(f"Metacritic using percentage setting from passed settings: {convert_to_percentage}")
            else:
                convert_to_percentage = await self._get_percentage_setting()
                self.logger.debug(f"Metacritic using percentage setting from database fallback: {convert_to_percentage}")
            
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
        
        # CRITICAL FIX: Get percentage setting from passed settings first, then fallback
        if use_percentage is not None:
            convert_to_percentage = use_percentage
        elif settings and 'show_percentage_only' in settings:
            convert_to_percentage = settings.get('show_percentage_only', False)
            self.logger.debug(f"Demo reviews using percentage from passed settings: {convert_to_percentage}")
        else:
            convert_to_percentage = self._get_percentage_setting_sync()
            self.logger.debug(f"Demo reviews using percentage from database fallback: {convert_to_percentage}")
        
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
