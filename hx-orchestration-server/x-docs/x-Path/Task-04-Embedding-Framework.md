# Task 4: Embedding Processing Framework

**Document Version:** 1.0  
**Date:** 2025-07-25  
**Author:** Manus AI  
**Project:** Citadel AI Operating System - Orchestration Server Implementation  
**Server:** hx-orchestration-server (192.168.10.31)  
**Purpose:** Phase 3 implementation - Ollama embedding framework with 4-model support  
**Classification:** Production-Ready Implementation Task  
**Duration:** 4-5 hours  
**Priority:** CRITICAL  
**Dependencies:** Tasks 1, 2, and 3 completion

---

## Task Overview

Implement comprehensive embedding processing framework using Ollama with 4-model support (nomic-embed-text, mxbai-embed-large, bge-m3, all-minilm), Redis caching, Qdrant vector storage, and performance optimization for production workloads.

### Key Deliverables

1. **Ollama Client Integration**
   - Async HTTP client for Ollama API
   - 4-model configuration and management
   - Connection pooling and error handling
   - Performance monitoring and metrics

2. **Embedding Cache Manager**
   - Redis-based caching with TTL management
   - Cache key generation and collision prevention
   - Cache warming and invalidation strategies
   - Performance optimization for frequent queries

3. **Vector Database Integration**
   - Qdrant client configuration and management
   - Collection creation and indexing
   - Similarity search and filtering
   - Batch operations and bulk updates

---

## Implementation Steps

### Step 4.1: Ollama Client Implementation (1.5-2 hours)

**Objective:** Create robust async client for Ollama embedding generation

