#!/usr/bin/env python3
# aphrodite_helpers/badge_components/workflow.py

import os
from .badge_settings import load_badge_settings
from .badge_generator import create_badge
from .badge_applicator import apply_badge_to_poster

def download_and_badge_poster(
    jellyfin_url, 
    api_key, 
    item_id, 
    badge_text=None, 
    output_dir="posters/modified", 
    settings_file="badge_settings_audio.yml",
    use_image=True
):
    """Download a poster from Jellyfin, apply a badge with text, and save it."""
    # Import poster_fetcher here to avoid circular imports
    from aphrodite_helpers.poster_fetcher import download_poster
    
    # Load badge settings
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
    
    # Set up directories
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    badge = create_badge(settings, badge_text, use_image=use_image)
    
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

def process_all_posters(
    poster_dir="posters/original", 
    working_dir="posters/working", 
    output_dir="posters/modified", 
    settings_file="badge_settings_audio.yml",
    badge_text=None,
    use_image=True
):
    """Process all posters in the specified directory."""
    # Load badge settings
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
    
    # Create the badge once
    badge = create_badge(settings, badge_text, use_image=use_image)
    
    # Use badge_applicator to process all posters
    from .badge_applicator import process_posters
    return process_posters(
        badge=badge,
        settings=settings,
        poster_dir=poster_dir,
        working_dir=working_dir,
        output_dir=output_dir
    )

def save_test_badge(settings_file="badge_settings_audio.yml", text=None, use_image=True):
    """Save a test badge to verify settings and implementation."""
    settings = load_badge_settings(settings_file)
    if not settings:
        return False
        
    badge = create_badge(settings, text, use_image=use_image)
    
    # Save the badge
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_path = os.path.join(root_dir, "test_badge.png")
    
    # Convert to RGB if saving as JPG
    if test_path.lower().endswith('.jpg') or test_path.lower().endswith('.jpeg'):
        badge = badge.convert('RGB')
        
    badge.save(test_path)
    print(f"✅ Test badge saved to {test_path}")
    return True
