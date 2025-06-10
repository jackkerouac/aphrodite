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

# Apply enhanced anime mapping to production
try:
    from integrate_enhanced_anime_mapping import apply_production_enhancements
    apply_production_enhancements()
except Exception as e:
    print(f"⚠️ Note: Enhanced anime mapping not available: {e}")

from aphrodite_helpers.cleanup.poster_cleanup import clean_poster_directories

# Import minimal logging
from aphrodite_helpers.minimal_logger import log_error, log_warning, log_critical, log_milestone, LoggedOperation

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

# 🗄️ PHASE 2: Database Integration imports
try:
    from aphrodite_helpers.database_integration import process_item_with_database_tracking
    DATABASE_TRACKING_AVAILABLE = True
except ImportError:
    DATABASE_TRACKING_AVAILABLE = False
    print("⚠️ Database tracking not available, running in legacy mode")

# 🗄️ PHASE 3: Database Commands imports
try:
    from aphrodite_helpers.database_reporter import DatabaseReporter
    from aphrodite_helpers.review_updater import ReviewUpdater
    DATABASE_COMMANDS_AVAILABLE = True
except ImportError:
    DATABASE_COMMANDS_AVAILABLE = False
    print("⚠️ Database commands not available")


BANNER = r"""
              _                   _ _ _       
             | |                 | (_) |      
   __ _ _ __ | |__  _ __ ___   __| |_| |_ ___ 
  / _` | '_ \| '_ \| '__/ _ \ / _` | | __/ _ \
 | (_| | |_) | | | | | | (_) | (_| | | ||  __/
  \__,_| .__/|_| |_|_|  \___/ \__,_|_|\__\___|
       | |                                    
       |_|                                    

                    v3.x.x    
"""

def display_banner() -> None:
    print(BANNER)


