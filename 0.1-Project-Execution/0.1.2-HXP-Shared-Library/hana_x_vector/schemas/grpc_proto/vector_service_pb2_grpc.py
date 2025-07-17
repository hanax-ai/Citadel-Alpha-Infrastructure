"""
Generated gRPC service stubs for vector_service.proto
"""

import grpc
from typing import Iterator, AsyncIterator
from . import vector_service_pb2 as vector__service__pb2


class VectorServiceStub(object):
    """gRPC client stub for VectorService."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InsertVector = channel.unary_unary(
            '/vectorservice.VectorService/InsertVector',
            request_serializer=vector__service__pb2.VectorRequest.SerializeToString,
            response_deserializer=vector__service__pb2.VectorResponse.FromString,
        )
        self.SearchVectors = channel.unary_unary(
            '/vectorservice.VectorService/SearchVectors',
            request_serializer=vector__service__pb2.SearchRequest.SerializeToString,
            response_deserializer=vector__service__pb2.SearchResponse.FromString,
        )
        self.CreateCollection = channel.unary_unary(
            '/vectorservice.VectorService/CreateCollection',
            request_serializer=vector__service__pb2.CollectionRequest.SerializeToString,
            response_deserializer=vector__service__pb2.CollectionResponse.FromString,
        )
        self.HealthCheck = channel.unary_unary(
            '/vectorservice.VectorService/HealthCheck',
            request_serializer=vector__service__pb2.HealthRequest.SerializeToString,
            response_deserializer=vector__service__pb2.HealthResponse.FromString,
        )


class VectorServiceServicer(object):
    """gRPC service implementation for VectorService."""

    def InsertVector(self, request, context):
        """Insert a vector into the database."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SearchVectors(self, request, context):
        """Search for similar vectors."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateCollection(self, request, context):
        """Create a new vector collection."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def HealthCheck(self, request, context):
        """Health check endpoint."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VectorServiceServicer_to_server(servicer, server):
    """Add VectorServiceServicer to gRPC server."""
    rpc_method_handlers = {
        'InsertVector': grpc.unary_unary_rpc_method_handler(
            servicer.InsertVector,
            request_deserializer=vector__service__pb2.VectorRequest.FromString,
            response_serializer=vector__service__pb2.VectorResponse.SerializeToString,
        ),
        'SearchVectors': grpc.unary_unary_rpc_method_handler(
            servicer.SearchVectors,
            request_deserializer=vector__service__pb2.SearchRequest.FromString,
            response_serializer=vector__service__pb2.SearchResponse.SerializeToString,
        ),
        'CreateCollection': grpc.unary_unary_rpc_method_handler(
            servicer.CreateCollection,
            request_deserializer=vector__service__pb2.CollectionRequest.FromString,
            response_serializer=vector__service__pb2.CollectionResponse.SerializeToString,
        ),
        'HealthCheck': grpc.unary_unary_rpc_method_handler(
            servicer.HealthCheck,
            request_deserializer=vector__service__pb2.HealthRequest.FromString,
            response_serializer=vector__service__pb2.HealthResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'vectorservice.VectorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# Alias for backward compatibility
VectorServiceServicer = VectorServiceServicer
