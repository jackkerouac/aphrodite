"""
Activity Performance Metrics Models

SQLAlchemy model for the activity_performance_metrics table.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ActivityPerformanceMetricModel(Base):
    """Activity performance metrics database model"""
    __tablename__ = "activity_performance_metrics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to media_activities
    activity_id = Column(UUID(as_uuid=True), ForeignKey('media_activities.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # System Performance
    cpu_usage_percent = Column(DECIMAL(5, 2), nullable=True)  # Peak CPU usage during operation
    memory_usage_mb = Column(Integer, nullable=True)          # Peak memory usage
    disk_io_read_mb = Column(DECIMAL(8, 2), nullable=True)    # Disk read in MB
    disk_io_write_mb = Column(DECIMAL(8, 2), nullable=True)   # Disk write in MB
    
    # Network Performance (for downloads/uploads)
    network_download_mb = Column(DECIMAL(8, 2), nullable=True)  # Data downloaded
    network_upload_mb = Column(DECIMAL(8, 2), nullable=True)    # Data uploaded
    network_latency_ms = Column(Integer, nullable=True)         # Average network latency
    
    # Processing Stages
    stage_timings = Column(JSONB, nullable=True)               # Breakdown of time per processing stage
    bottleneck_stage = Column(String(50), nullable=True)       # Slowest processing stage
    
    # Quality Metrics
    error_rate = Column(DECIMAL(3, 2), nullable=True)          # 0.00-1.00 error rate if batch operation
    throughput_items_per_second = Column(DECIMAL(6, 2), nullable=True)  # Processing throughput
    
    # Environment
    server_load_average = Column(DECIMAL(4, 2), nullable=True)  # System load during operation
    concurrent_operations = Column(Integer, nullable=True)       # Other operations running simultaneously
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<ActivityPerformanceMetric(id={self.id}, activity_id={self.activity_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'activity_id': str(self.activity_id),
            'cpu_usage_percent': float(self.cpu_usage_percent) if self.cpu_usage_percent else None,
            'memory_usage_mb': self.memory_usage_mb,
            'disk_io_read_mb': float(self.disk_io_read_mb) if self.disk_io_read_mb else None,
            'disk_io_write_mb': float(self.disk_io_write_mb) if self.disk_io_write_mb else None,
            'network_download_mb': float(self.network_download_mb) if self.network_download_mb else None,
            'network_upload_mb': float(self.network_upload_mb) if self.network_upload_mb else None,
            'network_latency_ms': self.network_latency_ms,
            'stage_timings': self.stage_timings,
            'bottleneck_stage': self.bottleneck_stage,
            'error_rate': float(self.error_rate) if self.error_rate else None,
            'throughput_items_per_second': float(self.throughput_items_per_second) if self.throughput_items_per_second else None,
            'server_load_average': float(self.server_load_average) if self.server_load_average else None,
            'concurrent_operations': self.concurrent_operations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
