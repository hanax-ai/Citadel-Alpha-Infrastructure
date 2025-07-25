import time
import logging
from typing import Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)

class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Prometheus metrics middleware for Citadel API Gateway.
    Collects detailed metrics for monitoring and alerting.
    """
    
    def __init__(self, app: ASGIApp, config: dict):
        super().__init__(app)
        
        # Handle case where config might be empty initially
        middleware_config = config.get('middleware', {}).get('metrics', {})
        self.metrics_enabled = middleware_config.get('enabled', True)
        self.collect_detailed_metrics = middleware_config.get('detailed', True)
        
        # Initialize Prometheus metrics
        self._init_metrics()
        
        # Set this instance as the global metrics middleware
        set_metrics_middleware(self)
        
        logger.info("PrometheusMetricsMiddleware initialized")
    
    def _init_metrics(self):
        """Initialize Prometheus metrics collectors."""
        
        # Request metrics
        self.request_count = Counter(
            'citadel_gateway_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = Histogram(
            'citadel_gateway_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'citadel_gateway_cache_hits_total',
            'Total number of cache hits',
            ['endpoint', 'cache_type']
        )
        
        self.cache_misses = Counter(
            'citadel_gateway_cache_misses_total',
            'Total number of cache misses',
            ['endpoint', 'cache_type']
        )
        
        self.cache_operations = Histogram(
            'citadel_gateway_cache_operation_duration_seconds',
            'Cache operation duration in seconds',
            ['operation', 'result'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
        )
        
        # LLM/Ollama backend metrics
        self.ollama_requests = Counter(
            'citadel_gateway_ollama_requests_total',
            'Total requests forwarded to Ollama',
            ['model', 'endpoint_type', 'status_code']
        )
        
        self.ollama_duration = Histogram(
            'citadel_gateway_ollama_request_duration_seconds',
            'Ollama request duration in seconds',
            ['model', 'endpoint_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
        )
        
        # System metrics
        self.active_connections = Gauge(
            'citadel_gateway_active_connections',
            'Number of active connections'
        )
        
        self.memory_usage = Gauge(
            'citadel_gateway_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        # Error metrics
        self.error_count = Counter(
            'citadel_gateway_errors_total',
            'Total number of errors',
            ['error_type', 'endpoint']
        )
        
        # Gateway info
        self.gateway_info = Info(
            'citadel_gateway_info',
            'Gateway information'
        )
        
        # Set gateway info
        self.gateway_info.info({
            'version': '1.0.0',
            'name': 'Citadel API Gateway',
            'features': 'caching,logging,metrics',
            'build_date': time.strftime('%Y-%m-%d')
        })
    
    async def dispatch(self, request: Request, call_next):
        if not self.metrics_enabled:
            return await call_next(request)
        
        # Track active connections
        self.active_connections.inc()
        
        start_time = time.time()
        method = request.method
        path = request.url.path
        endpoint = self._normalize_endpoint(path)
        
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            
            # Record request metrics
            duration = time.time() - start_time
            self.request_count.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            self.request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log detailed metrics if enabled
            if self.collect_detailed_metrics:
                logger.debug(f"Metrics: {method} {endpoint} - {status_code} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            # Record error metrics
            self.error_count.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            
            logger.error(f"Request error: {e}")
            raise
            
        finally:
            # Decrease active connections
            self.active_connections.dec()
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint paths for consistent metrics labeling."""
        
        # Map specific endpoints to normalized names
        endpoint_mapping = {
            '/health': 'health',
            '/api/tags': 'models',
            '/v1/chat/completions': 'chat_completions',
            '/v1/completions': 'completions',
            '/api/embeddings': 'embeddings',
            '/metrics': 'metrics'
        }
        
        # Check for exact matches first
        if path in endpoint_mapping:
            return endpoint_mapping[path]
        
        # Handle parameterized paths
        if path.startswith('/api/'):
            return 'api_other'
        elif path.startswith('/v1/'):
            return 'v1_other'
        else:
            return 'other'
    
    def record_cache_hit(self, endpoint: str, cache_type: str = 'redis'):
        """Record a cache hit event."""
        if self.metrics_enabled:
            self.cache_hits.labels(endpoint=endpoint, cache_type=cache_type).inc()
    
    def record_cache_miss(self, endpoint: str, cache_type: str = 'redis'):
        """Record a cache miss event."""
        if self.metrics_enabled:
            self.cache_misses.labels(endpoint=endpoint, cache_type=cache_type).inc()
    
    def record_cache_operation(self, operation: str, duration: float, result: str = 'success'):
        """Record cache operation timing."""
        if self.metrics_enabled:
            self.cache_operations.labels(operation=operation, result=result).observe(duration)
    
    def record_ollama_request(self, model: str, endpoint_type: str, duration: float, status_code: int):
        """Record Ollama backend request metrics."""
        if self.metrics_enabled:
            self.ollama_requests.labels(
                model=model,
                endpoint_type=endpoint_type,
                status_code=str(status_code)
            ).inc()
            
            self.ollama_duration.labels(
                model=model,
                endpoint_type=endpoint_type
            ).observe(duration)
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error occurrence."""
        if self.metrics_enabled:
            self.error_count.labels(error_type=error_type, endpoint=endpoint).inc()


# Global metrics instance for use across the application
_metrics_middleware = None

def get_metrics_middleware() -> 'PrometheusMetricsMiddleware':
    """Get the global metrics middleware instance."""
    return _metrics_middleware

def set_metrics_middleware(middleware: 'PrometheusMetricsMiddleware'):
    """Set the global metrics middleware instance."""
    global _metrics_middleware
    _metrics_middleware = middleware
