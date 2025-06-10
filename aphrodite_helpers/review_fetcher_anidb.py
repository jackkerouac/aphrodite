# AniDB API methods and utilities
import time
import requests
import re
import xml.etree.ElementTree as ET
from aphrodite_helpers.minimal_logger import log_error, log_warning, LoggedOperation

class AnidbMixin:
    def fetch_anidb_ratings(self, anidb_id=None, item_name=None, item_data=None):
        """Fetch ratings from AniDB HTTP API"""
        
        if not self.anidb_settings:
            return None
            
        # If we don't have an AniDB ID, try to find one using auto-discovery
        if not anidb_id and item_data:
            # Try auto-discovery using other provider IDs
            anidb_id = self.discover_anidb_id_from_providers(item_data)
            
            if not anidb_id:
                return None
        elif not anidb_id:
            return None
            
        # Check cache first
        cache_key = f"anidb_{anidb_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        # Fetch rating from AniDB HTTP API
        with LoggedOperation(f"AniDB API call for ID {anidb_id}", "anidb"):
            rating_data = self.fetch_anidb_anime_info_http(anidb_id)
        
        if rating_data:
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": rating_data
            }
            return rating_data
        else:
            return None
    
    def discover_anidb_id_from_providers(self, item_data):
        """Discover AniDB ID using other provider IDs via Kometa's Anime-IDs mapping"""
        if not item_data:
            return None
            
        provider_ids = item_data.get("ProviderIds", {})
        
        # Load Kometa's Anime-IDs mapping
        anime_mapping = self.load_kometa_anime_ids()
        if not anime_mapping:
            return None
            
        # Try different provider IDs to find AniDB mapping
        # Check TMDB TV ID first (most common for anime series)
        tmdb_id = provider_ids.get("Tmdb")
        if tmdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "tmdb_show_id", tmdb_id)
            if anidb_id:
                return anidb_id
                
        # Check IMDB ID
        imdb_id = provider_ids.get("Imdb")
        if imdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "imdb_id", imdb_id)
            if anidb_id:
                return anidb_id
                
        # Check TVDB ID
        tvdb_id = provider_ids.get("Tvdb")
        if tvdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "tvdb_id", tvdb_id)
            if anidb_id:
                return anidb_id
                
        # Check AniList ID
        anilist_id = provider_ids.get("AniList")
        if anilist_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "anilist_id", anilist_id)
            if anidb_id:
                return anidb_id
                
        return None
        
    def load_kometa_anime_ids(self):
        """Load Kometa's Anime-IDs mapping from GitHub"""
        cache_key = "kometa_anime_ids"
        cache_expiration = 60 * 60 * 24  # Cache for 24 hours
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < cache_expiration:
                return cache_entry["data"]
                
        # Fetch from GitHub
        url = "https://raw.githubusercontent.com/Kometa-Team/Anime-IDs/master/anime_ids.json"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            anime_mapping = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": anime_mapping
            }
            
            return anime_mapping
            
        except Exception as e:
            log_error(f"Error loading Kometa Anime-IDs mapping: {e}", "anidb")
            return None
            
    def find_anidb_in_mapping(self, anime_mapping, provider_key, provider_id):
        """Find AniDB ID in the mapping using a specific provider ID"""
        try:
            # Convert provider_id to appropriate type for comparison
            provider_id_str = str(provider_id)
            
            # Search through the mapping where AniDB IDs are the keys
            for anidb_id, anime_data in anime_mapping.items():
                if provider_key in anime_data:
                    mapped_id = anime_data[provider_key]
                    # Handle both string and integer comparisons
                    if str(mapped_id) == provider_id_str:
                        return str(anidb_id)
                        
            return None
            
        except Exception as e:
            log_error(f"Error searching mapping for {provider_key}={provider_id}: {e}", "anidb")
            return None

    def fetch_anidb_anime_info_http(self, anidb_id):
        """Fetch anime information including rating from AniDB HTTP API"""
        try:
            # Add rate limiting to be respectful to AniDB
            time.sleep(2)  # Wait 2 seconds between requests as per API documentation
            
            # Construct the API URL
            base_url = "http://api.anidb.net:9001/httpapi"
            params = {
                "request": "anime",
                "client": self.anidb_settings.get('client_name', 'aphrodite'),
                "clientver": self.anidb_settings.get('version', '1'),
                "protover": "1",
                "aid": anidb_id
            }
            
            headers = {
                "User-Agent": f"{self.anidb_settings.get('client_name', 'aphrodite')}/{self.anidb_settings.get('version', '1')}"
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse the XML response
            rating_data = self.parse_anidb_http_response(response.text, anidb_id)
            
            if rating_data:
                return rating_data
            else:
                return None
                
        except Exception as e:
            log_error(f"Error fetching AniDB anime info via HTTP API: {e}", "anidb")
            return None

    def parse_anidb_http_response(self, xml_content, anidb_id):
        """Parse the AniDB HTTP API XML response to extract rating information"""
        try:
            root = ET.fromstring(xml_content)
            
            # Check if there's an error
            if root.tag == 'error':
                log_warning(f"AniDB API error: {root.text}", "anidb")
                return None
            
            # Look for ratings in the XML response
            ratings_element = root.find('.//ratings')
            if ratings_element is not None:
                # Try to get permanent rating first (most reliable)
                permanent_element = ratings_element.find('permanent')
                if permanent_element is not None and permanent_element.text:
                    try:
                        rating = float(permanent_element.text)
                        return {
                            "anidb_id": anidb_id,
                            "rating": rating,
                            "rating_type": "permanent",
                            "source_url": f"https://anidb.net/anime/{anidb_id}"
                        }
                    except ValueError:
                        pass
                
                # Fallback to temporary rating
                temporary_element = ratings_element.find('temporary')
                if temporary_element is not None and temporary_element.text:
                    try:
                        rating = float(temporary_element.text)
                        return {
                            "anidb_id": anidb_id,
                            "rating": rating,
                            "rating_type": "temporary",
                            "source_url": f"https://anidb.net/anime/{anidb_id}"
                        }
                    except ValueError:
                        pass
                
                # Fallback to review rating
                review_element = ratings_element.find('review')
                if review_element is not None and review_element.text:
                    try:
                        rating = float(review_element.text)
                        return {
                            "anidb_id": anidb_id,
                            "rating": rating,
                            "rating_type": "review",
                            "source_url": f"https://anidb.net/anime/{anidb_id}"
                        }
                    except ValueError:
                        pass
            
            return None
            
        except Exception as e:
            log_error(f"Error parsing AniDB HTTP API response: {e}", "anidb")
            return None

    def clean_title_for_search(self, title):
        """Clean up the title for better AniDB search results"""
        # Remove common suffixes and prefixes that might interfere with search
        title = re.sub(r'\s*\(\d{4}\)\s*', '', title)  # Remove year in parentheses
        title = re.sub(r'\s*Season\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Season X"
        title = re.sub(r'\s*S\d+', '', title)  # Remove "S1", "S2", etc.
        title = re.sub(r'\s*Part\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Part X"
        title = re.sub(r'\s*Vol\.?\s*\d+', '', title, flags=re.IGNORECASE)  # Remove "Vol X"
        
        # Clean up extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
