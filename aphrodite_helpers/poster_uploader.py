#!/usr/bin/env python3
# aphrodite_helpers/poster_uploader.py

import os
import sys
import time
import random
import logging
import requests
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("poster_uploader")

class PosterUploader:
    """
    Handles uploading modified posters back to Jellyfin.
    
    Features:
    - Built-in retry mechanism for handling transient failures
    - Verification of successful uploads
    - Integration with the state management system
    """
    
    def __init__(self, jellyfin_url, api_key, user_id=None, state_manager=None):
        """Initialize the PosterUploader."""
        self.jellyfin_url = jellyfin_url
        self.api_key = api_key
        self.user_id = user_id
        
        # Initialize state manager if provided
        if state_manager:
            self.state_manager = state_manager
        else:
            # Import here to avoid circular imports
            from aphrodite_helpers.state_manager import StateManager
            self.state_manager = StateManager()
        
    def upload_poster(self, item_id, poster_path, max_retries=3, retry_delay=2):
        """
        Upload a poster to Jellyfin for a specific item.
        
        Args:
            item_id (str): The Jellyfin item ID
            poster_path (str): Path to the poster image file
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Base delay between retries in seconds
            
        Returns:
            bool: True if the upload was successful, False otherwise
        """
        if not os.path.exists(poster_path):
            error_msg = f"Poster file not found: {poster_path}"
            logger.error(error_msg)
            if self.state_manager:
                self.state_manager.record_failure(item_id, error_msg, "upload")
            return False
        
        # Track retry attempts
        attempts = 0
        last_error = None
        
        # Prepare URL and headers
        upload_url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"
        headers = {"X-Emby-Token": self.api_key}
        
        while attempts < max_retries:
            try:
                # Read the image file
                with open(poster_path, 'rb') as f:
                    image_data = f.read()
                
                # Upload the poster
                logger.info(f"Uploading poster for item {item_id} (Attempt {attempts + 1}/{max_retries})")
                response = requests.post(
                    upload_url,
                    headers=headers,
                    data=image_data,
                    timeout=30  # Add a reasonable timeout
                )
                
                # Check if successful
                if response.status_code == 204 or response.status_code == 200:
                    logger.info(f"✅ Successfully uploaded poster for item {item_id}")
                    
                    # Update state if state manager is available
                    if self.state_manager:
                        current_state = self.state_manager.get_current_state(item_id)
                        if current_state == "badged":
                            self.state_manager.transition_state(item_id, "uploaded")
                    
                    # Verify the upload by checking if we can download the new poster
                    if self.verify_upload(item_id):
                        logger.info(f"✅ Verified upload for item {item_id}")
                        return True
                    else:
                        logger.warning(f"❌ Upload verification failed for item {item_id}, will retry")
                        last_error = "Upload verification failed"
                else:
                    error_msg = f"Failed to upload poster: HTTP {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    last_error = error_msg
            
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error while uploading poster: {str(e)}"
                logger.error(error_msg)
                last_error = error_msg
            except Exception as e:
                error_msg = f"Unexpected error while uploading poster: {str(e)}"
                logger.error(error_msg)
                last_error = error_msg
            
            # Record the failure in state manager if available
            if self.state_manager:
                self.state_manager.record_failure(item_id, last_error, "upload")
            
            # Increment attempts counter
            attempts += 1
            
            # If we've reached max retries, break out of the loop
            if attempts >= max_retries:
                break
            
            # Calculate exponential backoff with jitter
            # This increases the delay with each retry and adds some randomness
            # to prevent all retries happening at exactly the same time
            backoff_time = retry_delay * (2 ** (attempts - 1))  # Exponential backoff
            jitter = random.uniform(0, 0.5 * backoff_time)  # Add up to 50% jitter
            wait_time = backoff_time + jitter
            
            logger.info(f"Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        
        # If we've exhausted all retries, mark the item as failed in the state manager
        if self.state_manager:
            self.state_manager.mark_as_failed(item_id, f"Upload failed after {max_retries} attempts: {last_error}", "upload")
        
        logger.error(f"❌ Failed to upload poster for item {item_id} after {max_retries} attempts")
        return False
    
    def verify_upload(self, item_id, timeout=5):
        """
        Verify that a poster was successfully uploaded by attempting to download it.
        
        Args:
            item_id (str): The Jellyfin item ID
            timeout (int): Timeout for the verification request in seconds
            
        Returns:
            bool: True if verification was successful, False otherwise
        """
        try:
            # Allow a short delay for Jellyfin to process the upload
            time.sleep(1)
            
            # Try to download the primary image
            verification_url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"
            headers = {"X-Emby-Token": self.api_key}
            
            response = requests.get(
                verification_url,
                headers=headers,
                timeout=timeout,
                stream=True  # Use stream=True to avoid downloading the entire image
            )
            
            # Check if we can access the image
            if response.status_code == 200:
                # Read just the first few bytes to confirm it's an image
                first_bytes = next(response.iter_content(256))
                
                # Check for common image file signatures
                if (first_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
                    first_bytes.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
                    first_bytes.startswith(b'GIF')):  # GIF
                    return True
                else:
                    logger.warning(f"Verification response doesn't appear to be an image")
                    return False
            else:
                logger.warning(f"Verification failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error during upload verification: {str(e)}")
            return False

    def batch_upload_posters(self, item_mappings, max_retries=3, retry_delay=2):
        """
        Upload multiple posters in batch mode.
        
        Args:
            item_mappings (dict): Dictionary mapping item IDs to poster file paths
            max_retries (int): Maximum number of retry attempts per poster
            retry_delay (int): Base delay between retries in seconds
            
        Returns:
            dict: Dictionary with item IDs as keys and success status as values
        """
        results = {}
        total_items = len(item_mappings)
        
        logger.info(f"Starting batch upload of {total_items} posters")
        
        for i, (item_id, poster_path) in enumerate(item_mappings.items(), 1):
            logger.info(f"Processing item {i}/{total_items}: {item_id}")
            success = self.upload_poster(item_id, poster_path, max_retries, retry_delay)
            results[item_id] = success
        
        # Summarize results
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Batch upload complete: {success_count}/{total_items} successful")
        
        return results

if __name__ == "__main__":
    import argparse
    from aphrodite_helpers.check_jellyfin_connection import load_settings
    
    parser = argparse.ArgumentParser(description="Upload modified posters to Jellyfin.")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--poster", required=True, help="Path to poster image file")
    parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    if not settings:
        sys.exit(1)
    
    jellyfin_settings = settings['api_keys']['Jellyfin'][0]
    url = jellyfin_settings['url']
    api_key = jellyfin_settings['api_key']
    user_id = jellyfin_settings.get('user_id')
    
    # Initialize uploader
    uploader = PosterUploader(url, api_key, user_id)
    
    # Upload poster
    success = uploader.upload_poster(args.itemid, args.poster, args.retries)
    
    if success:
        print(f"✅ Poster for item {args.itemid} uploaded successfully")
        sys.exit(0)
    else:
        print(f"❌ Failed to upload poster for item {args.itemid}")
        sys.exit(1)
