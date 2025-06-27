"""
V2 Awards Data Fetcher

Pure V2 awards data collection - no V1 dependencies.
Handles awards detection from metadata and demo generation.
"""

from typing import Dict, Any, Optional
import hashlib
from pathlib import Path

from aphrodite_logging import get_logger


class V2AwardsDataFetcher:
    """Pure V2 awards data collection"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.awards.fetcher.v2", service="badge")
    
    async def get_awards_for_media(self, jellyfin_id: str) -> Optional[str]:
        """Get awards data for media using pure V2 methods"""
        try:
            self.logger.info(f"🏆 [V2 AWARDS FETCHER] Getting awards for: {jellyfin_id}")
            
            # Get media metadata from Jellyfin
            media_metadata = await self._get_jellyfin_metadata(jellyfin_id)
            if not media_metadata:
                self.logger.warning(f"⚠️ [V2 AWARDS FETCHER] No metadata found for: {jellyfin_id}")
                return None
            
            # Extract basic info for awards detection
            title = media_metadata.get("Name", "")
            year = media_metadata.get("ProductionYear")
            media_type = media_metadata.get("Type", "").lower()
            provider_ids = media_metadata.get("ProviderIds", {})
            
            self.logger.debug(f"🎬 [V2 AWARDS FETCHER] Media: {title} ({year}) - Type: {media_type}")
            
            # Detect awards from metadata
            awards = await self._detect_awards_from_metadata(
                title, year, provider_ids.get("Tmdb"), 
                provider_ids.get("Imdb"), media_type
            )
            
            if awards:
                self.logger.info(f"🏆 [V2 AWARDS FETCHER] Awards detected: {awards}")
            else:
                self.logger.debug("🚫 [V2 AWARDS FETCHER] No awards detected")
            
            return awards
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error getting awards: {e}", exc_info=True)
            return None
    
    def get_demo_awards(self, poster_path: str) -> Optional[str]:
        """Generate consistent demo awards data"""
        try:
            self.logger.debug(f"🎭 [V2 AWARDS FETCHER] Generating demo awards for: {poster_path}")
            
            # Create hash for consistent results
            poster_name = Path(poster_path).stem
            hash_value = int(hashlib.md5(poster_name.encode()).hexdigest()[:8], 16)
            
            # 20% chance of awards
            if hash_value % 10 < 2:
                demo_awards = ["oscars", "emmys", "golden", "bafta", "cannes"]
                selected = demo_awards[hash_value % len(demo_awards)]
                self.logger.debug(f"🎭 [V2 AWARDS FETCHER] Demo award: {selected}")
                return selected
            
            self.logger.debug("🚫 [V2 AWARDS FETCHER] No demo awards")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error generating demo awards: {e}")
            return None
    
    async def _get_jellyfin_metadata(self, jellyfin_id: str) -> Optional[Dict[str, Any]]:
        """Get media metadata from Jellyfin service"""
        try:
            from app.services.jellyfin_service import get_jellyfin_service
            jellyfin_service = get_jellyfin_service()
            return await jellyfin_service.get_media_item_by_id(jellyfin_id)
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error getting Jellyfin metadata: {e}")
            return None
    
    async def _detect_awards_from_metadata(
        self, 
        title: str, 
        year: Optional[int], 
        tmdb_id: Optional[str], 
        imdb_id: Optional[str], 
        media_type: str
    ) -> Optional[str]:
        """Detect awards from media metadata"""
        try:
            # For now, use deterministic demo logic based on title/year
            # In a real implementation, this would query award databases
            
            title_hash = hashlib.md5(f"{title}{year or ''}".encode()).hexdigest()
            hash_value = int(title_hash[:8], 16)
            
            # 20% chance of awards
            if hash_value % 10 < 2:
                if media_type == "movie":
                    # Movie awards
                    movie_awards = ["oscars", "golden", "bafta", "cannes"]
                    selected = movie_awards[hash_value % len(movie_awards)]
                elif media_type in ["series", "season", "episode"]:
                    # TV awards
                    tv_awards = ["emmys", "golden", "bafta"]
                    selected = tv_awards[hash_value % len(tv_awards)]
                else:
                    # General awards
                    general_awards = ["oscars", "emmys", "golden", "bafta", "cannes"]
                    selected = general_awards[hash_value % len(general_awards)]
                
                self.logger.debug(f"🏆 [V2 AWARDS FETCHER] Award detected: {selected}")
                return selected
            
            self.logger.debug("🚫 [V2 AWARDS FETCHER] No awards detected")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ [V2 AWARDS FETCHER] Error detecting awards: {e}")
            return None
