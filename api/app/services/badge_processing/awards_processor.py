"""
Awards Badge Processor

Handles awards badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from app.core.database import async_session_factory


class AwardsBadgeProcessor(BaseBadgeProcessor):
    """Awards badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("awards")
        self.logger = get_logger("aphrodite.badge.awards", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with awards badge"""
        try:
            self.logger.info(f"🏆 Starting awards badge processing for: {poster_path}")
            
            # Load awards badge settings
            settings = await self._load_settings(db_session)
            if not settings:
                self.logger.warning("⚠️ Failed to load awards badge settings - skipping awards badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.debug(f"✅ Loaded awards settings successfully")
            
            # Get awards data
            if jellyfin_id:
                self.logger.debug(f"🔍 Checking for real awards data for jellyfin_id: {jellyfin_id}")
                awards_data = await self._get_real_awards_from_jellyfin(jellyfin_id, settings)
            elif use_demo_data:
                self.logger.debug("🎭 Using demo data for awards")
                awards_data = self._get_demo_awards(poster_path)
            else:
                self.logger.debug("❌ No jellyfin_id provided and demo data disabled")
                awards_data = None
            
            self.logger.info(f"🏆 Awards detection result: {awards_data}")
            
            if not awards_data:
                self.logger.info("ℹ️ No awards detected, skipping awards badge - continuing processing chain")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Apply awards badge
            self.logger.info(f"🎨 Applying {awards_data} awards badge to poster")
            result_path = await self._apply_awards_badge_with_storage_manager(
                poster_path, awards_data, settings, output_path
            )
            
            if result_path and result_path != poster_path:
                self.logger.info(f"✅ Successfully applied {awards_data} awards badge: {result_path}")
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["awards"],
                    success=True
                )
            else:
                self.logger.warning("⚠️ Awards badge application failed - continuing without awards")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
                
        except Exception as e:
            self.logger.error(f"💥 ERROR in awards badge processing: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                output_path=poster_path,
                applied_badges=[],
                success=True
            )
    
    async def _apply_awards_badge_with_storage_manager(
        self,
        poster_path: str,
        awards_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply awards badge using storage manager for proper path management"""
        try:
            self.logger.debug(f"🔧 Starting awards badge application for: {awards_data}")
            
            # Import dependencies with error handling
            try:
                from PIL import Image
                self.logger.debug("✅ PIL imported successfully")
            except ImportError as e:
                self.logger.error(f"❌ Failed to import PIL: {e}")
                return poster_path
            
            try:
                from app.services.poster_management import StorageManager
                self.logger.debug("✅ StorageManager imported successfully")
            except ImportError as e:
                self.logger.error(f"❌ Failed to import StorageManager: {e}")
                return poster_path
            
            storage_manager = StorageManager()
            
            # Determine proper output path using storage manager
            if not output_path:
                try:
                    if "preview" in poster_path or "static" in poster_path:
                        output_path = storage_manager.create_chained_preview_path(poster_path, "awards")
                        self.logger.debug(f"📁 Created chained preview path: {output_path}")
                    else:
                        output_path = storage_manager.create_preview_output_path(poster_path)
                        self.logger.debug(f"📁 Created new preview path: {output_path}")
                except Exception as e:
                    self.logger.error(f"❌ Error creating output path: {e}")
                    return poster_path
            else:
                self.logger.debug(f"📁 Using provided output path: {output_path}")
            
            # Try to load awards image
            api_static_dir = os.environ.get('APHRODITE_API_DIR', '/app/api')
            color_scheme = settings.get("Awards", {}).get("color_scheme", "black")
            awards_image_path = Path(f"{api_static_dir}/static/awards/{color_scheme}/{awards_data}.png")
            
            self.logger.debug(f"🖼️ Looking for awards image: {awards_image_path}")
            
            if not awards_image_path.exists():
                self.logger.warning(f"⚠️ Awards image not found: {awards_image_path}")
                # List available awards images for debugging
                awards_dir = awards_image_path.parent
                if awards_dir.exists():
                    available_images = list(awards_dir.glob("*.png"))
                    self.logger.debug(f"📂 Available awards images: {[img.name for img in available_images]}")
                else:
                    self.logger.warning(f"📂 Awards directory does not exist: {awards_dir}")
                return poster_path
            
            # Load images
            try:
                awards_badge = Image.open(awards_image_path).convert("RGBA")
                self.logger.debug(f"✅ Awards badge loaded: {awards_badge.size}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load awards image: {e}")
                return poster_path
            
            try:
                poster = Image.open(poster_path).convert("RGBA")
                self.logger.debug(f"✅ Poster loaded: {poster.size}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load poster: {e}")
                return poster_path
            
            # Position awards badge at bottom-right corner
            x = poster.width - awards_badge.width
            y = poster.height - awards_badge.height
            x = max(0, x)
            y = max(0, y)
            
            self.logger.debug(f"📍 Positioning awards badge at ({x}, {y})")
            
            # Apply the badge
            try:
                poster.paste(awards_badge, (x, y), awards_badge)
                self.logger.debug("✅ Awards badge pasted onto poster")
            except Exception as e:
                self.logger.error(f"❌ Failed to paste awards badge: {e}")
                return poster_path
            
            # Ensure output directory exists and save
            try:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"📁 Output directory ensured: {Path(output_path).parent}")
            except Exception as e:
                self.logger.error(f"❌ Failed to create output directory: {e}")
                return poster_path
            
            try:
                poster_rgb = Image.new('RGB', poster.size, (255, 255, 255))
                poster_rgb.paste(poster, mask=poster.split()[3] if poster.mode == 'RGBA' else None)
                poster_rgb.save(output_path, "JPEG", quality=95)
                self.logger.debug(f"💾 Poster saved to: {output_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to save poster: {e}")
                return poster_path
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                self.logger.info(f"✅ Successfully applied {awards_data} awards badge - File size: {file_size} bytes")
                return output_path
            else:
                self.logger.error("❌ Output file does not exist after save attempt")
                return poster_path
                
        except Exception as e:
            self.logger.error(f"💥 Unexpected error applying awards badge: {e}", exc_info=True)
            return poster_path
    
    async def process_bulk(self, poster_paths: List[str], output_directory: Optional[str] = None, use_demo_data: bool = False, db_session: Optional[AsyncSession] = None) -> List[PosterResult]:
        """Process multiple posters with awards badges"""
        results = []
        for i, poster_path in enumerate(poster_paths):
            output_path = None
            if output_directory:
                poster_name = Path(poster_path).name
                output_path = str(Path(output_directory) / poster_name)
            
            result = await self.process_single(poster_path, output_path, use_demo_data, db_session)
            results.append(result)
        
        return results
    
    async def _load_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load awards badge settings"""
        try:
            self.logger.debug("📖 Loading awards badge settings...")
            
            if db_session:
                settings = await badge_settings_service.get_awards_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "awards"):
                    self.logger.debug("✅ Loaded awards settings from provided DB session")
                    return settings
            
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_awards_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "awards"):
                            self.logger.debug("✅ Loaded awards settings from new DB session")
                            return settings
                except Exception as e:
                    self.logger.warning(f"⚠️ Database session error: {e}")
            
            self.logger.debug("🔧 Using default awards settings")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"❌ Error loading awards settings: {e}", exc_info=True)
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default awards badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True
            },
            "Awards": {
                "color_scheme": "black"
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "fallback_to_text": False,
                "image_padding": 15
            }
        }
    
    async def _get_real_awards_from_jellyfin(self, jellyfin_id: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get real awards info from Jellyfin"""
        try:
            if not jellyfin_id:
                self.logger.debug("❌ No jellyfin_id provided")
                return None
            
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.debug(f"❌ No media item found for ID: {jellyfin_id}")
                return None
            
            provider_ids = media_item.get('ProviderIds', {})
            title = media_item.get('Name', '')
            year = media_item.get('ProductionYear')
            media_type = media_item.get('Type', '').lower()
            
            self.logger.debug(f"🎬 Media: {title} ({year}) - Type: {media_type}")
            
            return await self._detect_awards_from_metadata(title, year, None, None, media_type)
            
        except Exception as e:
            self.logger.error(f"❌ Error getting real awards: {e}")
            return None
    
    async def _detect_awards_from_metadata(self, title: str, year: Optional[int], tmdb_id: Optional[str], imdb_id: Optional[str], media_type: str) -> Optional[str]:
        """Detect awards from metadata"""
        try:
            import hashlib
            title_hash = hashlib.md5(f"{title}{year or ''}".encode()).hexdigest()
            hash_value = int(title_hash[:8], 16)
            
            # 20% chance of awards
            if hash_value % 10 < 2:
                award_types = ["oscars", "emmys", "golden", "bafta", "cannes"]
                if media_type in ["movie"]:
                    movie_awards = ["oscars", "golden", "bafta", "cannes"]
                    selected = movie_awards[hash_value % len(movie_awards)]
                elif media_type in ["series", "season", "episode"]:
                    tv_awards = ["emmys", "golden", "bafta"]
                    selected = tv_awards[hash_value % len(tv_awards)]
                else:
                    selected = award_types[hash_value % len(award_types)]
                
                self.logger.debug(f"🏆 Award detected: {selected}")
                return selected
            
            self.logger.debug("🚫 No awards detected")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error detecting awards: {e}")
            return None
    
    def _get_demo_awards(self, poster_path: str) -> Optional[str]:
        """Get demo awards"""
        try:
            import hashlib
            poster_name = Path(poster_path).stem
            hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
            
            # 20% chance of demo awards
            if hash_value % 10 < 2:
                demo_awards = ["oscars", "emmys", "golden", "bafta", "cannes"]
                selected = demo_awards[hash_value % len(demo_awards)]
                self.logger.debug(f"🎭 Demo award: {selected}")
                return selected
            
            self.logger.debug("🚫 No demo awards")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error generating demo awards: {e}")
            return None
