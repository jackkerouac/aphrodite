#!/usr/bin/env python3
# aphrodite.py

import os
import sys
import argparse
import time
from pathlib import Path

# Import aphrodite helpers
from aphrodite_helpers.settings_validator import run_settings_check
from aphrodite_helpers.check_jellyfin_connection import (
    load_settings,
    get_jellyfin_libraries,
    get_library_item_count,
    get_library_items
)
from aphrodite_helpers.state_manager import StateManager
from aphrodite_helpers.get_media_info import (
    get_media_stream_info,
    get_primary_audio_codec
)
from aphrodite_helpers.poster_fetcher import download_poster
from aphrodite_helpers.apply_badge import (
    load_badge_settings,
    create_badge,
    apply_badge_to_poster
)
from aphrodite_helpers.poster_uploader import PosterUploader

def display_banner():
    """Display the Aphrodite banner."""
    BANNER = r"""
              _                   _ _ _       
             | |                 | (_) |      
   __ _ _ __ | |__  _ __ ___   __| |_| |_ ___ 
  / _` | '_ \| '_ \| '__/ _ \ / _` | | __/ _ \
 | (_| | |_) | | | | | | (_) | (_| | | ||  __/
  \__,_| .__/|_| |_|_|  \___/ \__,_|_|\__\___|
       | |                                    
       |_|                                    

                    v0.1.0       
"""
    print(BANNER)

def process_single_item(jellyfin_url, api_key, user_id, item_id, state_manager, max_retries=3):
    """Process a single Jellyfin item through the complete workflow."""
    print(f"\n📋 Processing item: {item_id}")
    
    # Check if the item is already being processed
    current_state = state_manager.get_current_state(item_id)
    if current_state:
        print(f"⚠️  Item {item_id} is already in state: {current_state}")
        
        # Ask if the user wants to retry or continue from current state
        choice = input("Continue from current state? (y/n): ").lower()
        if choice != 'y':
            print("⏭️  Skipping item")
            return False
    else:
        # Create a new item in the state manager
        state_manager.create_item(item_id)
    
    try:
        # Step 1: Get media info
        print("Step 1: Getting media information...")
        media_info = get_media_stream_info(jellyfin_url, api_key, item_id)
        if not media_info:
            state_manager.mark_as_failed(item_id, "Failed to retrieve media information", "media_info")
            print("❌ Failed to retrieve media information")
            return False
        
        # Extract the audio codec
        audio_codec = get_primary_audio_codec(media_info)
        print(f"📢 Found audio codec: {audio_codec} for {media_info['name']}")
        
        # Update state with media info
        state_manager.update_item_metadata(item_id, {
            "name": media_info['name'],
            "type": media_info['type'],
            "audio_codec": audio_codec,
            "audio_codecs": media_info['audio_codecs'],
            "video_codecs": media_info['video_codecs']
        })
        
        # Step 2: Download the poster
        print("Step 2: Downloading poster...")
        poster_path = download_poster(jellyfin_url, api_key, item_id)
        if not poster_path:
            state_manager.mark_as_failed(item_id, "Failed to download poster", "download")
            print("❌ Failed to download poster")
            return False
        
        # Update state
        state_manager.transition_state(item_id, "downloaded", {
            "poster_path": poster_path
        })
        
        # Step 3: Process the poster (resize if needed)
        # TODO: Implement resizing module
        # For now, just transition the state
        state_manager.transition_state(item_id, "resized")
        
        # Step 4: Apply badge to poster
        print("Step 3: Applying badge...")
        badge_settings = load_badge_settings()
        badge = create_badge(badge_settings, audio_codec)
        
        output_path = apply_badge_to_poster(
            poster_path=poster_path,
            badge=badge,
            settings=badge_settings
        )
        
        if not output_path:
            state_manager.mark_as_failed(item_id, "Failed to apply badge to poster", "badge")
            print("❌ Failed to apply badge to poster")
            return False
        
        # Update state
        state_manager.transition_state(item_id, "badged", {
            "modified_poster_path": output_path
        })
        
        # Step 5: Upload the modified poster
        print("Step 4: Uploading modified poster...")
        uploader = PosterUploader(jellyfin_url, api_key, user_id, state_manager)
        
        success = uploader.upload_poster(item_id, output_path, max_retries)
        if not success:
            print("❌ Failed to upload modified poster")
            return False
        
        print(f"✅ Successfully processed item {item_id}")
        return True
        
    except Exception as e:
        error_message = f"Error processing item {item_id}: {str(e)}"
        print(f"❌ {error_message}")
        state_manager.mark_as_failed(item_id, error_message)
        return False

