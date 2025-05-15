#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_generator.py

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .color_utils import hex_to_rgba
from .font_utils import load_font

def create_badge(settings, text=None, use_image=True):
    """Create a badge based on the settings, optionally with text or image."""
    # Try to use image badge if enabled and text is provided
    if use_image and text and settings.get('ImageBadges', {}).get('enable_image_badges', False):
        try:
            from .badge_image_handler import load_codec_image
            codec_image = load_codec_image(text, settings)
            
            if codec_image:
                # Apply the same styling to image badges as we do to text badges
                background_color_hex = settings.get('Background', {}).get('background-color')
                if isinstance(background_color_hex, str):
                    background_opacity = settings.get('Background', {}).get('background_opacity', 60)
                else:
                    background_opacity = settings.get('Background', {}).get('background-color', {}).get('background_opacity', 60)
                    background_color_hex = '#fe019a'  # Default if not found
                
                border_color_hex = settings.get('Border', {}).get('border-color')
                if isinstance(border_color_hex, str):
                    border_width = settings.get('Border', {}).get('border_width', 1)
                    border_radius = settings.get('Border', {}).get('border-radius', 10)
                else:
                    border_width = settings.get('Border', {}).get('border-color', {}).get('border_width', 1)
                    border_radius = settings.get('Border', {}).get('border-color', {}).get('border-radius', 10)
                    border_color_hex = '#000000'  # Default black if not found
                
                # Convert colors to RGBA
                background_color = hex_to_rgba(background_color_hex, background_opacity)
                border_color = hex_to_rgba(border_color_hex, 100)  # Full opacity for border
                
                # Apply styling to image badges
                codec_image = _apply_badge_style(codec_image, background_color, border_color, border_width, border_radius)
                
                # Apply shadow if enabled
                shadow_enabled = settings.get('Shadow', {}).get('shadow_enable', False)
                if shadow_enabled:
                    print(f"📝 Applying shadow to codec image with blur: {settings.get('Shadow', {}).get('shadow_blur', 5)}")
                    # Use the actual border radius from settings, not 0
                    codec_image = _apply_shadow(codec_image, settings, border_radius)
                
                print(f"✅ Using image badge for codec: {text}")
                return codec_image
                
            # Fall back to text if image not found and fallback is enabled
            if not settings.get('ImageBadges', {}).get('fallback_to_text', True):
                print(f"ℹ️ No image found for '{text}' and fallback to text is disabled")
                return None
            print(f"ℹ️ No image found for '{text}', falling back to text badge")
        except ImportError as e:
            print(f"⚠️ Warning: Could not import badge_image_handler: {e}")
        except Exception as e:
            print(f"⚠️ Warning: Error creating image badge: {e}, falling back to text badge")
    
    # Continue with text-based badge if no image was used
    if not settings:
        print(f"❌ Error: No settings provided for badge creation.")
        return None
        
    # Default badge size from settings (used as fallback)
    default_badge_size = settings.get('General', {}).get('general_badge_size', 100)
    
    # Get border width for calculations
    border_color_hex = settings.get('Border', {}).get('border-color')
    if isinstance(border_color_hex, str):
        border_width = settings.get('Border', {}).get('border_width', 1)
    else:
        border_width = settings.get('Border', {}).get('border-color', {}).get('border_width', 1)
        border_color_hex = '#000000'  # Default black if not found
    
    # Get border radius
    if isinstance(border_color_hex, str):
        border_radius = settings.get('Border', {}).get('border-radius', 10)
    else:
        border_radius = settings.get('Border', {}).get('border-color', {}).get('border-radius', 10)
    
    # Text padding (space between text and badge edge)
    text_padding = settings.get('General', {}).get('general_text_padding', 12)  # Get from settings or default to 12 pixels
    
    # Get font settings
    font_family = settings.get('Text', {}).get('font', "Arial.ttf")
    fallback_font = settings.get('Text', {}).get('fallback_font', "DejaVuSans.ttf")
    font_size = settings.get('Text', {}).get('text-size', 20)
    
    # For debugging
    print(f"📝 Font settings - Family: {font_family}, Fallback: {fallback_font}, Size: {font_size}")
    
    # Check if we should use dynamic sizing or fixed size
    use_dynamic_sizing = settings.get('General', {}).get('use_dynamic_sizing', True)
    
    # Create initial dimensions based on text if provided
    if text and use_dynamic_sizing:
        try:
            # Load font for text size calculation
            font = load_font(font_family, fallback_font, font_size)
            # If we got the default font, use a smaller size
            if font == ImageFont.load_default():
                font_size = 12  # Smaller for default font
            
            # Create temporary image for text measurement
            temp_img = Image.new('RGBA', (500, 100), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # Measure text dimensions
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate badge dimensions with padding
            badge_width = text_width + (2 * text_padding) + (2 * border_width)
            badge_height = text_height + (2 * text_padding) + (2 * border_width)
            
            # Set a minimum size to maintain aspect
            min_dimension = 30
            badge_width = max(badge_width, min_dimension)
            badge_height = max(badge_height, min_dimension)
            
            # Create a badge with the calculated dimensions
            badge = Image.new('RGBA', (badge_width, badge_height), (0, 0, 0, 0))
        except Exception as e:
            print(f"⚠️ Warning: Error calculating badge size: {e}")
            print(f"  Using default badge size {default_badge_size}x{default_badge_size} instead")
            badge = Image.new('RGBA', (default_badge_size, default_badge_size), (0, 0, 0, 0))
    else:
        # If no text or dynamic sizing is disabled, use default badge size
        badge = Image.new('RGBA', (default_badge_size, default_badge_size), (0, 0, 0, 0))
        
        # Try to load the font if we have text but aren't using dynamic sizing
        if text:
            # Load font
            font = load_font(font_family, fallback_font, font_size)
    
    draw = ImageDraw.Draw(badge)
    
    # Get badge settings - handling both possible formats
    background_color_hex = settings.get('Background', {}).get('background-color')
    if isinstance(background_color_hex, str):
        # Format: Background: { background-color: '#fe019a' }
        background_opacity = settings.get('Background', {}).get('background_opacity', 60)
    else:
        # Format: Background: { background-color: { background_opacity: 60 } }
        background_opacity = settings.get('Background', {}).get('background-color', {}).get('background_opacity', 60)
        background_color_hex = '#fe019a'  # Default if not found
    
    # Convert colors to RGBA
    background_color = hex_to_rgba(background_color_hex, background_opacity)
    border_color = hex_to_rgba(border_color_hex, 100)  # Full opacity for border
    
    # Apply base style to the badge
    badge = _apply_badge_style(badge, background_color, border_color, border_width, border_radius)
    
    # Add text if provided
    if text:
        badge = _add_text_to_badge(badge, text, font, settings)
    
    # Apply shadow if enabled
    shadow_enabled = settings.get('Shadow', {}).get('shadow_enable', False)
    if shadow_enabled:
        print(f"📝 Shadow enabled with blur: {settings.get('Shadow', {}).get('shadow_blur', 5)}")
        badge = _apply_shadow(badge, settings, border_radius)
        
    return badge

def _apply_badge_style(badge, background_color, border_color, border_width, border_radius):
    """Apply background and border styling to the badge."""
    # Create a new transparent image for the background and border
    styled_badge = Image.new('RGBA', badge.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(styled_badge)
    
    # Check if we're dealing with a badge that might already have content
    # by checking if it has any non-transparent pixels
    has_content = any(pixel[3] > 0 for pixel in badge.getdata())
    
    # Check if we should implement rounded corners
    if border_radius > 0:
        try:
            # Make the radius smaller if the badge is small
            effective_radius = min(border_radius, badge.width // 4, badge.height // 4)
            
            # Create a mask for the rounded rectangle
            mask = Image.new('L', badge.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            
            # Draw rounded rectangle on the mask
            # Top left corner
            mask_draw.pieslice([0, 0, effective_radius * 2, effective_radius * 2], 180, 270, fill=255)
            # Top right corner
            mask_draw.pieslice([badge.width - effective_radius * 2, 0, badge.width, effective_radius * 2], 270, 0, fill=255)
            # Bottom left corner
            mask_draw.pieslice([0, badge.height - effective_radius * 2, effective_radius * 2, badge.height], 90, 180, fill=255)
            # Bottom right corner
            mask_draw.pieslice([badge.width - effective_radius * 2, badge.height - effective_radius * 2, badge.width, badge.height], 0, 90, fill=255)
            
            # Fill in the center
            mask_draw.rectangle([effective_radius, 0, badge.width - effective_radius, badge.height], fill=255)
            mask_draw.rectangle([0, effective_radius, badge.width, badge.height - effective_radius], fill=255)
            
            # Create a background rectangle
            background = Image.new('RGBA', badge.size, background_color)
            
            # Apply mask to background
            styled_badge = Image.composite(background, styled_badge, mask)
            
            # Draw border if needed
            if border_width > 0:
                border_mask = Image.new('L', badge.size, 0)
                border_draw = ImageDraw.Draw(border_mask)
                
                # Draw outer rounded rectangle
                border_draw.pieslice([0, 0, effective_radius * 2, effective_radius * 2], 180, 270, fill=255)
                border_draw.pieslice([badge.width - effective_radius * 2, 0, badge.width, effective_radius * 2], 270, 0, fill=255)
                border_draw.pieslice([0, badge.height - effective_radius * 2, effective_radius * 2, badge.height], 90, 180, fill=255)
                border_draw.pieslice([badge.width - effective_radius * 2, badge.height - effective_radius * 2, badge.width, badge.height], 0, 90, fill=255)
                border_draw.rectangle([effective_radius, 0, badge.width - effective_radius, badge.height], fill=255)
                border_draw.rectangle([0, effective_radius, badge.width, badge.height - effective_radius], fill=255)
                
                # Draw inner rounded rectangle (to cut out center)
                inner_radius = max(0, effective_radius - border_width)
                inner_padding = border_width
                
                # Only draw inner mask if border is thick enough
                if inner_radius > 0 and badge.width > 2 * border_width and badge.height > 2 * border_width:
                    border_draw.pieslice([inner_padding, inner_padding, inner_padding + inner_radius * 2, inner_padding + inner_radius * 2], 180, 270, fill=0)
                    border_draw.pieslice([badge.width - inner_padding - inner_radius * 2, inner_padding, badge.width - inner_padding, inner_padding + inner_radius * 2], 270, 0, fill=0)
                    border_draw.pieslice([inner_padding, badge.height - inner_padding - inner_radius * 2, inner_padding + inner_radius * 2, badge.height - inner_padding], 90, 180, fill=0)
                    border_draw.pieslice([badge.width - inner_padding - inner_radius * 2, badge.height - inner_padding - inner_radius * 2, badge.width - inner_padding, badge.height - inner_padding], 0, 90, fill=0)
                    border_draw.rectangle([inner_padding + inner_radius, inner_padding, badge.width - inner_padding - inner_radius, badge.height - inner_padding], fill=0)
                    border_draw.rectangle([inner_padding, inner_padding + inner_radius, badge.width - inner_padding, badge.height - inner_padding - inner_radius], fill=0)
                
                # Create border overlay
                border_overlay = Image.new('RGBA', badge.size, border_color)
                
                # Apply border mask to overlay
                styled_badge = Image.composite(border_overlay, styled_badge, border_mask)
        except Exception as e:
            # Fall back to simple rectangle if rounded corners fail
            print(f"⚠️ Warning: Error creating rounded corners: {e}, falling back to rectangle")
            draw.rectangle([(0, 0), (badge.width, badge.height)], fill=background_color)
            draw.rectangle(
                [(border_width//2, border_width//2), 
                 (badge.width-border_width//2, badge.height-border_width//2)], 
                outline=border_color, 
                width=border_width
            )
    else:
        # Simple rectangle without rounded corners
        draw.rectangle([(0, 0), (badge.width, badge.height)], fill=background_color)
        draw.rectangle(
            [(border_width//2, border_width//2), 
             (badge.width-border_width//2, badge.height-border_width//2)], 
            outline=border_color, 
            width=border_width
        )
    
    # Now composite the original image content over our styled background if it has content
    if has_content:
        # For image badges, we want to extract just the non-transparent parts of the original
        # Create a mask from the alpha channel of the original image
        orig_mask = badge.split()[3] if badge.mode == 'RGBA' else Image.new('L', badge.size, 255)
        
        # Create a result with just the styled background
        result = styled_badge.copy()
        
        # Calculate the center position to place the original content
        x_offset = (styled_badge.width - badge.width) // 2
        y_offset = (styled_badge.height - badge.height) // 2
        
        # Paste only the non-transparent parts of the original image
        # This prevents any black boxes or backgrounds from the original image
        result.paste(badge, (x_offset, y_offset), orig_mask)
        return result
    else:
        # If there's no content, just return the styled badge
        return styled_badge

def _add_text_to_badge(badge, text, font, settings):
    """Add text to the badge image."""
    try:
        # Create a new draw object 
        draw = ImageDraw.Draw(badge)
        
        # Position text in center of badge
        # Get accurate text dimensions via textbbox
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except Exception as e:
            print(f"⚠️ Error measuring text: {e}")
            print(f"  Text: '{text}', Font: {font}")
            return badge
        
        # Calculate exact center position for perfect centering
        # Adjust for the text's actual baseline and offset
        text_x = (badge.width - text_width) // 2
        text_y = (badge.height - text_height) // 2 - bbox[1]
        
        # Create a new draw object if we used rounded corners (original might be invalid)
        text_overlay = Image.new('RGBA', badge.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_overlay)
        
        # Get text color from settings or default to white
        text_color_hex = settings.get('Text', {}).get('text-color', '#FFFFFF')
        text_color = hex_to_rgba(text_color_hex, 100)  # Full opacity for text
        print(f"📝 Text color: {text_color_hex} -> {text_color}")
        
        text_draw.text((text_x, text_y), text, fill=text_color, font=font)
        badge = Image.alpha_composite(badge, text_overlay)
        
        return badge
    except Exception as e:
        print(f"⚠️ Warning: Could not add text to badge: {e}")
        return badge

def _apply_shadow(badge, settings, border_radius):
    """Apply shadow effect to the badge."""
    try:
        shadow_blur = settings.get('Shadow', {}).get('shadow_blur', 5)
        shadow_offset_x = settings.get('Shadow', {}).get('shadow_offset_x', 2)
        shadow_offset_y = settings.get('Shadow', {}).get('shadow_offset_y', 2)
        
        # For rounded corners, create a shadow with the same mask
        if border_radius > 0:
            # Create a shadow by using the same mask as the badge
            shadow = Image.new('RGBA', badge.size, (0, 0, 0, 0))
            shadow_base = Image.new('RGBA', badge.size, (0, 0, 0, 100))  # Semi-transparent black
            
            # Recreate the mask for consistency
            shadow_mask = Image.new('L', badge.size, 0)
            shadow_mask_draw = ImageDraw.Draw(shadow_mask)
            
            effective_radius = min(border_radius, badge.width // 4, badge.height // 4)
            shadow_mask_draw.pieslice([0, 0, effective_radius * 2, effective_radius * 2], 180, 270, fill=255)
            shadow_mask_draw.pieslice([badge.width - effective_radius * 2, 0, badge.width, effective_radius * 2], 270, 0, fill=255)
            shadow_mask_draw.pieslice([0, badge.height - effective_radius * 2, effective_radius * 2, badge.height], 90, 180, fill=255)
            shadow_mask_draw.pieslice([badge.width - effective_radius * 2, badge.height - effective_radius * 2, badge.width, badge.height], 0, 90, fill=255)
            shadow_mask_draw.rectangle([effective_radius, 0, badge.width - effective_radius, badge.height], fill=255)
            shadow_mask_draw.rectangle([0, effective_radius, badge.width, badge.height - effective_radius], fill=255)
            
            # Use the mask for the shadow
            shadow = Image.composite(shadow_base, shadow, shadow_mask)
        else:
            # Simple shadow for rectangular badges
            shadow = Image.new('RGBA', badge.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rectangle([(0, 0), (badge.width, badge.height)], fill=(0, 0, 0, 100))
        
        # Apply blur to the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Create a composite with the shadow and the badge
        composite_width = badge.width + abs(shadow_offset_x) + shadow_blur
        composite_height = badge.height + abs(shadow_offset_y) + shadow_blur
        composite = Image.new('RGBA', (composite_width, composite_height), (0, 0, 0, 0))
        
        # Calculate positions for shadow and badge
        shadow_x = max(0, shadow_offset_x)
        shadow_y = max(0, shadow_offset_y)
        badge_x = max(0, -shadow_offset_x)
        badge_y = max(0, -shadow_offset_y)
        
        # Paste shadow and badge
        composite.paste(shadow, (shadow_x, shadow_y), shadow)
        composite.paste(badge, (badge_x, badge_y), badge)
        
        return composite
    except Exception as e:
        print(f"⚠️ Warning: Error creating shadow: {e}, returning badge without shadow")
        return badge
