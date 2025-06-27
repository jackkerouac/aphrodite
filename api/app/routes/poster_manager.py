"""
Poster Manager API Routes

Endpoints for managing poster libraries and collections.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db_session
from app.services.jellyfin_service import get_jellyfin_service
from app.services.badge_processing.database_service import badge_settings_service
from app.services.tag_management_service import get_tag_management_service, BulkTagRequest, BulkTagResponse
from app.services.badge_processing import (
    UniversalBadgeProcessor,
    UniversalBadgeRequest,
    SingleBadgeRequest,
    ProcessingMode
)
from app.services.poster_management import PosterSelector, StorageManager
from app.services.poster_sources import get_poster_source_manager
from app.models.poster_sources import (
    PosterSearchRequest, PosterSearchResponse,
    ReplacePosterRequest, ReplacePosterResponse
)
from aphrodite_logging import get_logger
from pathlib import Path
import os
import time
import tempfile
import json

router = APIRouter(tags=["poster-manager"])
logger = get_logger("aphrodite.api.poster_manager", service="api")

class ApplyBadgesRequest(BaseModel):
    item_id: str
    jellyfin_id: str
    badge_types: List[str]

class ApplyBadgesResponse(BaseModel):
    success: bool
    message: str
    poster_url: Optional[str] = None
    applied_badges: Optional[List[str]] = None
    processing_time: Optional[float] = None

class RestoreOriginalRequest(BaseModel):
    item_id: str
    jellyfin_id: str

class RestoreOriginalResponse(BaseModel):
    success: bool
    message: str
    original_poster_found: bool = False
    restored_to_jellyfin: bool = False

@router.get("/libraries")
async def get_libraries(db: AsyncSession = Depends(get_db_session)):
    """Get all available Jellyfin libraries"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Test connection first with proper error handling
        try:
            connected, message = await jellyfin_service.test_connection()
            if not connected:
                logger.error(f"Jellyfin connection failed: {message}")
                return {
                    "error": f"Jellyfin connection failed: {message}",
                    "libraries": []
                }
        except Exception as conn_error:
            logger.error(f"Jellyfin connection test failed: {conn_error}")
            return {
                "error": f"Jellyfin connection error: {str(conn_error)}",
                "libraries": []
            }
        
        # Get libraries
        libraries = await jellyfin_service.get_libraries()
        
        # Filter to only movie and TV libraries
        filtered_libraries = []
        for library in libraries:
            collection_type = library.get("CollectionType", "").lower()
            if collection_type in ["movies", "tvshows"]:
                filtered_libraries.append({
                    "id": library.get("ItemId"),
                    "name": library.get("Name"),
                    "type": collection_type,
                    "path": library.get("Locations", [])
                })
        
        logger.info(f"Found {len(filtered_libraries)} media libraries")
        return {"libraries": filtered_libraries}
        
    except Exception as e:
        logger.error(f"Error getting libraries: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/libraries/{library_id}/items")
