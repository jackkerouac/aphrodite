import os
import base64
from pathlib import Path

# Default paths for images
DEFAULT_ORIGINAL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'posters', 'original')
DEFAULT_MODIFIED_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'posters', 'modified')

def get_image_path(image_type, filename):
    """Get the full path for an image"""
    if image_type == 'original':
        return os.path.join(DEFAULT_ORIGINAL_PATH, filename)
    elif image_type == 'modified':
        return os.path.join(DEFAULT_MODIFIED_PATH, filename)
    else:
        raise ValueError(f"Unknown image type: {image_type}")

def get_image_as_base64(image_path):
    """Convert an image to base64 for embedding in HTML"""
    if not os.path.exists(image_path):
        return None
    
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine MIME type based on file extension
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
    
    return f"data:{mime_type};base64,{encoded_string}"

def get_image_pairs(page=1, per_page=20):
    """Get pairs of original and modified images (paginated)"""
    # Ensure directories exist
    os.makedirs(DEFAULT_ORIGINAL_PATH, exist_ok=True)
    os.makedirs(DEFAULT_MODIFIED_PATH, exist_ok=True)
    
    # Get all modified images (as these represent completed jobs)
    modified_files = [f for f in os.listdir(DEFAULT_MODIFIED_PATH) 
                     if os.path.isfile(os.path.join(DEFAULT_MODIFIED_PATH, f)) and 
                     f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Sort by modification time (newest first)
    modified_files.sort(key=lambda f: os.path.getmtime(os.path.join(DEFAULT_MODIFIED_PATH, f)), reverse=True)
    
    # Calculate pagination
    total = len(modified_files)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # Apply pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_files = modified_files[start:end]
    
    # Create pairs of original and modified images
    image_pairs = []
    for filename in paginated_files:
        original_path = os.path.join(DEFAULT_ORIGINAL_PATH, filename)
        modified_path = os.path.join(DEFAULT_MODIFIED_PATH, filename)
        
        # Only include if both original and modified exist
        if os.path.exists(original_path):
            image_pairs.append({
                'id': os.path.splitext(filename)[0],
                'filename': filename,
                'originalPath': original_path,
                'modifiedPath': modified_path,
                'timestamp': os.path.getmtime(modified_path)
            })
    
    return {
        'images': image_pairs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }
