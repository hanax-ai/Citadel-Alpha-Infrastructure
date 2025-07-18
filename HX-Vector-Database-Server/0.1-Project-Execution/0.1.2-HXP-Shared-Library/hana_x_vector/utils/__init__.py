"""
Utilities Package
================

Common utilities for the HANA-X Vector Database Shared Library.
Provides configuration management, custom exceptions, and validation utilities.
"""

from .config import ConfigManager
from .exceptions import (
    VectorDatabaseError,
    QdrantError,
    CacheError,
    ValidationError,
    ExternalModelError,
    HealthCheckError,
    AuthenticationError,
    RateLimitError
)
from .validators import (
    VectorValidator,
    CollectionValidator,
    SearchValidator,
    BatchValidator
)

__all__ = [
    # Configuration
    'ConfigManager',
    
    # Exceptions
    'VectorDatabaseError',
    'QdrantError',
    'CacheError',
    'ValidationError',
    'ExternalModelError',
    'HealthCheckError',
    'AuthenticationError',
    'RateLimitError',
    
    # Validators
    'VectorValidator',
    'CollectionValidator',
    'SearchValidator',
    'BatchValidator'
]
