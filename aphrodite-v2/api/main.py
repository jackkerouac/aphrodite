"""
Aphrodite v2 FastAPI Application

Modern, async-first API server with structured logging and comprehensive monitoring.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import uuid

# Import our logging system
from aphrodite_logging import get_logger, setup_logging
from shared.types import BaseResponse, ErrorResponse

# Import core components
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.middleware.logging import LoggingMiddleware
from app.middleware.correlation import CorrelationMiddleware

# Import routes
from app.routes import health, media, jobs, config, system, maintenance, preview, poster_manager, poster_replacement, image_proxy, schedules, analytics
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
    logger.info("Starting Aphrodite v2 API server")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Add any other startup tasks here
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}", exc_info=True)
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Aphrodite v2 API server")
        await close_db()
        logger.info("Database connections closed")

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Aphrodite v2 API",
        description="Modern media poster enhancement system",
        version="2.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware (order matters!)
    
    # Correlation ID middleware (first, so it's available for all other middleware)
    app.add_middleware(CorrelationMiddleware)
    
    # Logging middleware (second, so it can log the correlation ID)
    app.add_middleware(LoggingMiddleware)
    
    # Security middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.api_host]
        )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(media.router, prefix="/api/v1/media", tags=["Media"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
    app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
    app.include_router(schedules.router, tags=["Schedules"])
    app.include_router(analytics.router, tags=["Analytics"])
    app.include_router(system.router, tags=["System"])
    app.include_router(maintenance.router, tags=["Maintenance"])
    app.include_router(preview.router, prefix="/api/v1/preview", tags=["Preview"])
    app.include_router(poster_manager.router, prefix="/api/v1/poster-manager", tags=["Poster Manager"])
    app.include_router(poster_replacement.router, prefix="/api/v1", tags=["Poster Replacement"])
    app.include_router(image_proxy.router, prefix="/api/v1/images", tags=["Image Proxy"])
    
    # Workflow routes
    app.include_router(job_router, tags=["Workflow"])
    app.include_router(control_router, tags=["Workflow Control"])
    app.include_router(progress_router, tags=["Workflow Progress"])
    
    # WebSocket route
    app.websocket("/api/v1/workflow/ws/{job_id}")(websocket_endpoint)
    
    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/api/v1/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Root endpoint
    @app.get("/", response_model=BaseResponse)
    async def root():
        """API root endpoint"""
        return BaseResponse(
            message="Aphrodite v2 API - Modern media poster enhancement system"
        )
    
    return app

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
