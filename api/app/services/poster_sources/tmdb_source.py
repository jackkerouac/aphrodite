"""
TMDB Poster Source

Integration with The Movie Database (TMDB) API for poster discovery.
"""

from typing import List, Optional, Dict, Any
from app.models.poster_sources import PosterOption, PosterSource, APIKeyConfig
from .base_source import BasePosterSource
import aiohttp
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.poster_sources.tmdb", service="api")

class TMDBPosterSource(BasePosterSource):
    """TMDB API integration for poster discovery"""
    
    def __init__(self, config: APIKeyConfig):
        super().__init__(config)
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/"
        
    async def search_movie_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for movie posters on TMDB"""
        try:
            # First, search for the movie
            movie_id = await self._search_movie_id(title, year)
            if not movie_id:
                logger.warning(f"No TMDB movie found for: {title} ({year})")
                return []
                
            # Get poster images for the movie
            posters = await self._get_movie_images(movie_id)
            
            # Convert to PosterOption objects
            poster_options = []
            for poster_data in posters:
                poster_option = self._create_poster_option(poster_data, movie_id)
                if poster_option:
                    poster_options.append(poster_option)
                    
            logger.info(f"Found {len(poster_options)} TMDB movie posters for: {title}")
            return poster_options
            
        except Exception as e:
            logger.error(f"Error searching TMDB movie posters for {title}: {e}")
            return []
            
    async def search_tv_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for TV show posters on TMDB"""
        try:
            # First, search for the TV show
            tv_id = await self._search_tv_id(title, year)
            if not tv_id:
                logger.warning(f"No TMDB TV show found for: {title} ({year})")
                return []
                
            # Get poster images for the TV show
            posters = await self._get_tv_images(tv_id)
            
            # Convert to PosterOption objects
            poster_options = []
            for poster_data in posters:
                poster_option = self._create_poster_option(poster_data, tv_id)
                if poster_option:
                    poster_options.append(poster_option)
                    
            logger.info(f"Found {len(poster_options)} TMDB TV posters for: {title}")
            return poster_options
            
        except Exception as e:
            logger.error(f"Error searching TMDB TV posters for {title}: {e}")
            return []
            
    async def _search_movie_id(self, title: str, year: Optional[int] = None) -> Optional[int]:
        """Search for movie ID by title and year"""
        try:
            # TMDB API v3 uses Bearer token authentication
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "query": title,
                "language": "en-US"
            }
            
            if year:
                params["year"] = year
                
            url = f"{self.base_url}/search/movie"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    logger.debug(f"TMDB movie search for '{title}' returned {len(results)} results")
                    
                    if results:
                        # Return the first result's ID
                        movie_id = results[0].get("id")
                        movie_title = results[0].get("title", "Unknown")
                        logger.info(f"Found TMDB movie: '{movie_title}' (ID: {movie_id}) for: {title}")
                        return movie_id
                    else:
                        logger.warning(f"No TMDB movie results for: {title} ({year})")
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB movie search failed: HTTP {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error searching TMDB movie ID for {title}: {e}")
            
        return None
        
    async def _search_tv_id(self, title: str, year: Optional[int] = None) -> Optional[int]:
        """Search for TV show ID by title and year"""
        try:
            # TMDB API v3 uses Bearer token authentication
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "query": title,
                "language": "en-US"
            }
            
            if year:
                params["first_air_date_year"] = year
                
            url = f"{self.base_url}/search/tv"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    logger.debug(f"TMDB TV search for '{title}' returned {len(results)} results")
                    
                    if results:
                        # Return the first result's ID
                        tv_id = results[0].get("id")
                        tv_title = results[0].get("name", "Unknown")
                        logger.info(f"Found TMDB TV show: '{tv_title}' (ID: {tv_id}) for: {title}")
                        return tv_id
                    else:
                        logger.warning(f"No TMDB TV results for: {title} ({year})")
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB TV search failed: HTTP {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error searching TMDB TV ID for {title}: {e}")
            
        return None
        
    async def _get_movie_images(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get poster images for a movie"""
        try:
            # TMDB API v3 uses Bearer token authentication
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Include multiple languages to get more poster options
            params = {
                "include_image_language": "en,null,de,fr,es,it,ja,ko,zh"  # Multiple languages for more variety
            }
            
            url = f"{self.base_url}/movie/{movie_id}/images"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    posters = data.get("posters", [])
                    
                    # Sort by vote average and count for quality, but keep more variety
                    posters.sort(key=lambda x: (x.get("vote_average", 0), x.get("vote_count", 0)), reverse=True)
                    
                    logger.info(f"Retrieved {len(posters)} TMDB movie posters for ID {movie_id}")
                    return posters[:30]  # Increased limit to get more options
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB movie images request failed: HTTP {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting TMDB movie images for ID {movie_id}: {e}")
            
        return []
        
    async def _get_tv_images(self, tv_id: int) -> List[Dict[str, Any]]:
        """Get poster images for a TV show"""
        try:
            # TMDB API v3 uses Bearer token authentication
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Include multiple languages to get more poster options
            params = {
                "include_image_language": "en,null,de,fr,es,it,ja,ko,zh"  # Multiple languages for more variety
            }
            
            url = f"{self.base_url}/tv/{tv_id}/images"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    posters = data.get("posters", [])
                    
                    # Sort by vote average and count for quality, but keep more variety
                    posters.sort(key=lambda x: (x.get("vote_average", 0), x.get("vote_count", 0)), reverse=True)
                    
                    logger.info(f"Retrieved {len(posters)} TMDB TV posters for ID {tv_id}")
                    return posters[:30]  # Increased limit to get more options
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB TV images request failed: HTTP {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting TMDB TV images for ID {tv_id}: {e}")
            
        return []
        
    def _create_poster_option(self, poster_data: Dict[str, Any], tmdb_id: int) -> Optional[PosterOption]:
        """Convert TMDB poster data to PosterOption"""
        try:
            file_path = poster_data.get("file_path")
            if not file_path:
                return None
                
            width = poster_data.get("width", 0)
            height = poster_data.get("height", 0)
            aspect_ratio = width / height if height > 0 else None
            
            # Create URLs for different sizes
            # w500 for thumbnail, original for full size
            thumbnail_url = f"{self.image_base_url}w500{file_path}"
            full_url = f"{self.image_base_url}original{file_path}"
            
            # Calculate quality score
            quality_score = self._calculate_quality_score({
                "width": width,
                "height": height,
                "vote_average": poster_data.get("vote_average", 0),
                "vote_count": poster_data.get("vote_count", 0),
                "language": poster_data.get("iso_639_1"),
                "aspect_ratio": aspect_ratio
            })
            
            # Handle language - null/None means textless poster
            language_code = poster_data.get("iso_639_1")
            if language_code is None:
                language = None  # This represents textless/no language posters
            else:
                language = language_code
            
            return PosterOption(
                id=f"tmdb_{tmdb_id}_{file_path.replace('/', '_')}",
                source=PosterSource.TMDB,
                url=full_url,
                thumbnail_url=thumbnail_url,
                width=width,
                height=height,
                aspect_ratio=aspect_ratio,
                language=language,
                vote_average=poster_data.get("vote_average"),
                vote_count=poster_data.get("vote_count"),
                file_size_estimate=self._estimate_file_size(width, height),
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Error creating TMDB poster option: {e}")
            return None
