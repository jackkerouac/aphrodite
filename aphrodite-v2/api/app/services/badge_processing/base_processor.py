"""
Base Badge Processor

Abstract base class for all badge processors with common functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from aphrodite_logging import get_logger
from .types import PosterResult


class BaseBadgeProcessor(ABC):
    """Base class for all badge processors"""
    
    def __init__(self, badge_type: str):
        self.badge_type = badge_type
        self.logger = get_logger(f"aphrodite.badge.{badge_type}", service="badge")
    
    @abstractmethod
    async def process_single(
        self, 
        poster_path: str, 
        output_path: Optional[str] = None,
        use_demo_data: bool = False
    ) -> PosterResult:
        """Process a single poster with this badge type"""
        pass
    
    @abstractmethod
    async def process_bulk(
        self,
        poster_paths: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False
    ) -> List[PosterResult]:
        """Process multiple posters with this badge type"""
        pass
    
    def validate_poster_path(self, poster_path: str) -> bool:
        """Validate that poster path exists and is a valid image"""
        try:
            path = Path(poster_path)
            
            # Check if file exists
            if not path.exists():
                self.logger.warning(f"Poster file not found: {poster_path}")
                return False
            
            # Check if it's a file
            if not path.is_file():
                self.logger.warning(f"Poster path is not a file: {poster_path}")
                return False
            
            # Check file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
            if path.suffix.lower() not in valid_extensions:
                self.logger.warning(f"Invalid image extension: {path.suffix}")
                return False
            
            # Try to verify it's a valid image
            try:
                from PIL import Image
                with Image.open(poster_path) as img:
                    img.verify()
                return True
            except Exception as e:
                self.logger.warning(f"Invalid image file: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating poster path: {e}")
            return False
    
    def ensure_output_directory(self, output_path: str) -> bool:
        """Ensure output directory exists"""
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {e}")
            return False
    
    def generate_output_path(self, poster_path: str, suffix: str = None) -> str:
        """Generate output path for processed poster"""
        path = Path(poster_path)
        
        if suffix:
            stem = f"{path.stem}_{suffix}"
        else:
            stem = f"{path.stem}_{self.badge_type}"
        
        return str(path.parent / f"{stem}{path.suffix}")
    
    async def verify_result(self, result_path: str) -> bool:
        """Verify that the processing result is valid"""
        try:
            if not Path(result_path).exists():
                self.logger.error(f"Result file does not exist: {result_path}")
                return False
            
            # Verify it's a valid image
            try:
                from PIL import Image
                with Image.open(result_path) as img:
                    img.verify()
                return True
            except Exception as e:
                self.logger.error(f"Invalid result image: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying result: {e}")
            return False
