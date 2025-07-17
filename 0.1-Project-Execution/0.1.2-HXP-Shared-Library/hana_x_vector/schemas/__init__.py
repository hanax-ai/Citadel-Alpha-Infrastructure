"""
Schemas Package
==============

Schema definitions for the HANA-X Vector Database Shared Library.
Provides GraphQL schemas, gRPC protocol buffers, and REST API models.
"""

from .graphql_schemas import (
    VectorType,
    CollectionType,
    SearchResultType,
    Query,
    Mutation,
    create_graphql_schema
)
from .rest_models import (
    VectorModel,
    CollectionModel,
    SearchRequestModel,
    SearchResponseModel,
    BatchRequestModel,
    BatchResponseModel,
    HealthStatusModel,
    ErrorResponseModel
)
from .grpc_schemas import (
    VectorServicer,
    create_grpc_server,
    get_proto_definitions
)

__all__ = [
    # GraphQL
    'VectorType',
    'CollectionType',
    'SearchResultType',
    'Query',
    'Mutation',
    'create_graphql_schema',
    
    # REST Models
    'VectorModel',
    'CollectionModel',
    'SearchRequestModel',
    'SearchResponseModel',
    'BatchRequestModel',
    'BatchResponseModel',
    'HealthStatusModel',
    'ErrorResponseModel',
    
    # gRPC
    'VectorServicer',
    'create_grpc_server',
    'get_proto_definitions'
]
