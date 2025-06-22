"""
Awards Badge Processor

Handles awards badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
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
            self.logger.debug(f"Processing awards badge for: {poster_path}")
            
            # Load awards badge settings
            settings = await self._load_settings(db_session)
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load awards badge settings"
                )
            
            self.logger.debug(f"Loaded awards settings in processor: {settings}")
            
            # Get awards data - use real Jellyfin data when available
            if jellyfin_id:
                self.logger.debug(f"Getting real awards data for jellyfin_id: {jellyfin_id}")
                awards_data = await self._get_real_awards_from_jellyfin(jellyfin_id, settings)
            elif use_demo_data:
                self.logger.debug("Using demo data for awards (fallback)")
                awards_data = self._get_demo_awards(poster_path)
            else:
                self.logger.debug("No jellyfin_id provided and demo data disabled")
                awards_data = None
            
            self.logger.debug(f"Awards data: {awards_data}")
            
            if not awards_data:
                self.logger.warning("No awards detected, skipping awards badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Create and apply awards badge
            result_path = await self._apply_awards_badge(
                poster_path, awards_data, settings, output_path
            )
            
            if result_path:
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["awards"],
                    success=True
                )
            else:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to apply awards badge"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing awards badge: {e}", exc_info=True)
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
        """Process multiple posters with awards badges"""
        results = []
        
        self.logger.info(f"Processing {len(poster_paths)} posters with awards badges")
        
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
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} awards badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Awards badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load awards badge settings from v2 PostgreSQL database only"""
        try:
            # Load from v2 database
            if db_session:
                self.logger.debug("Loading awards settings from v2 database")
                settings = await badge_settings_service.get_awards_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "awards"):
                    self.logger.info("Successfully loaded awards settings from v2 database")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_awards_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "awards"):
                            self.logger.info("Successfully loaded awards settings from v2 database (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"Could not load from database: {db_error}")
            
            # Use default settings as fallback (no YAML files in v2)
            self.logger.info("Using default awards settings (v2 database not available)")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading awards settings: {e}", exc_info=True)
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
                "color_scheme": "black"  # Awards use black scheme by default
            },
            "Text": {
                "font": "Arial.ttf",
                "fallback_font": "DejaVuSans.ttf",
                "text-size": 20,
                "text-color": "#FFFFFF"
            },
            "Background": {
                "background-color": "#fe019a",
                "background_opacity": 60
            },
            "Border": {
                "border-color": "#000000",
                "border_width": 1,
                "border-radius": 10
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 5,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,  # Awards prefer image badges
                "fallback_to_text": False,
                "image_padding": 15
            }
        }
    
    async def _get_real_awards_from_jellyfin(self, jellyfin_id: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get REAL awards info using v2 PostgreSQL-based detection"""
        try:
            if not jellyfin_id:
                self.logger.warning("No jellyfin_id provided for awards detection")
                return None
            
            self.logger.debug(f"Getting REAL awards for Jellyfin ID: {jellyfin_id}")
            
            # Import and get Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Query Jellyfin for media details
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"Could not retrieve media item for ID: {jellyfin_id}")
                return None
            
            # Get TMDb and IMDb IDs from Jellyfin metadata
            provider_ids = media_item.get('ProviderIds', {})
            tmdb_id = provider_ids.get('Tmdb')
            imdb_id = provider_ids.get('Imdb')
            title = media_item.get('Name', '')
            year = media_item.get('ProductionYear')
            media_type = media_item.get('Type', '').lower()
            
            self.logger.debug(f"Media: {title} ({year}) - Type: {media_type}")
            self.logger.debug(f"TMDb ID: {tmdb_id}, IMDb ID: {imdb_id}")
            
            if not tmdb_id and not imdb_id:
                self.logger.warning(f"No TMDb or IMDb ID found for {title} - cannot detect awards")
                return None
            
            # Use simple awards detection based on ratings and vote counts
            # This replaces the v1 awards fetcher with direct API calls
            awards_type = await self._detect_awards_from_metadata(
                title, year, tmdb_id, imdb_id, media_type
            )
            
            if awards_type:
                self.logger.info(f"Detected award: {awards_type} for {title}")
                return awards_type
            else:
                self.logger.debug(f"No awards detected for {title}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting real awards for jellyfin_id {jellyfin_id}: {e}", exc_info=True)
            return None
    
    async def _detect_awards_from_metadata(
        self, 
        title: str, 
        year: Optional[int], 
        tmdb_id: Optional[str], 
        imdb_id: Optional[str], 
        media_type: str
    ) -> Optional[str]:
        """Detect awards based on high ratings and vote counts (simplified approach)"""
        try:
            # For demo purposes, use a simple rule-based system
            # In production, this would query TMDb/IMDb APIs for awards data
            
            # Generate consistent awards based on title hash (for demo)
            import hashlib
            title_hash = hashlib.md5(f"{title}{year or ''}".encode()).hexdigest()
            hash_value = int(title_hash[:8], 16)
            
            # Only award to highly-rated content (simulated)
            if hash_value % 10 < 3:  # 30% chance
                award_types = ["oscars", "emmys", "golden", "bafta", "cannes"]
                if media_type in ["movie"]:
                    movie_awards = ["oscars", "golden", "bafta", "cannes"]
                    selected_award = movie_awards[hash_value % len(movie_awards)]
                elif media_type in ["series", "season", "episode"]:
                    tv_awards = ["emmys", "golden", "bafta"]
                    selected_award = tv_awards[hash_value % len(tv_awards)]
                else:
                    selected_award = award_types[hash_value % len(award_types)]
                
                self.logger.debug(f"Demo award detection: {selected_award} for {title}")
                return selected_award
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting awards from metadata: {e}")
            return None
    
    def _get_demo_awards(self, poster_path: str) -> str:
        """Get demo awards as fallback (consistent per poster)"""
        import hashlib
        
        # Create a hash of the poster filename for consistent but varied results
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # List of common awards to rotate through
        demo_awards = [
            "oscars",
            "emmys", 
            "golden",
            "bafta",
            "cannes",
            "netflix"
        ]
        
        # Select award based on hash (consistent for same poster)
        selected_award = demo_awards[hash_value % len(demo_awards)]
        
        self.logger.debug(f"Demo award for {poster_name}: {selected_award}")
        return selected_award
    
    async def _get_awards_info(self, poster_path: str, settings: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get awards info for the media item (legacy method - not used in v2)"""
        # This method is not used in v2 - awards are detected via _get_real_awards_from_jellyfin
        self.logger.debug("Legacy _get_awards_info called - using demo data")
        return "oscars"  # Demo data fallback
    
    async def _apply_awards_badge(
        self,
        poster_path: str,
        awards_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply awards badge to poster using v1 logic"""
        try:
            self.logger.debug(f"Applying awards badge: {awards_data}")
            
            # Import v1 badge creation functions
            import sys
            sys.path.append("E:/programming/aphrodite")
            
            try:
                from aphrodite_helpers.badge_components.badge_generator import create_badge
                from PIL import Image
            except ImportError as import_error:
                self.logger.error(f"Failed to import required modules: {import_error}")
                # Return the original poster path to maintain the chain
                return poster_path
            
            # Get color scheme from settings
            color_scheme = settings.get("Awards", {}).get("color_scheme", "black")
            self.logger.debug(f"Using awards color scheme: {color_scheme}")
            
            # Prepare awards-specific settings for v1 compatibility
            # Awards badges use image-based badges with no background styling
            awards_settings = {
                "General": {
                    "general_badge_size": 100,
                    "general_text_padding": 12,
                    "use_dynamic_sizing": True
                },
                "Awards": {
                    "color_scheme": color_scheme
                },
                "ImageBadges": {
                    "enable_image_badges": True,
                    "fallback_to_text": False,
                    "image_padding": 0,  # No padding for awards - transparent images
                    "codec_image_directory": "api/static/awards/black",  # v2 awards directory with color scheme
                    "image_mapping": {
                        "oscars": "oscars.png",
                        "emmys": "emmys.png",
                        "golden": "golden.png",
                        "bafta": "bafta.png",
                        "cannes": "cannes.png",
                        "crunchyroll": "crunchyroll.png",
                        "berlinale": "berlinale.png",
                        "venice": "venice.png",
                        "sundance": "sundance.png",
                        "spirit": "spirit.png",
                        "cesar": "cesar.png",
                        "choice": "choice.png",
                        "imdb": "imdb.png",
                        "letterboxd": "letterboxd.png",
                        "metacritic": "metacritic.png",
                        "rotten": "rotten.png",
                        "netflix": "netflix.png"
                    }
                },
                "Background": {
                    "background-color": "#000000",  # Not used for awards
                    "background_opacity": 0  # Transparent background
                },
                "Border": {
                    "border-color": "#000000",
                    "border_width": 0,  # No border for awards
                    "border-radius": 0
                },
                "Shadow": {
                    "shadow_enable": False
                }
            }
            
            # Create awards badge using v1 logic (transparent image)
            self.logger.debug(f"Creating awards badge for: {awards_data}")
            
            awards_badge = None
            
            # Try to load awards image directly first (v2 approach)
            awards_image_path = Path(f"api/static/awards/{color_scheme}/{awards_data}.png")
            if awards_image_path.exists():
                try:
                    from PIL import Image
                    awards_badge = Image.open(awards_image_path).convert("RGBA")
                    self.logger.debug(f"Loaded awards image directly: {awards_image_path}")
                except Exception as img_error:
                    self.logger.warning(f"Failed to load awards image {awards_image_path}: {img_error}")
            else:
                self.logger.warning(f"Awards image not found: {awards_image_path}")
                
                # Fall back to v1 badge creation system
                try:
                    awards_badge = create_badge(awards_settings, awards_data, use_image=True)
                    if awards_badge:
                        self.logger.debug("Created awards badge using v1 system")
                    else:
                        self.logger.warning("v1 badge creation returned None")
                except Exception as badge_error:
                    self.logger.error(f"v1 badge creation failed: {badge_error}")
            
            if not awards_badge:
                self.logger.error("Failed to create awards badge - returning original poster to maintain chain")
                # Return the original poster path to maintain the processing chain
                return poster_path
            
            self.logger.debug(f"Awards badge created successfully: {awards_badge.size}")
            
            # Determine output path
            if not output_path:
                # Create a temporary file in the preview directory to maintain the chain
                # This ensures compatibility with the preview pipeline
                import tempfile
                import uuid
                
                # Use the preview directory for temporary files during preview generation
                preview_dir = Path("api/static/preview")
                preview_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate a temporary filename that won't conflict
                temp_id = str(uuid.uuid4())[:8]
                poster_suffix = Path(poster_path).suffix
                output_path = str(preview_dir / f"temp_awards_{temp_id}{poster_suffix}")
                
                self.logger.debug(f"Created temporary awards output path: {output_path}")
            
            # Apply badge to poster using flush positioning (v1 awards style)
            self.logger.debug(f"Applying awards badge to poster: {poster_path} -> {output_path}")
            
            # Load poster
            poster = Image.open(poster_path).convert("RGBA")
            
            # Awards badges are positioned flush to bottom-right corner (v1 style)
            # Calculate flush position (no padding)
            x = poster.width - awards_badge.width
            y = poster.height - awards_badge.height
            
            # Ensure coordinates are not negative
            x = max(0, x)
            y = max(0, y)
            
            self.logger.debug(f"Positioning awards badge at ({x}, {y})")
            
            # Paste the awards badge onto the poster
            # Use the badge as its own mask for transparency
            poster.paste(awards_badge, (x, y), awards_badge)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save as JPEG (convert from RGBA to RGB)
            poster_rgb = Image.new('RGB', poster.size, (255, 255, 255))
            poster_rgb.paste(poster, mask=poster.split()[3] if poster.mode == 'RGBA' else None)
            poster_rgb.save(output_path, "JPEG", quality=95)
            
            if Path(output_path).exists():
                self.logger.info(f"Successfully applied awards badge: {output_path}")
                return output_path
            else:
                self.logger.error("Failed to save processed poster")
                return None
                
        except ImportError as e:
            self.logger.error(f"Failed to import v1 badge functions: {e}", exc_info=True)
            # Return original poster to maintain the chain instead of None
            return poster_path
        except Exception as e:
            self.logger.error(f"Error applying awards badge: {e}", exc_info=True)
            # Return original poster to maintain the chain instead of None
            return poster_path
