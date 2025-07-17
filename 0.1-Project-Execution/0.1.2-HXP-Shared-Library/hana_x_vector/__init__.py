"""
HANA-X Vector Database Shared Library
=====================================

A comprehensive, production-ready foundation for implementing high-performance 
vector database operations using Qdrant. This library serves as the core 
infrastructure for the Vector Database Server (192.168.10.30) in the Citadel AI Operating System.

Version: 2.0.0 (Revised)
Date: 2025-07-15
Architecture Focus: Qdrant Vector Database Only

Core Components:
- API Gateway: Unified multi-protocol access (REST, GraphQL, gRPC)
- Vector Operations: High-performance vector storage and similarity search
- Qdrant Integration: Optimized database operations and management
- External Integration: Seamless integration with 9 external AI models
- Monitoring & Utils: Comprehensive observability and configuration management
"""

__version__ = "2.0.0"
__author__ = "Citadel AI Infrastructure Team"
__email__ = "infrastructure@citadel-ai.com"

# Core library imports
from .gateway.api_gateway import UnifiedAPIGateway
from .vector_ops.operations import VectorOperationsManager
from .qdrant.client import QdrantClient
from .external_models.integration_patterns import IntegrationPatternManager
from .monitoring.metrics import MetricsCollector
from .monitoring.health import HealthMonitor
from .utils.config import ConfigManager
from .utils.exceptions import (
    VectorOperationError,
    QdrantConnectionError,
    ExternalModelError,
    ConfigurationError
)

__all__ = [
    "UnifiedAPIGateway",
    "VectorOperationsManager", 
    "QdrantClient",
    "IntegrationPatternManager",
    "MetricsCollector",
    "HealthMonitor",
    "ConfigManager",
    "VectorOperationError",
    "QdrantConnectionError",
    "ExternalModelError",
    "ConfigurationError"
]
