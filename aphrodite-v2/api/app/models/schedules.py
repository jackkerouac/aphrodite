"""
Schedule models for Aphrodite v2
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, DateTime, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class ScheduleModel(Base):
    __tablename__ = "schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    timezone = Column(String(100), nullable=False, default='UTC')
    cron_expression = Column(String(100), nullable=False)
    badge_types = Column(ARRAY(String), nullable=False, default=[])
    reprocess_all = Column(Boolean, nullable=False, default=False)
    enabled = Column(Boolean, nullable=False, default=True)
    target_libraries = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ScheduleExecutionModel(Base):
    __tablename__ = "schedule_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    items_processed = Column(String)  # JSON string containing processing details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
