#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_applicator.py

import os
import shutil
from PIL import Image

def calculate_dynamic_padding(poster_width, poster_height, base_padding, reference_aspect_ratio=2/3):
    """
    Calculate dynamic padding based on poster aspect ratio.
    
    Args:
        poster_width (int): Width of the poster
        poster_height (int): Height of the poster
        base_padding (int): Base padding from settings (for reference aspect ratio)
        reference_aspect_ratio (float): Reference aspect ratio (default: 2:3 = 0.67)
    
    Returns:
        int: Calculated dynamic padding
    """
    # Calculate current aspect ratio
    current_aspect_ratio = poster_width / poster_height
    
    # Calculate padding as a percentage of the reference dimension
    # For the reference aspect ratio, use base_padding as-is
    # For other ratios, scale the padding to maintain visual consistency
    
    # Use height as the scaling dimension since that's what varies most
    # Calculate what the height would be for reference ratio at current width
    reference_height = poster_width / reference_aspect_ratio
    
    # Calculate the padding as a percentage of the reference height
    padding_percentage = base_padding / reference_height
    
    # Apply this percentage to the actual poster height
    dynamic_padding = int(padding_percentage * poster_height)
    
    # Ensure minimum and maximum padding bounds
    min_padding = max(10, base_padding // 3)  # At least 10px, or 1/3 of base
    max_padding = base_padding * 2  # At most 2x the base padding
    
    dynamic_padding = max(min_padding, min(max_padding, dynamic_padding))
    
    return dynamic_padding

def apply_badge_to_poster(
    poster_path, 
    badge, 
    settings, 
    working_dir="posters/working", 
    output_dir="posters/modified"
):
    """Apply the badge to a poster image and save to output directory."""
    # Create full paths
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    working_path = os.path.join(root_dir, working_dir, os.path.basename(poster_path))
    output_path = os.path.join(root_dir, output_dir, os.path.basename(poster_path))
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(working_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Only copy to working directory if the source is not already there
    if os.path.normpath(poster_path) != os.path.normpath(working_path):
        try:
            shutil.copy2(poster_path, working_path)
        except (shutil.SameFileError, PermissionError) as e:
            print(f"ℹ️ Copy skipped: {e}")
            # If we can't copy, but working_path exists, we'll try to use it
            if not os.path.exists(working_path):
                print(f"❌ No working file available at {working_path}")
                return None
    else:
        print(f"ℹ️ Poster already in working directory, skipping copy")
    
    try:
        # Open the poster
        poster = Image.open(working_path).convert("RGBA")
        
        # Get badge position from settings
        position = settings.get('General', {}).get('general_badge_position', 'top-left')
        base_edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
        
        # Calculate dynamic padding based on aspect ratio
        edge_padding = calculate_dynamic_padding(poster.width, poster.height, base_edge_padding)
        
        # Debug info
        aspect_ratio = poster.width / poster.height
        print(f"ℹ️ Poster: {poster.width}x{poster.height} (ratio: {aspect_ratio:.2f}), Base padding: {base_edge_padding}px, Dynamic padding: {edge_padding}px")
        
        # Calculate position coordinates
        if position == 'top-left':
            coords = (edge_padding, edge_padding)
        elif position == 'top-right':
            coords = (poster.width - badge.width - edge_padding, edge_padding)
        elif position == 'bottom-left':
            coords = (edge_padding, poster.height - badge.height - edge_padding)
        elif position == 'bottom-right':
            coords = (poster.width - badge.width - edge_padding, poster.height - badge.height - edge_padding)
        # New positions
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
        elif position == 'bottom-right-flush':
            # Flush positioning ignores edge padding and places badge at exact corner
            coords = (poster.width - badge.width, poster.height - badge.height)
        else:
            # Default to top-left
            coords = (edge_padding, edge_padding)
        
        # Paste the badge onto the poster
        poster.paste(badge, coords, badge)
        
        # Save the modified poster
        poster.convert("RGB").save(output_path, "JPEG")
        print(f"✅ Badge applied to {os.path.basename(poster_path)}")
        
        # Remove the working file if it's different from the original path
        # and different from the output path
        if (os.path.normpath(working_path) != os.path.normpath(poster_path) and 
            os.path.normpath(working_path) != os.path.normpath(output_path) and 
            os.path.exists(working_path)):
            try:
                os.remove(working_path)
                print(f"ℹ️ Cleaned up working file: {os.path.basename(working_path)}")
            except Exception as e:
                print(f"ℹ️ Could not clean up working file: {e}")
        
        return output_path
    except Exception as e:
        print(f"❌ Error applying badge to {os.path.basename(poster_path)}: {e}")
        # Clean up working file in case of error
        if (os.path.normpath(working_path) != os.path.normpath(poster_path) and 
            os.path.exists(working_path)):
            try:
                os.remove(working_path)
            except Exception as clean_error:
                print(f"ℹ️ Could not clean up working file: {clean_error}")
        return None

def process_posters(
    badge,
    settings,
    poster_dir="posters/original", 
    working_dir="posters/working", 
    output_dir="posters/modified"
):
    """Process all posters in the specified directory with the given badge."""
    # Get all poster files
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    return processed_count > 0
