from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class ProcessingMode(str, Enum):
    IMMEDIATE = "immediate"
    QUEUED = "queued"
    AUTO = "auto"

class SingleBadgeRequest(BaseModel):
    poster_path: str
    badge_types: List[str]
    use_demo_data: bool = False
    output_path: Optional[str] = None

class BulkBadgeRequest(BaseModel):
    poster_paths: List[str]
    badge_types: List[str]
    use_demo_data: bool = False
    output_directory: Optional[str] = None
    batch_size: int = 10

class UniversalBadgeRequest(BaseModel):
    single_request: Optional[SingleBadgeRequest] = None
    bulk_request: Optional[BulkBadgeRequest] = None
    processing_mode: ProcessingMode = ProcessingMode.AUTO

class PosterResult(BaseModel):
    source_path: str
    output_path: Optional[str] = None
    applied_badges: List[str] = []
    success: bool = True
    error: Optional[str] = None

class ProcessingResult(BaseModel):
    success: bool
    results: List[PosterResult]
    job_id: Optional[str] = None
    processing_time: float = 0.0
    error: Optional[str] = None
