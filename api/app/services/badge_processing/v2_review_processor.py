"""
Pure V2 Review Badge Processor

Completely V2-native review badge processing with no V1 dependencies.
Clear logging for system differentiation.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from .renderers.review_data_fetcher import V2ReviewDataFetcher
from .renderers.multi_badge_renderer import V2MultiBadgeRenderer
from app.core.database import async_session_factory


class V2ReviewBadgeProcessor(BaseBadgeProcessor):
    """Pure V2 review badge processor - no V1 dependencies"""
    
    def __init__(self):
        super().__init__("review")
        self.logger = get_logger("aphrodite.badge.review.v2", service="badge")
        self.review_fetcher = V2ReviewDataFetcher()
        self.multi_renderer = V2MultiBadgeRenderer()
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with review badge using pure V2 system"""
        try:
            self.logger.info(f"🎬 [V2 REVIEW] PROCESSOR STARTED for: {poster_path}")
            self.logger.info(f"🎬 [V2 REVIEW] Jellyfin ID: {jellyfin_id}")
            self.logger.info(f"🎬 [V2 REVIEW] Use demo data: {use_demo_data}")
            
            # Load review badge settings from PostgreSQL
            settings = await self._load_v2_settings(db_session)
            if not settings:
                self.logger.error("❌ [V2 REVIEW] Failed to load settings from PostgreSQL")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load V2 review badge settings"
                )
            
            self.logger.info("✅ [V2 REVIEW] Settings loaded from PostgreSQL")
            
            # Get review data using pure V2 methods
            reviews = await self._get_v2_review_data(jellyfin_id, use_demo_data, poster_path, settings)
            if not reviews:
                self.logger.warning("⚠️ [V2 REVIEW] No reviews found, skipping review badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            self.logger.info(f"📊 [V2 REVIEW] Found {len(reviews)} reviews")
            for i, review in enumerate(reviews):
                source = review.get('source', 'Unknown')
                score = review.get('text', 'N/A')
                self.logger.info(f"📈 [V2 REVIEW] Review {i+1}: {source} = {score}")
            
            # Create review badges using V2 renderer
            result_path = await self._create_v2_review_badges(
                poster_path, reviews, settings, output_path
            )
            
            if result_path:
                self.logger.info(f"✅ [V2 REVIEW] PROCESSOR COMPLETED: {result_path}")
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["review"],
                    success=True
                )
            else:
                self.logger.error(f"❌ [V2 REVIEW] Badge creation failed")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="V2 review badge creation failed"
                )
                
        except Exception as e:
            self.logger.error(f"🚨 [V2 REVIEW] PROCESSOR EXCEPTION: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=f"V2 review processor error: {str(e)}"
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
    ) -> List[PosterResult]:
        """Process multiple posters with V2 review badges"""
        results = []
        
        self.logger.info(f"🎬 [V2 REVIEW] BULK PROCESSING {len(poster_paths)} posters")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"🎬 [V2 REVIEW] Processing {i+1}/{len(poster_paths)}: {poster_path}")
            
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
                self.logger.info(f"🎬 [V2 REVIEW] Processed {i+1}/{len(poster_paths)} badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"🎬 [V2 REVIEW] BULK COMPLETED: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_v2_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load review badge settings from V2 PostgreSQL database only"""
        try:
            self.logger.debug("🗄️ [V2 REVIEW] Loading settings from PostgreSQL")
            
            # Load from v2 database
            if db_session:
                settings = await badge_settings_service.get_review_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "review"):
                    self.logger.info("✅ [V2 REVIEW] Settings loaded from PostgreSQL (provided session)")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_review_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "review"):
                            self.logger.info("✅ [V2 REVIEW] Settings loaded from PostgreSQL (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"⚠️ [V2 REVIEW] Database connection failed: {db_error}")
            
            # Use V2 default settings as fallback (no YAML files)
            self.logger.info("⚠️ [V2 REVIEW] Using V2 default settings (PostgreSQL unavailable)")
            return self._get_v2_default_settings()
            
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW] Error loading settings: {e}", exc_info=True)
            return self._get_v2_default_settings()
    
    def _get_v2_default_settings(self) -> Dict[str, Any]:
        """Get V2 default review badge settings"""
        return {
            "General": {
                "general_badge_position": "bottom-left",
                "general_edge_padding": 30,
                "badge_orientation": "vertical",
                "badge_spacing": 15,
                "max_badges_to_display": 4,
                "general_text_padding": 20
            },
            "Text": {
                "font": "AvenirNextLTProBold.otf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 60,
                "text-color": "#FFFFFF"
            },
            "Background": {
                "background-color": "#2C2C2C",
                "background_opacity": 60
            },
            "Border": {
                "border-color": "#2C2C2C",
                "border_width": 1,
                "border-radius": 10
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "fallback_to_text": True,
                "image_padding": 5,
                "codec_image_directory": "images/rating"
            },
            "Sources": {
                "enable_imdb": True,
                "enable_tmdb": True,
                "enable_rotten_tomatoes_critics": True,
                "enable_metacritic": True,
                "enable_myanimelist": False
            },
            "Display": {
                "show_percentage_only": True
            }
        }
    
    async def _get_v2_review_data(
        self, 
        jellyfin_id: Optional[str], 
        use_demo_data: bool, 
        poster_path: str,
        settings: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get review data using pure V2 methods only"""
        try:
            # Use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"🔍 [V2 REVIEW] Getting real reviews for ID: {jellyfin_id}")
                reviews = await self.review_fetcher.get_reviews_for_media(jellyfin_id, settings)
                if reviews:
                    self.logger.debug(f"✅ [V2 REVIEW] Real reviews found: {len(reviews)}")
                    return reviews
                else:
                    self.logger.debug("⚠️ [V2 REVIEW] No real reviews found, checking demo fallback")
            
            # Use demo data as fallback
            if use_demo_data:
                self.logger.debug("🎭 [V2 REVIEW] Using demo review data")
                return await self.review_fetcher.get_demo_reviews(poster_path, settings)
            
            self.logger.warning("⚠️ [V2 REVIEW] No review source available")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW] Error getting review data: {e}", exc_info=True)
            return None
    
    async def _create_v2_review_badges(
        self,
        poster_path: str,
        reviews: List[Dict[str, Any]],
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create review badges using pure V2 renderer"""
        try:
            self.logger.debug(f"🎨 [V2 REVIEW] Creating badges for {len(reviews)} reviews")
            
            # Determine output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate V2 preview path
                poster_name = Path(poster_path).name
                final_output_path = f"/app/api/static/preview/{poster_name}"
            
            # Apply review badges using V2 multi-renderer
            success = self.multi_renderer.apply_review_badges_to_poster(
                poster_path, reviews, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [V2 REVIEW] Review badges applied successfully: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [V2 REVIEW] Review badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [V2 REVIEW] Badge creation error: {e}", exc_info=True)
            return None
