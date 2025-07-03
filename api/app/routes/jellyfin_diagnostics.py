"""
Jellyfin Diagnostics API

Endpoints for diagnosing Jellyfin connectivity issues in production.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.jellyfin_service import get_jellyfin_service
from app.core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.media import MediaItemModel
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
    """Check Jellyfin configuration status"""
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
        
        if missing_settings:
            message = f"Jellyfin configuration incomplete. Missing: {', '.join(missing_settings)}"
            success = False
        else:
            message = "Jellyfin configuration appears complete"
            success = True
        
        details["missing_settings"] = missing_settings
        
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
        
        # Determine overall success
        success = any(test.get("success", False) for test in details["tests"].values())
        
        if success:
            message = f"Jellyfin ID {jellyfin_id} is valid and accessible"
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
