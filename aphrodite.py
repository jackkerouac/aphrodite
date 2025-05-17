#!/usr/bin/env python3
# aphrodite.py  •  stripped-down (no StateManager)

import sys
import os
import argparse
import time

from aphrodite_helpers.settings_validator import run_settings_check
from aphrodite_helpers.check_jellyfin_connection import (
    load_settings,
    get_jellyfin_libraries,
    get_library_item_count,
    get_library_items
)
from aphrodite_helpers.get_media_info import (
    get_media_stream_info,
    get_primary_audio_codec
)
from aphrodite_helpers.get_resolution_info import (
    get_media_resolution_info,
    get_resolution_badge_text
)
from aphrodite_helpers.apply_review_badges import process_item_reviews
from aphrodite_helpers.poster_fetcher import download_poster
from aphrodite_helpers.resize_posters import resize_image
from aphrodite_helpers.apply_badge import (
    load_badge_settings,
    create_badge,
    apply_badge_to_poster
)
from aphrodite_helpers.poster_uploader import PosterUploader


BANNER = r"""
              _                   _ _ _       
             | |                 | (_) |      
   __ _ _ __ | |__  _ __ ___   __| |_| |_ ___ 
  / _` | '_ \| '_ \| '__/ _ \ / _` | | __/ _ \
 | (_| | |_) | | | | | | (_) | (_| | | ||  __/
  \__,_| .__/|_| |_|_|  \___/ \__,_|_|\__\___|
       | |                                    
       |_|                                    

                    v0.2.1       
"""

def display_banner() -> None:
    print(BANNER)


def process_single_item(jellyfin_url: str, api_key: str, user_id: str, 
                        item_id: str, max_retries: int = 3,
                        add_audio: bool = True, add_resolution: bool = True,
                        add_reviews: bool = True, skip_upload: bool = False) -> bool:
    print(f"\n📋 Processing item {item_id}")

    if not add_audio and not add_resolution and not add_reviews:
        print("⚠️ No badge types selected. At least one badge type must be enabled.")
        return False

    # 1. Download poster (we'll need this for any badge type)
    poster_path = download_poster(jellyfin_url, api_key, item_id)
    if not poster_path:
        print("❌ Failed to download poster")
        return False

    # Get item name for display purposes
    item_info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
    if not item_info:
        item_name = "Unknown Item"
    else:
        item_name = item_info.get('name', 'Unknown Item')

    # 1.5. Resize the poster for consistent badge placement
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters", "working"), exist_ok=True)
    
    # Path for resized poster in working directory
    resized_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "posters", "working", 
        os.path.basename(poster_path)
    )
    
    # Resize the poster to ensure consistent badge placement
    resize_success = resize_image(poster_path, resized_path, target_width=1000)
    if not resize_success:
        print("⚠️ Failed to resize poster, continuing with original size")
        working_poster_path = poster_path
    else:
        print("✅ Resized poster to 1000px width")
        working_poster_path = resized_path
        
    # Ensure output directories exist
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters", "modified"), exist_ok=True)

    output_path = None

    # 2. Process Audio Badge if requested
    if add_audio:
        # Media info
        audio_info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
        if not audio_info:
            print("❌ Failed to retrieve audio information")
            return False

        codec = get_primary_audio_codec(audio_info)
        print(f"📢 Found audio codec: {codec} for {item_name}")
        
        # Skip adding audio badge if codec is UNKNOWN
        if codec.upper() == "UNKNOWN":
            print("⚠️ Skipping audio badge as codec is unknown")
        else:
            # Create audio badge
            audio_settings = load_badge_settings("badge_settings_audio.yml")
            audio_badge = create_badge(audio_settings, codec)
            
            # Apply audio badge to poster
            output_path = apply_badge_to_poster(working_poster_path, audio_badge, audio_settings)
            if not output_path:
                print("❌ Failed to apply audio badge to poster")
                return False
            
            # Update working_poster_path to point to the poster with audio badge
            working_poster_path = output_path

    # 3. Process Resolution Badge if requested
    if add_resolution:
        # Get resolution info
        resolution_info = get_media_resolution_info(jellyfin_url, api_key, user_id, item_id)
        if not resolution_info:
            print("❌ Failed to retrieve resolution information")
            return False

        resolution_text = get_resolution_badge_text(resolution_info)
        print(f"📏 Found resolution: {resolution_text} for {item_name}")

        # Skip adding resolution badge if it's UNKNOWN
        if resolution_text.upper() == "UNKNOWN":
            print("⚠️ Skipping resolution badge as resolution is unknown")
        else:
            # Create resolution badge
            resolution_settings = load_badge_settings("badge_settings_resolution.yml")
            resolution_badge = create_badge(resolution_settings, resolution_text)
            
            # Apply resolution badge to poster (which may already have an audio badge)
            output_path = apply_badge_to_poster(working_poster_path, resolution_badge, resolution_settings)
            if not output_path:
                print("❌ Failed to apply resolution badge to poster")
                return False
                
            # Update working_poster_path to point to the poster with resolution badge
            working_poster_path = output_path
    
    # 4. Process Review Badges if requested
    if add_reviews:
        print(f"📊 Adding review badges for {item_name}")
        # We want to add the review badges to the current version of the poster 
        # (which may already have audio and resolution badges)
        review_success = process_item_reviews(
            item_id, 
            jellyfin_url, 
            api_key, 
            user_id,
            "badge_settings_review.yml",
            "posters/modified",  # Save directly to modified directory
            working_poster_path  # Pass the current working poster path
        )
        
        if not review_success:
            print("⚠️ No reviews found or failed to create review badges")
        else:
            # Update output_path to point to the review badge output
            review_output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "posters", "modified", 
                os.path.basename(working_poster_path)
            )
            
            if os.path.exists(review_output_path):
                output_path = review_output_path
                working_poster_path = output_path  # Update working path too
                print(f"✅ Added review badges")
            else:
                print(f"⚠️ Review badges were processed but output not found at {review_output_path}")

    # 5. Upload the final modified poster (unless skipped)
    if not skip_upload:
        uploader = PosterUploader(jellyfin_url, api_key, user_id)
        if not uploader.upload_poster(item_id, output_path, max_retries):
            print("❌ Failed to upload modified poster")
            return False
        print(f"✅ Uploaded poster for: {item_name}")
    else:
        print(f"📤 Skipping upload, poster saved at: {output_path}")

    print(f"✅ Success: {item_name}")
    return True


