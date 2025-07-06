#!/usr/bin/env python3
# aphrodite_helpers/resize_posters.py

import os
import sys
import argparse
from pathlib import Path
from PIL import Image

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def resize_image(input_path, output_path, target_width=680, maintain_aspect=True):
    """
    Resize an image to the specified width while maintaining aspect ratio.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the resized image will be saved
        target_width (int): Desired width in pixels (default: 1000)
        maintain_aspect (bool): Whether to maintain aspect ratio (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Calculate new dimensions
        if maintain_aspect:
            # Calculate height to maintain aspect ratio
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
        else:
            # Use original height if not maintaining aspect
            target_height = img.height
        
        # Resize the image
        resized_img = img.resize((target_width, target_height), Image.LANCZOS)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the resized image
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            # Convert to RGB for JPEG (removes alpha channel if present)
            resized_img = resized_img.convert('RGB')
            resized_img.save(output_path, 'JPEG', quality=95)
        else:
            # Save with original format
            resized_img.save(output_path)
        
        print(f"✅ Resized {os.path.basename(input_path)} to {target_width}px width")
        return True
        
    except Exception as e:
        print(f"❌ Error resizing {os.path.basename(input_path)}: {e}")
        return False

def process_directory(input_dir, output_dir, target_width=1000):
    """
    Process all image files in a directory, resizing them to the target width.
    
    Args:
        input_dir (str): Directory containing images to resize
        output_dir (str): Directory where resized images will be saved
        target_width (int): Desired width in pixels (default: 1000)
    
    Returns:
        tuple: (total_processed, successful_count)
    """
    # Get absolute paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(root_dir, input_dir)
    output_path = os.path.join(root_dir, output_dir)
    
    # Ensure directories exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    
    # Get all image files in the input directory
    image_files = [f for f in os.listdir(input_path) 
                  if os.path.isfile(os.path.join(input_path, f)) and 
                  f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    if not image_files:
        print(f"ℹ️ No image files found in {input_path}")
        return 0, 0
    
    # Process each image
    successful_count = 0
    for img_file in image_files:
        input_file_path = os.path.join(input_path, img_file)
        output_file_path = os.path.join(output_path, img_file)
        
        if resize_image(input_file_path, output_file_path, target_width):
            successful_count += 1
    
    print(f"\n✅ Successfully resized {successful_count} of {len(image_files)} images")
    return len(image_files), successful_count

def main():
    """Main function to parse command line arguments and resize images."""
    parser = argparse.ArgumentParser(description="Resize images to a specified width while maintaining aspect ratio.")
    parser.add_argument(
        "--input", 
        default="posters/original", 
        help="Directory containing original images (default: posters/original)"
    )
    parser.add_argument(
        "--output", 
        default="/app/media/preview", 
        help="Output directory for resized images (default: /app/media/preview)"
    )
    parser.add_argument(
        "--width", 
        type=int,
        default=1000, 
        help="Target width in pixels (default: 1000)"
    )
    parser.add_argument(
        "--single",
        help="Resize a single image instead of a directory"
    )
    
    args = parser.parse_args()
    
    if args.single:
        # Process a single file
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_path = os.path.join(root_dir, args.single)
        
        # Determine output path
        filename = os.path.basename(input_path)
        output_path = os.path.join(root_dir, args.output, filename)
        
        success = resize_image(input_path, output_path, args.width)
        sys.exit(0 if success else 1)
    else:
        # Process a directory
        total, successful = process_directory(args.input, args.output, args.width)
        sys.exit(0 if successful > 0 else 1)

if __name__ == "__main__":
    main()
