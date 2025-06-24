"""
Review Badge Processor

Handles review badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from app.core.database import async_session_factory


class ReviewBadgeProcessor(BaseBadgeProcessor):
    """Review badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("review")
        self.logger = get_logger("aphrodite.badge.review", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with review badge"""
        try:
            self.logger.debug(f"Processing review badge for: {poster_path}")
            
            # Load review badge settings
            settings = await self._load_settings(db_session)
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load review badge settings"
                )
            
            # Debug: Log the loaded settings
            self.logger.debug(f"Loaded review settings in processor: {settings}")
            
            # Get review data - use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"Getting real review data for jellyfin_id: {jellyfin_id}")
                review_data = await self._get_real_reviews_from_jellyfin(jellyfin_id, settings)
            elif use_demo_data:
                self.logger.debug("Using demo data for reviews (fallback)")
                review_data = self._get_demo_reviews(poster_path, settings)
            else:
                self.logger.debug("No jellyfin_id provided and demo data disabled")
                review_data = None
            
            self.logger.debug(f"Retrieved {len(review_data)} reviews" if review_data else "No reviews found")
            
            if not review_data:
                self.logger.warning("No reviews found, skipping review badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Create and apply review badge
            result_path = await self._apply_review_badge(
                poster_path, review_data, settings, output_path
            )
            
            if result_path:
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["review"],
                    success=True
                )
            else:
                self.logger.error("Review badge applicator returned None - check applicator logs")
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to apply review badge - applicator returned None"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing review badge: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=str(e)
            )
    
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None
    ) -> List[PosterResult]:
        """Process multiple posters with review badges"""
        results = []
        
        self.logger.info(f"Processing {len(poster_paths)} posters with review badges")
        
        for i, poster_path in enumerate(poster_paths):
            self.logger.debug(f"Processing poster {i+1}/{len(poster_paths)}: {poster_path}")
            
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
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} review badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Review badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load review badge settings from v2 database only"""
        try:
            # Load from v2 database
            if db_session:
                self.logger.debug("Loading review settings from v2 database")
                settings = await badge_settings_service.get_review_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "review"):
                    self.logger.info("Successfully loaded review settings from v2 database")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_review_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "review"):
                            self.logger.info("Successfully loaded review settings from v2 database (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"Could not load from database: {db_error}")
            
            # Use default settings as fallback (no YAML files in v2)
            self.logger.info("Using default review settings (v2 database not available)")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading review settings: {e}", exc_info=True)
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default review badge settings"""
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
                "codec_image_directory": "images/rating",  # Where review badge images are located
                "image_mapping": {  # Maps review sources to image files
                    "IMDb": "IMDb.png",
                    "Rotten Tomatoes": "rt.png",
                    "RT-Crit-Fresh": "rt.png",
                    "Metacritic": "metacritic_logo.png",
                    "TMDb": "TMDb.png",
                    "MyAnimeList": "MAL.png"
                }
            }
        }
    
    async def _get_real_reviews_from_jellyfin(self, jellyfin_id: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """Get REAL review info using v2 PostgreSQL-based review detector"""
        try:
            if not jellyfin_id:
                self.logger.warning("No jellyfin_id provided for review detection")
                return None
            
            self.logger.debug(f"Getting REAL reviews for Jellyfin ID: {jellyfin_id}")
            
            # Use v2 review detector (PostgreSQL-based) instead of v1 system
            from .review_detector import get_review_detector
            detector = get_review_detector()
            
            # Load review source settings from PostgreSQL
            review_source_settings = await badge_settings_service.get_review_source_settings_standalone(force_reload=True)
            
            # Combine badge settings and source settings for the detector
            combined_settings = settings.copy() if settings else {}
            if review_source_settings:
                combined_settings.update(review_source_settings)
                self.logger.debug(f"Added PostgreSQL review source settings: {review_source_settings}")
            
            # Create a fake poster path for the detector (it expects a path)
            fake_poster_path = f"jellyfin_{jellyfin_id}_fake.jpg"
            
            # Get real reviews using v2 detector
            real_reviews = await detector.get_review_info(fake_poster_path, combined_settings, jellyfin_id)
            
            if real_reviews:
                self.logger.info(f"Found {len(real_reviews)} REAL reviews using v2 detector")
                for review in real_reviews:
                    source = review.get('source', 'Unknown')
                    score = review.get('text', 'N/A')
                    self.logger.debug(f"  Real {source}: {score}")
                return real_reviews
            else:
                self.logger.warning(f"No real reviews found using v2 detector")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting real reviews for jellyfin_id {jellyfin_id}: {e}", exc_info=True)
            return None
    
    async def _get_review_info(self, poster_path: str, settings: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """Get real review info using modular detector"""
        from .review_detector import get_review_detector
        detector = get_review_detector()
        
        # CRITICAL FIX: Load review source settings that contain percentage setting
        review_source_settings = await badge_settings_service.get_review_source_settings_standalone(force_reload=True)
        
        # Combine both badge settings and source settings for the detector
        combined_settings = settings.copy() if settings else {}
        
        if review_source_settings:
            # Add review source settings (which contain show_percentage_only)
            combined_settings.update(review_source_settings)
            self.logger.debug(f"Added review source settings to detector: {review_source_settings}")
        
        return await detector.get_review_info(poster_path, combined_settings)
    
    def _get_demo_reviews(self, poster_path: str, settings: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get demo review data using modular detector"""
        from .review_detector import get_review_detector
        detector = get_review_detector()
        
        # CRITICAL FIX: Load review source settings for demo data too
        import asyncio
        try:
            review_source_settings = asyncio.run(
                badge_settings_service.get_review_source_settings_standalone(force_reload=True)
            )
            
            # Combine both badge settings and source settings for the detector
            combined_settings = settings.copy() if settings else {}
            
            if review_source_settings:
                combined_settings.update(review_source_settings)
                self.logger.debug(f"Added review source settings to demo reviews: {review_source_settings}")
            
            return detector.get_demo_reviews(poster_path, combined_settings)
            
        except Exception as e:
            self.logger.error(f"Error loading review source settings for demo: {e}")
            return detector.get_demo_reviews(poster_path, settings)
    
    async def _apply_review_badge(
        self,
        poster_path: str,
        review_data: List[Dict[str, Any]],
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply review badge using modular applicator"""
        from .review_applicator import get_review_applicator
        applicator = get_review_applicator()
        return await applicator.apply_review_badge(
            poster_path, review_data, settings, output_path
        )
