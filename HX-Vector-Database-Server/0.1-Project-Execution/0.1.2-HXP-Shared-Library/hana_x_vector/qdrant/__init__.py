"""
Qdrant Integration Layer
=======================

Qdrant vector database integration components including client wrapper,
collection management, and indexing optimization.

Components:
- QdrantClient: Main database client wrapper
- CollectionManager: Collection schema and lifecycle management
- IndexOptimizer: Performance optimization for vector indices
- ConfigManager: Qdrant-specific configuration management
"""

from .client import QdrantClient
from .collections import CollectionManager
from .indexing import IndexOptimizer
from .config import QdrantConfigManager

__all__ = [
    "QdrantClient",
    "CollectionManager",
    "IndexOptimizer",
    "QdrantConfigManager"
]
