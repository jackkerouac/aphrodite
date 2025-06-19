"""
Poster Source Manager

Unified interface for managing multiple poster sources.
"""

from typing import List, Optional, Dict, Any
from app.models.poster_sources import (
    PosterOption, PosterSource, PosterSearchRequest, 
    PosterSearchResponse, APIKeyConfig
)
from .tmdb_source import TMDBPosterSource
from .omdb_source import OMDBPosterSource
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
import asyncio
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.poster_sources.manager", service="api")

class PosterSourceManager:
    """Unified manager for all poster sources"""
    
    def __init__(self):
        self._source_configs: Dict[PosterSource, APIKeyConfig] = {}
        
    async def load_api_configs(self, db: AsyncSession) -> None:
        """Load API configurations from database"""
        try:
            # Query settings.yaml configuration from database
            from sqlalchemy import text
            
            # Get the settings.yaml config which contains API keys
            result = await db.execute(
                text("SELECT value FROM system_config WHERE key = 'settings.yaml'")
            )
            config_row = result.fetchone()
            
            if not config_row or not config_row[0]:
                logger.warning("No settings.yaml configuration found in database")
                return
                
            config = config_row[0]  # This should be a JSON object
            api_keys = config.get("api_keys", {}) if config else {}
            
            logger.debug(f"Loaded API keys config: {list(api_keys.keys())}")
            
            # Load TMDB configuration
            tmdb_configs = api_keys.get("TMDB", [])
            if tmdb_configs and len(tmdb_configs) > 0:
                tmdb_config = tmdb_configs[0]  # Get first config
                if "api_key" in tmdb_config:
                    self._source_configs[PosterSource.TMDB] = APIKeyConfig(
                        service="TMDB",
                        api_key=tmdb_config["api_key"],
                        additional_config=tmdb_config
                    )
                    logger.info("Loaded TMDB API configuration")
                    
            # Load OMDB configuration
            omdb_configs = api_keys.get("OMDB", [])
            if omdb_configs and len(omdb_configs) > 0:
                omdb_config = omdb_configs[0]  # Get first config
                if "api_key" in omdb_config:
                    self._source_configs[PosterSource.OMDB] = APIKeyConfig(
                        service="OMDB", 
                        api_key=omdb_config["api_key"],
                        additional_config=omdb_config
                    )
                    logger.info("Loaded OMDB API configuration")
                    
            logger.info(f"Loaded {len(self._source_configs)} poster source configurations")
            
        except Exception as e:
            logger.error(f"Error loading API configurations: {e}", exc_info=True)
            
    async def search_posters(self, request: PosterSearchRequest) -> PosterSearchResponse:
        """Search for posters across multiple sources"""
        try:
            all_posters = []
            sources_searched = []
            
            # Create search tasks for each requested source
            search_tasks = []
            
            for source in request.sources:
                if source in self._source_configs:
                    task = self._search_source_posters(source, request)
                    search_tasks.append(task)
                    sources_searched.append(source)
                else:
                    logger.warning(f"No configuration found for source: {source}")
                    
            if not search_tasks:
                return PosterSearchResponse(
                    success=False,
                    message="No configured poster sources available",
                    posters=[],
                    total_found=0,
                    sources_searched=[]
                )
                
            # Execute all searches concurrently
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Collect all successful results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Search failed for source {sources_searched[i]}: {result}")
                elif isinstance(result, list):
                    all_posters.extend(result)
                    
            # Sort posters by quality score (highest first)
            all_posters.sort(key=lambda p: p.quality_score or 0, reverse=True)
            
            # Limit results to prevent overwhelming the UI
            limited_posters = all_posters[:50]  # Max 50 posters
            
            logger.info(f"Found {len(all_posters)} total posters from {len(sources_searched)} sources")
            
            return PosterSearchResponse(
                success=True,
                message=f"Found {len(all_posters)} posters from {len(sources_searched)} sources",
                posters=limited_posters,
                total_found=len(all_posters),
                sources_searched=sources_searched
            )
            
        except Exception as e:
            logger.error(f"Error in poster search: {e}")
            return PosterSearchResponse(
                success=False,
                message=f"Search failed: {str(e)}",
                posters=[],
                total_found=0,
                sources_searched=[]
            )
            
    async def _search_source_posters(self, source: PosterSource, request: PosterSearchRequest) -> List[PosterOption]:
        """Search posters from a specific source"""
        try:
            config = self._source_configs.get(source)
            if not config:
                logger.warning(f"No configuration for source: {source}")
                return []
                
            if source == PosterSource.TMDB:
                async with TMDBPosterSource(config) as tmdb:
                    return await tmdb.search_posters(
                        request.title,
                        request.item_type,
                        request.year,
                        request.imdb_id
                    )
                    
            elif source == PosterSource.OMDB:
                async with OMDBPosterSource(config) as omdb:
                    return await omdb.search_posters(
                        request.title,
                        request.item_type,
                        request.year,
                        request.imdb_id
                    )
                    
            else:
                logger.warning(f"Unsupported poster source: {source}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching {source} posters: {e}")
            return []
            
    async def download_poster(self, poster: PosterOption) -> Optional[bytes]:
        """Download poster image data"""
        try:
            config = self._source_configs.get(poster.source)
            if not config:
                logger.error(f"No configuration for source: {poster.source}")
                return None
                
            if poster.source == PosterSource.TMDB:
                async with TMDBPosterSource(config) as tmdb:
                    return await tmdb.download_poster(poster.url)
                    
            elif poster.source == PosterSource.OMDB:
                async with OMDBPosterSource(config) as omdb:
                    return await omdb.download_poster(poster.url)
                    
            else:
                logger.warning(f"Unsupported download source: {poster.source}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading poster from {poster.source}: {e}")
            return None
            
    def get_available_sources(self) -> List[PosterSource]:
        """Get list of configured and available poster sources"""
        return list(self._source_configs.keys())
        
    def is_source_available(self, source: PosterSource) -> bool:
        """Check if a poster source is configured and available"""
        return source in self._source_configs

# Global instance
_poster_source_manager = None

async def get_poster_source_manager() -> PosterSourceManager:
    """Get the global poster source manager instance"""
    global _poster_source_manager
    
    if _poster_source_manager is None:
        _poster_source_manager = PosterSourceManager()
        
        # Load API configs from database
        from app.core.database import get_db_session
        
        async for db in get_db_session():
            await _poster_source_manager.load_api_configs(db)
            break  # Only need one iteration
            
    return _poster_source_manager
