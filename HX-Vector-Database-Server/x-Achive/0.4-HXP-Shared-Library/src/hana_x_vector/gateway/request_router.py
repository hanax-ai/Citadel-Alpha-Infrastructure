"""
Request Router Module

Intelligent request routing and load balancing following HXP Governance Coding Standards.
Implements Single Responsibility Principle for request routing logic.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime
from enum import Enum
import hashlib
import random

from hana_x_vector.utils.metrics import get_metrics_collector, monitor_performance
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


class RoutingStrategy(Enum):
    """Routing strategies (Business rule encapsulation)."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    HASH_BASED = "hash_based"
    RANDOM = "random"


class BackendStatus(Enum):
    """Backend server status (State encapsulation)."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class Backend:
    """
    Backend server representation (Data encapsulation).
    
    Encapsulates backend server information and health status.
    """
    
    def __init__(self, id: str, host: str, port: int, weight: int = 1):
        """
        Initialize backend server.
        
        Args:
            id: Unique backend identifier
            host: Backend host address
            port: Backend port number
            weight: Backend weight for weighted routing
        """
        self.id = id
        self.host = host
        self.port = port
        self.weight = weight
        self.status = BackendStatus.UNKNOWN
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0
        self.last_health_check = None
        self.metadata = {}
    
    @property
    def url(self) -> str:
        """Get backend URL."""
        return f"http://{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        """Check if backend is healthy."""
        return self.status == BackendStatus.HEALTHY
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 100.0
        return ((self.total_requests - self.failed_requests) / self.total_requests) * 100
    
    def update_stats(self, success: bool, response_time: float) -> None:
        """Update backend statistics."""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
        
        # Update average response time (exponential moving average)
        alpha = 0.1
        self.average_response_time = (
            alpha * response_time + (1 - alpha) * self.average_response_time
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert backend to dictionary."""
        return {
            "id": self.id,
            "host": self.host,
            "port": self.port,
            "url": self.url,
            "weight": self.weight,
            "status": self.status.value,
            "active_connections": self.active_connections,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metadata": self.metadata
        }


class RequestRouterInterface(ABC):
    """
    Abstract interface for request router (Abstraction principle).
    
    Defines the contract for request routing without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def route_request(self, request_data: Dict[str, Any]) -> Optional[Backend]:
        """Route request to appropriate backend."""
        pass
    
    @abstractmethod
    async def add_backend(self, backend: Backend) -> None:
        """Add backend server."""
        pass
    
    @abstractmethod
    async def remove_backend(self, backend_id: str) -> None:
        """Remove backend server."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of request router."""
        pass


