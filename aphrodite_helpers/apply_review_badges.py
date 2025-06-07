#!/usr/bin/env python3
# aphrodite_helpers/apply_review_badges.py

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFilter

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.badge_components.badge_settings import load_badge_settings
from aphrodite_helpers.badge_components.badge_generator import create_badge
from aphrodite_helpers.badge_components.color_utils import hex_to_rgba
from aphrodite_helpers.badge_components.font_utils import load_font
from aphrodite_helpers.poster_fetcher import download_poster

# Import enhanced ReviewFetcher
try:
    # Try to import the enhanced version
    from production_anime_mapping import enhance_review_fetcher
    from aphrodite_helpers.get_review_info import ReviewFetcher as BaseReviewFetcher
    ReviewFetcher = enhance_review_fetcher(BaseReviewFetcher)
    print("✅ Using enhanced ReviewFetcher with comprehensive anime mapping")
except Exception as e:
    # Fallback to original ReviewFetcher
    from aphrodite_helpers.get_review_info import ReviewFetcher
    print(f"⚠️ Using original ReviewFetcher: {e}")
from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.badge_components.badge_image_handler import load_codec_image
from aphrodite_helpers.review_preferences import ReviewPreferences

def apply_badge_to_poster(
    poster_path, 
    badge, 
    settings, 
    working_dir="posters/working", 
    output_dir="posters/modified"
):
    """Apply a single badge to a poster image and save to output directory."""
    # Create full paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(root_dir, working_dir), exist_ok=True)
    os.makedirs(os.path.join(root_dir, output_dir), exist_ok=True)
    
    working_path = os.path.join(root_dir, working_dir, os.path.basename(poster_path))
    output_path = os.path.join(root_dir, output_dir, os.path.basename(poster_path))
    
    # Make sure we have the poster in memory
    try:
        poster = Image.open(poster_path).convert("RGBA")
    except Exception as e:
        print(f"❌ Error opening poster file {poster_path}: {e}")
        return None
    
    # Get badge settings
    position = settings.get('General', {}).get('general_badge_position', 'bottom-right')
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
    elif position == 'top-center':
        coords = ((poster.width - badge.width) // 2, edge_padding)
    elif position == 'center-left':
        coords = (edge_padding, (poster.height - badge.height) // 2)
    elif position == 'center':
        coords = ((poster.width - badge.width) // 2, (poster.height - badge.height) // 2)
    elif position == 'center-right':
        coords = (poster.width - badge.width - edge_padding, (poster.height - badge.height) // 2)
    elif position == 'bottom-center':
        coords = ((poster.width - badge.width) // 2, poster.height - badge.height - edge_padding)
    else:
        # Default to bottom-right
        coords = (poster.width - badge.width - edge_padding, poster.height - badge.height - edge_padding)
    
    try:
        # Paste the badge onto the poster
        poster.paste(badge, coords, badge)
        
        # Save the modified poster
        poster.convert("RGB").save(output_path, "JPEG")
        print(f"✅ Badge applied to {os.path.basename(poster_path)}")
        
        return output_path
    except Exception as e:
        print(f"❌ Error applying badge to {os.path.basename(poster_path)}: {e}")
        return None

def create_review_container(reviews, settings):
    """
    Create a single container badge that holds all review badges inside.
    The container uses styling from the settings file, and each review
    shows a logo and rating side by side.
    """
    # Get max badges from user preferences (database) if available, otherwise fallback to badge settings
    try:
        preferences = ReviewPreferences()
        max_badges = preferences.get_max_badges_to_display()
        print(f"🔍 Using database setting for max badges: {max_badges}")
    except Exception as e:
        print(f"⚠️ Could not load max badges from database, using badge settings: {e}")
        max_badges = settings.get('General', {}).get('max_badges_to_display', 3)
    
    reviews_to_process = reviews[:max_badges] if max_badges > 0 else reviews
    
    if not reviews_to_process:
        print(f"⚠️ No reviews to display")
        return None
    
    # Get settings for the container
    badge_orientation = settings.get('General', {}).get('badge_orientation', 'vertical')
    badge_spacing = settings.get('General', {}).get('badge_spacing', 1)
    padding = settings.get('General', {}).get('general_text_padding', 12)
    
    # Get color and style settings
    background_color_hex = settings.get('Background', {}).get('background-color', '#2C2C2C')
    background_opacity = settings.get('Background', {}).get('background_opacity', 80)
    background_color = hex_to_rgba(background_color_hex, background_opacity)
    
    border_color_hex = settings.get('Border', {}).get('border-color', '#FFFFFF')
    border_width = settings.get('Border', {}).get('border_width', 1)
    border_radius = settings.get('Border', {}).get('border-radius', 10)
    border_color = hex_to_rgba(border_color_hex, 100)  # Full opacity for border
    
    shadow_enabled = settings.get('Shadow', {}).get('shadow_enable', False)
    shadow_blur = settings.get('Shadow', {}).get('shadow_blur', 5)
    shadow_offset_x = settings.get('Shadow', {}).get('shadow_offset_x', 2)
    shadow_offset_y = settings.get('Shadow', {}).get('shadow_offset_y', 2)
    
    # Load the font for rating text
    font_family = settings.get('Text', {}).get('font', "AvenirNextLTProBold.otf")
    fallback_font = settings.get('Text', {}).get('fallback_font', "DejaVuSans.ttf")
    font_size = settings.get('Text', {}).get('text-size', 40)
    text_color_hex = settings.get('Text', {}).get('text-color', '#FFFFFF')
    text_color = hex_to_rgba(text_color_hex, 100)  # Full opacity for text
    font = load_font(font_family, fallback_font, font_size)
    
    # Create image elements for each review
    review_elements = []
    for review in reviews_to_process:
        source = review.get("source", "")
        rating = review.get("text", "")
        image_key = review.get("image_key", None)
        
        print(f"🔍 Processing review for {source}: {rating} with image_key={image_key}")
        
        # Try to load the logo
        logo_image = None
        if image_key:
            try:
                logo_image = load_codec_image(image_key, settings)
            except Exception as e:
                print(f"⚠️ Error loading logo for {source}: {e}")
        
        if logo_image:
            review_elements.append({
                "source": source,
                "rating": str(rating),
                "logo": logo_image
            })
    
    if not review_elements:
        print(f"⚠️ No review elements could be created")
        return None
    
    # Calculate container dimensions
    inner_padding = padding  # Padding inside the container
    logo_rating_spacing = 10  # Space between logo and rating
    
    # Measure text dimensions for all ratings
    temp_img = Image.new('RGBA', (500, 100), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Calculate sizes for each element and the full container
    if badge_orientation == 'horizontal':
        # For horizontal layout, reviews are side by side
        container_width = inner_padding * 2  # Start with left and right padding
        container_height = 0
        
        for i, element in enumerate(review_elements):
            logo = element["logo"]
            rating_text = element["rating"]
            
            # Calculate text size
            try:
                rating_bbox = temp_draw.textbbox((0, 0), rating_text, font=font)
                rating_width = rating_bbox[2] - rating_bbox[0]
                rating_height = rating_bbox[3] - rating_bbox[1]
            except Exception as e:
                print(f"⚠️ Error measuring text: {e}")
                rating_width = font_size * len(rating_text) * 0.6
                rating_height = font_size * 1.2
            
            # Calculate total width for this review (logo + spacing + rating)
            element_width = logo.width + logo_rating_spacing + rating_width
            element_height = max(logo.height, rating_height)
            
            # Update element with size information
            element["width"] = element_width
            element["height"] = element_height
            element["rating_width"] = rating_width
            element["rating_height"] = rating_height
            
            # Add to container width
            container_width += element_width
            if i < len(review_elements) - 1:
                container_width += badge_spacing  # Add spacing between reviews
            
            # Update container height if needed
            container_height = max(container_height, element_height + inner_padding * 2)
    else:  # vertical layout
        # For vertical layout, reviews are stacked with logos above text
        container_width = 0
        
        # Increased top and bottom padding for the container
        top_padding = inner_padding * 2  # Extra padding at the top
        bottom_padding = inner_padding * 2  # Extra padding at the bottom
        container_height = top_padding + bottom_padding  # Start with combined padding
        
        for i, element in enumerate(review_elements):
            logo = element["logo"]
            rating_text = element["rating"]
            
            # Calculate text size
            try:
                rating_bbox = temp_draw.textbbox((0, 0), rating_text, font=font)
                rating_width = rating_bbox[2] - rating_bbox[0]
                rating_height = rating_bbox[3] - rating_bbox[1]
            except Exception as e:
                print(f"⚠️ Error measuring text: {e}")
                rating_width = font_size * len(rating_text) * 0.6
                rating_height = font_size * 1.2
            
            # In vertical orientation, we stack logo above text
            # Each element needs enough width for the wider of logo or text
            element_width = max(logo.width, rating_width)
            # Height is logo + spacing + text height
            element_height = logo.height + 15 + rating_height  # Increased from 5 to 15px spacing
            
            # Update element with size information
            element["width"] = element_width
            element["height"] = element_height
            element["rating_width"] = rating_width
            element["rating_height"] = rating_height
            
            # Update container dimensions
            container_width = max(container_width, element_width + inner_padding * 2)
            container_height += element_height
            if i < len(review_elements) - 1:
                container_height += badge_spacing * 3  # Apply 3x multiplier for vertical spacing
    
    # Create the container image
    container = Image.new('RGBA', (container_width, container_height), (0, 0, 0, 0))
    container_draw = ImageDraw.Draw(container)
    
    # Draw the background with rounded corners if needed
    if border_radius > 0:
        # Create a mask for the rounded rectangle
        mask = Image.new('L', (container_width, container_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle on the mask
        effective_radius = min(border_radius, container_width // 4, container_height // 4)
        
        # Draw corners
        mask_draw.pieslice([0, 0, effective_radius * 2, effective_radius * 2], 180, 270, fill=255)
        mask_draw.pieslice([container_width - effective_radius * 2, 0, container_width, effective_radius * 2], 270, 0, fill=255)
        mask_draw.pieslice([0, container_height - effective_radius * 2, effective_radius * 2, container_height], 90, 180, fill=255)
        mask_draw.pieslice([container_width - effective_radius * 2, container_height - effective_radius * 2, container_width, container_height], 0, 90, fill=255)
        
        # Fill in the center
        mask_draw.rectangle([effective_radius, 0, container_width - effective_radius, container_height], fill=255)
        mask_draw.rectangle([0, effective_radius, container_width, container_height - effective_radius], fill=255)
        
        # Create background and apply mask
        background = Image.new('RGBA', (container_width, container_height), background_color)
        container = Image.composite(background, container, mask)
        
        # Draw border if needed
        if border_width > 0:
            border_mask = Image.new('L', (container_width, container_height), 0)
            border_draw = ImageDraw.Draw(border_mask)
            
            # Draw outer rounded rectangle
            border_draw.pieslice([0, 0, effective_radius * 2, effective_radius * 2], 180, 270, fill=255)
            border_draw.pieslice([container_width - effective_radius * 2, 0, container_width, effective_radius * 2], 270, 0, fill=255)
            border_draw.pieslice([0, container_height - effective_radius * 2, effective_radius * 2, container_height], 90, 180, fill=255)
            border_draw.pieslice([container_width - effective_radius * 2, container_height - effective_radius * 2, container_width, container_height], 0, 90, fill=255)
            border_draw.rectangle([effective_radius, 0, container_width - effective_radius, container_height], fill=255)
            border_draw.rectangle([0, effective_radius, container_width, container_height - effective_radius], fill=255)
            
            # Draw inner rounded rectangle (to cut out center)
            inner_radius = max(0, effective_radius - border_width)
            inner_padding = border_width
            
            # Only draw inner mask if border is thick enough
            if inner_radius > 0 and container_width > 2 * border_width and container_height > 2 * border_width:
                border_draw.pieslice([inner_padding, inner_padding, inner_padding + inner_radius * 2, inner_padding + inner_radius * 2], 180, 270, fill=0)
                border_draw.pieslice([container_width - inner_padding - inner_radius * 2, inner_padding, container_width - inner_padding, inner_padding + inner_radius * 2], 270, 0, fill=0)
                border_draw.pieslice([inner_padding, container_height - inner_padding - inner_radius * 2, inner_padding + inner_radius * 2, container_height - inner_padding], 90, 180, fill=0)
                border_draw.pieslice([container_width - inner_padding - inner_radius * 2, container_height - inner_padding - inner_radius * 2, container_width - inner_padding, container_height - inner_padding], 0, 90, fill=0)
                border_draw.rectangle([inner_padding + inner_radius, inner_padding, container_width - inner_padding - inner_radius, container_height - inner_padding], fill=0)
                border_draw.rectangle([inner_padding, inner_padding + inner_radius, container_width - inner_padding, container_height - inner_padding - inner_radius], fill=0)
            
            # Create border overlay
            border_overlay = Image.new('RGBA', (container_width, container_height), border_color)
            
            # Apply border mask to overlay and composite
            border_overlay_masked = Image.composite(border_overlay, Image.new('RGBA', (container_width, container_height), (0, 0, 0, 0)), border_mask)
            container = Image.alpha_composite(container, border_overlay_masked)
    else:
        # Simple rectangle without rounded corners
        container_draw.rectangle([(0, 0), (container_width, container_height)], fill=background_color)
        if border_width > 0:
            container_draw.rectangle(
                [(border_width//2, border_width//2), (container_width - border_width//2, container_height - border_width//2)],
                outline=border_color,
                width=border_width
            )
    
    # We need a new drawing context after the masking operations
    container_draw = ImageDraw.Draw(container)
    
    # Place each review element in the container
    if badge_orientation == 'horizontal':
        # Horizontal layout, place elements side by side
        
        # Calculate total width of all elements with spacing
        total_elements_width = sum(element["width"] for element in review_elements)
        total_elements_width += badge_spacing * (len(review_elements) - 1)  # Add spacing between elements
        
        # Center all elements horizontally in the container
        # Start position for first element
        current_x = (container_width - total_elements_width) // 2
        
        for element in review_elements:
            logo = element["logo"]
            rating_text = element["rating"]
            element_height = element["height"]
            rating_height = element["rating_height"]
            
            # Vertical centering
            y_position = (container_height - element_height) // 2
            
            # Place the logo
            logo_y = y_position + (element_height - logo.height) // 2
            container.paste(logo, (current_x, logo_y), logo)
            
            # Draw the rating text next to the logo
            rating_x = current_x + logo.width + logo_rating_spacing
            rating_y = y_position + (element_height - rating_height) // 2
            container_draw.text((rating_x, rating_y), rating_text, fill=text_color, font=font)
            
            # Move to the next element position
            current_x += element["width"] + badge_spacing
    else:
        # Vertical layout, stack elements
        current_y = top_padding  # Start at the increased top padding value
        
        for element in review_elements:
            logo = element["logo"]
            rating_text = element["rating"]
            rating_width = element["rating_width"]
            rating_height = element["rating_height"]
            
            # Center the logo horizontally
            logo_x = (container_width - logo.width) // 2
            container.paste(logo, (logo_x, current_y), logo)
            
            # Draw the rating text below the logo, centered horizontally
            rating_x = (container_width - rating_width) // 2
            rating_y = current_y + logo.height + 15  # Increased from 10 to 15px spacing between logo and text
            container_draw.text((rating_x, rating_y), rating_text, fill=text_color, font=font)
            
            # Calculate total element height (logo + spacing + text)
            total_element_height = logo.height + 15 + rating_height
            
            # Move to the next element position
            # Apply a 3x multiplier to badge_spacing for vertical layout to make it more noticeable
            current_y += total_element_height + (badge_spacing * 3)
    
    # Apply shadow if enabled
    if shadow_enabled:
        # Create shadow
        shadow = Image.new('RGBA', container.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(0, 0), container.size], fill=(0, 0, 0, 100))
        
        # Apply blur to shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Create a new image with room for the shadow
        shadow_offset = max(abs(shadow_offset_x), abs(shadow_offset_y)) + shadow_blur
        composite_width = container.width + shadow_offset * 2
        composite_height = container.height + shadow_offset * 2
        composite = Image.new('RGBA', (composite_width, composite_height), (0, 0, 0, 0))
        
        # Position shadow and badge
        shadow_x = shadow_offset + shadow_offset_x
        shadow_y = shadow_offset + shadow_offset_y
        badge_x = shadow_offset
        badge_y = shadow_offset
        
        # Paste shadow and badge
        composite.paste(shadow, (shadow_x, shadow_y), shadow)
        composite.paste(container, (badge_x, badge_y), container)
        
        return composite
    
    return container

def process_item_reviews(
    item_id, 
    jellyfin_url, 
    api_key, 
    user_id,
    settings_file="badge_settings_review.yml",
    output_dir="posters/modified",
    input_poster=None  # New parameter to accept an already processed poster
):
    """Process reviews for a Jellyfin item, create badges, and apply to poster."""
    try:
        # Load badge settings
        badge_settings = load_badge_settings(settings_file)
        if not badge_settings:
            print(f"❌ Failed to load badge settings from {settings_file}")
            return False
        
        # Create review fetcher
        settings = load_settings()
        if not settings:
            print(f"❌ Failed to load main settings")
            return False
            
        review_fetcher = ReviewFetcher(settings)
        
        # Get reviews
        reviews = review_fetcher.get_reviews(item_id)
        if not reviews:
            print(f"❌ No reviews found for item ID: {item_id}")
            return False
        
        print(f"✅ Found {len(reviews)} reviews")
    except Exception as e:
        print(f"❌ Error during review setup: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
    try:
        # Create container with all review badges
        container_badge = create_review_container(reviews, badge_settings)
        if not container_badge:
            print(f"❌ Failed to create review container")
            return False
        
        # Use the provided poster if available, otherwise download from Jellyfin
        poster_path = input_poster
        if not poster_path or not os.path.exists(poster_path):
            # Download poster
            poster_path = download_poster(jellyfin_url, api_key, item_id)
            if not poster_path:
                print(f"❌ Failed to download poster for item ID: {item_id}")
                return False
            
            # If we downloaded a new poster (not using the input one), resize it
            try:
                # Create a path for the resized poster
                resized_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "posters", "working",
                    os.path.basename(poster_path)
                )
                
                # Import resize function only when needed to avoid circular imports
                from aphrodite_helpers.resize_posters import resize_image
                
                # Resize the poster for consistent badge sizing
                resize_success = resize_image(poster_path, resized_path, target_width=1000)
                if resize_success:
                    print(f"✅ Resized downloaded poster to 1000px width")
                    poster_path = resized_path
            except Exception as e:
                print(f"⚠️ Error resizing poster: {str(e)}. Continuing with original size.")
                # Continue with original poster path
        
        # Verify we have a valid poster path before proceeding
        if not poster_path or not os.path.exists(poster_path):
            print(f"❌ Invalid or missing poster path")
            return False
        
        # Apply container badge to poster
        result = apply_badge_to_poster(
            poster_path=poster_path,
            badge=container_badge,
            settings=badge_settings,
            working_dir="posters/working",  # Explicitly set working directory
            output_dir=output_dir           # Use output dir from parameters
        )
        
        print(f"\nReview badge output path: {result}")
        
        # Check if the result is None, which indicates an error
        if result is None:
            print(f"❌ Error applying review badge to poster")
            return False
        else:
            # Ensure the output file exists
            if os.path.exists(result):
                return True
            else:
                print(f"❌ Review badge was created but the output file doesn't exist: {result}")
                return False
    except Exception as e:
        print(f"❌ Unexpected error during review badge processing: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    parser = argparse.ArgumentParser(description="Apply review badges to Jellyfin media posters")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--settings", default="badge_settings_review.yml", help="Badge settings file")
    parser.add_argument("--output", default="posters/modified", help="Output directory for modified posters")
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    if not settings:
        return 1
    
    jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
    
    # Process the item
    success = process_item_reviews(
        args.itemid,
        jellyfin_settings.get("url", ""),
        jellyfin_settings.get("api_key", ""),
        jellyfin_settings.get("user_id", ""),
        args.settings,
        args.output
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
