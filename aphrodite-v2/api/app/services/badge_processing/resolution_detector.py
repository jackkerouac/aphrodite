"""
Resolution Detection Helper

Handles resolution detection from Jellyfin metadata for the resolution badge processor.
Separated for modularity and reusability.
"""

from typing import Optional
from pathlib import Path
import json
import hashlib

from aphrodite_logging import get_logger


class ResolutionDetector:
    """Helper class for detecting resolution information from various sources"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.resolution.detector", service="badge")
    
    async def get_resolution_info(self, poster_path: str) -> Optional[str]:
        """Get real resolution info from Jellyfin metadata"""
        try:
            # Check if this is a cached Jellyfin poster
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
                self.logger.debug("Not a Jellyfin cached poster, no resolution info available")
                return None
            
            if not jellyfin_id:
                self.logger.warning("Could not extract Jellyfin ID from poster path")
                return None
            
            self.logger.debug(f"Extracting resolution info for Jellyfin ID: {jellyfin_id}")
            
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
                # For movies: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"Movie resolution for {jellyfin_id}: {resolution}")
                return resolution
            
            elif media_type in ['Series', 'Season']:
                # For TV: sample first 5 episodes for dominant resolution
                resolution = await jellyfin_service.get_tv_series_dominant_resolution(jellyfin_id)
                self.logger.debug(f"TV series dominant resolution for {jellyfin_id}: {resolution}")
                return resolution
            
            elif media_type == 'Episode':
                # For individual episodes: get resolution directly
                resolution = await jellyfin_service.get_video_resolution_info(media_item)
                self.logger.debug(f"Episode resolution for {jellyfin_id}: {resolution}")
                return resolution
            
            else:
                self.logger.warning(f"Unsupported media type '{media_type}' for {jellyfin_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting resolution info for {poster_path}: {e}", exc_info=True)
            # Fallback to demo data on error
            self.logger.info("Falling back to demo data due to error")
            return self.get_demo_resolution(poster_path)
    
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
    
    def get_demo_resolution(self, poster_path: str) -> str:
        """Get demo resolution as fallback (consistent per poster)"""
        # Create a hash of the poster filename for consistent but varied results
        poster_name = Path(poster_path).stem
        hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
        
        # List of common resolutions to rotate through
        demo_resolutions = [
            "4K HDR",
            "4K DV", 
            "4K",
            "1080p HDR",
            "1080p",
            "720p"
        ]
        
        # Select resolution based on hash (consistent for same poster)
        selected_resolution = demo_resolutions[hash_value % len(demo_resolutions)]
        
        self.logger.debug(f"Demo resolution for {poster_name}: {selected_resolution}")
        return selected_resolution


# Global detector instance for reuse
_resolution_detector: Optional[ResolutionDetector] = None

def get_resolution_detector() -> ResolutionDetector:
    """Get global resolution detector instance"""
    global _resolution_detector
    if _resolution_detector is None:
        _resolution_detector = ResolutionDetector()
    return _resolution_detector
