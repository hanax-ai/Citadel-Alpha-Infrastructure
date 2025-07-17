"""
Cache Manager
============

Redis-based caching layer for vector operations.
Provides intelligent caching strategies for search results and metadata.
"""

from typing import Dict, Any, Optional, List
import json
import hashlib
import time
import asyncio
import redis.asyncio as redis
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError


class CacheManager:
    """
    Redis-based cache manager for vector operations.
    Implements intelligent caching strategies for performance optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Cache configuration
        cache_config = config.get("cache", {})
        self.cache_enabled = cache_config.get("enabled", True)
        self.redis_host = cache_config.get("host", "192.168.10.35")
        self.redis_port = cache_config.get("port", 6379)
        self.redis_db = cache_config.get("db", 0)
        self.redis_password = cache_config.get("password")
        
        # Cache settings
        self.default_ttl = cache_config.get("default_ttl", 300)  # 5 minutes
        self.search_cache_ttl = cache_config.get("search_ttl", 600)  # 10 minutes
        self.metadata_cache_ttl = cache_config.get("metadata_ttl", 1800)  # 30 minutes
        self.max_cache_size = cache_config.get("max_size", 1000000)  # 1M entries
        
        # Key prefixes
        self.key_prefix = cache_config.get("key_prefix", "hana_x_vector:")
        self.search_prefix = f"{self.key_prefix}search:"
        self.metadata_prefix = f"{self.key_prefix}metadata:"
        self.collection_prefix = f"{self.key_prefix}collection:"
        
        # Cache strategies
        self.cache_strategies = {
            "search": cache_config.get("search_strategy", "lru"),
            "metadata": cache_config.get("metadata_strategy", "ttl"),
            "collection": cache_config.get("collection_strategy", "write_through")
        }
        
        # Redis client
        self.redis_client = None
        self.redis_pool = None
    
    async def startup(self):
        """Initialize cache manager and Redis connection."""
        if not self.cache_enabled:
            return
        
        try:
            # Create Redis connection pool
            self.redis_pool = redis.ConnectionPool(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                max_connections=20
            )
            
            # Create Redis client
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self.redis_client.ping()
            
            # Initialize cache monitoring
            await self._setup_cache_monitoring()
            
        except Exception as e:
            print(f"Warning: Cache initialization failed: {e}")
            self.cache_enabled = False
    
    async def shutdown(self):
        """Cleanup cache manager and Redis connections."""
        if self.redis_client:
            await self.redis_client.close()
        if self.redis_pool:
            await self.redis_pool.disconnect()
    
    def generate_search_cache_key(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> str:
        """
        Generate cache key for search operations.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Result limit
            filters: Search filters
            score_threshold: Score threshold
            
        Returns:
            Cache key string
        """
        # Create key data
        key_data = {
            "collection": collection_name,
            "vector_hash": self._hash_vector(query_vector),
            "limit": limit,
            "filters": filters,
            "score_threshold": score_threshold
        }
        
        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.search_prefix}{key_hash}"
    
    async def get_cached_search(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached search results.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached search results or None
        """
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            # Get from cache
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                result = json.loads(cached_data)
                
                # Update access time for LRU
                if self.cache_strategies["search"] == "lru":
                    await self.redis_client.expire(cache_key, self.search_cache_ttl)
                
                self.metrics.increment_counter("cache_hits", tags={"type": "search"})
                return result
            
            self.metrics.increment_counter("cache_misses", tags={"type": "search"})
            return None
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "search"})
            print(f"Cache get error: {e}")
            return None
    
    async def cache_search_result(
        self,
        cache_key: str,
        result: Dict[str, Any]
    ) -> bool:
        """
        Cache search results.
        
        Args:
            cache_key: Cache key
            result: Search results to cache
            
        Returns:
            True if cached successfully
        """
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            # Add timestamp
            result["cached_at"] = time.time()
            
            # Serialize and cache
            cached_data = json.dumps(result)
            await self.redis_client.setex(
                cache_key,
                self.search_cache_ttl,
                cached_data
            )
            
            self.metrics.increment_counter("cache_writes", tags={"type": "search"})
            return True
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "search"})
            print(f"Cache set error: {e}")
            return False
    
    async def get_cached_metadata(
        self,
        collection_name: str,
        vector_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached vector metadata.
        
        Args:
            collection_name: Collection name
            vector_id: Vector ID
            
        Returns:
            Cached metadata or None
        """
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            cache_key = f"{self.metadata_prefix}{collection_name}:{vector_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.metrics.increment_counter("cache_hits", tags={"type": "metadata"})
                return json.loads(cached_data)
            
            self.metrics.increment_counter("cache_misses", tags={"type": "metadata"})
            return None
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "metadata"})
            return None
    
    async def cache_metadata(
        self,
        collection_name: str,
        vector_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Cache vector metadata.
        
        Args:
            collection_name: Collection name
            vector_id: Vector ID
            metadata: Metadata to cache
            
        Returns:
            True if cached successfully
        """
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            cache_key = f"{self.metadata_prefix}{collection_name}:{vector_id}"
            cached_data = json.dumps(metadata)
            
            await self.redis_client.setex(
                cache_key,
                self.metadata_cache_ttl,
                cached_data
            )
            
            self.metrics.increment_counter("cache_writes", tags={"type": "metadata"})
            return True
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "metadata"})
            return False
    
    async def get_cached_collection_info(
        self,
        collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached collection information.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Cached collection info or None
        """
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            cache_key = f"{self.collection_prefix}info:{collection_name}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                self.metrics.increment_counter("cache_hits", tags={"type": "collection"})
                return json.loads(cached_data)
            
            self.metrics.increment_counter("cache_misses", tags={"type": "collection"})
            return None
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "collection"})
            return None
    
    async def cache_collection_info(
        self,
        collection_name: str,
        info: Dict[str, Any]
    ) -> bool:
        """
        Cache collection information.
        
        Args:
            collection_name: Collection name
            info: Collection info to cache
            
        Returns:
            True if cached successfully
        """
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            cache_key = f"{self.collection_prefix}info:{collection_name}"
            cached_data = json.dumps(info)
            
            await self.redis_client.setex(
                cache_key,
                self.metadata_cache_ttl,
                cached_data
            )
            
            self.metrics.increment_counter("cache_writes", tags={"type": "collection"})
            return True
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "collection"})
            return False
    
    async def invalidate_collection_cache(self, collection_name: str) -> bool:
        """
        Invalidate all cache entries for a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            True if invalidated successfully
        """
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            # Find all keys for this collection
            patterns = [
                f"{self.search_prefix}*{collection_name}*",
                f"{self.metadata_prefix}{collection_name}:*",
                f"{self.collection_prefix}*{collection_name}*"
            ]
            
            deleted_count = 0
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted_count += await self.redis_client.delete(*keys)
            
            self.metrics.increment_counter("cache_invalidations", deleted_count)
            return True
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "invalidation"})
            print(f"Cache invalidation error: {e}")
            return False
    
    async def invalidate_search_cache(
        self,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Invalidate search cache entries.
        
        Args:
            collection_name: Optional collection name filter
            
        Returns:
            True if invalidated successfully
        """
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            if collection_name:
                pattern = f"{self.search_prefix}*{collection_name}*"
            else:
                pattern = f"{self.search_prefix}*"
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted_count = await self.redis_client.delete(*keys)
                self.metrics.increment_counter("cache_invalidations", deleted_count)
            
            return True
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "invalidation"})
            return False
    
    async def warm_cache(
        self,
        collection_name: str,
        popular_queries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Warm cache with popular queries.
        
        Args:
            collection_name: Collection name
            popular_queries: List of popular query patterns
            
        Returns:
            Cache warming results
        """
        if not self.cache_enabled or not self.redis_client:
            return {"warmed": 0, "errors": 0}
        
        warmed_count = 0
        error_count = 0
        
        try:
            for query in popular_queries:
                try:
                    # Generate cache key
                    cache_key = self.generate_search_cache_key(
                        collection_name=collection_name,
                        query_vector=query["vector"],
                        limit=query.get("limit", 10),
                        filters=query.get("filters"),
                        score_threshold=query.get("score_threshold")
                    )
                    
                    # Check if already cached
                    if not await self.redis_client.exists(cache_key):
                        # Pre-populate with placeholder
                        placeholder = {
                            "results": [],
                            "duration": 0,
                            "collection": collection_name,
                            "count": 0,
                            "warmed": True,
                            "cached_at": time.time()
                        }
                        
                        await self.cache_search_result(cache_key, placeholder)
                        warmed_count += 1
                        
                except Exception as e:
                    error_count += 1
                    print(f"Cache warming error for query: {e}")
            
            self.metrics.increment_counter("cache_warm_operations", warmed_count)
            
            return {
                "warmed": warmed_count,
                "errors": error_count,
                "collection": collection_name
            }
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "warming"})
            raise VectorOperationError(f"Cache warming failed: {str(e)}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics
        """
        if not self.cache_enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            # Get Redis info
            info = await self.redis_client.info()
            
            # Count keys by type
            search_keys = len(await self.redis_client.keys(f"{self.search_prefix}*"))
            metadata_keys = len(await self.redis_client.keys(f"{self.metadata_prefix}*"))
            collection_keys = len(await self.redis_client.keys(f"{self.collection_prefix}*"))
            
            return {
                "enabled": True,
                "redis_info": {
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed")
                },
                "key_counts": {
                    "search": search_keys,
                    "metadata": metadata_keys,
                    "collection": collection_keys,
                    "total": search_keys + metadata_keys + collection_keys
                },
                "configuration": {
                    "default_ttl": self.default_ttl,
                    "search_ttl": self.search_cache_ttl,
                    "metadata_ttl": self.metadata_cache_ttl
                }
            }
            
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    async def clear_cache(self, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear cache entries.
        
        Args:
            pattern: Optional key pattern to clear
            
        Returns:
            Clear operation results
        """
        if not self.cache_enabled or not self.redis_client:
            return {"cleared": 0}
        
        try:
            if pattern:
                keys = await self.redis_client.keys(pattern)
            else:
                keys = await self.redis_client.keys(f"{self.key_prefix}*")
            
            if keys:
                cleared_count = await self.redis_client.delete(*keys)
            else:
                cleared_count = 0
            
            self.metrics.increment_counter("cache_clears", cleared_count)
            
            return {
                "cleared": cleared_count,
                "pattern": pattern or f"{self.key_prefix}*"
            }
            
        except Exception as e:
            self.metrics.increment_counter("cache_errors", tags={"type": "clear"})
            raise VectorOperationError(f"Cache clear failed: {str(e)}")
    
    def _hash_vector(self, vector: List[float]) -> str:
        """Generate hash for vector data."""
        # Convert to string and hash
        vector_str = ",".join(f"{v:.6f}" for v in vector)
        return hashlib.md5(vector_str.encode()).hexdigest()[:16]
    
    async def _setup_cache_monitoring(self):
        """Setup cache monitoring and cleanup tasks."""
        # Start background cleanup task
        asyncio.create_task(self._cleanup_expired_keys())
        
        # Start cache size monitoring
        asyncio.create_task(self._monitor_cache_size())
    
    async def _cleanup_expired_keys(self):
        """Background task to cleanup expired keys."""
        while self.cache_enabled and self.redis_client:
            try:
                # Let Redis handle TTL expiration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_cache_size(self):
        """Background task to monitor cache size."""
        while self.cache_enabled and self.redis_client:
            try:
                # Get current key count
                total_keys = len(await self.redis_client.keys(f"{self.key_prefix}*"))
                
                # Check if approaching limit
                if total_keys > self.max_cache_size * 0.9:
                    # Implement LRU eviction or cleanup
                    await self._evict_old_entries()
                
                self.metrics.record_gauge("cache_size", total_keys)
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"Cache monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _evict_old_entries(self):
        """Evict old cache entries when approaching size limit."""
        try:
            # Get all keys with TTL info
            keys = await self.redis_client.keys(f"{self.key_prefix}*")
            
            # Sort by TTL (evict keys expiring soonest)
            key_ttls = []
            for key in keys:
                ttl = await self.redis_client.ttl(key)
                key_ttls.append((key, ttl))
            
            # Sort by TTL (ascending)
            key_ttls.sort(key=lambda x: x[1])
            
            # Evict 10% of keys
            evict_count = len(keys) // 10
            keys_to_evict = [key for key, _ in key_ttls[:evict_count]]
            
            if keys_to_evict:
                await self.redis_client.delete(*keys_to_evict)
                self.metrics.increment_counter("cache_evictions", len(keys_to_evict))
                
        except Exception as e:
            print(f"Cache eviction error: {e}")
