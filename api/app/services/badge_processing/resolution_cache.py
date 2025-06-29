"""
Resolution caching system for improved performance.
Caches series resolution results to avoid repeated API calls.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path
from aphrodite_logging import get_logger

from .resolution_types import ResolutionInfo


class ResolutionCache:
    """
    In-memory and persistent caching for series resolution results.
    Significantly improves performance for repeated series processing.
    """
    
    def __init__(self, cache_ttl_hours: int = 24, cache_file: str = "cache/resolution_cache.json"):
        self.logger = get_logger("aphrodite.resolution.cache", service="badge")
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache_file = Path(cache_file)
        
        # In-memory cache
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "cache_size": 0,
            "last_cleanup": datetime.now()
        }
        
        # Load persistent cache
        self._load_persistent_cache()
    
    def get_cached_resolution(self, series_id: str) -> Optional[ResolutionInfo]:
        """
        Get cached series resolution if available and valid.
        
        Args:
            series_id: Series ID to look up
            
        Returns:
            Cached ResolutionInfo or None if not cached/expired
        """
        try:
            cache_entry = self._memory_cache.get(series_id)
            
            if not cache_entry:
                self._stats["misses"] += 1
                return None
            
            # Check if cache entry is still valid
            if not self._is_cache_valid(cache_entry):
                self.logger.debug(f"Cache entry expired for series: {series_id}")
                self._remove_cache_entry(series_id)
                self._stats["misses"] += 1
                return None
            
            # Return cached resolution
            resolution_data = cache_entry["resolution_data"]
            resolution_info = ResolutionInfo.from_dict(resolution_data)
            
            self._stats["hits"] += 1
            self.logger.debug(f"Cache hit for series {series_id}: {resolution_info}")
            
            return resolution_info
            
        except Exception as e:
            self.logger.warning(f"Cache retrieval error for series {series_id}: {e}")
            self._stats["misses"] += 1
            return None
    
    def cache_series_resolution(self, series_id: str, resolution: ResolutionInfo):
        """
        Cache series resolution with timestamp.
        
        Args:
            series_id: Series ID to cache
            resolution: Resolution info to store
        """
        try:
            cache_entry = {
                "resolution_data": resolution.to_dict(),
                "cached_at": datetime.now().isoformat(),
                "ttl_hours": self.cache_ttl.total_seconds() / 3600
            }
            
            self._memory_cache[series_id] = cache_entry
            self._stats["cache_size"] = len(self._memory_cache)
            
            self.logger.debug(f"Cached resolution for series {series_id}: {resolution}")
            
            # Periodic cleanup and persistence
            self._maybe_cleanup_and_persist()
            
        except Exception as e:
            self.logger.error(f"Cache storage error for series {series_id}: {e}")
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid based on TTL"""
        try:
            cached_at = datetime.fromisoformat(cache_entry["cached_at"])
            age = datetime.now() - cached_at
            return age < self.cache_ttl
        except Exception:
            return False
    
    def _remove_cache_entry(self, series_id: str):
        """Remove expired cache entry"""
        if series_id in self._memory_cache:
            del self._memory_cache[series_id]
            self._stats["cache_size"] = len(self._memory_cache)
    
    def _load_persistent_cache(self):
        """Load cache from persistent storage"""
        try:
            if not self.cache_file.exists():
                self.logger.debug("No persistent cache file found")
                return
            
            # Ensure cache directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'r') as f:
                persistent_data = json.load(f)
            
            # Load and validate entries
            loaded_count = 0
            for series_id, cache_entry in persistent_data.items():
                if self._is_cache_valid(cache_entry):
                    self._memory_cache[series_id] = cache_entry
                    loaded_count += 1
            
            self._stats["cache_size"] = len(self._memory_cache)
            self.logger.info(f"Loaded {loaded_count} valid cache entries from persistent storage")
            
        except Exception as e:
            self.logger.warning(f"Failed to load persistent cache: {e}")
    
    def _save_persistent_cache(self):
        """Save cache to persistent storage"""
        try:
            # Ensure cache directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Only save valid entries
            valid_entries = {
                series_id: entry 
                for series_id, entry in self._memory_cache.items()
                if self._is_cache_valid(entry)
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(valid_entries, f, indent=2)
            
            self.logger.debug(f"Saved {len(valid_entries)} cache entries to persistent storage")
            
        except Exception as e:
            self.logger.error(f"Failed to save persistent cache: {e}")
    
    def _maybe_cleanup_and_persist(self):
        """Perform periodic cleanup and persistence"""
        now = datetime.now()
        
        # Cleanup every hour
        if now - self._stats["last_cleanup"] > timedelta(hours=1):
            self._cleanup_expired_entries()
            self._save_persistent_cache()
            self._stats["last_cleanup"] = now
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from memory cache"""
        expired_keys = [
            series_id for series_id, entry in self._memory_cache.items()
            if not self._is_cache_valid(entry)
        ]
        
        for series_id in expired_keys:
            del self._memory_cache[series_id]
        
        self._stats["cache_size"] = len(self._memory_cache)
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear_cache(self):
        """Clear all cached data"""
        self._memory_cache.clear()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "cache_size": 0,
            "last_cleanup": datetime.now()
        }
        
        # Remove persistent cache file
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception as e:
            self.logger.warning(f"Failed to remove persistent cache file: {e}")
        
        self.logger.info("Resolution cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate_percent": round(hit_rate, 2),
            "total_hits": self._stats["hits"],
            "total_misses": self._stats["misses"],
            "cache_size": self._stats["cache_size"],
            "ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "last_cleanup": self._stats["last_cleanup"].isoformat()
        }
    
    def update_ttl(self, hours: int):
        """Update cache TTL"""
        self.cache_ttl = timedelta(hours=hours)
        self.logger.info(f"Cache TTL updated to {hours} hours")
    
    def get_cache_coverage_report(self) -> Dict[str, Any]:
        """Generate cache coverage report for diagnostics"""
        now = datetime.now()
        age_distribution = {"fresh": 0, "moderate": 0, "old": 0}
        
        for entry in self._memory_cache.values():
            try:
                cached_at = datetime.fromisoformat(entry["cached_at"])
                age = now - cached_at
                
                if age < timedelta(hours=6):
                    age_distribution["fresh"] += 1
                elif age < timedelta(hours=12):
                    age_distribution["moderate"] += 1
                else:
                    age_distribution["old"] += 1
            except Exception:
                continue
        
        return {
            "total_cached_series": len(self._memory_cache),
            "age_distribution": age_distribution,
            "cache_file_exists": self.cache_file.exists(),
            "cache_file_size_kb": self.cache_file.stat().st_size // 1024 if self.cache_file.exists() else 0
        }
