#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_image_handler.py

from PIL import Image
import os
import sys

def get_codec_image_path(codec_text, settings):
    """
    Find the appropriate codec image based on the codec text and settings.
    
    Args:
        codec_text (str): The codec text (e.g., "DTS-HD MA 7.1")
        settings (dict): The badge settings
        
    Returns:
        str or None: Path to the matching image file, or None if no match found
    """
    # Get image badge settings
    image_settings = settings.get('ImageBadges', {})
    if not image_settings.get('enable_image_badges', False):
        return None
        
    # Get the codec image directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    image_dir = os.path.join(root_dir, image_settings.get('codec_image_directory', 'images/codec'))
    
    if not os.path.exists(image_dir):
        print(f"⚠️ Warning: Image directory not found: {image_dir}")
        return None
    
    # Check for direct mapping first (if provided)
    image_mapping = image_settings.get('image_mapping', {})
    print(f"📊 Available image mappings: {list(image_mapping.keys())}")
    print(f"🔍 Looking for image for: '{codec_text}'")
    
    # Try to find a match in the mapping table
    # First try exact match
    if codec_text in image_mapping:
        image_path = os.path.join(image_dir, image_mapping[codec_text])
        if os.path.exists(image_path):
            print(f"📝 Found exact mapping match for '{codec_text}': {image_mapping[codec_text]}")
            return image_path
    
    # Try to find partial matches in the mapping table
    # This helps match e.g., "DTS-HD MA 7.1" to a mapping for "DTS-HD MA"
    for map_key, map_file in image_mapping.items():
        if map_key in codec_text:
            image_path = os.path.join(image_dir, map_file)
            if os.path.exists(image_path):
                print(f"📝 Found partial mapping match for '{codec_text}' using '{map_key}': {map_file}")
                return image_path
    
    # If no mapping match found, try filename-based matching
    # Remove spaces, special characters, and normalize case for matching
    normalized_codec = codec_text.replace(" ", "-").replace(".", "").upper()
    
    # Try different case variations and formats
    possible_matches = [
        normalized_codec,
        normalized_codec.replace("-", ""),
        # Add more variations if needed
    ]
    
    # Check all files in the directory for a match
    for filename in os.listdir(image_dir):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        # Strip extension for comparison
        base_filename = os.path.splitext(filename)[0]
        
        # Check for exact matches
        if base_filename.upper() == normalized_codec:
            print(f"📝 Found exact filename match for '{codec_text}': {filename}")
            return os.path.join(image_dir, filename)
        
        # Check for matches including partial matches
        for match in possible_matches:
            if match == base_filename.upper():
                print(f"📝 Found filename variant match for '{codec_text}': {filename}")
                return os.path.join(image_dir, filename)
    
    # Advanced matching (extract codec name without channel info)
    # This helps match "DTS-HD MA 7.1" to "DTS-HD.png"
    codec_parts = codec_text.split()
    if len(codec_parts) > 0:
        base_codec = codec_parts[0].upper()
        for filename in os.listdir(image_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            if base_codec in filename.upper():
                print(f"📝 Found base codec match for '{codec_text}' using '{base_codec}': {filename}")
                return os.path.join(image_dir, filename)
    
    print(f"ℹ️ No matching codec image found for '{codec_text}'")
    return None

def load_codec_image(codec_text, settings):
    """
    Load the appropriate codec image based on the codec text.
    
    Args:
        codec_text (str): The codec text
        settings (dict): The badge settings
        
    Returns:
        PIL.Image or None: The loaded image, or None if no suitable image found
    """
    # Check if this is an awards badge (has color scheme)
    if 'Awards' in settings and 'color_scheme' in settings['Awards']:
        return load_awards_image(codec_text, settings)
    
    image_path = get_codec_image_path(codec_text, settings)
    if not image_path:
        return None
        
    try:
        # Load and convert to RGBA for transparency support
        image = Image.open(image_path).convert("RGBA")
        print(f"✅ Loaded codec image: {os.path.basename(image_path)}")
        return image
    except Exception as e:
        print(f"❌ Error loading codec image: {e}")
        return None

def load_awards_image(award_type, settings):
    """
    Load the appropriate awards image based on the award type and color scheme.
    
    Args:
        award_type (str): The award type (e.g., "oscars")
        settings (dict): The badge settings containing color scheme
        
    Returns:
        PIL.Image or None: The loaded image, or None if no suitable image found
    """
    try:
        # Get color scheme from settings
        color_scheme = settings.get('Awards', {}).get('color_scheme', 'black')
        
        # Get the base directory
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Build path to color-specific awards directory
        awards_dir = os.path.join(root_dir, 'images', 'awards', color_scheme)
        
        # Get image mapping
        image_mapping = settings.get('ImageBadges', {}).get('image_mapping', {})
        
        # Try to find the image file
        if award_type in image_mapping:
            image_filename = image_mapping[award_type]
            image_path = os.path.join(awards_dir, image_filename)
            
            if os.path.exists(image_path):
                print(f"✅ Found awards image: {color_scheme}/{image_filename} for {award_type}")
                image = Image.open(image_path).convert("RGBA")
                return image
            else:
                print(f"❌ Awards image file not found: {image_path}")
        else:
            print(f"❌ Award type '{award_type}' not found in image mapping")
            
        return None
        
    except Exception as e:
        print(f"❌ Error loading awards image for '{award_type}': {e}")
        return None
