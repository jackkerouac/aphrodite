#!/usr/bin/env python3
# aphrodite_helpers/apply_badge.py

import os
import sys
import yaml
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_badge_settings(settings_file="badge_settings_audio.yml"):
    """Load badge settings from the provided YAML file."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, settings_file)
    
    try:
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: Badge settings file {settings_file} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing badge settings: {e}")
        return None

def hex_to_rgba(hex_color, opacity=100):
    """Convert hex color to RGBA tuple."""
    if not hex_color.startswith('#'):
        return (255, 0, 0, int(255 * opacity / 100))  # Default red with opacity
    
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, int(255 * opacity / 100))
    elif len(hex_color) == 3:
        r, g, b = tuple(int(hex_color[i] + hex_color[i], 16) for i in range(3))
        return (r, g, b, int(255 * opacity / 100))
    else:
        return (255, 0, 0, int(255 * opacity / 100))  # Default red with opacity

def create_badge(settings, text=None):
    """Create a badge based on the settings, optionally with text."""
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
    text_padding = 12  # Pixels of padding on all sides
    
    # Create initial dimensions based on text if provided
    if text:
        try:
            # Try to load a font
            try:
                # For Windows, a standard font
                font_path = "arial.ttf"
                font_size = 20  # Starting font size
                font = ImageFont.truetype(font_path, size=font_size)
            except IOError:
                # Default PIL font if standard font not found
                font = ImageFont.load_default()
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
            badge = Image.new('RGBA', (default_badge_size, default_badge_size), (0, 0, 0, 0))
    else:
        # If no text, use default badge size
        badge = Image.new('RGBA', (default_badge_size, default_badge_size), (0, 0, 0, 0))
    
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
    
    # Draw rounded rectangle for the badge background (currently simple rectangle for PIL compatibility)
    # TODO: Implement proper rounded corners if needed
    draw.rectangle([(0, 0), (badge.width, badge.height)], fill=background_color)
    
    # Draw border
    draw.rectangle(
        [(border_width//2, border_width//2), 
         (badge.width-border_width//2, badge.height-border_width//2)], 
        outline=border_color, 
        width=border_width
    )
    
    # Add text if provided
    if text:
        try:
            # Position text in center of badge
            # Get accurate text dimensions via textbbox
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate exact center position for perfect centering
            # Adjust for the text's actual baseline and offset
            text_x = (badge.width - text_width) // 2
            text_y = (badge.height - text_height) // 2 - bbox[1]
            
            # Draw text with white color (for contrast)
            draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        except Exception as e:
            print(f"⚠️ Warning: Could not add text to badge: {e}")
    
    # Apply shadow if enabled
    shadow_enabled = settings.get('Shadow', {}).get('shadow_enable', False)
    if shadow_enabled:
        shadow_blur = settings.get('Shadow', {}).get('shadow_blur', 5)
        # Create a shadow by blurring a black version of the badge
        shadow = Image.new('RGBA', badge.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(0, 0), (badge.width, badge.height)], fill=(0, 0, 0, 100))
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Create a composite with the shadow and the badge
        composite = Image.new('RGBA', badge.size, (0, 0, 0, 0))
        shadow_offset_x = settings.get('Shadow', {}).get('shadow_offset_x', 2)
        shadow_offset_y = settings.get('Shadow', {}).get('shadow_offset_y', 2)
        composite.paste(shadow, (shadow_offset_x, shadow_offset_y), shadow)
        composite.paste(badge, (0, 0), badge)
        return composite
        
    return badge

def apply_badge_to_poster(
    poster_path, 
    badge, 
    settings, 
    working_dir="posters/working", 
    output_dir="posters/modified"
):
    """Apply the badge to a poster image and save to output directory."""
    # Create full paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    working_path = os.path.join(root_dir, working_dir, os.path.basename(poster_path))
    output_path = os.path.join(root_dir, output_dir, os.path.basename(poster_path))
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(working_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Copy to working directory
    shutil.copy2(poster_path, working_path)
    
    try:
        # Open the poster
        poster = Image.open(working_path).convert("RGBA")
        
        # Get badge position from settings
        position = settings.get('General', {}).get('general_badge_position', 'top-left')
        edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
        
        # Calculate position coordinates
        if position == 'top-left':
            coords = (edge_padding, edge_padding)
        elif position == 'top-right':
            coords = (poster.width - badge.width - edge_padding, edge_padding)
        elif position == 'bottom-left':
            coords = (edge_padding, poster.height - badge.height - edge_padding)
        elif position == 'bottom-right':
            coords = (poster.width - badge.width - edge_padding, poster.height - badge.height - edge_padding)
        else:
            # Default to top-left
            coords = (edge_padding, edge_padding)
        
        # Paste the badge onto the poster
        poster.paste(badge, coords, badge)
        
        # Save the modified poster
        poster.convert("RGB").save(output_path, "JPEG")
        print(f"✅ Badge applied to {os.path.basename(poster_path)}")
        
        # Remove the working file
        os.remove(working_path)
        
        return output_path
    except Exception as e:
        print(f"❌ Error applying badge to {os.path.basename(poster_path)}: {e}")
        # Clean up working file in case of error
        if os.path.exists(working_path):
            os.remove(working_path)
        return None


def download_and_badge_poster(
    jellyfin_url, 
    api_key, 
    item_id, 
    badge_text=None, 
    output_dir="posters/modified", 
    settings_file="badge_settings_audio.yml"
):
    """Download a poster from Jellyfin, apply a badge with text, and save it."""
    # Import poster_fetcher here to avoid circular imports
    from aphrodite_helpers.poster_fetcher import download_poster
    
    # Load badge settings
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
    
    # Set up directories
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_dir = os.path.join(root_dir, "posters/original")
    working_dir = os.path.join(root_dir, "posters/working")
    output_dir = os.path.join(root_dir, output_dir)
    
    # Ensure directories exist
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the poster
    poster_path = download_poster(jellyfin_url, api_key, item_id, output_dir=original_dir)
    if not poster_path:
        print(f"❌ Failed to download poster for item {item_id}")
        return False
    
    # Create badge with text
    badge = create_badge(settings, badge_text)
    
    # Apply badge to poster
    result_path = apply_badge_to_poster(
        poster_path=poster_path,
        badge=badge,
        settings=settings,
        working_dir="posters/working",
        output_dir=output_dir
    )
    
    if result_path:
        print(f"✅ Successfully processed poster for item {item_id} with audio codec: {badge_text}")
        return True
    else:
        print(f"❌ Failed to process poster for item {item_id}")
        return False

def process_posters(
    poster_dir="posters/original", 
    working_dir="posters/working", 
    output_dir="posters/modified", 
    settings_file="badge_settings_audio.yml",
    badge_text=None
):
    """Process all posters in the specified directory."""
    # Load badge settings
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
    
    # Create the badge once
    badge = create_badge(settings, badge_text)
    
    # Get all poster files
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    poster_path = os.path.join(root_dir, poster_dir)
    
    if not os.path.exists(poster_path):
        print(f"❌ Poster directory {poster_path} not found.")
        return False
    
    poster_files = [os.path.join(poster_path, f) for f in os.listdir(poster_path) 
                   if os.path.isfile(os.path.join(poster_path, f)) and 
                   f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not poster_files:
        print(f"ℹ️ No poster images found in {poster_path}")
        return False
    
    # Process each poster
    processed_count = 0
    for poster_file in poster_files:
        if apply_badge_to_poster(poster_file, badge, settings, working_dir, output_dir):
            processed_count += 1
    
    print(f"\n✅ Processed {processed_count} of {len(poster_files)} posters")
    return True

def save_test_badge(settings_file="badge_settings_audio.yml", text=None):
    """Save a test badge to verify settings and implementation."""
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
        
    badge = create_badge(settings, text)
    
    # Save the badge
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_path = os.path.join(root_dir, "test_badge.png")
    
    # Convert to RGB if saving as JPG
    if test_path.lower().endswith('.jpg') or test_path.lower().endswith('.jpeg'):
        badge = badge.convert('RGB')
        
    badge.save(test_path)
    print(f"✅ Test badge saved to {test_path}")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Apply badges to poster images.")
    parser.add_argument(
        "--input", 
        default="posters/original", 
        help="Directory containing original posters"
    )
    parser.add_argument(
        "--working", 
        default="posters/working", 
        help="Working directory for temporary files"
    )
    parser.add_argument(
        "--output", 
        default="posters/modified", 
        help="Output directory for modified posters"
    )
    parser.add_argument(
        "--settings", 
        default="badge_settings_audio.yml", 
        help="Badge settings file"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Generate a test badge without processing posters"
    )
    parser.add_argument(
        "--text",
        help="Text to display in badge"
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = save_test_badge(args.settings, args.text)
    else:
        success = process_posters(
            poster_dir=args.input,
            working_dir=args.working,
            output_dir=args.output,
            settings_file=args.settings,
            badge_text=args.text
        )
    
    sys.exit(0 if success else 1)
