"""
Workflow Data Models

Ultra-focused data models for workflow processing system.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID


class ProcessingMethod(str, Enum):
    """Processing method determination"""
    IMMEDIATE = "immediate"
    BATCH = "batch"


class JobPriority(int, Enum):
    """Job priority levels (1=highest, 10=lowest)"""
    URGENT = 1
    HIGH = 2
    NORMAL = 5
    LOW = 8
    SCHEDULED = 10


class JobStatus(str, Enum):
    """Job lifecycle status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PosterStatus(str, Enum):
    """Individual poster processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobSource(str, Enum):
    """Job creation source"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class ProgressInfo(BaseModel):
    """Real-time progress information"""
    total_posters: int
    completed_posters: int
    failed_posters: int
    progress_percentage: float
    estimated_completion: Optional[str] = None  # ISO string, not datetime
    current_poster: Optional[str] = None


class BatchJobRequest(BaseModel):
    """Batch job creation request"""
    name: str
    poster_ids: List[str]  # Will be strings after validation
    badge_types: List[str]
    user_id: str = "default_user"  # Add for API compatibility
    source: JobSource = JobSource.MANUAL
    priority: JobPriority = JobPriority.NORMAL
    
    @model_validator(mode='before')
    @classmethod
    def convert_uuids_to_strings(cls, values):
        """Convert UUID objects to strings before validation"""
        if isinstance(values, dict) and 'poster_ids' in values:
            poster_ids = values['poster_ids']
            if isinstance(poster_ids, list):
                # Convert any UUID objects to strings
                values['poster_ids'] = [str(item) for item in poster_ids]
        return values
