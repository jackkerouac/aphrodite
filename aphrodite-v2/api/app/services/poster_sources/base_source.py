"""
Base Poster Source Class

Abstract base class for all poster source implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.poster_sources import PosterOption, APIKeyConfig
import aiohttp
import asyncio
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.poster_sources.base", service="api")

class BasePosterSource(ABC):
    """Abstract base class for poster sources"""
    
    def __init__(self, config: APIKeyConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def search_movie_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for movie posters"""
        pass
        
    @abstractmethod 
    async def search_tv_posters(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Search for TV show posters"""
        pass
        
    async def search_posters(self, title: str, item_type: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> List[PosterOption]:
        """Generic poster search that routes to appropriate method"""
        try:
            if item_type.lower() == "movie":
                return await self.search_movie_posters(title, year, imdb_id)
            elif item_type.lower() in ["series", "tv", "tvshow"]:
                return await self.search_tv_posters(title, year, imdb_id)
            else:
                logger.warning(f"Unknown item type: {item_type}, defaulting to movie search")
                return await self.search_movie_posters(title, year, imdb_id)
        except Exception as e:
            logger.error(f"Error searching posters for {title}: {e}")
            return []
            
    async def download_poster(self, url: str) -> Optional[bytes]:
        """Download poster image data"""
        try:
            if not self.session:
                logger.error("No active session for downloading poster")
                return None
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    logger.info(f"Successfully downloaded poster from {url} ({len(data)} bytes)")
                    return data
                else:
                    logger.warning(f"Failed to download poster from {url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading poster from {url}: {e}")
            return None
            
    def _calculate_quality_score(self, poster: Dict[str, Any]) -> float:
        """Calculate a quality score for sorting posters"""
        score = 0.0
        
        # Resolution score (higher is better)
        width = poster.get('width', 0)
        height = poster.get('height', 0)
        resolution_score = (width * height) / 1000000  # Normalize to megapixels
        score += resolution_score * 0.4
        
        # Vote score (if available)
        vote_average = poster.get('vote_average', 0)
        vote_count = poster.get('vote_count', 0)
        if vote_count > 0:
            # Weight by vote count (more votes = more reliable)
            vote_weight = min(vote_count / 100, 1.0)  # Cap at 100 votes for full weight
            vote_score = (vote_average / 10) * vote_weight
            score += vote_score * 0.3
            
        # Language score (English preferred)
        language = poster.get('language', '').lower()
        if language in ['en', 'english', 'null', None]:
            score += 0.2
            
        # Aspect ratio score (poster format preferred)
        aspect_ratio = poster.get('aspect_ratio', 0)
        if 0.6 <= aspect_ratio <= 0.8:  # Typical poster aspect ratio
            score += 0.1
            
        return score
        
    def _estimate_file_size(self, width: int, height: int) -> str:
        """Estimate file size based on dimensions"""
        if not width or not height:
            return "Unknown"
            
        pixels = width * height
        # Rough estimate: ~2-3 bytes per pixel for JPEG
        estimated_bytes = pixels * 2.5
        
        if estimated_bytes < 1024:
            return f"{int(estimated_bytes)} B"
        elif estimated_bytes < 1024 * 1024:
            return f"{estimated_bytes / 1024:.1f} KB"
        else:
            return f"{estimated_bytes / (1024 * 1024):.1f} MB"
