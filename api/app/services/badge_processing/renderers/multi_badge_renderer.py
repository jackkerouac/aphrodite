"""
V2 Multi-Badge Renderer

Handles layout and rendering of multiple badges (like review badges).
"""

from typing import List, Dict, Any, Tuple
from PIL import Image
from aphrodite_logging import get_logger

from .badge_renderer import UnifiedBadgeRenderer
from .positioning import BadgePositioning


class V2MultiBadgeRenderer:
    """V2 renderer for multiple badges with proper layout"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.multi.renderer.v2", service="badge")
        self.unified_renderer = UnifiedBadgeRenderer()
        self.positioning = BadgePositioning()
    
    def create_review_badges(
        self, 
        reviews: List[Dict[str, Any]], 
        settings: Dict[str, Any]
    ) -> List[Image.Image]:
        """Create individual review badges from review data"""
        try:
            self.logger.debug(f"🎨 [V2 MULTI RENDERER] Creating {len(reviews)} review badges")
            
            badges = []
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', True)
            fallback_to_text = settings.get('ImageBadges', {}).get('fallback_to_text', True)
            
            for i, review in enumerate(reviews):
                source = review.get('source', 'Unknown')
                text = review.get('text', 'N/A')
                image_key = review.get('image_key', source)
                
                self.logger.debug(f"🎨 [V2 MULTI RENDERER] Creating badge {i+1}: {source} = {text}")
                
                badge = None
                
                # Use specialized review badge method that combines image + text
                if image_badges_enabled:
                    badge = self.unified_renderer.create_review_badge(
                        image_key, text, settings
                    )
                    if badge:
                        self.logger.debug(f"✅ [V2 MULTI RENDERER] Created review badge for {source}")
                    else:
                        self.logger.debug(f"⚠️ [V2 MULTI RENDERER] Review badge failed for {source}")
                
                # Fallback to text badge if needed
                if not badge and fallback_to_text:
                    badge = self.unified_renderer.create_text_badge(
                        text, settings, "review"
                    )
                    if badge:
                        self.logger.debug(f"✅ [V2 MULTI RENDERER] Created text badge for {source}")
                
                if badge:
                    badges.append(badge)
                else:
                    self.logger.warning(f"⚠️ [V2 MULTI RENDERER] Failed to create badge for {source}")
            
            self.logger.info(f"✅ [V2 MULTI RENDERER] Created {len(badges)}/{len(reviews)} review badges")
            return badges
            
        except Exception as e:
            self.logger.error(f"❌ [V2 MULTI RENDERER] Error creating review badges: {e}", exc_info=True)
            return []
    
    def apply_review_badges_to_poster(
        self,
        poster_path: str,
        reviews: List[Dict[str, Any]],
        settings: Dict[str, Any],
        output_path: str
    ) -> bool:
        """Apply multiple review badges to poster with proper layout"""
        try:
            self.logger.info(f"🎨 [V2 MULTI RENDERER] Applying {len(reviews)} review badges to poster")
            
            # Create individual badges
            badges = self.create_review_badges(reviews, settings)
            if not badges:
                self.logger.warning("⚠️ [V2 MULTI RENDERER] No badges created, skipping application")
                return False
            
            # Apply badges using unified renderer's multi-badge method
            success = self.unified_renderer.apply_multiple_badges_to_poster(
                poster_path, badges, settings, output_path
            )
            
            if success:
                self.logger.info(f"✅ [V2 MULTI RENDERER] Successfully applied {len(badges)} review badges")
            else:
                self.logger.error(f"❌ [V2 MULTI RENDERER] Failed to apply review badges")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ [V2 MULTI RENDERER] Error applying review badges: {e}", exc_info=True)
            return False
    
    def _get_review_image_filename(self, image_key: str, source: str) -> str:
        """Map review source to image filename"""
        try:
            # Standard image mapping for review sources
            image_mapping = {
                "IMDb": "IMDb.png",
                "TMDb": "TMDb.png", 
                "RT-Crit-Fresh": "rt.png",
                "RT-Crit-Rotten": "rt.png",
                "Rotten Tomatoes": "rt.png",
                "RT Critics": "rt.png",
                "Metacritic": "metacritic_logo.png",
                "MyAnimeList": "MAL.png"
            }
            
            # First try exact image_key match
            if image_key in image_mapping:
                return image_mapping[image_key]
            
            # Then try source match
            if source in image_mapping:
                return image_mapping[source]
            
            # Default fallback
            self.logger.debug(f"🔍 [V2 MULTI RENDERER] No image mapping for {image_key}/{source}, using generic")
            return f"{source.lower().replace(' ', '_')}.png"
            
        except Exception as e:
            self.logger.error(f"❌ [V2 MULTI RENDERER] Error mapping image filename: {e}")
            return "generic_review.png"
