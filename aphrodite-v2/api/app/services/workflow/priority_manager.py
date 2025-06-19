"""
Priority Manager

Handles job priority and queuing logic.
"""

from typing import List, Optional
from datetime import datetime

from .types import JobPriority, JobStatus
from .database import JobRepository, BatchJobModel


class PriorityManager:
    """Job priority assignment and queue management"""
    
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository
    
    def calculate_effective_priority(self, base_priority: JobPriority, created_at: datetime) -> float:
        """Calculate effective priority including age factor"""
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        
        # Slightly boost priority for older jobs (max 1 priority level)
        age_boost = min(age_hours / 24, 1.0)
        
        return base_priority.value - age_boost
    
    async def get_next_job(self) -> Optional[BatchJobModel]:
        """Get next job to process based on priority"""
        return await self.job_repository.get_next_queued_job()
    
    def should_preempt(self, current_job: BatchJobModel, waiting_job: BatchJobModel) -> bool:
        """Determine if waiting job should preempt current job"""
        if current_job.priority <= JobPriority.HIGH.value:
            return False  # High priority jobs cannot be preempted
        
        priority_diff = current_job.priority - waiting_job.priority
        return priority_diff >= 3  # Preempt if 3+ priority levels higher
    
    def get_priority_description(self, priority: int) -> str:
        """Get human-readable priority description"""
        priority_map = {
            1: "Urgent",
            2: "High", 
            5: "Normal",
            8: "Low",
            10: "Scheduled"
        }
        return priority_map.get(priority, f"Priority {priority}")
