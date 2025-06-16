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
            
            # Get awards data - NO DEMO DATA, only real awards
            if use_demo_data:
                self.logger.warning("Demo data mode disabled - using real data only")
            
            self.logger.debug(f"Getting real awards data for jellyfin_id: {jellyfin_id}")
            awards_data = await self._get_real_awards_from_jellyfin(jellyfin_id, settings)
            self.logger.debug(f"Detected real awards: {awards_data}")
            
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
        """Get REAL awards info from external APIs using Jellyfin metadata"""
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
                self.logger.warning(f"No TMDb or IMDb ID found for {title} - cannot fetch real awards")
                return None
            
            # Use v1 awards fetcher to get REAL awards
            try:
                # Import v1 awards system
                import sys
                sys.path.append("E:/programming/aphrodite")
                
                from aphrodite_helpers.get_awards_info import AwardsFetcher
                from aphrodite_helpers.settings_validator import load_settings
                
                # Load v1 settings for API keys
                v1_settings = load_settings()
                if not v1_settings:
                    self.logger.warning("Could not load v1 settings for awards APIs")
                    return None
                
                # Create awards fetcher with real API credentials
                awards_fetcher = AwardsFetcher(v1_settings)
                
                # Get REAL awards using Jellyfin connection info
                jellyfin_config = v1_settings.get('api_keys', {}).get('Jellyfin', [{}])[0]
                jellyfin_url = jellyfin_config.get('url', '')
                api_key = jellyfin_config.get('api_key', '')
                user_id = jellyfin_config.get('user_id', '')
                
                if not all([jellyfin_url, api_key, user_id]):
                    self.logger.warning("Jellyfin connection details not available for awards detection")
                    return None
                
                # Get real awards information using v1 logic
                awards_info = awards_fetcher.get_media_awards_info(jellyfin_url, api_key, user_id, jellyfin_id)
                
                if awards_info and "award_type" in awards_info:
                    award_type = awards_info["award_type"]
                    self.logger.info(f"Found REAL award: {award_type} for {title}")
                    return award_type
                else:
                    self.logger.debug(f"No real awards detected for {title}")
                    return None
                
            except ImportError as e:
                self.logger.error(f"Could not import v1 awards system: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Error fetching real awards: {e}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting real awards for jellyfin_id {jellyfin_id}: {e}", exc_info=True)
            return None
    
    async def _get_awards_info(self, poster_path: str, settings: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get awards info for the media item using v1 logic"""
        try:
            # Import v1 awards detection logic
            import sys
            sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.get_awards_info import AwardsFetcher
            from aphrodite_helpers.settings_validator import load_settings
            
            # Load v1 settings for awards detection
            v1_settings = load_settings()
            if not v1_settings:
                self.logger.warning("Could not load v1 settings for awards detection")
                return None
            
            # Create awards fetcher
            awards_fetcher = AwardsFetcher(v1_settings)
            
            # Extract item ID from poster path (assuming path contains item ID)
            # This is a simplified approach - in production would need proper item ID extraction
            import re
            item_id_match = re.search(r'item_([a-f0-9]{32})', poster_path)
            if not item_id_match:
                self.logger.debug(f"Could not extract item ID from poster path: {poster_path}")
                return None
            
            item_id = item_id_match.group(1)
            self.logger.debug(f"Extracted item ID: {item_id}")
            
            # Get Jellyfin connection details from v1 settings
            jellyfin_settings = v1_settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
            jellyfin_url = jellyfin_settings.get("url", "")
            api_key = jellyfin_settings.get("api_key", "")
            user_id = jellyfin_settings.get("user_id", "")
            
            if not all([jellyfin_url, api_key, user_id]):
                self.logger.warning("Jellyfin connection details not available for awards detection")
                return None
            
            # Get awards information using v1 logic
            awards_info = awards_fetcher.get_media_awards_info(jellyfin_url, api_key, user_id, item_id)
            
            if awards_info and "award_type" in awards_info:
                award_type = awards_info["award_type"]
                self.logger.info(f"Detected award: {award_type} for item {item_id}")
                return award_type
            else:
                self.logger.debug(f"No awards detected for item {item_id}")
                return None
            
        except ImportError as e:
            self.logger.warning(f"Could not import v1 awards detection: {e}")
            # Fall back to demo data
            return "oscars"
        except Exception as e:
            self.logger.error(f"Error getting awards info: {e}", exc_info=True)
            # Fall back to demo data for development
            return "oscars"
    
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
            
            from aphrodite_helpers.badge_components.badge_generator import create_badge
            from PIL import Image
            
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
            
            # Try to load awards image directly first (v2 approach)
            awards_image_path = Path(f"api/static/awards/{color_scheme}/{awards_data}.png")
            if awards_image_path.exists():
                from PIL import Image
                awards_badge = Image.open(awards_image_path).convert("RGBA")
                self.logger.debug(f"Loaded awards image directly: {awards_image_path}")
            else:
                # Fall back to v1 badge creation system
                awards_badge = create_badge(awards_settings, awards_data, use_image=True)
            
            if not awards_badge:
                self.logger.error("Failed to create awards badge")
                return None
            
            self.logger.debug(f"Awards badge created successfully: {awards_badge.size}")
            
            # Determine output path
            if not output_path:
                poster_stem = Path(poster_path).stem
                poster_suffix = Path(poster_path).suffix
                output_path = str(Path(poster_path).parent / f"{poster_stem}_awards{poster_suffix}")
            
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
            return None
        except Exception as e:
            self.logger.error(f"Error applying awards badge: {e}", exc_info=True)
            return None
