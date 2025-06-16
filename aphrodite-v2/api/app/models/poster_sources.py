"""
Poster Sources Data Models

Models for external poster search and replacement functionality.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class PosterSource(str, Enum):
    """Available poster sources"""
    TMDB = "tmdb"
    OMDB = "omdb"
    FANART = "fanart"
    CUSTOM = "custom"

class PosterOption(BaseModel):
    """A poster option from an external source"""
    id: str
    source: PosterSource
    url: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    language: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    file_size_estimate: Optional[str] = None
    quality_score: Optional[float] = None

class PosterSearchRequest(BaseModel):
    """Request to search for poster alternatives"""
    item_id: str
    jellyfin_id: str
    title: str
    year: Optional[int] = None
    item_type: str  # "movie" or "series"
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    sources: List[PosterSource] = [PosterSource.TMDB, PosterSource.OMDB]

class PosterSearchResponse(BaseModel):
    """Response containing found poster alternatives"""
    success: bool
    message: str
    posters: List[PosterOption] = []
    total_found: int = 0
    sources_searched: List[PosterSource] = []

class ReplacePosterRequest(BaseModel):
    """Request to replace a poster with a selected alternative"""
    item_id: str
    jellyfin_id: str
    selected_poster: PosterOption

class ReplacePosterResponse(BaseModel):
    """Response from poster replacement operation"""
    success: bool
    message: str
    new_poster_url: Optional[str] = None
    uploaded_to_jellyfin: bool = False
    tag_updated: bool = False
    processing_time: Optional[float] = None

class CustomPosterUploadRequest(BaseModel):
    """Request to upload a custom poster file"""
    item_id: str
    jellyfin_id: str
    # File data will be handled separately via multipart form

class APIKeyConfig(BaseModel):
    """Configuration for external API access"""
    service: str
    api_key: str
    base_url: Optional[str] = None
    additional_config: Dict[str, Any] = {}
