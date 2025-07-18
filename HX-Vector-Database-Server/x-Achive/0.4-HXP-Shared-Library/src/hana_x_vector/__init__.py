"""
HANA-X Vector Database Shared Library

Unified API Gateway & External Model Integration Library for the Citadel AI Operating System.

This module provides comprehensive vector database operations, unified API Gateway functionality,
and external AI model integration patterns following HXP Governance Coding Standards.

Author: Citadel AI Team
Version: 1.0.0
License: MIT
"""

from typing import Dict, Any, Optional
import logging

# Version information
__version__ = "1.0.0"
__author__ = "Citadel AI Team"
__email__ = "dev@citadel-ai.com"
__license__ = "MIT"

# Core imports following dependency inversion principle
from hana_x_vector.core.vector_operations import VectorOperations
# EmbeddingService moved to Orchestration Server
from hana_x_vector.core.collection_manager import CollectionManager

# Gateway imports
from hana_x_vector.gateway.api_gateway import UnifiedAPIGateway
from hana_x_vector.gateway.request_router import RequestRouter
from hana_x_vector.gateway.load_balancer import LoadBalancer
from hana_x_vector.gateway.cache_manager import CacheManager

# External model imports
from hana_x_vector.external_models.integration_patterns import (
    ExternalModelIntegrator,
    IntegrationPattern
)
from hana_x_vector.external_models.model_registry import ExternalModelRegistry
from hana_x_vector.external_models.batch_processor import BatchProcessor

# Model imports
from hana_x_vector.models.vector_models import (
    Vector,
    VectorSearchRequest,
    VectorSearchResult,
    EmbeddingRequest,
    EmbeddingResponse
)
from hana_x_vector.models.external_models import (
    ExternalModel,
    BatchJob
)

# Utility imports
from hana_x_vector.utils.config import VectorDatabaseConfig
from hana_x_vector.utils.logging import setup_logging
from hana_x_vector.utils.metrics import MetricsCollector

# Orchestration imports
from hana_x_vector.orchestration.service_manager import ServiceOrchestrator
from hana_x_vector.protocols import ProtocolAbstractionLayer, ProtocolType
from hana_x_vector.migration import MigrationManager

# Configure logging
logger = logging.getLogger(__name__)

# Public API exports following interface segregation principle
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core components
    "VectorOperations",
    # "EmbeddingService",  # Moved to Orchestration Server 
    "CollectionManager",
    
    # Gateway components
    "UnifiedAPIGateway",
    "RequestRouter",
    "LoadBalancer",
    "CacheManager",
    
    # External model components
    "ExternalModelIntegrator",
    "ExternalModelRegistry",
    "BatchProcessor",
    "IntegrationPattern",
    
    # Data models
    "Vector",
    "VectorSearchRequest",
    "VectorSearchResult",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "ExternalModel",
    "BatchJob",
    
    # Utilities
    "VectorDatabaseConfig",
    "setup_logging",
    "MetricsCollector",
    
    # Orchestration
    "ServiceOrchestrator",
    "ProtocolAbstractionLayer",
    "ProtocolType",
    "MigrationManager",
    
    # Main classes
    "VectorDatabase",
    "APIGateway",
]


class VectorDatabase:
    """
    Main vector database class implementing facade pattern.
    
    This class provides a simplified interface to the complex vector database subsystem,
    following the Single Responsibility Principle by coordinating between components
    without implementing the business logic itself.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None):
        """
        Initialize vector database.
        
        Args:
            config: Configuration dictionary
            config_path: Path to configuration file
            
        Raises:
            ValueError: If neither config nor config_path is provided
        """
        if config is None and config_path is None:
            raise ValueError("Either config or config_path must be provided")
        
        # Load configuration following dependency inversion
        if config_path:
            from hana_x_vector.utils.config import load_config
            self._config = load_config(config_path)
        else:
            self._config = config
        
        # Initialize components following composition over inheritance
        self._vector_ops = VectorOperations(self._config)
        self._embedding_service = EmbeddingService(self._config)
        self._collection_manager = CollectionManager(self._config)
        
        logger.info("VectorDatabase initialized successfully")
    
    @property
    def vector_operations(self) -> VectorOperations:
        """Get vector operations component."""
        return self._vector_ops
    
    @property
    def embedding_service(self) -> EmbeddingService:
        """Get embedding service component."""
        return self._embedding_service
    
    @property
    def collection_manager(self) -> CollectionManager:
        """Get collection manager component."""
        return self._collection_manager
    
    async def initialize(self) -> None:
        """Initialize database components."""
        await self._vector_ops.initialize()
        await self._embedding_service.initialize()
        await self._collection_manager.initialize()
        logger.info("VectorDatabase components initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Dictionary containing health status of all components
        """
        return {
            "vector_operations": await self._vector_ops.health_check(),
            "embedding_service": await self._embedding_service.health_check(),
            "collection_manager": await self._collection_manager.health_check(),
            "overall_status": "healthy"
        }


class APIGateway:
    """
    Main API Gateway class implementing facade pattern.
    
    Provides unified access to all API protocols (REST, GraphQL, gRPC) following
    the Single Responsibility Principle by coordinating requests without implementing
    the protocol-specific logic.
    """
    
    def __init__(self, vector_db: VectorDatabase, config: Optional[Dict[str, Any]] = None):
        """
        Initialize API Gateway.
        
        Args:
            vector_db: Vector database instance
            config: Gateway configuration
        """
        self._vector_db = vector_db
        self._config = config or {}
        
        # Initialize gateway components following composition
        self._unified_gateway = UnifiedAPIGateway(self._config)
        self._request_router = RequestRouter(self._config)
        self._load_balancer = LoadBalancer(self._config)
        self._cache_manager = CacheManager(self._config)
        
        logger.info("APIGateway initialized successfully")
    
    async def start(self) -> None:
        """Start API Gateway services."""
        await self._unified_gateway.start()
        await self._request_router.start()
        await self._load_balancer.start()
        await self._cache_manager.start()
        logger.info("APIGateway services started")
    
    async def stop(self) -> None:
        """Stop API Gateway services."""
        await self._cache_manager.stop()
        await self._load_balancer.stop()
        await self._request_router.stop()
        await self._unified_gateway.stop()
        logger.info("APIGateway services stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Dictionary containing health status of all gateway components
        """
        return {
            "unified_gateway": await self._unified_gateway.health_check(),
            "request_router": await self._request_router.health_check(),
            "load_balancer": await self._load_balancer.health_check(),
            "cache_manager": await self._cache_manager.health_check(),
            "overall_status": "healthy"
        }


# Module initialization
def initialize_library(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the HANA-X Vector Database Shared Library.
    
    Args:
        config: Optional configuration dictionary
    """
    # Setup logging
    setup_logging(config)
    
    # Initialize metrics collection
    if config and config.get("metrics", {}).get("enabled", False):
        metrics_collector = MetricsCollector(
            port=config.get("metrics", {}).get("port", 9090)
        )
        metrics_collector.start_metrics_server()
    
    logger.info(f"HANA-X Vector Database Shared Library v{__version__} initialized")


# Auto-initialize with default configuration
initialize_library()
