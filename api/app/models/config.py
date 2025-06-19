"""
Configuration Models

SQLAlchemy models for system and badge configurations.
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

class BadgeConfigModel(Base):
    """Badge configuration database model"""
    __tablename__ = "badge_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False, unique=True, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<BadgeConfig(type='{self.type}', enabled={self.enabled})>"

class SystemConfigModel(Base):
    """System configuration database model"""
    __tablename__ = "system_config"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}')>"
