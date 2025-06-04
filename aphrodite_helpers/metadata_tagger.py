#!/usr/bin/env python3
# aphrodite_helpers/metadata_tagger.py - Add Aphrodite metadata tags to processed items

import requests
import logging
import time
from typing import Optional, List

logger = logging.getLogger(__name__)

def get_tagging_settings():
    """Get metadata tagging settings from settings.yaml"""
    try:
        from .check_jellyfin_connection import load_settings
        settings = load_settings()
        if settings and 'metadata_tagging' in settings:
            return settings['metadata_tagging']
        else:
            # Return default settings if not found
            return {
                'enabled': True,
                'tag_name': 'aphrodite-overlay', 
                'tag_on_success_only': True
            }
    except Exception as e:
        logger.warning(f"Could not load tagging settings, using defaults: {e}")
        return {
            'enabled': True,
            'tag_name': 'aphrodite-overlay',
            'tag_on_success_only': True
        }

class MetadataTagger:
    """
    Handles adding metadata tags to Jellyfin items to track Aphrodite processing.
    """
    
    def __init__(self, jellyfin_url: str, api_key: str, user_id: str):
        self.jellyfin_url = jellyfin_url.rstrip("/")
        self.api_key = api_key
        self.user_id = user_id
        self.headers = {"X-Emby-Token": api_key, "Content-Type": "application/json"}
        
    def get_item_metadata(self, item_id: str) -> Optional[dict]:
        """
        Get the current metadata for a Jellyfin item.
        """
        try:
            url = f"{self.jellyfin_url}/Users/{self.user_id}/Items/{item_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get metadata for item {item_id}: {e}")
            return None
    
    def add_aphrodite_tag(self, item_id: str, tag: str = "aphrodite-overlay") -> bool:
        """
        Add an Aphrodite tag to a Jellyfin item to mark it as processed.
        
        Args:
            item_id: Jellyfin item ID
            tag: The tag to add (default: "aphrodite-overlay")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, get the current item metadata
            item_data = self.get_item_metadata(item_id)
            if not item_data:
                logger.error(f"Could not retrieve item data for {item_id}")
                return False
            
            # Get current tags or initialize empty list
            current_tags = item_data.get("Tags", []) or []
            
            # Check if tag already exists
            if tag in current_tags:
                logger.info(f"Tag '{tag}' already exists on item {item_id}")
                return True
            
            # Add the new tag
            updated_tags = current_tags + [tag]
            
            # Create a comprehensive update payload to avoid API issues
            update_payload = {
                "Id": item_id,
                "Name": item_data.get("Name"),
                "Tags": updated_tags,
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
            
            # Update the item
            url = f"{self.jellyfin_url}/Items/{item_id}"
            response = requests.post(url, headers=self.headers, json=update_payload, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Successfully added tag '{tag}' to item {item_id}")
                return True
            else:
                logger.error(f"Failed to update item {item_id}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error while updating item {item_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while updating item {item_id}: {e}")
            return False
    
    def check_aphrodite_tag(self, item_id: str, tag: str = "aphrodite-overlay") -> bool:
        """
        Check if an item already has the Aphrodite tag.
        
        Args:
            item_id: Jellyfin item ID
            tag: The tag to check for (default: "aphrodite-overlay")
            
        Returns:
            True if tag exists, False otherwise
        """
        item_data = self.get_item_metadata(item_id)
        if not item_data:
            return False
        
        current_tags = item_data.get("Tags", []) or []
        return tag in current_tags
    
    def get_item_tags(self, item_id: str) -> List[str]:
        """
        Get all tags for a Jellyfin item.
        
        Args:
            item_id: Jellyfin item ID
            
        Returns:
            List of tags for the item
        """
        item_data = self.get_item_metadata(item_id)
        if not item_data:
            return []
        
        return item_data.get("Tags", []) or []
    
    def remove_aphrodite_tag(self, item_id: str, tag: str = "aphrodite-overlay") -> bool:
        """
        Remove an Aphrodite tag from a Jellyfin item.
        
        Args:
            item_id: Jellyfin item ID
            tag: The tag to remove (default: "aphrodite-overlay")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current item metadata
            item_data = self.get_item_metadata(item_id)
            if not item_data:
                logger.error(f"Could not retrieve item data for {item_id}")
                return False
            
            # Get current tags
            current_tags = item_data.get("Tags", []) or []
            
            # Check if tag exists
            if tag not in current_tags:
                logger.info(f"Tag '{tag}' not found on item {item_id}")
                return True
            
            # Remove the tag
            updated_tags = [t for t in current_tags if t != tag]
            
            # Create a comprehensive update payload to avoid API issues
            update_payload = {
                "Id": item_id,
                "Name": item_data.get("Name"),
                "Tags": updated_tags,
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
            
            # Update the item
            url = f"{self.jellyfin_url}/Items/{item_id}"
            response = requests.post(url, headers=self.headers, json=update_payload, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Successfully removed tag '{tag}' from item {item_id}")
                return True
            else:
                logger.error(f"Failed to update item {item_id}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error while updating item {item_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while updating item {item_id}: {e}")
            return False

    def get_library_items_without_tag(self, library_id: str, tag: str = "aphrodite-overlay") -> List[dict]:
        """
        Get all items in a library that don't have the specified tag.
        
        Args:
            library_id: Jellyfin library ID
            tag: The tag to check for (default: "aphrodite-overlay")
            
        Returns:
            List of items without the tag
        """
        from .check_jellyfin_connection import get_library_items
        
        all_items = get_library_items(self.jellyfin_url, self.api_key, self.user_id, library_id)
        if not all_items:
            return []
        
        untagged_items = []
        for item in all_items:
            item_id = item.get("Id")
            if item_id and not self.check_aphrodite_tag(item_id, tag):
                untagged_items.append(item)
        
        return untagged_items


# Convenience functions for easy integration
def add_aphrodite_tag(jellyfin_url: str, api_key: str, user_id: str, item_id: str, tag: str = None) -> bool:
    """
    Convenience function to add an Aphrodite tag to an item.
    If tag is None, uses the tag from settings.
    """
    if tag is None:
        tagging_settings = get_tagging_settings()
        tag = tagging_settings.get('tag_name', 'aphrodite-overlay')
        
        # Check if tagging is enabled
        if not tagging_settings.get('enabled', True):
            logger.info(f"Metadata tagging is disabled in settings")
            return True  # Return True to not fail processing
    
    tagger = MetadataTagger(jellyfin_url, api_key, user_id)
    return tagger.add_aphrodite_tag(item_id, tag)

def check_aphrodite_tag(jellyfin_url: str, api_key: str, user_id: str, item_id: str, tag: str = None) -> bool:
    """
    Convenience function to check if an item has an Aphrodite tag.
    If tag is None, uses the tag from settings.
    """
    if tag is None:
        tagging_settings = get_tagging_settings()
        tag = tagging_settings.get('tag_name', 'aphrodite-overlay')
    
    tagger = MetadataTagger(jellyfin_url, api_key, user_id)
    return tagger.check_aphrodite_tag(item_id, tag)
