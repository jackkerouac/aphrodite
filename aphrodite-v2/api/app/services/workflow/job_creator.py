"""
Job Creator

Handles job creation and validation logic.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from .types import BatchJobRequest, JobSource, JobPriority, ProcessingMethod
from .decision_engine import ProcessingDecisionEngine
from .database import JobRepository, BatchJobModel


class JobCreator:
    """Single responsibility: job creation and validation"""
    
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository
        self.decision_engine = ProcessingDecisionEngine()
    
    async def create_batch_job(self, 
                              user_id: str,
                              name: str,
                              poster_ids: List[UUID], 
                              badge_types: List[str],
                              source: JobSource = JobSource.MANUAL) -> BatchJobModel:
        """Create and validate batch job"""
        
        # Calculate job priority
        priority = self.decision_engine.calculate_priority(source.value)
        
        # Create job request
        request = BatchJobRequest(
            name=name,
            poster_ids=poster_ids,
            badge_types=badge_types,
            source=source,
            priority=priority
        )
        
        # Create in database
        job = await self.job_repository.create_batch_job(user_id, request)
        
        return job
    
    def validate_job_request(self, poster_ids: List[UUID], badge_types: List[str]) -> List[str]:
        """Validate job parameters and return errors"""
        errors = []
        
        if not poster_ids:
            errors.append("At least one poster required")
        
        if len(poster_ids) > 1000:
            errors.append("Maximum 1000 posters per job")
        
        if not badge_types:
            errors.append("At least one badge type required")
        
        valid_badges = ["audio", "resolution", "review", "awards"]
        invalid_badges = [b for b in badge_types if b not in valid_badges]
        if invalid_badges:
            errors.append(f"Invalid badge types: {invalid_badges}")
        
        return errors
