#!/usr/bin/env python3
# aphrodite.py  •  stripped-down (no StateManager)

import sys
import os
import argparse
import time

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    import codecs
    import io
    # Set UTF-8 encoding for stdout and stderr
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')
    # Set environment variable for subprocess communication
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from aphrodite_helpers.cleanup.poster_cleanup import clean_poster_directories

from aphrodite_helpers.settings_validator import run_settings_check
from aphrodite_helpers.config_auto_repair import validate_and_repair_settings
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
from aphrodite_helpers.tv_series_aggregator import get_series_dominant_badge_info
from aphrodite_helpers.metadata_tagger import add_aphrodite_tag, MetadataTagger, get_tagging_settings


BANNER = r"""
              _                   _ _ _       
             | |                 | (_) |      
   __ _ _ __ | |__  _ __ ___   __| |_| |_ ___ 
  / _` | '_ \| '_ \| '__/ _ \ / _` | | __/ _ \
 | (_| | |_) | | | | | | (_) | (_| | | ||  __/
  \__,_| .__/|_| |_|_|  \___/ \__,_|_|\__\___|
       | |                                    
       |_|                                    

                    v2.x.x    
"""

def display_banner() -> None:
    print(BANNER)


def process_single_item(jellyfin_url: str, api_key: str, user_id: str, 
                        item_id: str, max_retries: int = 3,
                        add_audio: bool = True, add_resolution: bool = True,
                        add_reviews: bool = True, add_awards: bool = True,
                        skip_upload: bool = False, add_metadata_tag: bool = True) -> bool:
    print(f"\n📋 Processing item {item_id}")

    if not add_audio and not add_resolution and not add_reviews and not add_awards:
        print("⚠️ No badge types selected. At least one badge type must be enabled.")
        return False

    # Check if this is a TV series and get dominant badge info if applicable
    print(f"🔍 Checking if item {item_id} is a TV series...")
    
    # Add more detailed debugging
    from aphrodite_helpers.tv_series_aggregator import get_jellyfin_item_details, is_tv_series, should_use_dominant_badges
    
    print(f"🔧 Debug: Checking TV series settings...")
    tv_enabled = should_use_dominant_badges()
    print(f"🔧 Debug: TV series dominant badges enabled: {tv_enabled}")
    
    if tv_enabled:
        print(f"🔧 Debug: Getting item details for {item_id}...")
        item_details = get_jellyfin_item_details(jellyfin_url, api_key, user_id, item_id)
        if item_details:
            item_type = item_details.get('Type', 'Unknown')
            print(f"🔧 Debug: Item type: {item_type}")
            is_series = is_tv_series(item_details)
            print(f"🔧 Debug: Is TV series: {is_series}")
        else:
            print(f"🔧 Debug: Failed to get item details")
    
    series_badge_info = get_series_dominant_badge_info(jellyfin_url, api_key, user_id, item_id)
    
    if series_badge_info:
        print(f"✅ TV series detected: {series_badge_info['name']}")
        print(f"📊 Dominant audio codec: {series_badge_info['audio_codec']}")
        print(f"📊 Dominant resolution: {series_badge_info['resolution']}")
    else:
        print(f"ℹ️ Not a TV series or TV series analysis disabled")
    
    # 1. Download poster (we'll need this for any badge type)
    poster_path = download_poster(jellyfin_url, api_key, item_id)
    if not poster_path:
        print("❌ Failed to download poster")
        return False

    # Get item name for display purposes
    if series_badge_info:
        item_name = series_badge_info['name']
        print(f"📺 Processing TV series: {item_name}")
    else:
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
        # Use series dominant codec if available, otherwise get individual item codec
        if series_badge_info:
            codec = series_badge_info['audio_codec']
            print(f"📢 Using dominant audio codec: {codec} for TV series {item_name}")
        else:
            # Media info for non-series items
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
        # Use series dominant resolution if available, otherwise get individual item resolution
        if series_badge_info:
            resolution_text = series_badge_info['resolution']
            print(f"📏 Using dominant resolution: {resolution_text} for TV series {item_name}")
        else:
            # Get resolution info for non-series items
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
    
    # 3.5. Process Awards Badge if requested
    if add_awards:
        print(f"🏆 Checking for awards badges for {item_name}")
        from aphrodite_helpers.get_awards_info import AwardsFetcher
        
        try:
            # Load settings and check for awards
            settings = load_settings()
            awards_fetcher = AwardsFetcher(settings)
            awards_info = awards_fetcher.get_media_awards_info(jellyfin_url, api_key, user_id, item_id)
            
            if awards_info:
                award_type = awards_info['award_type']
                print(f"🏆 Found award: {award_type} for {item_name}")
                
                # Create awards badge
                awards_settings = load_badge_settings("badge_settings_awards.yml")
                awards_badge = create_badge(awards_settings, award_type)
                
                # Apply awards badge to poster
                output_path = apply_badge_to_poster(working_poster_path, awards_badge, awards_settings)
                if not output_path:
                    print("❌ Failed to apply awards badge to poster")
                    # Don't return False here - awards are optional
                else:
                    # Update working_poster_path to point to the poster with awards badge
                    working_poster_path = output_path
                    print(f"✅ Added {award_type} award badge")
            else:
                print(f"ℹ️ No awards found for {item_name}")
                
        except Exception as e:
            print(f"⚠️ Error processing awards badge: {e}")
            # Don't fail the entire processing for awards errors
    
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
        # Check if we have a valid output path before attempting to upload
        if not output_path:
            print("⚠️ No modified poster was created, skipping upload")
            return False
            
        uploader = PosterUploader(jellyfin_url, api_key, user_id)
        if not uploader.upload_poster(item_id, output_path, max_retries):
            print("❌ Failed to upload modified poster")
            return False
        print(f"✅ Uploaded poster for: {item_name}")
    else:
        if output_path:
            print(f"📤 Skipping upload, poster saved at: {output_path}")
        else:
            print("⚠️ No modified poster was created, nothing to upload")

    # 6. Add metadata tag to mark this item as processed by Aphrodite
    if output_path and add_metadata_tag:  # Only tag if we actually processed something and tagging is enabled
        print(f"🏷️ Adding Aphrodite metadata tag...")
        tag_success = add_aphrodite_tag(jellyfin_url, api_key, user_id, item_id)  # Uses settings for tag name
        if tag_success:
            print(f"✅ Added metadata tag to track processing")
        else:
            print(f"⚠️ Failed to add metadata tag (processing was still successful)")
    elif output_path and not add_metadata_tag:
        print(f"🏷️ Skipping metadata tag (disabled via command line)")
    elif not output_path:
        print(f"🏷️ Skipping metadata tag (no processing occurred)")
    
    print(f"✅ Success: {item_name}")
    return True


