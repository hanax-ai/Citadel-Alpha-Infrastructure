"""
R5.3 Common Utilities
Shared utility functions and classes for standardized operations
"""

import asyncio
import time
import hashlib
import logging
import json
from typing import Dict, Any, Optional, Callable, Union, List
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

# Cache Key Generation
class CacheKeyGenerator:
    """Utility class for generating consistent cache keys."""
    
    @staticmethod
    def generate_key(prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and parameters."""
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
    
    @staticmethod
    def embedding_key(text: str, model: str, normalize: bool = True) -> str:
        """Generate cache key for embeddings."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{model}:{text_hash}:{'norm' if normalize else 'raw'}"
    
    @staticmethod
    def health_key(service: str, timestamp: Optional[datetime] = None) -> str:
        """Generate cache key for health checks."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        time_bucket = timestamp.replace(second=0, microsecond=0)  # Minute-level bucketing
        return f"health:{service}:{time_bucket.isoformat()}"

# Configuration Management
@dataclass
class ConfigurationManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger("ConfigurationManager")
    
    def load_from_env(self, prefix: str = "") -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        for key, value in os.environ.items():
            if not prefix or key.startswith(prefix):
                config_key = key[len(prefix):] if prefix else key
                config[config_key.lower()] = value
        
        self.config.update(config)
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
    
    def get_database_url(self) -> str:
        """Get database URL from configuration."""
        return self.get("database_url", "postgresql://localhost:5432/citadel")
    
    def get_redis_url(self) -> str:
        """Get Redis URL from configuration."""
        return self.get("redis_url", "redis://localhost:6379")
    
    def get_ollama_url(self) -> str:
        """Get Ollama URL from configuration."""
        return self.get("ollama_url", "http://localhost:11434")

# Retry Mechanism
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for implementing retry logic with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (backoff_factor ** attempt)
                        await asyncio.sleep(delay)
                    else:
                        raise last_exception
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (backoff_factor ** attempt)
                        time.sleep(delay)
                    else:
                        raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Performance Monitoring
def timing_decorator(func: Callable):
    """Decorator to measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.getLogger(func.__module__).info(
                f"Function {func.__name__} executed in {execution_time:.4f} seconds"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.getLogger(func.__module__).error(
                f"Function {func.__name__} failed after {execution_time:.4f} seconds: {e}"
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.getLogger(func.__module__).info(
                f"Function {func.__name__} executed in {execution_time:.4f} seconds"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.getLogger(func.__module__).error(
                f"Function {func.__name__} failed after {execution_time:.4f} seconds: {e}"
            )
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# Connection Pool Management
class ConnectionPoolManager:
    """Manages connection pools for different services."""
    
    def __init__(self):
        self.pools: Dict[str, Any] = {}
        self.logger = logging.getLogger("ConnectionPoolManager")
    
    async def create_redis_pool(self, redis_url: str, **kwargs):
        """Create Redis connection pool."""
        try:
            import aioredis
            pool = aioredis.from_url(redis_url, **kwargs)
            self.pools['redis'] = pool
            return pool
        except ImportError:
            self.logger.warning("aioredis not available, Redis pool not created")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create Redis pool: {e}")
            return None
    
    async def create_database_pool(self, database_url: str, **kwargs):
        """Create database connection pool."""
        try:
            import asyncpg
            pool = await asyncpg.create_pool(database_url, **kwargs)
            self.pools['database'] = pool
            return pool
        except ImportError:
            self.logger.warning("asyncpg not available, database pool not created")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create database pool: {e}")
            return None
    
    def get_pool(self, name: str):
        """Get a connection pool by name."""
        return self.pools.get(name)
    
    async def close_all_pools(self):
        """Close all connection pools."""
        for name, pool in self.pools.items():
            try:
                if hasattr(pool, 'close'):
                    if asyncio.iscoroutinefunction(pool.close):
                        await pool.close()
                    else:
                        pool.close()
                self.logger.info(f"Closed {name} pool")
            except Exception as e:
                self.logger.error(f"Error closing {name} pool: {e}")

# Response Formatting
class ResponseFormatter:
    """Utility class for formatting API responses."""
    
    @staticmethod
    def success(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Format successful response."""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error(error: str, status_code: int = 500, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Format error response."""
        response = {
            "success": False,
            "error": error,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def health_response(status: str, checks: Optional[Dict] = None, uptime: Optional[float] = None) -> Dict[str, Any]:
        """Format health check response."""
        response = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        if checks:
            response["checks"] = checks
        if uptime is not None:
            response["uptime"] = uptime
        return response

# Validation Utilities
class ValidationUtils:
    """Utility functions for data validation."""
    
    @staticmethod
    def validate_embedding_request(text: str, model: str) -> List[str]:
        """Validate embedding request parameters."""
        errors = []
        
        if not text or not text.strip():
            errors.append("Text cannot be empty")
        
        if len(text) > 10000:  # Arbitrary limit
            errors.append("Text exceeds maximum length of 10,000 characters")
        
        if not model or not model.strip():
            errors.append("Model name cannot be empty")
        
        return errors
    
    @staticmethod
    def validate_health_response(response: Dict[str, Any]) -> bool:
        """Validate health response format."""
        required_fields = ['status', 'timestamp']
        return all(field in response for field in required_fields)

# Logging Configuration
def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> logging.Logger:
    """Set up standardized logging configuration."""
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/r53_service.log")
        ]
    )
    
    return logging.getLogger("R53Service")

# Global Configuration Instance
config_manager = ConfigurationManager()
