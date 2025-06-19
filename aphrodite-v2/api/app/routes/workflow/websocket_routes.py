"""
WebSocket Routes for Workflow Progress

Real-time job progress updates via WebSocket connections.
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aphrodite_logging import get_logger
from app.core.database import get_db_session
from ...services.workflow import ProgressTracker, JobRepository

logger = get_logger("aphrodite.workflow.websocket")


class WebSocketManager:
    """Manages WebSocket connections for job progress updates"""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept WebSocket connection for specific job"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.info(f"WebSocket connected for job {job_id}")
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection"""
        if job_id in self.active_connections:
            try:
                self.active_connections[job_id].remove(websocket)
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
                logger.info(f"WebSocket disconnected for job {job_id}")
            except ValueError:
                pass
    
    async def send_progress_update(self, job_id: str, data: dict):
        """Send progress update to all connected clients for job"""
        logger.info(f"WebSocketManager: Attempting to send progress update for job {job_id}")
        logger.info(f"WebSocketManager: Data = {data}")
        
        if job_id in self.active_connections:
            connections = self.active_connections[job_id]
            logger.info(f"WebSocketManager: Found {len(connections)} active connections for job {job_id}")
            
            disconnected = []
            sent_count = 0
            
            for websocket in connections:
                try:
                    await websocket.send_json(data)
                    sent_count += 1
                    logger.info(f"WebSocketManager: Successfully sent update to WebSocket connection {sent_count}")
                except Exception as e:
                    logger.warning(f"WebSocketManager: Failed to send progress update to connection: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.disconnect(websocket, job_id)
            
            logger.info(f"WebSocketManager: Sent progress update to {sent_count} connections, removed {len(disconnected)} disconnected connections")
        else:
            logger.warning(f"WebSocketManager: No active connections found for job {job_id}")
            logger.info(f"WebSocketManager: Active connection jobs: {list(self.active_connections.keys())}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


async def websocket_endpoint(
    websocket: WebSocket,
    job_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """WebSocket endpoint for job progress updates"""
    job_repository = JobRepository(session)
    progress_tracker = ProgressTracker(job_repository)
    
    try:
        await websocket_manager.connect(websocket, job_id)
        
        # Send initial progress status
        progress = await progress_tracker.calculate_progress(job_id)
        if progress:
            await websocket.send_json({
                "type": "progress_update",
                "job_id": job_id,
                "data": progress.dict()
            })
        
        # Keep connection alive and listen for messages
        while True:
            await websocket.receive_text()  # Keep connection alive
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, job_id)
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
        websocket_manager.disconnect(websocket, job_id)