def _process_single_item_core(jellyfin_url: str, api_key: str, user_id: str, 
                        item_id: str, max_retries: int = 3,
                        add_audio: bool = True, add_resolution: bool = True,
                        add_reviews: bool = True, add_awards: bool = True,
                        skip_upload: bool = False, add_metadata_tag: bool = True) -> bool:

    if not add_audio and not add_resolution and not add_reviews and not add_awards:
        log_warning("No badge types selected. At least one badge type must be enabled.", "process")
        return False

    # Check if this is a TV series and get dominant badge info if applicable
    from aphrodite_helpers.tv_series_aggregator import get_jellyfin_item_details, is_tv_series, should_use_dominant_badges
    
    tv_enabled = should_use_dominant_badges()
    
    if tv_enabled:
        item_details = get_jellyfin_item_details(jellyfin_url, api_key, user_id, item_id)
        if not item_details:
            log_warning(f"Failed to get item details for {item_id}", "tv_series")
    
    series_badge_info = get_series_dominant_badge_info(jellyfin_url, api_key, user_id, item_id)
    
    # 1. Download poster (we'll need this for any badge type)
    poster_path = download_poster(jellyfin_url, api_key, item_id)
    if not poster_path:
        log_error(f"Failed to download poster for item {item_id}", "poster")
        return False

    # Get item name for display purposes
    if series_badge_info:
        item_name = series_badge_info['name']
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
        log_warning(f"Failed to resize poster for {item_name}, continuing with original size", "poster")
        working_poster_path = poster_path
    else:
        working_poster_path = resized_path
        
    # Ensure output directories exist
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters", "modified"), exist_ok=True)

    output_path = None

    # 2. Process Audio Badge if requested
    if add_audio:
        # Use series dominant codec if available, otherwise get individual item codec
        if series_badge_info:
            codec = series_badge_info['audio_codec']
        else:
            # Media info for non-series items
            audio_info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
            if not audio_info:
                log_error(f"Failed to retrieve audio information for {item_name}", "audio")
                return False

            codec = get_primary_audio_codec(audio_info)
        
        # Skip adding audio badge if codec is UNKNOWN
        if codec.upper() == "UNKNOWN":
            log_warning(f"Skipping audio badge for {item_name} - codec unknown", "audio")
        else:
            # Create audio badge - YAML DEPENDENCY: badge_settings_audio.yml
            audio_settings = load_badge_settings("badge_settings_audio.yml")
            audio_badge = create_badge(audio_settings, codec)
            
            # Apply audio badge to poster
            output_path = apply_badge_to_poster(working_poster_path, audio_badge, audio_settings)
            if not output_path:
                log_error(f"Failed to apply audio badge to poster for {item_name}", "badge")
                return False
            
            # Update working_poster_path to point to the poster with audio badge
            working_poster_path = output_path

    # 3. Process Resolution Badge if requested
    if add_resolution:
        # Use series dominant resolution if available, otherwise get individual item resolution
        if series_badge_info:
            resolution_text = series_badge_info['resolution']
        else:
            # Get resolution info for non-series items
            resolution_info = get_media_resolution_info(jellyfin_url, api_key, user_id, item_id)
            if not resolution_info:
                log_error(f"Failed to retrieve resolution information for {item_name}", "resolution")
                return False

            resolution_text = get_resolution_badge_text(resolution_info)

        # Skip adding resolution badge if it's UNKNOWN
        if resolution_text.upper() == "UNKNOWN":
            log_warning(f"Skipping resolution badge for {item_name} - resolution unknown", "resolution")
        else:
            # Create resolution badge - YAML DEPENDENCY: badge_settings_resolution.yml
            resolution_settings = load_badge_settings("badge_settings_resolution.yml")
            resolution_badge = create_badge(resolution_settings, resolution_text)
            
            # Apply resolution badge to poster (which may already have an audio badge)
            output_path = apply_badge_to_poster(working_poster_path, resolution_badge, resolution_settings)
            if not output_path:
                log_error(f"Failed to apply resolution badge to poster for {item_name}", "badge")
                return False
                
            # Update working_poster_path to point to the poster with resolution badge
            working_poster_path = output_path
    
    # 3.5. Process Awards Badge if requested
    if add_awards:
        from aphrodite_helpers.get_awards_info import AwardsFetcher
        
        try:
            # Load settings and check for awards - YAML DEPENDENCY: settings.yaml
            settings = load_settings()
            awards_fetcher = AwardsFetcher(settings)
            awards_info = awards_fetcher.get_media_awards_info(jellyfin_url, api_key, user_id, item_id)
            
            if awards_info:
                award_type = awards_info['award_type']
                
                # Create awards badge - YAML DEPENDENCY: badge_settings_awards.yml
                awards_settings = load_badge_settings("badge_settings_awards.yml")
                awards_badge = create_badge(awards_settings, award_type)
                
                # Apply awards badge to poster
                output_path = apply_badge_to_poster(working_poster_path, awards_badge, awards_settings)
                if not output_path:
                    log_error(f"Failed to apply awards badge to poster for {item_name}", "badge")
                    # Don't return False here - awards are optional
                else:
                    # Update working_poster_path to point to the poster with awards badge
                    working_poster_path = output_path
                
        except Exception as e:
            log_warning(f"Error processing awards badge for {item_name}: {e}", "awards")
            # Don't fail the entire processing for awards errors
    
    # 4. Process Review Badges if requested
    if add_reviews:
        # We want to add the review badges to the current version of the poster 
        # (which may already have audio and resolution badges)
        review_success = process_item_reviews(
            item_id, 
            jellyfin_url, 
            api_key, 
            user_id,
            "badge_settings_review.yml",  # YAML DEPENDENCY: badge_settings_review.yml
            "posters/modified",  # Save directly to modified directory
            working_poster_path  # Pass the current working poster path
        )
        
        if not review_success:
            log_warning(f"No reviews found or failed to create review badges for {item_name}", "reviews")
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
            else:
                log_warning(f"Review badges were processed but output not found for {item_name}", "reviews")

    # 5. Upload the final modified poster (unless skipped)
    if not skip_upload:
        # Check if we have a valid output path before attempting to upload
        if not output_path:
            log_warning(f"No modified poster was created for {item_name}, skipping upload", "upload")
            return False
            
        uploader = PosterUploader(jellyfin_url, api_key, user_id)
        if not uploader.upload_poster(item_id, output_path, max_retries):
            log_error(f"Failed to upload modified poster for {item_name}", "upload")
            return False

    # 6. Add metadata tag to mark this item as processed by Aphrodite
    if output_path and add_metadata_tag:  # Only tag if we actually processed something and tagging is enabled
        tag_success = add_aphrodite_tag(jellyfin_url, api_key, user_id, item_id)  # Uses settings for tag name
        if not tag_success:
            log_warning(f"Failed to add metadata tag for {item_name} (processing was still successful)", "metadata")
    
    return True


