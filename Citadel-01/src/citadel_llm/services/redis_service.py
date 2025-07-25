"""
Redis Service for Citadel LLM Architecture
Provides caching and session management capabilities
"""

import asyncio
import json
import logging
from typing import Optional, Any, Dict
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisService:
    """
    Redis service for caching and architectural support.
    Provides connection management and common Redis operations.
    """
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._config: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self, config: Dict[str, Any]):
        """Initialize Redis connection with configuration"""
        try:
            self._config = config.get('redis', {})
            host = self._config.get('host', 'localhost')
            port = self._config.get('port', 6379)
            db = self._config.get('db', 0)
            timeout = self._config.get('timeout', 5)
            
            logger.info(f"Initializing Redis connection to {host}:{port} (db: {db})")
            
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                socket_timeout=timeout,
                decode_responses=True
            )
            
            # Test connection
            await self._client.ping()
            self._initialized = True
            logger.info("Redis Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis Service: {e}")
            self._initialized = False
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check Redis service health"""
        if not self._initialized or not self._client:
            return {"status": "unhealthy", "error": "Redis not initialized"}
        
        try:
            await self._client.ping()
            info = await self._client.info()
            
            return {
                "status": "healthy",
                "connection": "active",
                "server_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        if not self._initialized:
            logger.warning("Redis not initialized, cannot set value")
            return False
            
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self._client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis set operation failed: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        if not self._initialized:
            logger.warning("Redis not initialized, cannot get value")
            return None
            
        try:
            value = await self._client.get(key)
            if value is None:
                return None
                
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis get operation failed: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key"""
        if not self._initialized:
            logger.warning("Redis not initialized, cannot delete key")
            return False
            
        try:
            result = await self._client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete operation failed: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._initialized:
            return False
            
        try:
            result = await self._client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis exists operation failed: {e}")
            return False

    async def close(self):
        """Close Redis connection"""
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        self._initialized = False

# Global Redis service instance
redis_service = RedisService()
