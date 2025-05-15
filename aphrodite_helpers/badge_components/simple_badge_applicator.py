#!/usr/bin/env python3
# aphrodite_helpers/badge_components/simple_badge_applicator.py

import os
from PIL import Image

def apply_badge_to_poster(poster_path, badge, position="top-right", padding=30, output_dir="posters/modified"):
    """Apply a badge to a poster image and save to output directory."""
    print(f"\nApplying badge to poster: {os.path.basename(poster_path)}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the output file path
    output_path = os.path.join(output_dir, os.path.basename(poster_path))
    
    try:
        # Open the poster
        poster = Image.open(poster_path).convert("RGBA")
        
        # Calculate position coordinates
        if position == 'top-left':
            coords = (padding, padding)
        elif position == 'top-right':
            coords = (poster.width - badge.width - padding, padding)
        elif position == 'bottom-left':
            coords = (padding, poster.height - badge.height - padding)
        elif position == 'bottom-right':
            coords = (poster.width - badge.width - padding, poster.height - badge.height - padding)
        else:
            # Default to top-right
            coords = (poster.width - badge.width - padding, padding)
        
        print(f"  Badge position: {position}, coordinates: {coords}")
        
        # Create a new image for the result
        result = Image.new("RGBA", poster.size, (0, 0, 0, 0))
        
        # Paste the poster
        result.paste(poster, (0, 0))
        
        # Paste the badge using its alpha channel as mask
        result.paste(badge, coords, badge)
        
        # Convert to RGB for JPEG
        result = result.convert("RGB")
        
        # Save the result
        result.save(output_path, "JPEG", quality=95)
        
        print(f"✅ Badge applied successfully, saved to: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Error applying badge: {e}")
        return None

def process_posters(badge, poster_dir="posters/original", output_dir="posters/modified"):
    """Process all posters in the specified directory with the given badge."""
    # Get all image files in the input directory
    if not os.path.exists(poster_dir):
        print(f"❌ Poster directory {poster_dir} not found.")
        return False
        
    poster_files = [f for f in os.listdir(poster_dir) 
                   if os.path.isfile(os.path.join(poster_dir, f)) and 
                   f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not poster_files:
        print(f"ℹ️ No poster images found in {poster_dir}")
        return False
    
    # Process each poster
    success_count = 0
    for poster_file in poster_files:
        poster_path = os.path.join(poster_dir, poster_file)
        if apply_badge_to_poster(poster_path, badge, output_dir=output_dir):
            success_count += 1
    
    print(f"\n✅ Successfully processed {success_count} of {len(poster_files)} posters")
    return success_count > 0
