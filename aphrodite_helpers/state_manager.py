#!/usr/bin/env python3
# aphrodite_helpers/state_manager.py

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for the state manager
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("state_manager")

class StateManager:
    """
    Manages the state of items being processed by Aphrodite.
    
    The state management works as follows:
    1. Each item is represented by a state file (JSON) containing metadata about the item.
    2. As the item progresses through the workflow, its state file moves between the different state directories.
    3. A state transition updates both the state file contents and moves it to the appropriate directory.
    4. Failure handling includes retry logic and detailed error tracking.
    """
    
    STATES = [
        "pending",      # Item identified but processing not started
        "downloaded",   # Poster successfully downloaded
        "resized",      # Poster resized if needed
        "badged",       # Badge successfully applied to poster
        "uploaded",     # Modified poster uploaded to Jellyfin
        "failed"        # Processing failed at some point
    ]
    
    def __init__(self, root_dir=None):
        """Initialize the StateManager."""
        if root_dir:
            self.root_dir = root_dir
        else:
            # Default to the project root directory
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.state_dir = os.path.join(self.root_dir, "workflow_state")
        
        # Ensure all state directories exist
        for state in self.STATES:
            state_path = os.path.join(self.state_dir, state)
            os.makedirs(state_path, exist_ok=True)
    
    def _get_state_file_path(self, item_id, state):
        """Get the path to a state file for a specific item and state."""
        return os.path.join(self.state_dir, state, f"{item_id}.json")
    
    def _load_state_file(self, item_id, state):
        """Load a state file for a specific item and state."""
        state_file_path = self._get_state_file_path(item_id, state)
        
        if not os.path.exists(state_file_path):
            return None
        
        try:
            with open(state_file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading state file for item {item_id} in state {state}: {e}")
            return None
    
    def create_item(self, item_id, metadata=None):
        """
        Create a new item in the pending state.
        
        Args:
            item_id (str): The unique identifier for the item
            metadata (dict, optional): Additional metadata to store with the item
            
        Returns:
            bool: True if the item was created successfully, False otherwise
        """
        # Check if item already exists in any state
        for state in self.STATES:
            state_file_path = self._get_state_file_path(item_id, state)
            if os.path.exists(state_file_path):
                logger.warning(f"Item {item_id} already exists in state {state}")
                return False
        
        # Create the state file
        state_data = {
            "item_id": item_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "state": "pending",
            "state_history": [
                {
                    "state": "pending",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "errors": [],
            "retry_count": 0,
            "metadata": metadata or {}
        }
        
        try:
            state_file_path = self._get_state_file_path(item_id, "pending")
            with open(state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"Item {item_id} created in pending state")
            return True
        except Exception as e:
            logger.error(f"Error creating state file for item {item_id}: {e}")
            return False
    
    def get_current_state(self, item_id):
        """
        Get the current state of an item.
        
        Args:
            item_id (str): The unique identifier for the item
            
        Returns:
            str or None: The current state of the item, or None if not found
        """
        for state in self.STATES:
            state_file_path = self._get_state_file_path(item_id, state)
            if os.path.exists(state_file_path):
                return state
        
        return None
    
    def get_item_data(self, item_id):
        """
        Get the state data for an item.
        
        Args:
            item_id (str): The unique identifier for the item
            
        Returns:
            dict or None: The state data for the item, or None if not found
        """
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return None
        
        return self._load_state_file(item_id, current_state)
    
    def update_item_metadata(self, item_id, metadata):
        """
        Update the metadata for an item.
        
        Args:
            item_id (str): The unique identifier for the item
            metadata (dict): The new metadata to merge with existing metadata
            
        Returns:
            bool: True if the metadata was updated successfully, False otherwise
        """
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return False
        
        state_data = self._load_state_file(item_id, current_state)
        if not state_data:
            logger.error(f"Failed to load state data for item {item_id}")
            return False
        
        # Merge metadata (update existing keys and add new ones)
        state_data["metadata"].update(metadata)
        state_data["updated_at"] = datetime.now().isoformat()
        
        try:
            state_file_path = self._get_state_file_path(item_id, current_state)
            with open(state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"Metadata updated for item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating metadata for item {item_id}: {e}")
            return False
    
    def transition_state(self, item_id, new_state, metadata=None):
        """
        Transition an item to a new state.
        
        Args:
            item_id (str): The unique identifier for the item
            new_state (str): The new state to transition to
            metadata (dict, optional): Additional metadata to update
            
        Returns:
            bool: True if the transition was successful, False otherwise
        """
        if new_state not in self.STATES:
            logger.error(f"Invalid state: {new_state}")
            return False
        
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return False
        
        # Load current state data
        state_data = self._load_state_file(item_id, current_state)
        if not state_data:
            logger.error(f"Failed to load state data for item {item_id}")
            return False
        
        # Update state info
        state_data["state"] = new_state
        state_data["updated_at"] = datetime.now().isoformat()
        state_data["state_history"].append({
            "state": new_state,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update metadata if provided
        if metadata:
            state_data["metadata"].update(metadata)
        
        # Reset retry count if moving to a new processing stage
        # (but not if retrying the same stage or moving to failed)
        if new_state != "failed" and new_state != current_state:
            state_data["retry_count"] = 0
        
        # Write state data to new location
        try:
            new_state_file_path = self._get_state_file_path(item_id, new_state)
            with open(new_state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # Remove old state file
            old_state_file_path = self._get_state_file_path(item_id, current_state)
            os.remove(old_state_file_path)
            
            logger.info(f"Item {item_id} transitioned from {current_state} to {new_state}")
            return True
        except Exception as e:
            logger.error(f"Error transitioning item {item_id} to {new_state}: {e}")
            return False
    
    def record_failure(self, item_id, error_message, error_source=None):
        """
        Record a failure for an item.
        
        Args:
            item_id (str): The unique identifier for the item
            error_message (str): The error message to record
            error_source (str, optional): The source of the error (e.g., 'download', 'badge')
            
        Returns:
            bool: True if the failure was recorded successfully, False otherwise
        """
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return False
        
        state_data = self._load_state_file(item_id, current_state)
        if not state_data:
            logger.error(f"Failed to load state data for item {item_id}")
            return False
        
        # Add error to the list
        error_entry = {
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "source": error_source or current_state
        }
        state_data["errors"].append(error_entry)
        state_data["updated_at"] = datetime.now().isoformat()
        
        # Increment retry count
        state_data["retry_count"] += 1
        
        try:
            # Save updated state data to the current state file
            state_file_path = self._get_state_file_path(item_id, current_state)
            with open(state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # If retry count exceeds threshold, move to failed state
            # This can be configured or handled externally
            
            logger.info(f"Failure recorded for item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error recording failure for item {item_id}: {e}")
            return False
    
    def mark_as_failed(self, item_id, error_message, error_source=None):
        """
        Mark an item as failed and move it to the failed state.
        
        Args:
            item_id (str): The unique identifier for the item
            error_message (str): The error message to record
            error_source (str, optional): The source of the error (e.g., 'download', 'badge')
            
        Returns:
            bool: True if the item was marked as failed successfully, False otherwise
        """
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return False
        
        # First record the failure
        if not self.record_failure(item_id, error_message, error_source):
            logger.error(f"Failed to record failure for item {item_id}")
            return False
        
        # Then transition to failed state
        metadata = {
            "failure_reason": error_message,
            "failed_at_state": current_state,
            "failure_source": error_source or current_state
        }
        
        return self.transition_state(item_id, "failed", metadata)
    
    def retry_item(self, item_id, target_state=None):
        """
        Retry processing an item, optionally transitioning to a specific state.
        
        Args:
            item_id (str): The unique identifier for the item
            target_state (str, optional): The state to transition to for retry
            
        Returns:
            bool: True if the retry was initiated successfully, False otherwise
        """
        current_state = self.get_current_state(item_id)
        if not current_state:
            logger.warning(f"Item {item_id} not found in any state")
            return False
        
        # If target_state not specified, determine it based on current state
        if not target_state:
            if current_state == "failed":
                # Get the state where it failed
                state_data = self._load_state_file(item_id, current_state)
                if not state_data:
                    logger.error(f"Failed to load state data for item {item_id}")
                    return False
                
                failed_at_state = state_data.get("metadata", {}).get("failed_at_state", "pending")
                target_state = failed_at_state
            else:
                # Stay in the current state (retry current operation)
                target_state = current_state
        
        # Check if target state is valid
        if target_state not in self.STATES:
            logger.error(f"Invalid target state for retry: {target_state}")
            return False
        
        # If already in that state, just update the state file
        if current_state == target_state:
            state_data = self._load_state_file(item_id, current_state)
            if not state_data:
                logger.error(f"Failed to load state data for item {item_id}")
                return False
            
            # Add retry event to history
            state_data["state_history"].append({
                "state": target_state,
                "timestamp": datetime.now().isoformat(),
                "event": "retry"
            })
            state_data["updated_at"] = datetime.now().isoformat()
            
            try:
                state_file_path = self._get_state_file_path(item_id, current_state)
                with open(state_file_path, 'w') as f:
                    json.dump(state_data, f, indent=2)
                
                logger.info(f"Item {item_id} retry initiated in state {target_state}")
                return True
            except Exception as e:
                logger.error(f"Error updating state file for retry of item {item_id}: {e}")
                return False
        else:
            # Transition to the target state for retry
            metadata = {"retry_from": current_state}
            return self.transition_state(item_id, target_state, metadata)
    
    def get_items_in_state(self, state):
        """
        Get all items in a specific state.
        
        Args:
            state (str): The state to query
            
        Returns:
            list: A list of item IDs in the specified state
        """
        if state not in self.STATES:
            logger.error(f"Invalid state: {state}")
            return []
        
        state_dir = os.path.join(self.state_dir, state)
        if not os.path.exists(state_dir):
            logger.warning(f"State directory for {state} does not exist")
            return []
        
        # Get all JSON files in the state directory
        item_files = [f for f in os.listdir(state_dir) if f.endswith('.json')]
        
        # Extract item IDs from filenames
        item_ids = [os.path.splitext(f)[0] for f in item_files]
        
        return item_ids
    
    def count_items_by_state(self):
        """
        Count the number of items in each state.
        
        Returns:
            dict: A dictionary with state names as keys and counts as values
        """
        counts = {}
        
        for state in self.STATES:
            state_dir = os.path.join(self.state_dir, state)
            if os.path.exists(state_dir):
                count = len([f for f in os.listdir(state_dir) if f.endswith('.json')])
                counts[state] = count
            else:
                counts[state] = 0
        
        return counts
    
    def get_next_pending_item(self):
        """
        Get the next pending item for processing.
        
        Returns:
            str or None: The ID of the next pending item, or None if no pending items
        """
        pending_items = self.get_items_in_state("pending")
        if not pending_items:
            return None
        
        # Sort by creation time
        pending_items_with_time = []
        for item_id in pending_items:
            state_data = self._load_state_file(item_id, "pending")
            if state_data:
                created_at = state_data.get("created_at")
                pending_items_with_time.append((item_id, created_at))
        
        # Sort by creation time (oldest first)
        pending_items_with_time.sort(key=lambda x: x[1])
        
        # Return the oldest item
        if pending_items_with_time:
            return pending_items_with_time[0][0]
        
        return None
    
    def cleanup_orphaned_files(self):
        """
        Clean up any orphaned state files (files with no corresponding poster).
        
        Returns:
            int: The number of orphaned files cleaned up
        """
        orphaned_count = 0
        
        # Get all state files from all states
        for state in self.STATES:
            state_dir = os.path.join(self.state_dir, state)
            if not os.path.exists(state_dir):
                continue
            
            item_files = [f for f in os.listdir(state_dir) if f.endswith('.json')]
            
            for item_file in item_files:
                item_id = os.path.splitext(item_file)[0]
                
                # Check if the poster files exist in the poster directories
                poster_exists = False
                poster_dirs = ["posters/original", "posters/working", "posters/modified"]
                
                for poster_dir in poster_dirs:
                    poster_path = os.path.join(self.root_dir, poster_dir, f"{item_id}.jpg")
                    if os.path.exists(poster_path):
                        poster_exists = True
                        break
                
                # If no poster files exist, this is an orphaned state file
                if not poster_exists:
                    try:
                        os.remove(os.path.join(state_dir, item_file))
                        logger.info(f"Cleaned up orphaned state file for item {item_id}")
                        orphaned_count += 1
                    except Exception as e:
                        logger.error(f"Error cleaning up orphaned state file for item {item_id}: {e}")
        
        return orphaned_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="State management for Aphrodite poster processing.")
    parser.add_argument(
        "--list", 
        choices=StateManager.STATES + ["all"],
        help="List items in a specific state"
    )
    parser.add_argument(
        "--count", 
        action="store_true",
        help="Count items in each state"
    )
    parser.add_argument(
        "--info", 
        metavar="ITEM_ID",
        help="Get information about a specific item"
    )
    parser.add_argument(
        "--retry", 
        metavar="ITEM_ID",
        help="Retry processing a specific item"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up orphaned state files"
    )
    
    args = parser.parse_args()
    
    state_manager = StateManager()
    
    if args.list:
        if args.list == "all":
            print("Items by state:")
            for state in StateManager.STATES:
                items = state_manager.get_items_in_state(state)
                if items:
                    print(f"  {state.upper()} ({len(items)}): {', '.join(items)}")
                else:
                    print(f"  {state.upper()} (0): None")
        else:
            items = state_manager.get_items_in_state(args.list)
            print(f"Items in state {args.list.upper()}:")
            if items:
                for item in items:
                    print(f"  - {item}")
            else:
                print("  None")
    
    elif args.count:
        counts = state_manager.count_items_by_state()
        print("Item counts by state:")
        for state, count in counts.items():
            print(f"  {state.upper()}: {count}")
        print(f"  TOTAL: {sum(counts.values())}")
    
    elif args.info:
        item_data = state_manager.get_item_data(args.info)
        if item_data:
            current_state = state_manager.get_current_state(args.info)
            print(f"Information for item {args.info} (Current state: {current_state.upper()}):")
            print(f"  Created: {item_data.get('created_at')}")
            print(f"  Updated: {item_data.get('updated_at')}")
            print(f"  Retry count: {item_data.get('retry_count', 0)}")
            
            # Print state history
            print("\n  State History:")
            for state_entry in item_data.get('state_history', []):
                state = state_entry.get('state', '?')
                timestamp = state_entry.get('timestamp', '?')
                print(f"    - {state.upper()} at {timestamp}")
            
            # Print errors
            errors = item_data.get('errors', [])
            if errors:
                print("\n  Errors:")
                for error in errors:
                    message = error.get('message', '?')
                    timestamp = error.get('timestamp', '?')
                    source = error.get('source', '?')
                    print(f"    - {timestamp} ({source}): {message}")
            
            # Print metadata
            metadata = item_data.get('metadata', {})
            if metadata:
                print("\n  Metadata:")
                for key, value in metadata.items():
                    print(f"    - {key}: {value}")
        else:
            print(f"No information found for item {args.info}")
    
    elif args.retry:
        success = state_manager.retry_item(args.retry)
        if success:
            current_state = state_manager.get_current_state(args.retry)
            print(f"Successfully initiated retry for item {args.retry} (Current state: {current_state.upper()})")
        else:
            print(f"Failed to retry item {args.retry}")
    
    elif args.cleanup:
        orphaned_count = state_manager.cleanup_orphaned_files()
        print(f"Cleaned up {orphaned_count} orphaned state files")
    
    else:
        parser.print_help()
        sys.exit(1)
