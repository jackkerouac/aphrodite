"""
Preview Routes

API endpoints for generating poster previews with badges.
Provides simple demonstration of badge effects using an example poster.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid

from shared import BaseResponse
from aphrodite_logging import get_logger
from app.services.badge_processing import (
    UniversalBadgeProcessor,
    UniversalBadgeRequest,
    SingleBadgeRequest,
    ProcessingMode
)
from app.services.poster_management import PosterSelector, StorageManager

router = APIRouter()

class BadgeType(BaseModel):
    id: str
    name: str
    description: str

class PreviewRequest(BaseModel):
    badgeTypes: List[str]

class PreviewResponse(BaseModel):
    success: bool
    message: str
    posterUrl: str = None
    appliedBadges: List[str] = []
    processingTime: float = 0.0

class BadgeTypesResponse(BaseModel):
    success: bool
    badgeTypes: List[BadgeType]

@router.get("/badge-types", response_model=BadgeTypesResponse)
async def get_badge_types():
    """Get all available badge types for preview"""
    logger = get_logger("aphrodite.api.preview.badge_types", service="api")
    
    badge_types = [
        BadgeType(
            id="audio",
            name="Audio",
            description="Audio codec badges (DTS-X, Atmos, etc.)"
        ),
        BadgeType(
            id="resolution",
            name="Resolution", 
            description="Resolution badges (4K, 1080p, etc.)"
        ),
        BadgeType(
            id="review",
            name="Review",
            description="Review/rating badges (IMDb, TMDb, etc.)"
        ),
        BadgeType(
            id="awards",
            name="Awards",
            description="Awards badges (Oscars, Emmys, etc.)"
        )
    ]
    
    logger.info(f"Returning {len(badge_types)} available badge types")
    
    return BadgeTypesResponse(
        success=True,
        badgeTypes=badge_types
    )

@router.post("/generate", response_model=PreviewResponse)
async def generate_preview(request: PreviewRequest):
    """Generate a preview poster with selected badges"""
    logger = get_logger("aphrodite.api.preview.generate", service="api")
    
    try:
        if not request.badgeTypes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one badge type must be selected"
            )
        
        # Generate unique job ID for logging
        job_id = str(uuid.uuid4())
        
        logger.info(f"Preview generation requested with badges: {request.badgeTypes}")
        logger.info(f"Generated job ID: {job_id}")
        
        # Initialize services
        poster_selector = PosterSelector()
        storage_manager = StorageManager()
        badge_processor = UniversalBadgeProcessor()
        
        # Select random poster from Jellyfin or originals
        selected_poster = await poster_selector.get_random_poster_async()
        if not selected_poster:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No original posters available for preview"
            )
        
        logger.info(f"Selected poster for preview: {selected_poster}")
        
        # Create output path for preview
        output_path = storage_manager.create_preview_output_path(selected_poster)
        
        # Create badge processing request
        single_request = SingleBadgeRequest(
            poster_path=selected_poster,
            badge_types=request.badgeTypes,
            use_demo_data=False,  # Use real Jellyfin metadata instead of demo data
            output_path=output_path
        )
        
        universal_request = UniversalBadgeRequest(
            single_request=single_request,
            processing_mode=ProcessingMode.IMMEDIATE  # Process immediately for preview
        )
        
        # Process the poster with badges
        processing_result = await badge_processor.process_request(universal_request)
        
        if processing_result.success and processing_result.results:
            poster_result = processing_result.results[0]
            
            if poster_result.success and poster_result.output_path:
                # Generate URL for the processed poster
                poster_url = storage_manager.get_file_url(poster_result.output_path)
                
                logger.info(f"Preview generated successfully: {poster_result.output_path}")
                
                return PreviewResponse(
                    success=True,
                    message=f"Preview generated with {len(poster_result.applied_badges)} badges",
                    posterUrl=poster_url,
                    appliedBadges=poster_result.applied_badges,
                    processingTime=processing_result.processing_time
                )
            else:
                logger.error(f"Badge processing failed: {poster_result.error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Badge processing failed: {poster_result.error}"
                )
        else:
            logger.error(f"Preview processing failed: {processing_result.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Preview processing failed: {processing_result.error}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )

# Cleanup endpoint for old preview files
@router.delete("/preview/cleanup")
async def cleanup_preview_files():
    """Clean up old preview files"""
    logger = get_logger("aphrodite.api.preview.cleanup", service="api")
    
    try:
        storage_manager = StorageManager()
        cleaned_count = storage_manager.cleanup_preview_files(max_age_hours=24)
        
        logger.info(f"Cleaned up {cleaned_count} old preview files")
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} old preview files"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up preview files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup preview files: {str(e)}"
        )

# Cleanup endpoint for cached Jellyfin posters
@router.delete("/cache/cleanup")
async def cleanup_cached_posters():
    """Clean up old cached Jellyfin posters"""
    logger = get_logger("aphrodite.api.preview.cache_cleanup", service="api")
    
    try:
        poster_selector = PosterSelector()
        cleaned_count = poster_selector.cleanup_cached_posters(max_age_hours=24)
        
        logger.info(f"Cleaned up {cleaned_count} old cached posters")
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} old cached Jellyfin posters"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up cached posters: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup cached posters: {str(e)}"
        )

# Libraries endpoint (placeholder for future Jellyfin integration)
@router.get("/libraries")
async def get_libraries():
    """Get available Jellyfin libraries (placeholder)"""
    logger = get_logger("aphrodite.api.preview.libraries", service="api")
    
    # TODO: Implement Jellyfin library fetching
    # This would connect to Jellyfin API and get available libraries
    
    logger.info("Libraries endpoint called (placeholder)")
    
    return {
        "success": True,
        "libraries": [
            {"id": "1", "name": "Movies", "type": "movies"},
            {"id": "2", "name": "TV Shows", "type": "series"}
        ]
    }

# Media endpoint (placeholder for future Jellyfin integration)
@router.get("/media")
async def get_media(library_id: str = None, search: str = None, page: int = 1, limit: int = 50):
    """Get media items from library (placeholder)"""
    logger = get_logger("aphrodite.api.preview.media", service="api")
    
    # TODO: Implement Jellyfin media fetching
    # This would fetch media items from selected library
    
    logger.info(f"Media endpoint called with library_id={library_id}, search={search}")
    
    return {
        "success": True,
        "media": [],
        "total": 0,
        "page": page,
        "limit": limit
    }
