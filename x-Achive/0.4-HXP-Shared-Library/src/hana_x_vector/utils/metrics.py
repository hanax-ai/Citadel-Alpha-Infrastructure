"""
Metrics Collection Module

Performance monitoring and metrics collection following HXP Governance Coding Standards.
Implements Single Responsibility Principle for metrics management.

Author: Citadel AI Team
License: MIT
"""

import time
import functools
from typing import Dict, Any, Optional, Callable
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import logging
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Centralized metrics collection (Single Responsibility Principle).
    
    Collects and exposes performance metrics for monitoring and alerting.
    """
    
    def __init__(self, port: int = 9090):
        """
        Initialize metrics collector.
        
        Args:
            port: Port for metrics HTTP server
        """
        self.port = port
        self._server_started = False
        self._lock = Lock()
        
        # Initialize Prometheus metrics
        self._init_metrics()
        
        logger.info(f"MetricsCollector initialized on port {port}")
    
    def _init_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        # Request metrics
        self.request_count = Counter(
            'hxp_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'hxp_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Vector operation metrics
        self.vector_operations = Counter(
            'hxp_vector_operations_total',
            'Total number of vector operations',
            ['operation', 'collection', 'status']
        )
        
        self.vector_operation_duration = Histogram(
            'hxp_vector_operation_duration_seconds',
            'Vector operation duration in seconds',
            ['operation', 'collection']
        )
        
        # Embedding metrics
        self.embedding_requests = Counter(
            'hxp_embedding_requests_total',
            'Total number of embedding requests',
            ['model', 'status']
        )
        
        self.embedding_duration = Histogram(
            'hxp_embedding_duration_seconds',
            'Embedding generation duration in seconds',
            ['model']
        )
        
        # External model metrics
        self.external_model_calls = Counter(
            'hxp_external_model_calls_total',
            'Total number of external model calls',
            ['model_id', 'operation', 'status']
        )
        
        self.external_model_duration = Histogram(
            'hxp_external_model_duration_seconds',
            'External model call duration in seconds',
            ['model_id', 'operation']
        )
        
        # Cache metrics
        self.cache_operations = Counter(
            'hxp_cache_operations_total',
            'Total number of cache operations',
            ['operation', 'status']
        )
        
        self.cache_hit_rate = Gauge(
            'hxp_cache_hit_rate',
            'Cache hit rate percentage'
        )
        
        # System metrics
        self.active_connections = Gauge(
            'hxp_active_connections',
            'Number of active connections'
        )
        
        self.memory_usage = Gauge(
            'hxp_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'hxp_cpu_usage_percent',
            'CPU usage percentage'
        )
        
        # Database metrics
        self.database_connections = Gauge(
            'hxp_database_connections',
            'Number of database connections'
        )
        
        self.vector_count = Gauge(
            'hxp_vector_count_total',
            'Total number of vectors',
            ['collection']
        )
    
    def start_metrics_server(self) -> None:
        """Start Prometheus metrics HTTP server."""
        with self._lock:
            if not self._server_started:
                try:
                    start_http_server(self.port)
                    self._server_started = True
                    logger.info(f"Metrics server started on port {self.port}")
                except Exception as e:
                    logger.error(f"Failed to start metrics server: {e}")
                    raise
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Record HTTP request metrics."""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_vector_operation(self, operation: str, collection: str, 
                              status: str, duration: float) -> None:
        """Record vector operation metrics."""
        self.vector_operations.labels(
            operation=operation, 
            collection=collection, 
            status=status
        ).inc()
        self.vector_operation_duration.labels(
            operation=operation, 
            collection=collection
        ).observe(duration)
    
    def record_embedding_request(self, model: str, status: str, duration: float) -> None:
        """Record embedding request metrics."""
        self.embedding_requests.labels(model=model, status=status).inc()
        self.embedding_duration.labels(model=model).observe(duration)
    
    def record_external_model_call(self, model_id: str, operation: str, 
                                 status: str, duration: float) -> None:
        """Record external model call metrics."""
        self.external_model_calls.labels(
            model_id=model_id, 
            operation=operation, 
            status=status
        ).inc()
        self.external_model_duration.labels(
            model_id=model_id, 
            operation=operation
        ).observe(duration)
    
    def record_cache_operation(self, operation: str, status: str) -> None:
        """Record cache operation metrics."""
        self.cache_operations.labels(operation=operation, status=status).inc()
    
    def update_cache_hit_rate(self, hit_rate: float) -> None:
        """Update cache hit rate."""
        self.cache_hit_rate.set(hit_rate)
    
    def update_system_metrics(self, active_connections: int, memory_usage: int, 
                            cpu_usage: float) -> None:
        """Update system metrics."""
        self.active_connections.set(active_connections)
        self.memory_usage.set(memory_usage)
        self.cpu_usage.set(cpu_usage)
    
    def update_database_metrics(self, connections: int) -> None:
        """Update database metrics."""
        self.database_connections.set(connections)
    
    def update_vector_count(self, collection: str, count: int) -> None:
        """Update vector count for collection."""
        self.vector_count.labels(collection=collection).set(count)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector


