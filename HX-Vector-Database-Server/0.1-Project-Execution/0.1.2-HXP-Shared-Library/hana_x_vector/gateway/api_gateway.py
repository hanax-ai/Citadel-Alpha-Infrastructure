"""
Unified API Gateway
==================

Multi-protocol API gateway supporting REST, GraphQL, and gRPC protocols
for vector database operations.
"""

from typing import Dict, Any, Optional
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import redis.asyncio as redis
from .rest_handler import RestHandler
from .graphql_handler import GraphQLHandler
from .grpc_handler import GRPCHandler
from ..monitoring.metrics import MetricsCollector
from ..monitoring.health import HealthMonitor
from ..utils.config import ConfigManager
from ..utils.exceptions import ConfigurationError


class UnifiedAPIGateway:
    """
    Unified API Gateway for multi-protocol vector database access.
    Supports REST, GraphQL, and gRPC protocols through a single entry point.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = FastAPI(
            title="HANA-X Vector Database API Gateway",
            description="Unified multi-protocol API for vector database operations",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Initialize handlers
        self.rest_handler = RestHandler(config)
        self.graphql_handler = GraphQLHandler(config)
        self.grpc_handler = GRPCHandler(config)
        
        # Initialize monitoring
        self.metrics = MetricsCollector()
        self.health_monitor = HealthMonitor(config)
        
        # Initialize caching
        self.redis_client = None
        
        self._setup_middleware()
        self._setup_routes()
    
    async def startup(self):
        """Initialize gateway services and connections."""
        # Initialize Redis cache connection
        self.redis_client = redis.Redis(
            host=self.config['redis']['host'],
            port=self.config['redis']['port'],
            db=self.config['redis']['db'],
            decode_responses=True
        )
        
        # Initialize handlers
        await self.rest_handler.startup()
        await self.graphql_handler.startup()
        await self.grpc_handler.startup()
        
        # Start health monitoring
        await self.health_monitor.startup()
        
        # Initialize metrics collection
        self.metrics.start_collection()
    
    async def shutdown(self):
        """Cleanup gateway services and connections."""
        if self.redis_client:
            await self.redis_client.close()
        
        await self.rest_handler.shutdown()
        await self.graphql_handler.shutdown()
        await self.grpc_handler.shutdown()
        await self.health_monitor.shutdown()
        self.metrics.stop_collection()
    
    def _setup_middleware(self):
        """Configure middleware for the gateway."""
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure for R&D environment
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add custom metrics middleware
        @self.app.middleware("http")
        async def metrics_middleware(request: Request, call_next):
            start_time = asyncio.get_event_loop().time()
            response = await call_next(request)
            process_time = asyncio.get_event_loop().time() - start_time
            
            self.metrics.record_request(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=response.status_code,
                duration=process_time
            )
            
            return response
    
    def _setup_routes(self):
        """Configure API routes for all protocols."""
        # Health and metrics endpoints
        @self.app.get("/health")
        async def health_check():
            return await self.health_monitor.get_status()
        
        @self.app.get("/metrics")
        async def get_metrics():
            return self.metrics.get_prometheus_metrics()
        
        # Include protocol-specific routers
        self.app.include_router(
            self.rest_handler.router,
            prefix="/api/v1",
            tags=["REST API"]
        )
        
        self.app.include_router(
            self.graphql_handler.router,
            prefix="/graphql",
            tags=["GraphQL API"]
        )
        
        # gRPC is handled separately via grpc_handler
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app
    
    async def start_grpc_server(self, port: int = 6334):
        """Start the gRPC server."""
        await self.grpc_handler.start_server(port)
    
    async def stop_grpc_server(self):
        """Stop the gRPC server."""
        await self.grpc_handler.stop_server()