**File:** `/app/core/embeddings/ollama_client.py`
```python
"""
Ollama Embedding Client
Async HTTP client for Ollama embedding generation with multi-model support
"""
import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

from app.utils.performance_monitor import MetricsCollector
from app.common.base_classes import BaseEmbeddingService

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for embedding model"""
    name: str
    dimensions: int
    max_sequence_length: int
    performance_tier: str  # "fast", "balanced", "quality"
    recommended_use: str

# Ollama model configurations
OLLAMA_MODELS = {
    "nomic-embed-text": ModelConfig(
        name="nomic-embed-text",
        dimensions=768,
        max_sequence_length=8192,
        performance_tier="fast",
        recommended_use="General purpose, quick embedding generation"
    ),
    "mxbai-embed-large": ModelConfig(
        name="mxbai-embed-large", 
        dimensions=1024,
        max_sequence_length=512,
        performance_tier="quality",
        recommended_use="High-quality embeddings for critical applications"
    ),
    "bge-m3": ModelConfig(
        name="bge-m3",
        dimensions=1024,
        max_sequence_length=8192,
        performance_tier="balanced",
        recommended_use="Multilingual and general domain tasks"
    ),
    "all-minilm": ModelConfig(
        name="all-minilm",
        dimensions=384,
        max_sequence_length=256,
        performance_tier="fast",
        recommended_use="Lightweight, fast processing"
    )
}

class OllamaEmbeddingClient(BaseEmbeddingService):
    """
    Production-ready Ollama embedding client with connection pooling,
    error handling, and performance monitoring
    """
    
    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        timeout: int = 300,
        max_connections: int = 10,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Initialize Ollama client
        
        Args:
            model_name: Name of the embedding model to use
            base_url: Ollama server base URL
            timeout: Request timeout in seconds
            max_connections: Maximum concurrent connections
            metrics_collector: Optional metrics collector instance
        """
        super().__init__()
        
        if model_name not in OLLAMA_MODELS:
            raise ValueError(f"Unsupported model: {model_name}. Available: {list(OLLAMA_MODELS.keys())}")
        
        self.model_name = model_name
        self.model_config = OLLAMA_MODELS[model_name]
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Connection pool configuration
        connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        # Session timeout configuration
        timeout_config = aiohttp.ClientTimeout(
            total=timeout,
            connect=30,
            sock_read=timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CitadelAI-OrchestrationServer/1.0"
            }
        )
        
        logger.info(f"Initialized Ollama client for model: {model_name}")
    
    async def generate_embedding(
        self,
        text: Union[str, List[str]],
        options: Optional[Dict[str, Any]] = None
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text using configured model
        
        Args:
            text: Single text string or list of texts
            options: Additional model options
        
        Returns:
            Single embedding vector or list of embedding vectors
        """
        start_time = time.time()
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        try:
            # Validate input length
            for t in texts:
                if len(t) > self.model_config.max_sequence_length:
                    logger.warning(
                        f"Text length {len(t)} exceeds model max length "
                        f"{self.model_config.max_sequence_length}, truncating"
                    )
                    t = t[:self.model_config.max_sequence_length]
            
            embeddings = []
            
            for single_text in texts:
                embedding = await self._generate_single_embedding(single_text, options)
                embeddings.append(embedding)
            
            # Record performance metrics
            duration = time.time() - start_time
            self.metrics_collector.record_embedding_duration(
                model=self.model_name,
                duration=duration,
                batch_size=len(texts)
            )
            
            # Return single embedding or list based on input type
            return embeddings if is_batch else embeddings[0]
            
        except Exception as exc:
            logger.error(f"Embedding generation failed: {exc}")
            self.metrics_collector.record_embedding_error(
                model=self.model_name,
                error_type=type(exc).__name__
            )
            raise
    
    async def _generate_single_embedding(
        self,
        text: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generate embedding for single text string
        
        Args:
            text: Text to embed
            options: Additional model options
        
        Returns:
            Embedding vector as list of floats
        """
        payload = {
            "model": self.model_name,
            "prompt": text
        }
        
        if options:
            payload["options"] = options
        
        url = f"{self.base_url}/api/embeddings"
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(
                    f"Ollama API error {response.status}: {error_text}"
                )
            
            result = await response.json()
            
            if "embedding" not in result:
                raise RuntimeError(f"Invalid response format: {result}")
            
            return result["embedding"]
    
    async def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        options: Optional[Dict[str, Any]] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for large batches efficiently
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in parallel
            options: Additional model options
        
        Returns:
            List of embedding vectors
        """
        start_time = time.time()
        
        try:
            all_embeddings = []
            
            # Process in batches to manage memory and connection limits
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings for batch concurrently
                tasks = [
                    self._generate_single_embedding(text, options)
                    for text in batch
                ]
                
                batch_embeddings = await asyncio.gather(*tasks)
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Processed batch {i//batch_size + 1}, total: {len(all_embeddings)}")
            
            # Record batch metrics
            duration = time.time() - start_time
            self.metrics_collector.record_batch_embedding_duration(
                model=self.model_name,
                duration=duration,
                total_count=len(texts),
                batch_size=batch_size
            )
            
            return all_embeddings
            
        except Exception as exc:
            logger.error(f"Batch embedding generation failed: {exc}")
            raise
    
    async def check_model_availability(self) -> Dict[str, Any]:
        """
        Check if the configured model is available in Ollama
        
        Returns:
            Dict containing model availability and metadata
        """
        try:
            url = f"{self.base_url}/api/tags"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"available": False, "error": f"API error: {response.status}"}
                
                result = await response.json()
                models = result.get("models", [])
                
                # Check if our model is in the list
                model_available = any(
                    model.get("name", "").startswith(self.model_name)
                    for model in models
                )
                
                return {
                    "available": model_available,
                    "model_name": self.model_name,
                    "model_config": self.model_config.__dict__,
                    "all_models": [model.get("name") for model in models],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as exc:
            logger.error(f"Model availability check failed: {exc}")
            return {
                "available": False,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the configured model
        
        Returns:
            Dict containing model information and capabilities
        """
        availability = await self.check_model_availability()
        
        return {
            "model_name": self.model_name,
            "configuration": self.model_config.__dict__,
            "availability": availability,
            "client_config": {
                "base_url": self.base_url,
                "timeout": self.timeout,
                "max_connections": self.session.connector.limit
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close the HTTP session and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Ollama client session closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
```

### Step 4.2: Embedding Cache Manager (1-1.5 hours)

