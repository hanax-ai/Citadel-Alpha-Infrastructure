"""
GraphQL Schemas
==============

GraphQL schema definitions for the HANA-X Vector Database API.
Provides type definitions, queries, and mutations for vector operations.
"""

import strawberry
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


@strawberry.type
class VectorType:
    """GraphQL type for vector data."""
    id: str
    vector: List[float]
    payload: Optional[Dict[str, Any]] = None
    collection: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@strawberry.type
class CollectionType:
    """GraphQL type for collection information."""
    name: str
    vector_size: int
    distance: str
    points_count: int
    indexed_vectors_count: int
    status: str
    optimizer_status: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


@strawberry.type
class SearchResultType:
    """GraphQL type for search results."""
    id: str
    score: float
    payload: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None


@strawberry.type
class SearchResponseType:
    """GraphQL type for search response."""
    results: List[SearchResultType]
    total_count: int
    query_time: float
    collection: str


@strawberry.type
class BatchOperationResultType:
    """GraphQL type for batch operation results."""
    operation: str
    success_count: int
    failed_count: int
    total_count: int
    errors: Optional[List[str]] = None
    duration: float


@strawberry.type
class HealthCheckType:
    """GraphQL type for health check results."""
    name: str
    status: str
    message: str
    last_check: datetime
    duration: float
    details: Optional[Dict[str, Any]] = None


@strawberry.type
class SystemHealthType:
    """GraphQL type for system health status."""
    status: str
    timestamp: datetime
    checks: List[HealthCheckType]
    summary: Dict[str, Any]


@strawberry.type
class MetricsType:
    """GraphQL type for system metrics."""
    name: str
    value: float
    labels: Optional[Dict[str, str]] = None
    timestamp: datetime


@strawberry.type
class CollectionStatsType:
    """GraphQL type for collection statistics."""
    collection: str
    points_count: int
    indexed_vectors_count: int
    memory_usage: Optional[int] = None
    disk_usage: Optional[int] = None
    avg_vector_size: Optional[float] = None


@strawberry.input
class VectorInput:
    """GraphQL input type for vector data."""
    id: Optional[str] = None
    vector: List[float]
    payload: Optional[Dict[str, Any]] = None


@strawberry.input
class SearchInput:
    """GraphQL input type for search queries."""
    vector: List[float]
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    filter: Optional[Dict[str, Any]] = None
    score_threshold: Optional[float] = None
    with_payload: Optional[bool] = True
    with_vector: Optional[bool] = False


@strawberry.input
class CollectionConfigInput:
    """GraphQL input type for collection configuration."""
    vector_size: int
    distance: str = "cosine"
    shard_number: Optional[int] = 1
    replication_factor: Optional[int] = 1
    write_consistency_factor: Optional[int] = 1


@strawberry.input
class BatchVectorInput:
    """GraphQL input type for batch vector operations."""
    vectors: List[VectorInput]
    operation: str = "insert"


@strawberry.type
class Query:
    """GraphQL query root."""
    
    @strawberry.field
    async def vector(self, collection: str, id: str) -> Optional[VectorType]:
        """Get a specific vector by ID."""
        # This would be implemented with actual vector operations
        return None
    
    @strawberry.field
    async def vectors(self, collection: str, limit: int = 10, offset: int = 0) -> List[VectorType]:
        """Get vectors from a collection."""
        # This would be implemented with actual vector operations
        return []
    
    @strawberry.field
    async def search(self, collection: str, query: SearchInput) -> SearchResponseType:
        """Search for similar vectors."""
        # This would be implemented with actual search operations
        return SearchResponseType(
            results=[],
            total_count=0,
            query_time=0.0,
            collection=collection
        )
    
    @strawberry.field
    async def multi_search(self, queries: List[SearchInput], collections: List[str]) -> List[SearchResponseType]:
        """Perform multiple searches across collections."""
        # This would be implemented with actual multi-search operations
        return []
    
    @strawberry.field
    async def collection(self, name: str) -> Optional[CollectionType]:
        """Get collection information."""
        # This would be implemented with actual collection operations
        return None
    
    @strawberry.field
    async def collections(self) -> List[CollectionType]:
        """Get all collections."""
        # This would be implemented with actual collection operations
        return []
    
    @strawberry.field
    async def collection_stats(self, name: str) -> Optional[CollectionStatsType]:
        """Get collection statistics."""
        # This would be implemented with actual statistics operations
        return None
    
    @strawberry.field
    async def health(self) -> SystemHealthType:
        """Get system health status."""
        # This would be implemented with actual health monitoring
        return SystemHealthType(
            status="healthy",
            timestamp=datetime.now(),
            checks=[],
            summary={}
        )
    
    @strawberry.field
    async def metrics(self, names: Optional[List[str]] = None) -> List[MetricsType]:
        """Get system metrics."""
        # This would be implemented with actual metrics collection
        return []
    
    @strawberry.field
    async def search_recommendations(self, collection: str, vector: List[float], 
                                   limit: int = 5) -> List[SearchResultType]:
        """Get search recommendations based on vector similarity."""
        # This would be implemented with recommendation algorithms
        return []


