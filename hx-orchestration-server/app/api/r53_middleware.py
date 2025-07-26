"""
Custom Middleware for Orchestration Server (R5.3 Compliance)
Provides logging, metrics, and request processing middleware
"""
import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger("hx_orchestration.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware with structured format"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"- ID: {request_id} - Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- ID: {request_id} - Status: {response.status_code} "
                f"- Time: {process_time:.4f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- ID: {request_id} - Error: {str(e)} - Time: {process_time:.4f}s"
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics collection middleware for performance monitoring"""
    
    def __init__(self, app, metrics_collector=None):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            if self.metrics_collector:
                process_time = time.time() - start_time
                self.metrics_collector.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    duration=process_time
                )
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                process_time = time.time() - start_time
                self.metrics_collector.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=500,
                    duration=process_time,
                    error=True
                )
            raise

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for request validation and rate limiting"""
    
    def __init__(self, app, rate_limit_requests_per_minute: int = 1000):
        super().__init__(app)
        self.rate_limit = rate_limit_requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Basic rate limiting
        current_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Reset counters every minute
        if current_time - self.last_reset > 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        # Check rate limit
        current_count = self.request_counts.get(client_ip, 0)
        if current_count >= self.rate_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Increment counter
        self.request_counts[client_ip] = current_count + 1
        
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
