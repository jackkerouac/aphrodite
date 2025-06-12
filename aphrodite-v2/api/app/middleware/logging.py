"""
Request Logging Middleware

Comprehensive request/response logging with structured data and performance metrics.
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from aphrodite_logging import get_logger
from shared import LogContext

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging with structured data
    """
    
    def __init__(self, app, include_request_body: bool = False, include_response_body: bool = False):
        super().__init__(app)
        self.include_request_body = include_request_body
        self.include_response_body = include_response_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Get correlation ID from request state
        correlation_id = getattr(request.state, "correlation_id", None)
        
        # Create log context
        log_context = LogContext(
            correlation_id=correlation_id,
            service="api"
        )
        
        # Get logger with context
        logger = get_logger("aphrodite.api.requests", **log_context.to_dict())
        
        # Log request
        await self._log_request(logger, request)
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url}",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "duration": duration,
                    "error": str(e),
                    "exception_type": type(e).__name__
                }
            )
            raise
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        await self._log_response(logger, request, response, duration)
        
        return response
    
    async def _log_request(self, logger, request: Request):
        """Log incoming request"""
        
        # Prepare request data
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent")
        }
        
        # Include request body if enabled and appropriate
        if self.include_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Note: This reads the body, which may interfere with FastAPI's body parsing
                # In production, consider using a different approach
                body = await request.body()
                if body:
                    request_data["body_size"] = len(body)
                    # Only log body for small payloads to avoid log bloat
                    if len(body) < 1024:
                        try:
                            request_data["body"] = json.loads(body.decode())
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            request_data["body"] = "<binary or invalid JSON>"
            except Exception:
                request_data["body"] = "<error reading body>"
        
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra=request_data
        )
    
    async def _log_response(self, logger, request: Request, response: Response, duration: float):
        """Log outgoing response"""
        
        # Prepare response data
        response_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": round(duration, 4),
            "response_headers": dict(response.headers)
        }
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = "error"
        elif response.status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
        
        # Include response body if enabled and appropriate
        if self.include_response_body and hasattr(response, "body"):
            try:
                if hasattr(response.body, "__len__"):
                    response_data["body_size"] = len(response.body)
                    # Only log small response bodies
                    if len(response.body) < 1024:
                        try:
                            response_data["body"] = json.loads(response.body.decode())
                        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                            response_data["body"] = "<binary or non-JSON>"
            except Exception:
                response_data["body"] = "<error reading response body>"
        
        # Log with appropriate level
        message = f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration:.4f}s)"
        
        if log_level == "error":
            logger.error(message, extra=response_data)
        elif log_level == "warning":
            logger.warning(message, extra=response_data)
        else:
            logger.info(message, extra=response_data)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
