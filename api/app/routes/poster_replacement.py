"""
Poster Replacement API Routes

Endpoints for searching and replacing posters from external sources.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import time
import tempfile
import os

from app.core.database import get_db_session
from app.services.jellyfin_service import get_jellyfin_service
from app.services.tag_management_service import get_tag_management_service
from app.services.poster_management import StorageManager
from app.services.poster_sources import get_poster_source_manager
from app.models.poster_sources import (
    PosterSearchRequest, PosterSearchResponse,
    ReplacePosterRequest, ReplacePosterResponse,
    BulkReplacePosterRequest, BulkReplacePosterResponse
)
from app.services.bulk_poster_replacement import get_bulk_poster_replacement_service
from aphrodite_logging import get_logger

router = APIRouter(tags=["poster-replacement"])
logger = get_logger("aphrodite.api.poster_replacement", service="api")

@router.get("/items/{item_id}/poster-sources", response_model=PosterSearchResponse)
async def search_poster_sources(
    item_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> PosterSearchResponse:
    """Search for alternative poster sources for an item"""
    try:
        logger.info(f"Searching poster sources for item {item_id}")
        
        # Get item details from Jellyfin
        jellyfin_service = get_jellyfin_service()
        item_details = await jellyfin_service.get_item_details(item_id)
        
        if not item_details:
            raise HTTPException(status_code=404, detail="Item not found in Jellyfin")
            
        # Extract search parameters
        title = item_details.get("Name", "")
        year = item_details.get("ProductionYear")
        item_type = item_details.get("Type", "").lower()
        
        if not title:
            raise HTTPException(status_code=400, detail="Item title not found")
            
        # Create search request
        search_request = PosterSearchRequest(
            item_id=item_id,
            jellyfin_id=item_id,
            title=title,
            year=year,
            item_type=item_type
        )
        
        # Get poster source manager and search
        poster_manager = await get_poster_source_manager()
        result = await poster_manager.search_posters(search_request)
        
        logger.info(f"Found {result.total_found} posters for {title} from {len(result.sources_searched)} sources")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching poster sources for {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search poster sources: {str(e)}")

@router.post("/items/{item_id}/replace-poster", response_model=ReplacePosterResponse)
async def replace_poster(
    item_id: str,
    request: ReplacePosterRequest,
    db: AsyncSession = Depends(get_db_session)
) -> ReplacePosterResponse:
    """Replace poster with selected alternative from external source"""
    start_time = time.time()
    
    try:
        logger.info(f"Replacing poster for item {item_id} with {request.selected_poster.source} poster")
        
        if request.item_id != item_id:
            raise HTTPException(status_code=400, detail="Item ID mismatch")
            
        # Get poster source manager
        poster_manager = await get_poster_source_manager()
        
        # Download the selected poster
        poster_data = await poster_manager.download_poster(request.selected_poster)
        if not poster_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Failed to download poster from {request.selected_poster.source}"
            )
            
        logger.info(f"Downloaded poster from {request.selected_poster.source} ({len(poster_data)} bytes)")
        
        # Cache the current poster as original before replacement
        jellyfin_service = get_jellyfin_service()
        
        # Get current poster from Jellyfin to cache as original
        current_poster_data = await jellyfin_service.download_poster(request.jellyfin_id)
        if current_poster_data:
            try:
                storage_manager = StorageManager()
                cached_original_path = storage_manager.cache_original_poster(
                    current_poster_data, 
                    request.jellyfin_id
                )
                logger.info(f"Cached current poster as original for {item_id}")
            except Exception as cache_error:
                logger.warning(f"Failed to cache current poster for {item_id}: {cache_error}")
                # Don't fail the operation if caching fails
        
        # Create temporary file for the new poster
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(poster_data)
            temp_poster_path = temp_file.name
            
        try:
            # Upload new poster to Jellyfin
            upload_success = await jellyfin_service.upload_poster_image(
                request.jellyfin_id,
                temp_poster_path
            )
            
            if not upload_success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload new poster to Jellyfin"
                )
                
            logger.info(f"Successfully uploaded new poster to Jellyfin for {item_id}")
            
            # Remove aphrodite-overlay tag since this is now original content
            tag_removal_success = False
            try:
                tag_service = get_tag_management_service()
                tag_result = await tag_service.remove_tag_from_items(
                    [request.jellyfin_id], 
                    "aphrodite-overlay"
                )
                tag_removal_success = tag_result.processed_count > 0
                
                if tag_removal_success:
                    logger.info(f"Removed aphrodite-overlay tag from {item_id}")
                    
            except Exception as tag_error:
                logger.warning(f"Failed to remove tag from {item_id}: {tag_error}")
                # Don't fail the operation for tag issues
                
            # Generate new poster URL with cache-busting
            timestamp = int(time.time())
            new_poster_url = f"/api/v1/images/proxy/image/{request.jellyfin_id}/thumbnail?replaced={timestamp}"
            
            processing_time = time.time() - start_time
            
            tag_message = " and removed aphrodite-overlay tag" if tag_removal_success else ""
            
            return ReplacePosterResponse(
                success=True,
                message=f"Poster replaced successfully with {request.selected_poster.source} image{tag_message}",
                new_poster_url=new_poster_url,
                uploaded_to_jellyfin=True,
                tag_updated=tag_removal_success,
                processing_time=processing_time
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_poster_path)
            except:
                pass  # Ignore cleanup errors
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replacing poster for {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to replace poster: {str(e)}")

@router.get("/poster-sources/available")
async def get_available_poster_sources(
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get list of available and configured poster sources"""
    try:
        poster_manager = await get_poster_source_manager()
        available_sources = poster_manager.get_available_sources()
        
        sources_info = []
        for source in available_sources:
            sources_info.append({
                "name": source.value,
                "display_name": source.value.upper(),
                "available": poster_manager.is_source_available(source)
            })
            
        logger.info(f"Available poster sources: {[s['name'] for s in sources_info]}")
        
        return {
            "sources": sources_info,
            "total_available": len(available_sources)
        }
        
    except Exception as e:
        logger.error(f"Error getting available poster sources: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get poster sources: {str(e)}")

@router.post("/bulk-replace-posters", response_model=BulkReplacePosterResponse)
async def bulk_replace_posters(
    request: BulkReplacePosterRequest,
    db: AsyncSession = Depends(get_db_session)
) -> BulkReplacePosterResponse:
    """Replace posters for multiple items with random alternatives from external sources"""
    try:
        logger.info(
            f"Starting bulk poster replacement for {len(request.item_ids)} items "
            f"with language preference: {request.language_preference}"
        )
        
        # Validate request
        if not request.item_ids or not request.jellyfin_ids:
            raise HTTPException(status_code=400, detail="Item IDs and Jellyfin IDs are required")
            
        if len(request.item_ids) != len(request.jellyfin_ids):
            raise HTTPException(
                status_code=400, 
                detail="Item IDs and Jellyfin IDs must have the same length"
            )
            
        if len(request.item_ids) > 50:  # Reasonable limit
            raise HTTPException(
                status_code=400, 
                detail="Maximum 50 items can be processed in a single batch"
            )
            
        # Get bulk replacement service and process
        bulk_service = await get_bulk_poster_replacement_service()
        result = await bulk_service.process_bulk_replacement(request, db)
        
        logger.info(
            f"Bulk replacement completed: {result.successful_replacements} successful, "
            f"{result.failed_replacements} failed"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk poster replacement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process bulk replacement: {str(e)}")
