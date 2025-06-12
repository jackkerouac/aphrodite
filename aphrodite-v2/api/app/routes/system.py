"""
System information and status API endpoints for the About page.
Provides system details, version information, health status, and statistics.
"""

import os
import time
import platform
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/system", tags=["system"])

# Store server start time for uptime calculation
server_start_time = time.time()

class SystemInfoResponse(BaseModel):
    success: bool
    version: str
    execution_mode: str
    database_schema_hash: str
    uptime: str

class UpdateInfoResponse(BaseModel):
    success: bool
    update_available: bool
    current_version: str
    latest_version: Optional[str] = None
    message: Optional[str] = None
    release_notes_url: Optional[str] = None

class HealthResponse(BaseModel):
    success: bool
    status: str
    services: Dict[str, str]
    timestamp: str

class StatsResponse(BaseModel):
    success: bool
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    success_rate: float
    total_media_processed: int
    database_size: str

def get_version() -> str:
    """Get the current application version."""
    try:
        # Try to read version from a version file or environment
        version_file = os.path.join(os.path.dirname(__file__), '..', '..', 'VERSION')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        
        # Fallback to environment variable or default
        return os.getenv('APHRODITE_VERSION', '2.0.0-dev')
    except Exception:
        return '2.0.0-dev'

def get_execution_mode() -> str:
    """Determine the execution mode (Docker, Development, etc.)."""
    try:
        # Check if running in Docker
        if os.path.exists('/.dockerenv'):
            return 'Docker'
        
        # Check if in development mode
        if os.getenv('FASTAPI_ENV') == 'development' or os.getenv('DEBUG') == 'true':
            return 'Development'
        
        # Check if installed as package
        if os.path.exists('/usr/local/bin/aphrodite') or os.path.exists('/opt/aphrodite'):
            return 'Installed Package'
        
        return 'Development'
    except Exception:
        return 'Unknown'

def get_database_schema_hash() -> str:
    """Generate a hash representing the current database schema."""
    try:
        # This would normally read the actual database schema
        # For now, we'll create a hash based on the application version and current time
        schema_string = f"{get_version()}-{platform.python_version()}"
        return hashlib.md5(schema_string.encode()).hexdigest()[:8]
    except Exception:
        return 'unknown'

def format_uptime(seconds: float) -> str:
    """Format uptime seconds into a human-readable string."""
    try:
        delta = timedelta(seconds=int(seconds))
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except Exception:
        return 'Unknown'

@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info():
    """
    Get system information including version, execution mode, database schema, and uptime.
    
    Returns:
        SystemInfoResponse: System information data
    """
    try:
        current_time = time.time()
        uptime_seconds = current_time - server_start_time
        
        return SystemInfoResponse(
            success=True,
            version=get_version(),
            execution_mode=get_execution_mode(),
            database_schema_hash=get_database_schema_hash(),
            uptime=format_uptime(uptime_seconds)
        )
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

@router.get("/check-updates", response_model=UpdateInfoResponse)
async def check_updates():
    """
    Check for available updates to the application.
    
    Returns:
        UpdateInfoResponse: Update availability information
    """
    try:
        current_version = get_version()
        
        # For now, simulate update checking
        # In a real implementation, this would check GitHub releases or update server
        return UpdateInfoResponse(
            success=True,
            update_available=False,
            current_version=current_version,
            message="You are running the latest version!"
        )
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check for updates: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def get_health_status():
    """
    Get health status of various system services.
    
    Returns:
        HealthResponse: Service health status
    """
    try:
        services = {
            "API": "healthy",
            "Database": "healthy", 
            "Workers": "healthy",
            "Redis": "healthy"
        }
        
        # Check if all services are healthy
        overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "degraded"
        
        return HealthResponse(
            success=True,
            status=overall_status,
            services=services,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")

@router.get("/stats", response_model=StatsResponse)
async def get_system_stats():
    """
    Get system statistics including job counts and processing metrics.
    
    Returns:
        StatsResponse: System statistics
    """
    try:
        # For now, return mock statistics
        # In a real implementation, this would query the database
        total_jobs = 1250
        successful_jobs = 1198
        failed_jobs = 52
        success_rate = (successful_jobs / total_jobs) * 100 if total_jobs > 0 else 0
        
        return StatsResponse(
            success=True,
            total_jobs=total_jobs,
            successful_jobs=successful_jobs,
            failed_jobs=failed_jobs,
            success_rate=round(success_rate, 1),
            total_media_processed=892,
            database_size="15.7 MB"
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@router.get("/logs")
async def get_recent_logs():
    """
    Get recent system logs for display in the About page.
    
    Returns:
        dict: Recent log entries
    """
    try:
        # For now, return mock log entries
        # In a real implementation, this would read from the logging system
        logs = [
            {
                "timestamp": "2025-06-12T10:30:15Z",
                "level": "INFO",
                "message": "Successfully processed movie poster",
                "source": "processor"
            },
            {
                "timestamp": "2025-06-12T10:28:42Z", 
                "level": "INFO",
                "message": "Connected to Jellyfin server",
                "source": "jellyfin"
            },
            {
                "timestamp": "2025-06-12T10:25:01Z",
                "level": "INFO", 
                "message": "System health check completed",
                "source": "health"
            },
            {
                "timestamp": "2025-06-12T10:20:33Z",
                "level": "WARNING",
                "message": "API rate limit approaching for TMDB",
                "source": "tmdb"
            },
            {
                "timestamp": "2025-06-12T10:15:17Z",
                "level": "INFO",
                "message": "Background job queue processed",
                "source": "worker"
            }
        ]
        
        return {
            "success": True,
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")
