"""
Advanced Cache Manager for Embedding Operations
Provides intelligent caching with multiple strategies and optimization
"""

import asyncio
import json
import time
import hashlib
import pickle
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import logging

from app.common.base_classes import BaseOrchestrationService
from app.utils.performance_monitor import PerformanceMonitor

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    embeddings: List[List[float]]
    model: str
    timestamp: float
    access_count: int
    input_hash: str
    ttl: Optional[int] = None

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    total_size: int
    evictions: int

class CacheManager(BaseOrchestrationService):
    """
    Intelligent cache manager for embedding operations
    Supports multiple caching strategies and optimization techniques
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("cache_manager", config)
        
        # Redis configuration
        self.redis_host = config.get("redis_host", "localhost")
        self.redis_port = config.get("redis_port", 6379)
        self.redis_db = config.get("redis_db", 1)  # Use DB 1 for embeddings cache
        self.redis_password = config.get("redis_password")
        
        # Cache configuration
        self.default_ttl = config.get("default_ttl", 3600)  # 1 hour
        self.max_cache_size = config.get("max_cache_size", 1000000)  # 1M entries
        self.enable_semantic_cache = config.get("enable_semantic_cache", True)
        self.semantic_threshold = config.get("semantic_threshold", 0.95)
        
        # Cache key prefixes
        self.embedding_prefix = "emb:"
        self.semantic_prefix = "sem:"
        self.stats_prefix = "stats:"
        
        self.redis_client: Optional[redis.Redis] = None
        self.performance_monitor = PerformanceMonitor()
        
        # Local statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "evictions": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection and cache structures"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=False,  # Keep binary for pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Initialize cache structures
            await self._initialize_cache_structures()
            
            self._health_status = "healthy"
            self.logger.info("Cache manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache manager: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def _initialize_cache_structures(self):
        """Initialize cache data structures and cleanup"""
        # Initialize stats if they don't exist
        if not await self.redis_client.exists(f"{self.stats_prefix}total_requests"):
            await self.redis_client.mset({
                f"{self.stats_prefix}total_requests": 0,
                f"{self.stats_prefix}cache_hits": 0,
                f"{self.stats_prefix}cache_misses": 0,
                f"{self.stats_prefix}evictions": 0
            })
        
        # Cleanup expired entries (run on startup)
        await self._cleanup_expired_entries()
    
    def _generate_cache_key(self, text: str, model: str, options: Optional[Dict] = None) -> str:
        """Generate consistent cache key for embedding request"""
        content = f"{text}:{model}"
        if options:
            content += f":{json.dumps(options, sort_keys=True)}"
        
        hash_obj = hashlib.sha256(content.encode())
        return f"{self.embedding_prefix}{hash_obj.hexdigest()[:16]}"
    
    def _generate_semantic_key(self, text: str, model: str) -> str:
        """Generate semantic cache key for similarity matching"""
        # Use a simpler hash for semantic matching
        text_normalized = text.lower().strip()
        hash_obj = hashlib.md5(f"{text_normalized}:{model}".encode())
        return f"{self.semantic_prefix}{hash_obj.hexdigest()[:12]}"
    
    async def get_embeddings(self, 
                           text: str, 
                           model: str, 
                           options: Optional[Dict] = None) -> Optional[List[List[float]]]:
        """
        Retrieve embeddings from cache if available
        
        Args:
            text: Input text
            model: Model name
            options: Additional options for cache key generation
            
        Returns:
            Cached embeddings or None if not found
        """
        
        self.stats["total_requests"] += 1
        await self.redis_client.incr(f"{self.stats_prefix}total_requests")
        
        # Try exact match first
        cache_key = self._generate_cache_key(text, model, options)
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                entry = pickle.loads(cached_data)
                
                # Update access count and timestamp
                entry.access_count += 1
                entry.timestamp = time.time()
                
                # Store updated entry
                await self.redis_client.setex(
                    cache_key, 
                    self.default_ttl, 
                    pickle.dumps(entry)
                )
                
                self.stats["cache_hits"] += 1
                await self.redis_client.incr(f"{self.stats_prefix}cache_hits")
                
                self.logger.debug(f"Cache hit for key: {cache_key[:20]}...")
                return entry.embeddings
            
            # Try semantic cache if enabled
            if self.enable_semantic_cache:
                semantic_result = await self._semantic_cache_lookup(text, model)
                if semantic_result:
                    self.stats["cache_hits"] += 1
                    await self.redis_client.incr(f"{self.stats_prefix}cache_hits")
                    return semantic_result
            
            # Cache miss
            self.stats["cache_misses"] += 1
            await self.redis_client.incr(f"{self.stats_prefix}cache_misses")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def _semantic_cache_lookup(self, text: str, model: str) -> Optional[List[List[float]]]:
        """Look for semantically similar cached embeddings"""
        try:
            semantic_key = self._generate_semantic_key(text, model)
            
            # Get potential matches (this is a simplified implementation)
            # In a production system, you'd use vector similarity search
            pattern = f"{self.semantic_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            # For now, we'll do a simple text similarity check
            # This could be enhanced with actual embedding similarity
            for key in keys[:10]:  # Limit search to avoid performance issues
                try:
                    cached_data = await self.redis_client.get(key)
                    if cached_data:
                        entry = pickle.loads(cached_data)
                        # Simple semantic check (could be improved)
                        if self._text_similarity(text, entry.input_hash) > self.semantic_threshold:
                            self.logger.debug(f"Semantic cache hit for: {text[:50]}...")
                            return entry.embeddings
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Semantic cache lookup error: {e}")
            return None
    
    def _text_similarity(self, text1: str, text2_hash: str) -> float:
        """Simple text similarity calculation (placeholder for more sophisticated methods)"""
        # This is a very basic implementation
        # In production, you'd want proper semantic similarity
        text1_normalized = text1.lower().strip()
        text1_hash = hashlib.md5(text1_normalized.encode()).hexdigest()
        
        # Simple character-level similarity
        common_chars = sum(1 for c1, c2 in zip(text1_hash, text2_hash) if c1 == c2)
        return common_chars / len(text1_hash)
    
    async def store_embeddings(self,
                             text: str,
                             model: str,
                             embeddings: List[List[float]],
                             options: Optional[Dict] = None,
                             ttl: Optional[int] = None) -> bool:
        """
        Store embeddings in cache
        
        Args:
            text: Input text
            model: Model name
            embeddings: Generated embeddings
            options: Additional options used for generation
            ttl: Time to live (uses default if None)
            
        Returns:
            True if stored successfully
        """
        
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            cache_key = self._generate_cache_key(text, model, options)
            
            entry = CacheEntry(
                embeddings=embeddings,
                model=model,
                timestamp=time.time(),
                access_count=1,
                input_hash=hashlib.md5(text.encode()).hexdigest(),
                ttl=ttl
            )
            
            # Store main cache entry
            await self.redis_client.setex(
                cache_key,
                ttl,
                pickle.dumps(entry)
            )
            
            # Store semantic cache entry if enabled
            if self.enable_semantic_cache:
                semantic_key = self._generate_semantic_key(text, model)
                await self.redis_client.setex(
                    semantic_key,
                    ttl,
                    pickle.dumps(entry)
                )
            
            # Check cache size and evict if necessary
            await self._manage_cache_size()
            
            self.logger.debug(f"Stored embeddings for key: {cache_key[:20]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache storage error: {e}")
            return False
    
    async def _manage_cache_size(self):
        """Manage cache size by evicting old entries if necessary"""
        try:
            # Get current cache size
            cache_size = await self.redis_client.dbsize()
            
            if cache_size > self.max_cache_size:
                # Get all embedding keys
                pattern = f"{self.embedding_prefix}*"
                keys = await self.redis_client.keys(pattern)
                
                # Sort by access time (oldest first) - this is approximate
                # In production, you'd want a more sophisticated LRU implementation
                entries_to_remove = len(keys) - int(self.max_cache_size * 0.8)
                
                if entries_to_remove > 0:
                    # Remove oldest entries
                    await self.redis_client.delete(*keys[:entries_to_remove])
                    
                    self.stats["evictions"] += entries_to_remove
                    await self.redis_client.incrby(
                        f"{self.stats_prefix}evictions", 
                        entries_to_remove
                    )
                    
                    self.logger.info(f"Evicted {entries_to_remove} cache entries")
        
        except Exception as e:
            self.logger.error(f"Cache size management error: {e}")
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        try:
            # Redis handles TTL automatically, but we can do additional cleanup
            # This is mainly for maintenance and statistics
            
            pattern = f"{self.embedding_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            expired_count = 0
            for key in keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    expired_count += 1
            
            if expired_count > 0:
                self.logger.info(f"Found {expired_count} expired cache entries")
        
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
    
    async def get_cache_stats(self) -> CacheStats:
        """Get comprehensive cache statistics"""
        try:
            # Get Redis stats
            total_requests = int(await self.redis_client.get(f"{self.stats_prefix}total_requests") or 0)
            cache_hits = int(await self.redis_client.get(f"{self.stats_prefix}cache_hits") or 0)
            cache_misses = int(await self.redis_client.get(f"{self.stats_prefix}cache_misses") or 0)
            evictions = int(await self.redis_client.get(f"{self.stats_prefix}evictions") or 0)
            
            # Calculate hit rate
            hit_rate = cache_hits / max(total_requests, 1)
            
            # Get cache size
            cache_size = await self.redis_client.dbsize()
            
            return CacheStats(
                total_requests=total_requests,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                hit_rate=hit_rate,
                total_size=cache_size,
                evictions=evictions
            )
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return CacheStats(0, 0, 0, 0.0, 0, 0)
    
    async def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries
        
        Args:
            pattern: Pattern to match (clears all embedding cache if None)
            
        Returns:
            Number of entries removed
        """
        try:
            if pattern is None:
                pattern = f"{self.embedding_prefix}*"
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                removed = await self.redis_client.delete(*keys)
                self.logger.info(f"Cleared {removed} cache entries with pattern: {pattern}")
                return removed
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for cache manager"""
        try:
            # Test Redis connectivity
            await self.redis_client.ping()
            redis_healthy = True
            
            # Get cache statistics
            stats = await self.get_cache_stats()
            
            # Test cache operations
            test_key = "health_check_test"
            await self.redis_client.setex(test_key, 10, "test_value")
            test_value = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            cache_ops_healthy = test_value == b"test_value"
            
            return {
                "status": "healthy" if redis_healthy and cache_ops_healthy else "unhealthy",
                "redis_connection": redis_healthy,
                "cache_operations": cache_ops_healthy,
                "cache_stats": asdict(stats),
                "config": {
                    "redis_host": self.redis_host,
                    "redis_port": self.redis_port,
                    "redis_db": self.redis_db,
                    "default_ttl": self.default_ttl,
                    "max_cache_size": self.max_cache_size,
                    "semantic_cache_enabled": self.enable_semantic_cache
                }
            }
            
        except Exception as e:
            self.logger.error(f"Cache health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of cache manager"""
        if self.redis_client:
            await self.redis_client.close()
        await super().shutdown()
        self.logger.info("Cache manager shut down gracefully")
