"""
gRPC Schemas
===========

gRPC service definitions and protocol buffer schemas for the HANA-X Vector Database API.
Provides high-performance gRPC interface for vector operations.
"""

import grpc
from concurrent import futures
import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
import json


# Protocol Buffer Message Definitions (would normally be generated from .proto files)
class VectorProto:
    """Protocol buffer message for vector data."""
    
    def __init__(self, id: str = "", vector: List[float] = None, 
                 payload: Dict[str, Any] = None, collection: str = ""):
        self.id = id
        self.vector = vector or []
        self.payload = payload or {}
        self.collection = collection
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "vector": self.vector,
            "payload": self.payload,
            "collection": self.collection,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorProto':
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            vector=data.get("vector", []),
            payload=data.get("payload", {}),
            collection=data.get("collection", "")
        )


class SearchRequestProto:
    """Protocol buffer message for search requests."""
    
    def __init__(self, collection: str = "", vector: List[float] = None,
                 limit: int = 10, offset: int = 0, filter: Dict[str, Any] = None,
                 score_threshold: float = 0.0, with_payload: bool = True,
                 with_vector: bool = False):
        self.collection = collection
        self.vector = vector or []
        self.limit = limit
        self.offset = offset
        self.filter = filter or {}
        self.score_threshold = score_threshold
        self.with_payload = with_payload
        self.with_vector = with_vector
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "collection": self.collection,
            "vector": self.vector,
            "limit": self.limit,
            "offset": self.offset,
            "filter": self.filter,
            "score_threshold": self.score_threshold,
            "with_payload": self.with_payload,
            "with_vector": self.with_vector
        }


class SearchResultProto:
    """Protocol buffer message for search results."""
    
    def __init__(self, id: str = "", score: float = 0.0,
                 payload: Dict[str, Any] = None, vector: List[float] = None):
        self.id = id
        self.score = score
        self.payload = payload or {}
        self.vector = vector or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "score": self.score,
            "payload": self.payload,
            "vector": self.vector
        }


class SearchResponseProto:
    """Protocol buffer message for search responses."""
    
    def __init__(self, results: List[SearchResultProto] = None,
                 total_count: int = 0, query_time: float = 0.0,
                 collection: str = ""):
        self.results = results or []
        self.total_count = total_count
        self.query_time = query_time
        self.collection = collection
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total_count": self.total_count,
            "query_time": self.query_time,
            "collection": self.collection
        }


class CollectionProto:
    """Protocol buffer message for collection information."""
    
    def __init__(self, name: str = "", vector_size: int = 0,
                 distance: str = "cosine", points_count: int = 0,
                 indexed_vectors_count: int = 0, status: str = "active"):
        self.name = name
        self.vector_size = vector_size
        self.distance = distance
        self.points_count = points_count
        self.indexed_vectors_count = indexed_vectors_count
        self.status = status
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "vector_size": self.vector_size,
            "distance": self.distance,
            "points_count": self.points_count,
            "indexed_vectors_count": self.indexed_vectors_count,
            "status": self.status,
            "created_at": self.created_at
        }


class BatchRequestProto:
    """Protocol buffer message for batch requests."""
    
    def __init__(self, operation: str = "insert", vectors: List[VectorProto] = None,
                 collection: str = ""):
        self.operation = operation
        self.vectors = vectors or []
        self.collection = collection
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "vectors": [v.to_dict() for v in self.vectors],
            "collection": self.collection
        }


class BatchResponseProto:
    """Protocol buffer message for batch responses."""
    
    def __init__(self, operation: str = "", success_count: int = 0,
                 failed_count: int = 0, total_count: int = 0,
                 errors: List[str] = None, duration: float = 0.0):
        self.operation = operation
        self.success_count = success_count
        self.failed_count = failed_count
        self.total_count = total_count
        self.errors = errors or []
        self.duration = duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "total_count": self.total_count,
            "errors": self.errors,
            "duration": self.duration
        }


class HealthStatusProto:
    """Protocol buffer message for health status."""
    
    def __init__(self, status: str = "unknown", timestamp: str = "",
                 checks: Dict[str, Any] = None, summary: Dict[str, Any] = None):
        self.status = status
        self.timestamp = timestamp or datetime.now().isoformat()
        self.checks = checks or {}
        self.summary = summary or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "checks": self.checks,
            "summary": self.summary
        }


