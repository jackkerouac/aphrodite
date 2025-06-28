"""
Storage Management Service

Handles file operations for processed posters and preview outputs.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
import json
from datetime import datetime

from aphrodite_logging import get_logger


class StorageManager:
    """Service for managing poster file storage and operations."""
    
    def __init__(self, 
                 processed_path: str = None,
                 preview_path: str = None,
                 cache_path: str = None):
        self.logger = get_logger("aphrodite.storage.manager")
        
        # Default to API static directories if no paths provided
        if processed_path is None or preview_path is None or cache_path is None:
            # Get the API directory path
            api_dir = Path(__file__).parent.parent.parent.parent  # Go up from services/poster_management to api root
            
            if processed_path is None:
                processed_path = api_dir / "static" / "processed"
            if preview_path is None:
                preview_path = api_dir / "static" / "preview"
            if cache_path is None:
                cache_path = api_dir / "cache" / "posters"
        
        self.processed_path = Path(processed_path)
        self.preview_path = Path(preview_path)
        self.cache_path = Path(cache_path)
        
        # Ensure directories exist
        self._ensure_directories()
    
    def create_preview_output_path(self, source_poster: str) -> str:
        """
        Create a unique output path for preview generation.
        
        Args:
            source_poster: Path to source poster file
            
        Returns:
            str: Path for preview output file
        """
        try:
            source_path = Path(source_poster)
            
            # Generate unique filename for preview
            unique_id = str(uuid.uuid4())[:8]
            preview_filename = f"preview_{unique_id}_{source_path.name}"
            
            output_path = self.preview_path / preview_filename
            
            self.logger.info(f"Created preview output path: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating preview output path: {e}", exc_info=True)
            # Fallback to temp file
            return str(self.preview_path / f"preview_temp_{uuid.uuid4()}.jpg")
    
    def create_chained_preview_path(self, current_path: str, badge_type: str) -> str:
        """
        Create a new preview path for badge chaining while maintaining preview directory structure.
        
        Args:
            current_path: Current poster path in the processing chain
            badge_type: Type of badge being applied (for debugging)
            
        Returns:
            str: New path for the next step in the chain
        """
        try:
            current_file = Path(current_path)
            
            # Always ensure we're working in the preview directory
            if "preview" not in str(current_file.parent):
                # If not in preview directory, move to preview directory
                unique_id = str(uuid.uuid4())[:8]
                if current_file.name.startswith("jellyfin_"):
                    # Extract the original filename for consistency
                    new_filename = f"preview_{unique_id}_{current_file.name}"
                else:
                    new_filename = f"preview_{unique_id}_{badge_type}_{current_file.name}"
                
                output_path = self.preview_path / new_filename
            else:
                # Already in preview directory, create a new variant
                unique_id = str(uuid.uuid4())[:8]
                stem = current_file.stem
                extension = current_file.suffix
                
                # Check if it already has preview_ prefix
                if stem.startswith("preview_"):
                    new_filename = f"{stem}_{badge_type}_{unique_id}{extension}"
                else:
                    new_filename = f"preview_{unique_id}_{badge_type}_{stem}{extension}"
                
                output_path = self.preview_path / new_filename
            
            self.logger.debug(f"Created chained preview path for {badge_type}: {current_path} -> {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating chained preview path: {e}", exc_info=True)
            # Fallback
            return str(self.preview_path / f"preview_chain_{uuid.uuid4()}.jpg")
    
    def create_processed_output_path(self, source_poster: str, job_id: str = None) -> str:
        """
        Create output path for processed poster.
        
        Args:
            source_poster: Path to source poster file
            job_id: Optional job ID for organizing outputs
            
        Returns:
            str: Path for processed output file
        """
        try:
            source_path = Path(source_poster)
            
            if job_id:
                # Organize by job ID
                job_dir = self.processed_path / job_id
                job_dir.mkdir(exist_ok=True)
                output_path = job_dir / f"processed_{source_path.name}"
            else:
                # Direct to processed directory
                output_path = self.processed_path / f"processed_{source_path.name}"
            
            self.logger.info(f"Created processed output path: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating processed output path: {e}", exc_info=True)
            # Fallback to temp file
            return str(self.processed_path / f"processed_temp_{uuid.uuid4()}.jpg")
    
    def copy_poster_for_processing(self, source_poster: str, destination: str) -> bool:
        """
        Copy poster to processing location.
        
        Args:
            source_poster: Path to source poster
            destination: Path to destination
            
        Returns:
            bool: True if copy successful, False otherwise
        """
        try:
            source_path = Path(source_poster)
            dest_path = Path(destination)
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            self.logger.info(f"Copied poster from {source_path} to {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying poster: {e}", exc_info=True)
            return False
    
    def cleanup_preview_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old preview files.
        
        Args:
            max_age_hours: Maximum age of files to keep (hours)
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            if not self.preview_path.exists():
                return 0
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            
            for file_path in self.preview_path.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
                        self.logger.debug(f"Cleaned up old preview file: {file_path.name}")
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old preview files")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up preview files: {e}", exc_info=True)
            return 0
    
    def get_file_url(self, file_path: str, base_url: str = "/api/v1/static") -> str:
        """
        Convert file path to accessible URL.
        
        Args:
            file_path: Local file path
            base_url: Base URL for static files
            
        Returns:
            str: Accessible URL for file
        """
        try:
            path_obj = Path(file_path)
            
            # CRITICAL FIX: Handle both preview and static directory structures
            path_parts = path_obj.parts
            static_index = None
            
            # Look for 'static' in the path
            for i, part in enumerate(path_parts):
                if part == "static":
                    static_index = i
                    break
            
            if static_index is not None:
                # Get all parts after 'static' 
                relative_parts = path_parts[static_index + 1:]
                relative_path = "/".join(relative_parts)
                
                # For preview files, ensure proper URL structure
                if "preview" in relative_parts:
                    # Already has preview in path structure
                    url = f"{base_url}/{relative_path}"
                else:
                    # Assume it's a preview file that should be in preview directory
                    url = f"{base_url}/preview/{path_obj.name}"
            else:
                # Fallback: assume it's a preview file
                url = f"{base_url}/preview/{path_obj.name}"
            
            self.logger.debug(f"Generated URL for {file_path}: {url}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error generating file URL: {e}", exc_info=True)
            # Fallback URL
            return f"{base_url}/preview/{Path(file_path).name}"
    
    def cache_original_poster(self, poster_data: bytes, jellyfin_id: str) -> str:
        """
        Cache original poster before processing.
        
        Args:
            poster_data: Raw poster image bytes
            jellyfin_id: Jellyfin item ID
            
        Returns:
            str: Path to cached poster file
        """
        try:
            # Generate unique filename for cached original
            unique_id = str(uuid.uuid4())[:8]
            cache_filename = f"jellyfin_{jellyfin_id}_{unique_id}.jpg"
            cache_file_path = self.cache_path / cache_filename
            
            # Save the original poster data
            with open(cache_file_path, 'wb') as f:
                f.write(poster_data)
            
            # Create metadata file
            meta_filename = f"jellyfin_{jellyfin_id}_{unique_id}.meta"
            meta_file_path = self.cache_path / meta_filename
            
            metadata = {
                "jellyfin_id": jellyfin_id,
                "cached_at": datetime.now().isoformat(),
                "original_size": len(poster_data),
                "cache_filename": cache_filename
            }
            
            with open(meta_file_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Cached original poster for {jellyfin_id}: {cache_filename}")
            return str(cache_file_path)
            
        except Exception as e:
            self.logger.error(f"Error caching original poster: {e}", exc_info=True)
            raise
    
    def get_cached_original(self, jellyfin_id: str) -> Optional[str]:
        """
        Get cached original poster path for a Jellyfin item.
        
        Args:
            jellyfin_id: Jellyfin item ID
            
        Returns:
            Optional[str]: Path to cached poster if found, None otherwise
        """
        try:
            # Look for cached poster using jellyfin_id pattern
            poster_pattern = f"jellyfin_{jellyfin_id}_*.jpg"
            cached_posters = list(self.cache_path.glob(poster_pattern))
            
            if cached_posters:
                cached_poster = cached_posters[0]  # Use first match
                if cached_poster.exists() and cached_poster.is_file():
                    self.logger.debug(f"Found cached original for {jellyfin_id}: {cached_poster.name}")
                    return str(cached_poster)
            
            self.logger.debug(f"No cached original found for {jellyfin_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cached original: {e}", exc_info=True)
            return None
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        try:
            self.processed_path.mkdir(parents=True, exist_ok=True)
            self.preview_path.mkdir(parents=True, exist_ok=True)
            self.cache_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug(f"Ensured directories exist: {self.processed_path}, {self.preview_path}, {self.cache_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating directories: {e}", exc_info=True)
