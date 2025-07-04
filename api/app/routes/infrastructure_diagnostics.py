"""
Infrastructure Diagnostics API

Endpoints for diagnosing Redis, Celery, Database, and other infrastructure issues.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import redis
import asyncio
from datetime import datetime
import sys
import os

from app.core.config import get_settings
from app.core.database import get_db_session, get_or_create_session_factory
from app.services.jellyfin_service import get_jellyfin_service
from celery_app import celery_app
from aphrodite_logging import get_logger

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


class InfrastructureDiagnosticResponse(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] = {}


class ComponentStatus(BaseModel):
    name: str
    status: str  # "healthy", "degraded", "failed"
    message: str
    details: Dict[str, Any] = {}


class SystemOverview(BaseModel):
    overall_status: str
    components: List[ComponentStatus]
    timestamp: str


@router.get("/infrastructure/overview", response_model=SystemOverview)
async def get_infrastructure_overview():
    """Get overall infrastructure health status"""
    logger = get_logger("aphrodite.api.diagnostics.infrastructure", service="api")
    
    components = []
    overall_healthy = True
    
    # Test Redis
    redis_status = await _test_redis_connection()
    components.append(redis_status)
    if redis_status.status != "healthy":
        overall_healthy = False
    
    # Test Database
    db_status = await _test_database_connection()
    components.append(db_status)
    if db_status.status != "healthy":
        overall_healthy = False
    
    # Test Celery
    celery_status = await _test_celery_workers()
    components.append(celery_status)
    if celery_status.status != "healthy":
        overall_healthy = False
    
    # Test Jellyfin
    jellyfin_status = await _test_jellyfin_basic()
    components.append(jellyfin_status)
    if jellyfin_status.status != "healthy":
        overall_healthy = False
    
    return SystemOverview(
        overall_status="healthy" if overall_healthy else "degraded",
        components=components,
        timestamp=datetime.now().isoformat()
    )


@router.get("/infrastructure/redis", response_model=InfrastructureDiagnosticResponse)
async def test_redis_infrastructure():
    """Comprehensive Redis connection and performance test"""
    logger = get_logger("aphrodite.api.diagnostics.redis", service="api")
    
    try:
        settings = get_settings()
        
        details = {
            "broker_url": settings.celery_broker_url,
            "result_backend": settings.celery_result_backend
        }
        
        # Test broker connection
        try:
            broker_client = redis.from_url(settings.celery_broker_url)
            broker_ping = broker_client.ping()
            broker_info = broker_client.info()
            details["broker"] = {
                "ping_successful": broker_ping,
                "redis_version": broker_info.get("redis_version"),
                "used_memory_human": broker_info.get("used_memory_human"),
                "connected_clients": broker_info.get("connected_clients"),
                "keyspace": broker_info.get("keyspace", {}),
                "uptime_in_seconds": broker_info.get("uptime_in_seconds")
            }
        except Exception as e:
            details["broker"] = {"error": str(e)}
            logger.error(f"Broker connection failed: {e}")
        
        # Test result backend connection  
        try:
            backend_client = redis.from_url(settings.celery_result_backend)
            backend_ping = backend_client.ping()
            backend_info = backend_client.info()
            details["result_backend"] = {
                "ping_successful": backend_ping,
                "redis_version": backend_info.get("redis_version"),
                "used_memory_human": backend_info.get("used_memory_human"),
                "connected_clients": backend_info.get("connected_clients"),
                "keyspace": backend_info.get("keyspace", {}),
                "uptime_in_seconds": backend_info.get("uptime_in_seconds")
            }
        except Exception as e:
            details["result_backend"] = {"error": str(e)}
            logger.error(f"Result backend connection failed: {e}")
        
        # Test performance
        try:
            test_key = "aphrodite:diagnostics:test"
            test_value = f"test-{datetime.now().timestamp()}"
            
            # Write test
            start_time = datetime.now()
            broker_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            write_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Read test
            start_time = datetime.now()
            retrieved_value = broker_client.get(test_key)
            read_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Cleanup
            broker_client.delete(test_key)
            
            details["performance"] = {
                "write_time_ms": round(write_time, 2),
                "read_time_ms": round(read_time, 2),
                "data_integrity": retrieved_value.decode() == test_value if retrieved_value else False
            }
            
        except Exception as e:
            details["performance"] = {"error": str(e)}
        
        # Determine success
        broker_ok = details.get("broker", {}).get("ping_successful", False)
        backend_ok = details.get("result_backend", {}).get("ping_successful", False)
        
        success = broker_ok and backend_ok
        
        if success:
            message = "Redis infrastructure is healthy"
        else:
            failed_components = []
            if not broker_ok:
                failed_components.append("broker")
            if not backend_ok:
                failed_components.append("result_backend")
            message = f"Redis issues detected in: {', '.join(failed_components)}"
        
        logger.info(f"Redis infrastructure test: {message}")
        
        return InfrastructureDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Redis infrastructure test failed: {e}")
        return InfrastructureDiagnosticResponse(
            success=False,
            message=f"Redis test failed: {str(e)}",
            details={"exception": str(e)}
        )


@router.get("/infrastructure/celery", response_model=InfrastructureDiagnosticResponse)
async def test_celery_infrastructure():
    """Comprehensive Celery worker and task system test"""
    logger = get_logger("aphrodite.api.diagnostics.celery", service="api")
    
    try:
        details = {
            "app_config": {
                "broker_url": celery_app.conf.broker_url,
                "result_backend": celery_app.conf.result_backend,
                "task_serializer": celery_app.conf.task_serializer,
                "worker_pool": celery_app.conf.worker_pool,
                "includes": list(celery_app.conf.include) if celery_app.conf.include else []
            }
        }
        
        # Test task registration
        registered_tasks = list(celery_app.tasks.keys())
        target_task = 'app.services.workflow.workers.batch_worker.process_batch_job'
        task_registered = target_task in registered_tasks
        
        details["task_registration"] = {
            "total_tasks": len(registered_tasks),
            "target_task_registered": task_registered,
            "target_task": target_task,
            "all_tasks": registered_tasks[:10]  # Show first 10 tasks
        }
        
        # Test worker inspection
        inspector = celery_app.control.inspect()
        
        try:
            active_workers = inspector.active()
            registered_tasks_on_workers = inspector.registered()
            worker_stats = inspector.stats()
            
            details["workers"] = {
                "active_workers": active_workers or {},
                "registered_tasks_on_workers": registered_tasks_on_workers or {},
                "worker_stats": worker_stats or {},
                "workers_available": bool(active_workers)
            }
            
        except Exception as e:
            details["workers"] = {
                "error": str(e),
                "workers_available": False
            }
        
        # Determine success
        success = (
            task_registered and 
            details["workers"].get("workers_available", False)
        )
        
        if success:
            worker_count = len(details["workers"].get("active_workers", {}))
            message = f"Celery infrastructure is healthy with {worker_count} active worker(s)"
        else:
            issues = []
            if not task_registered:
                issues.append("target task not registered")
            if not details["workers"].get("workers_available", False):
                issues.append("no active workers")
            message = f"Celery issues detected: {', '.join(issues)}"
        
        logger.info(f"Celery infrastructure test: {message}")
        
        return InfrastructureDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Celery infrastructure test failed: {e}")
        return InfrastructureDiagnosticResponse(
            success=False,
            message=f"Celery test failed: {str(e)}",
            details={"exception": str(e)}
        )


@router.get("/infrastructure/database", response_model=InfrastructureDiagnosticResponse)
async def test_database_infrastructure():
    """Test database connectivity and performance"""
    logger = get_logger("aphrodite.api.diagnostics.database", service="api")
    
    try:
        details = {}
        
        # Try multiple connection strategies
        connection_strategies = [
            ("session_factory", "async_session_factory"),
            ("fresh_session", "get_fresh_db_session"),
            ("health_check", "DatabaseManager.health_check")
        ]
        
        success = False
        message = "Database connection failed"
        
        # Strategy 1: Try async_session_factory
        session_factory = get_or_create_session_factory()
        if session_factory:
            try:
                # First, test if session factory can create a session
                test_session = None
                try:
                    test_session = session_factory()
                    details["session_factory_creation"] = "success"
                except Exception as creation_error:
                    details["session_factory_creation"] = f"failed: {creation_error}"
                    raise creation_error
                
                # Test the session with database operations
                async with test_session as db:
                    # Simple query test
                    from sqlalchemy import text
                    result = await db.execute(text("SELECT 1 as test"))
                    row = result.fetchone()
                    
                    # Performance test
                    start_time = datetime.now()
                    result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                    query_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    job_count = result.fetchone()[0] if result else 0
                    
                    details["connection"] = {
                        "successful": True,
                        "strategy": "session_factory",
                        "test_query_result": row[0] if row else None
                    }
                    
                    details["performance"] = {
                        "query_time_ms": round(query_time, 2),
                        "batch_jobs_count": job_count
                    }
                    
                    success = True
                    message = "Database infrastructure is healthy"
                    
            except Exception as e:
                logger.warning(f"Session factory strategy failed: {e}")
                details["session_factory_error"] = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "session_factory_exists": session_factory is not None
                }
        else:
            details["session_factory_error"] = "Could not get or create session factory"
        
        # Strategy 2: Try fresh session if first strategy failed
        if not success:
            try:
                from app.core.database import get_fresh_db_session
                
                async for db in get_fresh_db_session():
                    from sqlalchemy import text
                    result = await db.execute(text("SELECT 1 as test"))
                    row = result.fetchone()
                    
                    start_time = datetime.now()
                    result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                    query_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    job_count = result.fetchone()[0] if result else 0
                    
                    details["connection"] = {
                        "successful": True,
                        "strategy": "fresh_session",
                        "test_query_result": row[0] if row else None
                    }
                    
                    details["performance"] = {
                        "query_time_ms": round(query_time, 2),
                        "batch_jobs_count": job_count
                    }
                    
                    success = True
                    message = "Database infrastructure is healthy (using fresh connection)"
                    break
                    
            except Exception as e:
                logger.warning(f"Fresh session strategy failed: {e}")
                details["fresh_session_error"] = str(e)
        
        # Strategy 3: Try health check if other strategies failed
        if not success:
            try:
                from app.core.database import DatabaseManager
                health_result = await DatabaseManager.health_check()
                
                if health_result["status"] == "healthy":
                    details["connection"] = {
                        "successful": True,
                        "strategy": "health_check",
                        "test_query_result": 1
                    }
                    success = True
                    message = "Database infrastructure is healthy (health check only)"
                else:
                    details["connection"] = {
                        "successful": False,
                        "strategy": "health_check",
                        "error": health_result["message"]
                    }
                    message = f"Database health check failed: {health_result['message']}"
                    
            except Exception as e:
                logger.error(f"Health check strategy failed: {e}")
                details["health_check_error"] = str(e)
        
        # Final fallback
        if not success:
            details["connection"] = {
                "successful": False,
                "error": "All database connection strategies failed"
            }
            message = "Database connection failed: All strategies exhausted"
        
        logger.info(f"Database infrastructure test: {message}")
        
        return InfrastructureDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Database infrastructure test failed: {e}")
        return InfrastructureDiagnosticResponse(
            success=False,
            message=f"Database test failed: {str(e)}",
            details={"exception": str(e)}
        )


@router.post("/infrastructure/test-batch-workflow", response_model=InfrastructureDiagnosticResponse)
async def test_batch_workflow():
    """Test the complete batch workflow infrastructure"""
    logger = get_logger("aphrodite.api.diagnostics.batch_workflow", service="api")
    
    try:
        details = {
            "test_job_id": f"test-workflow-{int(datetime.now().timestamp())}"
        }
        
        # 1. Test database access for job creation with detailed error tracking
        try:
            # Try session factory first with detailed diagnostics
            from app.core.database import get_or_create_session_factory
            
            logger.info("Attempting to get or create session factory...")
            session_factory = get_or_create_session_factory()
            
            if session_factory:
                try:
                    logger.info("Testing session factory creation...")
                    test_session = session_factory()
                    logger.info("Session factory creation successful")
                    
                    async with test_session as db:
                        logger.info("Testing database query with session factory...")
                        from sqlalchemy import text
                        result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                        job_count = result.fetchone()[0] if result else 0
                        
                        details["database_access"] = {
                            "successful": True, 
                            "strategy": "session_factory",
                            "batch_jobs_count": job_count
                        }
                        logger.info(f"Database access successful using session factory (found {job_count} batch jobs)")
                        
                except Exception as sf_error:
                    logger.error(f"Session factory database access failed: {sf_error}")
                    details["session_factory_details"] = {
                        "error_type": type(sf_error).__name__,
                        "error_message": str(sf_error),
                        "factory_exists": session_factory is not None
                    }
                    
                    # Fall back to fresh session
                    try:
                        logger.info("Attempting fresh session fallback...")
                        from app.core.database import get_fresh_db_session
                        async for fresh_db in get_fresh_db_session():
                            from sqlalchemy import text
                            result = await fresh_db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                            job_count = result.fetchone()[0] if result else 0
                            
                            details["database_access"] = {
                                "successful": True, 
                                "strategy": "fresh_session",
                                "batch_jobs_count": job_count
                            }
                            logger.info(f"Database access successful using fresh session (found {job_count} batch jobs)")
                            break
                    except Exception as fs_error:
                        logger.error(f"Fresh session database access also failed: {fs_error}")
                        details["fresh_session_details"] = {
                            "error_type": type(fs_error).__name__,
                            "error_message": str(fs_error)
                        }
                        raise Exception(f"Both session factory ({sf_error}) and fresh session ({fs_error}) failed")
            else:
                details["session_factory_details"] = {"error": "Could not get or create session factory"}
                raise Exception("Database session factory not available and could not be recovered")
                
        except Exception as e:
            details["database_access"] = {
                "successful": False, 
                "error": str(e),
                "error_type": type(e).__name__
            }
        
        # 2. Test Celery task dispatch
        try:
            task_name = 'app.services.workflow.workers.batch_worker.process_batch_job'
            
            # Check if task is registered
            if task_name not in celery_app.tasks:
                details["task_dispatch"] = {
                    "successful": False, 
                    "error": f"Task {task_name} not registered",
                    "registered_tasks": list(celery_app.tasks.keys())[:5]
                }
            else:
                # Dispatch test task (it will fail safely since it's a fake job ID)
                result = celery_app.send_task(task_name, args=[details["test_job_id"]])
                
                details["task_dispatch"] = {
                    "successful": True,
                    "task_id": result.id,
                    "initial_state": result.state
                }
                
                # Wait briefly to see if worker picks it up
                await asyncio.sleep(2)
                details["task_dispatch"]["state_after_2s"] = result.state
                
        except Exception as e:
            details["task_dispatch"] = {"successful": False, "error": str(e)}
        
        # 3. Test Redis connectivity (used for progress updates)
        try:
            settings = get_settings()
            redis_client = redis.from_url(settings.celery_broker_url)
            
            # Test publishing a progress update (simulate what workers do)
            test_progress = {
                "job_id": details["test_job_id"],
                "progress": 50.0,
                "timestamp": datetime.now().isoformat()
            }
            
            redis_client.publish("job_progress", str(test_progress))
            details["redis_progress"] = {"successful": True}
            
        except Exception as e:
            details["redis_progress"] = {"successful": False, "error": str(e)}
        
        # 4. Test Jellyfin service initialization
        try:
            jellyfin_service = get_jellyfin_service()
            await jellyfin_service._load_jellyfin_settings()
            
            details["jellyfin_service"] = {
                "successful": True,
                "configured": bool(jellyfin_service.base_url and jellyfin_service.api_key)
            }
            
            await jellyfin_service.close()
            
        except Exception as e:
            details["jellyfin_service"] = {"successful": False, "error": str(e)}
        
        # Determine overall success
        required_components = ["database_access", "task_dispatch", "redis_progress", "jellyfin_service"]
        successful_components = [
            comp for comp in required_components 
            if details.get(comp, {}).get("successful", False)
        ]
        
        success = len(successful_components) == len(required_components)
        
        details["summary"] = {
            "required_components": required_components,
            "successful_components": successful_components,
            "failed_components": [comp for comp in required_components if comp not in successful_components]
        }
        
        if success:
            message = "Complete batch workflow infrastructure is healthy"
        else:
            failed = details["summary"]["failed_components"]
            message = f"Batch workflow issues in: {', '.join(failed)}"
        
        logger.info(f"Batch workflow test: {message}")
        
        return InfrastructureDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Batch workflow test failed: {e}", exc_info=True)
        return InfrastructureDiagnosticResponse(
            success=False,
            message=f"Workflow test failed: {str(e)}",
            details={
                "exception": str(e),
                "exception_type": type(e).__name__,
                "test_details": details
            }
        )


# Helper functions for overview endpoint
async def _test_redis_connection() -> ComponentStatus:
    """Helper to test Redis for overview"""
    try:
        settings = get_settings()
        client = redis.from_url(settings.celery_broker_url)
        client.ping()
        return ComponentStatus(
            name="Redis",
            status="healthy",
            message="Redis broker connection successful"
        )
    except Exception as e:
        return ComponentStatus(
            name="Redis", 
            status="failed",
            message=f"Redis connection failed: {str(e)}"
        )


async def _test_database_connection() -> ComponentStatus:
    """Helper to test database for overview"""
    try:
        # Try session factory first
        if async_session_factory:
            try:
                async with async_session_factory() as db:
                    from sqlalchemy import text
                    result = await db.execute(text("SELECT 1"))
                    result.fetchone()
                    
                return ComponentStatus(
                    name="Database",
                    status="healthy", 
                    message="Database connection successful"
                )
            except Exception:
                pass  # Fall through to fresh session
        
        # Try fresh session as fallback
        from app.core.database import get_fresh_db_session
        async for db in get_fresh_db_session():
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            
            return ComponentStatus(
                name="Database",
                status="healthy", 
                message="Database connection successful (fresh)"
            )
            break
            
    except Exception as e:
        return ComponentStatus(
            name="Database",
            status="failed",
            message=f"Database connection failed: {str(e)}"
        )


async def _test_celery_workers() -> ComponentStatus:
    """Helper to test Celery workers for overview"""
    try:
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        
        if active_workers:
            worker_count = len(active_workers)
            return ComponentStatus(
                name="Celery Workers",
                status="healthy",
                message=f"{worker_count} active worker(s) found",
                details={"worker_count": worker_count}
            )
        else:
            return ComponentStatus(
                name="Celery Workers",
                status="degraded", 
                message="No active workers found"
            )
    except Exception as e:
        return ComponentStatus(
            name="Celery Workers",
            status="failed",
            message=f"Worker inspection failed: {str(e)}"
        )


async def _test_jellyfin_basic() -> ComponentStatus:
    """Helper to test Jellyfin for overview"""
    try:
        jellyfin_service = get_jellyfin_service()
        success, message = await jellyfin_service.test_connection()
        await jellyfin_service.close()
        
        return ComponentStatus(
            name="Jellyfin",
            status="healthy" if success else "failed",
            message=message
        )
    except Exception as e:
        return ComponentStatus(
            name="Jellyfin",
            status="failed", 
            message=f"Jellyfin test failed: {str(e)}"
        )
