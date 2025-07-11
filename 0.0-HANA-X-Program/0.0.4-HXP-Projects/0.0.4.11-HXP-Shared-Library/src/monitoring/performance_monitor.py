"""
Performance monitoring utilities for HANA-X infrastructure.

This module provides common performance monitoring and metrics collection
utilities that can be reused across Enterprise and LoB server projects.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from threading import Lock
from collections import defaultdict, deque
import json
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics data."""
    requests_count: int = 0
    total_latency_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    
    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.requests_count == 0:
            return 0.0
        return self.total_latency_ms / self.requests_count
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.requests_count == 0:
            return 0.0
        return (self.success_count / self.requests_count) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.requests_count == 0:
            return 0.0
        return (self.error_count / self.requests_count) * 100
    
    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second."""
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            return 0.0
        return self.requests_count / elapsed_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'requests_count': self.requests_count,
            'total_latency_ms': self.total_latency_ms,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'min_latency_ms': self.min_latency_ms if self.min_latency_ms != float('inf') else 0.0,
            'max_latency_ms': self.max_latency_ms,
            'average_latency_ms': self.average_latency_ms,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate,
            'requests_per_second': self.requests_per_second,
            'start_time': self.start_time,
            'last_update': self.last_update
        }


class PerformanceMonitor:
    """
    Performance monitoring system for HANA-X infrastructure.
    
    Provides thread-safe performance metrics collection and analysis.
    """
    
    def __init__(self, 
                 server_id: str,
                 history_size: int = 1000,
                 metrics_file: Optional[Path] = None):
        """
        Initialize performance monitor.
        
        Args:
            server_id: Unique identifier for the server
            history_size: Number of recent metrics to keep in memory
            metrics_file: Optional file path to persist metrics
        """
        self.server_id = server_id
        self.history_size = history_size
        self.metrics_file = metrics_file
        
        # Thread-safe metrics storage
        self._lock = Lock()
        self._metrics = PerformanceMetrics()
        self._latency_history = deque(maxlen=history_size)
        self._metrics_by_endpoint = defaultdict(lambda: PerformanceMetrics())
        
        # Custom metrics and thresholds
        self._custom_metrics: Dict[str, Any] = {}
        self._thresholds: Dict[str, float] = {}
        self._alerts: List[Dict[str, Any]] = []
        
        logger.info(f"Performance monitor initialized for server: {server_id}")
    
    def record_request(self, 
                      latency_ms: float,
                      success: bool = True,
                      endpoint: Optional[str] = None,
                      additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a request's performance metrics.
        
        Args:
            latency_ms: Request latency in milliseconds
            success: Whether the request was successful
            endpoint: Optional endpoint identifier
            additional_metrics: Optional additional metrics to record
        """
        with self._lock:
            # Update global metrics
            self._metrics.requests_count += 1
            self._metrics.total_latency_ms += latency_ms
            self._metrics.last_update = time.time()
            
            if success:
                self._metrics.success_count += 1
            else:
                self._metrics.error_count += 1
            
            # Update latency bounds
            if latency_ms < self._metrics.min_latency_ms:
                self._metrics.min_latency_ms = latency_ms
            if latency_ms > self._metrics.max_latency_ms:
                self._metrics.max_latency_ms = latency_ms
            
            # Store latency history
            self._latency_history.append({
                'timestamp': time.time(),
                'latency_ms': latency_ms,
                'success': success,
                'endpoint': endpoint
            })
            
            # Update endpoint-specific metrics
            if endpoint:
                endpoint_metrics = self._metrics_by_endpoint[endpoint]
                endpoint_metrics.requests_count += 1
                endpoint_metrics.total_latency_ms += latency_ms
                endpoint_metrics.last_update = time.time()
                
                if success:
                    endpoint_metrics.success_count += 1
                else:
                    endpoint_metrics.error_count += 1
                
                if latency_ms < endpoint_metrics.min_latency_ms:
                    endpoint_metrics.min_latency_ms = latency_ms
                if latency_ms > endpoint_metrics.max_latency_ms:
                    endpoint_metrics.max_latency_ms = latency_ms
            
            # Record custom metrics
            if additional_metrics:
                for key, value in additional_metrics.items():
                    self._custom_metrics[key] = value
            
            # Check thresholds and generate alerts
            self._check_thresholds()
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Args:
            endpoint: Optional endpoint to get metrics for
            
        Returns:
            Dictionary containing performance metrics
        """
        with self._lock:
            if endpoint and endpoint in self._metrics_by_endpoint:
                base_metrics = self._metrics_by_endpoint[endpoint].to_dict()
            else:
                base_metrics = self._metrics.to_dict()
            
            # Add percentile calculations
            percentiles = self._calculate_percentiles()
            base_metrics.update(percentiles)
            
            # Add custom metrics
            base_metrics['custom_metrics'] = self._custom_metrics.copy()
            
            # Add server information
            base_metrics['server_id'] = self.server_id
            base_metrics['monitoring_started'] = self._metrics.start_time
            
            return base_metrics
    
    def get_historical_metrics(self, 
                             duration_seconds: Optional[int] = None,
                             endpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get historical performance metrics.
        
        Args:
            duration_seconds: Optional duration to filter metrics
            endpoint: Optional endpoint to filter by
            
        Returns:
            List of historical metrics
        """
        with self._lock:
            cutoff_time = time.time() - duration_seconds if duration_seconds else 0
            
            filtered_history = []
            for metric in self._latency_history:
                if metric['timestamp'] >= cutoff_time:
                    if endpoint is None or metric['endpoint'] == endpoint:
                        filtered_history.append(metric)
            
            return filtered_history
    
    def set_threshold(self, metric_name: str, threshold_value: float) -> None:
        """
        Set a threshold for automatic alerting.
        
        Args:
            metric_name: Name of the metric to monitor
            threshold_value: Threshold value for alerting
        """
        with self._lock:
            self._thresholds[metric_name] = threshold_value
            logger.info(f"Set threshold for {metric_name}: {threshold_value}")
    
    def get_alerts(self, clear_after_read: bool = True) -> List[Dict[str, Any]]:
        """
        Get current alerts.
        
        Args:
            clear_after_read: Whether to clear alerts after reading
            
        Returns:
            List of current alerts
        """
        with self._lock:
            alerts = self._alerts.copy()
            if clear_after_read:
                self._alerts.clear()
            return alerts
    
    def reset_metrics(self) -> None:
        """Reset all metrics to initial state."""
        with self._lock:
            self._metrics = PerformanceMetrics()
            self._latency_history.clear()
            self._metrics_by_endpoint.clear()
            self._custom_metrics.clear()
            self._alerts.clear()
            logger.info("Performance metrics reset")
    
    def export_metrics(self, file_path: Optional[Path] = None) -> Path:
        """
        Export metrics to JSON file.
        
        Args:
            file_path: Optional file path to export to
            
        Returns:
            Path to exported file
        """
        export_path = file_path or self.metrics_file
        if not export_path:
            export_path = Path(f"metrics_{self.server_id}_{int(time.time())}.json")
        
        with self._lock:
            export_data = {
                'server_id': self.server_id,
                'export_timestamp': time.time(),
                'global_metrics': self._metrics.to_dict(),
                'endpoint_metrics': {
                    endpoint: metrics.to_dict() 
                    for endpoint, metrics in self._metrics_by_endpoint.items()
                },
                'custom_metrics': self._custom_metrics.copy(),
                'recent_history': list(self._latency_history),
                'alerts': self._alerts.copy()
            }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {export_path}")
        return export_path
    
    def import_metrics(self, file_path: Path) -> None:
        """
        Import metrics from JSON file.
        
        Args:
            file_path: Path to metrics file to import
        """
        with open(file_path, 'r') as f:
            import_data = json.load(f)
        
        with self._lock:
            # Import global metrics
            global_data = import_data['global_metrics']
            self._metrics.requests_count = global_data['requests_count']
            self._metrics.total_latency_ms = global_data['total_latency_ms']
            self._metrics.error_count = global_data['error_count']
            self._metrics.success_count = global_data['success_count']
            self._metrics.min_latency_ms = global_data['min_latency_ms']
            self._metrics.max_latency_ms = global_data['max_latency_ms']
            self._metrics.start_time = global_data['start_time']
            self._metrics.last_update = global_data['last_update']
            
            # Import endpoint metrics
            for endpoint, metrics_data in import_data['endpoint_metrics'].items():
                endpoint_metrics = PerformanceMetrics()
                endpoint_metrics.requests_count = metrics_data['requests_count']
                endpoint_metrics.total_latency_ms = metrics_data['total_latency_ms']
                endpoint_metrics.error_count = metrics_data['error_count']
                endpoint_metrics.success_count = metrics_data['success_count']
                endpoint_metrics.min_latency_ms = metrics_data['min_latency_ms']
                endpoint_metrics.max_latency_ms = metrics_data['max_latency_ms']
                endpoint_metrics.start_time = metrics_data['start_time']
                endpoint_metrics.last_update = metrics_data['last_update']
                self._metrics_by_endpoint[endpoint] = endpoint_metrics
            
            # Import custom metrics
            self._custom_metrics.update(import_data['custom_metrics'])
            
            # Import history
            self._latency_history.clear()
            for history_item in import_data['recent_history']:
                self._latency_history.append(history_item)
            
            # Import alerts
            self._alerts.extend(import_data['alerts'])
        
        logger.info(f"Metrics imported from {file_path}")
    
    def _calculate_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles."""
        if not self._latency_history:
            return {
                'p50_latency_ms': 0.0,
                'p90_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'p99_latency_ms': 0.0
            }
        
        latencies = sorted([entry['latency_ms'] for entry in self._latency_history])
        length = len(latencies)
        
        def percentile(p: float) -> float:
            index = int(p * length)
            if index >= length:
                index = length - 1
            return latencies[index]
        
        return {
            'p50_latency_ms': percentile(0.5),
            'p90_latency_ms': percentile(0.9),
            'p95_latency_ms': percentile(0.95),
            'p99_latency_ms': percentile(0.99)
        }
    
    def _check_thresholds(self) -> None:
        """Check thresholds and generate alerts."""
        current_metrics = self._metrics.to_dict()
        
        for metric_name, threshold in self._thresholds.items():
            if metric_name in current_metrics:
                current_value = current_metrics[metric_name]
                
                # Check if threshold is exceeded
                if self._is_threshold_exceeded(metric_name, current_value, threshold):
                    alert = {
                        'timestamp': time.time(),
                        'server_id': self.server_id,
                        'metric_name': metric_name,
                        'current_value': current_value,
                        'threshold': threshold,
                        'severity': self._get_alert_severity(metric_name, current_value, threshold)
                    }
                    
                    self._alerts.append(alert)
                    logger.warning(f"Threshold exceeded for {metric_name}: {current_value} > {threshold}")
    
    def _is_threshold_exceeded(self, metric_name: str, current_value: float, threshold: float) -> bool:
        """Check if a threshold is exceeded based on metric type."""
        # For error rates and latency, exceeding threshold is bad
        if metric_name in ['error_rate', 'average_latency_ms', 'max_latency_ms', 'p95_latency_ms', 'p99_latency_ms']:
            return current_value > threshold
        
        # For success rate and RPS, falling below threshold is bad
        if metric_name in ['success_rate', 'requests_per_second']:
            return current_value < threshold
        
        # Default: exceeding threshold is bad
        return current_value > threshold
    
    def _get_alert_severity(self, metric_name: str, current_value: float, threshold: float) -> str:
        """Determine alert severity based on how much threshold is exceeded."""
        if metric_name in ['error_rate', 'average_latency_ms']:
            ratio = current_value / threshold
            if ratio > 2.0:
                return 'critical'
            elif ratio > 1.5:
                return 'high'
            else:
                return 'medium'
        
        return 'medium'


class MetricsCollector:
    """
    Utility class for collecting and aggregating metrics from multiple monitors.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.monitors: Dict[str, PerformanceMonitor] = {}
        self._lock = Lock()
    
    def add_monitor(self, monitor: PerformanceMonitor) -> None:
        """
        Add a performance monitor to the collector.
        
        Args:
            monitor: PerformanceMonitor instance to add
        """
        with self._lock:
            self.monitors[monitor.server_id] = monitor
            logger.info(f"Added monitor for server: {monitor.server_id}")
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all monitors.
        
        Returns:
            Dictionary containing aggregated metrics
        """
        with self._lock:
            aggregated = {
                'total_requests': 0,
                'total_errors': 0,
                'servers': {},
                'combined_metrics': {}
            }
            
            for server_id, monitor in self.monitors.items():
                server_metrics = monitor.get_metrics()
                aggregated['servers'][server_id] = server_metrics
                
                # Aggregate totals
                aggregated['total_requests'] += server_metrics['requests_count']
                aggregated['total_errors'] += server_metrics['error_count']
            
            # Calculate combined metrics
            if aggregated['total_requests'] > 0:
                aggregated['combined_metrics']['overall_success_rate'] = (
                    (aggregated['total_requests'] - aggregated['total_errors']) 
                    / aggregated['total_requests'] * 100
                )
                aggregated['combined_metrics']['overall_error_rate'] = (
                    aggregated['total_errors'] / aggregated['total_requests'] * 100
                )
            
            return aggregated
    
    def get_all_alerts(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get alerts from all monitors.
        
        Returns:
            Dictionary mapping server IDs to their alerts
        """
        with self._lock:
            all_alerts = {}
            for server_id, monitor in self.monitors.items():
                alerts = monitor.get_alerts(clear_after_read=False)
                if alerts:
                    all_alerts[server_id] = alerts
            return all_alerts
