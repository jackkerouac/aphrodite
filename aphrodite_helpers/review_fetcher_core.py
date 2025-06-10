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
        
        # Load badge settings to get image mappings
        self.badge_settings = self.load_badge_settings()
    
    def load_badge_settings(self, settings_file="badge_settings_review.yml"):
        """Load badge settings to get image mappings"""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(root_dir, settings_file)
            
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            log_warning(f"Could not load badge settings: {e}", "review_core")
            return {}
        
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
