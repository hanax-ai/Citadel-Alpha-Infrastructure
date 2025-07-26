"""
R5.3 Middleware Components
Custom middleware for logging, metrics, and security
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import DispatchFunction
from starlette.types import ASGIApp
import time
import logging
import json
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    def __init__(self, app: ASGIApp, logger: Optional[logging.Logger] = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("middleware.logging")
    
    async def dispatch(self, request: Request, call_next: DispatchFunction) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Log request
        start_time = time.time()
        self.logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            self.logger.info(
                f"Response {request_id}: {response.status_code} "
                f"processed in {process_time:.4f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.logger.error(
                f"Error {request_id}: {str(e)} after {process_time:.4f}s"
            )
            raise

# Metrics Middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0
        self.request_times: Dict[str, list] = {}
        self.error_count = 0
        self.logger = logging.getLogger("middleware.metrics")
    
    async def dispatch(self, request: Request, call_next: DispatchFunction) -> Response:
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # Increment request counter
            self.request_count += 1
            
            # Process request
            response = await call_next(request)
            
            # Record metrics
            process_time = time.time() - start_time
            
            if endpoint not in self.request_times:
                self.request_times[endpoint] = []
            
            self.request_times[endpoint].append(process_time)
            
            # Keep only last 100 requests for each endpoint
            if len(self.request_times[endpoint]) > 100:
                self.request_times[endpoint] = self.request_times[endpoint][-100:]
            
            # Add metrics to response headers
            response.headers["X-Total-Requests"] = str(self.request_count)
            response.headers["X-Endpoint-Avg-Time"] = str(
                sum(self.request_times[endpoint]) / len(self.request_times[endpoint])
            )
            
            return response
            
        except Exception as e:
            # Increment error counter
            self.error_count += 1
            self.logger.error(f"Request error for {endpoint}: {str(e)}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "endpoint_metrics": {}
        }
        
        for endpoint, times in self.request_times.items():
            if times:
                metrics["endpoint_metrics"][endpoint] = {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times)
                }
        
        return metrics

# Security Middleware
class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for basic security headers and validation."""
    
    def __init__(self, app: ASGIApp, require_auth: bool = False, allowed_origins: Optional[list] = None):
        super().__init__(app)
        self.require_auth = require_auth
        self.allowed_origins = allowed_origins or ["*"]
        self.logger = logging.getLogger("middleware.security")
    
    async def dispatch(self, request: Request, call_next: DispatchFunction) -> Response:
        # Validate origin if specified
        if self.allowed_origins != ["*"]:
            origin = request.headers.get("origin")
            if origin and origin not in self.allowed_origins:
                self.logger.warning(f"Blocked request from unauthorized origin: {origin}")
                return Response(
                    content=json.dumps({"error": "Unauthorized origin"}),
                    status_code=403,
                    media_type="application/json"
                )
        
        # Check authentication if required
        if self.require_auth and not self._is_authenticated(request):
            self.logger.warning(f"Unauthorized request to {request.url.path}")
            return Response(
                content=json.dumps({"error": "Authentication required"}),
                status_code=401,
                media_type="application/json"
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add CORS headers if needed
        if self.allowed_origins:
            origin = request.headers.get("origin")
            if origin in self.allowed_origins or "*" in self.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin or "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key"
        
        return response
    
    def _is_authenticated(self, request: Request) -> bool:
        """Simple authentication check."""
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # In a real implementation, validate against a database or service
            return True
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, validate the token
            return True
        
        # For health checks and public endpoints, allow without auth
        public_paths = ["/health", "/docs", "/openapi.json", "/metrics"]
        return request.url.path in public_paths
    
# Rate Limiting Middleware (Basic Implementation)
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, list] = {}
        self.logger = logging.getLogger("middleware.ratelimit")
    
    async def dispatch(self, request: Request, call_next: DispatchFunction) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Initialize client tracking
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        # Clean old requests (older than 1 minute)
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for client {client_ip}")
            return Response(
                content=json.dumps({
                    "error": "Rate limit exceeded",
                    "retry_after": 60
                }),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.client_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.client_requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response

# Exception Handling Middleware
class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized exception handling."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("middleware.exception")
    
    async def dispatch(self, request: Request, call_next: DispatchFunction) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return Response(
                content=json.dumps({
                    "error": "Validation error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }),
                status_code=400,
                media_type="application/json"
            )
            
        except PermissionError as e:
            self.logger.error(f"Permission error: {str(e)}")
            return Response(
                content=json.dumps({
                    "error": "Permission denied",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }),
                status_code=403,
                media_type="application/json"
            )
            
        except Exception as e:
            self.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return Response(
                content=json.dumps({
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }),
                status_code=500,
                media_type="application/json"
            )
