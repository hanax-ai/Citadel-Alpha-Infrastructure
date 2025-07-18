"""
gRPC API Handler
===============

gRPC service implementation for high-performance vector database operations.
Provides protocol buffer-based API for vector operations.
"""

from typing import Dict, Any, List, Optional
import asyncio
import grpc
from grpc import aio
from concurrent import futures
from ..vector_ops.operations import VectorOperationsManager
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError
from ..schemas.grpc_proto import vector_service_pb2, vector_service_pb2_grpc


class VectorServiceServicer(vector_service_pb2_grpc.VectorServiceServicer):
    """gRPC service implementation for vector operations."""
    
    def __init__(self, vector_ops: VectorOperationsManager, metrics: MetricsCollector):
        self.vector_ops = vector_ops
        self.metrics = metrics
    
    async def InsertVectors(self, request, context):
        """Insert vectors into a collection."""
        try:
            # Convert protobuf request to dict format
            vectors = []
            for vector_data in request.vectors:
                vectors.append({
                    "id": vector_data.id,
                    "vector": list(vector_data.vector),
                    "metadata": dict(vector_data.metadata) if vector_data.metadata else {}
                })
            
            # Insert vectors
            result = await self.vector_ops.insert_vectors(
                collection_name=request.collection,
                vectors=vectors,
                batch_size=request.batch_size or 1000
            )
            
            self.metrics.increment_counter("grpc_inserts", len(vectors))
            
            return vector_service_pb2.InsertResponse(
                status="success",
                inserted_count=result["inserted_count"],
                duration=result["duration"]
            )
            
        except VectorOperationError as e:
            self.metrics.increment_counter("grpc_insert_errors")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return vector_service_pb2.InsertResponse()
        except Exception as e:
            self.metrics.increment_counter("grpc_insert_errors")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.InsertResponse()
    
    async def SearchVectors(self, request, context):
        """Search for similar vectors."""
        try:
            # Convert protobuf filters to dict
            filters = dict(request.filters) if request.filters else None
            score_threshold = request.score_threshold if request.score_threshold > 0 else None
            
            # Perform search
            result = await self.vector_ops.similarity_search(
                collection_name=request.collection,
                query_vector=list(request.query_vector),
                limit=request.limit or 10,
                filters=filters,
                score_threshold=score_threshold
            )
            
            # Convert results to protobuf format
            search_results = []
            for r in result["results"]:
                search_result = vector_service_pb2.SearchResult(
                    id=r["id"],
                    score=r["score"]
                )
                if r.get("metadata"):
                    search_result.metadata.update(r["metadata"])
                search_results.append(search_result)
            
            self.metrics.increment_counter("grpc_searches")
            self.metrics.record_histogram("grpc_search_latency", result["duration"])
            
            return vector_service_pb2.SearchResponse(
                results=search_results,
                count=len(search_results),
                duration=result["duration"]
            )
            
        except VectorOperationError as e:
            self.metrics.increment_counter("grpc_search_errors")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return vector_service_pb2.SearchResponse()
        except Exception as e:
            self.metrics.increment_counter("grpc_search_errors")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.SearchResponse()
    
    async def UpdateVector(self, request, context):
        """Update a vector in a collection."""
        try:
            vector = list(request.vector) if request.vector else None
            metadata = dict(request.metadata) if request.metadata else None
            
            result = await self.vector_ops.update_vector(
                collection_name=request.collection,
                vector_id=request.vector_id,
                vector=vector,
                metadata=metadata
            )
            
            self.metrics.increment_counter("grpc_updates")
            
            return vector_service_pb2.UpdateResponse(
                status="success",
                updated=result["updated"]
            )
            
        except VectorOperationError as e:
            self.metrics.increment_counter("grpc_update_errors")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return vector_service_pb2.UpdateResponse()
        except Exception as e:
            self.metrics.increment_counter("grpc_update_errors")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.UpdateResponse()
    
    async def DeleteVector(self, request, context):
        """Delete a vector from a collection."""
        try:
            result = await self.vector_ops.delete_vector(
                collection_name=request.collection,
                vector_id=request.vector_id
            )
            
            self.metrics.increment_counter("grpc_deletes")
            
            return vector_service_pb2.DeleteResponse(
                status="success",
                deleted=result["deleted"]
            )
            
        except VectorOperationError as e:
            self.metrics.increment_counter("grpc_delete_errors")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return vector_service_pb2.DeleteResponse()
        except Exception as e:
            self.metrics.increment_counter("grpc_delete_errors")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.DeleteResponse()
    
    async def CreateCollection(self, request, context):
        """Create a new vector collection."""
        try:
            config = dict(request.config) if request.config else None
            
            result = await self.vector_ops.create_collection(
                name=request.name,
                vector_size=request.vector_size,
                distance=request.distance or "Cosine",
                config=config
            )
            
            self.metrics.increment_counter("grpc_collections_created")
            
            return vector_service_pb2.CollectionResponse(
                status="success",
                created=result["created"]
            )
            
        except VectorOperationError as e:
            self.metrics.increment_counter("grpc_collection_create_errors")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return vector_service_pb2.CollectionResponse()
        except Exception as e:
            self.metrics.increment_counter("grpc_collection_create_errors")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.CollectionResponse()
    
    async def ListCollections(self, request, context):
        """List all collections."""
        try:
            result = await self.vector_ops.list_collections()
            
            return vector_service_pb2.ListCollectionsResponse(
                collections=result["collections"]
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.ListCollectionsResponse()
    
    async def GetCollectionInfo(self, request, context):
        """Get collection information."""
        try:
            result = await self.vector_ops.get_collection_info(request.collection)
            info = result["info"]
            
            collection_info = vector_service_pb2.CollectionInfo(
                name=request.collection,
                vector_size=info["vector_size"],
                distance=info["distance"],
                points_count=info["points_count"]
            )
            
            if info.get("config"):
                collection_info.config.update(info["config"])
            
            return vector_service_pb2.CollectionInfoResponse(
                info=collection_info
            )
            
        except VectorOperationError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return vector_service_pb2.CollectionInfoResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return vector_service_pb2.CollectionInfoResponse()


class GRPCHandler:
    """gRPC API handler for vector database operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vector_ops = VectorOperationsManager(config)
        self.metrics = MetricsCollector()
        self.server = None
        self.servicer = None
    
    async def startup(self):
        """Initialize gRPC handler."""
        await self.vector_ops.startup()
        self.servicer = VectorServiceServicer(self.vector_ops, self.metrics)
    
    async def shutdown(self):
        """Cleanup gRPC handler."""
        if self.server:
            await self.server.stop(grace=5)
        await self.vector_ops.shutdown()
    
    async def start_server(self, port: int = 6334):
        """Start the gRPC server."""
        self.server = aio.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Add the service
        vector_service_pb2_grpc.add_VectorServiceServicer_to_server(
            self.servicer, self.server
        )
        
        # Configure server options
        listen_addr = f"[::]:{port}"
        self.server.add_insecure_port(listen_addr)
        
        # Start server
        await self.server.start()
        print(f"gRPC server started on port {port}")
        
        # Wait for termination
        await self.server.wait_for_termination()
    
    async def stop_server(self):
        """Stop the gRPC server."""
        if self.server:
            await self.server.stop(grace=5)
            self.server = None
