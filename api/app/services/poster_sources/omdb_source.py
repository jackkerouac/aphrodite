"""
OMDB Poster Source

Integration with Open Movie Database (OMDB) API for poster discovery.
"""

from typing import List, Optional, Dict, Any
from app.models.poster_sources import PosterOption, PosterSource, APIKeyConfig
from .base_source import BasePosterSource
import aiohttp
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.poster_sources.omdb", service="api")

class OMDBPosterSource(BasePosterSource):
    """OMDB API integration for poster discovery"""
    
    def __init__(self, config: APIKeyConfig):
        super().__init__(config)
        self.base_url = "http://www.omdbapi.com/"
        
    async def search_movie_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for movie posters on OMDB"""
        return await self._search_posters(title, "movie", year, imdb_id)
        
    async def search_tv_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for TV show posters on OMDB"""
        return await self._search_posters(title, "series", year, imdb_id)
        
    async def _search_posters(self, title: str, item_type: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for posters on OMDB"""
        try:
            # Build search parameters
            params = {
                "apikey": self.config.api_key,
                "type": item_type,
                "plot": "short"
            }
            
            # Prefer IMDB ID search if available
            if imdb_id:
                params["i"] = imdb_id
            else:
                params["t"] = title
                if year:
                    params["y"] = year
                    
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if search was successful
                    if data.get("Response") == "True":
                        poster_url = data.get("Poster")
                        
                        if poster_url and poster_url != "N/A":
                            # Create a single poster option from OMDB result
                            poster_option = self._create_poster_option(data, title)
                            if poster_option:
                                logger.info(f"Found OMDB poster for: {title}")
                                return [poster_option]
                        else:
                            logger.debug(f"No poster available on OMDB for: {title}")
                    else:
                        error = data.get("Error", "Unknown error")
                        logger.debug(f"OMDB search failed for {title}: {error}")
                else:
                    logger.warning(f"OMDB request failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching OMDB posters for {title}: {e}")
            
        return []
        
    def _create_poster_option(self, omdb_data: Dict[str, Any], title: str) -> Optional[PosterOption]:
        """Convert OMDB data to PosterOption"""
        try:
            poster_url = omdb_data.get("Poster")
            if not poster_url or poster_url == "N/A":
                return None
                
            imdb_id = omdb_data.get("imdbID", "unknown")
            imdb_rating = omdb_data.get("imdbRating")
            imdb_votes = omdb_data.get("imdbVotes")
            
            # Parse IMDB rating and votes
            vote_average = None
            vote_count = None
            
            try:
                if imdb_rating and imdb_rating != "N/A":
                    vote_average = float(imdb_rating)
            except (ValueError, TypeError):
                pass
                
            try:
                if imdb_votes and imdb_votes != "N/A":
                    # Remove commas from vote count
                    vote_count = int(imdb_votes.replace(",", ""))
            except (ValueError, TypeError):
                pass
                
            # OMDB doesn't provide image dimensions, so we estimate
            # Most OMDB posters are around 300x450 pixels
            estimated_width = 300
            estimated_height = 450
            aspect_ratio = estimated_width / estimated_height
            
            # Calculate quality score
            quality_score = self._calculate_quality_score({
                "width": estimated_width,
                "height": estimated_height,
                "vote_average": vote_average,
                "vote_count": vote_count,
                "language": "en",  # OMDB is primarily English
                "aspect_ratio": aspect_ratio
            })
            
            return PosterOption(
                id=f"omdb_{imdb_id}",
                source=PosterSource.OMDB,
                url=poster_url,
                thumbnail_url=poster_url,  # OMDB only provides one size
                width=estimated_width,
                height=estimated_height,
                aspect_ratio=aspect_ratio,
                language="en",
                vote_average=vote_average,
                vote_count=vote_count,
                file_size_estimate=self._estimate_file_size(estimated_width, estimated_height),
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Error creating OMDB poster option: {e}")
            return None
