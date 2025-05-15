#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_applicator.py

import os
import shutil
from PIL import Image

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
