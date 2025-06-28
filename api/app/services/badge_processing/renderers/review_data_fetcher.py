"""
V2 Review Data Fetcher - Main coordinator

Pure V2 review data collection - no V1 dependencies.
Coordinates individual fetchers for each review source.
"""

from typing import Dict, Any, Optional, List
import hashlib
from pathlib import Path

from aphrodite_logging import get_logger
from .review_fetchers import (
    IMDbFetcher, TMDbFetcher, RottenTomatoesFetcher, 
    MetacriticFetcher, MDBListFetcher, MyAnimeListFetcher
)


class V2ReviewDataFetcher:
    """Pure V2 review data collection coordinator"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.review.fetcher.v2", service="badge")
        
        # Initialize individual fetchers
        self.imdb_fetcher = IMDbFetcher()
        self.tmdb_fetcher = TMDbFetcher()
        self.rt_fetcher = RottenTomatoesFetcher()
        self.metacritic_fetcher = MetacriticFetcher()
        self.mdblist_fetcher = MDBListFetcher()
        self.mal_fetcher = MyAnimeListFetcher()
        
        # API keys loaded from PostgreSQL
        self.omdb_api_key = None
        self.tmdb_api_key = None
        self._api_keys_loaded = False
    
    async def get_reviews_for_media(self, jellyfin_id: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get review data for media using pure V2 methods"""
        try:
            self.logger.info(f"🔍 [V2 REVIEW FETCHER] Getting reviews for: {jellyfin_id}")
            
            # Load API keys if not already loaded
            await self._load_api_keys()
            
            # Get media metadata from Jellyfin
            media_metadata = await self._get_jellyfin_metadata(jellyfin_id)
            if not media_metadata:
                self.logger.warning(f"⚠️ [V2 REVIEW FETCHER] No metadata found for: {jellyfin_id}")
                return []
            
            # Extract IDs and basic info
            provider_ids = media_metadata.get("ProviderIds", {})
            imdb_id = provider_ids.get("Imdb")
            tmdb_id = provider_ids.get("Tmdb")
            title = media_metadata.get("Name", "")
            year = media_metadata.get("ProductionYear")
            media_type = media_metadata.get("Type", "").lower()
            
            self.logger.debug(f"🎬 [V2 REVIEW FETCHER] Media: {title} ({year}) - IMDb: {imdb_id}, TMDb: {tmdb_id}")
            
            # Get enabled sources from settings
            sources = settings.get('Sources', {})
            
            # Collect reviews from enabled sources
            reviews = []
            
            # Fetch IMDb rating if enabled
            if imdb_id and sources.get('enable_imdb', True):
                review = await self.imdb_fetcher.fetch(imdb_id, self.omdb_api_key)
                if review:
                    reviews.append(review)
            
            # Fetch TMDb rating if enabled
            if tmdb_id and sources.get('enable_tmdb', True):
                tmdb_media_type = "movie" if media_type == "movie" else "tv"
                review = await self.tmdb_fetcher.fetch(tmdb_id, tmdb_media_type, self.tmdb_api_key)
                if review:
                    reviews.append(review)
            
            # Fetch RT Critics if enabled (default True to match processor defaults)
            if imdb_id and sources.get('enable_rotten_tomatoes_critics', True):
                self.logger.debug(f"🍅 [V2 REVIEW FETCHER] Fetching RT Critics for IMDb: {imdb_id}")
                review = await self.rt_fetcher.fetch(imdb_id, self.omdb_api_key)
                if review:
                    reviews.append(review)
                    self.logger.debug(f"✅ [V2 REVIEW FETCHER] RT Critics: {review['text']}")
                else:
                    self.logger.warning(f"⚠️ [V2 REVIEW FETCHER] RT Critics fetch failed for {imdb_id}")
            
            # Fetch Metacritic if enabled (default True to match processor defaults)
            if imdb_id and sources.get('enable_metacritic', True):
                self.logger.debug(f"🎭 [V2 REVIEW FETCHER] Fetching Metacritic for IMDb: {imdb_id}")
                review = await self.metacritic_fetcher.fetch(imdb_id, self.omdb_api_key)
                if review:
                    reviews.append(review)
                    self.logger.debug(f"✅ [V2 REVIEW FETCHER] Metacritic: {review['text']}")
                else:
                    self.logger.warning(f"⚠️ [V2 REVIEW FETCHER] Metacritic fetch failed for {imdb_id}")
            
            # Fetch MDBList if enabled
            if (imdb_id or tmdb_id) and sources.get('enable_mdblist', False):
                self.logger.debug(f"📊 [V2 REVIEW FETCHER] Fetching MDBList for IMDb: {imdb_id}, TMDb: {tmdb_id}")
                review = await self.mdblist_fetcher.fetch(imdb_id, tmdb_id)
                if review:
                    reviews.append(review)
                    self.logger.debug(f"✅ [V2 REVIEW FETCHER] MDBList: {review['text']}")
                else:
                    self.logger.warning(f"⚠️ [V2 REVIEW FETCHER] MDBList fetch failed for {imdb_id}/{tmdb_id}")
            
            # Fetch MyAnimeList ONLY if enabled (not disabled by default)
            # Check both settings locations for enable_myanimelist
            mal_enabled = sources.get('enable_myanimelist', False)
            # Also check root level settings for override
            if 'enable_myanimelist' in settings:
                mal_enabled = settings.get('enable_myanimelist', False)
            
            if mal_enabled and media_type in ['series', 'season', 'episode']:
                mal_id = provider_ids.get("MyAnimeList")
                review = await self.mal_fetcher.fetch(mal_id, title)
                if review:
                    reviews.append(review)
            
            self.logger.info(f"✅ [V2 REVIEW FETCHER] Found {len(reviews)} reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW FETCHER] Error getting reviews: {e}", exc_info=True)
            return []
    
    async def get_demo_reviews(self, poster_path: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate consistent demo review data"""
        try:
            self.logger.debug(f"🎭 [V2 REVIEW FETCHER] Generating demo reviews for: {poster_path}")
            
            # Create hash for consistent results
            poster_name = Path(poster_path).stem
            hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
            
            # Generate ratings
            imdb_rating = round(6.0 + (hash_value % 35) / 10.0, 1)
            tmdb_rating = 60 + ((hash_value >> 8) % 36)
            rt_critics = 50 + ((hash_value >> 16) % 40)
            metacritic = 40 + ((hash_value >> 24) % 50)
            mal_score = 65 + ((hash_value >> 20) % 35)
            
            # Get enabled sources
            sources = settings.get('Sources', {})
            reviews = []
            
            # For demo/preview purposes, show all enabled sources with demo data
            # Note: In real usage, RT Critics and Metacritic may not be available for TV series
            
            # IMDb and TMDb - usually available for both movies and TV series
            if sources.get('enable_imdb', True):
                percentage_rating = int((imdb_rating / 10.0) * 100)
                reviews.append({
                    "source": "IMDb",
                    "text": f"{percentage_rating}%",
                    "score": percentage_rating,
                    "score_max": 100,
                    "image_key": "IMDb"
                })
            
            if sources.get('enable_tmdb', True):
                reviews.append({
                    "source": "TMDb", 
                    "text": f"{tmdb_rating}%",
                    "score": tmdb_rating,
                    "score_max": 100,
                    "image_key": "TMDb"
                })
            
            # RT Critics and Metacritic - enabled by default to match processor defaults
            if sources.get('enable_rotten_tomatoes_critics', True):
                reviews.append({
                    "source": "RT Critics",
                    "text": f"{rt_critics}%", 
                    "score": rt_critics,
                    "score_max": 100,
                    "image_key": "RT-Crit-Fresh" if rt_critics >= 60 else "RT-Crit-Rotten"
                })
                self.logger.debug(f"📝 [V2 REVIEW FETCHER] Demo RT Critics: {rt_critics}% (may not be available for all content)")
            
            if sources.get('enable_metacritic', True):
                reviews.append({
                    "source": "Metacritic",
                    "text": f"{metacritic}%",
                    "score": metacritic,
                    "score_max": 100,
                    "image_key": "Metacritic"
                })
                self.logger.debug(f"📝 [V2 REVIEW FETCHER] Demo Metacritic: {metacritic}% (may not be available for all content)")
            
            # MDBList if enabled
            if sources.get('enable_mdblist', False):
                mdblist_score = 60 + ((hash_value >> 12) % 30)  # 60-89% range
                reviews.append({
                    "source": "MDBList",
                    "text": f"{mdblist_score}%",
                    "score": mdblist_score,
                    "score_max": 100,
                    "image_key": "MDBList"
                })
            
            # MyAnimeList - check if enabled (should be disabled by default)
            mal_enabled = sources.get('enable_myanimelist', False)
            # Also check root level settings for override
            if 'enable_myanimelist' in settings:
                mal_enabled = settings.get('enable_myanimelist', False)
            
            if mal_enabled:
                reviews.append({
                    "source": "MyAnimeList",
                    "text": f"{mal_score}%",
                    "score": mal_score,
                    "score_max": 100,
                    "image_key": "MyAnimeList"
                })
            
            self.logger.debug(f"🎭 [V2 REVIEW FETCHER] Generated {len(reviews)} demo reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW FETCHER] Error generating demo reviews: {e}", exc_info=True)
            return []
    
    async def _load_api_keys(self):
        """Load API keys from PostgreSQL database"""
        if self._api_keys_loaded:
            return
        
        try:
            from app.services.settings_service import settings_service
            from app.core.database import async_session_factory
            
            # Load settings.yaml from PostgreSQL
            async with async_session_factory() as db:
                settings_yaml = await settings_service.get_settings(
                    "settings.yaml", db, use_cache=True, force_reload=True
                )
            
            if settings_yaml and 'api_keys' in settings_yaml:
                api_keys = settings_yaml['api_keys']
                
                # Extract OMDb API key
                omdb_config = api_keys.get("OMDB", [])
                if omdb_config and len(omdb_config) > 0 and omdb_config[0].get("api_key"):
                    self.omdb_api_key = omdb_config[0]["api_key"]
                    masked_key = '*' * (len(self.omdb_api_key) - 4) + self.omdb_api_key[-4:]
                    self.logger.info(f"✅ [V2 REVIEW FETCHER] Loaded OMDb API key: {masked_key}")
                
                # Extract TMDb API key
                tmdb_config = api_keys.get("TMDB", [])
                if tmdb_config and len(tmdb_config) > 0 and tmdb_config[0].get("api_key"):
                    self.tmdb_api_key = tmdb_config[0]["api_key"]
                    self.logger.info(f"✅ [V2 REVIEW FETCHER] Loaded TMDb Bearer token")
            
            self._api_keys_loaded = True
            
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW FETCHER] Error loading API keys: {e}")
    
    async def _get_jellyfin_metadata(self, jellyfin_id: str) -> Optional[Dict[str, Any]]:
        """Get media metadata from Jellyfin service"""
        try:
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            return await jellyfin_service.get_media_item_by_id(jellyfin_id)
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW FETCHER] Error getting Jellyfin metadata: {e}")
            return None
