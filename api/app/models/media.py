"""
Media Models

SQLAlchemy models for media items and related data.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

class MediaItemModel(Base):
    """Media item database model"""
    __tablename__ = "media_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False, index=True)
    media_type = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    poster_url = Column(Text, nullable=True)
    
    # External IDs
    jellyfin_id = Column(String(100), nullable=True, unique=True, index=True)
    tmdb_id = Column(Integer, nullable=True, index=True)
    imdb_id = Column(String(20), nullable=True, index=True)
    
    # Additional metadata
    overview = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)  # List of genre strings
    runtime = Column(Integer, nullable=True)  # Runtime in minutes
    community_rating = Column(String(10), nullable=True)
    official_rating = Column(String(20), nullable=True)
    premiere_date = Column(String(50), nullable=True)
    
    # TV Show specific fields
    series_name = Column(String(500), nullable=True)
    season_number = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=True)
    
    # Additional metadata
    additional_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MediaItem(id={self.id}, title='{self.title}', type='{self.media_type}')>"
