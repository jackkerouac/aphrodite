"""
Global Exception Handlers

Centralized exception handling with structured logging and consistent error responses.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from aphrodite_logging import get_logger
from shared import ErrorResponse, LogContext
from app.utils import JSONResponse

def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        correlation_id = getattr(request.state, "correlation_id", None)
        logger = get_logger("aphrodite.api.exceptions", correlation_id=correlation_id, service="api")
        
        logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
        "status_code": exc.status_code,
        "detail": exc.detail,
        "method": request.method,
        "url": str(request.url),
        "headers": dict(exc.headers) if exc.headers else None
        }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}"
            ).dict(),
            headers=exc.headers
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions"""
        correlation_id = getattr(request.state, "correlation_id", None)
        logger = get_logger("aphrodite.api.exceptions", correlation_id=correlation_id, service="api")
        
        logger.warning(
            f"Starlette HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "method": request.method,
                "url": str(request.url)
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}"
            ).dict()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        correlation_id = getattr(request.state, "correlation_id", None)
        logger = get_logger("aphrodite.api.exceptions", correlation_id=correlation_id, service="api")
        
        # Format validation errors
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error: {len(validation_errors)} field(s)",
            extra={
                "validation_errors": validation_errors,
                "method": request.method,
                "url": str(request.url)
            }
        )
        
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                message="Validation failed",
                error_code="VALIDATION_ERROR",
                details={
                    "validation_errors": validation_errors
                }
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        correlation_id = getattr(request.state, "correlation_id", None)
        logger = get_logger("aphrodite.api.exceptions", correlation_id=correlation_id, service="api")
        
        # Log full exception details
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "method": request.method,
                "url": str(request.url),
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return generic error response (don't expose internal details)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                error_code="INTERNAL_ERROR",
                details={
                    "correlation_id": correlation_id
                }
            ).dict()
        )

class AphroditeException(Exception):
    """Base exception for Aphrodite-specific errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "APHRODITE_ERROR"
        self.details = details or {}
        super().__init__(message)

class MediaNotFoundException(AphroditeException):
    """Raised when a media item is not found"""
    
    def __init__(self, media_id: str):
        super().__init__(
            message=f"Media item not found: {media_id}",
            error_code="MEDIA_NOT_FOUND",
            details={"media_id": media_id}
        )

class JobNotFoundException(AphroditeException):
    """Raised when a job is not found"""
    
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job not found: {job_id}",
            error_code="JOB_NOT_FOUND",
            details={"job_id": job_id}
        )

class ProcessingException(AphroditeException):
    """Raised when processing fails"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=f"Processing failed: {message}",
            error_code="PROCESSING_ERROR",
            details=details
        )

class JellyfinConnectionException(AphroditeException):
    """Raised when Jellyfin connection fails"""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Jellyfin connection failed: {message}",
            error_code="JELLYFIN_CONNECTION_ERROR"
        )
