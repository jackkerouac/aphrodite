"""
Workflow Database Models

SQLAlchemy models for batch job processing.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class BatchJobModel(Base):
    """Batch processing job model"""
    __tablename__ = "batch_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False, index=True)
    
    # Progress tracking
    total_posters = Column(Integer, nullable=False)
    completed_posters = Column(Integer, nullable=False, default=0)
    failed_posters = Column(Integer, nullable=False, default=0)
    
    # Job configuration
    status = Column(String(50), nullable=False, default="queued", index=True)
    priority = Column(Integer, nullable=False, default=5, index=True)
    badge_types = Column(JSON, nullable=False)
    selected_poster_ids = Column(JSON, nullable=False)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Error handling
    error_summary = Column(Text, nullable=True)
    
    # Relationships
    poster_statuses = relationship("PosterProcessingStatusModel", back_populates="batch_job")


class PosterProcessingStatusModel(Base):
    """Individual poster processing status"""
    __tablename__ = "poster_processing_status"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_job_id = Column(String(36), ForeignKey("batch_jobs.id", ondelete="CASCADE"), nullable=False)
    poster_id = Column(String(36), nullable=False, index=True)
    
    # Processing status
    status = Column(String(50), nullable=False, default="pending", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    output_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Relationships
    batch_job = relationship("BatchJobModel", back_populates="poster_statuses")
