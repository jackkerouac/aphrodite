"""
Enhanced Batch Debug API Routes

Provides API endpoints for enabling/disabling batch processing debug mode
and retrieving debug information.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
from pathlib import Path
import json

from app.services.diagnostics.batch_debug_logger import BatchDebugLogger
from aphrodite_logging import get_logger

router = APIRouter()
logger = get_logger("aphrodite.api.batch_debug")


class DebugModeRequest(BaseModel):
    duration_minutes: int = 30


class DebugModeResponse(BaseModel):
    success: bool
    message: str
    enabled: bool
    expires_at: Optional[str] = None


class DebugStatusResponse(BaseModel):
    debug_enabled: bool
    active_jobs_with_debug: List[str]
    recent_debug_files: List[Dict[str, Any]]


class JobDebugSummaryResponse(BaseModel):
    success: bool
    debug_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/batch-debug/enable", response_model=DebugModeResponse)
async def enable_batch_debug_mode(request: DebugModeRequest):
    """
    Enable comprehensive batch processing debug logging
    
    This will enable detailed logging for all subsequent batch jobs including:
    - Session state tracking
    - Request/response analysis  
    - Jellyfin environment detection
    - Performance metrics
    - Failure pattern analysis
    """
    try:
        success = BatchDebugLogger.enable_debug_mode(request.duration_minutes)
        
        if success:
            expires_at = datetime.utcnow().replace(microsecond=0)
            expires_at = expires_at.replace(minute=expires_at.minute + request.duration_minutes)
            
            logger.info(f"🔍 Batch debug mode enabled for {request.duration_minutes} minutes")
            
            return DebugModeResponse(
                success=True,
                message=f"Debug mode enabled for {request.duration_minutes} minutes",
                enabled=True,
                expires_at=expires_at.isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to enable debug mode")
            
    except Exception as e:
        logger.error(f"Failed to enable debug mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-debug/disable", response_model=DebugModeResponse)
async def disable_batch_debug_mode():
    """
    Disable batch processing debug logging immediately
    """
    try:
        success = BatchDebugLogger.disable_debug_mode()
        
        if success:
            logger.info("🔍 Batch debug mode disabled")
            
            return DebugModeResponse(
                success=True,
                message="Debug mode disabled",
                enabled=False
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to disable debug mode")
            
    except Exception as e:
        logger.error(f"Failed to disable debug mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch-debug/status", response_model=DebugStatusResponse)
async def get_debug_status():
    """
    Get current debug mode status and available debug information
    """
    try:
        debug_enabled = BatchDebugLogger.is_debug_enabled_globally()
        
        # Get recent debug files
        debug_dir = Path("E:/programming/aphrodite/api/debug_logs/batch_jobs")
        recent_files = []
        
        if debug_dir.exists():
            # Get all debug files sorted by creation time (newest first)
            debug_files = sorted(
                debug_dir.glob("job_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Get details for the 10 most recent files
            for debug_file in debug_files[:10]:
                try:
                    stat = debug_file.stat()
                    file_info = {
                        "filename": debug_file.name,
                        "job_id": debug_file.name.split("_")[1],
                        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "size_bytes": stat.st_size,
                        "path": str(debug_file)
                    }
                    recent_files.append(file_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for debug file {debug_file}: {e}")
        
        # TODO: Add detection of currently running jobs with debug enabled
        active_jobs = []
        
        return DebugStatusResponse(
            debug_enabled=debug_enabled,
            active_jobs_with_debug=active_jobs,
            recent_debug_files=recent_files
        )
        
    except Exception as e:
        logger.error(f"Failed to get debug status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch-debug/job/{job_id}/summary", response_model=JobDebugSummaryResponse)
async def get_job_debug_summary(job_id: str):
    """
    Get debug summary for a specific job
    """
    try:
        # Find the debug file for this job
        debug_dir = Path("E:/programming/aphrodite/api/debug_logs/batch_jobs")
        
        if not debug_dir.exists():
            return JobDebugSummaryResponse(
                success=False,
                error="No debug logs directory found"
            )
        
        # Look for debug files matching this job ID
        debug_files = list(debug_dir.glob(f"job_{job_id}_*.json"))
        
        if not debug_files:
            return JobDebugSummaryResponse(
                success=False,
                error=f"No debug file found for job {job_id}"
            )
        
        # Use the most recent debug file for this job
        latest_file = max(debug_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                debug_data = json.load(f)
            
            # Return just the summary part (not the full request history)
            summary = debug_data.get("summary", {})
            
            return JobDebugSummaryResponse(
                success=True,
                debug_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Failed to read debug file {latest_file}: {e}")
            return JobDebugSummaryResponse(
                success=False,
                error=f"Failed to read debug file: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Failed to get debug summary for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch-debug/job/{job_id}/full-log")
async def get_job_debug_full_log(job_id: str):
    """
    Download complete debug log file for a specific job
    """
    try:
        # Find the debug file for this job
        debug_dir = Path("E:/programming/aphrodite/api/debug_logs/batch_jobs")
        
        if not debug_dir.exists():
            raise HTTPException(status_code=404, detail="No debug logs directory found")
        
        # Look for debug files matching this job ID
        debug_files = list(debug_dir.glob(f"job_{job_id}_*.json"))
        
        if not debug_files:
            raise HTTPException(status_code=404, detail=f"No debug file found for job {job_id}")
        
        # Use the most recent debug file for this job
        latest_file = max(debug_files, key=lambda x: x.stat().st_mtime)
        
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=str(latest_file),
            filename=latest_file.name,
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get debug file for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/batch-debug/cleanup")
async def cleanup_old_debug_files(days: int = Query(7, description="Delete debug files older than this many days")):
    """
    Clean up old debug files to save disk space
    """
    try:
        debug_dir = Path("E:/programming/aphrodite/api/debug_logs/batch_jobs")
        
        if not debug_dir.exists():
            return {"deleted_files": 0, "message": "No debug directory found"}
        
        # Calculate cutoff date
        cutoff_time = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        
        deleted_files = 0
        total_size_freed = 0
        
        for debug_file in debug_dir.glob("job_*.json"):
            try:
                if debug_file.stat().st_mtime < cutoff_time:
                    file_size = debug_file.stat().st_size
                    debug_file.unlink()
                    deleted_files += 1
                    total_size_freed += file_size
                    logger.debug(f"Deleted old debug file: {debug_file.name}")
            except Exception as e:
                logger.warning(f"Failed to delete debug file {debug_file}: {e}")
        
        logger.info(f"Cleaned up {deleted_files} debug files, freed {total_size_freed} bytes")
        
        return {
            "deleted_files": deleted_files,
            "total_size_freed_bytes": total_size_freed,
            "message": f"Deleted {deleted_files} files older than {days} days"
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup debug files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
