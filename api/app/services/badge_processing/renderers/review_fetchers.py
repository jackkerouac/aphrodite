"""
Review Source Fetchers - Individual API implementations
"""

from typing import Dict, Any, Optional
import hashlib
import time
import aiohttp
from aphrodite_logging import get_logger


class SharedOMDbFetcher:
    """Shared OMDb API fetcher to avoid multiple API calls"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.review.fetcher.omdb", service="badge")
        self.cache = {}
        self.cache_expiration = 60 * 60  # 1 hour cache
    
    async def fetch_omdb_data(self, imdb_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Fetch OMDb data once and cache it for all fetchers"""
        try:
            cache_key = f"omdb_{imdb_id}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_expiration:
                    self.logger.debug(f"🔄 [SHARED OMDB] Using cached data for {imdb_id}")
                    return entry["data"]
            
            self.logger.debug(f"🌐 [SHARED OMDB] Making API call for {imdb_id}")
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("Response") == "True":
                            # Cache the result
                            self.cache[cache_key] = {
                                "timestamp": time.time(),
                                "data": data
                            }
                            self.logger.debug(f"✅ [SHARED OMDB] Successfully fetched and cached data for {imdb_id}")
                            return data
                        else:
                            error_msg = data.get('Error', 'Unknown error')
                            if "Request limit reached" in error_msg:
                                self.logger.error(f"🚫 [SHARED OMDB] OMDb API quota exceeded: {error_msg}")
                            else:
                                self.logger.warning(f"⚠️ [SHARED OMDB] OMDb returned error: {error_msg}")
                    elif response.status == 401:
                        try:
                            data = await response.json()
                            error_msg = data.get('Error', 'Unauthorized')
                            if "Request limit reached" in error_msg:
                                self.logger.error(f"🚫 [SHARED OMDB] OMDb API quota exceeded (HTTP 401): {error_msg}")
                            else:
                                self.logger.error(f"🔒 [SHARED OMDB] OMDb API authentication failed: {error_msg}")
                        except:
                            self.logger.error(f"🔒 [SHARED OMDB] OMDb API returned HTTP 401 (likely quota exceeded)")
                    else:
                        self.logger.warning(f"⚠️ [SHARED OMDB] HTTP {response.status} for {imdb_id}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [SHARED OMDB] Error fetching data for {imdb_id}: {e}")
            return None


