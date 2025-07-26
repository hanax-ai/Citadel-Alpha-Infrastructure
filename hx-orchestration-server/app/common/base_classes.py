"""
Base Classes

Common base classes following OOP principles (R5.1).
Provides foundation classes for services, clients, and utilities.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from config.settings import get_settings

settings = get_settings()


class BaseService(ABC):
    """
    Base service class providing common functionality
    
    All service classes should inherit from this base class to ensure
    consistent logging, error handling, and lifecycle management.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize base service
        
        Args:
            name: Service name for logging
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"hx_orchestration.{self.name}")
        self._initialized = False
        self._start_time = datetime.utcnow()
    
    async def initialize(self):
        """Initialize service - override in subclasses"""
        if self._initialized:
            return
        
        self.logger.info(f"Initializing {self.name}")
        self._initialized = True
    
    async def cleanup(self):
        """Cleanup service resources - override in subclasses"""
        self.logger.info(f"Cleaning up {self.name}")
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    @property
    def uptime(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.utcnow() - self._start_time).total_seconds()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', initialized={self._initialized})"


class BaseClient(ABC):
    """
    Base client class for external service integrations
    
    Provides common patterns for HTTP clients, connection pooling,
    and error handling when integrating with external services.
    """
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize base client
        
        Args:
            base_url: Base URL for the service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"hx_orchestration.{self.__class__.__name__}")
        self._session: Optional[Any] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    @abstractmethod
    async def connect(self):
        """Establish connection - implement in subclasses"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection - implement in subclasses"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health - implement in subclasses"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url='{self.base_url}')"


class BaseProcessor(ABC):
    """
    Base processor class for data processing pipelines
    
    Provides common patterns for batch processing, error handling,
    and progress tracking for data processing operations.
    """
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        """
        Initialize base processor
        
        Args:
            batch_size: Default batch size for processing
            max_workers: Maximum number of worker threads/tasks
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.logger = logging.getLogger(f"hx_orchestration.{self.__class__.__name__}")
        self._processing = False
    
    @abstractmethod
    async def process_item(self, item: Any) -> Any:
        """Process single item - implement in subclasses"""
        pass
    
    async def process_batch(self, items: list, **kwargs) -> list:
        """
        Process batch of items with error handling
        
        Args:
            items: List of items to process
            **kwargs: Additional processing options
            
        Returns:
            list: Processed results
        """
        if self._processing:
            raise RuntimeError(f"{self.__class__.__name__} is already processing")
        
        self._processing = True
        results = []
        
        try:
            self.logger.info(f"Processing batch of {len(items)} items")
            
            # Process items in smaller batches
            for i in range(0, len(items), self.batch_size):
                batch = items[i:i + self.batch_size]
                batch_results = await self._process_batch_chunk(batch, **kwargs)
                results.extend(batch_results)
                
                self.logger.debug(f"Processed {len(results)}/{len(items)} items")
            
            self.logger.info(f"Completed processing {len(results)} items")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
        finally:
            self._processing = False
    
    async def _process_batch_chunk(self, batch: list, **kwargs) -> list:
        """Process a chunk of the batch"""
        tasks = [self.process_item(item, **kwargs) for item in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    @property
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return self._processing


class BaseManager(ABC):
    """
    Base manager class for coordinating multiple services
    
    Provides common patterns for managing collections of services,
    lifecycle coordination, and state management.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize base manager
        
        Args:
            name: Manager name for logging
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"hx_orchestration.{self.name}")
        self._services: Dict[str, BaseService] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize manager and all services"""
        if self._initialized:
            return
        
        self.logger.info(f"Initializing {self.name}")
        
        # Initialize all registered services
        for service_name, service in self._services.items():
            try:
                await service.initialize()
                self.logger.debug(f"Initialized service: {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize service {service_name}: {e}")
                raise
        
        self._initialized = True
        self.logger.info(f"{self.name} initialized with {len(self._services)} services")
    
    async def cleanup(self):
        """Cleanup manager and all services"""
        self.logger.info(f"Cleaning up {self.name}")
        
        # Cleanup all services in reverse order
        for service_name, service in reversed(list(self._services.items())):
            try:
                await service.cleanup()
                self.logger.debug(f"Cleaned up service: {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup service {service_name}: {e}")
        
        self._initialized = False
    
    def register_service(self, name: str, service: BaseService):
        """Register a service with the manager"""
        if name in self._services:
            raise ValueError(f"Service '{name}' already registered")
        
        self._services[name] = service
        self.logger.debug(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a registered service by name"""
        return self._services.get(name)
    
    @property
    def service_count(self) -> int:
        """Get number of registered services"""
        return len(self._services)
    
    @property
    def is_initialized(self) -> bool:
        """Check if manager is initialized"""
        return self._initialized


class BaseEmbeddingService(BaseService):
    """
    Base class for embedding services
    
    Provides common functionality for embedding generation services
    including health checks, performance monitoring, and error handling.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize embedding service
        
        Args:
            name: Service name for logging
        """
        super().__init__(name)
        self._health_status = "unknown"
        self._last_health_check = None
        self._embedding_count = 0
        self._error_count = 0
    
    @abstractmethod
    async def generate_embeddings(self, texts: list, model: str) -> list:
        """
        Generate embeddings for given texts
        
        Args:
            texts: List of text strings to embed
            model: Model identifier to use
            
        Returns:
            List of embedding vectors (list of floats)
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> dict:
        """
        Perform health check on the embedding service
        
        Returns:
            Dict with health status information
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> list:
        """
        List available embedding models
        
        Returns:
            List of available model identifiers
        """
        pass
    
    async def record_embedding_request(self, count: int, success: bool = True):
        """
        Record embedding request metrics
        
        Args:
            count: Number of embeddings generated
            success: Whether the request was successful
        """
        if success:
            self._embedding_count += count
        else:
            self._error_count += 1
        
        self.logger.debug(f"Recorded embedding request: {count} embeddings, success={success}")
    
    @property
    def health_status(self) -> str:
        """Get current health status"""
        return self._health_status
    
    @property
    def embedding_count(self) -> int:
        """Get total number of embeddings generated"""
        return self._embedding_count
    
    @property
    def error_count(self) -> int:
        """Get total number of errors"""
        return self._error_count
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        total_requests = self._embedding_count + self._error_count
        if total_requests == 0:
            return 100.0
        return (self._embedding_count / total_requests) * 100.0


class BaseOrchestrationService(BaseService):
    """
    Base class for orchestration services
    
    Provides common functionality for orchestration components including
    service discovery, load balancing, and workflow management.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize orchestration service
        
        Args:
            name: Service name for logging
        """
        super().__init__(name)
        self._status = "initializing"
        self._last_update = None
        self._operation_count = 0
    
    @abstractmethod
    async def start_service(self):
        """Start the orchestration service"""
        pass
    
    @abstractmethod
    async def stop_service(self):
        """Stop the orchestration service"""
        pass
    
    @abstractmethod
    async def get_status(self) -> dict:
        """
        Get current service status
        
        Returns:
            Dict with status information
        """
        pass
    
    async def record_operation(self, operation_type: str, success: bool = True):
        """
        Record an operation for metrics
        
        Args:
            operation_type: Type of operation performed
            success: Whether the operation was successful
        """
        self._operation_count += 1
        self._last_update = datetime.utcnow()
        
        self.logger.debug(f"Recorded operation: {operation_type}, success={success}")
    
    @property
    def status(self) -> str:
        """Get current service status"""
        return self._status
    
    @property
    def operation_count(self) -> int:
        """Get total number of operations performed"""
        return self._operation_count
    
    @property
    def last_update(self) -> Optional[datetime]:
        """Get timestamp of last update"""
        return self._last_update
