"""
Vector Operations Layer
======================

Core vector operations for Qdrant database including CRUD operations,
similarity search, batch processing, and caching.

Components:
- VectorOperationsManager: Main operations coordinator
- SearchEngine: Similarity search algorithms
- BatchProcessor: Bulk operations handler
- CacheManager: Redis-based caching layer
"""

from .operations import VectorOperationsManager
from .search import SearchEngine
from .batch import BatchProcessor
from .cache import CacheManager

__all__ = [
    "VectorOperationsManager",
    "SearchEngine",
    "BatchProcessor", 
    "CacheManager"
]
