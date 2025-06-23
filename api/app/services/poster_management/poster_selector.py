"""
Poster Selection Service

Handles random selection of posters from Jellyfin movies library or fallback to originals directory.
"""

import os
import random
import aiohttp
import asyncio
from pathlib import Path
from typing import List, Optional
import tempfile
import uuid

from aphrodite_logging import get_logger
from app.services.jellyfin_service import get_jellyfin_service


class PosterSelector:
    """Service for selecting posters from Jellyfin movies library or originals directory."""
    
    def __init__(self, originals_path: str = None, cache_dir: str = None):
        self.logger = get_logger("aphrodite.poster.selector")
        
        # Default to API static directory if no path provided
        if originals_path is None:
            # Get the API directory path
            api_dir = Path(__file__).parent.parent.parent.parent  # Go up from services/poster_management to api root
            originals_path = api_dir / "static" / "originals"
        
        # Cache directory for downloaded Jellyfin posters
        if cache_dir is None:
            api_dir = Path(__file__).parent.parent.parent.parent
            cache_dir = api_dir / "cache" / "posters"
        
        self.originals_path = Path(originals_path)
        self.cache_dir = Path(cache_dir)
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported image extensions
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        
        # Initialize Jellyfin service
        self.jellyfin_service = get_jellyfin_service()
    
    def _clear_old_cache(self):
        """Clear old cached posters to ensure fresh selection"""
        try:
            if not self.cache_dir.exists():
                return
            
            import time
            current_time = time.time()
            
            # Remove all cached posters older than 5 minutes
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file() and file_path.name.startswith('jellyfin_'):
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > 300:  # 5 minutes
                        try:
                            file_path.unlink()
                            # Also remove metadata file
                            metadata_path = file_path.with_suffix('.meta')
                            if metadata_path.exists():
                                metadata_path.unlink()
                            self.logger.debug(f"Cleared old cached poster: {file_path.name}")
                        except Exception as e:
                            self.logger.warning(f"Failed to clear cache file {file_path.name}: {e}")
        except Exception as e:
            self.logger.warning(f"Error clearing old cache: {e}")

    def get_random_poster(self) -> Optional[str]:
        """
        Select a random poster from Jellyfin movies library or fallback to originals directory.
        
        Returns:
            str: Path to selected poster file, or None if no posters found
        """
        try:
            # First try to get poster from Jellyfin using sync wrapper
            jellyfin_poster = self._get_random_jellyfin_poster_sync()
            if jellyfin_poster:
                return jellyfin_poster
            
            # Fallback to originals directory
            self.logger.info("Falling back to originals directory")
            poster_files = self._get_all_posters()
            
            if not poster_files:
                self.logger.warning("No poster files found in originals directory")
                return None
            
            selected_poster = random.choice(poster_files)
            full_path = str(self.originals_path / selected_poster)
            
            self.logger.info(f"Selected random poster from originals: {selected_poster}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Error selecting random poster: {e}", exc_info=True)
            return None
    
    async def get_random_poster_async(self) -> Optional[str]:
        """
        Async version: Select a random poster from Jellyfin movies library or fallback to originals directory.
        
        Returns:
            str: Path to selected poster file, or None if no posters found
        """
        try:
            # First try to get poster from Jellyfin
            jellyfin_poster = await self._async_get_random_jellyfin_poster()
            if jellyfin_poster:
                return jellyfin_poster
            
            # Fallback to originals directory
            self.logger.info("Falling back to originals directory")
            poster_files = self._get_all_posters()
            
            if not poster_files:
                self.logger.warning("No poster files found in originals directory")
                return None
            
            selected_poster = random.choice(poster_files)
            full_path = str(self.originals_path / selected_poster)
            
            self.logger.info(f"Selected random poster from originals: {selected_poster}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Error selecting random poster: {e}", exc_info=True)
            return None
    
    def _get_random_jellyfin_poster_sync(self) -> Optional[str]:
        """
        Synchronous wrapper for getting a random poster from Jellyfin.
        Handles event loop detection automatically.
        
        Returns:
            str: Path to cached poster file, or None if failed
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, need to run in a new thread
                import concurrent.futures
                
                def run_in_new_loop():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self._async_get_random_jellyfin_poster())
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_new_loop)
                    return future.result(timeout=30)  # 30 second timeout
                    
            except RuntimeError:
                # No event loop running, safe to use asyncio.run()
                return asyncio.run(self._async_get_random_jellyfin_poster())
                
        except Exception as e:
            self.logger.warning(f"Failed to get Jellyfin poster: {e}")
            return None
    
    async def _async_get_random_jellyfin_poster(self) -> Optional[str]:
        """
        Async method to get random poster from Jellyfin.
        
        Returns:
            str: Path to cached poster file, or None if failed
        """
        try:
            # CRITICAL FIX: Force fresh random selection each time
            import random
            import time
            
            # Clear old cached posters to prevent reusing same ones
            self._clear_old_cache()
            
            # Use microsecond-level randomization for better entropy
            random.seed(time.time_ns() + random.randint(1, 1000000))
            self.logger.info("Initializing random poster selection from Jellyfin")
            # Test Jellyfin connection
            connected, message = await self.jellyfin_service.test_connection()
            if not connected:
                self.logger.warning(f"Jellyfin not connected: {message}")
                return None
            
            # Get all libraries
            libraries = await self.jellyfin_service.get_libraries()
            if not libraries:
                self.logger.warning("No Jellyfin libraries found")
                return None
            
            # Find movie libraries (looking for libraries with movie metadata)
            movie_libraries = []
            for lib in libraries:
                # Check if this library has movie metadata by examining its item types
                lib_name = lib.get('Name', '').lower()
                lib_locations = lib.get('Locations', [])
                
                # Simple heuristic: if library name contains 'movie' or has movie-like content
                if 'movie' in lib_name or 'film' in lib_name:
                    movie_libraries.append(lib)
                    self.logger.debug(f"Found movie library: {lib.get('Name')}")
            
            if not movie_libraries:
                # If no explicit movie libraries found, try all libraries
                self.logger.info("No explicit movie libraries found, trying all libraries")
                movie_libraries = libraries
            
            # Try each movie library until we find movies
            for library in movie_libraries:
                library_id = library.get('ItemId') or library.get('Id')
                if not library_id:
                    continue
                
                self.logger.info(f"Checking library: {library.get('Name')} (ID: {library_id})")
                
                # Get items from this library
                items = await self.jellyfin_service.get_library_items(library_id)
                
                # Filter for movie items
                movie_items = [item for item in items if item.get('Type') == 'Movie']
                
                if movie_items:
                    self.logger.info(f"Found {len(movie_items)} movies in library {library.get('Name')}")
                    
                    # CRITICAL FIX: Enhanced randomization to prevent same movie selection
                    import time
                    
                    # Use multiple entropy sources for better randomization
                    current_ns = time.time_ns()
                    library_hash = hash(library.get('Name', ''))
                    items_hash = hash(str([item.get('Id') for item in movie_items[:5]]))
                    
                    # Combine multiple sources of entropy
                    seed_value = current_ns + library_hash + items_hash + len(movie_items)
                    random.seed(seed_value)
                    
                    # Shuffle the list and select to further randomize
                    random.shuffle(movie_items)
                    selected_movie = random.choice(movie_items)
                    movie_id = selected_movie.get('Id')
                    movie_name = selected_movie.get('Name', 'Unknown')
                    
                    self.logger.info(f"Selected random movie: {movie_name} (ID: {movie_id})")
                    
                    # Download poster
                    poster_data = await self.jellyfin_service.download_poster(movie_id)
                    if poster_data:
                        # Save to cache with metadata - use timestamp for uniqueness
                        timestamp = int(time.time_ns() // 1000000)  # Millisecond timestamp
                        cache_filename = f"jellyfin_{movie_id}_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
                        cache_path = self.cache_dir / cache_filename
                        
                        with open(cache_path, 'wb') as f:
                            f.write(poster_data)
                        
                        # Also save metadata file for audio codec detection
                        metadata_path = cache_path.with_suffix('.meta')
                        metadata = {
                            'jellyfin_id': movie_id,
                            'movie_name': movie_name,
                            'library_name': library.get('Name'),
                            'cached_at': str(cache_path.stat().st_mtime)
                        }
                        
                        import json
                        with open(metadata_path, 'w') as f:
                            json.dump(metadata, f)
                        
                        self.logger.info(f"Downloaded and cached poster: {cache_path}")
                        self.logger.debug(f"Saved metadata: {metadata_path}")
                        return str(cache_path)
                    else:
                        self.logger.warning(f"Failed to download poster for movie: {movie_name}")
            
            self.logger.warning("No movies with posters found in any library")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Jellyfin poster: {e}", exc_info=True)
            return None
        finally:
            # CRITICAL FIX: Always clean up Jellyfin session to force fresh connections
            try:
                await self.jellyfin_service.close()
                # Reset the service to force fresh connection next time
                self.jellyfin_service._settings_loaded = False
                self.jellyfin_service.session = None
                self.logger.debug("Cleaned up Jellyfin session and reset connection state")
            except Exception as cleanup_error:
                self.logger.warning(f"Error during Jellyfin cleanup: {cleanup_error}")
    
    def get_all_posters(self) -> List[str]:
        """
        Get list of all available posters from originals directory.
        Note: This method only returns static originals, not Jellyfin posters.
        
        Returns:
            List[str]: List of poster file paths from originals directory
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
        
        self.logger.debug(f"Found {len(poster_files)} poster files in originals directory")
        return poster_files
    
    def cleanup_cached_posters(self, max_age_hours: int = 24) -> int:
        """
        Clean up old cached Jellyfin posters and their metadata files.
        
        Args:
            max_age_hours: Maximum age of cached files to keep (hours)
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            if not self.cache_dir.exists():
                return 0
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file() and file_path.name.startswith('jellyfin_'):
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        # Clean up the poster file
                        file_path.unlink()
                        cleaned_count += 1
                        self.logger.debug(f"Cleaned up old cached poster: {file_path.name}")
                        
                        # Also clean up the corresponding metadata file if it exists
                        metadata_path = file_path.with_suffix('.meta')
                        if metadata_path.exists():
                            metadata_path.unlink()
                            self.logger.debug(f"Cleaned up metadata file: {metadata_path.name}")
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old cached posters")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up cached posters: {e}", exc_info=True)
            return 0
