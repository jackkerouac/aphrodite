#!/usr/bin/env python3
# aphrodite_helpers/v2_settings_bridge.py

"""
V2 Settings Bridge

Provides a bridge between v1 helpers (like tv_series_aggregator.py) and the v2 PostgreSQL-based settings system.
This allows v1 helpers to continue working without modification while using v2 database settings.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the API directory to the path so we can import v2 modules
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))

async def get_v2_settings():
    """Get settings from v2 PostgreSQL database and convert to v1 YAML format"""
    try:
        # Import v2 settings service
        from app.services.settings_service import settings_service
        
        # Get API keys using v2 system
        api_keys = await settings_service.get_api_keys_standalone(force_reload=True)
        
        # Get TV series settings 
        # In v2, these are stored as individual keys, we need to group them
        tv_settings = {}
        
        # Try to get some common TV series settings
        # These would need to be configured in the v2 database
        tv_settings['max_episodes_to_analyze'] = 50  # Default
        tv_settings['episode_timeout'] = 15  # Default  
        tv_settings['show_dominant_badges'] = True  # Default for now
        
        # Construct v1-compatible settings structure
        settings = {
            'api_keys': api_keys or {},
            'tv_series': tv_settings
        }
        
        return settings
        
    except Exception as e:
        print(f"Error loading v2 settings: {e}")
        return None

def load_settings_sync():
    """Synchronous wrapper for loading v2 settings"""
    try:
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, we need to run in a new thread
            import concurrent.futures
            import threading
            
            def run_in_thread():
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(get_v2_settings())
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result(timeout=10)
                
        except RuntimeError:
            # No event loop running, we can use asyncio.run() directly
            return asyncio.run(get_v2_settings())
            
    except Exception as e:
        print(f"Error in sync settings loading: {e}")
        return None

# Replace the load_settings function for v1 compatibility
def load_settings(path=None):
    """
    V1-compatible load_settings function that uses v2 PostgreSQL database.
    
    Args:
        path: Ignored in v2 (legacy parameter for YAML file path)
        
    Returns:
        Settings dictionary in v1 YAML format
    """
    return load_settings_sync()
