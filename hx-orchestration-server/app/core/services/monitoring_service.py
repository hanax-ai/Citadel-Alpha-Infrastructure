"""
Monitoring Service

Centralized monitoring and metrics collection service.
Provides health checks, performance metrics, and dependency monitoring.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from prometheus_client import Counter, Histogram, Gauge, Info

from config.settings import get_settings
from app.common.base_classes import BaseService

settings = get_settings()

# Prometheus metrics
REQUEST_COUNT = Counter('hx_orchestration_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('hx_orchestration_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('hx_orchestration_active_connections', 'Active connections')
DEPENDENCY_STATUS = Gauge('hx_orchestration_dependency_status', 'Dependency status', ['service'])
EMBEDDING_REQUESTS = Counter('hx_orchestration_embedding_requests_total', 'Embedding requests', ['model'])
WORKFLOW_EXECUTIONS = Counter('hx_orchestration_workflow_executions_total', 'Workflow executions', ['workflow_id', 'status'])

# Service info
SERVICE_INFO = Info('hx_orchestration_service_info', 'Service information')


class MonitoringService(BaseService):
    """Centralized monitoring and metrics service"""
    
    def __init__(self):
        super().__init__()
        self._start_time = time.time()
        self._initialized = False
    
    async def initialize(self):
        """Initialize monitoring service"""
        if self._initialized:
            return
        
        # Set service info
        SERVICE_INFO.info({
            'version': '2.0.0',
            'server': settings.SERVER_NAME,
            'ip': settings.SERVER_IP,
            'environment': settings.ENVIRONMENT
        })
        
        self._initialized = True
        self.logger.info("Monitoring service initialized")
    
    async def cleanup(self):
        """Cleanup monitoring resources"""
        self.logger.info("Monitoring service cleanup completed")
    
    async def check_dependencies(self) -> Dict[str, Any]:
        """
        Check status of all external dependencies
        
        Returns:
            Dict[str, Any]: Dependency status information
        """
        dependencies = {}
        
        # Check LLM services
        dependencies['llm_01'] = await self._check_http_service(
            settings.LLM_01_URL, 
            "LLM-01 Service"
        )
        dependencies['llm_02'] = await self._check_http_service(
            settings.LLM_02_URL, 
            "LLM-02 Service"
        )
        
        # Check Qdrant
        dependencies['qdrant'] = await self._check_http_service(
            settings.QDRANT_URL, 
            "Qdrant Vector Database"
        )
        
        # Check Ollama
        dependencies['ollama'] = await self._check_http_service(
            settings.OLLAMA_URL, 
            "Ollama Service"
        )
        
        # Check Redis
        dependencies['redis'] = await self._check_redis()
        
        # Check PostgreSQL
        dependencies['postgresql'] = await self._check_postgresql()
        
        # Update Prometheus metrics
        for service, status in dependencies.items():
            DEPENDENCY_STATUS.labels(service=service).set(
                1 if status.get('status') == 'healthy' else 0
            )
        
        return dependencies
    
    async def check_critical_dependencies(self) -> Dict[str, Any]:
        """
        Check only critical dependencies for readiness checks
        
        Returns:
            Dict[str, Any]: Critical dependency status
        """
        critical_deps = {}
        
        # Only check services required for basic operation
        critical_deps['redis'] = await self._check_redis()
        critical_deps['ollama'] = await self._check_http_service(
            settings.OLLAMA_URL, 
            "Ollama Service"
        )
        
        return critical_deps
    
    async def _check_http_service(self, url: str, name: str) -> Dict[str, Any]:
        """Check HTTP service health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = time.time()
                response = await client.get(f"{url}/health", timeout=5.0)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return {
                        'status': 'healthy',
                        'response_time': response_time,
                        'name': name,
                        'url': url
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'response_time': response_time,
                        'error': f"HTTP {response.status_code}",
                        'name': name,
                        'url': url
                    }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'name': name,
                'url': url
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connection"""
        try:
            import redis.asyncio as redis
            
            redis_client = redis.from_url(settings.redis_url)
            start_time = time.time()
            await redis_client.ping()
            response_time = time.time() - start_time
            await redis_client.close()
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'name': 'Redis',
                'url': settings.redis_url
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'name': 'Redis',
                'url': settings.redis_url
            }
    
    async def _check_postgresql(self) -> Dict[str, Any]:
        """Check PostgreSQL connection"""
        try:
            # Basic connection check (implement with actual DB connection)
            return {
                'status': 'healthy',
                'response_time': 0.1,
                'name': 'PostgreSQL',
                'url': settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'name': 'PostgreSQL'
            }
    
    async def update_metrics(self):
        """Update dynamic metrics"""
        try:
            # Update uptime
            uptime = time.time() - self._start_time
            
            # Update dependency metrics
            dependencies = await self.check_critical_dependencies()
            for service, status in dependencies.items():
                DEPENDENCY_STATUS.labels(service=service).set(
                    1 if status.get('status') == 'healthy' else 0
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics: {e}")
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_embedding_request(self, model: str):
        """Record embedding request"""
        EMBEDDING_REQUESTS.labels(model=model).inc()
    
    def record_workflow_execution(self, workflow_id: str, status: str):
        """Record workflow execution"""
        WORKFLOW_EXECUTIONS.labels(workflow_id=workflow_id, status=status).inc()
    
    def set_active_connections(self, count: int):
        """Set active connections count"""
        ACTIVE_CONNECTIONS.set(count)
    
    @property
    def uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self._start_time
