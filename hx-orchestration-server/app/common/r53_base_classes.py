"""
Common Base Classes for Orchestration Services (R5.3 Compliance)
Provides standardized base classes with consistent patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass

class BaseOrchestrationService(ABC):
    """Base class for all orchestration services with common patterns"""
    
    def __init__(self, service_name: str, config: Dict[str, Any]):
        self.service_name = service_name
        self.config = config
        self.logger = logging.getLogger(f"orchestration.{service_name}")
        self._health_status = "initializing"
        self._start_time = datetime.utcnow()
        self._metrics = {"requests": 0, "errors": 0, "last_activity": None}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize service resources and dependencies"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return comprehensive service health status"""
        pass
    
    async def shutdown(self) -> None:
        """Graceful shutdown with resource cleanup"""
        self._health_status = "shutting_down"
        self.logger.info(f"{self.service_name} shutting down gracefully")
    
    def record_activity(self):
        """Record service activity for monitoring"""
        self._metrics["requests"] += 1
        self._metrics["last_activity"] = datetime.utcnow()
    
    def record_error(self):
        """Record service error for monitoring"""
        self._metrics["errors"] += 1
    
    @property
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.utcnow() - self._start_time).total_seconds()

class BaseEmbeddingService(BaseOrchestrationService):
    """Specialized base class for embedding services"""
    
    def __init__(self, service_name: str, config: Dict[str, Any], model_name: str):
        super().__init__(service_name, config)
        self.model_name = model_name
        self._embedding_metrics = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "average_latency": 0.0,
            "model_load_time": None
        }
    
    async def get_embedding_metrics(self) -> Dict[str, Any]:
        """Return embedding-specific performance metrics"""
        hit_rate = (self._embedding_metrics["cache_hits"] / 
                   max(self._embedding_metrics["total_embeddings"], 1))
        
        return {
            "model_name": self.model_name,
            "total_embeddings": self._embedding_metrics["total_embeddings"],
            "cache_hit_rate": hit_rate,
            "average_latency_ms": self._embedding_metrics["average_latency"],
            "uptime_seconds": self.uptime_seconds,
            "model_loaded": self._embedding_metrics["model_load_time"] is not None
        }
    
    def record_embedding(self, latency_ms: float, cache_hit: bool = False):
        """Record embedding generation metrics"""
        self.record_activity()
        self._embedding_metrics["total_embeddings"] += 1
        if cache_hit:
            self._embedding_metrics["cache_hits"] += 1
        
        # Update running average latency
        current_avg = self._embedding_metrics["average_latency"]
        count = self._embedding_metrics["total_embeddings"]
        self._embedding_metrics["average_latency"] = (
            (current_avg * (count - 1) + latency_ms) / count
        )

@dataclass
class ServiceConfig:
    """Standard configuration data class"""
    service_name: str
    host: str = "localhost"
    port: int = 8000
    timeout: int = 30
    max_retries: int = 3
    debug: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility"""
        return {
            "service_name": self.service_name,
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "debug": self.debug
        }

class BaseAPIClient(ABC):
    """Base class for external API clients with common patterns"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"client.{config.service_name}")
        self._session = None
        self._connection_pool = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection and cleanup resources"""
        pass
    
    async def is_healthy(self) -> bool:
        """Check if service is healthy and reachable"""
        try:
            # Implement basic connectivity check
            return await self.health_check()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Implement service-specific health check"""
        pass
