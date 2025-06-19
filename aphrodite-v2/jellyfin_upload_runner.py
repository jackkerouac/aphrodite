#!/usr/bin/env python3
"""
Jellyfin Upload Subprocess Runner - CLEAN OUTPUT VERSION
Isolated runner for Jellyfin uploads to avoid async context conflicts
"""

import sys
import json
import asyncio
import os
import logging
from pathlib import Path

def run_jellyfin_upload():
    """Run Jellyfin upload in isolated subprocess"""
    
    # CRITICAL: Suppress ALL logging to keep stdout clean for JSON response
    logging.getLogger().handlers = []
    logging.basicConfig(level=logging.CRITICAL)
    
    # Disable SQLAlchemy logging specifically
    logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
    logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
    
    try:
        # Read request from stdin
        request_json = sys.stdin.read().strip()
        request_data = json.loads(request_json)
        
        jellyfin_id = request_data["jellyfin_id"]
        poster_path = request_data["poster_path"]
        
        # Change to API directory
        script_dir = Path(__file__).parent
        api_dir = script_dir / "api"
        os.chdir(api_dir)
        sys.path.insert(0, str(api_dir))
        
        async def upload_and_tag():
            # Initialize database first
            from app.core.database import init_db
            await init_db()
            
            # Import services after database initialization
            from app.services.jellyfin_service import get_jellyfin_service
            from app.services.tag_management_service import get_tag_management_service
            
            jellyfin_service = get_jellyfin_service()
            
            # Upload enhanced poster to Jellyfin
            upload_success = await jellyfin_service.upload_poster_image(
                jellyfin_id, 
                poster_path
            )
            
            tag_success = False
            tag_error = None
            if upload_success:
                # Add aphrodite-overlay tag
                try:
                    tag_service = get_tag_management_service()
                    tag_result = await tag_service.add_tag_to_items([jellyfin_id], "aphrodite-overlay")
                    # Check if the tag was actually applied
                    tag_success = tag_result.processed_count > 0
                except Exception as e:
                    tag_error = str(e)
            else:
                # Even if upload fails, we should still try to add the tag for testing
                # This helps us isolate whether the tag issue is separate from upload issue
                try:
                    tag_service = get_tag_management_service()
                    tag_result = await tag_service.add_tag_to_items([jellyfin_id], "aphrodite-overlay")
                    tag_success = tag_result.processed_count > 0
                except Exception as e:
                    tag_error = str(e)
            
            return {
                "upload_success": upload_success,
                "tag_success": tag_success,
                "tag_error": tag_error
            }
        
        # Run async function
        result = asyncio.run(upload_and_tag())
        
        # Return clean JSON response
        print(json.dumps(result))
        
    except Exception as e:
        error_response = {
            "upload_success": False,
            "tag_success": False,
            "error": str(e)
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    run_jellyfin_upload()
