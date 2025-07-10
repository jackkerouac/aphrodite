"""
SQLAlchemy model for poster_replacements table
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, DECIMAL, UUID as SQLAlchemyUUID
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PosterReplacementModel(Base):
    """Model for poster replacement details"""
    
    __tablename__ = "poster_replacements"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    activity_id = Column(UUID(as_uuid=True), ForeignKey("media_activities.id", ondelete="CASCADE"), nullable=False)
    
    # Source Information
    replacement_source = Column(String(50), nullable=False)  # 'tmdb', 'fanart_tv', 'manual_upload', 'local_file'
    source_poster_id = Column(String(100))  # External ID from source
    source_poster_url = Column(Text)  # Original URL (if applicable)
    search_query = Column(Text)  # Query used to find replacement
    search_results_count = Column(Integer)  # Number of options found
    
    # Original Poster Info
    original_poster_url = Column(Text)  # Original Jellyfin poster URL
    original_poster_cached_path = Column(Text)  # Path where original was cached
    original_poster_dimensions = Column(String(20))  # "width x height"
    original_file_size = Column(Integer)  # Original file size in bytes
    original_poster_hash = Column(String(64))  # SHA256 hash of original
    
    # New Poster Info
    new_poster_dimensions = Column(String(20))  # "width x height"
    new_file_size = Column(Integer)  # New file size in bytes
    new_poster_hash = Column(String(64))  # SHA256 hash of new poster
    download_time_ms = Column(Integer)  # Time to download new poster
    upload_time_ms = Column(Integer)  # Time to upload to Jellyfin
    
    # Jellyfin Integration
    jellyfin_upload_success = Column(Boolean)  # Successfully uploaded to Jellyfin
    tag_operations = Column(JSONB)  # Tag additions/removals performed
    jellyfin_response = Column(JSONB)  # Jellyfin API responses
    
    # Quality Assessment
    quality_improvement_score = Column(DECIMAL(3, 2))  # -1.00 to 1.00 (negative = worse)
    visual_similarity_score = Column(DECIMAL(3, 2))  # 0.00-1.00 similarity to original
    user_rating = Column(Integer)  # 1-5 user rating (if provided)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (removed back_populates to avoid circular dependency)
    # activity = relationship("MediaActivityModel", back_populates="poster_replacement", lazy="select")
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "activity_id": str(self.activity_id),
            "replacement_source": self.replacement_source,
            "source_poster_id": self.source_poster_id,
            "source_poster_url": self.source_poster_url,
            "search_query": self.search_query,
            "search_results_count": self.search_results_count,
            "original_poster_url": self.original_poster_url,
            "original_poster_cached_path": self.original_poster_cached_path,
            "original_poster_dimensions": self.original_poster_dimensions,
            "original_file_size": self.original_file_size,
            "original_poster_hash": self.original_poster_hash,
            "new_poster_dimensions": self.new_poster_dimensions,
            "new_file_size": self.new_file_size,
            "new_poster_hash": self.new_poster_hash,
            "download_time_ms": self.download_time_ms,
            "upload_time_ms": self.upload_time_ms,
            "jellyfin_upload_success": self.jellyfin_upload_success,
            "tag_operations": self.tag_operations,
            "jellyfin_response": self.jellyfin_response,
            "quality_improvement_score": float(self.quality_improvement_score) if self.quality_improvement_score else None,
            "visual_similarity_score": float(self.visual_similarity_score) if self.visual_similarity_score else None,
            "user_rating": self.user_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
