"""
GraphQL Schema Definition

GraphQL schema and resolvers following HXP Governance Coding Standards.
Implements Single Responsibility Principle for GraphQL protocol abstraction.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List
import strawberry
from strawberry.types import Info
import logging
from datetime import datetime

from hana_x_vector.models.vector_models import (
    Vector, VectorSearchRequest, VectorSearchResult, EmbeddingRequest, EmbeddingResponse
)
from hana_x_vector.models.external_models import ExternalModel, ModelResponse
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


# GraphQL Types (Data Transfer Objects)
@strawberry.type
class VectorType:
    """GraphQL type for Vector."""
    id: str
    embedding: List[float]
    metadata: Optional[str] = None  # JSON string
    collection: Optional[str] = None
    score: Optional[float] = None
    created_at: str
    updated_at: Optional[str] = None
    
    @classmethod
    def from_vector(cls, vector: Vector) -> "VectorType":
        """Convert Vector model to GraphQL type."""
        import json
        return cls(
            id=str(vector.id),
            embedding=vector.embedding,
            metadata=json.dumps(vector.metadata) if vector.metadata else None,
            collection=vector.collection,
            score=vector.score,
            created_at=vector.created_at.isoformat(),
            updated_at=vector.updated_at.isoformat() if vector.updated_at else None
        )


@strawberry.type
class VectorSearchResultType:
    """GraphQL type for Vector Search Result."""
    vectors: List[VectorType]
    total_count: int
    query_time_ms: float
    collection: str
    timestamp: str
    
    @classmethod
    def from_search_result(cls, result: VectorSearchResult) -> "VectorSearchResultType":
        """Convert VectorSearchResult to GraphQL type."""
        return cls(
            vectors=[VectorType.from_vector(v) for v in result.vectors],
            total_count=result.total_count,
            query_time_ms=result.query_time_ms,
            collection=result.collection,
            timestamp=result.timestamp.isoformat()
        )


@strawberry.type
class EmbeddingResponseType:
    """GraphQL type for Embedding Response."""
    embeddings: List[List[float]]
    model_name: str
    dimension: int
    processing_time_ms: float
    token_count: Optional[int] = None
    timestamp: str
    
    @classmethod
    def from_embedding_response(cls, response: EmbeddingResponse) -> "EmbeddingResponseType":
        """Convert EmbeddingResponse to GraphQL type."""
        return cls(
            embeddings=response.embeddings,
            model_name=response.model_name,
            dimension=response.dimension,
            processing_time_ms=response.processing_time_ms,
            token_count=response.token_count,
            timestamp=response.timestamp.isoformat()
        )


@strawberry.type
class ExternalModelType:
    """GraphQL type for External Model."""
    id: str
    name: str
    model_type: str
    api_endpoint: str
    capabilities: List[str]
    integration_pattern: str
    is_active: bool
    created_at: str
    
    @classmethod
    def from_external_model(cls, model: ExternalModel) -> "ExternalModelType":
        """Convert ExternalModel to GraphQL type."""
        return cls(
            id=model.id,
            name=model.name,
            model_type=model.model_type.value,
            api_endpoint=model.api_endpoint,
            capabilities=[cap.value for cap in model.capabilities],
            integration_pattern=model.integration_pattern.value,
            is_active=model.is_active,
            created_at=model.created_at.isoformat()
        )


@strawberry.type
class ModelResponseType:
    """GraphQL type for Model Response."""
    model_id: str
    request_id: str
    response_data: str  # JSON string
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: float
    tokens_used: Optional[int] = None
    cached: bool
    timestamp: str
    
    @classmethod
    def from_model_response(cls, response: ModelResponse) -> "ModelResponseType":
        """Convert ModelResponse to GraphQL type."""
        import json
        return cls(
            model_id=response.model_id,
            request_id=response.request_id,
            response_data=json.dumps(response.response_data),
            success=response.success,
            error_message=response.error_message,
            processing_time_ms=response.processing_time_ms,
            tokens_used=response.tokens_used,
            cached=response.cached,
            timestamp=response.timestamp.isoformat()
        )


@strawberry.type
class CollectionInfoType:
    """GraphQL type for Collection Info."""
    name: str
    dimension: int
    vector_count: int
    created_at: str
    updated_at: Optional[str] = None
    metadata: Optional[str] = None  # JSON string


@strawberry.type
class HealthStatusType:
    """GraphQL type for Health Status."""
    status: str
    message: str
    timestamp: str
    details: Optional[str] = None  # JSON string


# GraphQL Input Types
@strawberry.input
class VectorSearchInput:
    """GraphQL input for vector search."""
    query_vector: List[float]
    collection: str
    limit: int = 10
    score_threshold: Optional[float] = None
    include_vectors: bool = False
    include_metadata: bool = True
    filter_conditions: Optional[str] = None  # JSON string


@strawberry.input
class EmbeddingInput:
    """GraphQL input for embedding generation."""
    text: List[str]
    model_name: str
    normalize: bool = True
    batch_size: int = 32
    max_length: int = 512


@strawberry.input
class ExternalModelCallInput:
    """GraphQL input for external model call."""
    model_id: str
    request_data: str  # JSON string


@strawberry.input
class VectorInsertInput:
    """GraphQL input for vector insertion."""
    id: Optional[str] = None
    embedding: List[float]
    metadata: Optional[str] = None  # JSON string
    collection: str


# GraphQL Resolvers
@strawberry.type
class Query:
    """GraphQL Query resolvers."""
    
    @strawberry.field
    async def vector_search(self, input: VectorSearchInput, info: Info) -> VectorSearchResultType:
        """Search for similar vectors."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # Parse filter conditions
            filter_conditions = None
            if input.filter_conditions:
                import json
                filter_conditions = json.loads(input.filter_conditions)
            
            # Create search request
            search_request = VectorSearchRequest(
                query_vector=input.query_vector,
                collection=input.collection,
                limit=input.limit,
                score_threshold=input.score_threshold,
                include_vectors=input.include_vectors,
                include_metadata=input.include_metadata,
                filter_conditions=filter_conditions
            )
            
            # Perform search
            result = await vector_db.vector_operations.search_vectors(search_request)
            
            return VectorSearchResultType.from_search_result(result)
            
        except Exception as e:
            logger.error(f"GraphQL vector search failed: {e}")
            raise Exception(f"Vector search failed: {e}")
    
    @strawberry.field
    async def get_vector(self, vector_id: str, collection: str, info: Info) -> Optional[VectorType]:
        """Get vector by ID."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # Get vector
            vector = await vector_db.vector_operations.get_vector(vector_id, collection)
            
            if vector:
                return VectorType.from_vector(vector)
            return None
            
        except Exception as e:
            logger.error(f"GraphQL get vector failed: {e}")
            raise Exception(f"Get vector failed: {e}")
    
    @strawberry.field
    async def list_collections(self, info: Info) -> List[CollectionInfoType]:
        """List all collections."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # This would call actual collection manager
            # For now, return mock data
            return [
                CollectionInfoType(
                    name="documents",
                    dimension=384,
                    vector_count=1000,
                    created_at=datetime.now().isoformat(),
                    metadata='{"description": "Document embeddings"}'
                ),
                CollectionInfoType(
                    name="embeddings",
                    dimension=768,
                    vector_count=500,
                    created_at=datetime.now().isoformat(),
                    metadata='{"description": "General embeddings"}'
                )
            ]
            
        except Exception as e:
            logger.error(f"GraphQL list collections failed: {e}")
            raise Exception(f"List collections failed: {e}")
    
    @strawberry.field
    async def list_external_models(self, info: Info) -> List[ExternalModelType]:
        """List all external models."""
        try:
            # Get model registry from context
            model_registry = info.context.get("model_registry")
            if not model_registry:
                raise Exception("Model registry not available")
            
            # Get models
            models = await model_registry.list_models()
            
            return [ExternalModelType.from_external_model(model) for model in models]
            
        except Exception as e:
            logger.error(f"GraphQL list external models failed: {e}")
            raise Exception(f"List external models failed: {e}")
    
    @strawberry.field
    async def health_check(self, info: Info) -> HealthStatusType:
        """Check system health."""
        try:
            # Get services from context
            vector_db = info.context.get("vector_db")
            api_gateway = info.context.get("api_gateway")
            
            # Perform health checks
            health_status = {
                "status": "healthy",
                "message": "System operational",
                "timestamp": datetime.now().isoformat()
            }
            
            if vector_db:
                db_health = await vector_db.health_check()
                health_status["database"] = db_health
            
            if api_gateway:
                gateway_health = await api_gateway.health_check()
                health_status["api_gateway"] = gateway_health
            
            import json
            return HealthStatusType(
                status=health_status["status"],
                message=health_status["message"],
                timestamp=health_status["timestamp"],
                details=json.dumps(health_status)
            )
            
        except Exception as e:
            logger.error(f"GraphQL health check failed: {e}")
            return HealthStatusType(
                status="unhealthy",
                message=f"Health check failed: {e}",
                timestamp=datetime.now().isoformat()
            )


