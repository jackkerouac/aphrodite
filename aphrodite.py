#!/usr/bin/env python3
# aphrodite.py  •  stripped-down (no StateManager)

import sys
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
from aphrodite_helpers.poster_fetcher import download_poster
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

                    v0.1.0       
"""

def display_banner() -> None:
    print(BANNER)


def process_single_item(jellyfin_url: str, api_key: str, user_id: str, 
                        item_id: str, max_retries: int = 3) -> bool:
    print(f"\n📋 Processing item {item_id}")

    # 1. Media info
    info = get_media_stream_info(jellyfin_url, api_key, user_id, item_id)
    if not info:
        print("❌ Failed to retrieve media information")
        return False

    codec = get_primary_audio_codec(info)
    print(f"📢 Found audio codec: {codec} for {info['name']}")

    # 2. Poster download
    poster_path = download_poster(jellyfin_url, api_key, item_id)
    if not poster_path:
        print("❌ Failed to download poster")
        return False

    # 3. Badge
    badge_settings = load_badge_settings()
    badge = create_badge(badge_settings, codec)
    output_path = apply_badge_to_poster(poster_path, badge, badge_settings)
    if not output_path:
        print("❌ Failed to apply badge to poster")
        return False

    # 4. Upload
    uploader = PosterUploader(jellyfin_url, api_key, user_id)
    if not uploader.upload_poster(item_id, output_path, max_retries):
        print("❌ Failed to upload modified poster")
        return False

    print(f"✅ Success: {info['name']}")
    return True


def process_library_items(jellyfin_url: str, api_key: str, user_id: str,
                          library_id: str, limit: int | None,
                          max_retries: int) -> None:
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
                            item_id, max_retries)
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

    lib_p = sub.add_parser("library", help="Process every item in a library")
    lib_p.add_argument("library_id")
    lib_p.add_argument("--limit", type=int)
    lib_p.add_argument("--retries", type=int, default=3)

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
        ok = process_single_item(url, api_key, user_id,
                                 args.item_id, args.retries)
        return 0 if ok else 1

    if args.cmd == "library":
        process_library_items(url, api_key, user_id, args.library_id,
                              args.limit, args.retries)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
