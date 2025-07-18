"""
Protocol Abstraction Layer

Unified protocol abstraction supporting REST, GraphQL, and gRPC protocols.
Implements Single Responsibility Principle and Interface Segregation Principle.

Author: Citadel AI Team
License: MIT
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import json

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
import uvicorn

from hana_x_vector.protocols.graphql_schema import schema
from hana_x_vector.protocols.grpc_service import GRPCServer
from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.metrics import MetricsCollector, monitor_performance
from hana_x_vector.utils.config import get_config

logger = get_logger(__name__)


class ProtocolType(Enum):
    """Supported protocol types."""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"


class IProtocolHandler(ABC):
    """Interface for protocol handlers following Interface Segregation Principle."""
    
    @abstractmethod
    async def start(self) -> None:
        """Start the protocol handler."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the protocol handler."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check protocol handler health."""
        pass
    
    @abstractmethod
    def get_protocol_type(self) -> ProtocolType:
        """Get the protocol type."""
        pass


class RESTProtocolHandler(IProtocolHandler):
    """REST protocol handler implementation."""
    
    def __init__(self, api_gateway, host: str = "0.0.0.0", port: int = 8000):
        """Initialize REST protocol handler."""
        self.api_gateway = api_gateway
        self.host = host
        self.port = port
        self.server = None
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    async def start(self) -> None:
        """Start REST server."""
        try:
            # Get FastAPI app from API Gateway
            app = self.api_gateway.app
            
            # Configure server
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True
            )
            
            self.server = uvicorn.Server(config)
            
            # Start server in background
            asyncio.create_task(self.server.serve())
            
            self.logger.info(f"REST server started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start REST server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop REST server."""
        try:
            if self.server:
                self.server.should_exit = True
                await asyncio.sleep(1)  # Give time for graceful shutdown
                self.logger.info("REST server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping REST server: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check REST server health."""
        try:
            return {
                "protocol": "REST",
                "status": "healthy",
                "host": self.host,
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "protocol": "REST",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_protocol_type(self) -> ProtocolType:
        """Get protocol type."""
        return ProtocolType.REST


class GraphQLProtocolHandler(IProtocolHandler):
    """GraphQL protocol handler implementation."""
    
    def __init__(self, vector_db, model_registry, api_gateway, 
                 host: str = "0.0.0.0", port: int = 8001):
        """Initialize GraphQL protocol handler."""
        self.vector_db = vector_db
        self.model_registry = model_registry
        self.api_gateway = api_gateway
        self.host = host
        self.port = port
        self.app = None
        self.server = None
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI app with GraphQL endpoint."""
        app = FastAPI(
            title="HXP Vector Database GraphQL API",
            description="GraphQL API for HXP Vector Database operations",
            version="1.0.0"
        )
        
        # Add middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Create GraphQL router with context
        async def get_context() -> Dict[str, Any]:
            """Get GraphQL context."""
            return {
                "vector_db": self.vector_db,
                "model_registry": self.model_registry,
                "api_gateway": self.api_gateway
            }
        
        graphql_app = GraphQLRouter(
            schema,
            context_getter=get_context,
            graphiql=True  # Enable GraphiQL interface
        )
        
        # Add GraphQL endpoint
        app.include_router(graphql_app, prefix="/graphql")
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return await self.health_check()
        
        return app
    
    async def start(self) -> None:
        """Start GraphQL server."""
        try:
            # Create app
            self.app = self._create_app()
            
            # Configure server
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True
            )
            
            self.server = uvicorn.Server(config)
            
            # Start server in background
            asyncio.create_task(self.server.serve())
            
            self.logger.info(f"GraphQL server started on {self.host}:{self.port}")
            self.logger.info(f"GraphiQL interface available at http://{self.host}:{self.port}/graphql")
            
        except Exception as e:
            self.logger.error(f"Failed to start GraphQL server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop GraphQL server."""
        try:
            if self.server:
                self.server.should_exit = True
                await asyncio.sleep(1)  # Give time for graceful shutdown
                self.logger.info("GraphQL server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping GraphQL server: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check GraphQL server health."""
        try:
            return {
                "protocol": "GraphQL",
                "status": "healthy",
                "host": self.host,
                "port": self.port,
                "graphiql_url": f"http://{self.host}:{self.port}/graphql",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "protocol": "GraphQL",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_protocol_type(self) -> ProtocolType:
        """Get protocol type."""
        return ProtocolType.GRAPHQL


class GRPCProtocolHandler(IProtocolHandler):
    """gRPC protocol handler implementation."""
    
    def __init__(self, vector_db, model_registry, api_gateway, port: int = 50051):
        """Initialize gRPC protocol handler."""
        self.vector_db = vector_db
        self.model_registry = model_registry
        self.api_gateway = api_gateway
        self.port = port
        self.grpc_server = None
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    async def start(self) -> None:
        """Start gRPC server."""
        try:
            # Create gRPC server
            self.grpc_server = GRPCServer(
                self.vector_db, 
                self.model_registry, 
                self.api_gateway, 
                self.port
            )
            
            # Start server
            await self.grpc_server.start()
            
            self.logger.info(f"gRPC server started on port {self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start gRPC server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop gRPC server."""
        try:
            if self.grpc_server:
                await self.grpc_server.stop()
                self.logger.info("gRPC server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping gRPC server: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check gRPC server health."""
        try:
            return {
                "protocol": "gRPC",
                "status": "healthy",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "protocol": "gRPC",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_protocol_type(self) -> ProtocolType:
        """Get protocol type."""
        return ProtocolType.GRPC


class ProtocolAbstractionLayer:
    """
    Unified Protocol Abstraction Layer
    
    Manages multiple protocol handlers and provides unified interface.
    Implements Facade pattern for protocol management.
    """
    
    def __init__(self, vector_db, model_registry, api_gateway):
        """Initialize protocol abstraction layer."""
        self.vector_db = vector_db
        self.model_registry = model_registry
        self.api_gateway = api_gateway
        self.handlers: Dict[ProtocolType, IProtocolHandler] = {}
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
        self.config = get_config()
        
        # Initialize handlers
        self._initialize_handlers()
    
    def _initialize_handlers(self) -> None:
        """Initialize protocol handlers."""
        try:
            # REST handler
            if self.config.api_gateway.enable_rest:
                self.handlers[ProtocolType.REST] = RESTProtocolHandler(
                    self.api_gateway,
                    host=self.config.api_gateway.host,
                    port=self.config.api_gateway.rest_port
                )
            
            # GraphQL handler
            if self.config.api_gateway.enable_graphql:
                self.handlers[ProtocolType.GRAPHQL] = GraphQLProtocolHandler(
                    self.vector_db,
                    self.model_registry,
                    self.api_gateway,
                    host=self.config.api_gateway.host,
                    port=self.config.api_gateway.graphql_port
                )
            
            # gRPC handler
            if self.config.api_gateway.enable_grpc:
                self.handlers[ProtocolType.GRPC] = GRPCProtocolHandler(
                    self.vector_db,
                    self.model_registry,
                    self.api_gateway,
                    port=self.config.api_gateway.grpc_port
                )
            
            self.logger.info(f"Initialized {len(self.handlers)} protocol handlers")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize protocol handlers: {e}")
            raise
    
    @monitor_performance
    async def start_all(self) -> None:
        """Start all protocol handlers."""
        try:
            start_tasks = []
            
            for protocol_type, handler in self.handlers.items():
                self.logger.info(f"Starting {protocol_type.value} protocol handler")
                start_tasks.append(handler.start())
            
            # Start all handlers concurrently
            await asyncio.gather(*start_tasks)
            
            self.logger.info("All protocol handlers started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start protocol handlers: {e}")
            raise
    
    @monitor_performance
    async def stop_all(self) -> None:
        """Stop all protocol handlers."""
        try:
            stop_tasks = []
            
            for protocol_type, handler in self.handlers.items():
                self.logger.info(f"Stopping {protocol_type.value} protocol handler")
                stop_tasks.append(handler.stop())
            
            # Stop all handlers concurrently
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            self.logger.info("All protocol handlers stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping protocol handlers: {e}")
    
    async def start_protocol(self, protocol_type: ProtocolType) -> None:
        """Start specific protocol handler."""
        try:
            if protocol_type in self.handlers:
                await self.handlers[protocol_type].start()
                self.logger.info(f"{protocol_type.value} protocol handler started")
            else:
                raise ValueError(f"Protocol {protocol_type.value} not configured")
        except Exception as e:
            self.logger.error(f"Failed to start {protocol_type.value} handler: {e}")
            raise
    
    async def stop_protocol(self, protocol_type: ProtocolType) -> None:
        """Stop specific protocol handler."""
        try:
            if protocol_type in self.handlers:
                await self.handlers[protocol_type].stop()
                self.logger.info(f"{protocol_type.value} protocol handler stopped")
            else:
                raise ValueError(f"Protocol {protocol_type.value} not configured")
        except Exception as e:
            self.logger.error(f"Failed to stop {protocol_type.value} handler: {e}")
            raise
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all protocol handlers."""
        try:
            health_results = {}
            
            for protocol_type, handler in self.handlers.items():
                health_results[protocol_type.value] = await handler.health_check()
            
            # Overall health status
            all_healthy = all(
                result.get("status") == "healthy" 
                for result in health_results.values()
            )
            
            return {
                "overall_status": "healthy" if all_healthy else "unhealthy",
                "protocols": health_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check_protocol(self, protocol_type: ProtocolType) -> Dict[str, Any]:
        """Check health of specific protocol handler."""
        try:
            if protocol_type in self.handlers:
                return await self.handlers[protocol_type].health_check()
            else:
                return {
                    "protocol": protocol_type.value,
                    "status": "not_configured",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Health check for {protocol_type.value} failed: {e}")
            return {
                "protocol": protocol_type.value,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_active_protocols(self) -> List[ProtocolType]:
        """Get list of active protocol types."""
        return list(self.handlers.keys())
    
    def get_protocol_handler(self, protocol_type: ProtocolType) -> Optional[IProtocolHandler]:
        """Get specific protocol handler."""
        return self.handlers.get(protocol_type)
    
    async def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol statistics."""
        try:
            stats = {
                "active_protocols": len(self.handlers),
                "protocol_types": [pt.value for pt in self.handlers.keys()],
                "timestamp": datetime.now().isoformat()
            }
            
            # Add individual protocol stats
            for protocol_type, handler in self.handlers.items():
                health = await handler.health_check()
                stats[f"{protocol_type.value}_status"] = health.get("status")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get protocol stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def reload_configuration(self) -> None:
        """Reload protocol configuration."""
        try:
            self.logger.info("Reloading protocol configuration")
            
            # Stop all handlers
            await self.stop_all()
            
            # Clear handlers
            self.handlers.clear()
            
            # Reload config
            self.config = get_config()
            
            # Reinitialize handlers
            self._initialize_handlers()
            
            # Start all handlers
            await self.start_all()
            
            self.logger.info("Protocol configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to reload protocol configuration: {e}")
            raise