def process_library_items(jellyfin_url, api_key, user_id, library_id, state_manager, max_items=None, max_retries=3):
    """Process all items in a Jellyfin library."""
    print(f"\n📚 Processing items from library: {library_id}")
    
    # Get library items
    items = get_library_items(jellyfin_url, api_key, user_id, library_id)
    
    if not items:
        print("⚠️  No items found in library.")
        return False
    
    print(f"Found {len(items)} items in library")
    
    # Limit the number of items if specified
    if max_items and max_items > 0:
        items = items[:max_items]
        print(f"Processing the first {max_items} items")
    
    # Process each item
    success_count = 0
    for i, item in enumerate(items, 1):
        item_id = item.get('Id')
        item_name = item.get('Name', 'Unknown')
        
        print(f"\n[{i}/{len(items)}] Processing: {item_name} (ID: {item_id})")
        
        if process_single_item(jellyfin_url, api_key, user_id, item_id, state_manager, max_retries):
            success_count += 1
        
        # Add a small delay between items to avoid overwhelming the server
        if i < len(items):
            time.sleep(1)
    
    print(f"\n✅ Successfully processed {success_count} of {len(items)} items")
    return success_count > 0

def process_state_items(jellyfin_url, api_key, user_id, state, state_manager, max_items=None, max_retries=3):
    """Process items in a specific state."""
    print(f"\n🔄 Processing items in state: {state}")
    
    # Get items in the specified state
    items = state_manager.get_items_in_state(state)
    
    if not items:
        print(f"⚠️  No items found in state: {state}")
        return False
    
    print(f"Found {len(items)} items in state: {state}")
    
    # Limit the number of items if specified
    if max_items and max_items > 0:
        items = items[:max_items]
        print(f"Processing the first {max_items} items")
    
    # Process each item
    success_count = 0
    for i, item_id in enumerate(items, 1):
        item_data = state_manager.get_item_data(item_id)
        item_name = item_data.get('metadata', {}).get('name', 'Unknown')
        
        print(f"\n[{i}/{len(items)}] Processing: {item_name} (ID: {item_id})")
        
        if process_single_item(jellyfin_url, api_key, user_id, item_id, state_manager, max_retries):
            success_count += 1
        
        # Add a small delay between items to avoid overwhelming the server
        if i < len(items):
            time.sleep(1)
    
    print(f"\n✅ Successfully processed {success_count} of {len(items)} items")
    return success_count > 0

def show_status(state_manager):
    """Display the current status of all items."""
    print("\n📊 Current Processing Status")
    
    # Get counts for each state
    counts = state_manager.count_items_by_state()
    
    total = sum(counts.values())
    if total == 0:
        print("No items are currently being processed")
        return
    
    # Display counts
    print(f"Total items: {total}")
    for state, count in counts.items():
        if count > 0:
            percentage = (count / total) * 100
            print(f"  {state.upper()}: {count} ({percentage:.1f}%)")
    
    # Show details for failed items
    failed_items = state_manager.get_items_in_state("failed")
    if failed_items:
        print("\nFailed items:")
        for item_id in failed_items:
            item_data = state_manager.get_item_data(item_id)
            if item_data:
                name = item_data.get('metadata', {}).get('name', 'Unknown')
                failure_reason = item_data.get('metadata', {}).get('failure_reason', 'Unknown')
                print(f"  - {name} (ID: {item_id}): {failure_reason}")