@strawberry.type
class Mutation:
    """GraphQL mutation root."""
    
    @strawberry.mutation
    async def insert_vector(self, collection: str, vector: VectorInput) -> VectorType:
        """Insert a single vector."""
        # This would be implemented with actual vector operations
        return VectorType(
            id=vector.id or "generated_id",
            vector=vector.vector,
            payload=vector.payload,
            collection=collection,
            created_at=datetime.now()
        )
    
    @strawberry.mutation
    async def insert_vectors(self, collection: str, vectors: List[VectorInput]) -> BatchOperationResultType:
        """Insert multiple vectors."""
        # This would be implemented with actual batch operations
        return BatchOperationResultType(
            operation="insert",
            success_count=len(vectors),
            failed_count=0,
            total_count=len(vectors),
            duration=0.0
        )
    
    @strawberry.mutation
    async def update_vector(self, collection: str, id: str, vector: VectorInput) -> VectorType:
        """Update a vector."""
        # This would be implemented with actual vector operations
        return VectorType(
            id=id,
            vector=vector.vector,
            payload=vector.payload,
            collection=collection,
            updated_at=datetime.now()
        )
    
    @strawberry.mutation
    async def delete_vector(self, collection: str, id: str) -> bool:
        """Delete a vector."""
        # This would be implemented with actual vector operations
        return True
    
    @strawberry.mutation
    async def delete_vectors(self, collection: str, ids: List[str]) -> BatchOperationResultType:
        """Delete multiple vectors."""
        # This would be implemented with actual batch operations
        return BatchOperationResultType(
            operation="delete",
            success_count=len(ids),
            failed_count=0,
            total_count=len(ids),
            duration=0.0
        )
    
    @strawberry.mutation
    async def batch_operation(self, collection: str, batch: BatchVectorInput) -> BatchOperationResultType:
        """Perform batch vector operations."""
        # This would be implemented with actual batch operations
        return BatchOperationResultType(
            operation=batch.operation,
            success_count=len(batch.vectors),
            failed_count=0,
            total_count=len(batch.vectors),
            duration=0.0
        )
    
    @strawberry.mutation
    async def create_collection(self, name: str, config: CollectionConfigInput) -> CollectionType:
        """Create a new collection."""
        # This would be implemented with actual collection operations
        return CollectionType(
            name=name,
            vector_size=config.vector_size,
            distance=config.distance,
            points_count=0,
            indexed_vectors_count=0,
            status="active",
            created_at=datetime.now()
        )
    
    @strawberry.mutation
    async def update_collection(self, name: str, config: CollectionConfigInput) -> CollectionType:
        """Update collection configuration."""
        # This would be implemented with actual collection operations
        return CollectionType(
            name=name,
            vector_size=config.vector_size,
            distance=config.distance,
            points_count=0,
            indexed_vectors_count=0,
            status="active"
        )
    
    @strawberry.mutation
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        # This would be implemented with actual collection operations
        return True
    
    @strawberry.mutation
    async def optimize_collection(self, name: str) -> bool:
        """Optimize a collection."""
        # This would be implemented with actual optimization operations
        return True
    
    @strawberry.mutation
    async def clear_collection(self, name: str) -> bool:
        """Clear all vectors from a collection."""
        # This would be implemented with actual collection operations
        return True
    
    @strawberry.mutation
    async def reindex_collection(self, name: str) -> bool:
        """Reindex a collection."""
        # This would be implemented with actual indexing operations
        return True


