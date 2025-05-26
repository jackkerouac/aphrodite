#!/usr/bin/env python3
# poster_cleanup.py

import os
import glob
import shutil
import sys

def clean_poster_directories(
    clean_modified=True, 
    clean_working=True, 
    clean_original=True, 
    verbose=True
):
    """
    Clean up the poster directories.
    
    Args:
        clean_modified (bool): Clean the modified posters directory
        clean_working (bool): Clean the working posters directory
        clean_original (bool): Clean the original posters directory
        verbose (bool): Print status messages
        
    Returns:
        tuple: (success, message) with success being a boolean and message a string
    """
    # Get the base path for posters
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "posters"
    )
    
    # Initialize directories to clean and their file counts
    dirs_to_clean = []
    file_counts = {}
    cleanup_results = {}
    
    # Add directories to clean based on parameters
    if clean_modified:
        dirs_to_clean.append(os.path.join(base_path, "modified"))
    if clean_working:
        dirs_to_clean.append(os.path.join(base_path, "working"))
    if clean_original:
        dirs_to_clean.append(os.path.join(base_path, "original"))
    
    # If no directories to clean, return success
    if not dirs_to_clean:
        return True, "No directories were specified for cleanup."
    
    # Check each directory
    for dir_path in dirs_to_clean:
        # Skip if directory doesn't exist
        if not os.path.exists(dir_path):
            if verbose:
                print(f"Directory not found: {dir_path}")
            cleanup_results[dir_path] = "Directory not found"
            continue
        
        # Count files in directory
        files = glob.glob(os.path.join(dir_path, "*"))
        file_counts[dir_path] = len(files)
        
        # Delete all files in directory
        try:
            # Use different methods based on number of files
            if file_counts[dir_path] > 100:
                # For many files, recreate the directory
                shutil.rmtree(dir_path)
                os.makedirs(dir_path, exist_ok=True)
            else:
                # For fewer files, delete them individually
                for file_path in files:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            
            cleanup_results[dir_path] = f"Deleted {file_counts[dir_path]} files"
            if verbose:
                print(f"✅ Cleaned {dir_path}: Deleted {file_counts[dir_path]} files")
        except Exception as e:
            cleanup_results[dir_path] = f"Error: {str(e)}"
            if verbose:
                print(f"❌ Failed to clean {dir_path}: {str(e)}")
    
    # Create summary message
    total_files_deleted = sum(file_counts.values())
    summary = f"Cleanup completed: {total_files_deleted} files deleted."
    for dir_path, result in cleanup_results.items():
        dir_name = os.path.basename(dir_path)
        summary += f"\n- {dir_name}: {result}"
    
    if verbose:
        print(f"✨ {summary}")
    
    return True, summary


def main():
    """CLI entrypoint when module is run directly"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up Aphrodite poster directories")
    parser.add_argument("--no-modified", action="store_true", help="Don't clean the modified posters directory")
    parser.add_argument("--no-working", action="store_true", help="Don't clean the working posters directory")
    parser.add_argument("--no-original", action="store_true", help="Don't clean the original posters directory")
    parser.add_argument("--quiet", action="store_true", help="Don't print status messages")
    
    args = parser.parse_args()
    
    # Invert the no-* arguments for the clean_* parameters
    clean_modified = not args.no_modified
    clean_working = not args.no_working
    clean_original = not args.no_original
    verbose = not args.quiet
    
    success, message = clean_poster_directories(
        clean_modified=clean_modified,
        clean_working=clean_working,
        clean_original=clean_original,
        verbose=verbose
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
