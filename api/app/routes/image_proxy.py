"""
Image Proxy Routes

Proxy Jellyfin images through our backend to avoid Next.js hostname restrictions.
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import aiohttp
from typing import Optional
import io
import urllib.parse

from app.services.jellyfin_service import get_jellyfin_service
from aphrodite_logging import get_logger

router = APIRouter(tags=["image-proxy"])
logger = get_logger("aphrodite.api.image_proxy", service="api")

@router.get("/proxy/image/{item_id}")
async def proxy_jellyfin_image(item_id: str, image_type: str = "Primary"):
    """
    Proxy Jellyfin images through our backend to avoid CORS and hostname issues
    
    Args:
        item_id: Jellyfin item ID
        image_type: Type of image (Primary, Backdrop, etc.)
    """
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Build the image URL
        image_url = f"{jellyfin_service.base_url}/Items/{item_id}/Images/{image_type}"
        
        logger.debug(f"Proxying image request: {image_url}")
        
        # Get the image from Jellyfin
        session = await jellyfin_service._get_session()
        
        async with session.get(image_url) as response:
            if response.status == 200:
                # Get the content type
                content_type = response.headers.get('content-type', 'image/jpeg')
                
                # Read the image data
                image_data = await response.read()
                
                logger.debug(f"Successfully proxied image for item {item_id}: {len(image_data)} bytes")
                
                # Return the image with proper headers
                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                        "Content-Length": str(len(image_data))
                    }
                )
            else:
                logger.warning(f"Jellyfin returned status {response.status} for item {item_id}")
                raise HTTPException(status_code=404, detail="Image not found")
                
    except Exception as e:
        logger.error(f"Error proxying image for item {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to proxy image")

@router.get("/proxy/image/{item_id}/thumbnail")
async def proxy_jellyfin_thumbnail(
    item_id: str, 
    width: Optional[int] = 300,
    height: Optional[int] = 450,
    quality: Optional[int] = 80,
    restored: Optional[str] = None,  # Cache-busting parameter
    refresh: Optional[str] = None,   # Alternative cache-busting parameter
    load: Optional[str] = None       # Page load cache-busting parameter
):
    """
    Proxy Jellyfin images with thumbnail sizing
    
    Args:
        item_id: Jellyfin item ID
        width: Thumbnail width
        height: Thumbnail height  
        quality: Image quality (1-100)
        restored: Cache-busting parameter (timestamp when poster was restored)
        refresh: Alternative cache-busting parameter
        load: Page load cache-busting parameter
    """
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Build the thumbnail URL with parameters
        image_url = f"{jellyfin_service.base_url}/Items/{item_id}/Images/Primary"
        params = {
            "width": width,
            "height": height,
            "quality": quality
        }
        
        logger.debug(f"Proxying thumbnail request: {image_url} with params {params}")
        
        # Determine cache behavior based on cache-busting parameters
        is_cache_busted = restored is not None or refresh is not None or load is not None
        if is_cache_busted:
            cache_params = []
            if restored: cache_params.append(f"restored={restored}")
            if refresh: cache_params.append(f"refresh={refresh}")
            if load: cache_params.append(f"load={load}")
            logger.debug(f"Cache-busting detected for item {item_id} ({', '.join(cache_params)})")
        
        # Get the image from Jellyfin
        session = await jellyfin_service._get_session()
        
        async with session.get(image_url, params=params) as response:
            if response.status == 200:
                # Get the content type
                content_type = response.headers.get('content-type', 'image/jpeg')
                
                # Read the image data
                image_data = await response.read()
                
                logger.debug(f"Successfully proxied thumbnail for item {item_id}: {len(image_data)} bytes")
                
                # Set cache headers based on whether this is cache-busted
                if is_cache_busted:
                    # No cache for cache-busted requests (force fresh fetch)
                    cache_control = "no-cache, no-store, must-revalidate"
                    # Add additional headers to really prevent caching
                    headers = {
                        "Cache-Control": cache_control,
                        "Pragma": "no-cache",
                        "Expires": "0",
                        "Content-Length": str(len(image_data))
                    }
                    logger.debug(f"Using no-cache headers for cache-busted request: {item_id}")
                else:
                    # Much shorter cache for regular requests (5 minutes instead of 2 hours)
                    cache_control = "public, max-age=300"  # Cache thumbnails for 5 minutes only
                    headers = {
                        "Cache-Control": cache_control,
                        "Content-Length": str(len(image_data))
                    }
                
                # Return the image with appropriate headers
                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers=headers
                )
            else:
                logger.warning(f"Jellyfin returned status {response.status} for thumbnail {item_id}")
                raise HTTPException(status_code=404, detail="Thumbnail not found")
                
    except Exception as e:
        logger.error(f"Error proxying thumbnail for item {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to proxy thumbnail")

@router.get("/proxy/external/")
async def proxy_external_image(url: str, w: Optional[int] = 384, q: Optional[int] = 75):
    """
    Proxy external images (like TMDB) through our backend to avoid CORS issues
    
    Args:
        url: External image URL to proxy
        w: Width parameter (for compatibility with Next.js)
        q: Quality parameter (for compatibility with Next.js)
    """
    try:
        # Decode the URL parameter
        decoded_url = urllib.parse.unquote(url)
        
        logger.debug(f"Proxying external image request: {decoded_url}")
        
        # Validate URL to prevent SSRF attacks
        if not decoded_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL scheme")
        
        # Get the image from external source
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(decoded_url) as response:
                if response.status == 200:
                    # Get the content type
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    
                    # Read the image data
                    image_data = await response.read()
                    
                    logger.debug(f"Successfully proxied external image: {len(image_data)} bytes")
                    
                    # Return the image with proper CORS headers
                    return Response(
                        content=image_data,
                        media_type=content_type,
                        headers={
                            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                            "Access-Control-Allow-Headers": "*",
                            "Content-Length": str(len(image_data))
                        }
                    )
                else:
                    logger.warning(f"External service returned status {response.status} for URL: {decoded_url}")
                    raise HTTPException(status_code=404, detail="External image not found")
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error proxying external image {decoded_url}: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch external image")
    except Exception as e:
        logger.error(f"Error proxying external image {decoded_url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to proxy external image")
