"""
Configuration Management Routes

API endpoints for managing system and badge configurations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel
import asyncio

from app.core.database import get_db_session
from app.core.config import get_settings
from app.models.config import SystemConfigModel, BadgeConfigModel
from shared import BaseResponse, BadgeConfig, SystemConfig
from aphrodite_logging import get_logger

router = APIRouter()

# Pydantic models for request/response
class ConfigData(BaseModel):
    config: Dict[str, Any]

class ConfigFilesResponse(BaseModel):
    config_files: List[str]

class JellyfinTestRequest(BaseModel):
    url: str
    api_key: str
    user_id: str

class ApiTestRequest(BaseModel):
    api_key: str

class AnidbTestRequest(BaseModel):
    username: str
    password: str
    version: int = 1
    client_name: str = ""
    language: str = "en"

@router.get("/", response_model=dict)
async def config_root():
    """Configuration root endpoint"""
    return {
        "success": True,
        "message": "Configuration API endpoints",
        "endpoints": [
            "/files",
            "/debug",
            "/cache/clear",
            "/test-jellyfin",
            "/test-omdb",
            "/test-tmdb",
            "/test-mdblist",
            "/review_source_settings"
        ]
    }

@router.get("/debug", response_model=dict)
async def debug_settings():
    """Debug endpoint to see raw settings"""
    # Clear the settings cache to force reload
    get_settings.cache_clear()
    settings = get_settings()
    return {
        "jellyfin_url": settings.jellyfin_url,
        "jellyfin_api_key": settings.jellyfin_api_key,
        "debug": settings.debug,
        "environment": settings.environment,
        "all_settings": settings.model_dump()
    }

@router.get("/debug/db", response_model=dict)
async def debug_database(
    db: AsyncSession = Depends(get_db_session)
):
    """Debug database connectivity"""
    from app.core.database import DatabaseManager
    
    try:
        health = await DatabaseManager.health_check()
        connection_info = await DatabaseManager.get_connection_info()
        
        # Test creating a simple job model
        from app.models.jobs import ProcessingJobModel
        from sqlalchemy import text
        
        # Test table exists
        result = await db.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='processing_jobs')"))
        table_exists = result.scalar()
        
        return {
            "health": health,
            "connection_info": connection_info,
            "processing_jobs_table_exists": table_exists,
            "database_test": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "database_test": "failed"
        }

@router.get("/files", response_model=ConfigFilesResponse)
async def get_config_files():
    """Get list of available configuration files"""
    logger = get_logger("aphrodite.api.config.files", service="api")
    
    # List of configuration files that Aphrodite v2 supports
    config_files = [
        "settings.yaml",
        "badge_settings_audio.yml",
        "badge_settings_resolution.yml", 
        "badge_settings_review.yml",
        "badge_settings_awards.yml",
        "review_source_settings"
    ]
    
    logger.info(f"Returning {len(config_files)} available config files")
    return ConfigFilesResponse(config_files=config_files)

@router.get("/{filename}", response_model=ConfigData)
async def get_config(
    filename: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get configuration by filename"""
    logger = get_logger("aphrodite.api.config.get", service="api")
    
    try:
        # Query the database for the configuration
        stmt = select(SystemConfigModel).where(SystemConfigModel.key == filename)
        result = await db.execute(stmt)
        config_model = result.scalar_one_or_none()
        
        if config_model is None:
            # Return default empty configuration for new files
            logger.info(f"Configuration {filename} not found, returning default")
            return ConfigData(config={})
        
        logger.info(f"Retrieved configuration: {filename}")
        return ConfigData(config=config_model.value or {})
        
    except Exception as e:
        logger.error(f"Error retrieving configuration {filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )

@router.put("/{filename}", response_model=BaseResponse)
async def update_config(
    filename: str,
    config_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session)
):
    """Update configuration by filename"""
    logger = get_logger("aphrodite.api.config.update", service="api")
    
    try:
        # Check if configuration exists
        stmt = select(SystemConfigModel).where(SystemConfigModel.key == filename)
        result = await db.execute(stmt)
        existing_config = result.scalar_one_or_none()
        
        if existing_config:
            # Update existing configuration
            update_stmt = (
                update(SystemConfigModel)
                .where(SystemConfigModel.key == filename)
                .values(value=config_data)
            )
            await db.execute(update_stmt)
            logger.info(f"Updated existing configuration: {filename}")
        else:
            # Create new configuration
            insert_stmt = insert(SystemConfigModel).values(
                key=filename,
                value=config_data
            )
            await db.execute(insert_stmt)
            logger.info(f"Created new configuration: {filename}")
        
        await db.commit()
        
        # Clear settings cache for this configuration
        from app.services.settings_service import settings_service
        settings_service.clear_cache(filename)
        
        # If this is a badge settings file, also clear the compatibility layer cache
        if 'badge_settings' in filename:
            settings_service.invalidate_badge_cache()
            
            # Clear the compatibility layer cache as well
            try:
                from aphrodite_helpers.settings_compat import _settings_compat
                if _settings_compat and hasattr(_settings_compat, '_cached_settings'):
                    _settings_compat._cached_settings = None
                    logger.info(f"Cleared compatibility layer cache for {filename}")
            except Exception as e:
                logger.warning(f"Could not clear compatibility layer cache: {e}")
        
        return BaseResponse(message=f"Configuration {filename} saved successfully")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving configuration {filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )

