"""
Vector Operations Module

Core vector database operations following HXP Governance Coding Standards.
Implements Single Responsibility Principle by handling only vector CRUD operations.

Author: Citadel AI Team
License: MIT
"""

from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime

from hana_x_vector.models.vector_models import (
    Vector,
    VectorSearchRequest,
    VectorSearchResult
)
from hana_x_vector.utils.metrics import monitor_performance

logger = logging.getLogger(__name__)


@dataclass
class VectorOperationResult:
    """Result of vector operation (Data encapsulation)."""
    success: bool
    message: str
    data: Optional[Any] = None
    operation_time_ms: Optional[float] = None


class VectorOperationInterface(ABC):
    """
    Abstract interface for vector operations (Abstraction principle).
    
    Defines the contract for vector database operations without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def insert_vector(self, vector: Vector, collection: str) -> VectorOperationResult:
        """Insert a single vector into collection."""
        pass
    
    @abstractmethod
    async def insert_vectors(self, vectors: List[Vector], collection: str) -> VectorOperationResult:
        """Insert multiple vectors into collection."""
        pass
    
    @abstractmethod
    async def search_vectors(self, request: VectorSearchRequest) -> VectorSearchResult:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def get_vector(self, vector_id: str, collection: str) -> Optional[Vector]:
        """Get vector by ID."""
        pass
    
    @abstractmethod
    async def update_vector(self, vector: Vector, collection: str) -> VectorOperationResult:
        """Update existing vector."""
        pass
    
    @abstractmethod
    async def delete_vector(self, vector_id: str, collection: str) -> VectorOperationResult:
        """Delete vector by ID."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of vector operations."""
        pass


