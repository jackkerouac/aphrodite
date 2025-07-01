"""
Unified Badge Renderer

Pure V2 badge rendering engine - no V1 dependencies.
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from aphrodite_logging import get_logger

from .font_manager import FontManager
from .color_utils import ColorUtils
from .positioning import BadgePositioning


class UnifiedBadgeRenderer:
    """Pure V2 badge rendering engine"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.renderer", service="badge")
        self.font_manager = FontManager()
        self.color_utils = ColorUtils()
        self.positioning = BadgePositioning()
        
        # Standard image paths in Docker container
        self.image_paths = [
            "/app/images",
            "/app/assets/images",
            "/app/static/images"
        ]
    
    def create_text_badge(
        self, 
        text: str, 
        settings: Dict[str, Any],
        badge_type: str = "generic"
    ) -> Image.Image:
        """Create a text-based badge"""
        try:
            self.logger.debug(f"🔨 [V2 RENDERER] Creating text badge: '{text}' ({badge_type})")
            
            # Get settings with defaults
            general = settings.get('General', {})
            text_settings = settings.get('Text', {})
            bg_settings = settings.get('Background', {})
            border_settings = settings.get('Border', {})
            shadow_settings = settings.get('Shadow', {})
            
            # Font settings
            font_name = text_settings.get('font', 'Arial.ttf')
            fallback_font = text_settings.get('fallback_font', 'DejaVuSans.ttf')
            text_size = text_settings.get('text-size', 20)
            text_color = text_settings.get('text-color', '#FFFFFF')
            
            # Badge dimensions
            text_padding = general.get('general_text_padding', 12)
            use_dynamic = general.get('use_dynamic_sizing', True)
            badge_size = general.get('general_badge_size', 100)
            
            # Load font
            font = self.font_manager.load_font(font_name, text_size, fallback_font)
            
            # Measure text
            text_width, text_height = self.font_manager.measure_text(text, font)
            
            # Calculate badge dimensions
            if use_dynamic:
                # Dynamic sizing: badge fits content
                width = text_width + (text_padding * 2)
                height = text_height + (text_padding * 2)
                self.logger.debug(f"🔨 [V2 RENDERER] Dynamic badge size: {width}x{height}")
            else:
                # Fixed sizing: badge is specific size
                width = badge_size
                height = badge_size
                self.logger.debug(f"🔨 [V2 RENDERER] Fixed badge size: {width}x{height}")
            
            # Create badge image
            badge = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(badge)
            
            # Background
            bg_color = bg_settings.get('background-color', '#fe019a')
            bg_opacity = bg_settings.get('background_opacity', 60)
            bg_rgba = self.color_utils.hex_to_rgba(bg_color, bg_opacity)
            
            # Border
            border_width = border_settings.get('border_width', 1)
            border_radius = border_settings.get('border-radius', 10)
            border_color = border_settings.get('border-color', '#000000')
            
            # Draw background with rounded corners
            if border_radius > 0:
                self._draw_rounded_rectangle(
                    draw, (0, 0, width, height), 
                    bg_rgba, border_radius
                )
            else:
                draw.rectangle((0, 0, width, height), fill=bg_rgba)
            
            # Draw border if specified
            if border_width > 0:
                border_rgba = self.color_utils.hex_to_rgba(border_color, 100)
                for i in range(border_width):
                    if border_radius > 0:
                        self._draw_rounded_rectangle_outline(
                            draw, (i, i, width-i-1, height-i-1),
                            border_rgba, border_radius-i
                        )
                    else:
                        draw.rectangle((i, i, width-i-1, height-i-1), outline=border_rgba)
            
            # Calculate text position (centered)
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            
            # Draw shadow if enabled
            if shadow_settings.get('shadow_enable', False):
                shadow_offset_x = shadow_settings.get('shadow_offset_x', 2)
                shadow_offset_y = shadow_settings.get('shadow_offset_y', 2)
                shadow_blur = shadow_settings.get('shadow_blur', 5)
                
                # Create shadow
                shadow_x = text_x + shadow_offset_x
                shadow_y = text_y + shadow_offset_y
                draw.text((shadow_x, shadow_y), text, font=font, fill=(0, 0, 0, 128))
                
                # Apply blur to shadow if needed
                if shadow_blur > 0:
                    badge = badge.filter(ImageFilter.GaussianBlur(radius=shadow_blur/2))
                    draw = ImageDraw.Draw(badge)
            
            # Draw text
            text_rgba = self.color_utils.hex_to_rgba(text_color, 100)
            draw.text((text_x, text_y), text, font=font, fill=text_rgba)
            
            self.logger.debug(f"✅ [V2 RENDERER] Text badge created successfully: {width}x{height}")
            return badge
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RENDERER] Error creating text badge: {e}", exc_info=True)
            # Return minimal fallback badge
            return self._create_fallback_badge(text)
    
    def create_image_badge(
        self, 
        image_name: str, 
        settings: Dict[str, Any],
        badge_type: str = "generic"
    ) -> Optional[Image.Image]:
        """Create an image-based badge with full database styling applied"""
        try:
            self.logger.debug(f"🔨 [V2 RENDERER] Creating image badge: '{image_name}' ({badge_type})")
            
            # Find image file
            image_path = self._find_image_file(image_name, badge_type, settings)
            if not image_path:
                self.logger.warning(f"⚠️ [V2 RENDERER] Image not found: {image_name}")
                return None
            
            # Load image
            badge_image = Image.open(image_path).convert('RGBA')
            
            # Get ALL settings sections from database
            general = settings.get('General', {})
            image_settings = settings.get('ImageBadges', {})
            bg_settings = settings.get('Background', {})
            border_settings = settings.get('Border', {})
            shadow_settings = settings.get('Shadow', {})
            
            badge_size = general.get('general_badge_size', 100)
            image_padding = image_settings.get('image_padding', 15)
            use_dynamic = general.get('use_dynamic_sizing', True)
            
            # Calculate target size - RESPECT USER'S BADGE SIZE SETTING
            if use_dynamic:
                # Dynamic sizing: use user's badge_size as max dimension, preserve aspect ratio
                max_dimension = badge_size  # Use the user's actual setting, not hardcoded 120px!
                original_width, original_height = badge_image.size
                
                # Calculate scaling to fit within user's specified size while preserving aspect ratio
                if original_width > original_height:
                    new_width = max_dimension
                    new_height = int((original_height * max_dimension) / original_width)
                else:
                    new_height = max_dimension
                    new_width = int((original_width * max_dimension) / original_height)
                    
                self.logger.debug(f"📏 [V2 RENDERER] Dynamic sizing: {original_width}x{original_height} -> {new_width}x{new_height} (max: {max_dimension})")
            else:
                # Fixed sizing: scale to user's badge_size while preserving aspect ratio (NOT forced square)
                target_size = badge_size
                original_width, original_height = badge_image.size
                
                # Scale to fit within the target size, preserving aspect ratio
                scale_factor = min(target_size / original_width, target_size / original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                self.logger.debug(f"📏 [V2 RENDERER] Fixed sizing: {original_width}x{original_height} -> {new_width}x{new_height} (target: {target_size})")
            
            # Resize image
            badge_image = badge_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # =====================================================================
            # APPLY ALL DATABASE STYLING SETTINGS TO IMAGE BADGE
            # =====================================================================
            
            # Calculate final badge dimensions with user's styling preferences
            final_padding = image_padding  # User's image padding setting
            border_width = border_settings.get('border_width', 1)
            
            # Total canvas size = image + padding + border
            canvas_width = new_width + (final_padding * 2) + (border_width * 2)
            canvas_height = new_height + (final_padding * 2) + (border_width * 2)
            
            # Create canvas for styled badge
            styled_badge = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(styled_badge)
            
            # User's background styling
            bg_color = bg_settings.get('background-color', bg_settings.get('background_color', '#000000'))
            bg_opacity = bg_settings.get('background_opacity', 60)
            bg_rgba = self.color_utils.hex_to_rgba(bg_color, bg_opacity)
            
            # User's border styling
            border_radius = border_settings.get('border-radius', border_settings.get('border_radius', 10))
            border_color = border_settings.get('border-color', border_settings.get('border_color', '#000000'))
            
            # Draw background with user's preferences
            if border_radius > 0:
                self._draw_rounded_rectangle(
                    draw, (0, 0, canvas_width, canvas_height), 
                    bg_rgba, border_radius
                )
            else:
                draw.rectangle((0, 0, canvas_width, canvas_height), fill=bg_rgba)
            
            # Draw border if user wants it
            if border_width > 0:
                border_rgba = self.color_utils.hex_to_rgba(border_color, 100)
                for i in range(border_width):
                    if border_radius > 0:
                        self._draw_rounded_rectangle_outline(
                            draw, (i, i, canvas_width-i-1, canvas_height-i-1),
                            border_rgba, max(0, border_radius-i)
                        )
                    else:
                        draw.rectangle((i, i, canvas_width-i-1, canvas_height-i-1), outline=border_rgba)
            
            # Apply shadow if user enabled it
            if shadow_settings.get('shadow_enable', False):
                shadow_offset_x = shadow_settings.get('shadow_offset_x', 2)
                shadow_offset_y = shadow_settings.get('shadow_offset_y', 2)
                shadow_blur = shadow_settings.get('shadow_blur', 5)
                
                # Create shadow layer (simplified implementation)
                shadow_x = border_width + final_padding + shadow_offset_x
                shadow_y = border_width + final_padding + shadow_offset_y
                shadow_color = (0, 0, 0, 128)  # Semi-transparent black
                
                # Draw simple shadow rectangle
                shadow_rect = (shadow_x, shadow_y, shadow_x + new_width, shadow_y + new_height)
                draw.rectangle(shadow_rect, fill=shadow_color)
            
            # Position the original image on the styled canvas
            paste_x = border_width + final_padding
            paste_y = border_width + final_padding
            styled_badge.paste(badge_image, (paste_x, paste_y), badge_image)
            
            self.logger.debug(f"✅ [V2 RENDERER] Styled image badge created: {canvas_width}x{canvas_height}")
            self.logger.debug(f"🎨 [V2 RENDERER] Applied styling - BG: {bg_color}, Border: {border_width}px, Padding: {final_padding}px")
            
            return styled_badge
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RENDERER] Error creating image badge: {e}", exc_info=True)
            return None
    
    def create_review_badge(
        self, 
        image_name: str, 
        percentage_text: str,
        settings: Dict[str, Any]
    ) -> Optional[Image.Image]:
        """Create a review badge with logo image and percentage text overlay - FULLY USER CONFIGURABLE"""
        try:
            self.logger.debug(f"🔨 [V2 RENDERER] Creating review badge: '{image_name}' with text '{percentage_text}'")
            
            # Get all settings sections from user's database
            general = settings.get('General', {})
            image_settings = settings.get('ImageBadges', {})
            text_settings = settings.get('Text', {})
            bg_settings = settings.get('Background', {})
            border_settings = settings.get('Border', {})
            shadow_settings = settings.get('Shadow', {})
            
            # Check if image badges are enabled by user
            if not image_settings.get('enable_image_badges', True):
                self.logger.debug("📝 [V2 RENDERER] Image badges disabled by user, using text badge")
                return self.create_text_badge(percentage_text, settings, "review")
            
            # Get user's image mapping from settings
            image_mapping = image_settings.get('image_mapping', {})
            mapped_filename = image_mapping.get(image_name, image_name.lower() + '.png')
            
            # Find image file using user's codec_image_directory setting
            image_directory = image_settings.get('codec_image_directory', '/app/assets/images/rating')
            image_path = self._find_review_image_file(mapped_filename, image_directory)
            
            if not image_path:
                self.logger.warning(f"⚠️ [V2 RENDERER] Review image not found: {mapped_filename} in {image_directory}")
                # Fallback based on user's preference
                if image_settings.get('fallback_to_text', True):
                    self.logger.debug("📝 [V2 RENDERER] Falling back to text badge per user setting")
                    return self.create_text_badge(percentage_text, settings, "review")
                else:
                    return None
            
            # Load logo image
            logo_image = Image.open(image_path).convert('RGBA')
            
            # =====================================================================
            # ALL SIZING AND SPACING FROM USER'S DATABASE SETTINGS
            # =====================================================================
            
            # User's core badge settings
            badge_size = general.get('general_badge_size', 100)           # User configurable
            use_dynamic = general.get('use_dynamic_sizing', True)         # User configurable
            image_padding = image_settings.get('image_padding', 5)       # User configurable
            text_padding = general.get('general_text_padding', 20)       # User configurable - UNIFORM PADDING
            badge_spacing = general.get('badge_spacing', 15)             # User configurable
            
            # User's text size preference - RESPECT IT EXACTLY
            user_text_size = text_settings.get('text-size', text_settings.get('text_size', 60))
            
            # Calculate actual scaled text size early - we need this for height calculation
            # Consistent scaling formula for all review badges
            scale_factor = min(badge_size / 150.0, badge_size / 120.0)  # Scale relative to badge size
            actual_text_size = max(int(user_text_size * scale_factor), 10)  # Minimum 10pt text
            
            # Calculate logo size based on user preferences
            if use_dynamic:
                # Logo takes up most of the badge space, but leave room for text and user padding
                available_space = badge_size - (text_padding * 2)  # Reserve space for uniform padding
                logo_size = int(available_space * 0.6)  # Logo gets 60% of available space
                original_width, original_height = logo_image.size
                
                if original_width > original_height:
                    logo_width = logo_size
                    logo_height = int((original_height * logo_size) / original_width)
                else:
                    logo_height = logo_size
                    logo_width = int((original_width * logo_size) / original_height)
            else:
                # Fixed mode: scale logo to fit nicely within badge
                available_space = badge_size - (text_padding * 2)
                logo_size = int(available_space * 0.6)
                original_width, original_height = logo_image.size
                
                scale_factor = min(logo_size / original_width, logo_size / original_height)
                logo_width = int(original_width * scale_factor)
                logo_height = int(original_height * scale_factor)
            
            # Resize logo to calculated size
            logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # Calculate final badge dimensions with UNIFORM PADDING on all sides
            # Width: logo width + uniform padding on left and right
            final_width = logo_width + (text_padding * 2) + (image_padding * 2)
            
            # Height: logo + actual text height + spacing + uniform padding on top and bottom
            # Use actual scaled text size instead of overestimating text area
            text_area_height = max(int(actual_text_size * 1.2), 20)  # Use actual scaled size + small buffer
            final_height = logo_height + text_area_height + badge_spacing + (text_padding * 2) + (image_padding * 2)
            
            # Create badge canvas
            badge = Image.new('RGBA', (final_width, final_height), (0, 0, 0, 0))
            
            # =====================================================================
            # USER'S BACKGROUND AND STYLING PREFERENCES
            # =====================================================================
            
            # User's background color choice (could be yellow, blue, anything!)
            bg_color = bg_settings.get('background-color', bg_settings.get('background_color', '#2C2C2C'))
            bg_opacity = bg_settings.get('background_opacity', 60)
            bg_rgba = self.color_utils.hex_to_rgba(bg_color, bg_opacity)
            
            # User's border preferences
            border_width = border_settings.get('border_width', 1)
            border_radius = border_settings.get('border-radius', border_settings.get('border_radius', 10))
            border_color = border_settings.get('border-color', border_settings.get('border_color', '#2C2C2C'))
            
            # Draw background with user's styling choices
            draw = ImageDraw.Draw(badge)
            if border_radius > 0:
                self._draw_rounded_rectangle(
                    draw, (0, 0, final_width, final_height), 
                    bg_rgba, border_radius
                )
            else:
                draw.rectangle((0, 0, final_width, final_height), fill=bg_rgba)
            
            # Draw border if user wants it
            if border_width > 0:
                border_rgba = self.color_utils.hex_to_rgba(border_color, 100)
                for i in range(border_width):
                    if border_radius > 0:
                        self._draw_rounded_rectangle_outline(
                            draw, (i, i, final_width-i-1, final_height-i-1),
                            border_rgba, max(0, border_radius-i)
                        )
                    else:
                        draw.rectangle((i, i, final_width-i-1, final_height-i-1), outline=border_rgba)
            
            # =====================================================================
            # POSITIONING BASED ON USER'S UNIFORM PADDING PREFERENCES
            # =====================================================================
            
            # Position logo with uniform padding from top and centered horizontally
            logo_x = (final_width - logo_width) // 2
            logo_y = text_padding + image_padding  # Uniform top padding
            badge.paste(logo_image, (logo_x, logo_y), logo_image)
            
            # =====================================================================
            # TEXT RENDERING WITH USER'S FONT AND SIZE PREFERENCES
            # =====================================================================
            
            # User's font choices
            font_path = text_settings.get('font', '/app/assets/fonts/AvenirNextLTProBold.otf')
            fallback_font = text_settings.get('fallback_font', '/app/assets/fonts/DejaVuSans.ttf')
            text_color = text_settings.get('text-color', text_settings.get('text_color', '#FFFFFF'))
            
            self.logger.debug(f"🔤 [V2 RENDERER] User text size: {user_text_size}, scaled: {actual_text_size} (scale: {scale_factor:.2f})")
            
            # Load font with user's preferred size
            font = self.font_manager.load_font(font_path, actual_text_size, fallback_font)
            
            # Measure text
            text_width, text_height = self.font_manager.measure_text(percentage_text, font)
            
            # Position text with uniform spacing below logo
            text_x = (final_width - text_width) // 2
            text_y = logo_y + logo_height + badge_spacing  # User controls this spacing!
            
            # =====================================================================
            # TEXT EFFECTS BASED ON USER'S SHADOW PREFERENCES
            # =====================================================================
            
            # Apply shadow if user enabled it
            if shadow_settings.get('shadow_enable', False):
                shadow_offset_x = shadow_settings.get('shadow_offset_x', 2)
                shadow_offset_y = shadow_settings.get('shadow_offset_y', 2)
                shadow_blur = shadow_settings.get('shadow_blur', 5)
                shadow_x = text_x + shadow_offset_x
                shadow_y = text_y + shadow_offset_y
                draw.text((shadow_x, shadow_y), percentage_text, font=font, fill=(0, 0, 0, 128))
            
            # Text outline for readability (subtle to respect user's design)
            text_rgba = self.color_utils.hex_to_rgba(text_color, 100)
            outline_color = (0, 0, 0, 150)  # Semi-transparent so it doesn't overwhelm user's colors
            
            # Subtle outline that works with any user background color
            for adj_x in range(-1, 2):
                for adj_y in range(-1, 2):
                    if adj_x != 0 or adj_y != 0:
                        draw.text((text_x + adj_x, text_y + adj_y), percentage_text, font=font, fill=outline_color)
            
            # Main text in user's chosen color
            draw.text((text_x, text_y), percentage_text, font=font, fill=text_rgba)
            
            self.logger.debug(f"✅ [V2 RENDERER] Review badge created: {final_width}x{final_height}")
            self.logger.debug(f"📊 [V2 RENDERER] User settings - Size: {badge_size}, Text: {user_text_size}pt, Spacing: {badge_spacing}px")
            
            return badge
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RENDERER] Error creating review badge: {e}", exc_info=True)
            # Fallback to text badge
            return self.create_text_badge(percentage_text, settings, "review")
    
    def _find_review_image_file(self, filename: str, image_directory: str) -> Optional[Path]:
        """Find review image file in specified directory"""
        try:
            directory = Path(image_directory)
            if directory.exists():
                # Try direct file match
                image_file = directory / filename
                if image_file.exists():
                    return image_file
                
                # Try with different cases
                for file in directory.iterdir():
                    if file.name.lower() == filename.lower():
                        return file
                
                # Try without extension and add common extensions
                name_without_ext = Path(filename).stem
                for ext in ['.png', '.jpg', '.jpeg', '.svg']:
                    image_file = directory / f"{name_without_ext}{ext}"
                    if image_file.exists():
                        return image_file
                    
                    # Try case-insensitive
                    for file in directory.iterdir():
                        if file.stem.lower() == name_without_ext.lower() and file.suffix.lower() == ext:
                            return file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding review image file {filename}: {e}")
            return None
    
    def apply_badge_to_poster(
        self,
        poster_path: str, 
        badge: Image.Image, 
        settings: Dict[str, Any], 
        output_path: str
    ) -> bool:
        """Apply badge to poster and save to output path"""
        try:
            self.logger.debug(f"🔨 [V2 RENDERER] Applying badge to poster: {poster_path} -> {output_path}")
            
            # Load poster
            poster = Image.open(poster_path).convert("RGBA")
            
            # Get position settings
            general = settings.get('General', {})
            position = general.get('general_badge_position', 'top-right')
            base_edge_padding = general.get('general_edge_padding', 30)
            
            # Calculate dynamic padding
            edge_padding = self.positioning.calculate_dynamic_padding(
                poster.width, poster.height, base_edge_padding
            )
            
            # Calculate badge position
            coords = self.positioning.calculate_badge_position(
                (poster.width, poster.height),
                (badge.width, badge.height),
                position,
                edge_padding
            )
            
            # Apply badge to poster
            poster.paste(badge, coords, badge)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save final poster
            poster.convert("RGB").save(output_path, "JPEG", quality=95)
            
            self.logger.debug(f"✅ [V2 RENDERER] Badge applied successfully to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RENDERER] Error applying badge: {e}", exc_info=True)
            return False
    
    def apply_multiple_badges_to_poster(
        self,
        poster_path: str,
        badges: List[Image.Image],
        settings: Dict[str, Any],
        output_path: str
    ) -> bool:
        """Apply multiple badges to poster with proper layout"""
        try:
            if not badges:
                self.logger.warning("No badges to apply")
                return False
            
            self.logger.debug(f"🔨 [V2 RENDERER] Applying {len(badges)} badges to poster: {poster_path}")
            
            # Load poster
            poster = Image.open(poster_path).convert("RGBA")
            
            # Calculate positions for all badges
            badge_sizes = [(badge.width, badge.height) for badge in badges]
            positions = self.positioning.calculate_multi_badge_layout(
                (poster.width, poster.height),
                badge_sizes,
                settings
            )
            
            # Apply each badge
            for badge, position in zip(badges, positions):
                poster.paste(badge, position, badge)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save final poster
            poster.convert("RGB").save(output_path, "JPEG", quality=95)
            
            self.logger.debug(f"✅ [V2 RENDERER] {len(badges)} badges applied successfully to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [V2 RENDERER] Error applying multiple badges: {e}", exc_info=True)
            return False
    
    def _find_image_file(self, image_name: str, badge_type: str, settings: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """Find image file in various locations, respecting user settings and dev environment"""
        try:
            search_paths = []
            
            # If settings provide a specific directory, prioritize it
            if settings and 'ImageBadges' in settings:
                image_settings = settings['ImageBadges']
                codec_dir = image_settings.get('codec_image_directory')
                if codec_dir:
                    search_paths.append(codec_dir)
                    # Also try corrected path if the database has wrong path
                    if '/app/assets/images' in codec_dir:
                        corrected_path = codec_dir.replace('/app/assets/images', '/app/images')
                        search_paths.append(corrected_path)
            
            # DEVELOPMENT ENVIRONMENT PATHS - Add these first for dev priority
            import os
            if os.name == 'nt' or not os.path.exists('/app'):
                # Windows development environment or non-Docker environment
                dev_paths = [
                    f"images/{badge_type}",     # Relative to project root
                    "images/codec",            # Main codec directory
                    "images/audio",            # Audio fallback
                    "images/rating",           # Reviews
                    "images/resolution",       # Resolution
                    "images/awards",           # Awards
                ]
                search_paths.extend(dev_paths)
            
            # Try specific badge type directories (Docker paths)
            type_specific_paths = [
                f"/app/images/{badge_type}",
                f"/app/images/codec",  # Audio codec images
                f"/app/images/rating",  # Reviews
                f"/app/images/resolution",  # Resolution
                f"/app/images/awards",  # Awards
                "/app/images/audio"  # Audio fallback
            ]
            
            # Combine all paths
            search_paths.extend(type_specific_paths)
            search_paths.extend(self.image_paths)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_paths = []
            for path in search_paths:
                if path not in seen:
                    seen.add(path)
                    unique_paths.append(path)
            
            for path_str in unique_paths:
                path = Path(path_str)
                if path.exists():
                    # Try direct file match
                    image_file = path / image_name
                    if image_file.exists():
                        self.logger.debug(f"🔍 [V2 RENDERER] Found image: {image_file}")
                        return image_file
                    
                    # Try case-insensitive match
                    for file in path.iterdir():
                        if file.name.lower() == image_name.lower():
                            self.logger.debug(f"🔍 [V2 RENDERER] Found image (case-insensitive): {file}")
                            return file
                    
                    # Try with different extensions
                    name_without_ext = Path(image_name).stem
                    for ext in ['.png', '.jpg', '.jpeg', '.svg']:
                        image_file = path / f"{name_without_ext}{ext}"
                        if image_file.exists():
                            self.logger.debug(f"🔍 [V2 RENDERER] Found image with extension: {image_file}")
                            return image_file
                        
                        # Try case-insensitive with extension
                        for file in path.iterdir():
                            if file.stem.lower() == name_without_ext.lower() and file.suffix.lower() == ext:
                                self.logger.debug(f"🔍 [V2 RENDERER] Found image (case-insensitive + ext): {file}")
                                return file
            
            self.logger.warning(f"⚠️ [V2 RENDERER] Image not found: {image_name} in paths: {unique_paths[:3]}...")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding image file {image_name}: {e}")
            return None
    
    def _draw_rounded_rectangle(self, draw: ImageDraw.Draw, bounds: Tuple[int, int, int, int], 
                               fill: Tuple[int, int, int, int], radius: int):
        """Draw a rounded rectangle"""
        try:
            x1, y1, x2, y2 = bounds
            
            # Draw the main rectangle
            draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
            draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
            
            # Draw the corners
            draw.pieslice((x1, y1, x1 + 2*radius, y1 + 2*radius), 180, 270, fill=fill)
            draw.pieslice((x2 - 2*radius, y1, x2, y1 + 2*radius), 270, 360, fill=fill)
            draw.pieslice((x1, y2 - 2*radius, x1 + 2*radius, y2), 90, 180, fill=fill)
            draw.pieslice((x2 - 2*radius, y2 - 2*radius, x2, y2), 0, 90, fill=fill)
            
        except Exception as e:
            self.logger.error(f"Error drawing rounded rectangle: {e}")
            # Fallback to regular rectangle
            draw.rectangle(bounds, fill=fill)
    
    def _draw_rounded_rectangle_outline(self, draw: ImageDraw.Draw, bounds: Tuple[int, int, int, int], 
                                       outline: Tuple[int, int, int, int], radius: int):
        """Draw a rounded rectangle outline"""
        try:
            x1, y1, x2, y2 = bounds
            
            # Draw the main rectangle outline
            draw.rectangle((x1 + radius, y1, x2 - radius, y1), outline=outline)
            draw.rectangle((x1 + radius, y2, x2 - radius, y2), outline=outline)
            draw.rectangle((x1, y1 + radius, x1, y2 - radius), outline=outline)
            draw.rectangle((x2, y1 + radius, x2, y2 - radius), outline=outline)
            
            # Draw the corner arcs
            draw.arc((x1, y1, x1 + 2*radius, y1 + 2*radius), 180, 270, fill=outline)
            draw.arc((x2 - 2*radius, y1, x2, y1 + 2*radius), 270, 360, fill=outline)
            draw.arc((x1, y2 - 2*radius, x1 + 2*radius, y2), 90, 180, fill=outline)
            draw.arc((x2 - 2*radius, y2 - 2*radius, x2, y2), 0, 90, fill=outline)
            
        except Exception as e:
            self.logger.error(f"Error drawing rounded rectangle outline: {e}")
            # Fallback to regular rectangle outline
            draw.rectangle(bounds, outline=outline)
    
    def _create_fallback_badge(self, text: str) -> Image.Image:
        """Create a minimal fallback badge when all else fails"""
        try:
            # Create simple text badge
            width, height = 120, 40
            badge = Image.new('RGBA', (width, height), (255, 0, 150, 180))  # Pink fallback
            draw = ImageDraw.Draw(badge)
            
            # Use default font
            font = self.font_manager.load_font("DejaVuSans.ttf", 14)
            
            # Center text
            text_width, text_height = self.font_manager.measure_text(text, font)
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            
            draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
            
            return badge
            
        except Exception as e:
            self.logger.error(f"Error creating fallback badge: {e}")
            # Return completely minimal badge
            return Image.new('RGBA', (100, 30), (255, 0, 0, 255))
