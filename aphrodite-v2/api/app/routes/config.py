"""
Configuration Management Routes

API endpoints for managing system and badge configurations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

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
        "badge_settings_awards.yml"
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
        
        return BaseResponse(message=f"Configuration {filename} saved successfully")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving configuration {filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )

@router.post("/test-jellyfin", response_model=BaseResponse)
async def test_jellyfin_connection(request: JellyfinTestRequest):
    """Test Jellyfin API connection"""
    logger = get_logger("aphrodite.api.config.test.jellyfin", service="api")
    
    try:
        import aiohttp
        import asyncio
        
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
                    
    except aiohttp.ClientTimeout:
        logger.error("Jellyfin connection timed out")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Connection timed out"
        )
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Jellyfin connection error (network): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot connect to server: {str(e)}"
        )
    except aiohttp.ClientError as e:
        logger.error(f"Jellyfin connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing Jellyfin connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )

@router.post("/test-tmdb", response_model=BaseResponse)
async def test_tmdb_connection(request: ApiTestRequest):
    """Test TMDB API connection"""
    logger = get_logger("aphrodite.api.config.test.tmdb", service="api")
    
    try:
        import aiohttp
        
        # Test TMDB API with a simple configuration request
        test_url = "https://api.themoviedb.org/3/configuration"
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("Testing TMDB API connection")
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    logger.info("TMDB API connection successful")
                    return BaseResponse(message="TMDB API connection successful")
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB API connection failed: HTTP {response.status} - {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"TMDB API connection failed: HTTP {response.status}"
                    )
                    
    except Exception as e:
        logger.error(f"Error testing TMDB connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TMDB test failed: {str(e)}"
        )

@router.post("/test-omdb", response_model=BaseResponse)
async def test_omdb_connection(request: ApiTestRequest):
    """Test OMDB API connection"""
    logger = get_logger("aphrodite.api.config.test.omdb", service="api")
    
    try:
        import aiohttp
        
        # Test OMDB API with a simple movie search
        test_url = f"http://www.omdbapi.com/?apikey={request.api_key}&t=The+Matrix"
        
        logger.info("Testing OMDB API connection")
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Response") == "True":
                        logger.info("OMDB API connection successful")
                        return BaseResponse(message="OMDB API connection successful")
                    else:
                        error = data.get("Error", "Unknown error")
                        logger.error(f"OMDB API error: {error}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"OMDB API error: {error}"
                        )
                else:
                    logger.error(f"OMDB API connection failed: HTTP {response.status}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"OMDB API connection failed: HTTP {response.status}"
                    )
                    
    except Exception as e:
        logger.error(f"Error testing OMDB connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OMDB test failed: {str(e)}"
        )

@router.post("/test-mdblist", response_model=BaseResponse)
async def test_mdblist_connection(request: ApiTestRequest):
    """Test MDBList API connection"""
    logger = get_logger("aphrodite.api.config.test.mdblist", service="api")
    
    try:
        import aiohttp
        
        # Test MDBList API with a simple movie lookup
        # MDBList uses different endpoint and parameter format
        test_url = f"https://mdblist.com/api/?apikey={request.api_key}&i=tt0133093"  # The Matrix
        
        logger.info("Testing MDBList API connection")
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if the response contains valid data
                    if isinstance(data, dict) and data.get('title'):
                        logger.info("MDBList API connection successful")
                        return BaseResponse(message="MDBList API connection successful")
                    elif isinstance(data, dict) and data.get('error'):
                        error_msg = data.get('error', 'Unknown error')
                        logger.error(f"MDBList API error: {error_msg}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"MDBList API error: {error_msg}"
                        )
                    else:
                        logger.error(f"MDBList API unexpected response: {data}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="MDBList API returned unexpected response"
                        )
                else:
                    error_text = await response.text()
                    logger.error(f"MDBList API connection failed: HTTP {response.status} - {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"MDBList API connection failed: HTTP {response.status}"
                    )
                    
    except Exception as e:
        logger.error(f"Error testing MDBList connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MDBList test failed: {str(e)}"
        )

@router.post("/test-anidb", response_model=BaseResponse)
async def test_anidb_connection(request: AnidbTestRequest):
    """Test AniDB API connection"""
    logger = get_logger("aphrodite.api.config.test.anidb", service="api")
    
    # Note: AniDB doesn't have a simple REST API test, so we'll just validate the credentials format
    try:
        if not request.username or not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
        
        logger.info("AniDB credentials format validated")
        return BaseResponse(message="AniDB credentials format validated (full connection test not implemented)")
        
    except Exception as e:
        logger.error(f"Error testing AniDB connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AniDB test failed: {str(e)}"
        )

@router.get("/system", response_model=SystemConfig)
async def get_system_config():
    """Get current system configuration"""
    logger = get_logger("aphrodite.api.config.system", service="api")
    
    settings = get_settings()
    logger.info("Getting system configuration")
    
    return SystemConfig(
        version="2.0.0",
        debug=settings.debug,
        jellyfin_url=settings.jellyfin_url,
        jellyfin_api_key=settings.jellyfin_api_key,
        max_concurrent_jobs=settings.max_concurrent_jobs,
        job_timeout=settings.job_timeout,
        badges=[]  # TODO: Load from database
    )

@router.put("/system", response_model=BaseResponse)
async def update_system_config(
    config: SystemConfig,
    db: AsyncSession = Depends(get_db_session)
):
    """Update system configuration"""
    logger = get_logger("aphrodite.api.config.system.update", service="api")
    
    # TODO: Implement configuration update
    logger.info("Updating system configuration")
    
    return BaseResponse(message="System configuration updated successfully")

@router.get("/badges", response_model=List[BadgeConfig])
async def get_badge_configs(
    db: AsyncSession = Depends(get_db_session)
):
    """Get all badge configurations"""
    logger = get_logger("aphrodite.api.config.badges", service="api")
    
    # TODO: Load badge configurations from database
    logger.info("Getting badge configurations")
    
    return []

@router.post("/badges", response_model=BaseResponse)
async def create_badge_config(
    config: BadgeConfig,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new badge configuration"""
    logger = get_logger("aphrodite.api.config.badges.create", service="api")
    
    # TODO: Save badge configuration to database
    logger.info(f"Creating badge configuration: {config.type}")
    
    return BaseResponse(message="Badge configuration created successfully")

@router.put("/badges/{badge_type}", response_model=BaseResponse)
async def update_badge_config(
    badge_type: str,
    config: BadgeConfig,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a badge configuration"""
    logger = get_logger("aphrodite.api.config.badges.update", service="api")
    
    # TODO: Update badge configuration in database
    logger.info(f"Updating badge configuration: {badge_type}")
    
    return BaseResponse(message=f"Badge configuration {badge_type} updated successfully")
