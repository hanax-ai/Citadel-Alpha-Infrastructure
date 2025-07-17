"""
REST API Handler
===============

FastAPI-based REST API implementation for vector database operations.
Provides JSON/HTTP endpoints for all vector operations.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import asyncio
from ..vector_ops.operations import VectorOperationsManager
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError
from ..utils.validators import validate_vector_data


class VectorInsertRequest(BaseModel):
    """Request model for vector insertion."""
    collection: str = Field(..., description="Collection name")
    vectors: List[Dict[str, Any]] = Field(..., description="Vector data with metadata")
    batch_size: int = Field(1000, description="Batch size for insertion")


class VectorSearchRequest(BaseModel):
    """Request model for vector search."""
    collection: str = Field(..., description="Collection name")
    query_vector: List[float] = Field(..., description="Query vector")
    limit: int = Field(10, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    score_threshold: Optional[float] = Field(None, description="Minimum similarity score")


class VectorUpdateRequest(BaseModel):
    """Request model for vector updates."""
    collection: str = Field(..., description="Collection name")
    vector_id: str = Field(..., description="Vector ID to update")
    vector: Optional[List[float]] = Field(None, description="New vector data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata")


class CollectionCreateRequest(BaseModel):
    """Request model for collection creation."""
    name: str = Field(..., description="Collection name")
    vector_size: int = Field(..., description="Vector dimensions")
    distance: str = Field("Cosine", description="Distance metric")
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class RestHandler:
    """REST API handler for vector database operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.router = APIRouter()
        self.vector_ops = VectorOperationsManager(config)
        self.metrics = MetricsCollector()
        
        self._setup_routes()
    
    async def startup(self):
        """Initialize REST handler."""
        await self.vector_ops.startup()
    
    async def shutdown(self):
        """Cleanup REST handler."""
        await self.vector_ops.shutdown()
    
    def _setup_routes(self):
        """Configure REST API routes."""
        
        @self.router.post("/vectors/insert")
        async def insert_vectors(request: VectorInsertRequest):
            """Insert vectors into a collection."""
            try:
                # Validate vector data
                validate_vector_data(request.vectors)
                
                # Insert vectors
                result = await self.vector_ops.insert_vectors(
                    collection_name=request.collection,
                    vectors=request.vectors,
                    batch_size=request.batch_size
                )
                
                self.metrics.increment_counter("vectors_inserted", len(request.vectors))
                return {
                    "status": "success",
                    "inserted_count": result["inserted_count"],
                    "collection": request.collection,
                    "duration": result["duration"]
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("vector_insert_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("vector_insert_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.post("/vectors/search")
        async def search_vectors(request: VectorSearchRequest):
            """Search for similar vectors."""
            try:
                # Perform similarity search
                result = await self.vector_ops.similarity_search(
                    collection_name=request.collection,
                    query_vector=request.query_vector,
                    limit=request.limit,
                    filters=request.filters,
                    score_threshold=request.score_threshold
                )
                
                self.metrics.increment_counter("vector_searches")
                self.metrics.record_histogram("search_latency", result["duration"])
                
                return {
                    "status": "success",
                    "results": result["results"],
                    "count": len(result["results"]),
                    "duration": result["duration"]
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("vector_search_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("vector_search_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.put("/vectors/update")
        async def update_vector(request: VectorUpdateRequest):
            """Update a vector in a collection."""
            try:
                result = await self.vector_ops.update_vector(
                    collection_name=request.collection,
                    vector_id=request.vector_id,
                    vector=request.vector,
                    metadata=request.metadata
                )
                
                self.metrics.increment_counter("vectors_updated")
                return {
                    "status": "success",
                    "updated": result["updated"],
                    "vector_id": request.vector_id,
                    "collection": request.collection
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("vector_update_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("vector_update_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.delete("/vectors/{collection}/{vector_id}")
        async def delete_vector(collection: str, vector_id: str):
            """Delete a vector from a collection."""
            try:
                result = await self.vector_ops.delete_vector(
                    collection_name=collection,
                    vector_id=vector_id
                )
                
                self.metrics.increment_counter("vectors_deleted")
                return {
                    "status": "success",
                    "deleted": result["deleted"],
                    "vector_id": vector_id,
                    "collection": collection
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("vector_delete_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("vector_delete_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.post("/collections/create")
        async def create_collection(request: CollectionCreateRequest):
            """Create a new vector collection."""
            try:
                result = await self.vector_ops.create_collection(
                    name=request.name,
                    vector_size=request.vector_size,
                    distance=request.distance,
                    config=request.config
                )
                
                self.metrics.increment_counter("collections_created")
                return {
                    "status": "success",
                    "collection": request.name,
                    "created": result["created"]
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("collection_create_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("collection_create_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.get("/collections")
        async def list_collections():
            """List all collections."""
            try:
                result = await self.vector_ops.list_collections()
                
                return {
                    "status": "success",
                    "collections": result["collections"],
                    "count": len(result["collections"])
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.get("/collections/{collection}/info")
        async def get_collection_info(collection: str):
            """Get collection information."""
            try:
                result = await self.vector_ops.get_collection_info(collection)
                
                return {
                    "status": "success",
                    "collection": collection,
                    "info": result["info"]
                }
                
            except VectorOperationError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.delete("/collections/{collection}")
        async def delete_collection(collection: str):
            """Delete a collection."""
            try:
                result = await self.vector_ops.delete_collection(collection)
                
                self.metrics.increment_counter("collections_deleted")
                return {
                    "status": "success",
                    "collection": collection,
                    "deleted": result["deleted"]
                }
                
            except VectorOperationError as e:
                self.metrics.increment_counter("collection_delete_errors")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.metrics.increment_counter("collection_delete_errors")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.post("/vectors/batch")
        async def batch_operations(background_tasks: BackgroundTasks):
            """Handle batch vector operations."""
            try:
                # Implement batch processing logic
                background_tasks.add_task(self._process_batch_operations)
                
                return {
                    "status": "accepted",
                    "message": "Batch operations queued for processing"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    async def _process_batch_operations(self):
        """Process batch operations in the background."""
        # Implement batch processing logic
        pass