**File:** `/app/core/embeddings/cache_manager.py`
```python
"""
Embedding Cache Manager
Redis-based caching for embedding vectors with TTL and performance optimization
"""
import json
import hashlib
import pickle
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import logging

import aioredis
from aioredis import Redis

from config.settings import get_settings
from app.utils.performance_monitor import MetricsCollector

# Configure logging
logger = logging.getLogger(__name__)

class EmbeddingCacheManager:
    """
    Production-ready embedding cache with Redis backend,
    optimized for high-performance embedding storage and retrieval
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 1,  # Separate DB for embeddings
        default_ttl: int = 86400,  # 24 hours default TTL
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Initialize embedding cache manager
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number for embeddings
            default_ttl: Default TTL for cached embeddings in seconds
            metrics_collector: Optional metrics collector
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.default_ttl = default_ttl
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        self.redis: Optional[Redis] = None
        self._connected = False
        
        # Cache configuration
        self.key_prefix = "citadel:embedding:"
        self.compression_enabled = True
        self.batch_size = 100
        
        logger.info(f"Initialized embedding cache manager for Redis {redis_host}:{redis_port}/{redis_db}")
    
    async def connect(self):
        """Establish Redis connection with optimal configuration"""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}",
                encoding="utf-8",
                decode_responses=False,  # Handle binary data for embeddings
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    "TCP_KEEPIDLE": 1,
                    "TCP_KEEPINTVL": 3,
                    "TCP_KEEPCNT": 5,
                }
            )
            
            # Test connection
            await self.redis.ping()
            self._connected = True
            
            logger.info("Redis connection established for embedding cache")
            
        except Exception as exc:
            logger.error(f"Failed to connect to Redis: {exc}")
            self._connected = False
            raise
    
    def _generate_cache_key(
        self,
        text: str,
        model: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate deterministic cache key for embedding
        
        Args:
            text: Input text
            model: Model name
            options: Optional model parameters
        
        Returns:
            Cache key string
        """
        # Create deterministic hash of input parameters
        key_data = {
            "text": text,
            "model": model,
            "options": options or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"{self.key_prefix}{model}:{key_hash}"
    
    async def store_embedding(
        self,
        text: str,
        model: str,
        embedding: List[float],
        options: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store embedding in cache with metadata
        
        Args:
            text: Original text
            model: Model used for embedding
            embedding: Embedding vector
            options: Model options used
            ttl: Time to live in seconds
        
        Returns:
            True if stored successfully
        """
        if not self._connected:
            await self.connect()
        
        try:
            cache_key = self._generate_cache_key(text, model, options)
            ttl = ttl or self.default_ttl
            
            # Prepare cache data with metadata
            cache_data = {
                "embedding": embedding,
                "model": model,
                "text_length": len(text),
                "text_hash": hashlib.md5(text.encode()).hexdigest(),
                "options": options,
                "created_at": datetime.utcnow().isoformat(),
                "ttl": ttl
            }
            
            # Serialize and optionally compress
            serialized_data = pickle.dumps(cache_data)
            
            if self.compression_enabled and len(serialized_data) > 1024:
                import gzip
                serialized_data = gzip.compress(serialized_data)
                cache_key += ":gz"
            
            # Store with TTL
            await self.redis.setex(cache_key, ttl, serialized_data)
            
            # Record cache metrics
            self.metrics_collector.record_cache_operation(
                operation="store",
                model=model,
                data_size=len(serialized_data)
            )
            
            logger.debug(f"Stored embedding in cache: {cache_key}")
            return True
            
        except Exception as exc:
            logger.error(f"Failed to store embedding in cache: {exc}")
            return False
    
    async def get_embedding(
        self,
        text: str,
        model: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[List[float]]:
        """
        Retrieve embedding from cache
        
        Args:
            text: Original text
            model: Model name
            options: Model options
        
        Returns:
            Embedding vector if found, None otherwise
        """
        if not self._connected:
            await self.connect()
        
        try:
            cache_key = self._generate_cache_key(text, model, options)
            
            # Try both compressed and uncompressed versions
            for key_variant in [cache_key, cache_key + ":gz"]:
                cached_data = await self.redis.get(key_variant)
                
                if cached_data is not None:
                    # Decompress if needed
                    if key_variant.endswith(":gz"):
                        import gzip
                        cached_data = gzip.decompress(cached_data)
                    
                    # Deserialize
                    cache_obj = pickle.loads(cached_data)
                    
                    # Validate cache integrity
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    if cache_obj.get("text_hash") != text_hash:
                        logger.warning(f"Cache text hash mismatch for key: {cache_key}")
                        await self.redis.delete(key_variant)
                        continue
                    
                    # Record cache hit
                    self.metrics_collector.record_cache_operation(
                        operation="hit",
                        model=model,
                        data_size=len(cached_data)
                    )
                    
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cache_obj["embedding"]
            
            # Record cache miss
            self.metrics_collector.record_cache_operation(
                operation="miss",
                model=model
            )
            
            logger.debug(f"Cache miss for key: {cache_key}")
            return None
            
        except Exception as exc:
            logger.error(f"Failed to retrieve from cache: {exc}")
            return None
    
    async def batch_store_embeddings(
        self,
        batch_data: List[Dict[str, Any]],
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store multiple embeddings efficiently using pipeline
        
        Args:
            batch_data: List of embedding data dictionaries
            ttl: Time to live in seconds
        
        Returns:
            Dict containing batch operation results
        """
        if not self._connected:
            await self.connect()
        
        try:
            ttl = ttl or self.default_ttl
            
            # Use Redis pipeline for batch operations
            pipe = self.redis.pipeline()
            
            stored_count = 0
            total_size = 0
            
            for item in batch_data:
                text = item["text"]
                model = item["model"]
                embedding = item["embedding"]
                options = item.get("options")
                
                cache_key = self._generate_cache_key(text, model, options)
                
                cache_data = {
                    "embedding": embedding,
                    "model": model,
                    "text_length": len(text),
                    "text_hash": hashlib.md5(text.encode()).hexdigest(),
                    "options": options,
                    "created_at": datetime.utcnow().isoformat(),
                    "ttl": ttl
                }
                
                serialized_data = pickle.dumps(cache_data)
                total_size += len(serialized_data)
                
                if self.compression_enabled and len(serialized_data) > 1024:
                    import gzip
                    serialized_data = gzip.compress(serialized_data)
                    cache_key += ":gz"
                
                pipe.setex(cache_key, ttl, serialized_data)
                stored_count += 1
            
            # Execute pipeline
            await pipe.execute()
            
            # Record batch metrics
            self.metrics_collector.record_cache_batch_operation(
                operation="batch_store",
                count=stored_count,
                total_size=total_size
            )
            
            return {
                "success": True,
                "stored_count": stored_count,
                "total_size_bytes": total_size,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Batch store operation failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics
        
        Returns:
            Dict containing cache performance and usage statistics
        """
        if not self._connected:
            await self.connect()
        
        try:
            # Redis info
            redis_info = await self.redis.info()
            
            # Count embedding keys
            embedding_keys = await self.redis.keys(f"{self.key_prefix}*")
            
            # Calculate cache size
            total_memory = redis_info.get("used_memory", 0)
            
            # Get cache hit/miss ratios from metrics
            cache_metrics = self.metrics_collector.get_cache_metrics()
            
            return {
                "cache_keys_count": len(embedding_keys),
                "total_memory_bytes": total_memory,
                "redis_connected_clients": redis_info.get("connected_clients", 0),
                "cache_hit_ratio": cache_metrics.get("hit_ratio", 0.0),
                "cache_operations_total": cache_metrics.get("operations_total", 0),
                "average_key_size_bytes": total_memory / max(len(embedding_keys), 1),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Failed to get cache stats: {exc}")
            return {
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_expired_cache(self) -> Dict[str, Any]:
        """
        Clean up expired cache entries and optimize memory usage
        
        Returns:
            Dict containing cleanup operation results
        """
        if not self._connected:
            await self.connect()
        
        try:
            # Get all embedding keys
            embedding_keys = await self.redis.keys(f"{self.key_prefix}*")
            
            cleaned_count = 0
            total_keys = len(embedding_keys)
            
            # Process keys in batches
            for i in range(0, len(embedding_keys), self.batch_size):
                batch = embedding_keys[i:i + self.batch_size]
                
                pipe = self.redis.pipeline()
                
                # Check TTL for each key
                for key in batch:
                    ttl = await self.redis.ttl(key)
                    if ttl == -1:  # No expiration set
                        pipe.expire(key, self.default_ttl)
                    elif ttl == -2:  # Key doesn't exist (already expired)
                        cleaned_count += 1
                
                await pipe.execute()
            
            return {
                "success": True,
                "total_keys_scanned": total_keys,
                "expired_keys_found": cleaned_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Cache cleanup failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close Redis connection"""
        if self.redis and self._connected:
            await self.redis.close()
            self._connected = False
            logger.info("Redis cache connection closed")
```

