"""
Progress Tracker

Real-time progress tracking and WebSocket broadcasting.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from aphrodite_logging import get_logger
from .database import JobRepository
from .types import ProgressInfo

logger = get_logger("aphrodite.workflow.progress")


class ProgressTracker:
    """Tracks and broadcasts job progress updates"""
    
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo
        self._websocket_connections: Dict[str, Any] = {}
    
    async def update_poster_status(self, 
                                  job_id: str, 
                                  poster_id: str, 
                                  status: str,
                                  output_path: Optional[str] = None,
                                  error_message: Optional[str] = None) -> None:
        """
        Update individual poster status and broadcast progress.
        
        Args:
            job_id: Job identifier
            poster_id: Poster identifier
            status: New poster status
            output_path: Output file path if completed
            error_message: Error message if failed
        """
        # Update poster status in database
        await self.job_repo.update_poster_status(
            job_id, poster_id, status, output_path, error_message
        )
        
        # Calculate and broadcast updated progress
        progress = await self.calculate_progress(job_id)
        if progress:
            await self.broadcast_progress(job_id, progress)
    
    async def calculate_progress(self, job_id: str) -> Optional[ProgressInfo]:
        """Calculate current progress information"""
        job = await self.job_repo.get_job_by_id(job_id)
        if not job:
            return None
        
        progress_percentage = 0.0
        if job.total_posters > 0:
            processed = job.completed_posters + job.failed_posters
            progress_percentage = (processed / job.total_posters) * 100.0
        
        return ProgressInfo(
            total_posters=job.total_posters,
            completed_posters=job.completed_posters,
            failed_posters=job.failed_posters,
            progress_percentage=progress_percentage,
            estimated_completion=job.estimated_completion,
            current_poster=None  # Could be enhanced to track current poster
        )
    
    async def broadcast_progress(self, job_id: str, progress: ProgressInfo) -> None:
        """
        Broadcast progress update to connected WebSocket clients.
        
        Args:
            job_id: Job identifier
            progress: Progress information to broadcast
        """
        logger.info(f"Progress update for job {job_id}: {progress.progress_percentage:.1f}% "
                   f"({progress.completed_posters}/{progress.total_posters} completed, "
                   f"{progress.failed_posters} failed)")
        
        # WebSocket broadcasting
        try:
            from ...routes.workflow import websocket_manager
            
            # Check if there are any active connections
            active_connections = websocket_manager.active_connections.get(job_id, [])
            logger.info(f"Found {len(active_connections)} active WebSocket connections for job {job_id}")
            
            if not active_connections:
                logger.warning(f"No active WebSocket connections for job {job_id} - progress update will not be sent")
            
            # Send the update
            await websocket_manager.send_progress_update(job_id, {
                "type": "progress_update",
                "job_id": job_id,
                "data": progress.dict()
            })
            
            logger.info(f"Successfully broadcast progress update for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast progress for job {job_id}: {e}", exc_info=True)
    
    def register_websocket_connection(self, job_id: str, websocket) -> None:
        """Register WebSocket connection for job progress updates"""
        if job_id not in self._websocket_connections:
            self._websocket_connections[job_id] = []
        self._websocket_connections[job_id].append(websocket)
        logger.debug(f"Registered WebSocket connection for job {job_id}")
    
    def unregister_websocket_connection(self, job_id: str, websocket) -> None:
        """Unregister WebSocket connection"""
        if job_id in self._websocket_connections:
            try:
                self._websocket_connections[job_id].remove(websocket)
                if not self._websocket_connections[job_id]:
                    del self._websocket_connections[job_id]
                logger.debug(f"Unregistered WebSocket connection for job {job_id}")
            except ValueError:
                pass
