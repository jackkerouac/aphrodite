"""
SQLAlchemy model for badge_applications table
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, DECIMAL, UUID as SQLAlchemyUUID
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BadgeApplicationModel(Base):
    """Model for badge application details"""
    
    __tablename__ = "badge_applications"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    activity_id = Column(UUID(as_uuid=True), ForeignKey("media_activities.id", ondelete="CASCADE"), nullable=False)
    
    # Badge Configuration
    badge_types = Column(JSONB, nullable=False)
    badge_settings_snapshot = Column(JSONB)
    badge_configuration_id = Column(String(50))
    
    # Processing Details
    poster_source = Column(String(100))
    original_poster_path = Column(Text)
    output_poster_path = Column(Text)
    intermediate_files = Column(JSONB)
    
    # Badge Results
    badges_applied = Column(JSONB)
    badges_failed = Column(JSONB)
    final_poster_dimensions = Column(String(20))
    final_file_size = Column(Integer)
    
    # Performance Metrics
    badge_generation_time_ms = Column(Integer)
    poster_processing_time_ms = Column(Integer)
    total_processing_time_ms = Column(Integer)
    
    # Quality Metrics
    poster_quality_score = Column(DECIMAL(3, 2))
    compression_ratio = Column(DECIMAL(5, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (removed back_populates to avoid circular dependency)
    # activity = relationship("MediaActivityModel", back_populates="badge_application", lazy="select")
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "activity_id": str(self.activity_id),
            "badge_types": self.badge_types,
            "badge_settings_snapshot": self.badge_settings_snapshot,
            "badge_configuration_id": self.badge_configuration_id,
            "poster_source": self.poster_source,
            "original_poster_path": self.original_poster_path,
            "output_poster_path": self.output_poster_path,
            "intermediate_files": self.intermediate_files,
            "badges_applied": self.badges_applied,
            "badges_failed": self.badges_failed,
            "final_poster_dimensions": self.final_poster_dimensions,
            "final_file_size": self.final_file_size,
            "badge_generation_time_ms": self.badge_generation_time_ms,
            "poster_processing_time_ms": self.poster_processing_time_ms,
            "total_processing_time_ms": self.total_processing_time_ms,
            "poster_quality_score": float(self.poster_quality_score) if self.poster_quality_score else None,
            "compression_ratio": float(self.compression_ratio) if self.compression_ratio else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
