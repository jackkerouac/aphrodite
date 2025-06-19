"""
Media Management Service

Handles media item CRUD operations and poster management.
"""

import os
import aiofiles
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.sql import func as sql_func
from pathlib import Path
import hashlib
from datetime import datetime

from app.core.database import get_db_session
from app.models import MediaItemModel
from app.services.jellyfin_service import get_jellyfin_service
from app.core.config import get_settings
from aphrodite_logging import get_logger
from shared.types import MediaItem, MediaType, generate_id


class MediaService:
    """Service for managing media items"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("aphrodite.service.media", service="media")
        self.jellyfin = get_jellyfin_service()
        
        # Ensure directories exist
        self.poster_cache_dir = Path(self.settings.poster_cache_dir)
        self.poster_cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def scan_jellyfin_library(self, db: AsyncSession) -> Tuple[int, int, List[str]]:
        """
        Scan Jellyfin library and update database
        Returns: (total_found, new_items, errors)
        """
        self.logger.info("Starting Jellyfin library scan")
        total_found = 0
        new_items = 0
        errors = []
        
        try:
            # Test connection first
            connected, message = await self.jellyfin.test_connection()
            if not connected:
                error_msg = f"Jellyfin connection failed: {message}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return 0, 0, errors
            
            # Get all libraries
            libraries = await self.jellyfin.get_libraries()
            if not libraries:
                error_msg = "No libraries found in Jellyfin"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                return 0, 0, errors
            
            # Process each library
            for library in libraries:
                library_name = library.get("Name", "Unknown")
                library_id = library.get("ItemId")
                
                if not library_id:
                    continue
                
                self.logger.info(f"Scanning library: {library_name}")
                
                # Get items from this library
                items = await self.jellyfin.get_library_items(library_id)
                total_found += len(items)
                
                # Process each item
                for item in items:
                    try:
                        jellyfin_id = item.get("Id")
                        if not jellyfin_id:
                            continue
                        
                        # Check if item already exists
                        existing = await self._get_media_by_jellyfin_id(db, jellyfin_id)
                        if existing:
                            continue
                        
                        # Parse and create new media item
                        parsed_item = self.jellyfin.parse_jellyfin_item(item)
                        media_item = await self._create_media_item(db, parsed_item)
                        
                        if media_item:
                            new_items += 1
                            self.logger.debug(f"Created media item: {media_item.title}")
                        
                    except Exception as e:
                        error_msg = f"Error processing item {item.get('Name', 'Unknown')}: {e}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        continue
            
            await db.commit()
            self.logger.info(f"Library scan complete: {total_found} found, {new_items} new")
            
        except Exception as e:
            await db.rollback()
            error_msg = f"Library scan failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        return total_found, new_items, errors
    
    async def _get_media_by_jellyfin_id(self, db: AsyncSession, jellyfin_id: str) -> Optional[MediaItemModel]:
        """Get media item by Jellyfin ID"""
        result = await db.execute(
            select(MediaItemModel).where(MediaItemModel.jellyfin_id == jellyfin_id)
        )
        return result.scalar_one_or_none()
    
    async def _create_media_item(self, db: AsyncSession, data: Dict[str, Any]) -> Optional[MediaItemModel]:
        """Create new media item in database"""
        try:
            media_item = MediaItemModel(
                id=data["id"],
                title=data["title"],
                media_type=data["media_type"],
                year=data.get("year"),
                jellyfin_id=data["jellyfin_id"],
                tmdb_id=data.get("tmdb_id"),
                imdb_id=data.get("imdb_id"),
                overview=data.get("overview"),
                genres=data.get("genres", []),
                runtime=data.get("runtime"),
                community_rating=data.get("community_rating"),
                official_rating=data.get("official_rating"),
                premiere_date=data.get("premiere_date"),
                series_name=data.get("series_name"),
                season_number=data.get("season_number"),
                episode_number=data.get("episode_number")
            )
            
            db.add(media_item)
            await db.flush()  # Get the ID without committing
            return media_item
            
        except Exception as e:
            self.logger.error(f"Error creating media item: {e}")
            return None
    
    async def get_media_items(
        self,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        media_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[MediaItem], int]:
        """Get paginated list of media items"""
        try:
            # Build query
            query = select(MediaItemModel)
            count_query = select(func.count(MediaItemModel.id))
            
            # Add filters
            filters = []
            if media_type:
                filters.append(MediaItemModel.media_type == media_type)
            if search:
                search_term = f"%{search}%"
                filters.append(
                    or_(
                        MediaItemModel.title.ilike(search_term),
                        MediaItemModel.overview.ilike(search_term),
                        MediaItemModel.series_name.ilike(search_term)
                    )
                )
            
            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Add pagination and ordering
            offset = (page - 1) * per_page
            query = query.order_by(MediaItemModel.title).offset(offset).limit(per_page)
            
            # Execute query
            result = await db.execute(query)
            media_models = result.scalars().all()
            
            # Convert to Pydantic models
            media_items = [self._model_to_pydantic(model) for model in media_models]
            
            self.logger.debug(f"Retrieved {len(media_items)} media items (page {page})")
            return media_items, total
            
        except Exception as e:
            self.logger.error(f"Error getting media items: {e}")
            return [], 0
    
    async def get_media_by_id(self, db: AsyncSession, media_id: str) -> Optional[MediaItem]:
        """Get media item by ID"""
        try:
            result = await db.execute(
                select(MediaItemModel).where(MediaItemModel.id == media_id)
            )
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_pydantic(model)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting media item {media_id}: {e}")
            return None
    
    def _model_to_pydantic(self, model: MediaItemModel) -> MediaItem:
        """Convert SQLAlchemy model to Pydantic model"""
        return MediaItem(
            id=model.id,
            title=model.title,
            media_type=MediaType(model.media_type),
            year=model.year,
            poster_url=model.poster_url,
            jellyfin_id=model.jellyfin_id,
            tmdb_id=model.tmdb_id,
            imdb_id=model.imdb_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def download_and_cache_poster(self, media_id: str, jellyfin_id: str) -> Optional[str]:
        """Download poster from Jellyfin and cache locally"""
        try:
            # Download poster data
            poster_data = await self.jellyfin.download_poster(jellyfin_id)
            if not poster_data:
                self.logger.warning(f"No poster data for media {media_id}")
                return None
            
            # Generate cache filename
            poster_hash = hashlib.md5(poster_data).hexdigest()
            poster_filename = f"{media_id}_{poster_hash}.jpg"
            poster_path = self.poster_cache_dir / poster_filename
            
            # Save to cache
            async with aiofiles.open(poster_path, 'wb') as f:
                await f.write(poster_data)
            
            # Return relative URL
            poster_url = f"/cache/posters/{poster_filename}"
            self.logger.info(f"Cached poster for media {media_id}: {poster_url}")
            return poster_url
            
        except Exception as e:
            self.logger.error(f"Error caching poster for media {media_id}: {e}")
            return None
    
    async def update_poster_url(self, db: AsyncSession, media_id: str, poster_url: str):
        """Update poster URL for media item"""
        try:
            result = await db.execute(
                select(MediaItemModel).where(MediaItemModel.id == media_id)
            )
            media_item = result.scalar_one_or_none()
            
            if media_item:
                media_item.poster_url = poster_url
                media_item.updated_at = datetime.utcnow()
                await db.commit()
                self.logger.debug(f"Updated poster URL for media {media_id}")
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error updating poster URL for media {media_id}: {e}")


# Global service instance
_media_service: Optional[MediaService] = None

def get_media_service() -> MediaService:
    """Get global Media service instance"""
    global _media_service
    if _media_service is None:
        _media_service = MediaService()
    return _media_service