def process_library_items(jellyfin_url: str, api_key: str, user_id: str,
                          library_id: str, limit: int | None,
                          max_retries: int, add_audio: bool = True, 
                          add_resolution: bool = True, add_reviews: bool = True,
                          add_awards: bool = True, skip_upload: bool = False,
                          add_metadata_tag: bool = True, skip_processed: bool = False) -> None:
    items = get_library_items(jellyfin_url, api_key, user_id, library_id)
    if not items:
        print("⚠️  No items found in library")
        return

    # Filter out already processed items if skip_processed is enabled
    if skip_processed:
        print(f"🔍 Checking for already processed items...")
        tagging_settings = get_tagging_settings()
        tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
        tagger = MetadataTagger(jellyfin_url, api_key, user_id)
        
        original_count = len(items)
        unprocessed_items = []
        
        for item in items:
            item_id = item.get('Id')
            if not item_id:
                unprocessed_items.append(item)
                continue
                
            has_tag = tagger.check_aphrodite_tag(item_id, tag_name)
            if not has_tag:
                unprocessed_items.append(item)
        
        skipped_count = original_count - len(unprocessed_items)
        print(f"📊 Skipped {skipped_count} already processed items, {len(unprocessed_items)} remaining")
        items = unprocessed_items

    if limit:
        items = items[:limit]
    print(f"Found {len(items)} items to process in library")

    successful_items = 0
    failed_items = 0

    for i, item in enumerate(items, 1):
        try:
            name = item.get("Name", "Unknown")
            item_id = item["Id"]
            print(f"\n[{i}/{len(items)}] {name}")
            
            success = process_single_item(jellyfin_url, api_key, user_id,
                                item_id, max_retries, add_audio, add_resolution, 
                                add_reviews, add_awards, skip_upload, add_metadata_tag)
            
            if success:
                successful_items += 1
            else:
                failed_items += 1
                print("⚠️ Failed to process item, continuing with next item")
                
            # Small delay between items
            time.sleep(1)
            
        except Exception as e:
            failed_items += 1
            print(f"❌ Error processing item: {str(e)}")
            print("⚠️ Continuing with next item")
            import traceback
            print(traceback.format_exc())
            time.sleep(1)
    
    # Summary at the end
    print(f"\n✨ Library processing complete: {successful_items} successful, {failed_items} failed out of {len(items)} total items")