class BaseReviewFetcher:
    """Base class for review fetchers"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.review.fetcher", service="badge")
        self.cache = {}
        self.cache_expiration = 60 * 60  # 1 hour cache


class IMDbFetcher(BaseReviewFetcher):
    """IMDb rating fetcher using OMDb API"""
    
    async def fetch(self, imdb_id: str, omdb_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch IMDb rating - PRODUCTION: NO DEMO DATA"""
        try:
            cache_key = f"imdb_{imdb_id}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_expiration:
                    return entry["data"]
            
            if not omdb_api_key:
                self.logger.warning(f"❌ No OMDb API key available - using demo data for {imdb_id} (IMDb)")
                return None  # NO DEMO DATA IN PRODUCTION
            
            # Real API call only
            omdb_data = await self._call_omdb_api(imdb_id, omdb_api_key)
            if omdb_data and "imdbRating" in omdb_data and omdb_data["imdbRating"] != "N/A":
                rating = float(omdb_data["imdbRating"])
                percentage = int((rating / 10.0) * 100)
                
                result = {
                    "source": "IMDb",
                    "text": f"{percentage}%", 
                    "score": percentage,
                    "score_max": 100,
                    "image_key": "IMDb"
                }
            else:
                self.logger.info(f"📊 [IMDb] No rating data available for {imdb_id}")
                return None
            
            # Cache result
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching IMDb rating: {e}")
            return None
    
    async def _call_omdb_api(self, imdb_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Make OMDb API call"""
        try:
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("Response") == "True":
                            return data
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OMDb API error: {e}")
            return None


class TMDbFetcher(BaseReviewFetcher):
    """TMDb rating fetcher"""
    
    async def fetch(self, tmdb_id: str, media_type: str = "movie", tmdb_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch TMDb rating - PRODUCTION: NO DEMO DATA"""
        try:
            cache_key = f"tmdb_{tmdb_id}_{media_type}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_expiration:
                    return entry["data"]
            
            if not tmdb_api_key:
                self.logger.warning(f"❌ No TMDb API key available - using demo data for {tmdb_id} (TMDb)")
                return None  # NO DEMO DATA IN PRODUCTION
            
            # Real API call only
            rating = await self._call_tmdb_api(tmdb_id, media_type, tmdb_api_key)
            if rating:
                percentage = int(round(rating * 10))
            else:
                self.logger.info(f"📊 [TMDb] No rating data available for {tmdb_id}")
                return None
            
            result = {
                "source": "TMDb",
                "text": f"{percentage}%",
                "score": percentage,
                "score_max": 100,
                "image_key": "TMDb"
            }
            
            # Cache result
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching TMDb rating: {e}")
            return None
    
    async def _call_tmdb_api(self, tmdb_id: str, media_type: str, api_key: str) -> Optional[float]:
        """Make TMDb API call"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "accept": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "vote_average" in data and data["vote_average"] > 0:
                            return float(data["vote_average"])
            return None
            
        except Exception as e:
            self.logger.error(f"❌ TMDb API error: {e}")
            return None


class RottenTomatoesFetcher(BaseReviewFetcher):
    """Rotten Tomatoes Critics rating fetcher"""
    
    async def fetch(self, imdb_id: str, omdb_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch RT Critics rating from OMDb API"""
        try:
            cache_key = f"rt_{imdb_id}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_expiration:
                    return entry["data"]
            
            result = None
            
            if omdb_api_key:
                # Try real API call first
                omdb_data = await self._call_omdb_api(imdb_id, omdb_api_key)
                if omdb_data and "Ratings" in omdb_data:
                    for rating in omdb_data["Ratings"]:
                        if rating["Source"] == "Rotten Tomatoes":
                            score = int(rating["Value"].rstrip("%"))
                            result = {
                                "source": "RT Critics",
                                "text": f"{score}%",
                                "score": score,
                                "score_max": 100,
                                "image_key": "RT-Crit-Fresh" if score >= 60 else "RT-Crit-Rotten"
                            }
                            break
            
            # Don't show badge if no real data available (common for TV series)
            if not result:
                self.logger.info(f"🍅 [RT FETCHER] No RT Critics data available for {imdb_id} - badge will be skipped")
                return None
            
            # Cache result
            if result:
                self.cache[cache_key] = {
                    "timestamp": time.time(),
                    "data": result
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching RT Critics: {e}")
            return None
    
    async def _call_omdb_api(self, imdb_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Make OMDb API call"""
        try:
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("Response") == "True":
                            return data
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OMDb API error: {e}")
            return None


class MetacriticFetcher(BaseReviewFetcher):
    """Metacritic rating fetcher"""
    
    async def fetch(self, imdb_id: str, omdb_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch Metacritic rating from OMDb API"""
        try:
            cache_key = f"meta_{imdb_id}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_expiration:
                    return entry["data"]
            
            result = None
            
            if omdb_api_key:
                # Try real API call first
                omdb_data = await self._call_omdb_api(imdb_id, omdb_api_key)
                if omdb_data and "Ratings" in omdb_data:
                    for rating in omdb_data["Ratings"]:
                        if rating["Source"] == "Metacritic":
                            score = int(rating["Value"].split("/")[0])
                            result = {
                                "source": "Metacritic",
                                "text": f"{score}%",
                                "score": score,
                                "score_max": 100,
                                "image_key": "Metacritic"
                            }
                            break
            
            # Don't show badge if no real data available (common for TV series)
            if not result:
                self.logger.info(f"🎭 [METACRITIC FETCHER] No Metacritic data available for {imdb_id} - badge will be skipped")
                return None
            
            # Cache result
            if result:
                self.cache[cache_key] = {
                    "timestamp": time.time(),
                    "data": result
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching Metacritic: {e}")
            return None
    
    async def _call_omdb_api(self, imdb_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Make OMDb API call"""
        try:
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("Response") == "True":
                            return data
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OMDb API error: {e}")
            return None


class MDBListFetcher(BaseReviewFetcher):
    """MDBList rating fetcher"""
    
    async def fetch(self, imdb_id: Optional[str], tmdb_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetch MDBList rating (demo implementation)"""
        try:
            # For now, generate demo MDBList rating
            # TODO: Implement real MDBList API when available
            
            # Use IMDb ID or TMDb ID for consistent demo data
            rating_seed = imdb_id or tmdb_id or "unknown"
            hash_val = int(hashlib.md5(f"mdb{rating_seed}".encode()).hexdigest()[:8], 16)
            score = (hash_val % 40) + 50  # 50-89% range
            
            return {
                "source": "MDBList",
                "text": f"{score}%",
                "score": score,
                "score_max": 100,
                "image_key": "MDBList"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching MDBList: {e}")
            return None


class MyAnimeListFetcher(BaseReviewFetcher):
    """MyAnimeList rating fetcher"""
    
    async def fetch(self, mal_id: Optional[str], title: str) -> Optional[Dict[str, Any]]:
        """Fetch MyAnimeList rating (demo implementation)"""
        try:
            # Generate demo MAL rating
            title_hash = hashlib.md5(f"mal{title}".encode()).hexdigest()
            score = (int(title_hash[:2], 16) % 35) + 65  # 65-99% range
            
            return {
                "source": "MyAnimeList",
                "text": f"{score}%",
                "score": score,
                "score_max": 100,
                "image_key": "MyAnimeList"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching MyAnimeList: {e}")
            return None
