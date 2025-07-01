"""
Audio Badge Creation
Handles creating audio badges using enhanced or legacy methods.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from aphrodite_logging import get_logger

from .audio_enhanced_components import EnhancedAudioComponents
from .audio_legacy_handler import LegacyAudioHandler


class AudioBadgeCreator:
    """Handles audio badge creation using enhanced or legacy methods"""
    
    def __init__(self, renderer, components: EnhancedAudioComponents, legacy_handler: LegacyAudioHandler):
        self.logger = get_logger("aphrodite.audio.badge", service="badge")
        self.renderer = renderer
        self.components = components
        self.legacy_handler = legacy_handler
    
    async def create_badge(
        self,
        poster_path: str,
        audio_data,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create audio badge using enhanced or legacy methods"""
        try:
            # Determine if we have AudioInfo (enhanced) or string (legacy)
            from .audio_types import AudioInfo
            
            if self.components.enabled and isinstance(audio_data, AudioInfo):
                return await self._create_enhanced_badge(poster_path, audio_data, settings, output_path)
            else:
                return await self._create_legacy_badge(poster_path, str(audio_data), settings, output_path)
                
        except Exception as e:
            self.logger.error(f"❌ [AUDIO BADGE] Badge creation error: {e}", exc_info=True)
            return None
    
    async def _create_enhanced_badge(
        self,
        poster_path: str,
        audio_info,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create audio badge using enhanced image manager"""
        try:
            self.logger.debug(f"🎨 [AUDIO BADGE] Creating enhanced badge for: {audio_info}")
            
            # Determine output path
            final_output_path = self._get_output_path(poster_path, output_path)
            
            # Create badge using enhanced image manager
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', False)
            
            if image_badges_enabled:
                # Get user mappings
                user_mappings = settings.get('ImageBadges', {}).get('image_mapping', {})
                
                # Find best image match using enhanced manager
                image_file = self.components.image_manager.find_best_image_match(
                    audio_info, user_mappings
                )
                
                self.logger.debug(f"🖼️ [AUDIO BADGE] Enhanced image match: {image_file}")
                
                # Try image badge first
                badge = self.renderer.create_image_badge(
                    image_file,
                    settings,
                    "audio"
                )
                
                if not badge:
                    # Fallback to text badge
                    self.logger.debug(f"📝 [AUDIO BADGE] Image failed, using text badge")
                    badge = self.renderer.create_text_badge(str(audio_info), settings, "audio")
            else:
                # Use text badge
                self.logger.debug(f"📝 [AUDIO BADGE] Creating text badge")
                badge = self.renderer.create_text_badge(str(audio_info), settings, "audio")
            
            if not badge:
                self.logger.error(f"❌ [AUDIO BADGE] Enhanced badge creation failed")
                return None
            
            # Apply badge to poster
            success = self.renderer.apply_badge_to_poster(
                poster_path, badge, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [AUDIO BADGE] Enhanced badge applied: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [AUDIO BADGE] Enhanced badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [AUDIO BADGE] Enhanced badge creation error: {e}", exc_info=True)
            return None
    
    async def _create_legacy_badge(
        self,
        poster_path: str,
        codec_data: str,
        settings: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create audio badge using legacy V2 renderer"""
        try:
            self.logger.debug(f"🎨 [AUDIO BADGE] Creating legacy badge for: {codec_data}")
            
            # Determine output path
            final_output_path = self._get_output_path(poster_path, output_path)
            
            # Create badge using V2 renderer
            image_badges_enabled = settings.get('ImageBadges', {}).get('enable_image_badges', False)
            
            if image_badges_enabled:
                # Try image badge first
                self.logger.debug(f"🖼️ [AUDIO BADGE] Attempting legacy image badge for: {codec_data}")
                badge = self.renderer.create_image_badge(
                    self.legacy_handler.map_codec_to_image(codec_data),
                    settings,
                    "audio"
                )
                
                if not badge:
                    # Fallback to text badge
                    self.logger.debug(f"📝 [AUDIO BADGE] Image failed, using text badge")
                    badge = self.renderer.create_text_badge(codec_data, settings, "audio")
            else:
                # Use text badge
                self.logger.debug(f"📝 [AUDIO BADGE] Creating text badge")
                badge = self.renderer.create_text_badge(codec_data, settings, "audio")
            
            if not badge:
                self.logger.error(f"❌ [AUDIO BADGE] Legacy badge creation failed")
                return None
            
            # Apply badge to poster
            success = self.renderer.apply_badge_to_poster(
                poster_path, badge, settings, final_output_path
            )
            
            if success:
                self.logger.debug(f"✅ [AUDIO BADGE] Legacy badge applied: {final_output_path}")
                return final_output_path
            else:
                self.logger.error(f"❌ [AUDIO BADGE] Legacy badge application failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [AUDIO BADGE] Legacy badge creation error: {e}", exc_info=True)
            return None
    
    def _get_output_path(self, poster_path: str, output_path: Optional[str] = None) -> str:
        """Determine final output path"""
        if output_path:
            return output_path
        else:
            # Generate V2 preview path
            poster_name = Path(poster_path).name
            return f"/app/api/static/preview/{poster_name}"
