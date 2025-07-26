"""
Shared Utility Functions and Classes (R5.3 Compliance)
Provides reusable functionality across orchestration components
"""
import hashlib
import json
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from functools import wraps

class CacheKeyGenerator:
    """Standardized cache key generation for consistent caching patterns"""
    
    @staticmethod
    def embedding_key(text: str, model: str, options: Optional[Dict] = None) -> str:
        """Generate consistent cache key for embedding operations"""
        content = f"{text}:{model}"
        if options:
            content += f":{json.dumps(options, sort_keys=True)}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"embedding:{hash_value}"
    
    @staticmethod
    def task_key(task_type: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for task results"""
        param_str = json.dumps(parameters, sort_keys=True)
        hash_value = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"task:{task_type}:{hash_value}"
    
    @staticmethod
    def session_key(user_id: str, session_data: Dict[str, Any]) -> str:
        """Generate cache key for user sessions"""
        content = f"{user_id}:{json.dumps(session_data, sort_keys=True)}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"session:{hash_value}"

class ConfigurationManager:
    """Centralized configuration management with environment variable support"""
    
    def __init__(self):
        self._config_cache = {}
        self._last_reload = datetime.utcnow()
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration settings"""
        return {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 8,
            "timeout": 300,
            "keepalive": 30
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration settings"""
        return {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "max_connections": 20,
            "socket_timeout": 30,
            "socket_connect_timeout": 30
        }
    
    def get_service_endpoints(self) -> Dict[str, str]:
        """Get external service endpoint configurations"""
        return {
            "llm01_endpoint": "http://192.168.10.34:8002",
            "llm02_endpoint": "http://192.168.10.28:8000",
            "qdrant_endpoint": "http://192.168.10.30:6333",
            "postgres_url": "postgresql://citadel_llm_user:CitadelLLM#2025$SecurePass!@192.168.10.35:5432/citadel_llm_db",
            "prometheus_endpoint": "http://192.168.10.37:9090"
        }
    
    def reload_config(self):
        """Reload configuration from environment and files"""
        self._config_cache.clear()
        self._last_reload = datetime.utcnow()

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0
) -> Any:
    """Shared retry mechanism with exponential backoff"""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                break
            
            delay = min(base_delay * (exponential_factor ** attempt), max_delay)
            await asyncio.sleep(delay)
    
    raise last_exception

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger = getattr(func, '__self__', None)
            if hasattr(logger, 'logger'):
                logger.logger.debug(f"{func.__name__} executed in {duration:.2f}ms")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            print(f"{func.__name__} executed in {duration:.2f}ms")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

class ConnectionPoolManager:
    """Shared HTTP connection pool management for external services"""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.connector = None
        self.session = None
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def get_session(self):
        """Context manager for HTTP session with connection pooling"""
        async with self._lock:
            if not self.session:
                self.connector = aiohttp.TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=20,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
                self.session = aiohttp.ClientSession(
                    connector=self.connector,
                    timeout=aiohttp.ClientTimeout(total=300)
                )
        
        try:
            yield self.session
        except Exception:
            # Don't close session on error, let it be reused
            raise
    
    async def close(self):
        """Close connection pool and cleanup resources"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