@router.post("/cache/clear", response_model=BaseResponse)
async def clear_settings_cache():
    """Clear all settings cache - useful for forcing reload of settings"""
    logger = get_logger("aphrodite.api.config.cache.clear", service="api")
    
    try:
        # Clear the main settings service cache
        from app.services.settings_service import settings_service
        settings_service.clear_cache()
        
        # Clear the compatibility layer cache
        try:
            from aphrodite_helpers.settings_compat import _settings_compat
            if _settings_compat and hasattr(_settings_compat, '_cached_settings'):
                _settings_compat._cached_settings = None
                logger.info("Cleared compatibility layer cache")
        except Exception as e:
            logger.warning(f"Could not clear compatibility layer cache: {e}")
        
        logger.info("All settings caches cleared")
        return BaseResponse(message="Settings cache cleared successfully")
        
    except Exception as e:
        logger.error(f"Error clearing settings cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear settings cache: {str(e)}"
        )

@router.post("/cache/clear/{cache_key}", response_model=BaseResponse)
async def clear_specific_cache(cache_key: str):
    """Clear cache for a specific settings key"""
    logger = get_logger("aphrodite.api.config.cache.clear_specific", service="api")
    
    try:
        # Clear the specific cache entry
        from app.services.settings_service import settings_service
        settings_service.clear_cache(cache_key)
        
        # If it's a badge settings key, also clear compatibility layer
        if 'badge_settings' in cache_key:
            try:
                from aphrodite_helpers.settings_compat import _settings_compat
                if _settings_compat and hasattr(_settings_compat, '_cached_settings'):
                    _settings_compat._cached_settings = None
                    logger.info(f"Cleared compatibility layer cache for {cache_key}")
            except Exception as e:
                logger.warning(f"Could not clear compatibility layer cache: {e}")
        
        logger.info(f"Cache cleared for {cache_key}")
        return BaseResponse(message=f"Cache cleared for {cache_key}")
        
    except Exception as e:
        logger.error(f"Error clearing cache for {cache_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache for {cache_key}: {str(e)}"
        )

