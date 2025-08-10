# OMDB and TMDB API methods
import time
import requests
from requests.exceptions import RequestException
from aphrodite_helpers.minimal_logger import log_error

class OmdbTmdbMixin:
    def fetch_omdb_ratings(self, imdb_id):
        """Fetch ratings from OMDB API"""
        if not imdb_id or not self.omdb_settings.get("api_key"):
            return None
        
        # Check cache first
        cache_key = f"omdb_{imdb_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        # Fetch from OMDB API
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_settings.get('api_key')}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return data
        except RequestException as e:
            log_error(f"OMDB API error: {e}", "omdb")
            return None
    
    def fetch_tmdb_ratings(self, tmdb_id, media_type="movie"):
        """Fetch ratings from TMDB API"""
        if not tmdb_id or not self.tmdb_settings.get("api_key"):
            return None
        
        # Check cache first
        cache_key = f"tmdb_{tmdb_id}_{media_type}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        # Fetch from TMDB API
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
        params = {
            "language": self.tmdb_settings.get("language", "en")
        }
        headers = {
            "Authorization": f"Bearer {self.tmdb_settings.get('api_key')}",
            "accept": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return data
        except RequestException as e:
            log_error(f"TMDB API error: {e}", "tmdb")
            return None