@strawberry.type
class Subscription:
    """GraphQL subscription root."""
    
    @strawberry.subscription
    async def vector_updates(self, collection: str) -> VectorType:
        """Subscribe to vector updates in a collection."""
        # This would be implemented with actual subscription mechanism
        yield VectorType(
            id="example",
            vector=[0.1, 0.2, 0.3],
            collection=collection,
            created_at=datetime.now()
        )
    
    @strawberry.subscription
    async def collection_stats(self, collection: str) -> CollectionStatsType:
        """Subscribe to collection statistics updates."""
        # This would be implemented with actual statistics streaming
        yield CollectionStatsType(
            collection=collection,
            points_count=0,
            indexed_vectors_count=0
        )
    
    @strawberry.subscription
    async def health_updates(self) -> SystemHealthType:
        """Subscribe to system health updates."""
        # This would be implemented with actual health monitoring
        yield SystemHealthType(
            status="healthy",
            timestamp=datetime.now(),
            checks=[],
            summary={}
        )
    
    @strawberry.subscription
    async def metrics_stream(self, metric_names: Optional[List[str]] = None) -> MetricsType:
        """Subscribe to metrics updates."""
        # This would be implemented with actual metrics streaming
        yield MetricsType(
            name="example_metric",
            value=0.0,
            timestamp=datetime.now()
        )


def create_graphql_schema():
    """
    Create GraphQL schema.
    
    Returns:
        Strawberry GraphQL schema
    """
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription
    )


# Custom scalars for complex types
@strawberry.scalar(
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class JSON:
    """Custom JSON scalar type."""
    pass


# Schema extensions for custom directives
@strawberry.directive(
    locations=[strawberry.directive.Location.FIELD_DEFINITION],
    description="Mark field as requiring authentication"
)
def auth_required() -> None:
    """Authentication required directive."""
    pass


@strawberry.directive(
    locations=[strawberry.directive.Location.FIELD_DEFINITION],
    description="Mark field as deprecated"
)
def deprecated(reason: str) -> None:
    """Deprecation directive."""
    pass


@strawberry.directive(
    locations=[strawberry.directive.Location.FIELD_DEFINITION],
    description="Rate limit directive"
)
def rate_limit(max_requests: int, window: int) -> None:
    """Rate limiting directive."""
    pass


# Schema validation utilities
def validate_schema():
    """Validate GraphQL schema."""
    try:
        schema = create_graphql_schema()
        # Basic validation - in production would use graphql-core validation
        return True, "Schema is valid"
    except Exception as e:
        return False, f"Schema validation failed: {str(e)}"


def get_schema_sdl():
    """
    Get Schema Definition Language representation.
    
    Returns:
        SDL string
    """
    schema = create_graphql_schema()
    return strawberry.export_schema.get_schema_from_schema(schema)


def get_introspection_query():
    """
    Get GraphQL introspection query.
    
    Returns:
        Introspection query string
    """
    return """
    query IntrospectionQuery {
        __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
                ...FullType
            }
            directives {
                name
                description
                locations
                args {
                    ...InputValue
                }
            }
        }
    }
    
    fragment FullType on __Type {
        kind
        name
        description
        fields(includeDeprecated: true) {
            name
            description
            args {
                ...InputValue
            }
            type {
                ...TypeRef
            }
            isDeprecated
            deprecationReason
        }
        inputFields {
            ...InputValue
        }
        interfaces {
            ...TypeRef
        }
        enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
        }
        possibleTypes {
            ...TypeRef
        }
    }
    
    fragment InputValue on __InputValue {
        name
        description
        type { ...TypeRef }
        defaultValue
    }
    
    fragment TypeRef on __Type {
        kind
        name
        ofType {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """


# Schema documentation utilities
def get_schema_documentation():
    """
    Get schema documentation.
    
    Returns:
        Documentation dictionary
    """
    return {
        "title": "HANA-X Vector Database GraphQL API",
        "version": "1.0.0",
        "description": "GraphQL API for vector database operations",
        "queries": {
            "vector": "Get a specific vector by ID",
            "vectors": "Get vectors from a collection",
            "search": "Search for similar vectors",
            "multi_search": "Perform multiple searches across collections",
            "collection": "Get collection information",
            "collections": "Get all collections",
            "health": "Get system health status",
            "metrics": "Get system metrics"
        },
        "mutations": {
            "insert_vector": "Insert a single vector",
            "insert_vectors": "Insert multiple vectors",
            "update_vector": "Update a vector",
            "delete_vector": "Delete a vector",
            "delete_vectors": "Delete multiple vectors",
            "batch_operation": "Perform batch vector operations",
            "create_collection": "Create a new collection",
            "update_collection": "Update collection configuration",
            "delete_collection": "Delete a collection",
            "optimize_collection": "Optimize a collection"
        },
        "subscriptions": {
            "vector_updates": "Subscribe to vector updates in a collection",
            "collection_stats": "Subscribe to collection statistics updates",
            "health_updates": "Subscribe to system health updates",
            "metrics_stream": "Subscribe to metrics updates"
        }
    }
