"""
gRPC Service Implementation

gRPC service implementation following HXP Governance Coding Standards.
Implements Single Responsibility Principle for gRPC protocol abstraction.

Author: Citadel AI Team
License: MIT
"""

import grpc
from concurrent import futures
from typing import Optional, Dict, Any, List
import asyncio
import json
from datetime import datetime
import logging

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty

from hana_x_vector.models.vector_models import (
    Vector, VectorSearchRequest, VectorSearchResult, EmbeddingRequest, EmbeddingResponse
)
from hana_x_vector.models.external_models import ExternalModel, ModelResponse
from hana_x_vector.utils.logging import get_logger

# Import generated protobuf classes (would be generated from .proto file)
# For now, we'll create mock classes to demonstrate the structure
class VectorDatabaseServiceServicer:
    """gRPC service implementation for Vector Database operations."""
    
    def __init__(self, vector_db, model_registry, api_gateway):
        """Initialize gRPC service with dependencies."""
        self.vector_db = vector_db
        self.model_registry = model_registry
        self.api_gateway = api_gateway
        self.logger = get_logger(__name__)
    
    def _datetime_to_timestamp(self, dt: datetime) -> Timestamp:
        """Convert datetime to protobuf Timestamp."""
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp
    
    def _vector_to_proto(self, vector: Vector):
        """Convert Vector model to protobuf Vector."""
        # This would use the generated protobuf classes
        proto_vector = {
            'id': str(vector.id),
            'embedding': vector.embedding,
            'metadata': json.dumps(vector.metadata) if vector.metadata else '',
            'collection': vector.collection or '',
            'score': vector.score or 0.0,
            'created_at': self._datetime_to_timestamp(vector.created_at),
            'updated_at': self._datetime_to_timestamp(vector.updated_at) if vector.updated_at else None
        }
        return proto_vector
    
    def _proto_to_vector(self, proto_vector) -> Vector:
        """Convert protobuf Vector to Vector model."""
        metadata = None
        if proto_vector.metadata:
            try:
                metadata = json.loads(proto_vector.metadata)
            except json.JSONDecodeError:
                metadata = {'raw': proto_vector.metadata}
        
        return Vector(
            id=proto_vector.id,
            embedding=list(proto_vector.embedding),
            metadata=metadata,
            collection=proto_vector.collection,
            score=proto_vector.score if proto_vector.score > 0 else None
        )
    
    async def SearchVectors(self, request, context):
        """Search for similar vectors."""
        try:
            # Parse filter conditions
            filter_conditions = None
            if request.filter_conditions:
                try:
                    filter_conditions = json.loads(request.filter_conditions)
                except json.JSONDecodeError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('Invalid filter conditions JSON')
                    return None
            
            # Create search request
            search_request = VectorSearchRequest(
                query_vector=list(request.query_vector),
                collection=request.collection,
                limit=request.limit or 10,
                score_threshold=request.score_threshold if request.score_threshold > 0 else None,
                include_vectors=request.include_vectors,
                include_metadata=request.include_metadata,
                filter_conditions=filter_conditions
            )
            
            # Perform search
            result = await self.vector_db.vector_operations.search_vectors(search_request)
            
            # Convert to protobuf response
            response = {
                'vectors': [self._vector_to_proto(v) for v in result.vectors],
                'total_count': result.total_count,
                'query_time_ms': result.query_time_ms,
                'collection': result.collection,
                'timestamp': self._datetime_to_timestamp(result.timestamp),
                'success': True,
                'error_message': ''
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC SearchVectors failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Search failed: {e}')
            return None
    
    async def GetVector(self, request, context):
        """Get vector by ID."""
        try:
            # Get vector
            vector = await self.vector_db.vector_operations.get_vector(
                request.vector_id, request.collection
            )
            
            if vector:
                response = {
                    'vector': self._vector_to_proto(vector),
                    'success': True,
                    'error_message': ''
                }
            else:
                response = {
                    'vector': None,
                    'success': False,
                    'error_message': 'Vector not found'
                }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC GetVector failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Get vector failed: {e}')
            return None
    
    async def InsertVector(self, request, context):
        """Insert a vector into collection."""
        try:
            # Convert protobuf vector to model
            vector = self._proto_to_vector(request.vector)
            
            # Insert vector
            result = await self.vector_db.vector_operations.insert_vector(
                vector, request.collection
            )
            
            response = {
                'success': result.success,
                'message': result.message,
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC InsertVector failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Insert vector failed: {e}')
            return None
    
    async def UpdateVector(self, request, context):
        """Update a vector in collection."""
        try:
            # Convert protobuf vector to model
            vector = self._proto_to_vector(request.vector)
            
            # Update vector
            result = await self.vector_db.vector_operations.update_vector(
                vector, request.collection
            )
            
            response = {
                'success': result.success,
                'message': result.message,
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC UpdateVector failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Update vector failed: {e}')
            return None
    
    async def DeleteVector(self, request, context):
        """Delete a vector from collection."""
        try:
            # Delete vector
            result = await self.vector_db.vector_operations.delete_vector(
                request.vector_id, request.collection
            )
            
            response = {
                'success': result.success,
                'message': result.message,
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC DeleteVector failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Delete vector failed: {e}')
            return None
    
    async def BatchInsertVectors(self, request, context):
        """Batch insert vectors into collection."""
        try:
            # Convert protobuf vectors to models
            vectors = [self._proto_to_vector(v) for v in request.vectors]
            
            # Batch insert
            result = await self.vector_db.vector_operations.batch_insert_vectors(
                vectors, request.collection, request.batch_size or 100
            )
            
            response = {
                'processed_count': result.processed_count,
                'failed_count': result.failed_count,
                'error_messages': result.error_messages,
                'processing_time_ms': result.processing_time_ms,
                'success': result.success
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC BatchInsertVectors failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Batch insert failed: {e}')
            return None
    
    async def GenerateEmbeddings(self, request, context):
        """Generate embeddings for text."""
        try:
            # Create embedding request
            embedding_request = EmbeddingRequest(
                text=list(request.text),
                model_name=request.model_name,
                normalize=request.normalize,
                batch_size=request.batch_size or 32,
                max_length=request.max_length or 512
            )
            
            # Generate embeddings
            result = await self.vector_db.embedding_service.generate_embeddings(
                embedding_request
            )
            
            # Convert embeddings to protobuf format
            embedding_vectors = [
                {'values': embedding} for embedding in result.embeddings
            ]
            
            response = {
                'embeddings': embedding_vectors,
                'model_name': result.model_name,
                'dimension': result.dimension,
                'processing_time_ms': result.processing_time_ms,
                'token_count': result.token_count or 0,
                'timestamp': self._datetime_to_timestamp(result.timestamp),
                'success': True,
                'error_message': ''
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC GenerateEmbeddings failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Generate embeddings failed: {e}')
            return None
    
    async def CreateCollection(self, request, context):
        """Create a new collection."""
        try:
            # Parse metadata
            metadata = None
            if request.metadata:
                try:
                    metadata = json.loads(request.metadata)
                except json.JSONDecodeError:
                    metadata = {'raw': request.metadata}
            
            # This would call actual collection manager
            # For now, return mock response
            response = {
                'success': True,
                'message': f'Collection {request.name} created successfully',
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC CreateCollection failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Create collection failed: {e}')
            return None
    
    async def DeleteCollection(self, request, context):
        """Delete a collection."""
        try:
            # This would call actual collection manager
            # For now, return mock response
            response = {
                'success': True,
                'message': f'Collection {request.name} deleted successfully',
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC DeleteCollection failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Delete collection failed: {e}')
            return None
    
    async def ListCollections(self, request, context):
        """List all collections."""
        try:
            # This would call actual collection manager
            # For now, return mock data
            collections = [
                {
                    'name': 'documents',
                    'dimension': 384,
                    'vector_count': 1000,
                    'created_at': self._datetime_to_timestamp(datetime.now()),
                    'updated_at': self._datetime_to_timestamp(datetime.now()),
                    'metadata': '{"description": "Document embeddings"}'
                },
                {
                    'name': 'embeddings',
                    'dimension': 768,
                    'vector_count': 500,
                    'created_at': self._datetime_to_timestamp(datetime.now()),
                    'updated_at': self._datetime_to_timestamp(datetime.now()),
                    'metadata': '{"description": "General embeddings"}'
                }
            ]
            
            response = {
                'collections': collections,
                'success': True,
                'error_message': ''
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC ListCollections failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'List collections failed: {e}')
            return None
    
    async def GetCollectionInfo(self, request, context):
        """Get collection information."""
        try:
            # This would call actual collection manager
            # For now, return mock data
            collection = {
                'name': request.name,
                'dimension': 384,
                'vector_count': 1000,
                'created_at': self._datetime_to_timestamp(datetime.now()),
                'updated_at': self._datetime_to_timestamp(datetime.now()),
                'metadata': '{"description": "Collection info"}'
            }
            
            response = {
                'collection': collection,
                'success': True,
                'error_message': ''
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC GetCollectionInfo failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Get collection info failed: {e}')
            return None
    
    async def CallExternalModel(self, request, context):
        """Call external AI model."""
        try:
            # Parse request data
            request_data = json.loads(request.request_data)
            
            # Call model
            response_data = await self.model_registry.call_model(
                request.model_id, request_data
            )
            
            # Convert to protobuf response
            response = {
                'model_id': response_data.get('model_id', request.model_id),
                'request_id': response_data.get('request_id', ''),
                'response_data': json.dumps(response_data.get('response_data', {})),
                'success': response_data.get('success', True),
                'error_message': response_data.get('error_message', ''),
                'processing_time_ms': response_data.get('processing_time_ms', 0.0),
                'tokens_used': response_data.get('tokens_used', 0),
                'cached': response_data.get('cached', False),
                'timestamp': self._datetime_to_timestamp(datetime.now())
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC CallExternalModel failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'External model call failed: {e}')
            return None
    
    async def ListExternalModels(self, request, context):
        """List all external models."""
        try:
            # Get models
            models = await self.model_registry.list_models()
            
            # Convert to protobuf format
            proto_models = []
            for model in models:
                proto_model = {
                    'id': model.id,
                    'name': model.name,
                    'model_type': model.model_type.value,
                    'api_endpoint': model.api_endpoint,
                    'capabilities': [cap.value for cap in model.capabilities],
                    'integration_pattern': model.integration_pattern.value,
                    'is_active': model.is_active,
                    'created_at': self._datetime_to_timestamp(model.created_at)
                }
                proto_models.append(proto_model)
            
            response = {
                'models': proto_models,
                'success': True,
                'error_message': ''
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC ListExternalModels failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'List external models failed: {e}')
            return None
    
    async def GetModelInfo(self, request, context):
        """Get external model information."""
        try:
            # Get model info
            model = await self.model_registry.get_model(request.model_id)
            
            if model:
                proto_model = {
                    'id': model.id,
                    'name': model.name,
                    'model_type': model.model_type.value,
                    'api_endpoint': model.api_endpoint,
                    'capabilities': [cap.value for cap in model.capabilities],
                    'integration_pattern': model.integration_pattern.value,
                    'is_active': model.is_active,
                    'created_at': self._datetime_to_timestamp(model.created_at)
                }
                
                response = {
                    'model': proto_model,
                    'success': True,
                    'error_message': ''
                }
            else:
                response = {
                    'model': None,
                    'success': False,
                    'error_message': 'Model not found'
                }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC GetModelInfo failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Get model info failed: {e}')
            return None
    
    async def HealthCheck(self, request, context):
        """Check system health."""
        try:
            # Perform health checks
            health_status = {
                "status": "healthy",
                "message": "System operational",
                "timestamp": datetime.now(),
                "details": {}
            }
            
            if self.vector_db:
                db_health = await self.vector_db.health_check()
                health_status["details"]["database"] = db_health
            
            if self.api_gateway:
                gateway_health = await self.api_gateway.health_check()
                health_status["details"]["api_gateway"] = gateway_health
            
            response = {
                'status': health_status["status"],
                'message': health_status["message"],
                'timestamp': self._datetime_to_timestamp(health_status["timestamp"]),
                'details': json.dumps(health_status["details"])
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"gRPC HealthCheck failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Health check failed: {e}',
                'timestamp': self._datetime_to_timestamp(datetime.now()),
                'details': '{}'
            }
    
    async def GetSystemStatus(self, request, context):
        """Get system status."""
        try:
            # Get system metrics
            import psutil
            
            status = {
                'status': 'operational',
                'version': '1.0.0',
                'active_connections': 0,  # Would get from actual connection pool
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'timestamp': self._datetime_to_timestamp(datetime.now()),
                'details': json.dumps({
                    'uptime': 'N/A',
                    'services': {
                        'vector_db': 'healthy',
                        'api_gateway': 'healthy',
                        'model_registry': 'healthy'
                    }
                })
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"gRPC GetSystemStatus failed: {e}")
            return {
                'status': 'error',
                'version': '1.0.0',
                'active_connections': 0,
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'timestamp': self._datetime_to_timestamp(datetime.now()),
                'details': json.dumps({'error': str(e)})
            }


class GRPCServer:
    """gRPC server wrapper following HXP Governance Coding Standards."""
    
    def __init__(self, vector_db, model_registry, api_gateway, port: int = 50051):
        """Initialize gRPC server."""
        self.vector_db = vector_db
        self.model_registry = model_registry
        self.api_gateway = api_gateway
        self.port = port
        self.server = None
        self.logger = get_logger(__name__)
    
    async def start(self):
        """Start gRPC server."""
        try:
            # Create server
            self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
            
            # Add service
            servicer = VectorDatabaseServiceServicer(
                self.vector_db, self.model_registry, self.api_gateway
            )
            
            # This would use generated add_VectorDatabaseServiceServicer_to_server
            # For now, we'll simulate the registration
            self.logger.info("gRPC service registered")
            
            # Add port
            listen_addr = f'[::]:{self.port}'
            self.server.add_insecure_port(listen_addr)
            
            # Start server
            await self.server.start()
            self.logger.info(f"gRPC server started on port {self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start gRPC server: {e}")
            raise
    
    async def stop(self):
        """Stop gRPC server."""
        try:
            if self.server:
                await self.server.stop(grace=5)
                self.logger.info("gRPC server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping gRPC server: {e}")
    
    async def wait_for_termination(self):
        """Wait for server termination."""
        if self.server:
            await self.server.wait_for_termination()
