"""
API Gateway Layer
================

Unified multi-protocol API gateway supporting REST, GraphQL, and gRPC protocols
for vector database operations.

Components:
- UnifiedAPIGateway: Main gateway orchestrator
- RestHandler: REST API implementation
- GraphQLHandler: GraphQL schema and resolvers
- GRPCHandler: gRPC service implementation
- Middleware: Authentication, validation, and caching
"""

from .api_gateway import UnifiedAPIGateway
from .rest_handler import RestHandler
from .graphql_handler import GraphQLHandler
from .grpc_handler import GRPCHandler
from .middleware import AuthenticationMiddleware, ValidationMiddleware, CachingMiddleware

__all__ = [
    "UnifiedAPIGateway",
    "RestHandler", 
    "GraphQLHandler",
    "GRPCHandler",
    "AuthenticationMiddleware",
    "ValidationMiddleware",
    "CachingMiddleware"
]
