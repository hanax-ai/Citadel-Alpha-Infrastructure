"""
API Gateway Middleware
=====================

Middleware components for authentication, validation, and caching
in the unified API gateway.
"""

from typing import Dict, Any, Optional, Callable
import time
import json
import hashlib
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as redis
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import AuthenticationError, ValidationError
from ..utils.validators import validate_api_key, validate_request_data


class AuthenticationMiddleware:
    """Authentication middleware for API requests."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security = HTTPBearer()
        self.metrics = MetricsCollector()
        
        # R&D environment settings
        self.require_auth = config.get("auth", {}).get("enabled", False)
        self.api_keys = config.get("auth", {}).get("api_keys", [])
        self.ip_allowlist = config.get("auth", {}).get("ip_allowlist", [])
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process authentication for incoming requests."""
        try:
            # Check IP allowlist for R&D environment
            if self.ip_allowlist:
                client_ip = request.client.host
                if client_ip not in self.ip_allowlist:
                    self.metrics.increment_counter("auth_ip_blocked")
                    raise HTTPException(
                        status_code=403,
                        detail="IP address not allowed"
                    )
            
            # Skip auth for health and metrics endpoints
            if request.url.path in ["/health", "/metrics"]:
                return await call_next(request)
            
            # API key authentication (if enabled)
            if self.require_auth:
                credentials = await self.security(request)
                if not self._validate_api_key(credentials.credentials):
                    self.metrics.increment_counter("auth_failures")
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid API key"
                    )
            
            self.metrics.increment_counter("auth_success")
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            self.metrics.increment_counter("auth_errors")
            raise HTTPException(
                status_code=500,
                detail=f"Authentication error: {str(e)}"
            )
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key against configured keys."""
        return api_key in self.api_keys


class ValidationMiddleware:
    """Request validation middleware."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Validation settings
        self.max_request_size = config.get("validation", {}).get("max_request_size", 10 * 1024 * 1024)  # 10MB
        self.max_vector_dimensions = config.get("validation", {}).get("max_vector_dimensions", 4096)
        self.max_batch_size = config.get("validation", {}).get("max_batch_size", 10000)
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process validation for incoming requests."""
        try:
            # Check request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                self.metrics.increment_counter("validation_size_exceeded")
                raise HTTPException(
                    status_code=413,
                    detail="Request too large"
                )
            
            # Skip validation for GET requests and health endpoints
            if request.method == "GET" or request.url.path in ["/health", "/metrics"]:
                return await call_next(request)
            
            # Validate request data for vector operations
            if request.url.path.startswith("/api/v1/vectors"):
                await self._validate_vector_request(request)
            
            self.metrics.increment_counter("validation_success")
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            self.metrics.increment_counter("validation_errors")
            raise HTTPException(
                status_code=400,
                detail=f"Validation error: {str(e)}"
            )
    
    async def _validate_vector_request(self, request: Request):
        """Validate vector operation requests."""
        try:
            # Read request body
            body = await request.body()
            if not body:
                return
            
            data = json.loads(body)
            
            # Validate vector operations
            if "vectors" in data:
                vectors = data["vectors"]
                if len(vectors) > self.max_batch_size:
                    raise ValidationError(f"Batch size exceeds maximum: {self.max_batch_size}")
                
                for vector_data in vectors:
                    if "vector" in vector_data:
                        vector = vector_data["vector"]
                        if len(vector) > self.max_vector_dimensions:
                            raise ValidationError(f"Vector dimensions exceed maximum: {self.max_vector_dimensions}")
            
            # Validate search requests
            if "query_vector" in data:
                query_vector = data["query_vector"]
                if len(query_vector) > self.max_vector_dimensions:
                    raise ValidationError(f"Query vector dimensions exceed maximum: {self.max_vector_dimensions}")
            
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON in request body")


class CachingMiddleware:
    """Response caching middleware using Redis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Cache settings
        self.cache_enabled = config.get("cache", {}).get("enabled", True)
        self.cache_ttl = config.get("cache", {}).get("ttl", 300)  # 5 minutes
        self.cache_key_prefix = config.get("cache", {}).get("key_prefix", "hana_x_vector:")
        
        # Redis connection
        self.redis_client = None
    
    async def startup(self):
        """Initialize Redis connection."""
        if self.cache_enabled:
            redis_config = self.config.get("redis", {})
            self.redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                decode_responses=True
            )
    
    async def shutdown(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process caching for incoming requests."""
        if not self.cache_enabled or not self.redis_client:
            return await call_next(request)
        
        try:
            # Only cache GET requests and search operations
            if request.method != "GET" and not self._is_cacheable_operation(request):
                return await call_next(request)
            
            # Generate cache key
            cache_key = await self._generate_cache_key(request)
            
            # Try to get cached response
            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                self.metrics.increment_counter("cache_hits")
                response_data = json.loads(cached_response)
                return Response(
                    content=response_data["content"],
                    status_code=response_data["status_code"],
                    headers=response_data["headers"],
                    media_type=response_data["media_type"]
                )
            
            # Process request
            response = await call_next(request)
            
            # Cache successful responses
            if response.status_code == 200:
                await self._cache_response(cache_key, response)
                self.metrics.increment_counter("cache_misses")
            
            return response
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors")
            # Continue without caching on error
            return await call_next(request)
    
    def _is_cacheable_operation(self, request: Request) -> bool:
        """Check if the operation is cacheable."""
        cacheable_paths = [
            "/api/v1/vectors/search",
            "/api/v1/collections",
            "/graphql"  # For query operations
        ]
        return any(request.url.path.startswith(path) for path in cacheable_paths)
    
    async def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for the request."""
        # Include method, path, and query parameters
        key_data = {
            "method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query)
        }
        
        # Include request body for POST requests (search operations)
        if request.method == "POST":
            body = await request.body()
            if body:
                key_data["body"] = body.decode()
        
        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.cache_key_prefix}{key_hash}"
    
    async def _cache_response(self, cache_key: str, response: Response):
        """Cache the response."""
        try:
            # Read response content
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Prepare cache data
            cache_data = {
                "content": response_body.decode(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            
            # Store in cache
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
            
            # Recreate response with same content
            response.body_iterator = self._create_body_iterator(response_body)
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"Cache storage error: {e}")
    
    def _create_body_iterator(self, content: bytes):
        """Create a body iterator from content."""
        async def body_iterator():
            yield content
        return body_iterator()


class RateLimitingMiddleware:
    """Rate limiting middleware for API requests."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Rate limiting settings
        self.rate_limit_enabled = config.get("rate_limit", {}).get("enabled", False)
        self.requests_per_minute = config.get("rate_limit", {}).get("requests_per_minute", 1000)
        self.burst_limit = config.get("rate_limit", {}).get("burst_limit", 100)
        
        # Redis connection for rate limiting
        self.redis_client = None
    
    async def startup(self):
        """Initialize Redis connection for rate limiting."""
        if self.rate_limit_enabled:
            redis_config = self.config.get("redis", {})
            self.redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 1),  # Use different DB for rate limiting
                decode_responses=True
            )
    
    async def shutdown(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process rate limiting for incoming requests."""
        if not self.rate_limit_enabled or not self.redis_client:
            return await call_next(request)
        
        try:
            # Get client identifier (IP address)
            client_id = request.client.host
            
            # Check rate limit
            if await self._is_rate_limited(client_id):
                self.metrics.increment_counter("rate_limit_exceeded")
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
            
            # Process request
            response = await call_next(request)
            
            # Record request
            await self._record_request(client_id)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.metrics.increment_counter("rate_limit_errors")
            # Continue without rate limiting on error
            return await call_next(request)
    
    async def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        current_time = int(time.time())
        window_start = current_time - 60  # 1 minute window
        
        # Count requests in the current window
        key = f"rate_limit:{client_id}"
        request_count = await self.redis_client.zcount(key, window_start, current_time)
        
        return request_count >= self.requests_per_minute
    
    async def _record_request(self, client_id: str):
        """Record a request for rate limiting."""
        current_time = int(time.time())
        key = f"rate_limit:{client_id}"
        
        # Add current request
        await self.redis_client.zadd(key, {str(current_time): current_time})
        
        # Clean up old entries
        window_start = current_time - 60
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Set expiration
        await self.redis_client.expire(key, 60)
