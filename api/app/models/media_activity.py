"""
Media Activity Models

SQLAlchemy model for the media_activities table.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class MediaActivityModel(Base):
    """Media activity database model"""
    __tablename__ = "media_activities"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core identification
    media_id = Column(String(36), nullable=False, index=True)
    jellyfin_id = Column(String(100), nullable=True, index=True)
    activity_type = Column(String(50), nullable=False, index=True)
    activity_subtype = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default='pending', index=True)
    
    # Operation Context
    initiated_by = Column(String(50), nullable=True)
    user_id = Column(String(36), nullable=True)
    batch_job_id = Column(String(36), nullable=True, index=True)
    parent_activity_id = Column(UUID(as_uuid=True), ForeignKey('media_activities.id'), nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    
    # Input Parameters (JSON for flexibility)
    input_parameters = Column(JSONB, nullable=True)
    
    # Results and Status
    success = Column(Boolean, nullable=True)
    result_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    system_version = Column(String(20), nullable=True)
    additional_metadata = Column(JSONB, nullable=True)
    
    # Relationships (one-way to avoid circular dependency)
    badge_application = relationship("BadgeApplicationModel", uselist=False, lazy="select", cascade="all, delete-orphan")
    poster_replacement = relationship("PosterReplacementModel", uselist=False, lazy="select", cascade="all, delete-orphan")
    performance_metrics = relationship("ActivityPerformanceMetricModel", uselist=False, lazy="select", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MediaActivity(id={self.id}, type='{self.activity_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'media_id': self.media_id,
            'jellyfin_id': self.jellyfin_id,
            'activity_type': self.activity_type,
            'activity_subtype': self.activity_subtype,
            'status': self.status,
            'initiated_by': self.initiated_by,
            'user_id': self.user_id,
            'batch_job_id': self.batch_job_id,
            'parent_activity_id': str(self.parent_activity_id) if self.parent_activity_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_duration_ms': self.processing_duration_ms,
            'input_parameters': self.input_parameters,
            'success': self.success,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'system_version': self.system_version,
            'additional_metadata': self.additional_metadata
        }
