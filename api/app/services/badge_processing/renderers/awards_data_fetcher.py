"""
V2 Awards Data Fetcher

Pure V2 awards data collection - no V1 dependencies.
Handles awards detection from metadata and demo generation.
"""

from typing import Dict, Any, Optional, List
import hashlib
from pathlib import Path
import sys
import os

from aphrodite_logging import get_logger


class V2AwardsDataFetcher:
    """Pure V2 awards data collection"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.awards.fetcher.v2", service="badge")
        self._awards_data_source_class = None
        self._helpers_path_added = False
        self._api_settings_cache = None
        self._api_settings_cache_time = 0
        self._cache_expiry = 300  # 5 minutes
    
    async def get_awards_for_media(self, jellyfin_id: str) -> Optional[str]:
        """Get awards data for media using pure V2 methods"""
        try:
            self.logger.info(f"🏆 [V2 AWARDS FETCHER] Getting awards for: {jellyfin_id}")
            
            # Get media metadata from Jellyfin
            media_metadata = await self._get_jellyfin_metadata(jellyfin_id)
            if not media_metadata:
                self.logger.warning(f"⚠️ [V2 AWARDS FETCHER] No metadata found for: {jellyfin_id}")
                return None
            
            # Extract basic info for awards detection
            title = media_metadata.get("Name", "")
            year = media_metadata.get("ProductionYear")
            media_type = media_metadata.get("Type", "").lower()
            provider_ids = media_metadata.get("ProviderIds", {})
            
            self.logger.debug(f"🎬 [V2 AWARDS FETCHER] Media: {title} ({year}) - Type: {media_type}")
            
            # Detect awards from metadata
            awards = await self._detect_awards_from_metadata(
                title, year, provider_ids.get("Tmdb"), 
                provider_ids.get("Imdb"), media_type
            )
            
            if awards:
                self.logger.info(f"🏆 [V2 AWARDS FETCHER] Awards detected: {awards}")
            else:
                self.logger.debug("🚫 [V2 AWARDS FETCHER] No awards detected")
            
            return awards
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error getting awards: {e}", exc_info=True)
            return None
    
    def get_demo_awards(self, poster_path: str) -> Optional[str]:
        """Generate consistent demo awards data"""
        try:
            self.logger.debug(f"🎭 [V2 AWARDS FETCHER] Generating demo awards for: {poster_path}")
            
            # Create hash for consistent results
            poster_name = Path(poster_path).stem
            hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
            
            # 20% chance of awards
            if hash_value % 10 < 2:
                demo_awards = ["oscars", "emmys", "golden", "bafta", "cannes"]
                selected = demo_awards[hash_value % len(demo_awards)]
                self.logger.debug(f"🎭 [V2 AWARDS FETCHER] Demo award: {selected}")
                return selected
            
            self.logger.debug("🚫 [V2 AWARDS FETCHER] No demo awards")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error generating demo awards: {e}")
            return None
    
    async def _get_jellyfin_metadata(self, jellyfin_id: str) -> Optional[Dict[str, Any]]:
        """Get media metadata from Jellyfin service"""
        try:
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            return await jellyfin_service.get_item_details(jellyfin_id)
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error getting Jellyfin metadata: {e}")
            return None
    
    async def _detect_awards_from_metadata(
        self, 
        title: str, 
        year: Optional[int], 
        tmdb_id: Optional[str], 
        imdb_id: Optional[str], 
        media_type: str
    ) -> Optional[str]:
        """Detect awards from media metadata using real award detection"""
        try:
            self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Detecting awards for: {title} ({year})")
            self.logger.debug(f"🔍 [V2 AWARDS FETCHER] IDs - TMDb: {tmdb_id}, IMDb: {imdb_id}")
            
            # Use the real awards detection system
            awards_list = await self._get_real_awards(title, year, tmdb_id, imdb_id, media_type)
            
            if awards_list:
                # Get the primary (most prestigious) award
                primary_award = self._get_primary_award(awards_list)
                self.logger.debug(f"🏆 [V2 AWARDS FETCHER] Primary award detected: {primary_award} (from {awards_list})")
                return primary_award
            
            self.logger.debug("🚫 [V2 AWARDS FETCHER] No awards detected")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error detecting awards: {e}")
            return None
    
    async def _get_real_awards(self, title: str, year: Optional[int], tmdb_id: Optional[str], imdb_id: Optional[str], media_type: str) -> List[str]:
        """Get real awards using the comprehensive awards detection system"""
        try:
            # Ensure AwardsDataSource is imported and available
            if not self._awards_data_source_class:
                self._awards_data_source_class = await self._import_awards_data_source()
            
            if not self._awards_data_source_class:
                self.logger.error("❌ [V2 AWARDS FETCHER] AwardsDataSource not available")
                return []
            
            # Load settings for the awards data source (with caching)
            settings = await self._get_api_settings()
            if not settings:
                self.logger.warning("⚠️ [V2 AWARDS FETCHER] No API settings available for awards detection")
                return []
            
            # Create awards data source
            awards_source = self._awards_data_source_class(settings)
            
            # Get awards based on media type
            if media_type == "movie":
                awards_list = awards_source.get_movie_awards(tmdb_id=tmdb_id, imdb_id=imdb_id, title=title)
            elif media_type in ["series", "season", "episode"]:
                awards_list = awards_source.get_tv_awards(tmdb_id=tmdb_id, imdb_id=imdb_id, title=title)
            else:
                # Try movie first, then TV
                awards_list = awards_source.get_movie_awards(tmdb_id=tmdb_id, imdb_id=imdb_id, title=title)
                if not awards_list:
                    awards_list = awards_source.get_tv_awards(tmdb_id=tmdb_id, imdb_id=imdb_id, title=title)
            
            self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Awards from detection system: {awards_list}")
            return awards_list
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error in real awards detection: {e}")
            return []
    
    async def _import_awards_data_source(self):
        """Import AwardsDataSource class with robust path handling"""
        try:
            # Only add paths once
            if not self._helpers_path_added:
                import sys
                import os
                
                # Try multiple possible paths for the helpers directory
                possible_paths = [
                    '/app/aphrodite_helpers',  # Docker container main path
                    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'aphrodite_helpers'),  # Local development
                    os.path.join('/app', 'aphrodite_helpers'),  # Docker container alternative
                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'aphrodite_helpers'))  # Absolute path
                ]
                
                helpers_path_found = False
                for helpers_path in possible_paths:
                    if os.path.exists(helpers_path):
                        if helpers_path not in sys.path:
                            sys.path.insert(0, helpers_path)
                            self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Added to path: {helpers_path}")
                        helpers_path_found = True
                        break
                
                if not helpers_path_found:
                    self.logger.error("❌ [V2 AWARDS FETCHER] Could not find aphrodite_helpers directory")
                    self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Tried paths: {possible_paths}")
                    return None
                
                self._helpers_path_added = True
            
            # Import the class
            try:
                from awards_data_source import AwardsDataSource
                self.logger.debug(f"✅ [V2 AWARDS FETCHER] Successfully imported AwardsDataSource")
                return AwardsDataSource
            except ImportError as e:
                self.logger.error(f"❌ [V2 AWARDS FETCHER] Failed to import AwardsDataSource: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error importing AwardsDataSource: {e}")
            return None
    
    async def _get_api_settings(self) -> Optional[dict]:
        """Get API settings for awards detection with caching"""
        try:
            import time
            
            # Check cache first
            current_time = time.time()
            if (self._api_settings_cache and 
                current_time - self._api_settings_cache_time < self._cache_expiry):
                self.logger.debug(f"👾 [V2 AWARDS FETCHER] Using cached API settings")
                return self._api_settings_cache
            
            # Try multiple strategies to get database connection in worker
            settings_data = None
            
            # Strategy 1: Try the main session factory
            try:
                from app.core.database import async_session_factory
                if async_session_factory and callable(async_session_factory):
                    async with async_session_factory() as db:
                        settings_data = await self._query_api_settings(db)
                        if settings_data:
                            self.logger.debug(f"✅ [V2 AWARDS FETCHER] API settings loaded via main session factory")
                else:
                    self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Main session factory not available")
            except Exception as e:
                self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Main session factory failed: {e}")
            
            # Strategy 2: Try creating fresh engine connection
            if not settings_data:
                try:
                    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
                    from app.core.config import get_settings
                    
                    app_settings = get_settings()
                    engine = create_async_engine(
                        app_settings.database_url,
                        echo=False,
                        pool_size=1,
                        max_overflow=0
                    )
                    
                    session_factory = async_sessionmaker(
                        engine,
                        class_=AsyncSession,
                        expire_on_commit=False
                    )
                    
                    async with session_factory() as db:
                        settings_data = await self._query_api_settings(db)
                        if settings_data:
                            self.logger.debug(f"✅ [V2 AWARDS FETCHER] API settings loaded via fresh engine")
                    
                    await engine.dispose()
                    
                except Exception as e:
                    self.logger.debug(f"🔍 [V2 AWARDS FETCHER] Fresh engine failed: {e}")
            
            if settings_data:
                # Cache the settings
                self._api_settings_cache = settings_data
                self._api_settings_cache_time = current_time
                return settings_data
            
            self.logger.warning("⚠️ [V2 AWARDS FETCHER] No API keys found in database")
            return None
                    
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error getting API settings: {e}")
            return None
    
    async def _query_api_settings(self, db_session) -> Optional[dict]:
        """Query API settings from database session"""
        try:
            from sqlalchemy import text
            
            # First try the settings.yaml key (main settings)
            result = await db_session.execute(text("SELECT value FROM system_config WHERE key = 'settings.yaml'"))
            row = result.fetchone()
            
            if row:
                settings_data = row[0]
                # The API keys should be in the api_keys section
                if isinstance(settings_data, dict) and 'api_keys' in settings_data:
                    api_settings = {"api_keys": settings_data['api_keys']}
                    return api_settings
            
            # Fallback: try direct api_keys key
            result = await db_session.execute(text("SELECT value FROM system_config WHERE key = 'api_keys'"))
            row = result.fetchone()
            
            if row:
                api_settings = {"api_keys": row[0]}
                return api_settings
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error querying API settings: {e}")
            return None
    
    def _get_primary_award(self, awards_list: List[str]) -> str:
        """Return the most prestigious award from a list"""
        if not awards_list:
            return None
        
        # Award priority order (most prestigious first)
        priority_order = [
            "oscars",      # Academy Awards
            "cannes",      # Cannes Film Festival
            "golden",      # Golden Globes
            "bafta",       # BAFTA Awards
            "emmys",       # Emmy Awards
            "crunchyroll", # Crunchyroll Anime Awards
            "berlinale",   # Berlin International Film Festival
            "venice",      # Venice Film Festival
            "sundance",    # Sundance Film Festival
            "spirit",      # Independent Spirit Awards
            "cesar",       # César Awards
            "choice",      # People's Choice Awards
            "imdb",        # IMDb Top lists
            "letterboxd",  # Letterboxd recognition
            "metacritic",  # Metacritic recognition
            "rotten",      # Rotten Tomatoes recognition
            "netflix"      # Netflix awards/recognition
        ]
        
        # Return the first award in priority order that exists in the list
        for award in priority_order:
            if award in awards_list:
                return award
        
        # If none match priority order, return first available
        return awards_list[0]