class VectorServicer:
    """
    gRPC service implementation for vector database operations.
    Provides high-performance async gRPC interface.
    """
    
    def __init__(self, vector_ops_manager=None, collection_manager=None,
                 health_monitor=None, metrics_collector=None):
        self.vector_ops_manager = vector_ops_manager
        self.collection_manager = collection_manager
        self.health_monitor = health_monitor
        self.metrics_collector = metrics_collector
    
    async def InsertVector(self, request: VectorProto, context) -> VectorProto:
        """Insert a single vector."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("InsertVector")
            
            # Validate request
            if not request.vector:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Vector data is required")
                return VectorProto()
            
            # Perform insertion (would use actual vector_ops_manager)
            result = VectorProto(
                id=request.id or f"generated_{datetime.now().timestamp()}",
                vector=request.vector,
                payload=request.payload,
                collection=request.collection
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("InsertVector")
            
            return result
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("InsertVector", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Insert failed: {str(e)}")
            return VectorProto()
    
    async def SearchVectors(self, request: SearchRequestProto, context) -> SearchResponseProto:
        """Search for similar vectors."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("SearchVectors")
            
            # Validate request
            if not request.vector:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Query vector is required")
                return SearchResponseProto()
            
            if not request.collection:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Collection name is required")
                return SearchResponseProto()
            
            # Perform search (would use actual search engine)
            results = [
                SearchResultProto(
                    id=f"result_{i}",
                    score=0.9 - (i * 0.1),
                    payload={"index": i},
                    vector=request.vector if request.with_vector else []
                )
                for i in range(min(request.limit, 3))  # Mock results
            ]
            
            response = SearchResponseProto(
                results=results,
                total_count=len(results),
                query_time=0.005,
                collection=request.collection
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("SearchVectors")
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("SearchVectors", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Search failed: {str(e)}")
            return SearchResponseProto()
    
    async def UpdateVector(self, request: VectorProto, context) -> VectorProto:
        """Update a vector."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("UpdateVector")
            
            # Validate request
            if not request.id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Vector ID is required")
                return VectorProto()
            
            # Perform update (would use actual vector_ops_manager)
            result = VectorProto(
                id=request.id,
                vector=request.vector,
                payload=request.payload,
                collection=request.collection
            )
            result.updated_at = datetime.now().isoformat()
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("UpdateVector")
            
            return result
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("UpdateVector", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Update failed: {str(e)}")
            return VectorProto()
    
    async def DeleteVector(self, request, context) -> BatchResponseProto:
        """Delete a vector."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("DeleteVector")
            
            # Validate request
            if not hasattr(request, 'id') or not request.id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Vector ID is required")
                return BatchResponseProto()
            
            # Perform deletion (would use actual vector_ops_manager)
            response = BatchResponseProto(
                operation="delete",
                success_count=1,
                failed_count=0,
                total_count=1,
                duration=0.001
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("DeleteVector")
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("DeleteVector", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Delete failed: {str(e)}")
            return BatchResponseProto()
    
    async def BatchOperation(self, request: BatchRequestProto, context) -> BatchResponseProto:
        """Perform batch operations."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("BatchOperation")
            
            # Validate request
            if not request.vectors:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Vectors are required for batch operation")
                return BatchResponseProto()
            
            # Perform batch operation (would use actual batch processor)
            response = BatchResponseProto(
                operation=request.operation,
                success_count=len(request.vectors),
                failed_count=0,
                total_count=len(request.vectors),
                duration=0.1
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("BatchOperation")
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("BatchOperation", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Batch operation failed: {str(e)}")
            return BatchResponseProto()
    
    async def GetCollection(self, request, context) -> CollectionProto:
        """Get collection information."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("GetCollection")
            
            # Validate request
            if not hasattr(request, 'name') or not request.name:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Collection name is required")
                return CollectionProto()
            
            # Get collection info (would use actual collection manager)
            collection = CollectionProto(
                name=request.name,
                vector_size=384,
                distance="cosine",
                points_count=1000,
                indexed_vectors_count=1000,
                status="active"
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("GetCollection")
            
            return collection
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("GetCollection", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Get collection failed: {str(e)}")
            return CollectionProto()
    
    async def ListCollections(self, request, context) -> AsyncIterator[CollectionProto]:
        """List all collections."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("ListCollections")
            
            # Get collections (would use actual collection manager)
            collections = [
                CollectionProto(
                    name=f"collection_{i}",
                    vector_size=384,
                    distance="cosine",
                    points_count=1000 * i,
                    indexed_vectors_count=1000 * i,
                    status="active"
                )
                for i in range(1, 4)  # Mock collections
            ]
            
            for collection in collections:
                yield collection
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("ListCollections")
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("ListCollections", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"List collections failed: {str(e)}")
    
    async def CreateCollection(self, request, context) -> CollectionProto:
        """Create a new collection."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("CreateCollection")
            
            # Validate request
            if not hasattr(request, 'name') or not request.name:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Collection name is required")
                return CollectionProto()
            
            # Create collection (would use actual collection manager)
            collection = CollectionProto(
                name=request.name,
                vector_size=getattr(request, 'vector_size', 384),
                distance=getattr(request, 'distance', 'cosine'),
                points_count=0,
                indexed_vectors_count=0,
                status="active"
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("CreateCollection")
            
            return collection
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("CreateCollection", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Create collection failed: {str(e)}")
            return CollectionProto()
    
    async def DeleteCollection(self, request, context) -> BatchResponseProto:
        """Delete a collection."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("DeleteCollection")
            
            # Validate request
            if not hasattr(request, 'name') or not request.name:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Collection name is required")
                return BatchResponseProto()
            
            # Delete collection (would use actual collection manager)
            response = BatchResponseProto(
                operation="delete_collection",
                success_count=1,
                failed_count=0,
                total_count=1,
                duration=0.01
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("DeleteCollection")
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("DeleteCollection", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Delete collection failed: {str(e)}")
            return BatchResponseProto()
    
    async def GetHealth(self, request, context) -> HealthStatusProto:
        """Get system health status."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("GetHealth")
            
            # Get health status (would use actual health monitor)
            health = HealthStatusProto(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                checks={
                    "qdrant_connection": {"status": "healthy", "message": "OK"},
                    "cache": {"status": "healthy", "message": "OK"}
                },
                summary={
                    "total_checks": 2,
                    "healthy_checks": 2,
                    "unhealthy_checks": 0
                }
            )
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("GetHealth")
            
            return health
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("GetHealth", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Get health failed: {str(e)}")
            return HealthStatusProto()
    
    async def StreamSearch(self, request: SearchRequestProto, context) -> AsyncIterator[SearchResultProto]:
        """Stream search results."""
        try:
            # Record metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_request("StreamSearch")
            
            # Validate request
            if not request.vector:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Query vector is required")
                return
            
            # Stream search results (would use actual search engine)
            for i in range(min(request.limit, 10)):
                result = SearchResultProto(
                    id=f"stream_result_{i}",
                    score=0.9 - (i * 0.05),
                    payload={"stream_index": i},
                    vector=request.vector if request.with_vector else []
                )
                yield result
                
                # Simulate streaming delay
                await asyncio.sleep(0.01)
            
            # Record success metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success("StreamSearch")
            
        except Exception as e:
            # Record error metrics
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error("StreamSearch", str(e))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Stream search failed: {str(e)}")


def create_grpc_server(servicer: VectorServicer, port: int = 50051,
                      max_workers: int = 10) -> grpc.aio.Server:
    """
    Create gRPC server with vector service.
    
    Args:
        servicer: Vector service implementation
        port: Server port
        max_workers: Maximum worker threads
        
    Returns:
        gRPC server instance
    """
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    
    # Add servicer to server (would normally use generated add_VectorServiceServicer_to_server)
    # server.add_VectorServiceServicer_to_server(servicer, server)
    
    # Add insecure port
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    return server


def get_proto_definitions() -> str:
    """
    Get protocol buffer definitions.
    
    Returns:
        Proto file content as string
    """
    return '''
syntax = "proto3";

package hana_x_vector;

// Vector service definition
service VectorService {
    // Vector operations
    rpc InsertVector(VectorRequest) returns (VectorResponse);
    rpc SearchVectors(SearchRequest) returns (SearchResponse);
    rpc UpdateVector(VectorRequest) returns (VectorResponse);
    rpc DeleteVector(DeleteRequest) returns (BatchResponse);
    rpc BatchOperation(BatchRequest) returns (BatchResponse);
    
    // Collection operations
    rpc GetCollection(CollectionRequest) returns (CollectionResponse);
    rpc ListCollections(Empty) returns (stream CollectionResponse);
    rpc CreateCollection(CreateCollectionRequest) returns (CollectionResponse);
    rpc DeleteCollection(CollectionRequest) returns (BatchResponse);
    
    // Health and monitoring
    rpc GetHealth(Empty) returns (HealthResponse);
    
    // Streaming operations
    rpc StreamSearch(SearchRequest) returns (stream SearchResult);
}

// Message definitions
message VectorRequest {
    string id = 1;
    repeated float vector = 2;
    map<string, string> payload = 3;
    string collection = 4;
}

message VectorResponse {
    string id = 1;
    repeated float vector = 2;
    map<string, string> payload = 3;
    string collection = 4;
    string created_at = 5;
    string updated_at = 6;
}

message SearchRequest {
    string collection = 1;
    repeated float vector = 2;
    int32 limit = 3;
    int32 offset = 4;
    map<string, string> filter = 5;
    float score_threshold = 6;
    bool with_payload = 7;
    bool with_vector = 8;
}

message SearchResult {
    string id = 1;
    float score = 2;
    map<string, string> payload = 3;
    repeated float vector = 4;
}

message SearchResponse {
    repeated SearchResult results = 1;
    int32 total_count = 2;
    float query_time = 3;
    string collection = 4;
}

message BatchRequest {
    string operation = 1;
    repeated VectorRequest vectors = 2;
    string collection = 3;
}

message BatchResponse {
    string operation = 1;
    int32 success_count = 2;
    int32 failed_count = 3;
    int32 total_count = 4;
    repeated string errors = 5;
    float duration = 6;
}

message CollectionRequest {
    string name = 1;
}

message CreateCollectionRequest {
    string name = 1;
    int32 vector_size = 2;
    string distance = 3;
    int32 shard_number = 4;
    int32 replication_factor = 5;
}

message CollectionResponse {
    string name = 1;
    int32 vector_size = 2;
    string distance = 3;
    int32 points_count = 4;
    int32 indexed_vectors_count = 5;
    string status = 6;
    string created_at = 7;
}

message DeleteRequest {
    string id = 1;
    string collection = 2;
}

message HealthResponse {
    string status = 1;
    string timestamp = 2;
    map<string, string> checks = 3;
    map<string, string> summary = 4;
}

message Empty {}
'''


# gRPC utilities
def create_grpc_client(host: str = "localhost", port: int = 50051):
    """
    Create gRPC client.
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        gRPC client stub
    """
    channel = grpc.aio.insecure_channel(f'{host}:{port}')
    # Would normally return generated VectorServiceStub(channel)
    return channel


def setup_grpc_interceptors():
    """Setup gRPC interceptors for logging, metrics, etc."""
    # Would implement actual interceptors
    pass


def create_grpc_health_check():
    """Create gRPC health check service."""
    # Would implement health check service
    pass


# gRPC middleware
class MetricsInterceptor:
    """gRPC interceptor for metrics collection."""
    
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept unary-unary calls."""
        method_name = client_call_details.method.split('/')[-1]
        
        # Record request
        if self.metrics_collector:
            self.metrics_collector.record_grpc_request(method_name)
        
        try:
            response = await continuation(client_call_details, request)
            
            # Record success
            if self.metrics_collector:
                self.metrics_collector.record_grpc_success(method_name)
            
            return response
            
        except Exception as e:
            # Record error
            if self.metrics_collector:
                self.metrics_collector.record_grpc_error(method_name, str(e))
            
            raise


class AuthInterceptor:
    """gRPC interceptor for authentication."""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept unary-unary calls for authentication."""
        # Extract API key from metadata
        metadata = dict(client_call_details.metadata or [])
        api_key = metadata.get('api-key')
        
        if not api_key or api_key not in self.api_keys:
            raise grpc.RpcError("Invalid API key")
        
        return await continuation(client_call_details, request)


# gRPC server management
class GrpcServerManager:
    """gRPC server lifecycle management."""
    
    def __init__(self, servicer: VectorServicer, port: int = 50051):
        self.servicer = servicer
        self.port = port
        self.server = None
    
    async def start(self):
        """Start gRPC server."""
        self.server = create_grpc_server(self.servicer, self.port)
        await self.server.start()
        print(f"gRPC server started on port {self.port}")
    
    async def stop(self):
        """Stop gRPC server."""
        if self.server:
            await self.server.stop(grace=5)
            print("gRPC server stopped")
    
    async def wait_for_termination(self):
        """Wait for server termination."""
        if self.server:
            await self.server.wait_for_termination()