class VectorOperations(VectorOperationInterface):
    """
    Vector operations implementation (Single Responsibility Principle).
    
    Handles all vector database CRUD operations with proper error handling,
    logging, and performance monitoring. Follows Open/Closed Principle by
    allowing extension through composition.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vector operations.
        
        Args:
            config: Configuration dictionary containing database settings
        """
        self._config = config
        self._client = None
        self._initialized = False
        
        # Configuration validation
        self._validate_config()
        
        logger.info("VectorOperations initialized with configuration")
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_keys = ["qdrant_host", "qdrant_port"]
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    async def initialize(self) -> None:
        """Initialize vector database connection."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models
            
            # Initialize Qdrant client (Dependency Inversion)
            self._client = QdrantClient(
                host=self._config["qdrant_host"],
                port=self._config["qdrant_port"],
                timeout=self._config.get("qdrant_timeout", 30)
            )
            
            # Test connection
            await self._client.get_collections()
            self._initialized = True
            
            logger.info("Vector operations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector operations: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure vector operations are initialized."""
        if not self._initialized:
            raise RuntimeError("VectorOperations not initialized. Call initialize() first.")
    
    @monitor_performance("insert_vector")
    async def insert_vector(self, vector: Vector, collection: str) -> VectorOperationResult:
        """
        Insert a single vector into collection.
        
        Args:
            vector: Vector to insert
            collection: Target collection name
            
        Returns:
            VectorOperationResult with operation status
        """
        self._ensure_initialized()
        
        try:
            from qdrant_client.http import models
            
            # Convert to Qdrant point format
            point = models.PointStruct(
                id=vector.id,
                vector=vector.embedding,
                payload=vector.metadata or {}
            )
            
            # Insert vector
            result = await self._client.upsert(
                collection_name=collection,
                points=[point]
            )
            
            logger.info(f"Vector {vector.id} inserted into collection {collection}")
            
            return VectorOperationResult(
                success=True,
                message=f"Vector {vector.id} inserted successfully",
                data={"vector_id": vector.id, "collection": collection}
            )
            
        except Exception as e:
            logger.error(f"Failed to insert vector {vector.id}: {e}")
            return VectorOperationResult(
                success=False,
                message=f"Failed to insert vector: {e}"
            )
    
    @monitor_performance("insert_vectors")
    async def insert_vectors(self, vectors: List[Vector], collection: str) -> VectorOperationResult:
        """
        Insert multiple vectors into collection.
        
        Args:
            vectors: List of vectors to insert
            collection: Target collection name
            
        Returns:
            VectorOperationResult with operation status
        """
        self._ensure_initialized()
        
        try:
            from qdrant_client.http import models
            
            # Convert to Qdrant points format
            points = [
                models.PointStruct(
                    id=vector.id,
                    vector=vector.embedding,
                    payload=vector.metadata or {}
                )
                for vector in vectors
            ]
            
            # Insert vectors in batches for performance
            batch_size = self._config.get("batch_size", 100)
            inserted_count = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                await self._client.upsert(
                    collection_name=collection,
                    points=batch
                )
                inserted_count += len(batch)
            
            logger.info(f"{inserted_count} vectors inserted into collection {collection}")
            
            return VectorOperationResult(
                success=True,
                message=f"{inserted_count} vectors inserted successfully",
                data={"inserted_count": inserted_count, "collection": collection}
            )
            
        except Exception as e:
            logger.error(f"Failed to insert vectors: {e}")
            return VectorOperationResult(
                success=False,
                message=f"Failed to insert vectors: {e}"
            )
    
    @monitor_performance("search_vectors")
    async def search_vectors(self, request: VectorSearchRequest) -> VectorSearchResult:
        """
        Search for similar vectors.
        
        Args:
            request: Vector search request
            
        Returns:
            VectorSearchResult with matching vectors
        """
        self._ensure_initialized()
        
        try:
            from qdrant_client.http import models
            
            # Perform vector search
            search_result = await self._client.search(
                collection_name=request.collection,
                query_vector=request.query_vector,
                limit=request.limit,
                score_threshold=request.score_threshold,
                with_payload=True,
                with_vectors=request.include_vectors
            )
            
            # Convert results to Vector objects
            vectors = []
            for hit in search_result:
                vector = Vector(
                    id=str(hit.id),
                    embedding=hit.vector if request.include_vectors else [],
                    metadata=hit.payload or {},
                    collection=request.collection,
                    score=hit.score
                )
                vectors.append(vector)
            
            logger.info(f"Vector search returned {len(vectors)} results from {request.collection}")
            
            return VectorSearchResult(
                vectors=vectors,
                total_count=len(vectors),
                query_time_ms=0.0,  # Would be calculated from actual timing
                collection=request.collection,
                search_params=request
            )
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return VectorSearchResult(
                vectors=[],
                total_count=0,
                query_time_ms=0.0,
                collection=request.collection,
                search_params=request
            )
    
    @monitor_performance("get_vector")
    async def get_vector(self, vector_id: str, collection: str) -> Optional[Vector]:
        """
        Get vector by ID.
        
        Args:
            vector_id: Vector ID to retrieve
            collection: Collection name
            
        Returns:
            Vector if found, None otherwise
        """
        self._ensure_initialized()
        
        try:
            # Retrieve vector by ID
            result = await self._client.retrieve(
                collection_name=collection,
                ids=[vector_id],
                with_payload=True,
                with_vectors=True
            )
            
            if result:
                point = result[0]
                vector = Vector(
                    id=str(point.id),
                    embedding=point.vector or [],
                    metadata=point.payload or {},
                    collection=collection
                )
                
                logger.info(f"Vector {vector_id} retrieved from {collection}")
                return vector
            
            logger.warning(f"Vector {vector_id} not found in {collection}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get vector {vector_id}: {e}")
            return None
    
    @monitor_performance("update_vector")
    async def update_vector(self, vector: Vector, collection: str) -> VectorOperationResult:
        """
        Update existing vector.
        
        Args:
            vector: Updated vector data
            collection: Collection name
            
        Returns:
            VectorOperationResult with operation status
        """
        self._ensure_initialized()
        
        try:
            from qdrant_client.http import models
            
            # Update vector (upsert operation)
            point = models.PointStruct(
                id=vector.id,
                vector=vector.embedding,
                payload=vector.metadata or {}
            )
            
            await self._client.upsert(
                collection_name=collection,
                points=[point]
            )
            
            logger.info(f"Vector {vector.id} updated in collection {collection}")
            
            return VectorOperationResult(
                success=True,
                message=f"Vector {vector.id} updated successfully",
                data={"vector_id": vector.id, "collection": collection}
            )
            
        except Exception as e:
            logger.error(f"Failed to update vector {vector.id}: {e}")
            return VectorOperationResult(
                success=False,
                message=f"Failed to update vector: {e}"
            )
    
    @monitor_performance("delete_vector")
    async def delete_vector(self, vector_id: str, collection: str) -> VectorOperationResult:
        """
        Delete vector by ID.
        
        Args:
            vector_id: Vector ID to delete
            collection: Collection name
            
        Returns:
            VectorOperationResult with operation status
        """
        self._ensure_initialized()
        
        try:
            # Delete vector
            await self._client.delete(
                collection_name=collection,
                points_selector=models.PointIdsList(
                    points=[vector_id]
                )
            )
            
            logger.info(f"Vector {vector_id} deleted from collection {collection}")
            
            return VectorOperationResult(
                success=True,
                message=f"Vector {vector_id} deleted successfully",
                data={"vector_id": vector_id, "collection": collection}
            )
            
        except Exception as e:
            logger.error(f"Failed to delete vector {vector_id}: {e}")
            return VectorOperationResult(
                success=False,
                message=f"Failed to delete vector: {e}"
            )
    
    async def get_total_vector_count(self) -> int:
        """Get total number of vectors across all collections."""
        self._ensure_initialized()
        
        try:
            collections = await self._client.get_collections()
            total_count = 0
            
            for collection in collections.collections:
                info = await self._client.get_collection(collection.name)
                total_count += info.points_count or 0
            
            return total_count
            
        except Exception as e:
            logger.error(f"Failed to get total vector count: {e}")
            return 0
    
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self._initialized and self._client is not None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of vector operations.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "message": "Not initialized",
                    "connected": False
                }
            
            # Test connection with collections list
            collections = await self._client.get_collections()
            total_vectors = await self.get_total_vector_count()
            
            return {
                "status": "healthy",
                "message": "Vector operations operational",
                "connected": True,
                "collections_count": len(collections.collections),
                "total_vectors": total_vectors,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {e}",
                "connected": False,
                "error": str(e)
            }
