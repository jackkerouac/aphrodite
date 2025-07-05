"""
Audio detection caching system.
Direct adaptation of successful ResolutionCache.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path
from aphrodite_logging import get_logger

from .audio_types import AudioInfo


class AudioCache:
    """
    Audio detection caching system.
    Direct adaptation of successful ResolutionCache.
    """
    
    def __init__(self):
        self.logger = get_logger("aphrodite.audio.cache", service="badge")
        
        # In-memory cache for active session
        self.series_cache: Dict[str, Dict] = {}
        
        # Cache configuration
        self.cache_ttl = timedelta(hours=24)  # 24-hour TTL
        self.max_cache_size = 1000  # Limit memory usage
        
        # Persistent cache file (optional)
        self.cache_file = Path("/app/data/cache/audio/audio_cache.json")
        
        # Ensure cache directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load persistent cache on startup
        self._load_persistent_cache()
    
    def get_series_audio(self, series_id: str) -> Optional[AudioInfo]:
        """Get cached audio info for series"""
        try:
            if series_id not in self.series_cache:
                return None
            
            cache_entry = self.series_cache[series_id]
            
            # Check if cache entry is still valid
            if not self._is_cache_valid(cache_entry):
                self.logger.debug(f"Cache expired for series: {series_id}")
                del self.series_cache[series_id]
                return None
            
            # Return cached audio info
            audio_data = cache_entry['audio_info']
            audio_info = AudioInfo.from_dict(audio_data)
            
            self.logger.debug(f"Cache hit for series: {series_id}")
            return audio_info
            
        except Exception as e:
            self.logger.warning(f"Cache retrieval error for {series_id}: {e}")
            return None
    
    def cache_series_audio(self, series_id: str, audio_info: AudioInfo) -> None:
        """Cache audio info for series"""
        try:
            # Check cache size limit
            if len(self.series_cache) >= self.max_cache_size:
                self._cleanup_old_entries()
            
            # Create cache entry
            cache_entry = {
                'audio_info': audio_info.to_dict(),
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + self.cache_ttl).isoformat()
            }
            
            self.series_cache[series_id] = cache_entry
            
            self.logger.debug(f"Cached audio for series: {series_id}")
            
            # Optionally save to persistent cache
            self._save_persistent_cache()
            
        except Exception as e:
            self.logger.warning(f"Cache storage error for {series_id}: {e}")
    
    def invalidate_series(self, series_id: str) -> None:
        """Invalidate cached audio for specific series"""
        if series_id in self.series_cache:
            del self.series_cache[series_id]
            self.logger.debug(f"Invalidated cache for series: {series_id}")
            self._save_persistent_cache()
    
    def clear_cache(self) -> None:
        """Clear all cached audio data"""
        self.series_cache.clear()
        
        # Remove persistent cache file
        if self.cache_file.exists():
            self.cache_file.unlink()
        
        self.logger.info("Audio cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        valid_entries = 0
        expired_entries = 0
        
        for cache_entry in self.series_cache.values():
            if self._is_cache_valid(cache_entry):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.series_cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600,
            'max_cache_size': self.max_cache_size,
            'cache_file_exists': self.cache_file.exists()
        }
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        try:
            expires_at_str = cache_entry.get('expires_at')
            if not expires_at_str:
                return False
            
            expires_at = datetime.fromisoformat(expires_at_str)
            return datetime.now() < expires_at
            
        except Exception:
            return False
    
    def _cleanup_old_entries(self) -> None:
        """Remove expired cache entries"""
        expired_keys = []
        
        for series_id, cache_entry in self.series_cache.items():
            if not self._is_cache_valid(cache_entry):
                expired_keys.append(series_id)
        
        for key in expired_keys:
            del self.series_cache[key]
        
        self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _load_persistent_cache(self) -> None:
        """Load cache from persistent storage"""
        try:
            if not self.cache_file.exists():
                return
            
            with open(self.cache_file, 'r') as f:
                persistent_cache = json.load(f)
            
            # Load valid entries only
            loaded_count = 0
            for series_id, cache_entry in persistent_cache.items():
                if self._is_cache_valid(cache_entry):
                    self.series_cache[series_id] = cache_entry
                    loaded_count += 1
            
            self.logger.debug(f"Loaded {loaded_count} valid cache entries from persistent storage")
            
        except Exception as e:
            self.logger.warning(f"Failed to load persistent cache: {e}")
    
    def _save_persistent_cache(self) -> None:
        """Save cache to persistent storage"""
        try:
            # Only save valid entries
            valid_cache = {}
            for series_id, cache_entry in self.series_cache.items():
                if self._is_cache_valid(cache_entry):
                    valid_cache[series_id] = cache_entry
            
            with open(self.cache_file, 'w') as f:
                json.dump(valid_cache, f, indent=2)
            
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Saved {len(valid_cache)} cache entries to persistent storage")
            
        except Exception as e:
            self.logger.warning(f"Failed to save persistent cache: {e}")
