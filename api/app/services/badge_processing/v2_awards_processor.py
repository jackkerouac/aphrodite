"""
Pure V2 Awards Badge Processor

Completely V2-native awards badge processing with no V1 dependencies.
Clear logging for system differentiation.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import os

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from .renderers.awards_data_fetcher import V2AwardsDataFetcher
from .renderers import UnifiedBadgeRenderer
from app.core.database import async_session_factory


class V2AwardsBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 awards badge processor - no V1 dependencies"""
    
    def __init__(self):
        super().__init__("awards")
        self.logger = get_logger("aphrodite.badge.awards.v2", service="badge")
        self.awards_fetcher = V2AwardsDataFetcher()
        self.renderer = UnifiedBadgeRenderer()
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with awards badge using pure V2 system"""
        try:
            self.logger.info(f"🏆 [V2 AWARDS] PROCESSOR STARTED for: {poster_path}")
            self.logger.info(f"🏆 [V2 AWARDS] Jellyfin ID: {jellyfin_id}")
            self.logger.info(f"🏆 [V2 AWARDS] Use demo data: {use_demo_data}")
            
            # Load awards badge settings from PostgreSQL
            settings = await self._load_v2_settings(db_session)
            if not settings:
                self.logger.error("❌ [V2 AWARDS] Failed to load settings from PostgreSQL")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load V2 awards badge settings"
                )
            
            self.logger.info("✅ [V2 AWARDS] Settings loaded from PostgreSQL")
            
            # Get awards data using pure V2 methods
            awards_data = await self._get_v2_awards_data(jellyfin_id, use_demo_data, poster_path)
            if not awards_data:
                self.logger.warning("⚠️ [V2 AWARDS] No awards found, skipping awards badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.info(f"🏆 [V2 AWARDS] Awards detected: {awards_data}")
            
            # Create awards badge using V2 renderer
            result_path = await self._create_v2_awards_badge(
                poster_path, awards_data, settings, output_path
            )
            
            if result_path:
                self.logger.info(f"✅ [V2 AWARDS] PROCESSOR COMPLETED: {result_path}")
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["awards"],
                    success=True
                )
            else:
                self.logger.error(f"❌ [V2 AWARDS] Badge creation failed")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="V2 awards badge creation failed"
                )
                
        except Exception as e:
            self.logger.error(f"🚨 [V2 AWARDS] PROCESSOR EXCEPTION: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=f"V2 awards processor error: {str(e)}"
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
    ) -> List[PosterResult]:
        """Process multiple posters with V2 awards badges"""
        results = []
        
        self.logger.info(f"🏆 [V2 AWARDS] BULK PROCESSING {len(poster_paths)} posters")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"🏆 [V2 AWARDS] Processing {i+1}/{len(poster_paths)}: {poster_path}")
            
            # Calculate output path for bulk processing
            output_path = None
            if output_directory:
                poster_name = Path(poster_path).name
                output_path = str(Path(output_directory) / poster_name)
            
            # Process single poster
            result = await self.process_single(poster_path, output_path, use_demo_data, db_session)
            results.append(result)
            
            # Log progress for bulk operations
            if (i + 1) % 10 == 0:
                self.logger.info(f"🏆 [V2 AWARDS] Processed {i+1}/{len(poster_paths)} badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"🏆 [V2 AWARDS] BULK COMPLETED: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_v2_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load awards badge settings from V2 PostgreSQL database only"""
        try:
            self.logger.debug("🗄️ [V2 AWARDS] Loading settings from PostgreSQL")
            
            # Load from v2 database
            if db_session:
                settings = await badge_settings_service.get_awards_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "awards"):
                    self.logger.info("✅ [V2 AWARDS] Settings loaded from PostgreSQL (provided session)")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_awards_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "awards"):
                            self.logger.info("✅ [V2 AWARDS] Settings loaded from PostgreSQL (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"⚠️ [V2 AWARDS] Database connection failed: {db_error}")
            
            # Use V2 default settings as fallback (no YAML files)
            self.logger.info("⚠️ [V2 AWARDS] Using V2 default settings (PostgreSQL unavailable)")
            return self._get_v2_default_settings()
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS] Error loading settings: {e}", exc_info=True)
            return self._get_v2_default_settings()
    
    def _get_v2_default_settings(self) -> Dict[str, Any]:
        """Get V2 default awards badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True,
                "general_badge_position": "bottom-right",
                "general_edge_padding": 30
            },
            "Text": {
                "font": "Arial.ttf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 20,
                "text-color": "#FFFFFF"
            },
            "Background": {
                "background-color": "#FFD700",
                "background_opacity": 80
            },
            "Border": {
                "border-color": "#000000",
                "border_width": 1,
                "border-radius": 10
            },
            "Awards": {
                "color_scheme": "black"
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "fallback_to_text": False,
                "image_padding": 15,
                "codec_image_directory": "images/awards"
            }
        }
    
    async def _get_v2_awards_data(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str
    ) -> Optional[str]:
        """Get awards data using pure V2 methods only"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [V2 AWARDS] Getting real awards for ID: {jellyfin_id}")
                awards = await self.awards_fetcher.get_awards_for_media(jellyfin_id)
                if awards:
                    self.logger.debug(f"✅ [V2 AWARDS] Real awards found: {awards}")
                    return awards
                else:
                    self.logger.debug("⚠️ [V2 AWARDS] No real awards found, checking demo fallback")
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [V2 AWARDS] Using demo awards data")
                return self.awards_fetcher.get_demo_awards(poster_path)
            
            self.logger.warning("⚠️ [V2 AWARDS] No awards source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS] Error getting awards data: {e}", exc_info=True)
            return None
    
    async def _create_v2_awards_badge(
        self,
        poster_path: str,
        awards_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create awards badge using pure V2 renderer"""
        try:
            self.logger.debug(f"🎨 [V2 AWARDS] Creating badge for awards: {awards_data}")
            
            # Determine output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate V2 preview path
                poster_name = Path(poster_path).name
                final_output_path = f"/app/api/static/preview/{poster_name}"
            
            # Check if image badges are enabled
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', True)
            
            badge = None
            
            if image_badges_enabled:
                # Try image badge first
                self.logger.debug(f"🖼️ [V2 AWARDS] Attempting image badge for: {awards_data}")
                color_scheme = settings.get('Awards', {}).get('color_scheme', 'black')
                image_file = f"{color_scheme}/{awards_data}.png"
                
                badge = self.renderer.create_image_badge(image_file, settings, "awards")
                
                if badge:
                    self.logger.debug(f"✅ [V2 AWARDS] Image badge created successfully")
                else:
                    self.logger.debug(f"⚠️ [V2 AWARDS] Image badge failed, checking fallback")
                    fallback_to_text = settings.get('ImageBadges', {}).get('fallback_to_text', False)
                    
                    if fallback_to_text:
                        self.logger.debug(f"📝 [V2 AWARDS] Using text badge fallback")
                        badge = self.renderer.create_text_badge(awards_data.upper(), settings, "awards")
            else:
                # Use text badge directly
                self.logger.debug(f"📝 [V2 AWARDS] Creating text badge")
                badge = self.renderer.create_text_badge(awards_data.upper(), settings, "awards")
            
            if not badge:
                self.logger.error(f"❌ [V2 AWARDS] Badge creation failed")
                return None
            
            # Apply badge to poster
            success = self.renderer.apply_badge_to_poster(
                poster_path, badge, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [V2 AWARDS] Badge applied successfully: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [V2 AWARDS] Badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS] Badge creation error: {e}", exc_info=True)
            return None
