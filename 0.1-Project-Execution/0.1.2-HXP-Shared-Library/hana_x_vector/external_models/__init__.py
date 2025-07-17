"""
External Models Integration Layer
================================

Integration components for external AI models including pattern management,
client connections, and connection pooling.

Components:
- IntegrationPatternManager: Manages different integration patterns
- ModelClients: Client connections to external AI models
- ConnectionPool: Connection pooling and management
"""

from .integration_patterns import IntegrationPatternManager
from .model_clients import ModelClients
from .connection_pool import ConnectionPool

__all__ = [
    "IntegrationPatternManager",
    "ModelClients",
    "ConnectionPool"
]