@strawberry.type
class Mutation:
    """GraphQL Mutation resolvers."""
    
    @strawberry.mutation
    async def generate_embeddings(self, input: EmbeddingInput, info: Info) -> EmbeddingResponseType:
        """Generate embeddings for text."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # Create embedding request
            embedding_request = EmbeddingRequest(
                text=input.text,
                model_name=input.model_name,
                normalize=input.normalize,
                batch_size=input.batch_size,
                max_length=input.max_length
            )
            
            # Generate embeddings
            response = await vector_db.embedding_service.generate_embeddings(embedding_request)
            
            return EmbeddingResponseType.from_embedding_response(response)
            
        except Exception as e:
            logger.error(f"GraphQL generate embeddings failed: {e}")
            raise Exception(f"Generate embeddings failed: {e}")
    
    @strawberry.mutation
    async def insert_vector(self, input: VectorInsertInput, info: Info) -> VectorType:
        """Insert a vector into collection."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # Parse metadata
            metadata = None
            if input.metadata:
                import json
                metadata = json.loads(input.metadata)
            
            # Create vector
            vector = Vector(
                id=input.id,
                embedding=input.embedding,
                metadata=metadata,
                collection=input.collection
            )
            
            # Insert vector
            result = await vector_db.vector_operations.insert_vector(vector, input.collection)
            
            if result.success:
                return VectorType.from_vector(vector)
            else:
                raise Exception(result.message)
                
        except Exception as e:
            logger.error(f"GraphQL insert vector failed: {e}")
            raise Exception(f"Insert vector failed: {e}")
    
    @strawberry.mutation
    async def call_external_model(self, input: ExternalModelCallInput, info: Info) -> ModelResponseType:
        """Call external AI model."""
        try:
            # Get model registry from context
            model_registry = info.context.get("model_registry")
            if not model_registry:
                raise Exception("Model registry not available")
            
            # Parse request data
            import json
            request_data = json.loads(input.request_data)
            
            # Call model
            response_data = await model_registry.call_model(input.model_id, request_data)
            
            # Convert to ModelResponse
            response = ModelResponse(**response_data)
            
            return ModelResponseType.from_model_response(response)
            
        except Exception as e:
            logger.error(f"GraphQL external model call failed: {e}")
            raise Exception(f"External model call failed: {e}")
    
    @strawberry.mutation
    async def create_collection(self, name: str, dimension: int, info: Info) -> CollectionInfoType:
        """Create a new collection."""
        try:
            # Get vector database from context
            vector_db = info.context.get("vector_db")
            if not vector_db:
                raise Exception("Vector database not available")
            
            # This would call actual collection manager
            # For now, return mock response
            return CollectionInfoType(
                name=name,
                dimension=dimension,
                vector_count=0,
                created_at=datetime.now().isoformat(),
                metadata='{"created_via": "graphql"}'
            )
            
        except Exception as e:
            logger.error(f"GraphQL create collection failed: {e}")
            raise Exception(f"Create collection failed: {e}")


# Create GraphQL Schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
