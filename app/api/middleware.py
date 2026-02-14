"""Logging and tracing middleware."""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.logging import get_logger

logger = get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Request-ID into application state and logs."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in state for later use if needed
        request.state.request_id = request_id
        
        # Create a contextual filter to inject request_id into logs
        class RequestIDFilter(logging.Filter):
            def filter(self, record):
                record.request_id = request_id
                return True
        
        # Apply filter to all loggers for this request scope
        # Note: In a truly async environment, we usually use contextvars
        # But for this simple implementation, we'll ensure the root logger handles it
        root_logger = logging.getLogger()
        request_filter = RequestIDFilter()
        root_logger.addFilter(request_filter)
        
        start_time = time.time()
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful requests
            logger.info(
                f"Request finished",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
        finally:
            root_logger.removeFilter(request_filter)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to inject security headers."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
