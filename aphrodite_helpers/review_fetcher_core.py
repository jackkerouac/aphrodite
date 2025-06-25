# Core ReviewFetcher class with basic methods
import os
import time
import yaml
from aphrodite_helpers.minimal_logger import log_error, log_warning

class ReviewFetcher:
    def __init__(self, settings):
        self.settings = settings
        self.jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        self.omdb_settings = settings.get("api_keys", {}).get("OMDB", [{}])[0]
        self.tmdb_settings = settings.get("api_keys", {}).get("TMDB", [{}])[0]
        anidb_list = settings.get("api_keys", {}).get("aniDB", [{}])
        self.anidb_settings = anidb_list[0] if anidb_list else {}
        
        # Setup headers for Jellyfin API calls
        self.jellyfin_headers = {"X-Emby-Token": self.jellyfin_settings.get("api_key", "")}
        
        # Initialize cache
        self.cache = {}
        self.cache_expiration = 60 * 60  # Default 1 hour
        
        # Initialize Jikan API for MyAnimeList
        from aphrodite_helpers.jikan_api import JikanAPI
        self.jikan_api = JikanAPI()
        
        # Load badge settings to get source filtering
        self.badge_settings = self.load_badge_settings()
        
        # Load review badge settings separately for image mappings
        self.review_badge_settings = self.load_review_badge_settings()
    
    def load_badge_settings(self, settings_file="review_source_settings"):
        """Load badge settings from PostgreSQL database (never YAML)"""
        engine = None
        try:
            # Load badge settings from PostgreSQL using synchronous approach
            import json
            from sqlalchemy import create_engine, text
            from app.core.config import get_settings as get_app_settings
            
            # Get database URL from app settings
            app_settings = get_app_settings()
            database_url = app_settings.get_database_url()
            
            # Convert async URL to sync URL
            sync_database_url = database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
            
            # Create synchronous engine with minimal connection pool
            engine = create_engine(
                sync_database_url,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True
            )
            
            # Query the database
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT value FROM system_config WHERE key = :key"),
                    {"key": settings_file}
                )
                row = result.fetchone()
                
                if row and row[0]:
                    badge_settings = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    log_milestone(f"Loaded badge settings from PostgreSQL: {settings_file}", "review_core")
                    return badge_settings
                else:
                    log_warning(f"No badge settings found in database for key: {settings_file}", "review_core")
                    return {}
            
        except Exception as e:
            log_error(f"Could not load badge settings from PostgreSQL database: {e}", "review_core")
            # Return empty dict rather than falling back to YAML
            return {}
        finally:
            # Clean up the engine
            if engine:
                try:
                    engine.dispose()
                except Exception as cleanup_error:
                    log_warning(f"Error disposing database engine: {cleanup_error}", "review_core")
                    
    def load_review_badge_settings(self, settings_file="badge_settings_review.yml"):
        """Load review badge settings from PostgreSQL database for image mappings"""
        engine = None
        try:
            # Load badge settings from PostgreSQL using synchronous approach
            import json
            from sqlalchemy import create_engine, text
            from app.core.config import get_settings as get_app_settings
            
            # Get database URL from app settings
            app_settings = get_app_settings()
            database_url = app_settings.get_database_url()
            
            # Convert async URL to sync URL
            sync_database_url = database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
            
            # Create synchronous engine with minimal connection pool
            engine = create_engine(
                sync_database_url,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True
            )
            
            # Query the database
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT value FROM system_config WHERE key = :key"),
                    {"key": settings_file}
                )
                row = result.fetchone()
                
                if row and row[0]:
                    badge_settings = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    log_milestone(f"Loaded review badge settings from PostgreSQL: {settings_file}", "review_core")
                    return badge_settings
                else:
                    log_warning(f"No review badge settings found in database for key: {settings_file}", "review_core")
                    return {}
            
        except Exception as e:
            log_error(f"Could not load review badge settings from PostgreSQL database: {e}", "review_core")
            # Return empty dict rather than falling back to YAML
            return {}
        finally:
            # Clean up the engine
            if engine:
                try:
                    engine.dispose()
                except Exception as cleanup_error:
                    log_warning(f"Error disposing database engine: {cleanup_error}", "review_core")
        
    def is_source_enabled(self, source_name):
        """Check if a review source is enabled in badge settings"""
        if not self.badge_settings:
            return False
            
        sources_settings = self.badge_settings.get('Sources', {})
        
        # Map source names to their enable keys in settings
        source_key_mapping = {
            'imdb': 'enable_imdb',
            'rotten_tomatoes': 'enable_rotten_tomatoes_critics', 
            'metacritic': 'enable_metacritic',
            'tmdb': 'enable_tmdb',
            'myanimelist': 'enable_myanimelist',
            'anidb': 'enable_anidb',
            'letterboxd': 'enable_letterboxd',
            'trakt': 'enable_trakt',
            'mdblist': 'enable_mdblist'
        }
        
        enable_key = source_key_mapping.get(source_name.lower())
        if enable_key:
            is_enabled = sources_settings.get(enable_key, False)
            log_milestone(f"Source {source_name}: {enable_key} = {is_enabled}", "review_core")
            return is_enabled
        else:
            log_warning(f"Unknown source name: {source_name}", "review_core")
            return False
        
    def get_jellyfin_item_metadata(self, item_id):
        """Retrieve item metadata from Jellyfin"""
        from aphrodite_helpers.get_media_info import get_jellyfin_item_details
        return get_jellyfin_item_details(
            self.jellyfin_settings.get('url'),
            self.jellyfin_settings.get('api_key'),
            self.jellyfin_settings.get('user_id'),
            item_id
        )
    
    def get_imdb_id(self, item_data):
        """Extract IMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get IMDB ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        imdb_id = provider_ids.get("Imdb")
        
        return imdb_id
    
    def get_tmdb_id(self, item_data):
        """Extract TMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get TMDb ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        tmdb_id = provider_ids.get("Tmdb")
        
        return tmdb_id
    
    def get_anidb_id(self, item_data):
        """Extract AniDB ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get AniDB ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        anidb_id = provider_ids.get("AniDb")
        
        return anidb_id

    def get_mal_id(self, item_data):
        """Extract MyAnimeList ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get MAL ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        mal_id = provider_ids.get("MyAnimeList")
        
        return mal_id
    
    def fetch_anidb_ratings(self, anidb_id, item_name=None, item_data=None):
        """Fetch ratings from AniDB (stub implementation)"""
        # AniDB integration not implemented yet
        # Return None to avoid AttributeError
        return None
    
    def fetch_myanimelist_ratings(self, mal_id, item_name=None, item_data=None):
        """Fetch ratings from MyAnimeList (stub implementation)"""
        # MyAnimeList integration not implemented yet
        # Return None to avoid AttributeError
        return None