def monitor_performance(operation_name: str, collection: Optional[str] = None):
    """
    Decorator for monitoring function performance.
    
    Args:
        operation_name: Name of the operation being monitored
        collection: Optional collection name for vector operations
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Operation {operation_name} failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                
                if collection:
                    metrics.record_vector_operation(
                        operation_name, collection, status, duration
                    )
                else:
                    # Record as general operation
                    metrics.request_duration.labels(
                        method="internal", 
                        endpoint=operation_name
                    ).observe(duration)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Operation {operation_name} failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                
                if collection:
                    metrics.record_vector_operation(
                        operation_name, collection, status, duration
                    )
                else:
                    # Record as general operation
                    metrics.request_duration.labels(
                        method="internal", 
                        endpoint=operation_name
                    ).observe(duration)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceTracker:
    """
    Performance tracking utility (Single Responsibility Principle).
    
    Tracks performance metrics for specific operations and provides
    statistical analysis.
    """
    
    def __init__(self):
        """Initialize performance tracker."""
        self._metrics: Dict[str, list] = {}
        self._lock = Lock()
    
    def record_timing(self, operation: str, duration_ms: float) -> None:
        """Record timing for an operation."""
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = []
            self._metrics[operation].append(duration_ms)
    
    def get_statistics(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        with self._lock:
            if operation not in self._metrics or not self._metrics[operation]:
                return {}
            
            timings = self._metrics[operation]
            return {
                "count": len(timings),
                "min": min(timings),
                "max": max(timings),
                "avg": sum(timings) / len(timings),
                "p50": self._percentile(timings, 50),
                "p95": self._percentile(timings, 95),
                "p99": self._percentile(timings, 99)
            }
    
    def _percentile(self, data: list, percentile: float) -> float:
        """Calculate percentile value."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def clear_metrics(self, operation: Optional[str] = None) -> None:
        """Clear metrics for operation or all operations."""
        with self._lock:
            if operation:
                self._metrics.pop(operation, None)
            else:
                self._metrics.clear()
    
    def get_all_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op: self.get_statistics(op) for op in self._metrics.keys()}


# Global performance tracker instance
_performance_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance."""
    global _performance_tracker
    
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    
    return _performance_tracker


def track_performance(operation: str):
    """
    Context manager for tracking operation performance.
    
    Args:
        operation: Name of the operation to track
    """
    class PerformanceContext:
        def __init__(self, op_name: str):
            self.operation = op_name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration_ms = (time.time() - self.start_time) * 1000
                tracker = get_performance_tracker()
                tracker.record_timing(self.operation, duration_ms)
    
    return PerformanceContext(operation)