class RequestRouter(RequestRouterInterface):
    """
    Request router implementation (Single Responsibility Principle).
    
    Handles intelligent request routing with multiple strategies,
    health checking, and load balancing capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize request router.
        
        Args:
            config: Configuration dictionary containing routing settings
        """
        self._config = config
        self._backends: Dict[str, Backend] = {}
        self._strategy = RoutingStrategy(config.get("strategy", "round_robin"))
        self._current_index = 0
        self._health_check_interval = config.get("health_check_interval", 30)
        self._health_check_task = None
        self._running = False
        
        # Initialize backends from configuration
        self._init_backends()
        
        logger.info(f"RequestRouter initialized with strategy: {self._strategy.value}")
    
    def _init_backends(self) -> None:
        """Initialize backends from configuration."""
        backends_config = self._config.get("backends", [])
        
        for backend_config in backends_config:
            backend = Backend(
                id=backend_config["id"],
                host=backend_config["host"],
                port=backend_config["port"],
                weight=backend_config.get("weight", 1)
            )
            self._backends[backend.id] = backend
        
        logger.info(f"Initialized {len(self._backends)} backends")
    
    async def start(self) -> None:
        """Start request router services."""
        if self._running:
            logger.warning("Request router already running")
            return
        
        try:
            # Start health check task
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._running = True
            
            logger.info("Request router started")
            
        except Exception as e:
            logger.error(f"Failed to start request router: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop request router services."""
        if not self._running:
            logger.warning("Request router not running")
            return
        
        try:
            # Stop health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            self._running = False
            logger.info("Request router stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop request router: {e}")
            raise
    
    @monitor_performance("route_request")
    async def route_request(self, request_data: Dict[str, Any]) -> Optional[Backend]:
        """
        Route request to appropriate backend.
        
        Args:
            request_data: Request data for routing decision
            
        Returns:
            Selected backend or None if no healthy backends available
        """
        try:
            # Get healthy backends
            healthy_backends = [
                backend for backend in self._backends.values()
                if backend.is_healthy
            ]
            
            if not healthy_backends:
                logger.warning("No healthy backends available")
                return None
            
            # Route based on strategy
            if self._strategy == RoutingStrategy.ROUND_ROBIN:
                return self._round_robin_routing(healthy_backends)
            elif self._strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_routing(healthy_backends)
            elif self._strategy == RoutingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_routing(healthy_backends)
            elif self._strategy == RoutingStrategy.RESPONSE_TIME:
                return self._response_time_routing(healthy_backends)
            elif self._strategy == RoutingStrategy.HASH_BASED:
                return self._hash_based_routing(healthy_backends, request_data)
            elif self._strategy == RoutingStrategy.RANDOM:
                return self._random_routing(healthy_backends)
            else:
                return self._round_robin_routing(healthy_backends)
                
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            return None
    
    def _round_robin_routing(self, backends: List[Backend]) -> Backend:
        """Round-robin routing strategy."""
        if not backends:
            return None
        
        backend = backends[self._current_index % len(backends)]
        self._current_index = (self._current_index + 1) % len(backends)
        return backend
    
    def _weighted_round_robin_routing(self, backends: List[Backend]) -> Backend:
        """Weighted round-robin routing strategy."""
        if not backends:
            return None
        
        # Create weighted list
        weighted_backends = []
        for backend in backends:
            weighted_backends.extend([backend] * backend.weight)
        
        if not weighted_backends:
            return backends[0]
        
        backend = weighted_backends[self._current_index % len(weighted_backends)]
        self._current_index = (self._current_index + 1) % len(weighted_backends)
        return backend
    
    def _least_connections_routing(self, backends: List[Backend]) -> Backend:
        """Least connections routing strategy."""
        if not backends:
            return None
        
        return min(backends, key=lambda b: b.active_connections)
    
    def _response_time_routing(self, backends: List[Backend]) -> Backend:
        """Response time based routing strategy."""
        if not backends:
            return None
        
        return min(backends, key=lambda b: b.average_response_time)
    
    def _hash_based_routing(self, backends: List[Backend], request_data: Dict[str, Any]) -> Backend:
        """Hash-based routing strategy."""
        if not backends:
            return None
        
        # Create hash key from request data
        hash_key = str(request_data.get("client_id", "")) + str(request_data.get("session_id", ""))
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        
        return backends[hash_value % len(backends)]
    
    def _random_routing(self, backends: List[Backend]) -> Backend:
        """Random routing strategy."""
        if not backends:
            return None
        
        return random.choice(backends)
    
    async def add_backend(self, backend: Backend) -> None:
        """
        Add backend server.
        
        Args:
            backend: Backend server to add
        """
        try:
            self._backends[backend.id] = backend
            
            # Perform initial health check
            await self._check_backend_health(backend)
            
            logger.info(f"Backend added: {backend.id} ({backend.url})")
            
        except Exception as e:
            logger.error(f"Failed to add backend {backend.id}: {e}")
            raise
    
    async def remove_backend(self, backend_id: str) -> None:
        """
        Remove backend server.
        
        Args:
            backend_id: Backend ID to remove
        """
        try:
            if backend_id in self._backends:
                backend = self._backends.pop(backend_id)
                logger.info(f"Backend removed: {backend_id} ({backend.url})")
            else:
                logger.warning(f"Backend not found: {backend_id}")
                
        except Exception as e:
            logger.error(f"Failed to remove backend {backend_id}: {e}")
            raise
    
    async def update_backend_stats(self, backend_id: str, success: bool, response_time: float) -> None:
        """Update backend statistics."""
        try:
            if backend_id in self._backends:
                backend = self._backends[backend_id]
                backend.update_stats(success, response_time)
                
                # Record metrics
                metrics = get_metrics_collector()
                status = "success" if success else "error"
                metrics.record_external_model_call(
                    backend_id, "request", status, response_time * 1000
                )
                
        except Exception as e:
            logger.error(f"Failed to update backend stats for {backend_id}: {e}")
    
    async def _health_check_loop(self) -> None:
        """Health check loop for all backends."""
        while self._running:
            try:
                # Check health of all backends
                for backend in self._backends.values():
                    await self._check_backend_health(backend)
                
                # Wait for next health check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _check_backend_health(self, backend: Backend) -> None:
        """Check health of a single backend."""
        try:
            # This would implement actual health check logic
            # For now, simulate health check
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                try:
                    async with session.get(f"{backend.url}/health") as response:
                        if response.status == 200:
                            backend.status = BackendStatus.HEALTHY
                        else:
                            backend.status = BackendStatus.UNHEALTHY
                except:
                    backend.status = BackendStatus.UNHEALTHY
            
            backend.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Health check failed for backend {backend.id}: {e}")
            backend.status = BackendStatus.UNHEALTHY
            backend.last_health_check = datetime.now()
    
    async def get_backend_stats(self) -> Dict[str, Any]:
        """Get statistics for all backends."""
        return {
            backend_id: backend.to_dict()
            for backend_id, backend in self._backends.items()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of request router.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            healthy_backends = sum(1 for b in self._backends.values() if b.is_healthy)
            total_backends = len(self._backends)
            
            return {
                "status": "healthy" if self._running else "stopped",
                "message": "Request router operational" if self._running else "Request router stopped",
                "running": self._running,
                "strategy": self._strategy.value,
                "backends": {
                    "total": total_backends,
                    "healthy": healthy_backends,
                    "unhealthy": total_backends - healthy_backends
                },
                "health_check_interval": self._health_check_interval,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {e}",
                "running": False,
                "error": str(e)
            }