def main():
    """Main entry point for Aphrodite."""
    # Display banner
    display_banner()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Aphrodite - Jellyfin Poster Processing System")
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check system settings and Jellyfin connection")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show processing status")
    
    # Process item command
    item_parser = subparsers.add_parser("item", help="Process a single item")
    item_parser.add_argument("item_id", help="Jellyfin item ID")
    item_parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    
    # Process library command
    library_parser = subparsers.add_parser("library", help="Process all items in a library")
    library_parser.add_argument("library_id", help="Jellyfin library ID")
    library_parser.add_argument("--limit", type=int, help="Limit the number of items to process")
    library_parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    
    # Process state command
    state_parser = subparsers.add_parser("state", help="Process items in a specific state")
    state_parser.add_argument("state", choices=StateManager.STATES, help="State to process")
    state_parser.add_argument("--limit", type=int, help="Limit the number of items to process")
    state_parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    
    # Retry command
    retry_parser = subparsers.add_parser("retry", help="Retry failed items")
    retry_parser.add_argument("--limit", type=int, help="Limit the number of items to retry")
    retry_parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run settings check
    run_settings_check()
    
    # Create state manager
    state_manager = StateManager()
    
    # Load settings
    settings = load_settings()
    if not settings:
        print("❌ Failed to load settings")
        return 1
    
    jellyfin_settings = settings['api_keys']['Jellyfin'][0]
    url = jellyfin_settings['url']
    api_key = jellyfin_settings['api_key']
    user_id = jellyfin_settings['user_id']
    
    # Process command
    if args.command == "check":
        print(f"\n📡 Connecting to Jellyfin at: {url}")
        libraries = get_jellyfin_libraries(url, api_key, user_id)
        
        if not libraries:
            print("⚠️  No libraries found in Jellyfin.")
            return 1
        
        print("\n📚 Libraries and item counts:")
        for lib in libraries:
            lib_name = lib.get('Name', 'Unnamed')
            lib_id = lib.get('Id')
            count = get_library_item_count(url, api_key, user_id, lib_id)
            print(f"  - {lib_name} (ID: {lib_id}): {count} items")
        
        return 0
    
    elif args.command == "status":
        show_status(state_manager)
        return 0
    
    elif args.command == "item":
        success = process_single_item(url, api_key, user_id, args.item_id, state_manager, args.retries)
        return 0 if success else 1
    
    elif args.command == "library":
        success = process_library_items(url, api_key, user_id, args.library_id, state_manager, args.limit, args.retries)
        return 0 if success else 1
    
    elif args.command == "state":
        success = process_state_items(url, api_key, user_id, args.state, state_manager, args.limit, args.retries)
        return 0 if success else 1
    
    elif args.command == "retry":
        failed_items = state_manager.get_items_in_state("failed")
        
        if not failed_items:
            print("No failed items to retry")
            return 0
        
        print(f"Found {len(failed_items)} failed items")
        
        # Limit the number of items if specified
        if args.limit and args.limit > 0:
            failed_items = failed_items[:args.limit]
            print(f"Retrying the first {args.limit} items")
        
        # Retry each failed item
        success_count = 0
        for i, item_id in enumerate(failed_items, 1):
            item_data = state_manager.get_item_data(item_id)
            item_name = item_data.get('metadata', {}).get('name', 'Unknown')
            
            print(f"\n[{i}/{len(failed_items)}] Retrying: {item_name} (ID: {item_id})")
            
            # Retry the item
            state_manager.retry_item(item_id)
            
            if process_single_item(url, api_key, user_id, item_id, state_manager, args.retries):
                success_count += 1
            
            # Add a small delay between items to avoid overwhelming the server
            if i < len(failed_items):
                time.sleep(1)
        
        print(f"\n✅ Successfully retried {success_count} of {len(failed_items)} items")
        return 0 if success_count > 0 else 1
    
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
