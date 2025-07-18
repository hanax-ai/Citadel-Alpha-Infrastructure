"""
GraphQL API Handler
==================

GraphQL schema and resolver implementation for vector database operations.
Provides schema-based queries and mutations for vector operations.
"""

from typing import Dict, Any, List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from ..vector_ops.operations import VectorOperationsManager
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError


@strawberry.type
class VectorResult:
    """GraphQL type for vector search results."""
    id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


@strawberry.type
class SearchResponse:
    """GraphQL type for search response."""
    results: List[VectorResult]
    count: int
    duration: float


@strawberry.type
class CollectionInfo:
    """GraphQL type for collection information."""
    name: str
    vector_size: int
    distance: str
    points_count: int
    config: Optional[Dict[str, Any]] = None


@strawberry.type
class OperationResponse:
    """GraphQL type for operation responses."""
    status: str
    message: str
    count: Optional[int] = None
    duration: Optional[float] = None


@strawberry.input
class VectorInput:
    """GraphQL input type for vector data."""
    id: str
    vector: List[float]
    metadata: Optional[Dict[str, Any]] = None


@strawberry.input
class SearchFilters:
    """GraphQL input type for search filters."""
    filters: Optional[Dict[str, Any]] = None
    score_threshold: Optional[float] = None


class GraphQLHandler:
    """GraphQL API handler for vector database operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vector_ops = VectorOperationsManager(config)
        self.metrics = MetricsCollector()
        
        # Create GraphQL schema
        self.schema = strawberry.Schema(
            query=Query,
            mutation=Mutation
        )
        
        # Create router
        self.router = GraphQLRouter(
            self.schema,
            context_getter=self._get_context
        )
    
    async def startup(self):
        """Initialize GraphQL handler."""
        await self.vector_ops.startup()
    
    async def shutdown(self):
        """Cleanup GraphQL handler."""
        await self.vector_ops.shutdown()
    
    async def _get_context(self) -> Dict[str, Any]:
        """Get GraphQL context with shared services."""
        return {
            "vector_ops": self.vector_ops,
            "metrics": self.metrics
        }


@strawberry.type
class Query:
    """GraphQL query operations."""
    
    @strawberry.field
    async def search_vectors(
        self,
        info: Info,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[SearchFilters] = None
    ) -> SearchResponse:
        """Search for similar vectors in a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            # Extract filters
            search_filters = None
            score_threshold = None
            if filters:
                search_filters = filters.filters
                score_threshold = filters.score_threshold
            
            # Perform search
            result = await vector_ops.similarity_search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                filters=search_filters,
                score_threshold=score_threshold
            )
            
            # Convert results to GraphQL types
            vector_results = [
                VectorResult(
                    id=r["id"],
                    score=r["score"],
                    metadata=r.get("metadata")
                )
                for r in result["results"]
            ]
            
            metrics.increment_counter("graphql_searches")
            metrics.record_histogram("graphql_search_latency", result["duration"])
            
            return SearchResponse(
                results=vector_results,
                count=len(vector_results),
                duration=result["duration"]
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_search_errors")
            raise Exception(f"Search error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_search_errors")
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.field
    async def get_collection_info(
        self,
        info: Info,
        collection: str
    ) -> CollectionInfo:
        """Get information about a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            
            result = await vector_ops.get_collection_info(collection)
            collection_info = result["info"]
            
            return CollectionInfo(
                name=collection,
                vector_size=collection_info["vector_size"],
                distance=collection_info["distance"],
                points_count=collection_info["points_count"],
                config=collection_info.get("config")
            )
            
        except VectorOperationError as e:
            raise Exception(f"Collection not found: {str(e)}")
        except Exception as e:
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.field
    async def list_collections(self, info: Info) -> List[str]:
        """List all available collections."""
        try:
            vector_ops = info.context["vector_ops"]
            
            result = await vector_ops.list_collections()
            return result["collections"]
            
        except Exception as e:
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.field
    async def get_vector(
        self,
        info: Info,
        collection: str,
        vector_id: str
    ) -> Optional[VectorResult]:
        """Get a specific vector by ID."""
        try:
            vector_ops = info.context["vector_ops"]
            
            result = await vector_ops.get_vector(
                collection_name=collection,
                vector_id=vector_id
            )
            
            if result["found"]:
                vector_data = result["vector"]
                return VectorResult(
                    id=vector_data["id"],
                    score=1.0,  # Perfect match for exact retrieval
                    metadata=vector_data.get("metadata")
                )
            
            return None
            
        except VectorOperationError as e:
            raise Exception(f"Vector retrieval error: {str(e)}")
        except Exception as e:
            raise Exception(f"Internal error: {str(e)}")


@strawberry.type
class Mutation:
    """GraphQL mutation operations."""
    
    @strawberry.mutation
    async def insert_vectors(
        self,
        info: Info,
        collection: str,
        vectors: List[VectorInput],
        batch_size: int = 1000
    ) -> OperationResponse:
        """Insert vectors into a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            # Convert GraphQL input to dict format
            vector_data = [
                {
                    "id": v.id,
                    "vector": v.vector,
                    "metadata": v.metadata or {}
                }
                for v in vectors
            ]
            
            # Insert vectors
            result = await vector_ops.insert_vectors(
                collection_name=collection,
                vectors=vector_data,
                batch_size=batch_size
            )
            
            metrics.increment_counter("graphql_inserts", len(vectors))
            
            return OperationResponse(
                status="success",
                message=f"Inserted {result['inserted_count']} vectors",
                count=result["inserted_count"],
                duration=result["duration"]
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_insert_errors")
            raise Exception(f"Insert error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_insert_errors")
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.mutation
    async def update_vector(
        self,
        info: Info,
        collection: str,
        vector_id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OperationResponse:
        """Update a vector in a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            result = await vector_ops.update_vector(
                collection_name=collection,
                vector_id=vector_id,
                vector=vector,
                metadata=metadata
            )
            
            metrics.increment_counter("graphql_updates")
            
            return OperationResponse(
                status="success",
                message=f"Updated vector {vector_id}",
                count=1 if result["updated"] else 0
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_update_errors")
            raise Exception(f"Update error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_update_errors")
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.mutation
    async def delete_vector(
        self,
        info: Info,
        collection: str,
        vector_id: str
    ) -> OperationResponse:
        """Delete a vector from a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            result = await vector_ops.delete_vector(
                collection_name=collection,
                vector_id=vector_id
            )
            
            metrics.increment_counter("graphql_deletes")
            
            return OperationResponse(
                status="success",
                message=f"Deleted vector {vector_id}",
                count=1 if result["deleted"] else 0
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_delete_errors")
            raise Exception(f"Delete error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_delete_errors")
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.mutation
    async def create_collection(
        self,
        info: Info,
        name: str,
        vector_size: int,
        distance: str = "Cosine",
        config: Optional[Dict[str, Any]] = None
    ) -> OperationResponse:
        """Create a new vector collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            result = await vector_ops.create_collection(
                name=name,
                vector_size=vector_size,
                distance=distance,
                config=config
            )
            
            metrics.increment_counter("graphql_collections_created")
            
            return OperationResponse(
                status="success",
                message=f"Created collection {name}",
                count=1 if result["created"] else 0
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_collection_create_errors")
            raise Exception(f"Collection creation error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_collection_create_errors")
            raise Exception(f"Internal error: {str(e)}")
    
    @strawberry.mutation
    async def delete_collection(
        self,
        info: Info,
        collection: str
    ) -> OperationResponse:
        """Delete a collection."""
        try:
            vector_ops = info.context["vector_ops"]
            metrics = info.context["metrics"]
            
            result = await vector_ops.delete_collection(collection)
            
            metrics.increment_counter("graphql_collections_deleted")
            
            return OperationResponse(
                status="success",
                message=f"Deleted collection {collection}",
                count=1 if result["deleted"] else 0
            )
            
        except VectorOperationError as e:
            metrics.increment_counter("graphql_collection_delete_errors")
            raise Exception(f"Collection deletion error: {str(e)}")
        except Exception as e:
            metrics.increment_counter("graphql_collection_delete_errors")
            raise Exception(f"Internal error: {str(e)}")
