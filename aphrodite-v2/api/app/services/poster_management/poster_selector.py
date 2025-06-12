"""
Poster Selection Service

Handles random selection of posters from the originals directory.
"""

import os
import random
from pathlib import Path
from typing import List, Optional

from aphrodite_logging import get_logger


class PosterSelector:
    """Service for selecting posters from the originals directory."""
    
    def __init__(self, originals_path: str = None):
        self.logger = get_logger("aphrodite.poster.selector")
        
        # Default to API static directory if no path provided
        if originals_path is None:
            # Get the API directory path
            api_dir = Path(__file__).parent.parent.parent.parent  # Go up from services/poster_management to api root
            originals_path = api_dir / "static" / "originals"
        
        self.originals_path = Path(originals_path)
        
        # Supported image extensions
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    def get_random_poster(self) -> Optional[str]:
        """
        Select a random poster from the originals directory.
        
        Returns:
            str: Path to selected poster file, or None if no posters found
        """
        try:
            poster_files = self._get_all_posters()
            
            if not poster_files:
                self.logger.warning("No poster files found in originals directory")
                return None
            
            selected_poster = random.choice(poster_files)
            full_path = str(self.originals_path / selected_poster)
            
            self.logger.info(f"Selected random poster: {selected_poster}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Error selecting random poster: {e}", exc_info=True)
            return None
    
    def get_all_posters(self) -> List[str]:
        """
        Get list of all available posters.
        
        Returns:
            List[str]: List of poster file paths
        """
        try:
            poster_files = self._get_all_posters()
            return [str(self.originals_path / f) for f in poster_files]
        except Exception as e:
            self.logger.error(f"Error getting all posters: {e}", exc_info=True)
            return []
    
    def get_poster_count(self) -> int:
        """
        Get total count of available posters.
        
        Returns:
            int: Number of available posters
        """
        try:
            return len(self._get_all_posters())
        except Exception as e:
            self.logger.error(f"Error counting posters: {e}", exc_info=True)
            return 0
    
    def poster_exists(self, poster_path: str) -> bool:
        """
        Check if a specific poster file exists.
        
        Args:
            poster_path: Path to poster file
            
        Returns:
            bool: True if poster exists, False otherwise
        """
        try:
            if Path(poster_path).is_absolute():
                return Path(poster_path).exists()
            else:
                return (self.originals_path / poster_path).exists()
        except Exception as e:
            self.logger.error(f"Error checking poster existence: {e}", exc_info=True)
            return False
    
    def _get_all_posters(self) -> List[str]:
        """
        Get list of all poster files from originals directory.
        
        Returns:
            List[str]: List of poster filenames
        """
        if not self.originals_path.exists():
            self.logger.error(f"Originals directory does not exist: {self.originals_path}")
            return []
        
        poster_files = []
        
        for file_path in self.originals_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                poster_files.append(file_path.name)
        
        self.logger.debug(f"Found {len(poster_files)} poster files")
        return poster_files