# 🗄️ PHASE 2: Database Integration Wrapper
def process_single_item(jellyfin_url: str, api_key: str, user_id: str, 
                        item_id: str, max_retries: int = 3,
                        add_audio: bool = True, add_resolution: bool = True,
                        add_reviews: bool = True, add_awards: bool = True,
                        skip_upload: bool = False, add_metadata_tag: bool = True) -> bool:
    """
    Database-integrated wrapper for process_single_item.
    
    This function adds database tracking to the core processing function
    while maintaining full backward compatibility.
    """
    
    # Processing options for database tracking
    processing_options = {
        'audio': add_audio,
        'resolution': add_resolution,
        'reviews': add_reviews,
        'awards': add_awards
    }
    
    # Use database integration if available, otherwise fall back to core function
    if DATABASE_TRACKING_AVAILABLE:
        return process_item_with_database_tracking(
            jellyfin_url, api_key, user_id, item_id,
            processing_options,
            _process_single_item_core,
            jellyfin_url, api_key, user_id, item_id, max_retries,
            add_audio, add_resolution, add_reviews, add_awards,
            skip_upload, add_metadata_tag
        )
    else:
        # Fall back to original function without database tracking
        return _process_single_item_core(
            jellyfin_url, api_key, user_id, item_id, max_retries,
            add_audio, add_resolution, add_reviews, add_awards,
            skip_upload, add_metadata_tag
        )


def _skip_processed_legacy(items, jellyfin_url: str, api_key: str, user_id: str):
    """
    Legacy method for skipping processed items using metadata tags.
    Used as fallback when database commands are not available.
    """
    # YAML DEPENDENCY: settings.yaml for tag configuration
    tagging_settings = get_tagging_settings()
    tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
    tagger = MetadataTagger(jellyfin_url, api_key, user_id)
    
    original_count = len(items)
    unprocessed_items = []
    
    with LoggedOperation(f"Legacy skip check for {original_count} items", "skip_legacy"):
        for item in items:
            item_id = item.get('Id')
            if not item_id:
                unprocessed_items.append(item)
                continue
                
            has_tag = tagger.check_aphrodite_tag(item_id, tag_name)
            if not has_tag:
                unprocessed_items.append(item)
        
        skipped_count = original_count - len(unprocessed_items)
        log_milestone(f"Metadata tag skip: {skipped_count} already processed, {len(unprocessed_items)} remaining", "skip_legacy")
    
    return unprocessed_items


