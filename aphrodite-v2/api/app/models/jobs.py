"""
Job Models

SQLAlchemy models for background processing jobs.
"""

from sqlalchemy import Column, String, Integer, DateTime, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

class ProcessingJobModel(Base):
    """Processing job database model"""
    __tablename__ = "processing_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(String(36), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    progress = Column(Float, nullable=False, default=0.0)
    
    # Job details
    job_type = Column(String(50), nullable=False, index=True)
    parameters = Column(JSON, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results and errors
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"