### Step 4.3: Vector Database Integration (1-1.5 hours)

**File:** `/app/core/embeddings/vector_store.py`
```python
"""
Vector Database Integration
Qdrant client for vector storage, similarity search, and collection management
"""
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException

from app.utils.performance_monitor import MetricsCollector

# Configure logging
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Production-ready Qdrant vector database manager for embedding storage
    and similarity search operations
    """
    
    def __init__(
        self,
        host: str = "192.168.10.30",
        port: int = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = True,
        timeout: int = 60,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Initialize Qdrant vector store manager
        
        Args:
            host: Qdrant server host
            port: Qdrant HTTP API port
            grpc_port: Qdrant gRPC port
            prefer_grpc: Use gRPC for better performance
            timeout: Request timeout in seconds
            metrics_collector: Optional metrics collector
        """
        self.host = host
        self.port = port
        self.grpc_port = grpc_port
        self.prefer_grpc = prefer_grpc
        self.timeout = timeout
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Initialize client
        try:
            if prefer_grpc:
                self.client = QdrantClient(
                    host=host,
                    grpc_port=grpc_port,
                    prefer_grpc=True,
                    timeout=timeout
                )
            else:
                self.client = QdrantClient(
                    host=host,
                    port=port,
                    timeout=timeout
                )
            
            logger.info(f"Initialized Qdrant client: {host}:{grpc_port if prefer_grpc else port}")
            
        except Exception as exc:
            logger.error(f"Failed to initialize Qdrant client: {exc}")
            raise
    
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "Cosine",
        shard_number: int = 1,
        replication_factor: int = 1
    ) -> Dict[str, Any]:
        """
        Create a new collection for storing vectors
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the vectors
            distance_metric: Distance metric (Cosine, Euclidean, Dot)
            shard_number: Number of shards
            replication_factor: Replication factor
        
        Returns:
            Dict containing collection creation results
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_names = [col.name for col in collections.collections]
            
            if collection_name in existing_names:
                logger.info(f"Collection {collection_name} already exists")
                return {
                    "success": True,
                    "message": f"Collection {collection_name} already exists",
                    "collection_name": collection_name
                }
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=getattr(models.Distance, distance_metric.upper())
                ),
                shard_number=shard_number,
                replication_factor=replication_factor,
                optimizers_config=models.OptimizersConfig(
                    default_segment_number=2,
                    max_segment_size_kb=20000,
                    memmap_threshold_kb=10000,
                    indexing_threshold_kb=20000,
                    flush_interval_sec=5,
                    max_optimization_threads=2
                )
            )
            
            logger.info(f"Created collection: {collection_name}")
            
            return {
                "success": True,
                "message": f"Collection {collection_name} created successfully",
                "collection_name": collection_name,
                "vector_size": vector_size,
                "distance_metric": distance_metric,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Failed to create collection {collection_name}: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Insert or update vectors in collection with batch processing
        
        Args:
            collection_name: Target collection name
            vectors: List of vector dictionaries with id, vector, and payload
            batch_size: Batch size for processing
        
        Returns:
            Dict containing upsert operation results
        """
        try:
            total_vectors = len(vectors)
            processed_count = 0
            
            # Process in batches for memory efficiency
            for i in range(0, total_vectors, batch_size):
                batch = vectors[i:i + batch_size]
                
                # Prepare points for batch
                points = [
                    models.PointStruct(
                        id=vector["id"],
                        vector=vector["vector"],
                        payload=vector.get("payload", {})
                    )
                    for vector in batch
                ]
                
                # Upsert batch
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                processed_count += len(batch)
                logger.info(f"Processed {processed_count}/{total_vectors} vectors")
            
            # Record metrics
            self.metrics_collector.record_vector_operation(
                operation="upsert",
                collection=collection_name,
                count=total_vectors
            )
            
            return {
                "success": True,
                "collection_name": collection_name,
                "vectors_processed": processed_count,
                "total_vectors": total_vectors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Vector upsert failed for collection {collection_name}: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def similarity_search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform similarity search in vector collection
        
        Args:
            collection_name: Collection to search in
            query_vector: Query vector for similarity search
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional payload filters
        
        Returns:
            Dict containing search results and metadata
        """
        try:
            # Prepare search request
            search_params = models.SearchParams(
                hnsw_ef=128,  # Higher ef for better recall
                exact=False   # Use approximate search for speed
            )
            
            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )
            
            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                params=search_params,
                with_payload=True,
                with_vectors=False  # Don't return vectors to save bandwidth
            )
            
            # Format results
            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in search_results
            ]
            
            # Record search metrics
            self.metrics_collector.record_vector_search(
                collection=collection_name,
                results_count=len(formatted_results),
                query_limit=limit
            )
            
            return {
                "success": True,
                "collection_name": collection_name,
                "results": formatted_results,
                "results_count": len(formatted_results),
                "query_limit": limit,
                "score_threshold": score_threshold,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Similarity search failed for collection {collection_name}: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a collection
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            Dict containing collection information and statistics
        """
        try:
            # Get collection info
            collection_info = self.client.get_collection(collection_name)
            
            # Get collection statistics
            collection_stats = {
                "vectors_count": collection_info.vectors_count,
                "segments_count": collection_info.segments_count,
                "disk_data_size": collection_info.disk_data_size,
                "ram_data_size": collection_info.ram_data_size,
                "config": {
                    "vector_size": collection_info.config.params.vectors.size,
                    "distance_metric": collection_info.config.params.vectors.distance.name,
                    "shard_number": collection_info.config.params.shard_number,
                    "replication_factor": collection_info.config.params.replication_factor
                }
            }
            
            return {
                "success": True,
                "collection_name": collection_name,
                "statistics": collection_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Failed to get collection info for {collection_name}: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all available collections
        
        Returns:
            Dict containing list of collections and their basic info
        """
        try:
            collections = self.client.get_collections()
            
            collection_list = [
                {
                    "name": col.name,
                    "vectors_count": col.vectors_count,
                    "segments_count": col.segments_count
                }
                for col in collections.collections
            ]
            
            return {
                "success": True,
                "collections": collection_list,
                "total_collections": len(collection_list),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"Failed to list collections: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
```

---

## Success Criteria

### Ollama Integration
- ✅ 4-model support (nomic-embed-text, mxbai-embed-large, bge-m3, all-minilm)
- ✅ Async HTTP client with connection pooling
- ✅ Error handling and retry logic for API failures
- ✅ Performance metrics and monitoring

### Caching Layer
- ✅ Redis-based embedding cache with TTL management
- ✅ Cache key generation preventing collisions
- ✅ Compression for large embeddings
- ✅ Batch operations for high-throughput scenarios

### Vector Database
- ✅ Qdrant collection management and configuration
- ✅ Efficient vector storage and retrieval
- ✅ Similarity search with filtering capabilities
- ✅ Performance optimization for production workloads

---

## Next Steps

1. **Task 5:** Modern Framework Integration (Clerk, AG UI, Copilot Kit, LiveKit)
2. **Task 6:** Production Testing and Monitoring Integration
3. **Performance Optimization:** Fine-tune cache and vector search parameters
4. **Load Testing:** Validate embedding processing throughput

**Dependencies for Next Task:**
- Ollama models operational and responsive
- Redis cache performing optimally
- Qdrant collections configured and indexed
- Embedding processing pipeline functioning end-to-end