def process_library_items(jellyfin_url: str, api_key: str, user_id: str,
                          library_id: str, limit: int | None,
                          max_retries: int, add_audio: bool = True, 
                          add_resolution: bool = True, add_reviews: bool = True,
                          add_awards: bool = True, skip_upload: bool = False,
                          add_metadata_tag: bool = True, skip_processed: bool = False) -> None:
    
    with LoggedOperation(f"Library processing for library {library_id}", "library"):
        items = get_library_items(jellyfin_url, api_key, user_id, library_id)
        if not items:
            log_warning(f"No items found in library {library_id}", "library")
            return

        # Filter out already processed items if skip_processed is enabled
        if skip_processed:
            log_milestone("Checking for already processed items", "library")
        
            # 🗄️ PHASE 3: Use hybrid database+metadata approach for skip-processed
            if DATABASE_COMMANDS_AVAILABLE:
                try:
                    reporter = DatabaseReporter()
                    
                    # Use hybrid method that checks BOTH database AND metadata tags
                    # This ensures we catch all processed items regardless of when they were processed
                    processed_item_ids = reporter.get_processed_items_hybrid(
                        library_id, jellyfin_url, api_key, user_id
                    )
                    reporter.close()
                    
                    original_count = len(items)
                    unprocessed_items = []
                    
                    for item in items:
                        item_id = item.get('Id')
                        if item_id and item_id not in processed_item_ids:
                            unprocessed_items.append(item)
                        elif not item_id:
                            unprocessed_items.append(item)  # Include items without ID
                    
                    skipped_count = original_count - len(unprocessed_items)
                    log_milestone(f"Hybrid skip (DB + metadata tags): {skipped_count} already processed, {len(unprocessed_items)} remaining", "library")
                    items = unprocessed_items
                    
                except Exception as e:
                    log_warning(f"Database skip failed, falling back to metadata tags: {e}", "library")
                    # Fall back to original metadata tag method
                    items = _skip_processed_legacy(items, jellyfin_url, api_key, user_id)
            else:
                # Fall back to original metadata tag method
                items = _skip_processed_legacy(items, jellyfin_url, api_key, user_id)

        if limit:
            items = items[:limit]
        
        log_milestone(f"Found {len(items)} items to process in library {library_id}", "library")

        successful_items = 0
        failed_items = 0

        for i, item in enumerate(items, 1):
            try:
                name = item.get("Name", "Unknown")
                item_id = item["Id"]
                # Silent processing - no per-item status messages
                
                success = process_single_item(jellyfin_url, api_key, user_id,
                                    item_id, max_retries, add_audio, add_resolution, 
                                    add_reviews, add_awards, skip_upload, add_metadata_tag)
                
                if success:
                    successful_items += 1
                else:
                    failed_items += 1
                    log_warning(f"Failed to process item {name} ({item_id})", "library")
                    
                # Small delay between items
                time.sleep(1)
                
            except Exception as e:
                failed_items += 1
                log_error(f"Error processing item {item.get('Name', 'Unknown')}: {str(e)}", "library")
                time.sleep(1)
        
        # Summary at the end
        log_milestone(f"Library processing complete: {successful_items} successful, {failed_items} failed out of {len(items)} total items", "library")



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

    # 🗄️ PHASE 3: Database Commands
    db_status_p = sub.add_parser("db-status", help="Show database processing statistics")
    db_status_p.add_argument("--library", help="Filter by library ID")
    db_status_p.add_argument("--detailed", action="store_true", help="Show detailed item list")

    check_reviews_p = sub.add_parser("check-reviews", help="Check which items need review updates")
    check_reviews_p.add_argument("library_id", help="Library ID to check")
    check_reviews_p.add_argument("--hours", type=int, default=24, help="Hours since last review check (default: 24)")
    check_reviews_p.add_argument("--update", action="store_true", help="Actually update reviews for items that need it")
    check_reviews_p.add_argument("--limit", type=int, help="Maximum number of items to update")

    reprocess_p = sub.add_parser("reprocess", help="Reprocess items based on criteria")
    reprocess_p.add_argument("--failed-only", action="store_true", help="Only reprocess failed items")
    reprocess_p.add_argument("--older-than", type=int, help="Reprocess items older than X days")
    reprocess_p.add_argument("--library", help="Library ID to process")
    reprocess_p.add_argument("--limit", type=int, help="Maximum number of items to reprocess")
    reprocess_p.add_argument("--dry-run", action="store_true", help="Show what would be reprocessed without actually doing it")

    # 🗄️ PHASE 4: Enhanced Features
    report_p = sub.add_parser("report", help="Generate comprehensive processing reports")
    report_p.add_argument("--library", help="Filter by library ID")
    report_p.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    report_p.add_argument("--export", choices=["csv", "json"], help="Export data to file")
    report_p.add_argument("--output", help="Custom output path for export")

    settings_check_p = sub.add_parser("settings-check", help="Check for badge settings changes")
    settings_check_p.add_argument("--library", help="Filter by library ID")
    settings_check_p.add_argument("--mark-for-reprocess", action="store_true", help="Mark affected items for reprocessing")
    settings_check_p.add_argument("--dry-run", action="store_true", help="Show what would be marked without actually marking")

    backup_p = sub.add_parser("backup", help="Database backup and restore operations")
    backup_subparsers = backup_p.add_subparsers(dest="backup_cmd", help="Backup operations")
    
    # Backup subcommands
    create_backup_p = backup_subparsers.add_parser("create", help="Create database backup")
    create_backup_p.add_argument("--no-compress", action="store_true", help="Don't compress the backup")
    create_backup_p.add_argument("--no-timestamp", action="store_true", help="Don't include timestamp in filename")
    
    restore_backup_p = backup_subparsers.add_parser("restore", help="Restore from backup")
    restore_backup_p.add_argument("backup_path", help="Path to backup file")
    restore_backup_p.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    
    list_backups_p = backup_subparsers.add_parser("list", help="List available backups")
    
    export_json_p = backup_subparsers.add_parser("export", help="Export database to JSON")
    export_json_p.add_argument("--output", help="Output path for JSON file")
    export_json_p.add_argument("--include-sensitive", action="store_true", help="Include sensitive data like API keys")
    
    import_json_p = backup_subparsers.add_parser("import", help="Import database from JSON")
    import_json_p.add_argument("json_path", help="Path to JSON file")
    import_json_p.add_argument("--tables", nargs="+", help="Specific tables to import")
    import_json_p.add_argument("--merge", action="store_true", help="Merge with existing data instead of replacing")
    
    cleanup_backups_p = backup_subparsers.add_parser("cleanup", help="Remove old backup files")
    cleanup_backups_p.add_argument("--keep", type=int, default=10, help="Number of backups to keep (default: 10)")
    
    verify_backup_p = backup_subparsers.add_parser("verify", help="Verify backup integrity")
    verify_backup_p.add_argument("backup_path", help="Path to backup file to verify")

    args = parser.parse_args()
    
    # Auto-repair settings before validation - keep user feedback
    print("🔧 Auto-repairing settings file...")
    with LoggedOperation("Settings auto-repair", "setup"):
        try:
            validate_and_repair_settings()
            log_milestone("Settings auto-repair completed", "setup")
        except Exception as e:
            log_error(f"Settings auto-repair failed: {e}", "setup")
    
    with LoggedOperation("Settings validation", "setup"):
        try:
            run_settings_check()
            log_milestone("Settings validation completed", "setup")
        except Exception as e:
            log_error(f"Settings validation failed: {e}", "setup")

    settings = load_settings()
    if not settings:
        log_critical("Failed to load settings", "setup")
        print("❌ Failed to load settings")
        return 1
    
    jf = settings["api_keys"]["Jellyfin"][0]
    url, api_key, user_id = jf["url"], jf["api_key"], jf["user_id"]
    log_milestone(f"Loaded Jellyfin connection: {url}", "setup")

    if args.cmd == "check":
        with LoggedOperation("Connection check command", "check"):
            # Keep essential CLI feedback for connection check
            print(f"📡 Connecting to Jellyfin at {url}")
            try:
                libs = get_jellyfin_libraries(url, api_key, user_id)
                for lib in libs:
                    count = get_library_item_count(url, api_key, user_id, lib['Id'])
                    print(f"  - {lib['Name']} ({lib['Id']}): {count} items")
                log_milestone(f"Connection check successful: {len(libs)} libraries found", "check")
            except Exception as e:
                log_error(f"Connection check failed: {e}", "check")
                print(f"❌ Connection failed: {e}")
                return 1
        
        # Clean up posters if requested
        if hasattr(args, 'cleanup') and args.cleanup:
            with LoggedOperation("Poster cleanup after check", "cleanup"):
                print("\n🧹 Cleaning up poster directories...")
                try:
                    clean_poster_directories(
                        clean_modified=True,
                        clean_working=True,
                        clean_original=True,
                        verbose=True
                    )
                    log_milestone("Poster cleanup completed", "cleanup")
                except Exception as e:
                    log_error(f"Poster cleanup failed: {e}", "cleanup")
                    return 1
            
        return 0
    
    if args.cmd == "status":
        from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
        
        with LoggedOperation(f"Status check for library {args.library_id}", "status"):
            # Keep essential CLI feedback for status command
            print(f"📊 Checking processing status for library {args.library_id}")
            
            try:
                # Get tag from settings if not specified
                tag_to_check = args.tag
                if tag_to_check is None:
                    tagging_settings = get_tagging_settings()
                    tag_to_check = tagging_settings.get('tag_name', 'aphrodite-overlay')
                
                # Get all items in the library
                items = get_library_items(url, api_key, user_id, args.library_id)
                if not items:
                    log_warning(f"No items found in library {args.library_id}", "status")
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
                
                # Keep summary for user
                print(f"\n📈 Summary:")
                print(f"  Processed: {processed_count}/{len(items)} ({processed_count/len(items)*100:.1f}%)")
                print(f"  Unprocessed: {unprocessed_count}/{len(items)} ({unprocessed_count/len(items)*100:.1f}%)")
                
                log_milestone(f"Status check complete: {processed_count} processed, {unprocessed_count} unprocessed", "status")
                
            except Exception as e:
                log_error(f"Status check failed: {e}", "status")
                print(f"❌ Status check failed: {e}")
                return 1
        
        return 0
        
    if args.cmd == "cleanup":
        with LoggedOperation("Poster cleanup command", "cleanup"):
            # Invert the no-* arguments for the clean_* parameters
            clean_modified = not (hasattr(args, 'no_modified') and args.no_modified)
            clean_working = not (hasattr(args, 'no_working') and args.no_working)
            clean_original = not (hasattr(args, 'no_original') and args.no_original)
            verbose = not (hasattr(args, 'quiet') and args.quiet)
            
            try:
                success, message = clean_poster_directories(
                    clean_modified=clean_modified,
                    clean_working=clean_working,
                    clean_original=clean_original,
                    verbose=verbose
                )
                
                if success:
                    log_milestone(f"Poster cleanup successful: {message}", "cleanup")
                else:
                    log_error(f"Poster cleanup failed: {message}", "cleanup")
                    
                return 0 if success else 1
                
            except Exception as e:
                log_error(f"Poster cleanup error: {e}", "cleanup")
                return 1

    if args.cmd == "item":
        with LoggedOperation(f"Item processing command for {args.item_id}", "item"):
            # By default, all badge types are ON
            add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
            add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
            add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
            add_awards = not (hasattr(args, 'no_awards') and args.no_awards)
            skip_upload = hasattr(args, 'no_upload') and args.no_upload
            add_metadata_tag = not (hasattr(args, 'no_metadata_tag') and args.no_metadata_tag)
            
            try:
                # Silent processing - core function already handles logging
                ok = process_single_item(
                    url, api_key, user_id, args.item_id, args.retries,
                    add_audio=add_audio, add_resolution=add_resolution,
                    add_reviews=add_reviews, add_awards=add_awards,
                    skip_upload=skip_upload, add_metadata_tag=add_metadata_tag
                )
                
                if ok:
                    log_milestone(f"Item {args.item_id} processed successfully", "item")
                else:
                    log_error(f"Item {args.item_id} processing failed", "item")
                
                # Clean up posters if requested
                if hasattr(args, 'cleanup') and args.cleanup:
                    with LoggedOperation("Poster cleanup after item processing", "cleanup"):
                        print("\n🧹 Cleaning up poster directories...")
                        try:
                            clean_poster_directories(
                                clean_modified=True,
                                clean_working=True,
                                clean_original=True,
                                verbose=True
                            )
                            log_milestone("Post-processing cleanup completed", "cleanup")
                        except Exception as e:
                            log_error(f"Post-processing cleanup failed: {e}", "cleanup")
                            return 1
                        
                return 0 if ok else 1
                
            except Exception as e:
                log_error(f"Item processing command error: {e}", "item")
                return 1

    if args.cmd == "library":
        with LoggedOperation(f"Library processing command for {args.library_id}", "library_cmd"):
            # By default, all badge types are ON
            add_audio = not (hasattr(args, 'no_audio') and args.no_audio)
            add_resolution = not (hasattr(args, 'no_resolution') and args.no_resolution)
            add_reviews = not (hasattr(args, 'no_reviews') and args.no_reviews)
            add_awards = not (hasattr(args, 'no_awards') and args.no_awards)
            skip_upload = hasattr(args, 'no_upload') and args.no_upload
            add_metadata_tag = not (hasattr(args, 'no_metadata_tag') and args.no_metadata_tag)
            skip_processed = hasattr(args, 'skip_processed') and args.skip_processed
            
            try:
                # Silent processing - library function already handles logging
                process_library_items(
                    url, api_key, user_id, args.library_id, args.limit, args.retries,
                    add_audio=add_audio, add_resolution=add_resolution,
                    add_reviews=add_reviews, add_awards=add_awards,
                    skip_upload=skip_upload, add_metadata_tag=add_metadata_tag,
                    skip_processed=skip_processed
                )
                
                log_milestone(f"Library {args.library_id} processing command completed", "library_cmd")
                return 0
                
            except Exception as e:
                log_error(f"Library processing command error: {e}", "library_cmd")
                return 1

    # 🗄️ PHASE 3: Database Command Handlers
    if args.cmd == "db-status":
        if not DATABASE_COMMANDS_AVAILABLE:
            log_error("Database commands not available - check Phase 3 installation", "db_status")
            print("❌ Database commands not available. Please check Phase 3 installation.")
            return 1
        
        with LoggedOperation("Database status command", "db_status"):
            try:
                reporter = DatabaseReporter()
                reporter.print_status_report(library_id=args.library, detailed=args.detailed)
                reporter.close()
                log_milestone("Database status report generated", "db_status")
            except Exception as e:
                log_error(f"Database status generation failed: {e}", "db_status")
                print(f"❌ Error generating database status: {e}")
                return 1
        return 0
    
    if args.cmd == "check-reviews":
        if not DATABASE_COMMANDS_AVAILABLE:
            print("❌ Database commands not available. Please check Phase 3 installation.")
            return 1
        
        try:
            updater = ReviewUpdater(url, api_key, user_id)
            
            if args.update:
                # Actually update reviews
                items_needing_update = updater.check_items_needing_review_update(
                    args.library_id, args.hours
                )
                
                if not items_needing_update:
                    print("✅ All items have current review data")
                else:
                    item_ids = [item['jellyfin_item_id'] for item in items_needing_update]
                    if args.limit:
                        item_ids = item_ids[:args.limit]
                    
                    print(f"🔄 Updating reviews for {len(item_ids)} items...")
                    stats = updater.bulk_update_reviews(item_ids, rate_limit_seconds=1.5, max_items=args.limit)
                    print(f"\n📊 Update complete: {stats['successful']} successful, {stats['failed']} failed")
            else:
                # Just show summary
                summary = updater.get_review_update_summary(args.library_id, args.hours)
                
                print(f"\n📊 REVIEW UPDATE SUMMARY for Library {args.library_id}")
                print(f"🕒 Threshold: {args.hours} hours")
                print(f"📋 Total items needing update: {summary['total_items']}")
                print("\n📂 Breakdown:")
                print(f"  • Never checked: {summary['categories']['never_checked']}")
                print(f"  • Very stale (>7d): {summary['categories']['very_stale']}")
                print(f"  • Stale (>1d): {summary['categories']['stale']}")
                print(f"  • Recent: {summary['categories']['recent']}")
                
                if summary['total_items'] > 0:
                    print(f"\n💡 Run with --update to actually update these {summary['total_items']} items")
            
            updater.close()
        except Exception as e:
            print(f"❌ Error checking reviews: {e}")
            return 1
        return 0
    
    if args.cmd == "reprocess":
        if not DATABASE_COMMANDS_AVAILABLE:
            print("❌ Database commands not available. Please check Phase 3 installation.")
            return 1
        
        try:
            reporter = DatabaseReporter()
            
            # Get items that meet reprocessing criteria
            items_to_reprocess = reporter.get_items_for_reprocessing(
                failed_only=args.failed_only,
                older_than_days=args.older_than,
                library_id=args.library
            )
            
            if args.limit:
                items_to_reprocess = items_to_reprocess[:args.limit]
            
            reporter.close()
            
            if not items_to_reprocess:
                print("✅ No items found matching reprocessing criteria")
                return 0
            
            print(f"\n📋 Found {len(items_to_reprocess)} items matching criteria:")
            for i, item in enumerate(items_to_reprocess[:10], 1):  # Show first 10
                status_icon = "❌" if item['status'] == 'failed' else "⚠️"
                print(f"  {i}. {status_icon} {item['title']} ({item['type']}) - {item['status']}")
            
            if len(items_to_reprocess) > 10:
                print(f"  ... and {len(items_to_reprocess) - 10} more items")
            
            if args.dry_run:
                print(f"\n🔍 DRY RUN: Would reprocess {len(items_to_reprocess)} items")
                return 0
            
            # Ask for confirmation
            print(f"\n⚠️  This will reprocess {len(items_to_reprocess)} items.")
            confirm = input("Continue? (y/N): ").lower().strip()
            if confirm != 'y':
                print("❌ Reprocessing cancelled")
                return 0
            
            # Process items
            print(f"\n🚀 Starting reprocessing of {len(items_to_reprocess)} items...")
            successful = 0
            failed = 0
            
            for i, item in enumerate(items_to_reprocess, 1):
                print(f"\n[{i}/{len(items_to_reprocess)}] Reprocessing: {item['title']}")
                
                # Determine badge settings (use defaults for reprocessing)
                success = process_single_item(
                    url, api_key, user_id, item['item_id'], max_retries=3,
                    add_audio=True, add_resolution=True, add_reviews=True, add_awards=True,
                    skip_upload=False, add_metadata_tag=True
                )
                
                if success:
                    successful += 1
                    print("✅ Success")
                else:
                    failed += 1
                    print("❌ Failed")
                
                # Small delay between items
                time.sleep(1)
            
            print(f"\n📊 Reprocessing complete: {successful} successful, {failed} failed")
        
        except Exception as e:
            print(f"❌ Error during reprocessing: {e}")
            return 1
        return 0

    # 🗄️ PHASE 4: Enhanced Features Command Handlers
    if args.cmd == "report":
        try:
            from aphrodite_helpers.reporting import ProcessingHistoryReporter
            
            reporter = ProcessingHistoryReporter()
            
            if args.export:
                # Export data
                export_path = reporter.export_processing_data(
                    format=args.export,
                    library_id=args.library,
                    days_back=args.days
                )
                print(f"✅ Data exported to: {export_path}")
            else:
                # Generate comprehensive report
                report = reporter.generate_comprehensive_report(
                    library_id=args.library,
                    days_back=args.days
                )
                
                print(f"\n📊 COMPREHENSIVE PROCESSING REPORT")
                print(f"🕒 Period: {report['period_analyzed']}")
                print(f"📚 Library: {report['library_filter']}")
                print(f"📅 Generated: {report['generated_at']}")
                
                # Summary
                summary = report['summary']
                if summary.get('total_processed', 0) > 0:
                    print(f"\n📈 SUMMARY")
                    print(f"  • Total processed: {summary['total_processed']}")
                    print(f"  • Success rate: {summary['success_rate']}%")
                    print(f"  • Average time: {summary['avg_processing_time']}s")
                    print(f"  • Libraries: {summary['libraries_processed']}")
                    print(f"  • Item types: {summary['item_types_processed']}")
                    
                    # Performance insights
                    performance = report['performance']
                    if performance.get('by_item_type'):
                        print(f"\n⚡ PERFORMANCE BY TYPE")
                        for ptype in performance['by_item_type'][:3]:  # Top 3
                            print(f"  • {ptype['item_type']}: {ptype['avg_time']}s avg ({ptype['count']} items)")
                    
                    # Error insights
                    errors = report['errors']
                    if errors.get('common_errors'):
                        print(f"\n❌ COMMON ERRORS")
                        for error in errors['common_errors'][:3]:  # Top 3
                            print(f"  • {error['error_message'][:60]}... ({error['count']} occurrences)")
                    
                    # Recommendations
                    if report.get('recommendations'):
                        print(f"\n💡 RECOMMENDATIONS")
                        for rec in report['recommendations'][:3]:  # Top 3
                            print(f"  • {rec}")
                else:
                    print(f"\n📭 No items processed in the specified period")
                    
        except ImportError:
            print("❌ Enhanced reporting not available. Please check Phase 4 installation.")
            return 1
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return 1
        return 0
    
    if args.cmd == "settings-check":
        try:
            from aphrodite_helpers.settings_change_detector import SettingsChangeDetector
            
            detector = SettingsChangeDetector()
            
            if args.mark_for_reprocess:
                # Mark items for reprocessing
                result = detector.mark_items_for_settings_reprocessing(
                    library_id=args.library,
                    dry_run=args.dry_run
                )
                
                print(f"\n🔄 SETTINGS REPROCESSING RESULTS")
                print(f"🔧 Settings changed: {'Yes' if result['settings_changed'] else 'No'}")
                print(f"📋 Items found: {result['items_found']}")
                print(f"✅ Items marked: {result['items_marked']}")
                print(f"🔍 Dry run: {'Yes' if result['dry_run'] else 'No'}")
                print(f"📚 Library filter: {result['library_filter'] or 'All libraries'}")
                print(f"\n💬 {result['message']}")
                
                if result.get('sample_items'):
                    print(f"\n📄 Sample affected items:")
                    for item in result['sample_items']:
                        print(f"  • {item['title']} ({item['item_type']})")
            else:
                # Just generate report
                report = detector.get_settings_change_report(library_id=args.library)
                
                print(f"\n🔧 SETTINGS CHANGE REPORT")
                print(f"📅 Generated: {report['generated_at']}")
                print(f"📚 Library filter: {report['library_filter'] or 'All libraries'}")
                
                status = report['settings_status']
                print(f"\n📊 STATUS")
                print(f"  • Settings changed: {'Yes' if status['settings_changed'] else 'No'}")
                print(f"  • Current hash: {status['current_hash'][:8]}...")
                print(f"  • Stored hash: {(status['stored_hash'] or 'None')[:8] if status['stored_hash'] else 'None'}...")
                
                affected = report['affected_items']
                print(f"\n📋 AFFECTED ITEMS")
                print(f"  • Total items: {affected['count']}")
                
                if affected['by_type']:
                    print(f"  • By type:")
                    for item_type, count in affected['by_type'].items():
                        print(f"    - {item_type}: {count}")
                
                if report.get('recommendations'):
                    print(f"\n💡 RECOMMENDATIONS")
                    for rec in report['recommendations']:
                        print(f"  • {rec}")
                        
        except ImportError:
            print("❌ Settings change detection not available. Please check Phase 4 installation.")
            return 1
        except Exception as e:
            print(f"❌ Error checking settings: {e}")
            return 1
        return 0
    
    if args.cmd == "backup":
        try:
            from tools.database_backup import DatabaseBackup
            
            backup = DatabaseBackup()
            
            if args.backup_cmd == "create":
                compress = not args.no_compress
                include_timestamp = not args.no_timestamp
                backup_path = backup.create_full_backup(compress=compress, include_timestamp=include_timestamp)
                print(f"✅ Backup created: {backup_path}")
                
            elif args.backup_cmd == "restore":
                success = backup.restore_from_backup(args.backup_path, confirm=args.confirm)
                return 0 if success else 1
                
            elif args.backup_cmd == "list":
                backups = backup.list_backups()
                if not backups:
                    print("📭 No backups found")
                else:
                    print(f"\n📦 AVAILABLE BACKUPS ({len(backups)} found)")
                    for i, b in enumerate(backups, 1):
                        compressed_icon = "🗜️" if b['compressed'] else "📄"
                        print(f"  {i}. {compressed_icon} {b['filename']} ({b['size_formatted']}) - {b['created']}")
                        
            elif args.backup_cmd == "export":
                export_path = backup.export_to_json(
                    output_path=args.output,
                    include_sensitive=args.include_sensitive
                )
                print(f"✅ Database exported to JSON: {export_path}")
                
            elif args.backup_cmd == "import":
                success = backup.import_from_json(
                    args.json_path,
                    tables_to_import=args.tables,
                    merge_mode=args.merge
                )
                return 0 if success else 1
                
            elif args.backup_cmd == "cleanup":
                removed_count = backup.cleanup_old_backups(keep_count=args.keep)
                print(f"✅ Cleanup complete: removed {removed_count} old backups")
                
            elif args.backup_cmd == "verify":
                is_valid = backup.verify_backup(args.backup_path)
                return 0 if is_valid else 1
                
            else:
                # No subcommand provided
                print("❌ Please specify a backup operation: create, restore, list, export, import, cleanup, or verify")
                return 1
                
        except ImportError:
            print("❌ Database backup not available. Please check Phase 4 installation.")
            return 1
        except Exception as e:
            print(f"❌ Error during backup operation: {e}")
            return 1
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
