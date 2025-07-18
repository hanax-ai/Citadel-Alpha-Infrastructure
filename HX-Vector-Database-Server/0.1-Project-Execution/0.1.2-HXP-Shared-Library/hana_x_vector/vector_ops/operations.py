"""
Vector Operations Manager
========================

Core vector operations manager for Qdrant database operations.
Handles vector insertion, search, and batch operations with performance optimization.
"""

from typing import List, Dict, Any, Optional, Union
import asyncio
import time
import numpy as np
from ..qdrant.client import QdrantClient
from ..external_models.integration_patterns import IntegrationPatternManager
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError
from ..utils.validators import validate_vector_data, validate_collection_name
from .search import SearchEngine
from .batch import BatchProcessor
from .cache import CacheManager


class VectorOperationsManager:
    """
    Core vector operations manager for Qdrant database operations.
    Handles vector insertion, search, and batch operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.qdrant_client = QdrantClient(config)
        self.search_engine = SearchEngine(config)
        self.batch_processor = BatchProcessor(config)
        self.cache_manager = CacheManager(config)
        self.integration_patterns = IntegrationPatternManager(config)
        self.metrics = MetricsCollector()
        
        # Performance settings
        self.default_batch_size = config.get("vector_ops", {}).get("batch_size", 1000)
        self.max_retries = config.get("vector_ops", {}).get("max_retries", 3)
        self.retry_delay = config.get("vector_ops", {}).get("retry_delay", 1.0)
        
        # Collection configurations for different AI models
        self.model_collections = {
            'mixtral_embeddings': {'dimensions': 4096, 'distance': 'Cosine'},
            'hermes_embeddings': {'dimensions': 4096, 'distance': 'Cosine'},
            'llama_embeddings': {'dimensions': 4096, 'distance': 'Cosine'},
            'qwen_embeddings': {'dimensions': 4096, 'distance': 'Cosine'},
            'phi_embeddings': {'dimensions': 2560, 'distance': 'Cosine'},
            'gemma_embeddings': {'dimensions': 2048, 'distance': 'Cosine'},
            'deepseek_embeddings': {'dimensions': 4096, 'distance': 'Cosine'},
            'claude_embeddings': {'dimensions': 1536, 'distance': 'Cosine'},
            'general_embeddings': {'dimensions': 1536, 'distance': 'Cosine'}
        }
    
    async def startup(self):
        """Initialize vector operations manager."""
        await self.qdrant_client.startup()
        await self.search_engine.startup()
        await self.batch_processor.startup()
        await self.cache_manager.startup()
        await self.integration_patterns.startup()
        
        # Initialize default collections
        await self._initialize_collections()
    
    async def shutdown(self):
        """Cleanup vector operations manager."""
        await self.qdrant_client.shutdown()
        await self.search_engine.shutdown()
        await self.batch_processor.shutdown()
        await self.cache_manager.shutdown()
        await self.integration_patterns.shutdown()
    
    async def insert_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Insert vectors into a collection with batch processing.
        
        Args:
            collection_name: Name of the collection
            vectors: List of vector data with metadata
            batch_size: Batch size for insertion
            
        Returns:
            Dict with insertion results and metrics
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            validate_collection_name(collection_name)
            validate_vector_data(vectors)
            
            # Use default batch size if not specified
            if batch_size is None:
                batch_size = self.default_batch_size
            
            # Ensure collection exists
            await self._ensure_collection_exists(collection_name)
            
            # Process insertion with retries
            result = await self._insert_with_retries(
                collection_name, vectors, batch_size
            )
            
            # Update metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("vector_insert_duration", duration)
            self.metrics.increment_counter("vectors_inserted_total", len(vectors))
            
            # Invalidate cache for this collection
            await self.cache_manager.invalidate_collection_cache(collection_name)
            
            return {
                "inserted_count": result["inserted_count"],
                "duration": duration,
                "batch_count": result["batch_count"],
                "collection": collection_name
            }
            
        except Exception as e:
            self.metrics.increment_counter("vector_insert_errors")
            raise VectorOperationError(f"Vector insertion failed: {str(e)}")
    
    async def similarity_search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform similarity search in a collection.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector for similarity search
            limit: Maximum number of results
            filters: Metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            Dict with search results and metrics
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            validate_collection_name(collection_name)
            if not query_vector:
                raise VectorOperationError("Query vector cannot be empty")
            
            # Check cache first
            cache_key = self.cache_manager.generate_search_cache_key(
                collection_name, query_vector, limit, filters, score_threshold
            )
            cached_result = await self.cache_manager.get_cached_search(cache_key)
            
            if cached_result:
                self.metrics.increment_counter("search_cache_hits")
                return cached_result
            
            # Perform search using search engine
            result = await self.search_engine.similarity_search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                filters=filters,
                score_threshold=score_threshold
            )
            
            # Update metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("vector_search_duration", duration)
            self.metrics.increment_counter("vector_searches_total")
            
            # Cache the result
            search_result = {
                "results": result["results"],
                "duration": duration,
                "collection": collection_name,
                "count": len(result["results"])
            }
            
            await self.cache_manager.cache_search_result(cache_key, search_result)
            
            return search_result
            
        except Exception as e:
            self.metrics.increment_counter("vector_search_errors")
            raise VectorOperationError(f"Vector search failed: {str(e)}")
    
    async def update_vector(
        self,
        collection_name: str,
        vector_id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a vector in a collection.
        
        Args:
            collection_name: Name of the collection
            vector_id: ID of the vector to update
            vector: New vector data (optional)
            metadata: New metadata (optional)
            
        Returns:
            Dict with update results
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            validate_collection_name(collection_name)
            if not vector_id:
                raise VectorOperationError("Vector ID cannot be empty")
            
            # Perform update
            result = await self.qdrant_client.update_vector(
                collection_name=collection_name,
                vector_id=vector_id,
                vector=vector,
                metadata=metadata
            )
            
            # Update metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("vector_update_duration", duration)
            self.metrics.increment_counter("vectors_updated_total")
            
            # Invalidate cache for this collection
            await self.cache_manager.invalidate_collection_cache(collection_name)
            
            return {
                "updated": result["updated"],
                "duration": duration,
                "vector_id": vector_id,
                "collection": collection_name
            }
            
        except Exception as e:
            self.metrics.increment_counter("vector_update_errors")
            raise VectorOperationError(f"Vector update failed: {str(e)}")
    
    async def delete_vector(
        self,
        collection_name: str,
        vector_id: str
    ) -> Dict[str, Any]:
        """
        Delete a vector from a collection.
        
        Args:
            collection_name: Name of the collection
            vector_id: ID of the vector to delete
            
        Returns:
            Dict with deletion results
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            validate_collection_name(collection_name)
            if not vector_id:
                raise VectorOperationError("Vector ID cannot be empty")
            
            # Perform deletion
            result = await self.qdrant_client.delete_vector(
                collection_name=collection_name,
                vector_id=vector_id
            )
            
            # Update metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("vector_delete_duration", duration)
            self.metrics.increment_counter("vectors_deleted_total")
            
            # Invalidate cache for this collection
            await self.cache_manager.invalidate_collection_cache(collection_name)
            
            return {
                "deleted": result["deleted"],
                "duration": duration,
                "vector_id": vector_id,
                "collection": collection_name
            }
            
        except Exception as e:
            self.metrics.increment_counter("vector_delete_errors")
            raise VectorOperationError(f"Vector deletion failed: {str(e)}")
    
    async def get_vector(
        self,
        collection_name: str,
        vector_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific vector by ID.
        
        Args:
            collection_name: Name of the collection
            vector_id: ID of the vector to retrieve
            
        Returns:
            Dict with vector data
        """
        try:
            # Validate inputs
            validate_collection_name(collection_name)
            if not vector_id:
                raise VectorOperationError("Vector ID cannot be empty")
            
            # Get vector from Qdrant
            result = await self.qdrant_client.get_vector(
                collection_name=collection_name,
                vector_id=vector_id
            )
            
            self.metrics.increment_counter("vector_retrievals_total")
            
            return result
            
        except Exception as e:
            self.metrics.increment_counter("vector_retrieval_errors")
            raise VectorOperationError(f"Vector retrieval failed: {str(e)}")
    
    async def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: str = "Cosine",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new vector collection.
        
        Args:
            name: Collection name
            vector_size: Vector dimensions
            distance: Distance metric
            config: Additional configuration
            
        Returns:
            Dict with creation results
        """
        try:
            # Validate inputs
            validate_collection_name(name)
            if vector_size <= 0:
                raise VectorOperationError("Vector size must be positive")
            
            # Create collection
            result = await self.qdrant_client.create_collection(
                name=name,
                vector_size=vector_size,
                distance=distance,
                config=config
            )
            
            self.metrics.increment_counter("collections_created_total")
            
            return result
            
        except Exception as e:
            self.metrics.increment_counter("collection_create_errors")
            raise VectorOperationError(f"Collection creation failed: {str(e)}")
    
    async def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            Dict with deletion results
        """
        try:
            # Validate inputs
            validate_collection_name(name)
            
            # Delete collection
            result = await self.qdrant_client.delete_collection(name)
            
            # Invalidate all cache for this collection
            await self.cache_manager.invalidate_collection_cache(name)
            
            self.metrics.increment_counter("collections_deleted_total")
            
            return result
            
        except Exception as e:
            self.metrics.increment_counter("collection_delete_errors")
            raise VectorOperationError(f"Collection deletion failed: {str(e)}")
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all collections.
        
        Returns:
            Dict with collection list
        """
        try:
            result = await self.qdrant_client.list_collections()
            return result
            
        except Exception as e:
            raise VectorOperationError(f"Collection listing failed: {str(e)}")
    
    async def get_collection_info(self, name: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            name: Collection name
            
        Returns:
            Dict with collection information
        """
        try:
            # Validate inputs
            validate_collection_name(name)
            
            result = await self.qdrant_client.get_collection_info(name)
            return result
            
        except Exception as e:
            raise VectorOperationError(f"Collection info retrieval failed: {str(e)}")
    
    async def batch_insert(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform batch vector operations.
        
        Args:
            operations: List of batch operations
            
        Returns:
            Dict with batch results
        """
        try:
            result = await self.batch_processor.process_batch(operations)
            
            self.metrics.increment_counter("batch_operations_total")
            
            return result
            
        except Exception as e:
            self.metrics.increment_counter("batch_operation_errors")
            raise VectorOperationError(f"Batch operation failed: {str(e)}")
    
    async def _initialize_collections(self):
        """Initialize default collections for AI models."""
        try:
            existing_collections = await self.list_collections()
            existing_names = set(existing_collections.get("collections", []))
            
            for collection_name, config in self.model_collections.items():
                if collection_name not in existing_names:
                    await self.create_collection(
                        name=collection_name,
                        vector_size=config["dimensions"],
                        distance=config["distance"]
                    )
                    
        except Exception as e:
            print(f"Warning: Failed to initialize collections: {e}")
    
    async def _ensure_collection_exists(self, collection_name: str):
        """Ensure a collection exists, create if not."""
        try:
            await self.get_collection_info(collection_name)
        except VectorOperationError:
            # Collection doesn't exist, create with default config
            if collection_name in self.model_collections:
                config = self.model_collections[collection_name]
                await self.create_collection(
                    name=collection_name,
                    vector_size=config["dimensions"],
                    distance=config["distance"]
                )
            else:
                # Use general embeddings config as default
                await self.create_collection(
                    name=collection_name,
                    vector_size=1536,
                    distance="Cosine"
                )
    
    async def _insert_with_retries(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int
    ) -> Dict[str, Any]:
        """Insert vectors with retry logic."""
        for attempt in range(self.max_retries):
            try:
                result = await self.batch_processor.insert_batch(
                    collection_name=collection_name,
                    vectors=vectors,
                    batch_size=batch_size
                )
                return result
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
                
        # Should never reach here
        raise VectorOperationError("Max retries exceeded")
