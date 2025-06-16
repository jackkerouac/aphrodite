"""
Poster Resizer

Standardizes poster dimensions to 1,000px width with appropriate aspect ratio height
before badge processing begins. This ensures consistent badge sizing across all posters.
"""

from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
import shutil

from aphrodite_logging import get_logger


class PosterResizer:
    """Handles poster resizing to standardized dimensions"""
    
    STANDARD_WIDTH = 1000  # Standard width for all posters
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.resizer", service="badge")
    
    def resize_poster(self, input_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Resize poster to standard 1,000px width with maintained aspect ratio.
        
        Args:
            input_path: Path to original poster
            output_path: Path for resized poster (optional, defaults to temp location)
            
        Returns:
            Path to resized poster or None if failed
        """
        try:
            input_path_obj = Path(input_path)
            
            # Validate input
            if not input_path_obj.exists():
                self.logger.error(f"Input poster not found: {input_path}")
                return None
            
            # Load and validate image
            try:
                image = Image.open(input_path).convert("RGB")
                original_width, original_height = image.size
                self.logger.debug(f"Original dimensions: {original_width}x{original_height}")
            except Exception as e:
                self.logger.error(f"Failed to load image {input_path}: {e}")
                return None
            
            # Check if resizing is needed
            if original_width == self.STANDARD_WIDTH:
                self.logger.debug(f"Poster already at standard width ({self.STANDARD_WIDTH}px), no resize needed")
                # If no resize needed and no specific output path, return original
                if not output_path:
                    return input_path
                # Otherwise copy to output path
                if input_path != output_path:
                    shutil.copy2(input_path, output_path)
                return output_path
            
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = original_height / original_width
            new_width = self.STANDARD_WIDTH
            new_height = int(new_width * aspect_ratio)
            
            self.logger.debug(f"Resizing from {original_width}x{original_height} to {new_width}x{new_height}")
            
            # Resize the image using high-quality resampling
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Determine output path
            if not output_path:
                # Create temp resized version in same directory
                output_path = str(input_path_obj.parent / f"resized_{input_path_obj.name}")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save resized image
            resized_image.save(output_path, "JPEG", quality=95, optimize=True)
            
            self.logger.info(f"Successfully resized poster: {input_path} -> {output_path}")
            self.logger.debug(f"Final dimensions: {new_width}x{new_height}")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error resizing poster {input_path}: {e}", exc_info=True)
            return None
    
    def get_standardized_dimensions(self, original_width: int, original_height: int) -> Tuple[int, int]:
        """
        Calculate standardized dimensions for given original dimensions.
        
        Args:
            original_width: Original poster width
            original_height: Original poster height
            
        Returns:
            Tuple of (new_width, new_height)
        """
        aspect_ratio = original_height / original_width
        new_width = self.STANDARD_WIDTH
        new_height = int(new_width * aspect_ratio)
        return new_width, new_height
    
    def needs_resizing(self, poster_path: str) -> bool:
        """
        Check if poster needs resizing.
        
        Args:
            poster_path: Path to poster file
            
        Returns:
            True if resizing is needed, False otherwise
        """
        try:
            with Image.open(poster_path) as image:
                width, height = image.size
                return width != self.STANDARD_WIDTH
        except Exception as e:
            self.logger.error(f"Error checking poster dimensions {poster_path}: {e}")
            return False
    
    def get_poster_info(self, poster_path: str) -> Optional[dict]:
        """
        Get poster information including dimensions and whether resizing is needed.
        
        Args:
            poster_path: Path to poster file
            
        Returns:
            Dictionary with poster info or None if failed
        """
        try:
            with Image.open(poster_path) as image:
                width, height = image.size
                new_width, new_height = self.get_standardized_dimensions(width, height)
                
                return {
                    "original_dimensions": (width, height),
                    "standardized_dimensions": (new_width, new_height),
                    "needs_resizing": width != self.STANDARD_WIDTH,
                    "aspect_ratio": height / width,
                    "file_size": Path(poster_path).stat().st_size
                }
        except Exception as e:
            self.logger.error(f"Error getting poster info {poster_path}: {e}")
            return None


# Create global instance for easy import
poster_resizer = PosterResizer()