async def get_library_items(
    library_id: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Get items from a specific library with pagination"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Get library items
        all_items = await jellyfin_service.get_library_items(library_id)
        
        # Filter to only movies and TV shows (no episodes, seasons, etc.)
        filtered_items = []
        for item in all_items:
            item_type = item.get("Type", "").lower()
            if item_type in ["movie", "series"]:
                # Check for aphrodite-overlay tag to determine badge status
                tags = item.get("Tags", [])
                has_aphrodite_overlay = "aphrodite-overlay" in tags
                badge_status = "BADGED" if has_aphrodite_overlay else "ORIGINAL"
                
                # Build poster URL using our image proxy with cache-busting
                poster_url = None
                if item.get("Id"):
                    # Always add a cache-busting parameter to ensure fresh images
                    timestamp = int(time.time())  # Use current timestamp
                    poster_url = f"/api/v1/images/proxy/image/{item['Id']}/thumbnail?load={timestamp}"
                
                filtered_items.append({
                    "id": item.get("Id"),
                    "title": item.get("Name", "Unknown"),
                    "type": item_type,
                    "year": item.get("ProductionYear"),
                    "overview": item.get("Overview", ""),
                    "genres": item.get("Genres", []),
                    "community_rating": item.get("CommunityRating"),
                    "official_rating": item.get("OfficialRating"),
                    "poster_url": poster_url,
                    "jellyfin_id": item.get("Id"),
                    "badge_status": badge_status
                })
        
        # Sort alphabetically by title
        filtered_items.sort(key=lambda x: x["title"].lower())
        
        # Apply pagination
        total_count = len(filtered_items)
        paginated_items = filtered_items[offset:offset + limit] if limit else filtered_items[offset:]
        
        logger.info(f"Returning {len(paginated_items)} items from library {library_id} (total: {total_count})")
        
        return {
            "items": paginated_items,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(paginated_items) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error getting library items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/libraries/{library_id}/stats")
async def get_library_stats(library_id: str, db: AsyncSession = Depends(get_db_session)):
    """Get statistics for a specific library"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Get all library items
        all_items = await jellyfin_service.get_library_items(library_id)
        
        # Calculate statistics
        stats = {
            "total_items": 0,
            "movies": 0,
            "tv_shows": 0,
            "other": 0,
            "years": set(),
            "genres": set()
        }
        
        for item in all_items:
            item_type = item.get("Type", "").lower()
            stats["total_items"] += 1
            
            if item_type == "movie":
                stats["movies"] += 1
            elif item_type == "series":
                stats["tv_shows"] += 1
            else:
                stats["other"] += 1
            
            # Collect years and genres
            if item.get("ProductionYear"):
                stats["years"].add(item["ProductionYear"])
            
            for genre in item.get("Genres", []):
                stats["genres"].add(genre)
        
        # Convert sets to sorted lists
        stats["years"] = sorted(list(stats["years"]), reverse=True)
        stats["genres"] = sorted(list(stats["genres"]))
        
        logger.info(f"Library {library_id} stats: {stats['total_items']} total items")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting library stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_items(
    library_id: str,
    query: Optional[str] = None,
    badge_filter: Optional[str] = None,
    media_type: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Search and filter library items with badge filtering support"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Get all library items
        all_items = await jellyfin_service.get_library_items(library_id)
        
        # Filter items based on criteria
        filtered_items = []
        for item in all_items:
            item_type = item.get("Type", "").lower()
            
            # Only include movies and TV shows
            if item_type not in ["movie", "series"]:
                continue
            
            # Apply filters
            if media_type and item_type != media_type.lower():
                continue
            
            if genre and genre.lower() not in [g.lower() for g in item.get("Genres", [])]:
                continue
            
            if year and item.get("ProductionYear") != year:
                continue
            
            if query:
                title = item.get("Name", "").lower()
                if query.lower() not in title:
                    continue
            
            # Check for aphrodite-overlay tag to determine badge status
            tags = item.get("Tags", [])
            has_aphrodite_overlay = "aphrodite-overlay" in tags
            badge_status = "BADGED" if has_aphrodite_overlay else "ORIGINAL"
            
            # Apply badge filter
            if badge_filter:
                if badge_filter == "badged" and badge_status != "BADGED":
                    continue
                elif badge_filter == "original" and badge_status != "ORIGINAL":
                    continue
            
            # Debug logging for tag detection
            if tags:  # Only log if there are any tags
                logger.debug(f"Search item {item.get('Name')}: Tags = {tags}, Badge Status = {badge_status}")
            
            # Build poster URL using our image proxy with cache-busting
            poster_url = None
            if item.get("Id"):
                # Always add a cache-busting parameter to ensure fresh images
                timestamp = int(time.time())  # Use current timestamp
                poster_url = f"/api/v1/images/proxy/image/{item['Id']}/thumbnail?load={timestamp}"
            
            filtered_items.append({
                "id": item.get("Id"),
                "title": item.get("Name", "Unknown"),
                "type": item_type,
                "year": item.get("ProductionYear"),
                "overview": item.get("Overview", ""),
                "genres": item.get("Genres", []),
                "community_rating": item.get("CommunityRating"),
                "official_rating": item.get("OfficialRating"),
                "poster_url": poster_url,
                "jellyfin_id": item.get("Id"),
                "badge_status": badge_status
            })
        
        # Sort alphabetically by title
        filtered_items.sort(key=lambda x: x["title"].lower())
        
        # Apply pagination
        total_count = len(filtered_items)
        paginated_items = filtered_items[offset:offset + limit] if limit else filtered_items[offset:]
        
        logger.info(f"Search returned {len(paginated_items)} items (total: {total_count})")
        
        return {
            "items": paginated_items,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(paginated_items) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error searching items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_poster_manager_settings(db: AsyncSession = Depends(get_db_session)):
    """Get poster manager settings from database"""
    try:
        # Get settings using the badge settings service pattern
        settings = await badge_settings_service.get_poster_manager_settings_standalone()
        
        if not settings:
            # Return default settings
            default_settings = {
                "default_library_id": None,
                "items_per_page": 50,
                "enable_thumbnails": True,
                "thumbnail_size": "medium",
                "enable_auto_refresh": False,
                "refresh_interval": 300
            }
            logger.info("Using default poster manager settings")
            return {"settings": default_settings}
        
        logger.info("Loaded poster manager settings from database")
        return {"settings": settings}
        
    except Exception as e:
        logger.error(f"Error getting poster manager settings: {e}", exc_info=True)
        # Return defaults on error
        return {
            "settings": {
                "default_library_id": None,
                "items_per_page": 50,
                "enable_thumbnails": True,
                "thumbnail_size": "medium",
                "enable_auto_refresh": False,
                "refresh_interval": 300
            }
        }

@router.post("/tags/add")
async def add_tags_to_items(
    request: BulkTagRequest,
    db: AsyncSession = Depends(get_db_session)
) -> BulkTagResponse:
    """Add aphrodite-overlay tag to multiple items"""
    try:
        tag_service = get_tag_management_service()
        result = await tag_service.add_tag_to_items(request.item_ids, request.tag_name)
        
        logger.info(
            f"Bulk tag addition completed: {result.processed_count}/{len(request.item_ids)} successful"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk tag addition: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags/remove")
async def remove_tags_from_items(
    request: BulkTagRequest,
    db: AsyncSession = Depends(get_db_session)
) -> BulkTagResponse:
    """Remove aphrodite-overlay tag from multiple items"""
    try:
        tag_service = get_tag_management_service()
        result = await tag_service.remove_tag_from_items(request.item_ids, request.tag_name)
        
        logger.info(
            f"Bulk tag removal completed: {result.processed_count}/{len(request.item_ids)} successful"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk tag removal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}/tags")
async def get_item_tags(
    item_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, List[str]]:
    """Get current tags for an item"""
    try:
        tag_service = get_tag_management_service()
        tags = await tag_service.get_item_tags(item_id)
        
        if tags is None:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
        
        return {"tags": tags}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tags for item {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-badges", response_model=ApplyBadgesResponse)
async def apply_badges_to_poster(
    request: ApplyBadgesRequest,
    db: AsyncSession = Depends(get_db_session)
) -> ApplyBadgesResponse:
    """Apply badges to a specific poster"""
    try:
        logger.info(f"Applying badges to item {request.item_id} with badges: {request.badge_types}")
        
        if not request.badge_types:
            raise HTTPException(status_code=400, detail="At least one badge type must be selected")
        
        # Get the item's current poster from Jellyfin
        jellyfin_service = get_jellyfin_service()
        
        # Download the poster image for this specific item
        poster_data = await jellyfin_service.download_poster(request.jellyfin_id)
        if not poster_data:
            raise HTTPException(status_code=404, detail="Poster image not found for this item")
        
        # Cache the original poster before processing
        storage_manager = StorageManager()
        import tempfile
        import os
        
        # Cache the original poster for restore functionality
        try:
            cached_original_path = storage_manager.cache_original_poster(poster_data, request.jellyfin_id)
            logger.info(f"Successfully cached original poster for {request.item_id}")
        except Exception as cache_error:
            logger.warning(f"Failed to cache original poster for {request.item_id}: {cache_error}")
            # Don't fail the whole operation if caching fails
        
        # Create a temporary file for the downloaded poster
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(poster_data)
            temp_poster_path = temp_file.name
        
        # Create output path for the processed poster
        output_path = storage_manager.create_preview_output_path(f"jellyfin_{request.jellyfin_id}")
        
        # Create badge processing request
        single_request = SingleBadgeRequest(
            poster_path=temp_poster_path,
            badge_types=request.badge_types,
            use_demo_data=False,  # Use real Jellyfin metadata
            output_path=output_path,
            jellyfin_id=request.jellyfin_id  # Pass jellyfin_id for real metadata
        )
        
        universal_request = UniversalBadgeRequest(
            single_request=single_request,
            processing_mode=ProcessingMode.IMMEDIATE
        )
        
        # Process the poster with badges
        badge_processor = UniversalBadgeProcessor()
        processing_result = await badge_processor.process_request(universal_request)
        
        if processing_result.success and processing_result.results:
            poster_result = processing_result.results[0]
            
            if poster_result.success and poster_result.output_path:
                # Generate URL for the processed poster
                poster_url = storage_manager.get_file_url(poster_result.output_path)
                
                # Upload processed poster back to Jellyfin
                upload_success = await jellyfin_service.upload_poster_image(
                    request.jellyfin_id, 
                    poster_result.output_path
                )
                
                if upload_success:
                    logger.info(f"Successfully uploaded processed poster to Jellyfin for {request.item_id}")
                    
                    # Add aphrodite-overlay tag to track badged items
                    try:
                        tag_service = get_tag_management_service()
                        await tag_service.add_tag_to_items([request.jellyfin_id], "aphrodite-overlay")
                        logger.info(f"Added aphrodite-overlay tag to {request.item_id}")
                    except Exception as tag_error:
                        logger.warning(f"Failed to add tag to {request.item_id}: {tag_error}")
                else:
                    logger.warning(f"Failed to upload poster to Jellyfin for {request.item_id}")
                
                # Clean up temporary file
                try:
                    os.unlink(temp_poster_path)
                except:
                    pass  # Ignore cleanup errors
                
                logger.info(f"Successfully applied badges to poster for {request.item_id}")
                
                upload_message = " and uploaded to Jellyfin" if upload_success else " (Jellyfin upload failed)"
                
                return ApplyBadgesResponse(
                    success=True,
                    message=f"Badges applied successfully: {', '.join(poster_result.applied_badges)}{upload_message}",
                    poster_url=poster_url,
                    applied_badges=poster_result.applied_badges,
                    processing_time=processing_result.processing_time
                )
            else:
                logger.error(f"Badge processing failed: {poster_result.error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Badge processing failed: {poster_result.error}"
                )
        else:
            logger.error(f"Processing failed: {processing_result.error}")
            raise HTTPException(
                status_code=500,
                detail=f"Processing failed: {processing_result.error}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying badges to poster: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to apply badges: {str(e)}")

@router.post("/restore-original", response_model=RestoreOriginalResponse)
async def restore_original_poster(
    request: RestoreOriginalRequest,
    db: AsyncSession = Depends(get_db_session)
) -> RestoreOriginalResponse:
    """Restore original poster from cache and upload to Jellyfin"""
    try:
        logger.info(f"Restoring original poster for item {request.item_id} (Jellyfin ID: {request.jellyfin_id})")
        
        # Use the storage manager for consistent cache handling
        storage_manager = StorageManager()
        
        # Get cached original poster using the jellyfin_id (not item_id)
        cached_poster_path = storage_manager.get_cached_original(request.jellyfin_id)
        
        if not cached_poster_path:
            logger.warning(f"No original poster found in cache for Jellyfin ID: {request.jellyfin_id}")
            return RestoreOriginalResponse(
                success=False,
                message=f"No original poster found in cache for this item",
                original_poster_found=False,
                restored_to_jellyfin=False
            )
        
        # Verify the cached poster file exists and is readable
        cached_path = Path(cached_poster_path)
        if not cached_path.exists() or not cached_path.is_file():
            logger.error(f"Original poster file not accessible: {cached_path}")
            return RestoreOriginalResponse(
                success=False,
                message="Original poster file not accessible",
                original_poster_found=True,
                restored_to_jellyfin=False
            )
        
        # Verify the cache metadata to ensure we have the right poster
        cache_dir = cached_path.parent
        meta_files = list(cache_dir.glob(f"{cached_path.stem}.meta"))
        if meta_files:
            meta_file = meta_files[0]
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                
                # Validate that the cached poster is for the correct jellyfin_id
                if metadata.get('jellyfin_id') != request.jellyfin_id:
                    logger.error(f"Cache metadata mismatch! Expected {request.jellyfin_id}, got {metadata.get('jellyfin_id')}")
                    return RestoreOriginalResponse(
                        success=False,
                        message="Cache metadata validation failed - poster ID mismatch",
                        original_poster_found=True,
                        restored_to_jellyfin=False
                    )
                logger.info(f"Cache metadata validated for {request.jellyfin_id}")
            except Exception as meta_error:
                logger.warning(f"Could not validate cache metadata: {meta_error}")
                # Continue anyway, but log the issue
        
        logger.info(f"Found valid original poster: {cached_path.name}")
        
        # Upload original poster back to Jellyfin
        jellyfin_service = get_jellyfin_service()
        upload_success = await jellyfin_service.upload_poster_image(
            request.jellyfin_id,
            str(cached_path)
        )
        
        if not upload_success:
            logger.error(f"Failed to upload original poster to Jellyfin for {request.item_id}")
            return RestoreOriginalResponse(
                success=False,
                message="Failed to upload original poster to Jellyfin",
                original_poster_found=True,
                restored_to_jellyfin=False
            )
        
        logger.info(f"Successfully uploaded original poster to Jellyfin for {request.item_id}")
        
        # Remove aphrodite-overlay tag from the item
        tag_removal_success = False
        try:
            tag_service = get_tag_management_service()
            tag_result = await tag_service.remove_tag_from_items([request.jellyfin_id], "aphrodite-overlay")
            tag_removal_success = tag_result.processed_count > 0
            
            if tag_removal_success:
                logger.info(f"Successfully removed aphrodite-overlay tag from {request.item_id}")
            else:
                logger.warning(f"Tag removal reported no items processed for {request.item_id}")
                
        except Exception as tag_error:
            logger.warning(f"Failed to remove aphrodite-overlay tag from {request.item_id}: {tag_error}")
            # Don't fail the whole operation for tag removal failure
        
        # Clean up any processed preview files
        try:
            preview_pattern = f"jellyfin_{request.jellyfin_id}_*.jpg"
            preview_dir = Path("api/static/preview")
            
            if preview_dir.exists():
                preview_files = list(preview_dir.glob(preview_pattern))
                for preview_file in preview_files:
                    try:
                        preview_file.unlink()
                        logger.debug(f"Cleaned up preview file: {preview_file.name}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to clean up preview file {preview_file.name}: {cleanup_error}")
        except Exception as cleanup_error:
            logger.warning(f"Error during preview file cleanup: {cleanup_error}")
            # Don't fail the operation for cleanup errors
        
        tag_message = " and removed aphrodite-overlay tag" if tag_removal_success else " (tag removal failed)"
        
        return RestoreOriginalResponse(
            success=True,
            message=f"Original poster restored successfully{tag_message}",
            original_poster_found=True,
            restored_to_jellyfin=True
        )
        
    except Exception as e:
        logger.error(f"Error restoring original poster: {e}", exc_info=True)
        return RestoreOriginalResponse(
            success=False,
            message=f"Failed to restore original poster: {str(e)}",
            original_poster_found=False,
            restored_to_jellyfin=False
        )
