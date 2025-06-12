"""
Preview Routes

API endpoints for generating poster previews with badges.
Provides simple demonstration of badge effects using an example poster.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from shared import BaseResponse
from aphrodite_logging import get_logger

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
    jobId: str

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
        
        # For now, return a mock job ID
        # TODO: Implement actual preview generation with job system
        import uuid
        job_id = str(uuid.uuid4())
        
        logger.info(f"Preview generation requested with badges: {request.badgeTypes}")
        logger.info(f"Generated job ID: {job_id}")
        
        # TODO: Create actual background job for preview generation
        # This would:
        # 1. Copy example poster to working directory
        # 2. Apply selected badges using badge processing pipeline
        # 3. Save result to modified directory
        # 4. Update job status with poster URL
        
        return PreviewResponse(
            success=True,
            message=f"Preview generation started with {len(request.badgeTypes)} badge types",
            jobId=job_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
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
