"""
Database Service for Badge Settings

Service to load and manage badge configurations from the PostgreSQL database.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.config import SystemConfigModel
from app.core.database import async_session_factory
from aphrodite_logging import get_logger

class BadgeSettingsService:
    """Service for managing badge settings from database"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.settings", service="badge")
        self._cache = {}  # Simple in-memory cache
    
    async def get_badge_settings(
        self, 
        badge_type: str, 
        db: AsyncSession,
        use_cache: bool = True,
        force_reload: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Load badge settings from system_config table for the specified badge type
        
        Args:
            badge_type: Type of badge (audio, resolution, review, awards)
            db: Database session
            use_cache: Whether to use cached settings
            force_reload: Whether to force reload from database (ignores cache)
            
        Returns:
            Dictionary of badge settings or None if not found
        """
        try:
            # Check cache first (unless force_reload is True)
            cache_key = f"badge_settings_{badge_type}"
            if use_cache and not force_reload and cache_key in self._cache:
                self.logger.debug(f"Using cached settings for {badge_type}")
                return self._cache[cache_key]
            
            # Force reload: clear cache for this badge type
            if force_reload and cache_key in self._cache:
                del self._cache[cache_key]
                self.logger.debug(f"Cleared cache for {badge_type} due to force_reload")
            
            self.logger.debug(f"Loading {badge_type} badge settings from database (cache: {use_cache}, force_reload: {force_reload})")
            
            # Try different key patterns for badge settings
            key_patterns = [
                f"badge_settings_{badge_type}.yml",  # Pattern like "badge_settings_audio.yml"
                f"badge_settings_{badge_type}",      # Pattern like "badge_settings_audio"
                f"{badge_type}_badge_settings",      # Pattern like "audio_badge_settings"
                f"{badge_type}_settings"              # Pattern like "audio_settings"
            ]
            
            settings = None
            found_key = None
            
            # Try each key pattern
            for key_pattern in key_patterns:
                self.logger.debug(f"Searching for {badge_type} settings with key: {key_pattern}")
                stmt = select(SystemConfigModel).where(SystemConfigModel.key == key_pattern)
                result = await db.execute(stmt)
                config_model = result.scalar_one_or_none()
                
                if config_model and config_model.value:
                    settings = config_model.value
                    found_key = key_pattern
                    self.logger.info(f"Found {badge_type} settings with key: {found_key}")
                    break
            
            if not settings:
                self.logger.warning(f"No {badge_type} badge configuration found in system_config with any key pattern")
                return None
            
            # Cache and return settings
            if use_cache:
                self._cache[cache_key] = settings
            
            self.logger.info(f"Successfully loaded {badge_type} badge settings from system_config (key: {found_key})")
            self.logger.debug(f"{badge_type} settings keys: {list(settings.keys())}")
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error loading {badge_type} badge settings: {e}", exc_info=True)
            return None
    
    async def get_audio_settings(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get audio badge settings"""
        return await self.get_badge_settings("audio", db, force_reload=force_reload)
    
    async def get_resolution_settings(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get resolution badge settings"""
        return await self.get_badge_settings("resolution", db, force_reload=force_reload)
    
    async def get_review_settings(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get review badge settings"""
        return await self.get_badge_settings("review", db, force_reload=force_reload)
    
    async def get_awards_settings(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get awards badge settings"""
        return await self.get_badge_settings("awards", db, force_reload=force_reload)
    
    async def get_audio_settings_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get audio badge settings using internal session"""
        try:
            async with async_session_factory() as db:
                return await self.get_audio_settings(db, force_reload=force_reload)
        except Exception as e:
            self.logger.error(f"Error getting audio settings standalone: {e}", exc_info=True)
            return None
    
    async def get_resolution_settings_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get resolution badge settings using internal session"""
        try:
            async with async_session_factory() as db:
                return await self.get_resolution_settings(db, force_reload=force_reload)
        except Exception as e:
            self.logger.error(f"Error getting resolution settings standalone: {e}", exc_info=True)
            return None
    
    async def get_review_settings_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get review badge settings using internal session"""
        try:
            async with async_session_factory() as db:
                return await self.get_review_settings(db, force_reload=force_reload)
        except Exception as e:
            self.logger.error(f"Error getting review settings standalone: {e}", exc_info=True)
            return None
    
    async def get_awards_settings_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get awards badge settings using internal session"""
        try:
            async with async_session_factory() as db:
                return await self.get_awards_settings(db, force_reload=force_reload)
        except Exception as e:
            self.logger.error(f"Error getting awards settings standalone: {e}", exc_info=True)
            return None
    
    def clear_cache(self):
        """Clear the settings cache"""
        self._cache.clear()
        self.logger.info("Badge settings cache cleared")
    
    def clear_badge_cache(self, badge_type: str):
        """Clear cache for a specific badge type"""
        cache_key = f"badge_settings_{badge_type}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            self.logger.info(f"Cleared cache for {badge_type} badge settings")
    
    async def validate_settings(self, settings: Dict[str, Any], badge_type: str) -> bool:
        """
        Validate badge settings structure
        
        Args:
            settings: Settings dictionary to validate
            badge_type: Type of badge being validated
            
        Returns:
            True if settings are valid, False otherwise
        """
        try:
            required_sections = {
                "audio": ["General", "Text", "Background", "Border", "ImageBadges"],
                "resolution": ["General", "Text", "Background", "Border", "ImageBadges"],
                "review": ["General", "Text", "Background", "Border"],
                "awards": ["General", "Background", "Border", "ImageBadges"]
            }
            
            if badge_type not in required_sections:
                self.logger.error(f"Unknown badge type: {badge_type}")
                return False
            
            missing_sections = []
            for section in required_sections[badge_type]:
                if section not in settings:
                    missing_sections.append(section)
            
            if missing_sections:
                self.logger.error(f"Missing required sections in {badge_type} settings: {missing_sections}")
                return False
            
            # Validate General section has required fields
            general = settings.get("General", {})
            required_general = ["general_badge_size", "general_text_padding"]
            missing_general = [field for field in required_general if field not in general]
            
            if missing_general:
                self.logger.error(f"Missing required General fields in {badge_type} settings: {missing_general}")
                return False
            
            self.logger.debug(f"{badge_type} settings validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating {badge_type} settings: {e}", exc_info=True)
            return False

# Global instance for easy access
badge_settings_service = BadgeSettingsService()
