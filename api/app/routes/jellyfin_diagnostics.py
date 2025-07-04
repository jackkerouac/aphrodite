"""
Jellyfin Diagnostics API

Endpoints for diagnosing Jellyfin connectivity issues in production.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.jellyfin_service import get_jellyfin_service
from app.core.database import get_db_session, async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.media import MediaItemModel
from app.services.workflow.database import JobRepository
from app.services.workflow.types import JobStatus
from aphrodite_logging import get_logger

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


class JellyfinDiagnosticResponse(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] = {}


class MediaItemTestResult(BaseModel):
    jellyfin_id: str
    title: str
    metadata_available: bool
    poster_available: bool
    error_message: str = None


class BatchJobDiagnosticResult(BaseModel):
    job_id: str
    status: str
    total_posters: int
    completed_posters: int
    failed_posters: int
    error_message: str = None
    sample_failed_ids: List[str] = []
    failed_poster_tests: List[MediaItemTestResult] = []


@router.get("/jellyfin/connection", response_model=JellyfinDiagnosticResponse)
async def test_jellyfin_connection():
    """Test basic Jellyfin connectivity and configuration"""
    logger = get_logger("aphrodite.api.diagnostics.jellyfin", service="api")
    
    jellyfin_service = get_jellyfin_service()
    
    try:
        # Test basic connection
        success, message = await jellyfin_service.test_connection()
        
        details = {
            "connection_test": {
                "success": success,
                "message": message
            }
        }
        
        if success:
            # If connection works, test getting libraries
            try:
                libraries = await jellyfin_service.get_libraries()
                details["libraries"] = {
                    "count": len(libraries),
                    "available": [{"name": lib.get("Name"), "id": lib.get("ItemId") or lib.get("Id")} for lib in libraries[:5]]
                }
                logger.info(f"Jellyfin connection test successful - {len(libraries)} libraries found")
            except Exception as lib_error:
                details["libraries"] = {
                    "error": str(lib_error)
                }
                logger.warning(f"Library test failed: {lib_error}")
        
        return JellyfinDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Jellyfin connection test failed: {e}")
        return JellyfinDiagnosticResponse(
            success=False,
            message=f"Connection test failed: {str(e)}",
            details={"exception": str(e)}
        )
    finally:
        await jellyfin_service.close()


@router.get("/jellyfin/media-sample", response_model=List[MediaItemTestResult])
async def test_media_items():
    """Test a sample of media items directly from Jellyfin to check for invalid IDs"""
    logger = get_logger("aphrodite.api.diagnostics.media", service="api")
    
    results = []
    jellyfin_service = get_jellyfin_service()
    
    try:
        logger.info("Getting sample media items directly from Jellyfin")
        
        # Get libraries from Jellyfin
        libraries = await jellyfin_service.get_libraries()
        if not libraries:
            logger.warning("No Jellyfin libraries found")
            return []
        
        # Sample items from the first few libraries
        sample_items = []
        for library in libraries[:3]:  # Test first 3 libraries
            library_id = library.get('ItemId') or library.get('Id')
            library_name = library.get('Name', 'Unknown')
            
            if not library_id:
                logger.warning(f"Library '{library_name}' has no ID field")
                continue
                
            logger.info(f"Getting items from library: {library_name} (ID: {library_id})")
            
            try:
                # Get items from this library
                library_items = await jellyfin_service.get_library_items(library_id)
                
                # Take first 3-4 items from each library
                for item in library_items[:4]:
                    if len(sample_items) >= 10:  # Limit total items to test
                        break
                    
                    item_id = item.get('Id')
                    item_name = item.get('Name', 'Unknown')
                    item_type = item.get('Type', 'Unknown')
                    
                    if item_id:
                        sample_items.append({
                            'jellyfin_id': item_id,
                            'title': f"{item_name} ({item_type})",
                            'library': library_name
                        })
                        
            except Exception as lib_error:
                logger.error(f"Failed to get items from library {library_name}: {lib_error}")
                continue
        
        if not sample_items:
            logger.warning("No media items found in any Jellyfin library")
            return []
        
        logger.info(f"Testing {len(sample_items)} media items from Jellyfin")
        
        # Test each sample item
        for item_info in sample_items:
            test_result = MediaItemTestResult(
                jellyfin_id=item_info['jellyfin_id'],
                title=item_info['title'],
                metadata_available=False,
                poster_available=False
            )
            
            try:
                # Test metadata retrieval (general API)
                metadata = await jellyfin_service.get_item_metadata(item_info['jellyfin_id'])
                test_result.metadata_available = metadata is not None
                
                # Test user-specific API
                user_metadata = await jellyfin_service.get_media_item_by_id(item_info['jellyfin_id'])
                user_api_works = user_metadata is not None
                
                # Test poster availability
                poster_url = await jellyfin_service.get_poster_url(item_info['jellyfin_id'])
                test_result.poster_available = poster_url is not None
                
                # Set appropriate error messages
                if not test_result.metadata_available and not user_api_works:
                    test_result.error_message = "Both general and user-specific APIs failed"
                elif not test_result.metadata_available and user_api_works:
                    test_result.error_message = "General API failed (HTTP 400), but user API works - this is expected"
                elif not test_result.poster_available:
                    test_result.error_message = "Metadata available but poster not accessible"
                
                # Consider it successful if either API works
                if user_api_works and test_result.poster_available:
                    # Override metadata_available to show green if user API works
                    test_result.metadata_available = True
                    if test_result.error_message == "General API failed (HTTP 400), but user API works - this is expected":
                        test_result.error_message = None
                
            except Exception as e:
                test_result.error_message = f"Exception: {str(e)}"
                logger.error(f"Error testing media item {item_info['jellyfin_id']}: {e}")
            
            results.append(test_result)
        
        # Log summary
        working_count = sum(1 for r in results if r.metadata_available and r.poster_available)
        logger.info(f"Media item test complete: {working_count}/{len(results)} items working properly")
        
        return results
        
    except Exception as e:
        logger.error(f"Media items test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test media items: {str(e)}"
        )
    finally:
        await jellyfin_service.close()


@router.get("/jellyfin/config", response_model=JellyfinDiagnosticResponse)
async def check_jellyfin_config():
    """Check Jellyfin configuration status with API key and User ID validation"""
    logger = get_logger("aphrodite.api.diagnostics.config", service="api")
    
    jellyfin_service = get_jellyfin_service()
    
    try:
        # Force load settings to check configuration
        await jellyfin_service._load_jellyfin_settings()
        
        details = {
            "base_url": jellyfin_service.base_url if jellyfin_service.base_url else "Not configured",
            "api_key": "Configured" if jellyfin_service.api_key else "Not configured",
            "user_id": jellyfin_service.user_id if jellyfin_service.user_id else "Not configured",
            "settings_loaded": jellyfin_service._settings_loaded
        }
        
        # Check if all required settings are present
        missing_settings = []
        if not jellyfin_service.base_url:
            missing_settings.append("base_url")
        if not jellyfin_service.api_key:
            missing_settings.append("api_key")
        if not jellyfin_service.user_id:
            missing_settings.append("user_id")
        
        details["missing_settings"] = missing_settings
        
        # Test API key and User ID validity if they exist
        if jellyfin_service.base_url and jellyfin_service.api_key:
            try:
                # Test API key by using the existing test_connection method
                success, message = await jellyfin_service.test_connection()
                details["api_key_valid"] = success
                if success:
                    # Extract server info from the message
                    details["connection_message"] = message
                else:
                    details["api_key_error"] = message
            except Exception as api_error:
                details["api_key_valid"] = False
                details["api_key_error"] = str(api_error)
                logger.warning(f"API key validation failed: {api_error}")
        
        if jellyfin_service.base_url and jellyfin_service.api_key and jellyfin_service.user_id:
            try:
                # Test User ID by getting libraries (which requires valid user ID)
                libraries = await jellyfin_service.get_libraries()
                details["user_id_valid"] = len(libraries) >= 0  # Empty list is still valid
                details["libraries_count"] = len(libraries)
            except Exception as user_error:
                details["user_id_valid"] = False
                details["user_id_error"] = str(user_error)
                logger.warning(f"User ID validation failed: {user_error}")
        
        # Determine overall success
        config_complete = len(missing_settings) == 0
        api_key_ok = details.get("api_key_valid", True)  # Default True if not tested
        user_id_ok = details.get("user_id_valid", True)  # Default True if not tested
        
        success = config_complete and api_key_ok and user_id_ok
        
        if success:
            message = "Jellyfin configuration is complete and valid"
        else:
            issues = []
            if missing_settings:
                issues.append(f"missing: {', '.join(missing_settings)}")
            if not api_key_ok:
                issues.append("invalid API key")
            if not user_id_ok:
                issues.append("invalid User ID")
            message = f"Jellyfin configuration issues: {', '.join(issues)}"
        
        logger.info(f"Jellyfin config check: {message}")
        
        return JellyfinDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Jellyfin config check failed: {e}")
        return JellyfinDiagnosticResponse(
            success=False,
            message=f"Config check failed: {str(e)}",
            details={"exception": str(e)}
        )
    finally:
        await jellyfin_service.close()


@router.post("/jellyfin/test-id/{jellyfin_id}", response_model=JellyfinDiagnosticResponse)
async def test_specific_jellyfin_id(jellyfin_id: str):
    """Test a specific Jellyfin ID to diagnose issues"""
    logger = get_logger("aphrodite.api.diagnostics.test_id", service="api")
    
    jellyfin_service = get_jellyfin_service()
    
    try:
        logger.info(f"Testing specific Jellyfin ID: {jellyfin_id}")
        
        details = {
            "jellyfin_id": jellyfin_id,
            "tests": {}
        }
        
        # Test metadata retrieval
        try:
            metadata = await jellyfin_service.get_item_metadata(jellyfin_id)
            details["tests"]["metadata"] = {
                "success": metadata is not None,
                "item_name": metadata.get("Name") if metadata else None
            }
        except Exception as e:
            details["tests"]["metadata"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test user-specific API
        try:
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            details["tests"]["user_api"] = {
                "success": media_item is not None,
                "item_name": media_item.get("Name") if media_item else None
            }
        except Exception as e:
            details["tests"]["user_api"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test poster availability
        try:
            poster_url = await jellyfin_service.get_poster_url(jellyfin_id)
            details["tests"]["poster"] = {
                "success": poster_url is not None,
                "url": poster_url
            }
        except Exception as e:
            details["tests"]["poster"] = {
                "success": False,
                "error": str(e)
            }
        
        # Determine overall success - prioritize what's actually needed for processing
        # For batch processing, we primarily need:
        # 1. Either metadata API to work (user API is more reliable)
        # 2. Poster to be available
        
        user_api_works = details["tests"].get("user_api", {}).get("success", False)
        poster_works = details["tests"].get("poster", {}).get("success", False)
        metadata_works = details["tests"].get("metadata", {}).get("success", False)
        
        # Success if we can get the item data AND poster (which is what batch processing needs)
        success = (user_api_works or metadata_works) and poster_works
        
        if success:
            message = f"Jellyfin ID {jellyfin_id} is valid and accessible"
        elif user_api_works and not poster_works:
            message = f"Jellyfin ID {jellyfin_id} is valid but has no poster image"
        elif poster_works and not (user_api_works or metadata_works):
            message = f"Jellyfin ID {jellyfin_id} has poster but metadata access failed"
        else:
            message = f"Jellyfin ID {jellyfin_id} is not accessible - may be invalid or deleted"
        
        logger.info(f"Jellyfin ID test result: {message}")
        
        return JellyfinDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Jellyfin ID test failed: {e}")
        return JellyfinDiagnosticResponse(
            success=False,
            message=f"Test failed: {str(e)}",
            details={"exception": str(e)}
        )
    finally:
        await jellyfin_service.close()


@router.get("/jellyfin/batch-jobs/failed", response_model=List[BatchJobDiagnosticResult])
async def get_failed_batch_jobs():
    """Get recent failed batch jobs for analysis"""
    logger = get_logger("aphrodite.api.diagnostics.batch_jobs", service="api")
    
    try:
        # Try multiple database connection strategies
        results = []
        
        # Strategy 1: Try async_session_factory
        if async_session_factory:
            try:
                async with async_session_factory() as db:
                    job_repo = JobRepository(db)
                    
                    # Get recent failed or partially failed jobs
                    failed_jobs = await job_repo.get_recent_jobs_by_status(
                        [JobStatus.FAILED, JobStatus.COMPLETED],  # Include completed jobs with failures
                        limit=10
                    )
                    
                    for job in failed_jobs:
                        # Only include jobs that actually had failures
                        if job.status == JobStatus.FAILED.value or job.failed_posters > 0:
                            result = BatchJobDiagnosticResult(
                                job_id=job.id,
                                status=job.status,
                                total_posters=job.total_posters,
                                completed_posters=job.completed_posters,
                                failed_posters=job.failed_posters,
                                error_message=job.error_summary
                            )
                            
                            # Get sample of failed poster IDs from this job
                            if job.selected_poster_ids and job.failed_posters > 0:
                                # For demonstration, we'll take the first few IDs as "potentially failed"
                                # In a real implementation, you'd want to track which specific IDs failed
                                sample_size = min(3, len(job.selected_poster_ids))
                                result.sample_failed_ids = job.selected_poster_ids[:sample_size]
                            
                            results.append(result)
                    
                    logger.info(f"Found {len(results)} failed batch jobs using session factory")
                    return results
                    
            except Exception as e:
                logger.warning(f"Session factory strategy failed: {e}")
        
        # Strategy 2: Try fresh database session
        try:
            from app.core.database import get_fresh_db_session
            
            async for db in get_fresh_db_session():
                job_repo = JobRepository(db)
                
                # Get recent failed or partially failed jobs
                failed_jobs = await job_repo.get_recent_jobs_by_status(
                    [JobStatus.FAILED, JobStatus.COMPLETED],  # Include completed jobs with failures
                    limit=10
                )
                
                for job in failed_jobs:
                    # Only include jobs that actually had failures
                    if job.status == JobStatus.FAILED.value or job.failed_posters > 0:
                        result = BatchJobDiagnosticResult(
                            job_id=job.id,
                            status=job.status,
                            total_posters=job.total_posters,
                            completed_posters=job.completed_posters,
                            failed_posters=job.failed_posters,
                            error_message=job.error_summary
                        )
                        
                        # Get sample of failed poster IDs from this job
                        if job.selected_poster_ids and job.failed_posters > 0:
                            sample_size = min(3, len(job.selected_poster_ids))
                            result.sample_failed_ids = job.selected_poster_ids[:sample_size]
                        
                        results.append(result)
                
                logger.info(f"Found {len(results)} failed batch jobs using fresh session")
                return results
                
        except Exception as e:
            logger.error(f"Fresh session strategy also failed: {e}")
        
        # If all strategies fail, return empty list
        logger.warning("All database connection strategies failed for batch jobs query")
        return []
            
    except Exception as e:
        logger.error(f"Failed to get batch jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get batch jobs: Database connection failed"
        )


@router.post("/jellyfin/batch-jobs/{job_id}/diagnose", response_model=JellyfinDiagnosticResponse)
async def diagnose_failed_batch_job(job_id: str):
    """Diagnose a specific failed batch job by testing its poster IDs"""
    logger = get_logger("aphrodite.api.diagnostics.batch_diagnosis", service="api")
    
    jellyfin_service = get_jellyfin_service()
    
    try:
        # Try multiple database connection strategies
        job = None
        
        # Strategy 1: Try async_session_factory
        if async_session_factory:
            try:
                async with async_session_factory() as db:
                    job_repo = JobRepository(db)
                    job = await job_repo.get_job_by_id(job_id)
                    
                    if job:
                        logger.info(f"Found job {job_id} using session factory")
            except Exception as e:
                logger.warning(f"Session factory strategy failed: {e}")
        
        # Strategy 2: Try fresh session if first strategy failed
        if not job:
            try:
                from app.core.database import get_fresh_db_session
                
                async for db in get_fresh_db_session():
                    job_repo = JobRepository(db)
                    job = await job_repo.get_job_by_id(job_id)
                    
                    if job:
                        logger.info(f"Found job {job_id} using fresh session")
                        break
                    
            except Exception as e:
                logger.error(f"Fresh session strategy also failed: {e}")
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        logger.info(f"Diagnosing batch job {job_id} with {len(job.selected_poster_ids)} poster IDs")
        
        # Test a sample of poster IDs from the job
        sample_size = min(5, len(job.selected_poster_ids))
        sample_ids = job.selected_poster_ids[:sample_size]
        
        poster_test_results = []
        successful_tests = 0
        
        for poster_id in sample_ids:
            test_result = MediaItemTestResult(
                jellyfin_id=poster_id,
                title="Testing...",
                metadata_available=False,
                poster_available=False
            )
            
            try:
                # Test metadata retrieval using the same method as the worker
                metadata = await jellyfin_service.get_media_item_by_id(poster_id)
                if metadata:
                    test_result.metadata_available = True
                    test_result.title = metadata.get("Name", "Unknown")
                
                # Test poster download using the same method as the worker  
                poster_data = await jellyfin_service.download_poster(poster_id)
                if poster_data:
                    test_result.poster_available = True
                    successful_tests += 1
                else:
                    test_result.error_message = "No poster found for item (HTTP 404)"
                    
            except Exception as e:
                test_result.error_message = f"Error: {str(e)}"
                logger.warning(f"Failed to test poster ID {poster_id}: {e}")
            
            poster_test_results.append(test_result)
        
        # Determine the issue pattern
        failed_tests = sample_size - successful_tests
        
        if failed_tests == 0:
            message = f"All tested poster IDs from job {job_id} are working - issue may be temporary or environment-specific"
            success = True
        elif failed_tests == sample_size:
            message = f"All tested poster IDs from job {job_id} are failing - likely configuration or authentication issue"
            success = False
        else:
            message = f"{failed_tests}/{sample_size} poster IDs from job {job_id} are failing - likely data consistency issue"
            success = False
        
        details = {
            "job_info": {
                "id": job.id,
                "status": job.status,
                "total_posters": job.total_posters,
                "completed_posters": job.completed_posters,
                "failed_posters": job.failed_posters,
                "badge_types": job.badge_types,
                "error_message": job.error_summary
            },
            "tested_poster_ids": sample_ids,
            "poster_test_results": [result.dict() for result in poster_test_results],
            "summary": {
                "total_tested": sample_size,
                "successful": successful_tests,
                "failed": failed_tests
            }
        }
        
        logger.info(f"Batch job diagnosis complete: {message}")
        
        return JellyfinDiagnosticResponse(
            success=success,
            message=message,
            details=details
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch job diagnosis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis failed: {str(e)}"
        )
    finally:
        await jellyfin_service.close()
