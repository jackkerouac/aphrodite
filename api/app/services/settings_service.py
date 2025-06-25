"""
Settings Service

Service to load and manage system settings from the PostgreSQL database.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.config import SystemConfigModel
from aphrodite_logging import get_logger

class SettingsService:
    """Service for managing system settings from database"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.settings", service="settings")
        self._cache = {}  # Simple in-memory cache
    
    async def get_settings(
        self, 
        key: str, 
        db: AsyncSession,
        use_cache: bool = True,
        force_reload: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Load settings from system_config table for the specified key
        
        Args:
            key: Settings key (e.g., 'settings.yaml', 'badge_settings_review.yml')
            db: Database session
            use_cache: Whether to use cached settings
            force_reload: Whether to force reload from database (ignores cache)
            
        Returns:
            Dictionary of settings or None if not found
        """
        try:
            # Check cache first (unless force_reload is True)
            cache_key = f"settings_{key}"
            if use_cache and not force_reload and cache_key in self._cache:
                self.logger.debug(f"Using cached settings for {key}")
                return self._cache[cache_key]
            
            # Force reload: clear cache for this key
            if force_reload and cache_key in self._cache:
                del self._cache[cache_key]
                self.logger.debug(f"Cleared cache for {key} due to force_reload")
            
            self.logger.debug(f"Loading settings from database: {key}")
            
            # Query database for settings
            stmt = select(SystemConfigModel).where(SystemConfigModel.key == key)
            result = await db.execute(stmt)
            config_model = result.scalar_one_or_none()
            
            if not config_model or not config_model.value:
                self.logger.warning(f"No settings found for key: {key}")
                return None
            
            settings = config_model.value
            
            # Cache and return settings
            if use_cache:
                self._cache[cache_key] = settings
            
            self.logger.info(f"Successfully loaded settings for {key}")
            return settings
            
        except Exception as e:
            self.logger.error(f"Error loading settings for {key}: {e}", exc_info=True)
            return None
    
    async def get_api_keys(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get API keys from settings.yaml"""
        settings = await self.get_settings("settings.yaml", db, force_reload=force_reload)
        if settings:
            return settings.get("api_keys", {})
        return None
    
    async def get_api_keys_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get API keys using internal session - robust worker-compatible version"""
        try:
            # Try to use global session factory first
            from app.core.database import async_session_factory
            
            if async_session_factory is not None:
                async with async_session_factory() as db:
                    return await self.get_api_keys(db, force_reload=force_reload)
            
            # Fallback: create our own database connection for workers
            self.logger.warning("Global session factory not available, creating direct connection")
            
            from app.core.config import get_settings
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
            
            settings = get_settings()
            database_url = settings.get_database_url()
            
            # Create temporary engine and session
            temp_engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True
            )
            
            temp_session_factory = async_sessionmaker(
                temp_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            try:
                async with temp_session_factory() as db:
                    return await self.get_api_keys(db, force_reload=force_reload)
            finally:
                await temp_engine.dispose()
                
        except Exception as e:
            self.logger.error(f"Error getting API keys standalone: {e}", exc_info=True)
            return None
    
    async def get_review_settings(self, db: AsyncSession, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get review badge settings"""
        return await self.get_settings("badge_settings_review.yml", db, force_reload=force_reload)
    
    async def get_review_settings_standalone(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get review badge settings using internal session - robust worker-compatible version"""
        try:
            # Try to use global session factory first
            from app.core.database import async_session_factory
            
            if async_session_factory is not None:
                async with async_session_factory() as db:
                    return await self.get_review_settings(db, force_reload=force_reload)
            
            # Fallback: create our own database connection for workers
            self.logger.warning("Global session factory not available, creating direct connection for review settings")
            
            from app.core.config import get_settings
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
            
            settings = get_settings()
            database_url = settings.get_database_url()
            
            # Create temporary engine and session
            temp_engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True
            )
            
            temp_session_factory = async_sessionmaker(
                temp_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            try:
                async with temp_session_factory() as db:
                    return await self.get_review_settings(db, force_reload=force_reload)
            finally:
                await temp_engine.dispose()
                
        except Exception as e:
            self.logger.error(f"Error getting review settings standalone: {e}", exc_info=True)
            return None
    
    def clear_cache(self, key: Optional[str] = None):
        """Clear the settings cache"""
        if key:
            cache_key = f"settings_{key}"
            if cache_key in self._cache:
                del self._cache[cache_key]
                self.logger.info(f"Cleared cache for {key}")
        else:
            self._cache.clear()
            self.logger.info("Settings cache cleared")
    
    def invalidate_badge_cache(self):
        """Invalidate all badge-related cache entries"""
        badge_keys = [key for key in self._cache.keys() if 'badge_settings' in key]
        for key in badge_keys:
            del self._cache[key]
        self.logger.info(f"Invalidated {len(badge_keys)} badge cache entries")

# Global instance for easy access
settings_service = SettingsService()
