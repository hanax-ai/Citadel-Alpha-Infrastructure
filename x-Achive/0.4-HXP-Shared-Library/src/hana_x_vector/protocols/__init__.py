"""
Protocol Abstraction Package

Unified protocol abstraction supporting REST, GraphQL, and gRPC protocols.
Follows HXP Governance Coding Standards and SOLID principles.

Author: Citadel AI Team
License: MIT
"""

from .protocol_abstraction import (
    ProtocolAbstractionLayer,
    ProtocolType,
    IProtocolHandler,
    RESTProtocolHandler,
    GraphQLProtocolHandler,
    GRPCProtocolHandler
)
from .graphql_schema import schema as graphql_schema
from .grpc_service import GRPCServer, VectorDatabaseServiceServicer

__all__ = [
    "ProtocolAbstractionLayer",
    "ProtocolType",
    "IProtocolHandler",
    "RESTProtocolHandler",
    "GraphQLProtocolHandler",
    "GRPCProtocolHandler",
    "graphql_schema",
    "GRPCServer",
    "VectorDatabaseServiceServicer"
]