# aphrodite_helpers/docker_check_jellyfin_connection.py
"""Docker-friendly version of check_jellyfin_connection.py"""

import yaml
import requests
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_jellyfin_connection(url, api_key, user_id=None):
    """Check if we can connect to the Jellyfin server."""
    logger.info(f"Checking connection to Jellyfin at {url} with user_id: {user_id}")
    
    # Ensure URL doesn't end with a slash for consistent API paths
    if url.endswith('/'):
        url = url[:-1]
    
    headers = {"X-Emby-Token": api_key}
    
    try:
        # First, check if the server is responding at all
        logger.info(f"Testing server info endpoint: {url}/System/Info")
        resp = requests.get(f"{url}/System/Info", headers=headers)
        resp.raise_for_status()
        
        server_info = resp.json()
        server_name = server_info.get('ServerName', 'Unknown')
        version = server_info.get('Version', 'Unknown')
        
        logger.info(f"Success: Connected to Jellyfin server: {server_name} (Version {version})")
        print(f"Success: Connected to Jellyfin server: {server_name} (Version {version})")
        
        # If user_id is provided, check if we can access the user's data
        if user_id:
            logger.info(f"Testing user access: {url}/Users/{user_id}")
            resp = requests.get(f"{url}/Users/{user_id}", headers=headers)
            resp.raise_for_status()
            
            user_info = resp.json()
            user_name = user_info.get('Name', 'Unknown')
            
            logger.info(f"Success: Authenticated as user: {user_name}")
            print(f"Success: Authenticated as user: {user_name}")
            
            # Check libraries
            libraries = get_jellyfin_libraries(url, api_key, user_id)
            print("\nAvailable libraries:")
            
            if not libraries:
                print("  None found")
            else:
                for lib in libraries:
                    lib_name = lib.get('Name', 'Unnamed')
                    lib_id = lib.get('Id')
                    print(f"  - {lib_name} (ID: {lib_id})")
        
        return True
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Error: Connection error - Could not connect to Jellyfin server: {e}"
        logger.error(error_msg)
        print(error_msg)
        return False
    except requests.exceptions.HTTPError as e:
        error_msg = f"Error: HTTP error - Server returned error code: {e}"
        logger.error(error_msg)
        print(error_msg)
        return False
    except requests.RequestException as e:
        error_msg = f"Error: Error connecting to Jellyfin: {e}"
        logger.error(error_msg)
        print(error_msg)
        return False
    except Exception as e:
        error_msg = f"Error: Unexpected error checking Jellyfin connection: {e}"
        logger.error(error_msg)
        print(error_msg)
        return False

def get_jellyfin_libraries(url, api_key, user_id):
    """Get all libraries (views) from Jellyfin for a specific user."""
    headers = {"X-Emby-Token": api_key}
    try:
        logger.info(f"Getting libraries: {url}/Users/{user_id}/Views")
        resp = requests.get(f"{url}/Users/{user_id}/Views", headers=headers)
        resp.raise_for_status()
        return resp.json().get('Items', [])
    except requests.RequestException as e:
        logger.error(f"Error: Error getting Jellyfin libraries: {e}")
        return []

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Jellyfin connection.")
    parser.add_argument("--url", required=True, help="Jellyfin server URL")
    parser.add_argument("--api-key", required=True, help="Jellyfin API key")
    parser.add_argument("--user-id", required=True, help="Jellyfin user ID")
    
    args = parser.parse_args()
    
    # Log the arguments
    logger.info(f"Command line arguments: url={args.url}, api_key={'*' * len(args.api_key)}, user_id={args.user_id}")
    
    # Check connection with timeout handling
    try:
        result = check_jellyfin_connection(args.url, args.api_key, args.user_id)
        if not result:
            sys.exit(1)
    except Exception as e:
        logger.exception("Unhandled exception during connection check")
        print(f"Error: Unhandled exception: {e}")
        sys.exit(1)
