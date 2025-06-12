"""
Media Management Routes

API endpoints for managing media items and posters.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.media_service import get_media_service
from app.services.job_service import get_job_service
from shared.types import BaseResponse, MediaItem, MediaListResponse
from aphrodite_logging import get_logger

router = APIRouter()

@router.get("/", response_model=MediaListResponse)
async def list_media(
    page: int = 1,
    per_page: int = 20,
    media_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List media items with pagination"""
    logger = get_logger("aphrodite.api.media.list", service="api")
    media_service = get_media_service()
    
    logger.info(f"Listing media items: page={page}, per_page={per_page}, type={media_type}")
    
    try:
        items, total = await media_service.get_media_items(
            db, page=page, per_page=per_page, 
            media_type=media_type, search=search
        )
        
        return MediaListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            message="Media list retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing media items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{media_id}", response_model=MediaItem)
async def get_media(
    media_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific media item"""
    logger = get_logger("aphrodite.api.media.get", service="api", media_id=media_id)
    media_service = get_media_service()
    
    logger.info(f"Getting media item: {media_id}")
    
    try:
        media_item = await media_service.get_media_by_id(db, media_id)
        if not media_item:
            raise HTTPException(status_code=404, detail="Media item not found")
        
        return media_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting media item {media_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/scan")
async def scan_media_library(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Scan Jellyfin library for new media"""
    logger = get_logger("aphrodite.api.media.scan", service="api")
    job_service = get_job_service()
    
    logger.info("Starting media library scan")
    
    try:
        # Create a library scan job
        job = await job_service.create_processing_job(
            db, 
            media_id="library_scan",  # Special ID for library scans
            job_type="library_scan"
        )
        
        if job:
            # Queue the job for background processing
            await job_service.queue_job(db, job.id)
            return BaseResponse(message=f"Library scan started (Job ID: {job.id})")
        else:
            raise HTTPException(status_code=500, detail="Failed to create scan job")
            
    except Exception as e:
        logger.error(f"Error starting library scan: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{media_id}/process")
async def process_media_poster(
    media_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Start poster processing for a media item"""
    logger = get_logger("aphrodite.api.media.process", service="api", media_id=media_id)
    job_service = get_job_service()
    
    logger.info(f"Starting poster processing for media: {media_id}")
    
    try:
        # Create a poster processing job
        job = await job_service.create_processing_job(
            db,
            media_id=media_id,
            job_type="poster_processing"
        )
        
        if job:
            # Queue the job for background processing
            await job_service.queue_job(db, job.id)
            return BaseResponse(message=f"Poster processing started (Job ID: {job.id})")
        else:
            raise HTTPException(status_code=500, detail="Failed to create processing job")
            
    except Exception as e:
        logger.error(f"Error starting poster processing for {media_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
