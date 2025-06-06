#!/usr/bin/env python3
# aphrodite_helpers/get_review_info.py

import os
import sys
import argparse
import requests
import json
import time
from requests.exceptions import RequestException

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.get_media_info import get_jellyfin_item_details
from aphrodite_helpers.review_preferences import filter_reviews_by_preferences

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
        
        # Load badge settings to get image mappings
        self.badge_settings = self.load_badge_settings()
    
    def load_badge_settings(self, settings_file="badge_settings_review.yml"):
        """Load badge settings to get image mappings"""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(root_dir, settings_file)
            
            with open(full_path, 'r') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load badge settings: {e}")
            return {}
        
    def get_jellyfin_item_metadata(self, item_id):
        """Retrieve item metadata from Jellyfin"""
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
            print(f"🔍 No item data provided to get_anidb_id")
            return None
        
        # Try to get AniDB ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        print(f"🔍 Provider IDs available: {list(provider_ids.keys())}")
        anidb_id = provider_ids.get("AniDb")
        print(f"🔍 AniDB ID found: {anidb_id}")
        
        return anidb_id
    
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
            print(f"❌ Error fetching OMDB data: {e}")
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
            "api_key": self.tmdb_settings.get("api_key"),
            "language": self.tmdb_settings.get("language", "en")
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return data
        except RequestException as e:
            print(f"❌ Error fetching TMDB data: {e}")
            return None
    
    def fetch_anidb_ratings(self, anidb_id=None, item_name=None, item_data=None):
        """Fetch ratings from AniDB HTTP API
        
        This implementation uses the official AniDB HTTP API to fetch ratings.
        If no AniDB ID is provided, it tries to find one using Kometa's Anime-IDs mapping.
        """
        print(f"🔍 fetch_anidb_ratings called with anidb_id: {anidb_id}, item_name: {item_name}")
        print(f"🔍 anidb_settings available: {bool(self.anidb_settings)}")
        
        if not self.anidb_settings:
            print(f"❌ No AniDB settings found")
            return None
            
        # If we don't have an AniDB ID, try to find one using auto-discovery
        if not anidb_id and item_data:
            print(f"🔍 No AniDB ID provided, trying auto-discovery for: {item_name}")
            
            # Try auto-discovery using other provider IDs
            anidb_id = self.discover_anidb_id_from_providers(item_data)
            
            if not anidb_id:
                print(f"❌ Could not discover AniDB ID for title: {item_name}")
                return None
        elif not anidb_id:
            print(f"❌ No AniDB ID or item data provided")
            return None
            
        print(f"🔍 Fetching AniDB rating for ID: {anidb_id}")
        
        # Check cache first
        cache_key = f"anidb_{anidb_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                print(f"✅ Using cached AniDB data for ID: {anidb_id}")
                return cache_entry["data"]
        
        # Fetch rating from AniDB HTTP API
        rating_data = self.fetch_anidb_anime_info_http(anidb_id)
        
        if rating_data:
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": rating_data
            }
            print(f"✅ Successfully fetched AniDB rating: {rating_data.get('rating', 'N/A')}")
            return rating_data
        else:
            print(f"❌ Failed to fetch AniDB rating for ID: {anidb_id}")
            return None
    
    def discover_anidb_id_from_providers(self, item_data):
        """Discover AniDB ID using other provider IDs via Kometa's Anime-IDs mapping"""
        if not item_data:
            return None
            
        provider_ids = item_data.get("ProviderIds", {})
        print(f"🔍 Available provider IDs: {list(provider_ids.keys())}")
        
        # Load Kometa's Anime-IDs mapping
        anime_mapping = self.load_kometa_anime_ids()
        if not anime_mapping:
            print(f"❌ Could not load Kometa Anime-IDs mapping")
            return None
            
        # Try different provider IDs to find AniDB mapping
        # Check TMDB TV ID first (most common for anime series)
        tmdb_id = provider_ids.get("Tmdb")
        if tmdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "tmdb_show_id", tmdb_id)
            if anidb_id:
                print(f"✅ Found AniDB ID {anidb_id} via TMDB Show ID {tmdb_id}")
                return anidb_id
                
        # Check IMDB ID
        imdb_id = provider_ids.get("Imdb")
        if imdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "imdb_id", imdb_id)
            if anidb_id:
                print(f"✅ Found AniDB ID {anidb_id} via IMDB ID {imdb_id}")
                return anidb_id
                
        # Check TVDB ID
        tvdb_id = provider_ids.get("Tvdb")
        if tvdb_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "tvdb_id", tvdb_id)
            if anidb_id:
                print(f"✅ Found AniDB ID {anidb_id} via TVDB ID {tvdb_id}")
                return anidb_id
                
        # Check AniList ID
        anilist_id = provider_ids.get("AniList")
        if anilist_id:
            anidb_id = self.find_anidb_in_mapping(anime_mapping, "anilist_id", anilist_id)
            if anidb_id:
                print(f"✅ Found AniDB ID {anidb_id} via AniList ID {anilist_id}")
                return anidb_id
                
        print(f"❌ Could not find AniDB mapping for any available provider IDs")
        return None
        
    def load_kometa_anime_ids(self):
        """Load Kometa's Anime-IDs mapping from GitHub"""
        cache_key = "kometa_anime_ids"
        cache_expiration = 60 * 60 * 24  # Cache for 24 hours
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < cache_expiration:
                print(f"✅ Using cached Kometa Anime-IDs mapping")
                return cache_entry["data"]
                
        # Fetch from GitHub
        url = "https://raw.githubusercontent.com/Kometa-Team/Anime-IDs/master/anime_ids.json"
        
        try:
            print(f"🌐 Fetching Kometa Anime-IDs mapping from GitHub...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            anime_mapping = response.json()
            print(f"✅ Successfully loaded {len(anime_mapping)} anime mappings")
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": anime_mapping
            }
            
            return anime_mapping
            
        except Exception as e:
            print(f"❌ Error loading Kometa Anime-IDs mapping: {e}")
            return None
            
    def find_anidb_in_mapping(self, anime_mapping, provider_key, provider_id):
        """Find AniDB ID in the mapping using a specific provider ID
        
        The Kometa mapping format has AniDB IDs as keys, like:
        {
          "15441": {
            "tmdb_show_id": 115036,
            "imdb_id": "tt13266248",
            "tvdb_id": 394243
          }
        }
        """
        try:
            # Convert provider_id to appropriate type for comparison
            provider_id_str = str(provider_id)
            
            # Search through the mapping where AniDB IDs are the keys
            for anidb_id, anime_data in anime_mapping.items():
                if provider_key in anime_data:
                    mapped_id = anime_data[provider_key]
                    # Handle both string and integer comparisons
                    if str(mapped_id) == provider_id_str:
                        print(f"✅ Found match: {provider_key}={provider_id} -> AniDB ID {anidb_id}")
                        return str(anidb_id)
                        
            return None
            
        except Exception as e:
            print(f"❌ Error searching mapping for {provider_key}={provider_id}: {e}")
            return None
    
    def search_anidb_id_via_web_search(self, title):
        """Legacy method - now deprecated in favor of Kometa mapping
        
        Kept for reference but no longer used in the main flow.
        """
        print(f"⚠️ search_anidb_id_via_web_search is deprecated - use discover_anidb_id_from_providers instead")
        return None

    
    def extract_anidb_id_from_search_results_legacy(self, html_content, search_title):
        """Extract AniDB ID from search engine results HTML (legacy method)"""
        import re
        
        try:
            # Look for AniDB URLs in the search results
            # Pattern: anidb.net/anime/12345 or anidb.net/perl-bin/animedb.pl?show=anime&aid=12345
            anidb_patterns = [
                r'anidb\.net/anime/(\d+)',  # Modern URL format
                r'anidb\.net/perl-bin/animedb\.pl\?[^"]*aid=(\d+)',  # Legacy URL format
            ]
            
            found_ids = set()
            
            for pattern in anidb_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    found_ids.add(match)
                    print(f"🔍 Found potential AniDB ID: {match}")
            
            if found_ids:
                # Return the first ID found (most likely to be relevant)
                anidb_id = list(found_ids)[0]
                print(f"✅ Selected AniDB ID: {anidb_id} from search results")
                return anidb_id
            else:
                print(f"❌ No AniDB IDs found in search results")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting AniDB ID from search results: {e}")
            return None
    
    def get_known_anidb_mapping(self, title):
        """Get AniDB ID from known title mappings
        
        Since we need AniDB IDs to use the HTTP API, we maintain a mapping of known titles.
        This can be expanded as needed by manually looking up anime on AniDB.
        """
        # Clean up the title for search
        search_title = self.clean_title_for_search(title)
        
        # Known title to AniDB ID mappings
        # These can be found by manually searching AniDB and noting the IDs from the URLs
        known_mappings = {
            "the apothecary diaries": "17870",
            "kusuriya no hitorigoto": "17870",
            "apothecary diaries": "17870",
            "aesthetica of a rogue hero": "9015",
            "hagure yuusha no aesthetica": "9015",
            "hagure yuusha no estetica": "9015",
            "demon slayer": "14107",
            "kimetsu no yaiba": "14107",
            "attack on titan": "9541",
            "shingeki no kyojin": "9541",
            "spirited away": "112",
            "sen to chihiro no kamikakushi": "112",
            "your name": "11614",
            "kimi no na wa": "11614",
            "weathering with you": "14827",
            "tenki no ko": "14827",
            "princess mononoke": "7",
            "mononoke hime": "7",
            "my neighbor totoro": "320",
            "tonari no totoro": "320",
            "akira": "28",
            "ghost in the shell": "61",
            "kokaku kidotai": "61",
            "cowboy bebop": "23",
            "neon genesis evangelion": "22",
            "shinseiki evangelion": "22",
            "one piece": "69",
            "naruto": "239",
            "dragon ball z": "12",
            "dragon ball": "231",
            "fullmetal alchemist brotherhood": "6107",
            "hagane no renkinjutsushi fullmetal alchemist": "6107",
            "death note": "4563",
            "jujutsu kaisen": "15532",
            "chainsaw man": "16701",
            "spy x family": "16405",
            "mob psycho 100": "12557",
            "one punch man": "11123",
            "86 eighty-six": "15441",
            "86 eighty six": "15441",
            "eighty six": "15441",
            "86": "15441"
        }
        
        # Normalize the search title for lookup
        normalized_title = search_title.lower().strip()
        
        # Handle special characters and alternative formats
        normalized_title = normalized_title.replace('-', ' ').replace('_', ' ')
        # Normalize multiple spaces to single space
        import re
        normalized_title = re.sub(r'\s+', ' ', normalized_title).strip()
        
        # Try exact match first
        if normalized_title in known_mappings:
            return known_mappings[normalized_title]
        
        # Try partial matches (useful for series with different naming)
        for known_title, anidb_id in known_mappings.items():
            if known_title in normalized_title or normalized_title in known_title:
                # Check if it's a reasonable partial match (avoid too short matches)
                if len(known_title) >= 3 and len(normalized_title) >= 3:
                    return anidb_id
        
        return None
    
    def clean_title_for_search(self, title):
        """Clean up the title for better AniDB search results"""
        import re
        
        # Remove common suffixes and prefixes that might interfere with search
        title = re.sub(r'\s*\(\d{4}\)\s*', '', title)  # Remove year in parentheses
        title = re.sub(r'\s*Season\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Season X"
        title = re.sub(r'\s*S\d+', '', title)  # Remove "S1", "S2", etc.
        title = re.sub(r'\s*Part\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Part X"
        title = re.sub(r'\s*Vol\.?\s*\d+', '', title, flags=re.IGNORECASE)  # Remove "Vol X"
        
        # Clean up extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def parse_anidb_search_response(self, html_content, search_title):
        """Parse AniDB search response HTML to extract the anime ID
        
        Note: This method is deprecated due to AniDB's robots.txt restrictions.
        Kept for reference only.
        """
        print(f"⚠️ AniDB web scraping is blocked. Using known mappings instead.")
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
            
            print(f"🌐 Fetching AniDB anime info via HTTP API for ID: {anidb_id}")
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse the XML response
            rating_data = self.parse_anidb_http_response(response.text, anidb_id)
            
            if rating_data:
                return rating_data
            else:
                print(f"❌ Could not extract rating from AniDB HTTP API response")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching AniDB anime info via HTTP API: {e}")
            return None
    
    def parse_anidb_http_response(self, xml_content, anidb_id):
        """Parse the AniDB HTTP API XML response to extract rating information"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            # Check if there's an error
            if root.tag == 'error':
                print(f"❌ AniDB API error: {root.text}")
                return None
            
            # Look for ratings in the XML response
            ratings_element = root.find('.//ratings')
            if ratings_element is not None:
                # Try to get permanent rating first (most reliable)
                permanent_element = ratings_element.find('permanent')
                if permanent_element is not None and permanent_element.text:
                    try:
                        rating = float(permanent_element.text)
                        print(f"✅ Found AniDB permanent rating: {rating}")
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
                        print(f"✅ Found AniDB temporary rating: {rating}")
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
                        print(f"✅ Found AniDB review rating: {rating}")
                        return {
                            "anidb_id": anidb_id,
                            "rating": rating,
                            "rating_type": "review",
                            "source_url": f"https://anidb.net/anime/{anidb_id}"
                        }
                    except ValueError:
                        pass
            
            print(f"❌ Could not find valid rating in AniDB HTTP API response")
            return None
            
        except Exception as e:
            print(f"❌ Error parsing AniDB HTTP API response: {e}")
            return None
    
    def format_review_data(self, review_data, show_details=False):
        """Format the review data from various sources into a structured format"""
        formatted_reviews = []
        
        # Get image mappings from settings
        image_mappings = self.badge_settings.get("ImageBadges", {}).get("image_mapping", {})
        
        # Process OMDB data
        if review_data.get("omdb"):
            omdb_data = review_data["omdb"]
            
            # IMDB Rating - Convert to percentage
            if "imdbRating" in omdb_data and omdb_data["imdbRating"] != "N/A":
                try:
                    # Convert rating from 0-10 scale to percentage
                    imdb_rating = float(omdb_data["imdbRating"])
                    percentage_rating = int(round(imdb_rating * 10))
                    
                    formatted_reviews.append({
                        "source": "IMDb",
                        "rating": f"{percentage_rating}%",  # Display as percentage
                        "original_rating": omdb_data["imdbRating"],  # Keep original for reference
                        "max_rating": "100%",  # Standardize max rating
                        "votes": omdb_data.get("imdbVotes", "N/A"),
                        "image_key": "IMDb"
                    })
                    
                    # Check if in top listings based on rating and votes
                    imdb_votes_str = omdb_data.get("imdbVotes", "0").replace(",", "")
                    imdb_votes = int(imdb_votes_str) if imdb_votes_str.isdigit() else 0
                    
                    if imdb_rating >= 8.0 and imdb_votes >= 100000:
                        # Add top badge based on rating
                        if imdb_rating >= 8.5 and imdb_votes >= 250000:
                            formatted_reviews.append({
                                "source": "IMDb Top 250",
                                "rating": f"{percentage_rating}%",
                                "image_key": "IMDbTop250"
                            })
                        elif imdb_rating >= 8.0 and imdb_votes >= 100000:
                            formatted_reviews.append({
                                "source": "IMDb Top 1000",
                                "rating": f"{percentage_rating}%",
                                "image_key": "IMDbTop1000"
                            })
                except (ValueError, TypeError):
                    pass
                
            # Rotten Tomatoes
            if "Ratings" in omdb_data:
                for rating in omdb_data["Ratings"]:
                    if rating["Source"] == "Rotten Tomatoes":
                        rt_value = rating["Value"].rstrip("%")
                        try:
                            rt_score = int(rt_value)
                            
                            # Determine RT image based on score
                            if rt_score >= 90:
                                image_key = "RT-Crit-Top"
                            elif rt_score >= 60:
                                image_key = "RT-Crit-Fresh"
                            else:
                                image_key = "RT-Crit-Rotten"
                                
                            formatted_reviews.append({
                                "source": "Rotten Tomatoes",
                                "rating": f"{rt_score}%",  # Already a percentage
                                "max_rating": "100%",
                                "image_key": image_key
                            })
                        except ValueError:
                            pass
                    
                    elif rating["Source"] == "Metacritic":
                        mc_value = rating["Value"].split("/")[0]
                        try:
                            mc_score = int(mc_value)
                            
                            # Determine Metacritic image based on score
                            image_key = "Metacritic"
                            if mc_score >= 90:
                                image_key = "MetacriticTop"
                                
                            formatted_reviews.append({
                                "source": "Metacritic",
                                "rating": f"{mc_score}%",  # Convert to percentage format
                                "max_rating": "100%",
                                "image_key": image_key
                            })
                        except ValueError:
                            pass
        
        # Process TMDB data
        if review_data.get("tmdb"):
            tmdb_data = review_data["tmdb"]
            
            if "vote_average" in tmdb_data and tmdb_data["vote_average"]:
                vote_average = tmdb_data["vote_average"]
                vote_count = tmdb_data.get("vote_count", 0)
                
                # Only include if there are enough votes to be meaningful
                if vote_count >= 10:
                    try:
                        # Convert from 0-10 scale to percentage
                        percentage_rating = int(round(float(vote_average) * 10))
                        
                        formatted_reviews.append({
                            "source": "TMDb",
                            "rating": f"{percentage_rating}%",  # Display as percentage
                            "original_rating": f"{vote_average:.1f}",  # Keep original for reference
                            "max_rating": "100%",  # Standardize max rating
                            "votes": vote_count,
                            "image_key": "TMDb"
                        })
                    except (ValueError, TypeError):
                        # Fallback in case of parsing errors
                        formatted_reviews.append({
                            "source": "TMDb",
                            "rating": f"{vote_average:.1f}",
                            "max_rating": "10",
                            "votes": vote_count,
                            "image_key": "TMDb"
                        })
        
        # Process AniDB data (placeholder)
        if review_data.get("anidb"):
            anidb_data = review_data["anidb"]
            
            if "rating" in anidb_data:
                try:
                    # Convert from 0-10 scale to percentage
                    anidb_rating = float(anidb_data["rating"])
                    percentage_rating = int(round(anidb_rating * 10))
                    
                    formatted_reviews.append({
                        "source": "AniDB",
                        "rating": f"{percentage_rating}%",  # Display as percentage
                        "original_rating": anidb_data["rating"],  # Keep original for reference
                        "max_rating": "100%",  # Standardize max rating
                        "image_key": "AniDB"
                    })
                except (ValueError, TypeError):
                    # Fallback to original format if conversion fails
                    formatted_reviews.append({
                        "source": "AniDB",
                        "rating": anidb_data["rating"],
                        "max_rating": "10",
                        "image_key": "AniDB"
                    })
        
        # If show_details is True, return detailed review information
        if show_details:
            return formatted_reviews
        else:
            # Return simplified data for badge creation
            simplified_reviews = []
            for review in formatted_reviews:
                # For badge creation, we use image_key for loading the image
                # and provide the rating as additional text for display if needed
                simplified_reviews.append({
                    "source": review["source"],
                    "image_key": review["image_key"],
                    "text": review.get("rating", "")
                })
            return simplified_reviews
    
    def get_reviews(self, item_id, show_details=False):
        """Get reviews for a media item from all available sources"""
        # Get item data from Jellyfin
        item_data = self.get_jellyfin_item_metadata(item_id)
        if not item_data:
            print("❌ Could not retrieve item data from Jellyfin")
            return []
        
        # Get IDs from different sources
        imdb_id = self.get_imdb_id(item_data)
        tmdb_id = self.get_tmdb_id(item_data)
        anidb_id = self.get_anidb_id(item_data)
        
        # Item type - movie or tv series
        media_type = "tv" if item_data.get("Type") == "Series" else "movie"
        
        # Collect review data from different sources
        review_data = {}
        
        # OMDB (includes IMDb, Rotten Tomatoes, Metacritic)
        if imdb_id and self.omdb_settings.get("api_key"):
            review_data["omdb"] = self.fetch_omdb_ratings(imdb_id)
        
        # TMDB
        if tmdb_id and self.tmdb_settings.get("api_key"):
            review_data["tmdb"] = self.fetch_tmdb_ratings(tmdb_id, media_type)
        
        # AniDB (with auto-discovery fallback)
        print(f"🔍 Checking AniDB: anidb_id={anidb_id}, settings_available={bool(self.anidb_settings)}")
        if self.anidb_settings:
            # Try with AniDB ID first, fall back to auto-discovery
            item_name = item_data.get('Name')
            print(f"🔍 Fetching AniDB ratings (ID: {anidb_id}, Name: {item_name})")
            review_data["anidb"] = self.fetch_anidb_ratings(anidb_id, item_name, item_data)
        else:
            print(f"🔍 Skipping AniDB - no settings available")
        
        # Format the collected review data
        formatted_reviews = self.format_review_data(review_data, show_details)
        
        # Apply user preferences to filter and order reviews
        filtered_reviews = filter_reviews_by_preferences(formatted_reviews, item_data)
        
        return filtered_reviews

def display_reviews(reviews, item_title):
    """Display reviews in a human-readable format"""
    print(f"\n📊 Reviews for: {item_title}\n")
    print("-" * 50)
    
    if not reviews:
        print("No reviews found.")
        return
    
    for review in reviews:
        source = review.get("source", "Unknown")
        rating = review.get("rating", "N/A")
        max_rating = review.get("max_rating", "")
        votes = review.get("votes", "")
        
        print(f"🏆 {source}: {rating}" + (f"/{max_rating}" if max_rating else ""))
        if votes:
            print(f"   Votes: {votes}")
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Get reviews for a Jellyfin media item")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--show-reviews", action="store_true", help="Display reviews in human-readable format")
    parser.add_argument("--settings", default="settings.yaml", help="Settings file path")
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings(args.settings)
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    try:
        # Get item details for title
        jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        item_details = get_jellyfin_item_details(
            jellyfin_settings.get("url", ""),
            jellyfin_settings.get("api_key", ""),
            jellyfin_settings.get("user_id", ""),
            args.itemid
        )
        
        if not item_details:
            print(f"❌ Could not retrieve item details for ID: {args.itemid}")
            return 1
        
        item_title = item_details.get("Name", "Unknown Title")
        
        # Get reviews with detailed information for display
        reviews = review_fetcher.get_reviews(args.itemid, show_details=True)
        
        # Display reviews if requested
        if args.show_reviews:
            display_reviews(reviews, item_title)
        else:
            # Just return the number of reviews found
            print(f"✅ Found {len(reviews)} reviews for '{item_title}'")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
