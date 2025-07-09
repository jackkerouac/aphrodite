"""
Aphrodite v2 FastAPI Application with Next.js Frontend Integration

Modern, async-first API server with Next.js frontend serving and comprehensive monitoring.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path using environment variable for Docker compatibility
project_root = Path(os.environ.get('APHRODITE_ROOT', str(Path(__file__).parent.parent)))
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import uuid
import aiohttp

# Import our logging system
from aphrodite_logging import get_logger, setup_logging
from shared.types import BaseResponse, ErrorResponse

# Import core components
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.middleware.logging import LoggingMiddleware
from app.middleware.correlation import CorrelationMiddleware

# Import routes
from app.routes import health, media, jobs, config, system, maintenance, preview, poster_manager, poster_replacement, image_proxy, schedules, analytics, resolution_diagnostics, audio_diagnostics, jellyfin_diagnostics, infrastructure_diagnostics, batch_debug, activity_tracking
from app.routes.workflow import job_router, control_router, progress_router, websocket_endpoint

# Import exception handlers
from app.core.exceptions import register_exception_handlers

class LogContext:
    """Simple log context for compatibility"""
    def __init__(self, **kwargs):
        self.context = kwargs
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Initialize logging first
    setup_logging("development")
    logger = get_logger("aphrodite.api.startup", service="api")
    
    # Startup
    logger.info("Starting Aphrodite v2 API server with Next.js frontend integration")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Verify that session factory was created
        from app.core.database import async_session_factory, get_session_factory_status
        if async_session_factory is None:
            logger.error("CRITICAL: Session factory is None after database initialization!")
            status = get_session_factory_status()
            logger.error(f"Session factory status: {status}")
            # Try to reinitialize
            logger.info("Attempting to reinitialize database...")
            await init_db()
            if async_session_factory is None:
                logger.error("Session factory is still None after reinitialize - this will cause batch job failures")
            else:
                logger.info(f"Session factory recovered: {id(async_session_factory)}")
        else:
            logger.info(f"Session factory verified: {id(async_session_factory)}")
        
        # Auto-initialize badge settings if needed
        try:
            from api.database_defaults_init import auto_initialize_on_startup
            await auto_initialize_on_startup()
        except Exception as init_error:
            logger.warning(f"Badge settings auto-initialization failed: {init_error}")
        
        # NOTE: Automatic library scan disabled to prevent startup issues
        # The dashboard will fetch live counts directly from Jellyfin instead
        # Users can manually trigger scans from the Media page if needed
        # 
        # # Scan Jellyfin library on startup
        # try:
        #     from app.services.media_service import get_media_service
        #     from app.core.database import get_db_session
        #     
        #     logger.info("Performing initial Jellyfin library scan...")
        #     media_service = get_media_service()
        #     async for db in get_db_session():
        #         total, new, errors = await media_service.scan_jellyfin_library(db)
        #         if errors:
        #             logger.warning(f"Library scan completed with errors: {errors}")
        #         else:
        #             logger.info(f"Initial library scan complete: {total} found, {new} new items")
        #         break # Run only once
        # except Exception as scan_error:
        #     logger.error(f"Initial Jellyfin library scan failed: {scan_error}")
        
        # Check for frontend files
        frontend_path = Path(__file__).parent.parent / "frontend" / ".next"
        if frontend_path.exists():
            logger.info("Frontend build found - serving Next.js application")
            # Log the contents of the .next directory for debugging
            try:
                next_server_dir = frontend_path / "server"
                if next_server_dir.exists():
                    logger.info(f"Found Next.js server directory at {next_server_dir}")
                    logger.debug(f"Next.js server directory contents: {list(next_server_dir.glob('**/*.html'))}")
                else:
                    logger.warning(f"Next.js server directory not found at {next_server_dir}")
            except Exception as e:
                logger.warning(f"Error checking Next.js directory structure: {e}")
        else:
            logger.warning("Frontend build not found - API only mode")
        
        # Start WebSocket Redis listener (after database is fully initialized)
        try:
            # Import only when needed to avoid initialization during module loading
            from app.routes.workflow.websocket_routes import websocket_manager
            await websocket_manager.start_redis_listener()
            logger.info("WebSocket Redis listener started successfully")
        except Exception as e:
            logger.warning(f"Failed to start WebSocket Redis listener: {e}")
        
        # Start scheduler service
        try:
            from app.services.scheduler_service import get_scheduler_service
            scheduler_service = get_scheduler_service()
            await scheduler_service.start()
            logger.info("Scheduler service started successfully")
        except Exception as e:
            logger.warning(f"Failed to start scheduler service: {e}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}", exc_info=True)
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Aphrodite v2 API server")
        
        # Stop scheduler service
        try:
            from app.services.scheduler_service import get_scheduler_service
            scheduler_service = get_scheduler_service()
            await scheduler_service.stop()
            logger.info("Scheduler service stopped")
        except Exception as e:
            logger.warning(f"Error stopping scheduler service: {e}")
        
        # Stop WebSocket Redis listener
        try:
            # Import only when needed
            from app.routes.workflow.websocket_routes import websocket_manager
            await websocket_manager.stop_redis_listener()
            logger.info("WebSocket Redis listener stopped")
        except Exception as e:
            logger.warning(f"Error stopping WebSocket Redis listener: {e}")
        
        await close_db()
        logger.info("Database connections closed")

def create_application() -> FastAPI:
    """Create and configure FastAPI application with Next.js frontend integration"""
    settings = get_settings()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Aphrodite v2 API",
        description="Modern media poster enhancement system with Next.js frontend",
        version="2.0.0",
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        openapi_url="/api/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware (order matters!)
    # Correlation ID middleware (first, so it's available for all other middleware)
    app.add_middleware(CorrelationMiddleware)
    
    # Logging middleware (second, so it can log the correlation ID)
    app.add_middleware(LoggingMiddleware)
    
    # Security middleware - only apply host restrictions if not wildcard
    allowed_hosts_list = settings.get_allowed_hosts_list()
    if not settings.debug and "*" not in allowed_hosts_list:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts_list
        )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Setup static file serving BEFORE routes
    setup_static_files(app)
    
    # Include API routers with correct /api/v1 prefix to match frontend expectations
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(media.router, prefix="/api/v1/media", tags=["Media"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
    app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
    app.include_router(resolution_diagnostics.router, prefix="/api/v1/settings/resolution", tags=["Resolution Diagnostics"])
    app.include_router(audio_diagnostics.router, prefix="/api/v1/settings/audio", tags=["Audio Diagnostics"])
    app.include_router(schedules.router, prefix="/api/v1", tags=["Schedules"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(system.router, prefix="/api/v1", tags=["System"])
    app.include_router(maintenance.router, prefix="/api/v1", tags=["Maintenance"])
    app.include_router(preview.router, prefix="/api/v1/preview", tags=["Preview"])
    app.include_router(poster_manager.router, prefix="/api/v1/poster-manager", tags=["Poster Manager"])
    app.include_router(poster_replacement.router, prefix="/api/v1/poster-replacement", tags=["Poster Replacement"])
    app.include_router(image_proxy.router, prefix="/api/v1/images", tags=["Image Proxy"])
    app.include_router(jellyfin_diagnostics.router, prefix="/api/v1", tags=["Jellyfin Diagnostics"])
    app.include_router(infrastructure_diagnostics.router, prefix="/api/v1", tags=["Infrastructure Diagnostics"])
    app.include_router(batch_debug.router, prefix="/api/v1", tags=["Batch Debug"])
    app.include_router(activity_tracking.router, prefix="/api/v1", tags=["Activity Tracking"])
    
    # Workflow routes
    app.include_router(job_router, prefix="/api/v1", tags=["Workflow"])
    app.include_router(control_router, prefix="/api/v1", tags=["Workflow Control"])
    app.include_router(progress_router, prefix="/api/v1", tags=["Workflow Progress"])
    
    # WebSocket route
    app.websocket("/api/v1/workflow/ws/{job_id}")(websocket_endpoint)
    
    # Handle OPTIONS requests for Next.js image optimization
    @app.options("/_next/image")
    async def nextjs_image_options():
        """Handle CORS preflight for Next.js image optimization"""
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # Handle Next.js image optimization directly without redirects
    @app.get("/_next/image")
    async def nextjs_image_proxy(url: str, w: int = 384, q: int = 75):
        """Handle Next.js image optimization requests directly"""
        import urllib.parse
        import aiohttp
        from fastapi.responses import Response
        
        logger = get_logger("aphrodite.api.nextjs_image", service="api")
        
        try:
            # Decode the URL parameter
            decoded_url = urllib.parse.unquote(url)
            
            logger.info(f"🖼️ Next.js image optimization request: {decoded_url} (w={w}, q={q})")
            
            # Validate URL to prevent SSRF attacks
            if not decoded_url.startswith(('http://', 'https://')):
                logger.warning(f"❌ Invalid URL scheme in Next.js image request: {decoded_url}")
                raise HTTPException(status_code=400, detail="Invalid URL scheme")
            
            # Get the image from external source with timeout
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(decoded_url) as response:
                    if response.status == 200:
                        # Get the content type
                        content_type = response.headers.get('content-type', 'image/jpeg')
                        
                        # Read the image data
                        image_data = await response.read()
                        
                        logger.info(f"✅ Successfully served Next.js optimized image: {len(image_data)} bytes")
                        
                        # Return the image directly with proper headers
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
                        logger.warning(f"⚠️ External service returned status {response.status} for Next.js image: {decoded_url}")
                        raise HTTPException(status_code=404, detail="Image not found")
                        
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Network error in Next.js image optimization {decoded_url}: {e}")
            raise HTTPException(status_code=502, detail="Failed to fetch image")
        except Exception as e:
            logger.error(f"💥 Error in Next.js image optimization {decoded_url}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to optimize image")
    
    # Add redirect routes for endpoints without trailing slashes
    from fastapi.responses import RedirectResponse
    
    @app.get("/api/v1/schedules")
    async def redirect_schedules():
        return RedirectResponse("/api/v1/schedules/", status_code=307)
    
    @app.get("/api/v1/workflow/jobs")
    async def redirect_workflow_jobs():
        return RedirectResponse("/api/v1/workflow/jobs/", status_code=307)
    
    # API-only root endpoint for API access
    @app.get("/api", response_model=BaseResponse)
    async def api_root():
        """API root endpoint"""
        return BaseResponse(
            message="Aphrodite v2 API - Modern media poster enhancement system"
        )
    
    # Setup frontend serving AFTER API routes
    setup_frontend_routes(app)
    
    return app

def setup_static_files(app: FastAPI):
    """Setup static file serving for Next.js and API files"""
    logger = get_logger("aphrodite.api.static", service="api")
    settings = get_settings()

    # Paths for frontend files
    project_root = Path(__file__).parent.parent
    frontend_build = project_root / "frontend" / ".next"
    frontend_static = project_root / "frontend" / ".next" / "static"
    frontend_public = project_root / "frontend" / "public"

    # Create custom StaticFiles class with proper CORS headers
    class CORSStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope):
            response = await super().get_response(path, scope)
            # Add CORS headers for all static files
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = '*'
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            return response

    # CRITICAL FIX: Ensure directories exist before mounting static files
    # This is especially important when using host directory mounts
    directories_to_ensure = [
        (settings.static_originals_dir, "Original static files"),
        (settings.processed_dir, "Processed files"),
        (settings.preview_dir, "Preview files"),
        (settings.data_dir, "General API static files")
    ]
    
    for dir_path, description in directories_to_ensure:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Ensured directory exists: {dir_path} ({description})")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create directory {dir_path}: {e}")

    # Mount API static files from new volume locations
    # Original posters
    if Path(settings.static_originals_dir).exists():
        logger.info(f"Mounting original static files from {settings.static_originals_dir}")
        app.mount("/api/v1/static/originals", CORSStaticFiles(directory=settings.static_originals_dir), name="api-static-originals")
    else:
        logger.warning(f"Original static directory does not exist: {settings.static_originals_dir}")

    # Processed posters
    if Path(settings.processed_dir).exists():
        logger.info(f"Mounting processed static files from {settings.processed_dir}")
        app.mount("/api/v1/static/processed", CORSStaticFiles(directory=settings.processed_dir), name="api-static-processed")
    else:
        logger.warning(f"Processed directory does not exist: {settings.processed_dir}")

    # Preview files
    if Path(settings.preview_dir).exists():
        logger.info(f"Mounting preview static files from {settings.preview_dir}")
        app.mount("/api/v1/static/preview", CORSStaticFiles(directory=settings.preview_dir), name="api-static-preview")
    else:
        logger.warning(f"Preview directory does not exist: {settings.preview_dir}")

    # Mount Next.js static files (_next/static) - being specific to avoid conflicts
    if frontend_static.exists():
        logger.info(f"Mounting Next.js static files from {frontend_static}")
        app.mount("/_next/static", StaticFiles(directory=str(frontend_static), html=True), name="nextjs-static")

    # Mount public files
    if frontend_public.exists():
        logger.info(f"Mounting public files from {frontend_public}")
        app.mount("/public", StaticFiles(directory=str(frontend_public)), name="public")
        images_dir = frontend_public / "images"
        if images_dir.exists():
            app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")

    # Mount the general /api/v1/static route to the data directory for other static assets
    if Path(settings.data_dir).exists():
        logger.info(f"Mounting general API static files from {settings.data_dir}")
        app.mount("/api/v1/static", CORSStaticFiles(directory=settings.data_dir), name="api-static-general")
    else:
        logger.warning(f"Data directory does not exist: {settings.data_dir}")


def setup_frontend_routes(app: FastAPI):
    """Setup Next.js frontend page serving"""
    logger = get_logger("aphrodite.api.frontend", service="api")
    
    # Paths for frontend files
    project_root = Path(__file__).parent.parent
    frontend_build = project_root / "frontend" / ".next"
    
    # Check if frontend build exists
    if not frontend_build.exists():
        logger.warning("Frontend build not found - serving API-only mode")
        
        @app.get("/")
        async def fallback_root():
            return BaseResponse(
                message="Aphrodite v2 API - Frontend build not available, API-only mode"
            )
        return
    
    logger.info("Setting up Next.js frontend routes")
    
    # Root route - serve index page
    @app.get("/")
    async def serve_index():
        """Serve the Next.js index page"""
        index_file = frontend_build / "server" / "app" / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        else:
            # Fallback to a simple page
            return HTMLResponse(content=create_simple_frontend(), status_code=200)
    
    # Handle specific Next.js routes
    @app.get("/about")
    async def serve_about():
        """Serve the about page"""
        return serve_nextjs_page("about")
    
    @app.get("/analytics")
    async def serve_analytics():
        """Serve the analytics page"""
        return serve_nextjs_page("analytics")
    
    @app.get("/maintenance")
    async def serve_maintenance():
        """Serve the maintenance page"""
        return serve_nextjs_page("maintenance")
    
    @app.get("/poster-manager")
    async def serve_poster_manager():
        """Serve the poster manager page"""
        return serve_nextjs_page("poster-manager")
    
    @app.get("/preview")
    async def serve_preview():
        """Serve the preview page"""
        return serve_nextjs_page("preview")
    
    @app.get("/schedules")
    async def serve_schedules():
        """Serve the schedules page"""
        return serve_nextjs_page("schedules")
    
    @app.get("/settings")
    async def serve_settings():
        """Serve the settings page"""
        return serve_nextjs_page("settings")
    
    @app.get("/diagnostics")
    async def serve_diagnostics():
        """Serve the diagnostics page"""
        return serve_nextjs_page("diagnostics")
    
    # Catch-all for any other routes
    @app.get("/{full_path:path}")
    async def serve_frontend_catchall(full_path: str):
        """Catch-all for frontend routes"""
        
        # Skip API routes
        if full_path.startswith("api/") or full_path.startswith("health/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Skip Next.js internal routes
        if full_path.startswith("_next/"):
            raise HTTPException(status_code=404, detail="Static file not found")
        
        # For any other route, serve the index page (SPA behavior)
        return serve_nextjs_page("index")

def serve_nextjs_page(page_name: str):
    """Serve a specific Next.js page"""
    project_root = Path(__file__).parent.parent
    frontend_build = project_root / "frontend" / ".next"
    
    # Try to serve the specific page
    page_file = frontend_build / "server" / "app" / f"{page_name}.html"
    if page_file.exists():
        return FileResponse(str(page_file), media_type="text/html")
    
    # Fallback to index
    index_file = frontend_build / "server" / "app" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    
    # Final fallback
    return HTMLResponse(content=create_simple_frontend(), status_code=200)



def create_simple_frontend():
    """Create a simple frontend page when Next.js files aren't available"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aphrodite v2</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            padding: 2rem;
            text-align: center;
            border-bottom: 1px solid #334155;
        }
        .header h1 { 
            font-size: 3rem; 
            margin-bottom: 1rem; 
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header p { 
            font-size: 1.2rem; 
            color: #94a3b8; 
        }
        .content {
            flex: 1;
            padding: 3rem 2rem;
            text-align: center;
        }
        .nav {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            max-width: 800px;
            margin: 0 auto;
        }
        .nav-item {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
        }
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: #3b82f6;
            transform: translateY(-2px);
        }
        .nav-item h3 {
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            color: #3b82f6;
        }
        .nav-item p {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        .footer {
            padding: 2rem;
            text-align: center;
            border-top: 1px solid #334155;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Aphrodite v2</h1>
        <p>Modern Media Poster Enhancement System</p>
    </div>
    
    <div class="content">
        <div class="nav">
            <a href="/about" class="nav-item">
                <h3>About</h3>
                <p>Learn about Aphrodite v2</p>
            </a>
            <a href="/poster-manager" class="nav-item">
                <h3>Poster Manager</h3>
                <p>Manage your media posters</p>
            </a>
            <a href="/analytics" class="nav-item">
                <h3>Analytics</h3>
                <p>View system analytics</p>
            </a>
            <a href="/schedules" class="nav-item">
                <h3>Schedules</h3>
                <p>Manage processing schedules</p>
            </a>
            <a href="/settings" class="nav-item">
                <h3>Settings</h3>
                <p>Configure system settings</p>
            </a>
            <a href="/api/docs" class="nav-item">
                <h3>API Documentation</h3>
                <p>Explore the API endpoints</p>
            </a>
        </div>
    </div>
    
    <div class="footer">
        <p>Aphrodite v2 - Powered by FastAPI + Next.js</p>
    </div>
</body>
</html>"""
    return html_content

# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
