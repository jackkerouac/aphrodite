"""
Resource Manager

Manages concurrent processing limits and resource allocation.
"""

import asyncio
from typing import Dict, Optional


class ResourceManager:
    """Concurrent processing limits and resource control"""
    
    def __init__(self, max_concurrent_jobs: int = 3, max_posters_per_job: int = 50):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_posters_per_job = max_posters_per_job
        self._active_jobs: Dict[str, asyncio.Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
    
    async def acquire_processing_slot(self, job_id: str) -> bool:
        """Acquire processing slot for job"""
        try:
            await self._semaphore.acquire()
            return True
        except Exception:
            return False
    
    def release_processing_slot(self, job_id: str):
        """Release processing slot"""
        if job_id in self._active_jobs:
            del self._active_jobs[job_id]
        self._semaphore.release()
    
    def register_job_task(self, job_id: str, task: asyncio.Task):
        """Register active job task"""
        self._active_jobs[job_id] = task
    
    def get_active_job_count(self) -> int:
        """Get number of active jobs"""
        return len(self._active_jobs)
    
    def is_resource_available(self) -> bool:
        """Check if resources available for new job"""
        return self.get_active_job_count() < self.max_concurrent_jobs
    
    def calculate_chunk_size(self, total_posters: int) -> int:
        """Calculate optimal chunk size for large batches"""
        if total_posters <= self.max_posters_per_job:
            return total_posters
        
        # Split into chunks that can be processed efficiently
        num_chunks = (total_posters + self.max_posters_per_job - 1) // self.max_posters_per_job
        return (total_posters + num_chunks - 1) // num_chunks
