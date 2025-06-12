"""
Health Check Routes

Comprehensive health monitoring endpoints for all system components.
"""

import time
import psutil
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Depends
from datetime import datetime

from app.core.database import DatabaseManager
from app.core.config import get_settings
from shared import BaseResponse
from aphrodite_logging import get_logger

router = APIRouter()

@router.get("/", response_model=BaseResponse)
async def health_check():
    """Basic health check endpoint"""
    return BaseResponse(message="API is healthy")

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    logger = get_logger("aphrodite.api.health", service="api")
    
    start_time = time.time()
    
    # Check all components
    checks = await asyncio.gather(
        _check_api(),
        _check_database(),
        _check_redis(),
        _check_system_resources(),
        return_exceptions=True
    )
    
    api_check, db_check, redis_check, system_check = checks
    
    # Determine overall status
    all_healthy = all(
        isinstance(check, dict) and check.get("status") == "healthy"
        for check in checks
        if not isinstance(check, Exception)
    )
    
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    response = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "duration": round(time.time() - start_time, 4),
        "components": {
            "api": api_check if not isinstance(api_check, Exception) else {"status": "error", "message": str(api_check)},
            "database": db_check if not isinstance(db_check, Exception) else {"status": "error", "message": str(db_check)},
            "redis": redis_check if not isinstance(redis_check, Exception) else {"status": "error", "message": str(redis_check)},
            "system": system_check if not isinstance(system_check, Exception) else {"status": "error", "message": str(system_check)}
        }
    }
    
    # Log health check result
    if overall_status == "healthy":
        logger.info("Health check completed - all systems healthy")
    else:
        logger.warning("Health check completed - some systems unhealthy", extra=response)
    
    return response

@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Check critical components only
    db_healthy = False
    try:
        db_status = await DatabaseManager.health_check()
        db_healthy = db_status.get("status") == "healthy"
    except Exception:
        pass
    
    if db_healthy:
        return {"status": "ready"}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@router.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Database metrics
    db_info = await DatabaseManager.get_connection_info()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "database": db_info,
        "application": {
            "version": "2.0.0",
            "environment": get_settings().environment
        }
    }

async def _check_api() -> Dict[str, Any]:
    """Check API server health"""
    return {
        "status": "healthy",
        "message": "API server is running",
        "version": "2.0.0"
    }

async def _check_database() -> Dict[str, Any]:
    """Check database health"""
    try:
        return await DatabaseManager.health_check()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database check failed: {str(e)}"
        }

async def _check_redis() -> Dict[str, Any]:
    """Check Redis health"""
    try:
        import redis.asyncio as redis
        settings = get_settings()
        
        # Create Redis client
        redis_client = redis.from_url(settings.redis_url)
        
        # Test connection
        await redis_client.ping()
        
        # Get info
        info = await redis_client.info()
        
        await redis_client.close()
        
        return {
            "status": "healthy",
            "message": "Redis connection successful",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human")
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Redis connection failed: {str(e)}"
        }

async def _check_system_resources() -> Dict[str, Any]:
    """Check system resource health"""
    try:
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_healthy = cpu_percent < 90
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_healthy = memory.percent < 90
        
        # Disk check
        disk = psutil.disk_usage('/')
        disk_healthy = (disk.used / disk.total) < 0.90
        
        overall_healthy = cpu_healthy and memory_healthy and disk_healthy
        
        return {
            "status": "healthy" if overall_healthy else "warning",
            "message": "System resources checked",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": round((disk.used / disk.total) * 100, 2),
            "warnings": [
                warning for warning in [
                    "High CPU usage" if not cpu_healthy else None,
                    "High memory usage" if not memory_healthy else None,
                    "High disk usage" if not disk_healthy else None
                ] if warning
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"System resource check failed: {str(e)}"
        }