def main() -> int:
    display_banner()

    parser = argparse.ArgumentParser(
        description="Aphrodite – Jellyfin poster badge tool (stateless)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("check", help="Validate settings and Jellyfin connection")
    
    status_p = sub.add_parser("status", help="Check processing status of items in a library")
    status_p.add_argument("library_id", help="Library ID to check")
    status_p.add_argument("--tag", help="Metadata tag to check for (default: from settings)")
    status_p.add_argument("--unprocessed-only", action="store_true", help="Only show items that haven't been processed")

    cleanup_p = sub.add_parser("cleanup", help="Clean up poster directories")
    cleanup_p.add_argument("--no-modified", action="store_true", help="Don't clean the modified posters directory")
    cleanup_p.add_argument("--no-working", action="store_true", help="Don't clean the working posters directory")
    cleanup_p.add_argument("--no-original", action="store_true", help="Don't clean the original posters directory")
    cleanup_p.add_argument("--quiet", action="store_true", help="Don't print status messages")

    item_p = sub.add_parser("item", help="Process a single item")
    item_p.add_argument("item_id")
    item_p.add_argument("--retries", type=int, default=3)
    item_p.add_argument("--no-audio", action="store_true", help="Don't add audio codec badge")
    item_p.add_argument("--no-resolution", action="store_true", help="Don't add resolution badge")
    item_p.add_argument("--no-reviews", action="store_true", help="Don't add review badges")
    item_p.add_argument("--no-awards", action="store_true", help="Don't add awards badges")
    item_p.add_argument("--no-upload", action="store_true", help="Don't upload posters to Jellyfin, only save locally")
    item_p.add_argument("--no-metadata-tag", action="store_true", help="Don't add metadata tag to track processing")
    item_p.add_argument("--cleanup", action="store_true", help="Clean up poster directories after processing")

    lib_p = sub.add_parser("library", help="Process every item in a library")
    lib_p.add_argument("library_id")
    lib_p.add_argument("--limit", type=int)
    lib_p.add_argument("--retries", type=int, default=3)
    lib_p.add_argument("--no-audio", action="store_true", help="Don't add audio codec badge")
    lib_p.add_argument("--no-resolution", action="store_true", help="Don't add resolution badge")
    lib_p.add_argument("--no-reviews", action="store_true", help="Don't add review badges")
    lib_p.add_argument("--no-awards", action="store_true", help="Don't add awards badges")
    lib_p.add_argument("--no-upload", action="store_true", help="Don't upload posters to Jellyfin, only save locally")
    lib_p.add_argument("--no-metadata-tag", action="store_true", help="Don't add metadata tag to track processing")
    lib_p.add_argument("--skip-processed", action="store_true", help="Skip items that already have the aphrodite-overlay tag")
    lib_p.add_argument("--cleanup", action="store_true", help="Clean up poster directories after processing")

    args = parser.parse_args()
    
    # Auto-repair settings before validation
    print("🔧 Auto-repairing settings file...")
    validate_and_repair_settings()
    
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
        # Clean up posters if requested
        if hasattr(args, 'cleanup') and args.cleanup:
            print("\n🧹 Cleaning up poster directories...")
            clean_poster_directories(
                clean_modified=True,
                clean_working=True,
                clean_original=True,
                verbose=True
            )
            
        return 0
    
    if args.cmd == "status":
        from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
        
        print(f"📊 Checking processing status for library {args.library_id}")
        
        # Get tag from settings if not specified
        tag_to_check = args.tag
        if tag_to_check is None:
            tagging_settings = get_tagging_settings()
            tag_to_check = tagging_settings.get('tag_name', 'aphrodite-overlay')
        
        # Get all items in the library
        items = get_library_items(url, api_key, user_id, args.library_id)
        if not items:
            print("⚠️  No items found in library")
            return 1
        
        tagger = MetadataTagger(url, api_key, user_id)
        processed_count = 0
        unprocessed_count = 0
        
        print(f"\nProcessing status for {len(items)} items:")
        print(f"Tag: '{tag_to_check}'\n")
        
        for item in items:
            item_id = item.get('Id')
            item_name = item.get('Name', 'Unknown')
            
            if not item_id:
                continue
                
            has_tag = tagger.check_aphrodite_tag(item_id, tag_to_check)
            
            if has_tag:
                processed_count += 1
                if not args.unprocessed_only:
                    print(f"✅ {item_name} (Processed)")
            else:
                unprocessed_count += 1
                print(f"⚪ {item_name} (Not processed)")
        
        print(f"\n📈 Summary:")
        print(f"  Processed: {processed_count}/{len(items)} ({processed_count/len(items)*100:.1f}%)")
        print(f"  Unprocessed: {unprocessed_count}/{len(items)} ({unprocessed_count/len(items)*100:.1f}%)")
        
        return 0
        
    if args.cmd == "cleanup":
        # Invert the no-* arguments for the clean_* parameters
        clean_modified = not (hasattr(args, 'no_modified') and args.no_modified)
        clean_working = not (hasattr(args, 'no_working') and args.no_working)
        clean_original = not (hasattr(args, 'no_original') and args.no_original)
        verbose = not (hasattr(args, 'quiet') and args.quiet)
        
        success, message = clean_poster_directories(
            clean_modified=clean_modified,
            clean_working=clean_working,
            clean_original=clean_original,
            verbose=verbose
        )
        return 0 if success else 1

    if args.cmd == "item":
        # By default, all badge types are ON
        add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
        add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
        add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
        add_awards = not (hasattr(args, 'no_awards') and args.no_awards)
        skip_upload = hasattr(args, 'no_upload') and args.no_upload
        add_metadata_tag = not (hasattr(args, 'no_metadata_tag') and args.no_metadata_tag)
        
        ok = process_single_item(
            url, api_key, user_id, args.item_id, args.retries,
            add_audio=add_audio, add_resolution=add_resolution,
            add_reviews=add_reviews, add_awards=add_awards,
            skip_upload=skip_upload, add_metadata_tag=add_metadata_tag
        )
        # Clean up posters if requested
        if hasattr(args, 'cleanup') and args.cleanup:
            print("\n🧹 Cleaning up poster directories...")
            clean_poster_directories(
                clean_modified=True,
                clean_working=True,
                clean_original=True,
                verbose=True
            )
            
        return 0 if ok else 1

    if args.cmd == "library":
        # By default, all badge types are ON
        add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
        add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
        add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
        add_awards = not (hasattr(args, 'no_awards') and args.no_awards)
        skip_upload = hasattr(args, 'no_upload') and args.no_upload
        add_metadata_tag = not (hasattr(args, 'no_metadata_tag') and args.no_metadata_tag)
        skip_processed = hasattr(args, 'skip_processed') and args.skip_processed
        
        process_library_items(
            url, api_key, user_id, args.library_id, args.limit, args.retries,
            add_audio=add_audio, add_resolution=add_resolution,
            add_reviews=add_reviews, add_awards=add_awards,
            skip_upload=skip_upload, add_metadata_tag=add_metadata_tag,
            skip_processed=skip_processed
        )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