def process_library_items(jellyfin_url: str, api_key: str, user_id: str,
                          library_id: str, limit: int | None,
                          max_retries: int, add_audio: bool = True, 
                          add_resolution: bool = True, add_reviews: bool = True,
                          skip_upload: bool = False) -> None:
    items = get_library_items(jellyfin_url, api_key, user_id, library_id)
    if not items:
        print("⚠️  No items found in library")
        return

    if limit:
        items = items[:limit]
    print(f"Found {len(items)} items in library")

    for i, item in enumerate(items, 1):
        name = item.get("Name", "Unknown")
        item_id = item["Id"]
        print(f"\n[{i}/{len(items)}] {name}")
        process_single_item(jellyfin_url, api_key, user_id,
                            item_id, max_retries, add_audio, add_resolution, 
                            add_reviews, skip_upload)
        time.sleep(1)


def main() -> int:
    display_banner()

    parser = argparse.ArgumentParser(
        description="Aphrodite – Jellyfin poster badge tool (stateless)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("check", help="Validate settings and Jellyfin connection")

    item_p = sub.add_parser("item", help="Process a single item")
    item_p.add_argument("item_id")
    item_p.add_argument("--retries", type=int, default=3)
    item_p.add_argument("--no-audio", action="store_true", help="Don't add audio codec badge")
    item_p.add_argument("--no-resolution", action="store_true", help="Don't add resolution badge")
    item_p.add_argument("--no-reviews", action="store_true", help="Don't add review badges")
    item_p.add_argument("--no-upload", action="store_true", help="Don't upload posters to Jellyfin, only save locally")

    lib_p = sub.add_parser("library", help="Process every item in a library")
    lib_p.add_argument("library_id")
    lib_p.add_argument("--limit", type=int)
    lib_p.add_argument("--retries", type=int, default=3)
    lib_p.add_argument("--no-audio", action="store_true", help="Don't add audio codec badge")
    lib_p.add_argument("--no-resolution", action="store_true", help="Don't add resolution badge")
    lib_p.add_argument("--no-reviews", action="store_true", help="Don't add review badges")
    lib_p.add_argument("--no-upload", action="store_true", help="Don't upload posters to Jellyfin, only save locally")

    args = parser.parse_args()
    run_settings_check()

    settings = load_settings()
    if not settings:
        print("❌ Failed to load settings")
        return 1
    jf = settings["api_keys"]["Jellyfin"][0]
    url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]

    if args.cmd == "check":
        print(f"📡 Connecting to Jellyfin at {url}")
        libs = get_jellyfin_libraries(url, api_key, user_id)
        for lib in libs:
            print(f"  - {lib['Name']} ({lib['Id']}): "
                  f"{get_library_item_count(url, api_key, user_id, lib['Id'])} items")
        return 0

    if args.cmd == "item":
        # By default, all badge types are ON
        add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
        add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
        add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
        skip_upload = hasattr(args, 'no_upload') and args.no_upload
        
        ok = process_single_item(
            url, api_key, user_id, args.item_id, args.retries,
            add_audio=add_audio, add_resolution=add_resolution,
            add_reviews=add_reviews, skip_upload=skip_upload
        )
        return 0 if ok else 1

    if args.cmd == "library":
        # By default, all badge types are ON
        add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
        add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
        add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
        skip_upload = hasattr(args, 'no_upload') and args.no_upload
        
        process_library_items(
            url, api_key, user_id, args.library_id, args.limit, args.retries,
            add_audio=add_audio, add_resolution=add_resolution,
            add_reviews=add_reviews, skip_upload=skip_upload
        )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
