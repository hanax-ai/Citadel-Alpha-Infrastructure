"""
Performance Monitor Utility

Utility class for monitoring application performance and metrics collection.
Provides request tracking, timing, and performance analytics.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

from app.common.base_classes import BaseService


class PerformanceMonitor(BaseService):
    """
    Performance monitoring utility
    
    Tracks request metrics, response times, and system performance
    indicators for monitoring and optimization purposes.
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            history_size: Number of recent metrics to keep in memory
        """
        super().__init__("PerformanceMonitor")
        self.history_size = history_size
        
        # Metrics storage
        self._request_times: deque = deque(maxlen=history_size)
        self._embedding_metrics: deque = deque(maxlen=history_size)
        self._workflow_metrics: deque = deque(maxlen=history_size)
        self._error_counts: defaultdict = defaultdict(int)
        
        # Counters
        self._total_requests = 0
        self._total_embeddings = 0
        self._total_workflows = 0
        
        # Start time for uptime calculation
        self._start_time = time.time()
    
    async def record_request(self, 
                           endpoint: str, 
                           method: str, 
                           duration: float, 
                           status_code: int,
                           **kwargs):
        """
        Record API request metrics
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            duration: Request duration in seconds
            status_code: HTTP status code
            **kwargs: Additional metadata
        """
        metric = {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            **kwargs
        }
        
        self._request_times.append(metric)
        self._total_requests += 1
        
        # Track errors
        if status_code >= 400:
            self._error_counts[f"{method}_{endpoint}_{status_code}"] += 1
    
    async def record_embedding_request(self,
                                     texts_count: int,
                                     model: str,
                                     processing_time: float,
                                     cache_hits: int = 0,
                                     **kwargs):
        """
        Record embedding request metrics
        
        Args:
            texts_count: Number of texts processed
            model: Model used for embeddings
            processing_time: Total processing time
            cache_hits: Number of cache hits
            **kwargs: Additional metadata
        """
        metric = {
            'timestamp': datetime.utcnow(),
            'texts_count': texts_count,
            'model': model,
            'processing_time': processing_time,
            'cache_hits': cache_hits,
            'cache_ratio': cache_hits / texts_count if texts_count > 0 else 0,
            'throughput': texts_count / processing_time if processing_time > 0 else 0,
            **kwargs
        }
        
        self._embedding_metrics.append(metric)
        self._total_embeddings += texts_count
    
    async def record_workflow_execution(self,
                                      workflow_id: str,
                                      execution_time: float,
                                      status: str,
                                      task_count: int = 0,
                                      **kwargs):
        """
        Record workflow execution metrics
        
        Args:
            workflow_id: Workflow identifier
            execution_time: Total execution time
            status: Execution status
            task_count: Number of tasks in workflow
            **kwargs: Additional metadata
        """
        metric = {
            'timestamp': datetime.utcnow(),
            'workflow_id': workflow_id,
            'execution_time': execution_time,
            'status': status,
            'task_count': task_count,
            **kwargs
        }
        
        self._workflow_metrics.append(metric)
        self._total_workflows += 1
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics summary
        
        Returns:
            Dict[str, Any]: Current metrics and statistics
        """
        now = datetime.utcnow()
        uptime = time.time() - self._start_time
        
        # Calculate request statistics
        recent_requests = [
            r for r in self._request_times 
            if (now - r['timestamp']).total_seconds() <= 300  # Last 5 minutes
        ]
        
        request_stats = {}
        if recent_requests:
            durations = [r['duration'] for r in recent_requests]
            request_stats = {
                'count': len(recent_requests),
                'avg_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'p95_duration': self._percentile(durations, 95),
                'error_rate': len([r for r in recent_requests if r['status_code'] >= 400]) / len(recent_requests)
            }
        
        # Calculate embedding statistics
        recent_embeddings = [
            e for e in self._embedding_metrics 
            if (now - e['timestamp']).total_seconds() <= 300
        ]
        
        embedding_stats = {}
        if recent_embeddings:
            throughputs = [e['throughput'] for e in recent_embeddings]
            cache_ratios = [e['cache_ratio'] for e in recent_embeddings]
            embedding_stats = {
                'count': len(recent_embeddings),
                'total_texts': sum(e['texts_count'] for e in recent_embeddings),
                'avg_throughput': statistics.mean(throughputs),
                'avg_cache_ratio': statistics.mean(cache_ratios),
                'models_used': list(set(e['model'] for e in recent_embeddings))
            }
        
        # Calculate workflow statistics
        recent_workflows = [
            w for w in self._workflow_metrics 
            if (now - w['timestamp']).total_seconds() <= 300
        ]
        
        workflow_stats = {}
        if recent_workflows:
            execution_times = [w['execution_time'] for w in recent_workflows]
            workflow_stats = {
                'count': len(recent_workflows),
                'avg_execution_time': statistics.mean(execution_times),
                'success_rate': len([w for w in recent_workflows if w['status'] == 'completed']) / len(recent_workflows),
                'active_workflows': list(set(w['workflow_id'] for w in recent_workflows))
            }
        
        return {
            'timestamp': now,
            'uptime': uptime,
            'totals': {
                'requests': self._total_requests,
                'embeddings': self._total_embeddings,
                'workflows': self._total_workflows
            },
            'recent': {
                'requests': request_stats,
                'embeddings': embedding_stats,
                'workflows': workflow_stats
            },
            'errors': dict(self._error_counts),
            'memory_usage': {
                'request_metrics': len(self._request_times),
                'embedding_metrics': len(self._embedding_metrics),
                'workflow_metrics': len(self._workflow_metrics)
            }
        }
    
    async def get_health_score(self) -> float:
        """
        Calculate overall system health score (0.0 to 1.0)
        
        Returns:
            float: Health score based on recent performance
        """
        metrics = await self.get_current_metrics()
        
        # Start with perfect score
        score = 1.0
        
        # Reduce score based on error rate
        if 'requests' in metrics['recent'] and metrics['recent']['requests']:
            error_rate = metrics['recent']['requests'].get('error_rate', 0)
            score *= (1.0 - error_rate)
        
        # Reduce score based on slow responses
        if 'requests' in metrics['recent'] and metrics['recent']['requests']:
            avg_duration = metrics['recent']['requests'].get('avg_duration', 0)
            if avg_duration > 5.0:  # More than 5 seconds is concerning
                score *= 0.5
            elif avg_duration > 2.0:  # More than 2 seconds is degraded
                score *= 0.8
        
        # Reduce score based on workflow failures
        if 'workflows' in metrics['recent'] and metrics['recent']['workflows']:
            success_rate = metrics['recent']['workflows'].get('success_rate', 1.0)
            score *= success_rate
        
        return max(0.0, min(1.0, score))  # Ensure 0.0 <= score <= 1.0
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self._request_times.clear()
        self._embedding_metrics.clear()
        self._workflow_metrics.clear()
        self._error_counts.clear()
        self._total_requests = 0
        self._total_embeddings = 0
        self._total_workflows = 0
        self._start_time = time.time()
        
        self.logger.info("Performance metrics reset")
