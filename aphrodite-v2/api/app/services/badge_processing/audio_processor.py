"""
Audio Badge Processor

Handles audio codec badge creation and application using v1 logic ported to v2 architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import json
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from .base_processor import BaseBadgeProcessor
from .types import PosterResult
from .database_service import badge_settings_service
from app.core.database import async_session_factory


class AudioBadgeProcessor(BaseBadgeProcessor):
    """Audio badge processor for single and bulk operations"""
    
    def __init__(self):
        super().__init__("audio")
        self.logger = get_logger("aphrodite.badge.audio", service="badge")
    
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False,
        db_session: Optional[AsyncSession] = None,
        jellyfin_id: Optional[str] = None
    ) -> PosterResult:
        """Process a single poster with audio badge"""
        try:
            self.logger.debug(f"Processing audio badge for: {poster_path}")
            
            # Load audio badge settings
            settings = await self._load_settings(db_session)
            if not settings:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to load audio badge settings"
                )
            
            # Get audio codec data - NO DEMO DATA, only real codec detection
            if use_demo_data:
                self.logger.warning("Demo data mode disabled - using real data only")
            
            self.logger.debug(f"Getting real audio codec for jellyfin_id: {jellyfin_id}")
            codec_data = await self._get_audio_codec_from_jellyfin_id(jellyfin_id)
            self.logger.debug(f"Detected real audio codec: {codec_data}")
            
            if not codec_data:
                self.logger.warning("No audio codec detected, skipping audio badge")
                return PosterResult(
                    source_path=poster_path,
                    output_path=poster_path,
                    applied_badges=[],
                    success=True
                )
            
            # Create and apply audio badge
            result_path = await self._apply_audio_badge(
                poster_path, codec_data, settings, output_path
            )
            
            if result_path:
                return PosterResult(
                    source_path=poster_path,
                    output_path=result_path,
                    applied_badges=["audio"],
                    success=True
                )
            else:
                return PosterResult(
                    source_path=poster_path,
                    success=False,
                    error="Failed to apply audio badge"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing audio badge: {e}", exc_info=True)
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
        """Process multiple posters with audio badges"""
        results = []
        
        self.logger.info(f"Processing {len(poster_paths)} posters with audio badges")
        
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
                self.logger.info(f"Processed {i+1}/{len(poster_paths)} audio badges")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Audio badge bulk processing complete: {successful}/{len(results)} successful")
        
        return results
    
    async def _load_settings(self, db_session: Optional[AsyncSession] = None) -> Optional[Dict[str, Any]]:
        """Load audio badge settings from v2 PostgreSQL database only"""
        try:
            # Load from v2 database
            if db_session:
                self.logger.debug("Loading audio settings from v2 database")
                settings = await badge_settings_service.get_audio_settings(db_session, force_reload=True)
                if settings and await badge_settings_service.validate_settings(settings, "audio"):
                    self.logger.info("Successfully loaded audio settings from v2 database")
                    return settings
            
            # Try to get a database session if not provided
            if not db_session:
                try:
                    async with async_session_factory() as db:
                        settings = await badge_settings_service.get_audio_settings(db, force_reload=True)
                        if settings and await badge_settings_service.validate_settings(settings, "audio"):
                            self.logger.info("Successfully loaded audio settings from v2 database (new session)")
                            return settings
                except Exception as db_error:
                    self.logger.warning(f"Could not load from database: {db_error}")
            
            # Use default settings as fallback (no YAML files in v2)
            self.logger.info("Using default audio settings (v2 database not available)")
            return self._get_default_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading audio settings: {e}", exc_info=True)
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default audio badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
                "general_text_padding": 12,
                "use_dynamic_sizing": True
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
                "enable_image_badges": False,
                "fallback_to_text": True,
                "image_padding": 15
            }
        }
    
    async def _get_audio_codec_from_jellyfin_id(self, jellyfin_id: Optional[str] = None) -> Optional[str]:
        """Get real audio codec directly from Jellyfin ID (CRITICAL FIX)"""
        try:
            if not jellyfin_id:
                self.logger.warning("No jellyfin_id provided for audio codec detection")
                return None
            
            self.logger.debug(f"Getting audio codec for Jellyfin ID: {jellyfin_id}")
            
            # Import and get Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Query Jellyfin for media details
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"Could not retrieve media item for ID: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"Media type for {jellyfin_id}: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get audio codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"Movie audio codec for {jellyfin_id}: {codec}")
                return codec
            
            elif media_type in ['Series', 'Season']:
                # For TV: sample first 5 episodes for dominant codec
                codec = await jellyfin_service.get_tv_series_dominant_codec(jellyfin_id)
                self.logger.debug(f"TV series dominant codec for {jellyfin_id}: {codec}")
                return codec
            
            elif media_type == 'Episode':
                # For individual episodes: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"Episode audio codec for {jellyfin_id}: {codec}")
                return codec
            
            else:
                self.logger.warning(f"Unsupported media type '{media_type}' for {jellyfin_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting audio codec for jellyfin_id {jellyfin_id}: {e}", exc_info=True)
            return None
    
    async def _get_audio_codec(self, poster_path: str, jellyfin_id: Optional[str] = None) -> Optional[str]:
        """Get real audio codec from Jellyfin metadata"""
        try:
            # If jellyfin_id is provided directly, use it (preferred method)
            if jellyfin_id:
                self.logger.debug(f"Using provided Jellyfin ID: {jellyfin_id}")
            else:
                # Fall back to extracting from poster path (legacy method)
                poster_file = Path(poster_path)
                
                # Handle both original and resized filenames
                if "jellyfin_" in poster_file.name:
                    # For resized files, we need to look for the original metadata file
                    if poster_file.name.startswith('resized_jellyfin_'):
                        # Convert resized filename back to original for metadata lookup
                        original_name = poster_file.name[8:]  # Remove 'resized_' prefix
                        metadata_name = Path(original_name).stem + '.meta'
                        metadata_path = poster_file.parent / metadata_name
                    else:
                        # Use normal metadata path for original files
                        metadata_path = poster_file.with_suffix('.meta')
                    if metadata_path.exists():
                        try:
                            import json
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            jellyfin_id = metadata.get('jellyfin_id')
                            if jellyfin_id:
                                self.logger.debug(f"Found Jellyfin ID from metadata: {jellyfin_id}")
                            else:
                                self.logger.warning("No jellyfin_id in metadata file")
                                return None
                        except Exception as e:
                            self.logger.warning(f"Could not read metadata file: {e}")
                            # Fall back to filename parsing
                            jellyfin_id = self._extract_jellyfin_id_from_filename(poster_file.name)
                    else:
                        # Fall back to filename parsing for older cached files
                        jellyfin_id = self._extract_jellyfin_id_from_filename(poster_file.name)
                else:
                    # Not a Jellyfin cached poster, return None
                    self.logger.debug("Not a Jellyfin cached poster, no audio codec available")
                    return None
                
                if not jellyfin_id:
                    self.logger.warning("Could not extract Jellyfin ID from poster path")
                    return None
            
            self.logger.debug(f"Extracting audio codec for Jellyfin ID: {jellyfin_id}")
            
            # Import and get Jellyfin service
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            
            # Query Jellyfin for media details
            media_item = await jellyfin_service.get_media_item_by_id(jellyfin_id)
            if not media_item:
                self.logger.warning(f"Could not retrieve media item for ID: {jellyfin_id}")
                return None
            
            media_type = media_item.get('Type', '')
            self.logger.debug(f"Media type for {jellyfin_id}: {media_type}")
            
            if media_type == 'Movie':
                # For movies: get audio codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"Movie audio codec for {jellyfin_id}: {codec}")
                return codec
            
            elif media_type in ['Series', 'Season']:
                # For TV: sample first 5 episodes for dominant codec
                codec = await jellyfin_service.get_tv_series_dominant_codec(jellyfin_id)
                self.logger.debug(f"TV series dominant codec for {jellyfin_id}: {codec}")
                return codec
            
            elif media_type == 'Episode':
                # For individual episodes: get codec directly
                codec = await jellyfin_service.get_audio_codec_info(media_item)
                self.logger.debug(f"Episode audio codec for {jellyfin_id}: {codec}")
                return codec
            
            else:
                self.logger.warning(f"Unsupported media type '{media_type}' for {jellyfin_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting audio codec for {poster_path}: {e}", exc_info=True)
            # Fallback to demo data on error
            self.logger.info("Falling back to demo data due to error")
            return self._get_demo_audio_codec(poster_path)
    
    def _extract_jellyfin_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract Jellyfin ID from cached filename like jellyfin_0c2379d5d4fa0591f9ec64c9866b40f3_11a6b644.jpg or resized_jellyfin_..."""
        try:
            # Handle both original and resized filenames
            if filename.startswith('resized_jellyfin_'):
                # Remove 'resized_' prefix and process as normal jellyfin file
                filename = filename[8:]  # Remove 'resized_'
            
            if filename.startswith('jellyfin_'):
                # Remove extension and jellyfin_ prefix
                base_name = Path(filename).stem
                parts = base_name.split('_')
                
                # Format: jellyfin_<32-char-hex-id>_<8-char-uuid>
                if len(parts) == 3 and parts[0] == 'jellyfin':
                    jellyfin_id = parts[1]
                    if len(jellyfin_id) == 32:  # Jellyfin IDs are 32 character hex strings
                        self.logger.debug(f"Extracted Jellyfin ID from filename: {jellyfin_id}")
                        return jellyfin_id
                
            self.logger.warning(f"Could not extract Jellyfin ID from filename: {filename}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting Jellyfin ID from filename {filename}: {e}")
            return None
    
    def _get_demo_audio_codec(self, poster_path: str) -> str:
        """Get demo audio codec as fallback (consistent per poster)"""
        import hashlib
        
        # Create a hash of the poster filename for consistent but varied results
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # List of common audio codecs to rotate through
        demo_codecs = [
            "DTS-HD MA",
            "TRUEHD ATMOS", 
            "DOLBY DIGITAL PLUS",
            "DTS-X",
            "TRUEHD",
            "ATMOS"
        ]
        
        # Select codec based on hash (consistent for same poster)
        selected_codec = demo_codecs[hash_value % len(demo_codecs)]
        
        self.logger.debug(f"Demo audio codec for {poster_name}: {selected_codec}")
        return selected_codec
    
    async def _apply_audio_badge(
        self,
        poster_path: str,
        codec_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Apply audio badge to poster using v1 logic with v2 output path control"""
        try:
            # Import v1 badge creation functions
            import sys
            import shutil
            from PIL import Image
            sys.path.append("E:/programming/aphrodite")
            
            from aphrodite_helpers.badge_components.badge_generator import create_badge
            from aphrodite_helpers.badge_components.badge_applicator import calculate_dynamic_padding
            
            # Create audio badge using v1 logic
            self.logger.debug(f"Creating badge with settings - Badge Size: {settings.get('General', {}).get('general_badge_size')}, Image Badges: {settings.get('ImageBadges', {}).get('enable_image_badges')}, Use Dynamic: {settings.get('General', {}).get('use_dynamic_sizing')}")
            
            # Log the exact settings being passed to create_badge
            self.logger.debug(f"Full settings being passed to create_badge: {json.dumps(settings, indent=2)}")
            
            # Modify settings to respect database settings properly
            modified_settings = settings.copy()
            
            # Handle badge sizing based on what the user actually wants
            general_settings = modified_settings.get('General', {})
            badge_size = general_settings.get('general_badge_size', 100)
            use_dynamic = general_settings.get('use_dynamic_sizing', True)
            
            self.logger.debug(f"Original settings - Badge size: {badge_size}, Dynamic sizing: {use_dynamic}")
            
            # The v1 code treats general_badge_size as pixel dimensions for square badges
            # Most users probably want dynamic sizing (badges that fit their content)
            # Only disable dynamic sizing if the user set a VERY different size from default
            
            if badge_size == 100:  # Default size
                # Keep dynamic sizing for default
                general_settings['use_dynamic_sizing'] = True
                self.logger.debug("Using dynamic sizing for default badge size")
            elif badge_size < 150:  # Small to medium custom sizes (50-149)
                # Keep dynamic sizing but these will affect minimum dimensions
                general_settings['use_dynamic_sizing'] = True
                self.logger.debug(f"Using dynamic sizing with custom base size: {badge_size}")
            else:  # Large sizes (150+) - user probably wants fixed large badges
                # Use fixed sizing but limit to reasonable maximum
                max_reasonable_size = 120  # Reasonable max for square badges
                if badge_size > max_reasonable_size:
                    general_settings['general_badge_size'] = max_reasonable_size
                    self.logger.debug(f"Limited large badge size from {badge_size} to {max_reasonable_size}")
                general_settings['use_dynamic_sizing'] = False
                self.logger.debug(f"Using fixed sizing for large badge: {general_settings['general_badge_size']}")
            
            # Force image badges setting by modifying the use_image parameter
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', True)
            use_image_for_badge = image_badges_enabled
            
            self.logger.debug(f"Final settings - Badge size: {general_settings.get('general_badge_size')}, Dynamic sizing: {general_settings.get('use_dynamic_sizing')}, Will use images: {use_image_for_badge}")
            
            audio_badge = create_badge(modified_settings, codec_data, use_image=use_image_for_badge)
            if not audio_badge:
                self.logger.error("Failed to create audio badge")
                return None
            
            self.logger.debug(f"Created badge dimensions: {audio_badge.size} (Dynamic: {general_settings.get('use_dynamic_sizing')})")
            
            # Determine the final output path
            if output_path:
                final_output_path = output_path
            else:
                # Generate output path in v2 preview directory
                poster_name = Path(poster_path).name
                final_output_path = f"E:/programming/aphrodite/aphrodite-v2/api/static/preview/{poster_name}"
            
            # Ensure output directory exists
            output_dir = Path(final_output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Apply badge using v2-compatible logic (based on v1 badge_applicator.py)
            poster = Image.open(poster_path).convert("RGBA")
            
            # Get badge position from settings
            position = settings.get('General', {}).get('general_badge_position', 'top-right')
            base_edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
            
            # Calculate dynamic padding based on aspect ratio
            edge_padding = calculate_dynamic_padding(poster.width, poster.height, base_edge_padding)
            
            # Calculate position coordinates
            if position == 'top-left':
                coords = (edge_padding, edge_padding)
            elif position == 'top-right':
                coords = (poster.width - audio_badge.width - edge_padding, edge_padding)
            elif position == 'bottom-left':
                coords = (edge_padding, poster.height - audio_badge.height - edge_padding)
            elif position == 'bottom-right':
                coords = (poster.width - audio_badge.width - edge_padding, poster.height - audio_badge.height - edge_padding)
            elif position == 'top-center':
                coords = ((poster.width - audio_badge.width) // 2, edge_padding)
            elif position == 'center-left':
                coords = (edge_padding, (poster.height - audio_badge.height) // 2)
            elif position == 'center':
                coords = ((poster.width - audio_badge.width) // 2, (poster.height - audio_badge.height) // 2)
            elif position == 'center-right':
                coords = (poster.width - audio_badge.width - edge_padding, (poster.height - audio_badge.height) // 2)
            elif position == 'bottom-center':
                coords = ((poster.width - audio_badge.width) // 2, poster.height - audio_badge.height - edge_padding)
            elif position == 'bottom-right-flush':
                coords = (poster.width - audio_badge.width, poster.height - audio_badge.height)
            else:
                # Default to top-right
                coords = (poster.width - audio_badge.width - edge_padding, edge_padding)
            
            # Paste the badge onto the poster
            poster.paste(audio_badge, coords, audio_badge)
            
            # Save the modified poster to the specified output path
            poster.convert("RGB").save(final_output_path, "JPEG")
            
            self.logger.debug(f"Successfully applied audio badge: {final_output_path}")
            return final_output_path
                
        except Exception as e:
            self.logger.error(f"Error applying audio badge: {e}", exc_info=True)
            return None
