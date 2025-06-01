#!/usr/bin/env python3
# aphrodite_helpers/awards_data_source.py

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional, Union
from requests.exceptions import RequestException

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

class AwardsDataSource:
    """Interface with external APIs and databases for comprehensive award detection"""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.tmdb_settings = settings.get("api_keys", {}).get("TMDB", [{}])[0]
        self.omdb_settings = settings.get("api_keys", {}).get("OMDB", [{}])[0]
        
        # API endpoints
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.omdb_base_url = "http://www.omdbapi.com/"
        
        # Cache for API responses
        self.cache = {}
        self.cache_expiration = 60 * 60 * 24 * 7  # Cache for 7 days (awards don't change often)
        
        # Load static awards mapping
        self.static_awards = self.load_static_awards_mapping()
    
    def load_static_awards_mapping(self) -> dict:
        """Load static awards mapping from JSON file"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            awards_file = os.path.join(data_dir, "awards_mapping.json")
            
            if os.path.exists(awards_file):
                with open(awards_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"ℹ️ Awards mapping file not found: {awards_file}")
                return self.get_default_awards_mapping()
        except Exception as e:
            print(f"⚠️ Warning: Could not load awards mapping: {e}")
            return self.get_default_awards_mapping()
    
    def get_default_awards_mapping(self) -> dict:
        """Return default awards mapping with expanded entries"""
        return {
            "movies": {
                # Academy Award Winners (Best Picture)
                "tt0111161": {"awards": ["imdb"], "year": 1994, "title": "The Shawshank Redemption"},
                "tt0068646": {"awards": ["oscars"], "year": 1972, "title": "The Godfather"},
                "tt0071562": {"awards": ["oscars"], "year": 1974, "title": "The Godfather Part II"},
                "tt0468569": {"awards": ["bafta"], "year": 2008, "title": "The Dark Knight"},
                "tt1375666": {"awards": ["bafta"], "year": 2010, "title": "Inception"},
                "tt0167260": {"awards": ["oscars"], "year": 2003, "title": "The Lord of the Rings: The Return of the King"},
                "tt0108052": {"awards": ["oscars"], "year": 1993, "title": "Schindler's List"},
                "tt0137523": {"awards": ["choice"], "year": 1999, "title": "Fight Club"},
                "tt0110912": {"awards": ["cannes", "oscars"], "year": 1994, "title": "Pulp Fiction"},
                "tt0109830": {"awards": ["oscars"], "year": 1994, "title": "Forrest Gump"},
                "tt0120737": {"awards": ["oscars"], "year": 2001, "title": "The Lord of the Rings: The Fellowship of the Ring"},
                "tt0167261": {"awards": ["oscars"], "year": 2002, "title": "The Lord of the Rings: The Two Towers"},
                "tt0073486": {"awards": ["oscars"], "year": 1975, "title": "One Flew Over the Cuckoo's Nest"},
                "tt0099685": {"awards": ["oscars"], "year": 1990, "title": "Goodfellas"},
                "tt0047478": {"awards": ["oscars"], "year": 1954, "title": "Seven Samurai"},
                "tt0076759": {"awards": ["spirit"], "year": 1977, "title": "Star Wars"},
                "tt0102926": {"awards": ["oscars"], "year": 1991, "title": "The Silence of the Lambs"},
                "tt0034583": {"awards": ["oscars"], "year": 1942, "title": "Casablanca"},
                "tt0245429": {"awards": ["cannes"], "year": 2001, "title": "Spirited Away"},
                "tt0120815": {"awards": ["oscars"], "year": 1998, "title": "Saving Private Ryan"},
                "tt0317248": {"awards": ["oscar"], "year": 2004, "title": "City of God"},
                "tt0118799": {"awards": ["oscar"], "year": 1997, "title": "Life Is Beautiful"},
                "tt0114369": {"awards": ["cannes"], "year": 1995, "title": "Seven"},
                "tt0816692": {"awards": ["oscar"], "year": 2008, "title": "The Dark Knight"},
                
                # Cannes Film Festival Winners
                "tt0378194": {"awards": ["cannes"], "year": 2005, "title": "The Pianist"},
                "tt0110413": {"awards": ["cannes"], "year": 1994, "title": "Léon: The Professional"},
                "tt0078748": {"awards": ["spirit"], "year": 1979, "title": "Alien"},
                "tt0078788": {"awards": ["spirit"], "year": 1979, "title": "Apocalypse Now"},
                
                # Golden Globe Winners
                "tt0095016": {"awards": ["golden"], "year": 1988, "title": "Die Hard"},
                "tt0110357": {"awards": ["golden"], "year": 1994, "title": "The Lion King"},
                "tt0133093": {"awards": ["choice"], "year": 1999, "title": "The Matrix"},
                "tt0172495": {"awards": ["golden"], "year": 2001, "title": "Gladiator"},
                
                # BAFTA Winners
                "tt0266697": {"awards": ["bafta"], "year": 2004, "title": "Kill Bill: Vol. 1"},
                "tt0253474": {"awards": ["bafta"], "year": 2002, "title": "The Pianist"},
                "tt0407887": {"awards": ["bafta"], "year": 2004, "title": "The Departed"},
                
                # Independent Spirit Awards
                "tt0361748": {"awards": ["spirit"], "year": 2003, "title": "Inglourious Basterds"},
                "tt0120689": {"awards": ["spirit"], "year": 1998, "title": "The Green Mile"},
                
                # Venice Film Festival
                "tt0993846": {"awards": ["venice"], "year": 2007, "title": "The Wolf of Wall Street"},
                "tt1853728": {"awards": ["venice"], "year": 2013, "title": "Django Unchained"}
            },
            "tv": {
                # Emmy Award Winners (Outstanding Drama Series)
                "tt0944947": {"awards": ["emmys"], "year": 2011, "title": "Game of Thrones"},
                "tt0903747": {"awards": ["emmys"], "year": 2008, "title": "Breaking Bad"},
                "tt2356777": {"awards": ["emmys"], "year": 2014, "title": "True Detective"},
                "tt0386676": {"awards": ["emmys"], "year": 2005, "title": "The Office"},
                "tt0460649": {"awards": ["emmys"], "year": 2007, "title": "How I Met Your Mother"},
                "tt0773262": {"awards": ["emmys"], "year": 2005, "title": "Dexter"},
                "tt1596220": {"awards": ["emmys"], "year": 2009, "title": "The Big Bang Theory"},
                "tt0098904": {"awards": ["emmys"], "year": 1989, "title": "Seinfeld"},
                "tt0412142": {"awards": ["emmys"], "year": 2005, "title": "House"},
                "tt0185906": {"awards": ["emmys"], "year": 1999, "title": "Band of Brothers"},
                "tt0417299": {"awards": ["emmys"], "year": 2004, "title": "Avatar: The Last Airbender"},
                "tt1475582": {"awards": ["emmys"], "year": 2010, "title": "Sherlock"},
                "tt2467372": {"awards": ["emmys"], "year": 2013, "title": "Brooklyn Nine-Nine"},
                "tt1439629": {"awards": ["emmys"], "year": 2011, "title": "Community"},
                "tt1831164": {"awards": ["emmys"], "year": 2013, "title": "House of Cards"},
                "tt3032476": {"awards": ["emmys"], "year": 2014, "title": "Better Call Saul"},
                "tt4574334": {"awards": ["emmys"], "year": 2016, "title": "Stranger Things"},
                "tt2802850": {"awards": ["emmys"], "year": 2014, "title": "Fargo"},
                "tt0141842": {"awards": ["emmys"], "year": 1999, "title": "The Sopranos"},
                "tt0749451": {"awards": ["emmys"], "year": 2006, "title": "The Crown"},
                "tt2575988": {"awards": ["emmys"], "year": 2014, "title": "Silicon Valley"},
                "tt2707408": {"awards": ["emmys"], "year": 2014, "title": "Narcos"},
                "tt1399664": {"awards": ["emmys"], "year": 2011, "title": "Suits"},
                "tt2861424": {"awards": ["emmys"], "year": 2014, "title": "Rick and Morty"},
                "tt1442449": {"awards": ["emmys"], "year": 2010, "title": "Sherlock"},
                
                # Golden Globe TV Winners
                "tt5753856": {"awards": ["golden"], "year": 2017, "title": "Dark"},
                "tt1442437": {"awards": ["golden"], "year": 2010, "title": "Modern Family"},
                "tt1520211": {"awards": ["golden"], "year": 2010, "title": "The Walking Dead"},
                "tt0773262": {"awards": ["golden"], "year": 2006, "title": "Dexter"},
                
                # Critics Choice TV Winners
                "tt1844624": {"awards": ["choice"], "year": 2011, "title": "American Horror Story"},
                "tt1856010": {"awards": ["choice"], "year": 2013, "title": "House of Cards"},
                "tt2243973": {"awards": ["choice"], "year": 2014, "title": "Hannibal"}
            }
        }
    
    def get_cache_key(self, source: str, identifier: str) -> str:
        """Generate cache key for API responses"""
        return f"{source}_{identifier}"
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get("timestamp", 0)
        return time.time() - cached_time < self.cache_expiration
    
    def cache_data(self, cache_key: str, data: dict):
        """Cache API response data"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def get_cached_data(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached data if valid"""
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        return None
    
    def get_movie_awards_from_tmdb(self, tmdb_id: str) -> List[str]:
        """Get awards for a movie from TMDb API"""
        try:
            cache_key = self.get_cache_key("tmdb_movie", tmdb_id)
            cached_data = self.get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            api_key = self.tmdb_settings.get("api_key")
            if not api_key:
                print("⚠️ TMDb API key not configured")
                return []
            
            # Get movie details including awards keywords
            url = f"{self.tmdb_base_url}/movie/{tmdb_id}"
            params = {
                "api_key": api_key,
                "append_to_response": "keywords,reviews"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            movie_data = response.json()
            awards = self.extract_awards_from_tmdb_data(movie_data)
            
            # Cache the result
            self.cache_data(cache_key, awards)
            return awards
            
        except Exception as e:
            print(f"⚠️ Error fetching TMDb movie awards for ID {tmdb_id}: {e}")
            return []
    
    def get_tv_awards_from_tmdb(self, tmdb_id: str) -> List[str]:
        """Get awards for a TV show from TMDb API"""
        try:
            cache_key = self.get_cache_key("tmdb_tv", tmdb_id)
            cached_data = self.get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            api_key = self.tmdb_settings.get("api_key")
            if not api_key:
                print("⚠️ TMDb API key not configured")
                return []
            
            # Get TV show details including awards keywords
            url = f"{self.tmdb_base_url}/tv/{tmdb_id}"
            params = {
                "api_key": api_key,
                "append_to_response": "keywords,reviews"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            tv_data = response.json()
            awards = self.extract_awards_from_tmdb_data(tv_data)
            
            # Cache the result
            self.cache_data(cache_key, awards)
            return awards
            
        except Exception as e:
            print(f"⚠️ Error fetching TMDb TV awards for ID {tmdb_id}: {e}")
            return []
    
    def get_awards_from_omdb(self, imdb_id: str) -> List[str]:
        """Get awards for a movie/TV show from OMDB API"""
        try:
            cache_key = self.get_cache_key("omdb", imdb_id)
            cached_data = self.get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            api_key = self.omdb_settings.get("api_key")
            if not api_key:
                print("⚠️ OMDB API key not configured")
                return []
            
            params = {
                "apikey": api_key,
                "i": imdb_id,
                "plot": "short"
            }
            
            response = requests.get(self.omdb_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            omdb_data = response.json()
            awards = self.extract_awards_from_omdb_data(omdb_data)
            
            # Cache the result
            self.cache_data(cache_key, awards)
            return awards
            
        except Exception as e:
            print(f"⚠️ Error fetching OMDB awards for IMDb ID {imdb_id}: {e}")
            return []
    
    def extract_awards_from_tmdb_data(self, tmdb_data: dict) -> List[str]:
        """Extract award types from TMDb data"""
        awards = []
        
        # Check for high vote average (potential award winner indicator)
        vote_average = tmdb_data.get("vote_average", 0)
        if vote_average >= 8.5:
            awards.append("imdb")  # High rating suggests recognition
        
        # Check keywords for award mentions
        keywords = tmdb_data.get("keywords", {})
        keyword_list = keywords.get("keywords", []) if "keywords" in keywords else keywords.get("results", [])
        
        for keyword in keyword_list:
            keyword_name = keyword.get("name", "").lower()
            if any(award_term in keyword_name for award_term in ["oscar", "academy", "emmy", "golden globe", "bafta", "cannes"]):
                if "oscar" in keyword_name or "academy" in keyword_name:
                    awards.append("oscars")
                elif "emmy" in keyword_name:
                    awards.append("emmys")
                elif "golden" in keyword_name:
                    awards.append("golden")
                elif "bafta" in keyword_name:
                    awards.append("bafta")
                elif "cannes" in keyword_name:
                    awards.append("cannes")
        
        return list(set(awards))  # Remove duplicates
    
    def extract_awards_from_omdb_data(self, omdb_data: dict) -> List[str]:
        """Extract award types from OMDB data"""
        awards = []
        
        # Check Awards field
        awards_text = omdb_data.get("Awards", "").lower()
        if "n/a" not in awards_text and awards_text:
            if "oscar" in awards_text or "academy award" in awards_text:
                awards.append("oscars")
            if "emmy" in awards_text:
                awards.append("emmys")
            if "golden globe" in awards_text:
                awards.append("golden")
            if "bafta" in awards_text:
                awards.append("bafta")
            if "cannes" in awards_text:
                awards.append("cannes")
        
        # Check high IMDb rating as indicator
        imdb_rating = omdb_data.get("imdbRating", "N/A")
        if imdb_rating != "N/A":
            try:
                rating = float(imdb_rating)
                if rating >= 8.5:
                    awards.append("imdb")
            except ValueError:
                pass
        
        return list(set(awards))  # Remove duplicates
    
    def get_movie_awards(self, tmdb_id: str = None, imdb_id: str = None) -> List[str]:
        """Get awards for a movie from various sources"""
        all_awards = []
        
        # Check static mapping first (most reliable)
        if imdb_id and imdb_id in self.static_awards.get("movies", {}):
            static_awards = self.static_awards["movies"][imdb_id].get("awards", [])
            all_awards.extend(static_awards)
            print(f"✅ Found static awards for {imdb_id}: {static_awards}")
        
        # Check TMDb API
        if tmdb_id:
            tmdb_awards = self.get_movie_awards_from_tmdb(tmdb_id)
            all_awards.extend(tmdb_awards)
            if tmdb_awards:
                print(f"✅ Found TMDb awards for {tmdb_id}: {tmdb_awards}")
        
        # Check OMDB API
        if imdb_id:
            omdb_awards = self.get_awards_from_omdb(imdb_id)
            all_awards.extend(omdb_awards)
            if omdb_awards:
                print(f"✅ Found OMDB awards for {imdb_id}: {omdb_awards}")
        
        return list(set(all_awards))  # Remove duplicates
    
    def get_tv_awards(self, tmdb_id: str = None, imdb_id: str = None) -> List[str]:
        """Get awards for a TV show from various sources"""
        all_awards = []
        
        # Check static mapping first (most reliable)
        if imdb_id and imdb_id in self.static_awards.get("tv", {}):
            static_awards = self.static_awards["tv"][imdb_id].get("awards", [])
            all_awards.extend(static_awards)
            print(f"✅ Found static awards for {imdb_id}: {static_awards}")
        
        # Check TMDb API
        if tmdb_id:
            tmdb_awards = self.get_tv_awards_from_tmdb(tmdb_id)
            all_awards.extend(tmdb_awards)
            if tmdb_awards:
                print(f"✅ Found TMDb awards for {tmdb_id}: {tmdb_awards}")
        
        # Check OMDB API
        if imdb_id:
            omdb_awards = self.get_awards_from_omdb(imdb_id)
            all_awards.extend(omdb_awards)
            if omdb_awards:
                print(f"✅ Found OMDB awards for {imdb_id}: {omdb_awards}")
        
        return list(set(all_awards))  # Remove duplicates
    
    def save_awards_mapping(self):
        """Save current awards mapping to JSON file"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(data_dir, exist_ok=True)
            
            awards_file = os.path.join(data_dir, "awards_mapping.json")
            with open(awards_file, 'w', encoding='utf-8') as f:
                json.dump(self.static_awards, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Awards mapping saved to: {awards_file}")
            
        except Exception as e:
            print(f"❌ Error saving awards mapping: {e}")
