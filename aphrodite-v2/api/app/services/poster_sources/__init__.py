"""
Poster Sources Package

External poster source integrations for replacement functionality.
"""

from .manager import PosterSourceManager, get_poster_source_manager
from .base_source import BasePosterSource
from .tmdb_source import TMDBPosterSource
from .omdb_source import OMDBPosterSource

__all__ = [
    "PosterSourceManager",
    "get_poster_source_manager",
    "BasePosterSource", 
    "TMDBPosterSource",
    "OMDBPosterSource"
]
