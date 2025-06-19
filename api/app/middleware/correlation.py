"""
Correlation ID Middleware

Adds correlation IDs to requests for distributed tracing and log correlation.
"""

import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs to requests for tracing across services
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if correlation ID already exists in headers
        correlation_id = request.headers.get("X-Correlation-ID")
        
        if not correlation_id:
            # Generate new correlation ID
            correlation_id = str(uuid.uuid4())[:8]
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
