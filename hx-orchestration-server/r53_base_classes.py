"""
R5.3 Compliant Base Classes
Common base classes following LLM-01 patterns for standardization
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging

# Configuration and Service Status
class ServiceStatus(Enum):
    """Standard service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceConfig:
    """Standard service configuration class."""
    name: str
    version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8000
    timeout: int = 30
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("Service name cannot be empty")
        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")

# Base Service Classes
class BaseOrchestrationService(ABC):
    """
    Abstract base class for orchestration services.
    Implements LLM-01 pattern for standardized service architecture.
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{config.name}.service")
        self.status = ServiceStatus.UNKNOWN
        self._health_checks: Dict[str, callable] = {}
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the service. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check. Must be implemented by subclasses."""
        pass
    
    async def start(self) -> bool:
        """Start the service."""
        try:
            initialized = await self.initialize()
            if initialized:
                self.status = ServiceStatus.HEALTHY
                self.logger.info(f"Service {self.config.name} started successfully")
                return True
            else:
                self.status = ServiceStatus.UNHEALTHY
                self.logger.error(f"Service {self.config.name} failed to initialize")
                return False
        except Exception as e:
            self.status = ServiceStatus.UNHEALTHY
            self.logger.error(f"Service {self.config.name} startup failed: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the service."""
        try:
            # Perform cleanup
            self.status = ServiceStatus.UNHEALTHY
            self.logger.info(f"Service {self.config.name} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Service {self.config.name} stop failed: {e}")
            return False
    
    def register_health_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self._health_checks[name] = check_func
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        for name, check_func in self._health_checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results

class BaseEmbeddingService(BaseOrchestrationService):
    """
    Base class for embedding services.
    Extends BaseOrchestrationService with embedding-specific functionality.
    """
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.supported_models: List[str] = []
        self.model_dimensions: Dict[str, int] = {}
    
    @abstractmethod
    async def create_embedding(self, text: str, model: str) -> List[float]:
        """Create an embedding for the given text."""
        pass
    
    @abstractmethod
    async def create_embeddings_batch(self, texts: List[str], model: str) -> List[List[float]]:
        """Create embeddings for a batch of texts."""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available embedding models."""
        pass
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model not in self.supported_models:
            raise ValueError(f"Model {model} is not supported")
        
        return {
            "name": model,
            "dimensions": self.model_dimensions.get(model, 0),
            "supported": True
        }

# Base API Client
class BaseAPIClient(ABC):
    """
    Abstract base class for API clients.
    Provides common functionality for HTTP API interactions.
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the API is healthy."""
        pass
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle HTTP response with standard error handling."""
        try:
            if hasattr(response, 'json'):
                return await response.json()
            else:
                return {"error": "Invalid response format"}
        except Exception as e:
            self.logger.error(f"Response handling error: {e}")
            return {"error": str(e)}

# Service Registry
class ServiceRegistry:
    """
    Registry for managing service instances.
    Implements singleton pattern for global service management.
    """
    
    _instance = None
    _services: Dict[str, BaseOrchestrationService] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_service(self, name: str, service: BaseOrchestrationService):
        """Register a service in the registry."""
        self._services[name] = service
    
    def get_service(self, name: str) -> Optional[BaseOrchestrationService]:
        """Get a service from the registry."""
        return self._services.get(name)
    
    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self._services.keys())
    
    async def start_all_services(self) -> Dict[str, bool]:
        """Start all registered services."""
        results = {}
        for name, service in self._services.items():
            results[name] = await service.start()
        return results
    
    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all registered services."""
        results = {}
        for name, service in self._services.items():
            results[name] = await service.stop()
        return results
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health checks on all services."""
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = await service.health_check()
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results