# Add the rest of the original endpoints that weren't shown in the corrupted file...
@router.post("/test-jellyfin", response_model=BaseResponse)
async def test_jellyfin_connection(request: JellyfinTestRequest):
    """Test Jellyfin API connection"""
    logger = get_logger("aphrodite.api.config.test.jellyfin", service="api")
    
    try:
        import aiohttp
        
        # Prepare the test URL
        test_url = f"{request.url.rstrip('/')}/System/Info"
        headers = {
            "X-Emby-Token": request.api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Testing Jellyfin connection to: {request.url}")
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    server_name = data.get("ServerName", "Unknown")
                    version = data.get("Version", "Unknown")
                    
                    logger.info(f"Jellyfin connection successful: {server_name} v{version}")
                    return BaseResponse(
                        message=f"Connected to {server_name} (v{version})"
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Jellyfin connection failed: HTTP {response.status} - {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Jellyfin connection failed: HTTP {response.status}"
                    )
                    
    except asyncio.TimeoutError:
        logger.error("Jellyfin connection timed out")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Connection timed out"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing Jellyfin connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )

# New API connection test endpoints
@router.post("/test-omdb", response_model=BaseResponse)
async def test_omdb_connection(request: ApiTestRequest):
    """Test OMDb API key by making a sample request."""
    logger = get_logger("aphrodite.api.config.test.omdb", service="api")

    try:
        import aiohttp

        test_url = f"http://www.omdbapi.com/?i=tt0133093&apikey={request.api_key}"
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Response") == "True":
                        logger.info("OMDb connection successful")
                        return BaseResponse(message="Connection successful!")
                    error_msg = data.get("Error", "Unknown error")
                    logger.error(f"OMDb API error: {error_msg}")
                    return BaseResponse(
                        success=False,
                        message=f"OMDb API error: {error_msg}"
                    )
                error_text = await response.text()
                logger.error(f"OMDb connection failed: HTTP {response.status} - {error_text}")
                return BaseResponse(
                    success=False,
                    message=f"HTTP {response.status}: {error_text[:100]}"
                )

    except asyncio.TimeoutError:
        logger.error("OMDb connection timed out")
        return BaseResponse(
            success=False,
            message="Connection timed out"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing OMDb connection: {e}", exc_info=True)
        return BaseResponse(
            success=False,
            message=f"Test failed: {str(e)}"
        )


@router.post("/test-tmdb", response_model=BaseResponse)
async def test_tmdb_connection(request: ApiTestRequest):
    """Test TMDb API key by making a sample request."""
    logger = get_logger("aphrodite.api.config.test.tmdb", service="api")

    try:
        import aiohttp

        test_url = "https://api.themoviedb.org/3/movie/603"
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "accept": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    await response.json()
                    logger.info("TMDb connection successful")
                    return BaseResponse(message="Connection successful!")
                error_text = await response.text()
                logger.error(f"TMDb connection failed: HTTP {response.status} - {error_text}")
                return BaseResponse(
                    success=False,
                    message=f"HTTP {response.status}: {error_text[:100]}"
                )

    except asyncio.TimeoutError:
        logger.error("TMDb connection timed out")
        return BaseResponse(
            success=False,
            message="Connection timed out"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing TMDb connection: {e}", exc_info=True)
        return BaseResponse(
            success=False,
            message=f"Test failed: {str(e)}"
        )


@router.post("/test-mdblist", response_model=BaseResponse)
async def test_mdblist_connection(request: ApiTestRequest):
    """Test MDBList API key by making a sample request."""
    logger = get_logger("aphrodite.api.config.test.mdblist", service="api")

    try:
        import aiohttp

        test_url = f"https://mdblist.com/api/?i=tt0133093&apikey={request.api_key}"
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if the response indicates success
                    # MDBList returns different response formats, so let's be more flexible
                    if isinstance(data, dict):
                        # Check for various success indicators
                        if (data.get("response") == "True" or 
                            data.get("id") or 
                            data.get("imdb_id") or
                            "title" in data):
                            logger.info("MDBList connection successful")
                            return BaseResponse(message="Connection successful!")
                        # Check for error messages
                        elif "error" in data:
                            error_msg = data.get("error", "Unknown error")
                            logger.error(f"MDBList API error: {error_msg}")
                            return BaseResponse(
                                success=False,
                                message=f"MDBList API error: {error_msg}"
                            )
                        else:
                            # Got a response but format is unexpected
                            logger.info(f"MDBList responded with data: {data}")
                            return BaseResponse(message="Connection successful - API responded with data")
                    else:
                        # Non-dict response, assume success if we got data
                        logger.info("MDBList connection successful - got response data")
                        return BaseResponse(message="Connection successful!")
                else:
                    error_text = await response.text()
                    logger.error(f"MDBList connection failed: HTTP {response.status} - {error_text}")
                    return BaseResponse(
                        success=False,
                        message=f"HTTP {response.status}: {error_text[:100]}"
                    )

    except asyncio.TimeoutError:
        logger.error("MDBList connection timed out")
        return BaseResponse(
            success=False,
            message="Connection timed out"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing MDBList connection: {e}", exc_info=True)
        return BaseResponse(
            success=False,
            message=f"Test failed: {str(e)}"
        )

@router.get("/review_source_settings", response_model=ConfigData)
async def get_review_source_settings(
    db: AsyncSession = Depends(get_db_session)
):
    """Get review source settings configuration"""
    logger = get_logger("aphrodite.api.config.review_source_settings.get", service="api")
    
    try:
        # Query the database for the review source settings
        stmt = select(SystemConfigModel).where(SystemConfigModel.key == "review_source_settings")
        result = await db.execute(stmt)
        config_model = result.scalar_one_or_none()
        
        if config_model is None:
            # Return default review source settings
            logger.info("Review source settings not found, returning defaults")
            default_settings = {
                "max_badges_display": 4,
                "source_selection_mode": "priority",
                "show_percentage_only": True,
                "group_related_sources": True,
                "anime_sources_for_anime_only": True
            }
            return ConfigData(config=default_settings)
        
        logger.info("Retrieved review source settings")
        return ConfigData(config=config_model.value or {})
        
    except Exception as e:
        logger.error(f"Error retrieving review source settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve review source settings: {str(e)}"
        )

@router.put("/review_source_settings", response_model=BaseResponse)
async def update_review_source_settings(
    config_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session)
):
    """Update review source settings configuration"""
    logger = get_logger("aphrodite.api.config.review_source_settings.update", service="api")
    
    try:
        # Check if configuration exists
        stmt = select(SystemConfigModel).where(SystemConfigModel.key == "review_source_settings")
        result = await db.execute(stmt)
        existing_config = result.scalar_one_or_none()
        
        if existing_config:
            # Update existing configuration
            update_stmt = (
                update(SystemConfigModel)
                .where(SystemConfigModel.key == "review_source_settings")
                .values(value=config_data)
            )
            await db.execute(update_stmt)
            logger.info("Updated existing review source settings")
        else:
            # Create new configuration
            insert_stmt = insert(SystemConfigModel).values(
                key="review_source_settings",
                value=config_data
            )
            await db.execute(insert_stmt)
            logger.info("Created new review source settings")
        
        await db.commit()
        
        # Clear settings cache
        from app.services.settings_service import settings_service
        settings_service.clear_cache("review_source_settings")
        
        logger.info(f"Review source settings saved: {config_data}")
        return BaseResponse(message="Review source settings saved successfully")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving review source settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save review source settings: {str(e)}"
        )
