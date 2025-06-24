"""
Shared Types and Models for Aphrodite v2

Common data structures used across all services.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field

# Processing Status Enums
class ProcessingStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MediaType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    EPISODE = "episode"
    SEASON = "season"

class BadgeType(str, Enum):
    RATING = "rating"
    REVIEW = "review"
    AWARDS = "awards"
    RESOLUTION = "resolution"
    AUDIO = "audio"
    CUSTOM = "custom"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Base Models
class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Media Models
class MediaItem(BaseModel):
    """Media item representation"""
    id: str
    title: str
    media_type: MediaType
    year: Optional[int] = None
    poster_url: Optional[str] = None
    jellyfin_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    imdb_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Badge(BaseModel):
    """Badge configuration and data"""
    id: str
    type: BadgeType
    enabled: bool = True
    position: tuple[int, int] = (0, 0)
    size: tuple[int, int] = (100, 50)
    
    # Badge-specific data
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

# Processing Models
class ProcessingJob(BaseModel):
    """Background processing job"""
    id: str
    media_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0  # 0.0 to 1.0
    
    # Job details
    job_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Media information (populated from joins)
    title: Optional[str] = None
    media_name: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and errors
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# API Request/Response Models
class CreateJobRequest(BaseModel):
    """Request to create a processing job"""
    media_ids: List[str]
    job_type: str
    parameters: Optional[Dict[str, Any]] = None

class JobStatusResponse(BaseResponse):
    """Response with job status"""
    job: ProcessingJob

class MediaListResponse(BaseResponse):
    """Response with list of media items"""
    items: List[MediaItem]
    total: int
    page: int
    per_page: int

# Configuration Models
class BadgeConfig(BaseModel):
    """Badge configuration"""
    type: BadgeType
    enabled: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

class SystemConfig(BaseModel):
    """System configuration"""
    version: str = "2.0.0"
    debug: bool = False
    
    # Service URLs
    jellyfin_url: Optional[str] = None
    jellyfin_api_key: Optional[str] = None
    
    # Processing settings
    max_concurrent_jobs: int = 4
    job_timeout: int = 300  # seconds
    
    # Badge configurations
    badges: List[BadgeConfig] = Field(default_factory=list)

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class JobUpdateMessage(WebSocketMessage):
    """Job update WebSocket message"""
    type: str = "job_update"
    job_id: str
    status: ProcessingStatus
    progress: float

# Logging Models
@dataclass
class LogContext:
    """Context information for structured logging"""
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    service: Optional[str] = None
    media_id: Optional[str] = None
    job_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

# Utility Functions
def generate_id() -> str:
    """Generate a unique ID"""
    import uuid
    return str(uuid.uuid4())

def generate_short_id() -> str:
    """Generate a short unique ID"""
    import uuid
    return str(uuid.uuid4())[:8]
