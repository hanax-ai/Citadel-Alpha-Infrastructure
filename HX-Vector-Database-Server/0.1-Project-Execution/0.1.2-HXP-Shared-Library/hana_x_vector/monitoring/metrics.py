"""
Metrics Collector
================

Prometheus metrics collection and export for vector database operations.
Provides comprehensive performance and operational metrics.
"""

from typing import Dict, Any, List, Optional
import time
from collections import defaultdict, Counter
from prometheus_client import Counter as PrometheusCounter, Histogram, Gauge, CollectorRegistry, generate_latest
import asyncio
import threading


class MetricsCollector:
    """
    Prometheus metrics collector for vector database operations.
    Provides comprehensive performance and operational metrics.
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._lock = threading.Lock()
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Internal metrics storage
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)
        self.gauges = defaultdict(float)
        
        # Collection settings
        self.collection_interval = 60  # seconds
        self.max_histogram_samples = 1000
        
        # Background collection task
        self.collection_task = None
        self.collecting = False
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Vector operation metrics
        self.vector_operations_total = PrometheusCounter(
            'vector_operations_total',
            'Total number of vector operations',
            ['operation', 'collection', 'status'],
            registry=self.registry
        )
        
        self.vector_operation_duration = Histogram(
            'vector_operation_duration_seconds',
            'Duration of vector operations',
            ['operation', 'collection'],
            registry=self.registry
        )
        
        self.vector_search_latency = Histogram(
            'vector_search_latency_seconds',
            'Vector search latency',
            ['collection'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # API Gateway metrics
        self.api_requests_total = PrometheusCounter(
            'api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code', 'protocol'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint', 'protocol'],
            registry=self.registry
        )
        
        # Qdrant metrics
        self.qdrant_operations_total = PrometheusCounter(
            'qdrant_operations_total',
            'Total number of Qdrant operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.qdrant_connection_pool_size = Gauge(
            'qdrant_connection_pool_size',
            'Qdrant connection pool size',
            ['status'],
            registry=self.registry
        )
        
        # External model metrics
        self.external_model_requests_total = PrometheusCounter(
            'external_model_requests_total',
            'Total number of external model requests',
            ['model', 'status'],
            registry=self.registry
        )
        
        self.external_model_latency = Histogram(
            'external_model_latency_seconds',
            'External model request latency',
            ['model'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations_total = PrometheusCounter(
            'cache_operations_total',
            'Total number of cache operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.cache_hit_ratio = Gauge(
            'cache_hit_ratio',
            'Cache hit ratio',
            ['cache_type'],
            registry=self.registry
        )
        
        # System metrics
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            ['service'],
            registry=self.registry
        )
        
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        # Performance metrics
        self.throughput_ops_per_second = Gauge(
            'throughput_ops_per_second',
            'Operations per second',
            ['operation_type'],
            registry=self.registry
        )
        
        self.error_rate = Gauge(
            'error_rate',
            'Error rate percentage',
            ['component'],
            registry=self.registry
        )
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Counter name
            value: Increment value
            tags: Optional tags
        """
        with self._lock:
            self.counters[name] += value
            
            # Update Prometheus metrics based on counter name
            if name.startswith('vector_'):
                self._update_vector_metrics(name, value, tags)
            elif name.startswith('api_'):
                self._update_api_metrics(name, value, tags)
            elif name.startswith('qdrant_'):
                self._update_qdrant_metrics(name, value, tags)
            elif name.startswith('external_model_'):
                self._update_external_model_metrics(name, value, tags)
            elif name.startswith('cache_'):
                self._update_cache_metrics(name, value, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a histogram value.
        
        Args:
            name: Histogram name
            value: Value to record
            tags: Optional tags
        """
        with self._lock:
            self.histograms[name].append(value)
            
            # Keep only recent samples
            if len(self.histograms[name]) > self.max_histogram_samples:
                self.histograms[name] = self.histograms[name][-self.max_histogram_samples:]
            
            # Update Prometheus histograms
            if name.endswith('_duration'):
                self._update_duration_metrics(name, value, tags)
            elif name.endswith('_latency'):
                self._update_latency_metrics(name, value, tags)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a gauge value.
        
        Args:
            name: Gauge name
            value: Value to record
            tags: Optional tags
        """
        with self._lock:
            self.gauges[name] = value
            
            # Update Prometheus gauges
            self._update_gauge_metrics(name, value, tags)
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        protocol: str = "http"
    ):
        """
        Record API request metrics.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            duration: Request duration
            protocol: Protocol used
        """
        # Update Prometheus metrics
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            protocol=protocol
        ).inc()
        
        self.api_request_duration.labels(
            method=method,
            endpoint=endpoint,
            protocol=protocol
        ).observe(duration)
        
        # Update internal metrics
        self.increment_counter(f"api_requests_{protocol}", tags={
            "method": method,
            "endpoint": endpoint,
            "status": str(status_code)
        })
        
        self.record_histogram(f"api_duration_{protocol}", duration, tags={
            "method": method,
            "endpoint": endpoint
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.
        
        Returns:
            Dict with metrics summary
        """
        with self._lock:
            # Calculate histogram statistics
            histogram_stats = {}
            for name, values in self.histograms.items():
                if values:
                    histogram_stats[name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "p50": self._percentile(values, 50),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99)
                    }
            
            return {
                "counters": dict(self.counters),
                "histograms": histogram_stats,
                "gauges": dict(self.gauges),
                "timestamp": time.time()
            }
    
    def get_prometheus_metrics(self) -> str:
        """
        Get Prometheus formatted metrics.
        
        Returns:
            Prometheus metrics string
        """
        return generate_latest(self.registry).decode('utf-8')
    
    def start_collection(self):
        """Start background metrics collection."""
        if not self.collecting:
            self.collecting = True
            self.collection_task = asyncio.create_task(self._collect_metrics())
    
    def stop_collection(self):
        """Stop background metrics collection."""
        self.collecting = False
        if self.collection_task:
            self.collection_task.cancel()
    
    async def _collect_metrics(self):
        """Background metrics collection task."""
        while self.collecting:
            try:
                # Update system metrics
                await self._update_system_metrics()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Sleep until next collection
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _update_system_metrics(self):
        """Update system-level metrics."""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage_bytes.labels(component="system").set(memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.record_gauge("cpu_usage_percent", cpu_percent)
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            print(f"Error updating system metrics: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics."""
        try:
            # Calculate throughput from recent counters
            current_time = time.time()
            
            # This is a simplified implementation
            # In production, you'd track rates over time windows
            for counter_name, count in self.counters.items():
                if "requests" in counter_name or "operations" in counter_name:
                    # Estimate ops per second (simplified)
                    ops_per_second = count / max(1, current_time - (current_time - 60))
                    self.throughput_ops_per_second.labels(
                        operation_type=counter_name
                    ).set(ops_per_second)
            
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def _update_vector_metrics(self, name: str, value: int, tags: Optional[Dict[str, str]]):
        """Update vector operation metrics."""
        if not tags:
            tags = {}
        
        operation = tags.get("operation", "unknown")
        collection = tags.get("collection", "unknown")
        status = tags.get("status", "success")
        
        self.vector_operations_total.labels(
            operation=operation,
            collection=collection,
            status=status
        ).inc(value)
    
    def _update_api_metrics(self, name: str, value: int, tags: Optional[Dict[str, str]]):
        """Update API metrics."""
        # Already handled in record_request method
        pass
    
    def _update_qdrant_metrics(self, name: str, value: int, tags: Optional[Dict[str, str]]):
        """Update Qdrant metrics."""
        if not tags:
            tags = {}
        
        operation = tags.get("operation", "unknown")
        status = tags.get("status", "success")
        
        self.qdrant_operations_total.labels(
            operation=operation,
            status=status
        ).inc(value)
    
    def _update_external_model_metrics(self, name: str, value: int, tags: Optional[Dict[str, str]]):
        """Update external model metrics."""
        if not tags:
            tags = {}
        
        model = tags.get("model", "unknown")
        status = tags.get("status", "success")
        
        self.external_model_requests_total.labels(
            model=model,
            status=status
        ).inc(value)
    
    def _update_cache_metrics(self, name: str, value: int, tags: Optional[Dict[str, str]]):
        """Update cache metrics."""
        if not tags:
            tags = {}
        
        operation = tags.get("operation", "unknown")
        status = tags.get("status", "success")
        
        self.cache_operations_total.labels(
            operation=operation,
            status=status
        ).inc(value)
    
    def _update_duration_metrics(self, name: str, value: float, tags: Optional[Dict[str, str]]):
        """Update duration metrics."""
        if not tags:
            tags = {}
        
        if "vector_operation" in name:
            operation = tags.get("operation", "unknown")
            collection = tags.get("collection", "unknown")
            
            self.vector_operation_duration.labels(
                operation=operation,
                collection=collection
            ).observe(value)
    
    def _update_latency_metrics(self, name: str, value: float, tags: Optional[Dict[str, str]]):
        """Update latency metrics."""
        if not tags:
            tags = {}
        
        if "search_latency" in name:
            collection = tags.get("collection", "unknown")
            self.vector_search_latency.labels(collection=collection).observe(value)
        elif "model_latency" in name:
            model = tags.get("model", "unknown")
            self.external_model_latency.labels(model=model).observe(value)
    
    def _update_gauge_metrics(self, name: str, value: float, tags: Optional[Dict[str, str]]):
        """Update gauge metrics."""
        if not tags:
            tags = {}
        
        if "connection" in name:
            service = tags.get("service", "unknown")
            self.active_connections.labels(service=service).set(value)
        elif "cache_hit_ratio" in name:
            cache_type = tags.get("cache_type", "unknown")
            self.cache_hit_ratio.labels(cache_type=cache_type).set(value)
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        index = min(index, len(sorted_values) - 1)
        
        return sorted_values[index]
    
    def reset_metrics(self):
        """Reset all metrics."""
        with self._lock:
            self.counters.clear()
            self.histograms.clear()
            self.gauges.clear()
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ("prometheus", "json")
            
        Returns:
            Formatted metrics string
        """
        if format == "prometheus":
            return self.get_prometheus_metrics()
        elif format == "json":
            import json
            return json.dumps(self.get_metrics_summary(), indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get health-related metrics.
        
        Returns:
            Health metrics
        """
        with self._lock:
            # Calculate error rates
            error_metrics = {}
            
            for name, count in self.counters.items():
                if "error" in name or "failed" in name:
                    base_name = name.replace("_errors", "").replace("_failed", "")
                    total_name = f"{base_name}_total"
                    
                    total_count = self.counters.get(total_name, count)
                    error_rate = (count / total_count * 100) if total_count > 0 else 0
                    
                    error_metrics[base_name] = {
                        "errors": count,
                        "total": total_count,
                        "error_rate": error_rate
                    }
            
            return {
                "error_metrics": error_metrics,
                "active_connections": {k: v for k, v in self.gauges.items() if "connection" in k},
                "cache_performance": {k: v for k, v in self.gauges.items() if "cache" in k},
                "timestamp": time.time()
            }
