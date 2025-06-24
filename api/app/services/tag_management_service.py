"""
Tag Management Service

Handles adding/removing tags from Jellyfin media items.
"""

import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.jellyfin_service import get_jellyfin_service
from aphrodite_logging import get_logger


class BulkTagRequest(BaseModel):
    """Request model for bulk tag operations"""
    item_ids: List[str]
    tag_name: str = "aphrodite-overlay"


class BulkTagResponse(BaseModel):
    """Response model for bulk tag operations"""
    success: bool
    processed_count: int
    failed_items: List[str]
    errors: List[str]


class TagManagementService:
    """Service for managing tags on Jellyfin items"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.service.tag_management", service="tag_management")
        self.jellyfin_service = get_jellyfin_service()
        # Don't initialize these here - load from database when needed
        self.base_url = None
        self.api_key = None
        self.user_id = None
        self._jellyfin_config = None
    
    async def _get_jellyfin_config(self) -> Optional[Dict[str, Any]]:
        """Load Jellyfin configuration from database"""
        if self._jellyfin_config is not None:
            return self._jellyfin_config
        
        try:
            from app.core.database import async_session_factory
            from app.models.config import SystemConfigModel
            from sqlalchemy import select
            import yaml
            
            # Check if global session factory is available, otherwise create a temporary one
            session_factory = async_session_factory
            temporary_engine = None
            
            if session_factory is None:
                self.logger.warning("Global database session factory not available for tag service, creating temporary one")
                
                # Create temporary database engine like other services do
                from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
                from app.core.config import get_settings
                
                settings = get_settings()
                temporary_engine = create_async_engine(
                    settings.database_url,
                    echo=False,
                    pool_size=1,
                    max_overflow=0,
                    pool_pre_ping=True
                )
                
                session_factory = async_sessionmaker(
                    temporary_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            
            try:
                async with session_factory() as db:
                    # Load the settings.yaml configuration
                    stmt = select(SystemConfigModel).where(SystemConfigModel.key == "settings.yaml")
                    result = await db.execute(stmt)
                    config_model = result.scalar_one_or_none()
                    
                    if not config_model or not config_model.value:
                        self.logger.error("No settings.yaml configuration found in database")
                        return None
                    
                    settings_data = config_model.value
                    
                    # Parse YAML string if it's a string (like Jellyfin service)
                    if isinstance(settings_data, str):
                        try:
                            settings_data = yaml.safe_load(settings_data)
                            self.logger.debug("Parsed settings.yaml from string format for tag service")
                        except Exception as yaml_error:
                            self.logger.error(f"Failed to parse settings.yaml for tag service: {yaml_error}")
                            return None
                    
                    if not isinstance(settings_data, dict):
                        self.logger.error("Settings data is not a valid dictionary after parsing")
                        return None
                    
                    # Extract Jellyfin settings from the nested structure
                    api_keys = settings_data.get("api_keys", {})
                    jellyfin_configs = api_keys.get("Jellyfin", [])
                    
                    if not jellyfin_configs or len(jellyfin_configs) == 0:
                        self.logger.error("No Jellyfin configuration found in settings.yaml")
                        return None
                    
                    # Use the first Jellyfin configuration
                    jellyfin_config = jellyfin_configs[0]
                    
                    # Validate required fields
                    required_fields = ["url", "api_key", "user_id"]
                    missing_fields = [field for field in required_fields if field not in jellyfin_config]
                    
                    if missing_fields:
                        self.logger.error(f"Missing required Jellyfin config fields: {missing_fields}")
                        return None
                    
                    # Cache the config
                    self._jellyfin_config = jellyfin_config
                    
                    # Set instance variables
                    self.base_url = jellyfin_config["url"].rstrip("/")
                    self.api_key = jellyfin_config["api_key"]
                    self.user_id = jellyfin_config["user_id"]
                    
                    self.logger.info(f"Successfully loaded Jellyfin config for tag service: {self.base_url}, user: {self.user_id}")
                    return jellyfin_config
            finally:
                # Clean up temporary engine if created
                if temporary_engine is not None:
                    await temporary_engine.dispose()
                
        except Exception as e:
            self.logger.error(f"Error loading Jellyfin config from database: {e}", exc_info=True)
            # Clean up temporary engine if created
            if 'temporary_engine' in locals() and temporary_engine is not None:
                try:
                    await temporary_engine.dispose()
                except Exception:
                    pass  # Ignore cleanup errors
            return None
    
    async def add_tag_to_items(self, item_ids: List[str], tag_name: str = "aphrodite-overlay") -> BulkTagResponse:
        """Add a tag to multiple Jellyfin items"""
        # Ensure Jellyfin config is loaded
        if not await self._get_jellyfin_config():
            return BulkTagResponse(
                success=False,
                processed_count=0,
                failed_items=item_ids,
                errors=["Failed to load Jellyfin configuration from database"]
            )
        
        processed_count = 0
        failed_items = []
        errors = []
        
        self.logger.info(f"Adding tag '{tag_name}' to {len(item_ids)} items")
        
        for item_id in item_ids:
            try:
                success = await self._add_tag_to_item(item_id, tag_name)
                if success:
                    processed_count += 1
                    self.logger.debug(f"Successfully added tag to item {item_id}")
                else:
                    failed_items.append(item_id)
                    errors.append(f"Failed to add tag to item {item_id}")
                    self.logger.warning(f"Failed to add tag to item {item_id}")
            except Exception as e:
                failed_items.append(item_id)
                error_msg = f"Error adding tag to item {item_id}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        success = len(failed_items) == 0
        self.logger.info(f"Tag addition complete: {processed_count}/{len(item_ids)} successful")
        
        return BulkTagResponse(
            success=success,
            processed_count=processed_count,
            failed_items=failed_items,
            errors=errors
        )
    
    async def remove_tag_from_items(self, item_ids: List[str], tag_name: str = "aphrodite-overlay") -> BulkTagResponse:
        """Remove a tag from multiple Jellyfin items"""
        # Ensure Jellyfin config is loaded
        if not await self._get_jellyfin_config():
            return BulkTagResponse(
                success=False,
                processed_count=0,
                failed_items=item_ids,
                errors=["Failed to load Jellyfin configuration from database"]
            )
        
        processed_count = 0
        failed_items = []
        errors = []
        
        self.logger.info(f"Removing tag '{tag_name}' from {len(item_ids)} items")
        
        for item_id in item_ids:
            try:
                success = await self._remove_tag_from_item(item_id, tag_name)
                if success:
                    processed_count += 1
                    self.logger.debug(f"Successfully removed tag from item {item_id}")
                else:
                    failed_items.append(item_id)
                    errors.append(f"Failed to remove tag from item {item_id}")
                    self.logger.warning(f"Failed to remove tag from item {item_id}")
            except Exception as e:
                failed_items.append(item_id)
                error_msg = f"Error removing tag from item {item_id}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        success = len(failed_items) == 0
        self.logger.info(f"Tag removal complete: {processed_count}/{len(item_ids)} successful")
        
        return BulkTagResponse(
            success=success,
            processed_count=processed_count,
            failed_items=failed_items,
            errors=errors
        )
    
    async def _add_tag_to_item(self, item_id: str, tag_name: str) -> bool:
        """Add a tag to a single Jellyfin item"""
        try:
            # First get current item data
            current_tags = await self._get_item_tags(item_id)
            if current_tags is None:
                return False
            
            # Check if tag already exists
            if tag_name in current_tags:
                self.logger.debug(f"Tag '{tag_name}' already exists on item {item_id}")
                return True
            
            # Add the new tag
            updated_tags = current_tags + [tag_name]
            
            # Update the item
            return await self._update_item_tags(item_id, updated_tags)
            
        except Exception as e:
            self.logger.error(f"Error adding tag to item {item_id}: {e}")
            return False
    
    async def _remove_tag_from_item(self, item_id: str, tag_name: str) -> bool:
        """Remove a tag from a single Jellyfin item"""
        try:
            # First get current item data
            current_tags = await self._get_item_tags(item_id)
            if current_tags is None:
                return False
            
            # Check if tag exists
            if tag_name not in current_tags:
                self.logger.debug(f"Tag '{tag_name}' does not exist on item {item_id}")
                return True
            
            # Remove the tag
            updated_tags = [tag for tag in current_tags if tag != tag_name]
            
            # Update the item
            return await self._update_item_tags(item_id, updated_tags)
            
        except Exception as e:
            self.logger.error(f"Error removing tag from item {item_id}: {e}")
            return False
    
    async def _get_item_tags(self, item_id: str) -> Optional[List[str]]:
        """Get current tags for an item (following v1 pattern)"""
        try:
            # Use the user-specific endpoint like v1 does
            url = urljoin(self.base_url, f"/Users/{self.user_id}/Items/{item_id}")
            session = await self.jellyfin_service._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    tags = data.get("Tags", []) or []  # Handle None case
                    self.logger.debug(f"Retrieved {len(tags)} tags for item {item_id}: {tags}")
                    return tags
                else:
                    response_text = await response.text()
                    self.logger.error(f"Failed to get item {item_id}: HTTP {response.status} - {response_text}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting tags for item {item_id}: {e}")
            return None
    
    async def _update_item_tags(self, item_id: str, tags: List[str]) -> bool:
        """Update tags for an item using Jellyfin API (following v1 pattern)"""
        try:
            # First get the full item data using user-specific endpoint
            get_url = urljoin(self.base_url, f"/Users/{self.user_id}/Items/{item_id}")
            session = await self.jellyfin_service._get_session()
            
            async with session.get(get_url) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to get item data for {item_id}: HTTP {response.status}")
                    return False
                
                item_data = await response.json()
            
            # Create a comprehensive update payload following v1 pattern
            update_payload = {
                "Id": item_id,
                "Name": item_data.get("Name"),
                "Tags": tags,
                "LockedFields": item_data.get("LockedFields", []),
                "ServerId": item_data.get("ServerId"),
                "Type": item_data.get("Type"),
                "UserData": item_data.get("UserData", {})
            }
            
            # Add essential metadata fields that Jellyfin expects
            essential_fields = [
                "Overview", "ProductionYear", "CommunityRating", "OfficialRating",
                "Genres", "Studios", "People", "ProviderIds", "PremiereDate",
                "EndDate", "RunTimeTicks", "DisplayOrder", "SortName",
                "ForcedSortName", "OriginalTitle", "DateCreated",
                "ExternalUrls", "MediaType", "Width", "Height"
            ]
            
            for field in essential_fields:
                if field in item_data and item_data[field] is not None:
                    update_payload[field] = item_data[field]
            
            # Use the standard update endpoint
            update_url = urljoin(self.base_url, f"/Items/{item_id}")
            
            async with session.post(update_url, json=update_payload) as response:
                if response.status in [200, 204]:
                    self.logger.debug(f"Successfully updated tags for item {item_id} to: {tags}")
                    return True
                else:
                    response_text = await response.text()
                    self.logger.error(f"Failed to update item {item_id}: HTTP {response.status} - {response_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error updating tags for item {item_id}: {e}")
            return False
    
    async def _update_item_tags_alternative(self, item_id: str, tags: List[str], item_data: Dict[str, Any]) -> bool:
        """Alternative method to update item tags using library management endpoint"""
        try:
            session = await self.jellyfin_service._get_session()
            
            # Try using the library management endpoint
            update_url = urljoin(self.base_url, f"/Library/Media/Updated")
            
            # Prepare minimal update payload
            update_payload = {
                "Id": item_id,
                "Tags": tags,
                "Name": item_data.get("Name", ""),
                "Overview": item_data.get("Overview", ""),
                "Genres": item_data.get("Genres", [])
            }
            
            async with session.post(update_url, json=update_payload) as response:
                if response.status in [200, 204]:
                    self.logger.debug(f"Successfully updated tags using alternative method for item {item_id}")
                    return True
                else:
                    response_text = await response.text()
                    self.logger.error(f"Alternative update failed for item {item_id}: HTTP {response.status} - {response_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error in alternative update for item {item_id}: {e}")
            return False
    
    async def get_item_tags(self, item_id: str) -> Optional[List[str]]:
        """Public method to get tags for an item"""
        # Ensure Jellyfin config is loaded
        if not await self._get_jellyfin_config():
            self.logger.error("Failed to load Jellyfin configuration")
            return None
        
        return await self._get_item_tags(item_id)


# Global service instance
_tag_management_service: Optional[TagManagementService] = None

def get_tag_management_service() -> TagManagementService:
    """Get global tag management service instance"""
    global _tag_management_service
    if _tag_management_service is None:
        _tag_management_service = TagManagementService()
    return _tag_management_service
