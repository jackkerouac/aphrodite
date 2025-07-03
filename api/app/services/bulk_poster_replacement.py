"""
Bulk Poster Replacement Service

Handles bulk replacement of posters with random alternatives from external sources.
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.jellyfin_service import get_jellyfin_service
from app.services.tag_management_service import get_tag_management_service
from app.services.poster_management import StorageManager
from app.services.poster_sources import get_poster_source_manager
from app.models.poster_sources import (
    BulkReplacePosterRequest, BulkReplacePosterResponse, BulkItemResult,
    PosterSearchRequest, PosterOption, ReplacePosterRequest
)
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.services.bulk_poster_replacement", service="api")

class BulkPosterReplacementService:
    """Service for handling bulk poster replacement operations"""
    
    def __init__(self):
        self.storage_manager = StorageManager()
        self.semaphore = asyncio.Semaphore(3)  # Limit concurrent processing
        
    async def process_bulk_replacement(
        self, 
        request: BulkReplacePosterRequest,
        db: AsyncSession
    ) -> BulkReplacePosterResponse:
        """Process bulk poster replacement for multiple items"""
        start_time = time.time()
        
        if len(request.item_ids) != len(request.jellyfin_ids):
            raise ValueError("Item IDs and Jellyfin IDs must have the same length")
            
        logger.info(
            f"Starting bulk poster replacement for {len(request.item_ids)} items "
            f"with language preference: {request.language_preference}"
        )
        
        # Create tasks for concurrent processing
        tasks = []
        for item_id, jellyfin_id in zip(request.item_ids, request.jellyfin_ids):
            task = self._process_single_item(
                item_id, 
                jellyfin_id, 
                request.language_preference,
                request.random_selection
            )
            tasks.append(task)
            
        # Process all items concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processing_results = []
        successful_count = 0
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions
                item_result = BulkItemResult(
                    item_id=request.item_ids[i],
                    jellyfin_id=request.jellyfin_ids[i],
                    success=False,
                    message=f"Processing failed: {str(result)}",
                    error_details=str(result)
                )
                failed_count += 1
            else:
                item_result = result
                if item_result.success:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            processing_results.append(item_result)
            
        processing_time = time.time() - start_time
        
        # Generate summary message
        summary_message = (
            f"Bulk replacement completed: {successful_count} successful, "
            f"{failed_count} failed out of {len(request.item_ids)} items"
        )
        
        logger.info(
            f"Bulk replacement completed in {processing_time:.2f}s: "
            f"{successful_count} successful, {failed_count} failed"
        )
        
        return BulkReplacePosterResponse(
            success=successful_count > 0,
            message=summary_message,
            processed_count=len(request.item_ids),
            successful_replacements=successful_count,
            failed_replacements=failed_count,
            processing_results=processing_results,
            processing_time=processing_time
        )
        
    async def _process_single_item(
        self,
        item_id: str,
        jellyfin_id: str,
        language_preference: str,
        random_selection: bool
    ) -> BulkItemResult:
        """Process a single item for poster replacement"""
        
        async with self.semaphore:  # Limit concurrent processing
            try:
                # Get item details from Jellyfin
                jellyfin_service = get_jellyfin_service()
                item_details = await jellyfin_service.get_item_details(item_id)
                
                if not item_details:
                    return BulkItemResult(
                        item_id=item_id,
                        jellyfin_id=jellyfin_id,
                        success=False,
                        message="Item not found in Jellyfin",
                        error_details="Item not found"
                    )
                    
                # Extract search parameters
                title = item_details.get("Name", "")
                year = item_details.get("ProductionYear")
                item_type = item_details.get("Type", "").lower()
                
                if not title:
                    return BulkItemResult(
                        item_id=item_id,
                        jellyfin_id=jellyfin_id,
                        success=False,
                        message="Item title not found",
                        error_details="Missing title"
                    )
                    
                # Search for poster alternatives
                search_request = PosterSearchRequest(
                    item_id=item_id,
                    jellyfin_id=jellyfin_id,
                    title=title,
                    year=year,
                    item_type=item_type
                )
                
                poster_manager = await get_poster_source_manager()
                search_result = await poster_manager.search_posters(search_request)
                
                if not search_result.posters:
                    return BulkItemResult(
                        item_id=item_id,
                        jellyfin_id=jellyfin_id,
                        success=False,
                        message="No alternative posters found",
                        error_details="No posters available"
                    )
                    
                # Filter posters by language preference if specified
                filtered_posters = self._filter_posters_by_language(
                    search_result.posters, 
                    language_preference
                )
                
                if not filtered_posters:
                    # Fall back to all posters if no language matches
                    filtered_posters = search_result.posters
                    
                # Select a random poster
                selected_poster = random.choice(filtered_posters) if random_selection else filtered_posters[0]
                
                # Replace the poster
                replacement_result = await self._replace_poster(
                    item_id, 
                    jellyfin_id, 
                    selected_poster,
                    title
                )
                
                return replacement_result
                
            except Exception as e:
                logger.error(f"Error processing item {item_id}: {e}", exc_info=True)
                return BulkItemResult(
                    item_id=item_id,
                    jellyfin_id=jellyfin_id,
                    success=False,
                    message=f"Processing error: {str(e)}",
                    error_details=str(e)
                )
                
    def _filter_posters_by_language(
        self, 
        posters: List[PosterOption], 
        language_preference: str
    ) -> List[PosterOption]:
        """Filter posters by language preference"""
        
        if language_preference == "null":
            # For textless/no language, prioritize posters with null/None language
            textless_posters = [
                poster for poster in posters 
                if poster.language is None or poster.language == "null"
            ]
            if textless_posters:
                return textless_posters
            # If no textless posters, fall back to all posters
            return posters
            
        elif language_preference == "en":
            # For English, include both "en" and None (universal)
            return [
                poster for poster in posters 
                if poster.language in ["en", None]
            ]
        else:
            # For other languages, prefer exact match but fall back to universal
            preferred = [
                poster for poster in posters 
                if poster.language == language_preference
            ]
            if preferred:
                return preferred
                
            # Fall back to universal posters
            return [
                poster for poster in posters 
                if poster.language is None
            ]
            
    async def _replace_poster(
        self,
        item_id: str,
        jellyfin_id: str,
        selected_poster: PosterOption,
        title: str
    ) -> BulkItemResult:
        """Replace poster for a single item"""
        
        try:
            # Get services
            jellyfin_service = get_jellyfin_service()
            poster_manager = await get_poster_source_manager()
            
            # Download the selected poster
            poster_data = await poster_manager.download_poster(selected_poster)
            if not poster_data:
                return BulkItemResult(
                    item_id=item_id,
                    jellyfin_id=jellyfin_id,
                    success=False,
                    message=f"Failed to download poster from {selected_poster.source}",
                    error_details="Download failed"
                )
                
            # Cache current poster as original
            try:
                current_poster_data = await jellyfin_service.download_poster(jellyfin_id)
                if current_poster_data:
                    self.storage_manager.cache_original_poster(current_poster_data, jellyfin_id)
            except Exception as cache_error:
                logger.warning(f"Failed to cache current poster for {item_id}: {cache_error}")
                
            # Upload new poster to Jellyfin
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(poster_data)
                temp_poster_path = temp_file.name
                
            try:
                upload_success = await jellyfin_service.upload_poster_image(
                    jellyfin_id,
                    temp_poster_path
                )
                
                if not upload_success:
                    return BulkItemResult(
                        item_id=item_id,
                        jellyfin_id=jellyfin_id,
                        success=False,
                        message="Failed to upload new poster to Jellyfin",
                        error_details="Upload failed"
                    )
                    
                # Remove aphrodite-overlay tag
                tag_removal_success = False
                try:
                    tag_service = get_tag_management_service()
                    tag_result = await tag_service.remove_tag_from_items(
                        [jellyfin_id], 
                        "aphrodite-overlay"
                    )
                    tag_removal_success = tag_result.processed_count > 0
                except Exception as tag_error:
                    logger.warning(f"Failed to remove tag from {item_id}: {tag_error}")
                    
                # Generate new poster URL with cache-busting
                timestamp = int(time.time())
                new_poster_url = f"/api/v1/images/proxy/image/{jellyfin_id}/thumbnail?replaced={timestamp}"
                
                success_message = f"Replaced poster for '{title}' with {selected_poster.source} image"
                if tag_removal_success:
                    success_message += " and removed aphrodite-overlay tag"
                    
                return BulkItemResult(
                    item_id=item_id,
                    jellyfin_id=jellyfin_id,
                    success=True,
                    message=success_message,
                    new_poster_url=new_poster_url,
                    selected_poster=selected_poster
                )
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_poster_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error replacing poster for {item_id}: {e}", exc_info=True)
            return BulkItemResult(
                item_id=item_id,
                jellyfin_id=jellyfin_id,
                success=False,
                message=f"Replacement failed: {str(e)}",
                error_details=str(e)
            )

# Service instance
_bulk_poster_service: Optional[BulkPosterReplacementService] = None

async def get_bulk_poster_replacement_service() -> BulkPosterReplacementService:
    """Get the bulk poster replacement service instance"""
    global _bulk_poster_service
    if _bulk_poster_service is None:
        _bulk_poster_service = BulkPosterReplacementService()
    return _bulk_poster_service
