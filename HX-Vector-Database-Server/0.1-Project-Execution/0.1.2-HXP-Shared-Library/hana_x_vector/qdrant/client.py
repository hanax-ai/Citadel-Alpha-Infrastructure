"""
Qdrant Client
============

Optimized Qdrant client wrapper for vector database operations.
Provides high-performance interface with connection pooling and error handling.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import time
from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import QdrantConnectionError, VectorOperationError
from .collections import CollectionManager
from .indexing import IndexOptimizer
from .config import QdrantConfigManager


class QdrantClient:
    """
    Optimized Qdrant client wrapper with performance enhancements.
    Provides connection pooling, retry logic, and comprehensive error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Qdrant configuration
        qdrant_config = config.get("qdrant", {})
        self.host = qdrant_config.get("host", "localhost")
        self.port = qdrant_config.get("port", 6333)
        self.grpc_port = qdrant_config.get("grpc_port", 6334)
        self.prefer_grpc = qdrant_config.get("prefer_grpc", True)
        self.timeout = qdrant_config.get("timeout", 30.0)
        
        # Connection settings
        self.max_retries = qdrant_config.get("max_retries", 3)
        self.retry_delay = qdrant_config.get("retry_delay", 1.0)
        self.connection_pool_size = qdrant_config.get("pool_size", 10)
        
        # Performance settings
        self.batch_size = qdrant_config.get("batch_size", 1000)
        self.parallel_operations = qdrant_config.get("parallel_operations", 4)
        
        # Initialize components
        self.collection_manager = CollectionManager(config)
        self.index_optimizer = IndexOptimizer(config)
        self.config_manager = QdrantConfigManager(config)
        
        # Client instances
        self.client = None
        self.grpc_client = None
        self._connection_lock = asyncio.Lock()
    
    async def startup(self):
        """Initialize Qdrant client connections."""
        async with self._connection_lock:
            try:
                # Initialize HTTP client
                self.client = QdrantClientBase(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout
                )
                
                # Initialize gRPC client if preferred
                if self.prefer_grpc:
                    self.grpc_client = QdrantClientBase(
                        host=self.host,
                        port=self.grpc_port,
                        prefer_grpc=True,
                        timeout=self.timeout
                    )
                
                # Test connections
                await self._test_connections()
                
                # Initialize components
                await self.collection_manager.startup()
                await self.index_optimizer.startup()
                
                self.metrics.increment_counter("qdrant_connections_established")
                
            except Exception as e:
                self.metrics.increment_counter("qdrant_connection_errors")
                raise QdrantConnectionError(f"Failed to initialize Qdrant client: {str(e)}")
    
    async def shutdown(self):
        """Cleanup Qdrant client connections."""
        async with self._connection_lock:
            try:
                if self.collection_manager:
                    await self.collection_manager.shutdown()
                if self.index_optimizer:
                    await self.index_optimizer.shutdown()
                
                # Close clients
                if self.client:
                    self.client.close()
                if self.grpc_client:
                    self.grpc_client.close()
                
                self.metrics.increment_counter("qdrant_connections_closed")
                
            except Exception as e:
                print(f"Warning: Error during Qdrant client shutdown: {e}")
    
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
        return await self.collection_manager.create_collection(
            name=name,
            vector_size=vector_size,
            distance=distance,
            config=config
        )
    
    async def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            Dict with deletion results
        """
        return await self.collection_manager.delete_collection(name)
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all collections.
        
        Returns:
            Dict with collection list
        """
        return await self.collection_manager.list_collections()
    
    async def get_collection_info(self, name: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            name: Collection name
            
        Returns:
            Dict with collection information
        """
        return await self.collection_manager.get_collection_info(name)
    
    async def insert_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert vectors into a collection.
        
        Args:
            collection_name: Name of the collection
            vectors: List of vector data
            
        Returns:
            Dict with insertion results
        """
        start_time = time.time()
        
        try:
            # Convert to Qdrant points format
            points = []
            for vector_data in vectors:
                point = models.PointStruct(
                    id=vector_data["id"],
                    vector=vector_data["vector"],
                    payload=vector_data.get("metadata", {})
                )
                points.append(point)
            
            # Perform insertion with retry logic
            result = await self._execute_with_retry(
                self._insert_points,
                collection_name,
                points
            )
            
            duration = time.time() - start_time
            self.metrics.record_histogram("qdrant_insert_duration", duration)
            self.metrics.increment_counter("qdrant_vectors_inserted", len(vectors))
            
            return {
                "inserted_count": len(vectors),
                "duration": duration,
                "operation_id": result.operation_id if hasattr(result, 'operation_id') else None
            }
            
        except Exception as e:
            self.metrics.increment_counter("qdrant_insert_errors")
            raise VectorOperationError(f"Vector insertion failed: {str(e)}")
    
    async def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
        search_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Maximum number of results
            filters: Search filters
            score_threshold: Minimum similarity score
            search_params: Additional search parameters
            
        Returns:
            List of search results
        """
        start_time = time.time()
        
        try:
            # Convert filters to Qdrant format
            qdrant_filter = self._convert_filters(filters) if filters else None
            
            # Prepare search parameters
            search_params = search_params or {}
            
            # Perform search with retry logic
            results = await self._execute_with_retry(
                self._search_points,
                collection_name,
                query_vector,
                limit,
                qdrant_filter,
                score_threshold,
                search_params
            )
            
            # Convert results to standard format
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": str(result.id),
                    "score": result.score,
                    "metadata": result.payload or {}
                }
                if hasattr(result, 'vector') and result.vector:
                    formatted_result["vector"] = result.vector
                formatted_results.append(formatted_result)
            
            duration = time.time() - start_time
            self.metrics.record_histogram("qdrant_search_duration", duration)
            self.metrics.increment_counter("qdrant_searches_performed")
            
            return formatted_results
            
        except Exception as e:
            self.metrics.increment_counter("qdrant_search_errors")
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
            vector: New vector data
            metadata: New metadata
            
        Returns:
            Dict with update results
        """
        try:
            # Prepare update data
            update_data = {}
            if vector is not None:
                update_data["vector"] = vector
            if metadata is not None:
                update_data["payload"] = metadata
            
            # Perform update with retry logic
            result = await self._execute_with_retry(
                self._update_point,
                collection_name,
                vector_id,
                update_data
            )
            
            self.metrics.increment_counter("qdrant_vectors_updated")
            
            return {
                "updated": True,
                "operation_id": result.operation_id if hasattr(result, 'operation_id') else None
            }
            
        except Exception as e:
            self.metrics.increment_counter("qdrant_update_errors")
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
        try:
            # Perform deletion with retry logic
            result = await self._execute_with_retry(
                self._delete_point,
                collection_name,
                vector_id
            )
            
            self.metrics.increment_counter("qdrant_vectors_deleted")
            
            return {
                "deleted": True,
                "operation_id": result.operation_id if hasattr(result, 'operation_id') else None
            }
            
        except Exception as e:
            self.metrics.increment_counter("qdrant_delete_errors")
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
            # Perform retrieval with retry logic
            result = await self._execute_with_retry(
                self._get_point,
                collection_name,
                vector_id
            )
            
            if result:
                return {
                    "found": True,
                    "vector": {
                        "id": str(result.id),
                        "vector": result.vector,
                        "metadata": result.payload or {}
                    }
                }
            else:
                return {"found": False}
                
        except Exception as e:
            self.metrics.increment_counter("qdrant_retrieval_errors")
            raise VectorOperationError(f"Vector retrieval failed: {str(e)}")
    
    async def scroll_points(
        self,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scroll through points in a collection.
        
        Args:
            collection_name: Name of the collection
            filters: Search filters
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of points
        """
        try:
            # Convert filters to Qdrant format
            qdrant_filter = self._convert_filters(filters) if filters else None
            
            # Perform scroll with retry logic
            result = await self._execute_with_retry(
                self._scroll_points,
                collection_name,
                qdrant_filter,
                limit,
                offset
            )
            
            # Convert results to standard format
            formatted_results = []
            for point in result[0]:  # result is (points, next_page_offset)
                formatted_result = {
                    "id": str(point.id),
                    "metadata": point.payload or {}
                }
                if hasattr(point, 'vector') and point.vector:
                    formatted_result["vector"] = point.vector
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            self.metrics.increment_counter("qdrant_scroll_errors")
            raise VectorOperationError(f"Point scrolling failed: {str(e)}")
    
    async def _test_connections(self):
        """Test Qdrant connections."""
        try:
            # Test HTTP connection
            if self.client:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.client.get_collections
                )
            
            # Test gRPC connection
            if self.grpc_client:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.grpc_client.get_collections
                )
                
        except Exception as e:
            raise QdrantConnectionError(f"Connection test failed: {str(e)}")
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Use gRPC client if available and preferred
                client = self.grpc_client if self.grpc_client else self.client
                
                # Execute in thread pool to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None, func, client, *args, **kwargs
                )
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries - 1:
                    break
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # All retries failed
        self.metrics.increment_counter("qdrant_retry_failures")
        raise last_exception
    
    def _insert_points(self, client, collection_name: str, points: List[models.PointStruct]):
        """Insert points using Qdrant client."""
        return client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    def _search_points(
        self,
        client,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        qdrant_filter: Optional[models.Filter],
        score_threshold: Optional[float],
        search_params: Dict[str, Any]
    ):
        """Search points using Qdrant client."""
        return client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=limit,
            score_threshold=score_threshold,
            search_params=models.SearchParams(**search_params) if search_params else None
        )
    
    def _update_point(
        self,
        client,
        collection_name: str,
        vector_id: str,
        update_data: Dict[str, Any]
    ):
        """Update point using Qdrant client."""
        point = models.PointStruct(
            id=vector_id,
            vector=update_data.get("vector"),
            payload=update_data.get("payload")
        )
        return client.upsert(
            collection_name=collection_name,
            points=[point]
        )
    
    def _delete_point(self, client, collection_name: str, vector_id: str):
        """Delete point using Qdrant client."""
        return client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(
                points=[vector_id]
            )
        )
    
    def _get_point(self, client, collection_name: str, vector_id: str):
        """Get point using Qdrant client."""
        result = client.retrieve(
            collection_name=collection_name,
            ids=[vector_id],
            with_vectors=True,
            with_payload=True
        )
        return result[0] if result else None
    
    def _scroll_points(
        self,
        client,
        collection_name: str,
        qdrant_filter: Optional[models.Filter],
        limit: int,
        offset: Optional[str]
    ):
        """Scroll points using Qdrant client."""
        return client.scroll(
            collection_name=collection_name,
            scroll_filter=qdrant_filter,
            limit=limit,
            offset=offset,
            with_vectors=True,
            with_payload=True
        )
    
    def _convert_filters(self, filters: Dict[str, Any]) -> models.Filter:
        """Convert filters to Qdrant format."""
        # Simple filter conversion - can be extended for complex filters
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle nested conditions
                if "match" in value:
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value["match"])
                        )
                    )
                elif "range" in value:
                    range_val = value["range"]
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            range=models.Range(
                                gte=range_val.get("gte"),
                                lte=range_val.get("lte")
                            )
                        )
                    )
            else:
                # Simple equality match
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )
        
        return models.Filter(must=conditions) if conditions else None
