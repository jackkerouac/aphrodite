"""
Processing Decision Engine

Determines processing method based on poster count and source.
"""

from datetime import timedelta
from typing import List

from .types import ProcessingMethod, JobPriority, JobSource


class ProcessingDecisionEngine:
    """Ultra-focused decision logic for processing method"""
    
    @staticmethod
    def determine_method(poster_count: int, source: str) -> ProcessingMethod:
        """Determine immediate vs batch processing"""
        if source == JobSource.SCHEDULED.value:
            return ProcessingMethod.BATCH
        
        return ProcessingMethod.IMMEDIATE if poster_count == 1 else ProcessingMethod.BATCH
    
    @staticmethod
    def calculate_priority(source: str, user_tier: str = "standard") -> JobPriority:
        """Calculate job priority based on source and user tier"""
        if source == JobSource.MANUAL.value:
            return JobPriority.NORMAL if user_tier == "standard" else JobPriority.HIGH
        
        return JobPriority.SCHEDULED
    
    @staticmethod
    def estimate_duration(poster_count: int, badge_types: List[str]) -> timedelta:
        """Estimate processing duration"""
        # Base processing time per poster (seconds)
        base_time = 5
        
        # Additional time per badge type
        badge_time = len(badge_types) * 2
        
        total_seconds = poster_count * (base_time + badge_time)
        return timedelta(seconds=total_seconds)
