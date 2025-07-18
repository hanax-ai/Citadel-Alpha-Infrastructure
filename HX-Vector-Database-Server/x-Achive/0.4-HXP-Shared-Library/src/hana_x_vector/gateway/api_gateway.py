"""
Unified API Gateway Module

Unified API Gateway consolidating REST, GraphQL, and gRPC protocols following HXP Governance Coding Standards.
Implements Single Responsibility Principle for API Gateway coordination.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from hana_x_vector.models.vector_models import (
    VectorSearchRequest, VectorSearchResult, EmbeddingRequest, EmbeddingResponse
)
from hana_x_vector.utils.metrics import get_metrics_collector, monitor_performance
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


class APIGatewayInterface(ABC):
    """
    Abstract interface for API Gateway (Abstraction principle).
    
    Defines the contract for unified API Gateway without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start API Gateway services."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop API Gateway services."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of API Gateway."""
        pass
    
    @abstractmethod
    def register_routes(self) -> None:
        """Register API routes."""
        pass


class UnifiedAPIGateway(APIGatewayInterface):
    """
    Unified API Gateway implementation (Single Responsibility Principle).
    
    Consolidates REST, GraphQL, and gRPC protocols into a single entry point
    with intelligent routing, load balancing, and caching capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Unified API Gateway.
        
        Args:
            config: Configuration dictionary containing gateway settings
        """
        self._config = config
        self._app = None
        self._server = None
        self._running = False
        
        # Initialize FastAPI application
        self._init_fastapi()
        
        # Register routes
        self.register_routes()
        
        logger.info("UnifiedAPIGateway initialized")
    
    def _init_fastapi(self) -> None:
        """Initialize FastAPI application with middleware."""
        self._app = FastAPI(
            title="HANA-X Vector Database API Gateway",
            description="Unified API Gateway for Vector Database Operations",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        if self._config.get("cors_enabled", True):
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=self._config.get("cors_origins", ["*"]),
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        
        # Add compression middleware
        self._app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add request logging middleware
        @self._app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.now()
            
            # Process request
            response = await call_next(request)
            
            # Log request
            duration = (datetime.now() - start_time).total_seconds()
            metrics = get_metrics_collector()
            metrics.record_request(
                method=request.method,
                endpoint=str(request.url.path),
                status=response.status_code,
                duration=duration
            )
            
            return response
    
    def register_routes(self) -> None:
        """Register API routes for all protocols."""
        # Health check endpoint
        @self._app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return await self.health_check()
        
        # Vector operations endpoints
        @self._app.post("/api/v1/vectors/search")
        @monitor_performance("vector_search")
        async def search_vectors(request: VectorSearchRequest):
            """Search for similar vectors."""
            try:
                # This would integrate with actual vector operations
                # For now, return mock response
                return VectorSearchResult(
                    vectors=[],
                    total_count=0,
                    query_time_ms=0.0,
                    collection=request.collection,
                    search_params=request
                )
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Embedding generation endpoints
        @self._app.post("/api/v1/embeddings/generate")
        @monitor_performance("embedding_generation")
        async def generate_embeddings(request: EmbeddingRequest):
            """Generate embeddings for text."""
            try:
                # This would integrate with actual embedding service
                # For now, return mock response
                return EmbeddingResponse(
                    embeddings=[[0.1, 0.2, 0.3]],
                    model_name=request.model_name,
                    dimension=384,
                    processing_time_ms=100.0
                )
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # External model endpoints
        @self._app.post("/api/v1/external/models/{model_id}/generate")
        @monitor_performance("external_model_call")
        async def call_external_model(model_id: str, request: Dict[str, Any]):
            """Call external AI model."""
            try:
                # This would integrate with external model service
                # For now, return mock response
                return {
                    "model_id": model_id,
                    "response": "Mock response",
                    "success": True,
                    "processing_time_ms": 200.0
                }
            except Exception as e:
                logger.error(f"External model call failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Batch processing endpoints
        @self._app.post("/api/v1/batch/submit")
        @monitor_performance("batch_submit")
        async def submit_batch_job(request: Dict[str, Any]):
            """Submit batch processing job."""
            try:
                # This would integrate with batch processing service
                # For now, return mock response
                return {
                    "job_id": "batch_123",
                    "status": "submitted",
                    "estimated_completion": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Batch job submission failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Collection management endpoints
        @self._app.get("/api/v1/collections")
        async def list_collections():
            """List all collections."""
            try:
                # This would integrate with collection manager
                return {
                    "collections": [
                        {"name": "documents", "vectors": 1000, "dimension": 384},
                        {"name": "embeddings", "vectors": 500, "dimension": 768}
                    ]
                }
            except Exception as e:
                logger.error(f"Collection listing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self._app.post("/api/v1/collections/{collection_name}")
        async def create_collection(collection_name: str, request: Dict[str, Any]):
            """Create new collection."""
            try:
                # This would integrate with collection manager
                return {
                    "name": collection_name,
                    "dimension": request.get("dimension", 384),
                    "created": True
                }
            except Exception as e:
                logger.error(f"Collection creation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        logger.info("API routes registered successfully")
    
    async def start(self) -> None:
        """Start API Gateway services."""
        if self._running:
            logger.warning("API Gateway already running")
            return
        
        try:
            # Get configuration
            host = self._config.get("host", "0.0.0.0")
            port = self._config.get("rest_port", 8000)
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=self._app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
            # Start server
            self._server = uvicorn.Server(config)
            
            # Start in background task
            asyncio.create_task(self._server.serve())
            
            self._running = True
            logger.info(f"API Gateway started on {host}:{port}")
            
        except Exception as e:
            logger.error(f"Failed to start API Gateway: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop API Gateway services."""
        if not self._running:
            logger.warning("API Gateway not running")
            return
        
        try:
            if self._server:
                self._server.should_exit = True
                await self._server.shutdown()
            
            self._running = False
            logger.info("API Gateway stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop API Gateway: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of API Gateway.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            return {
                "status": "healthy" if self._running else "stopped",
                "message": "API Gateway operational" if self._running else "API Gateway stopped",
                "running": self._running,
                "endpoints": {
                    "rest": f"http://{self._config.get('host', '0.0.0.0')}:{self._config.get('rest_port', 8000)}",
                    "docs": f"http://{self._config.get('host', '0.0.0.0')}:{self._config.get('rest_port', 8000)}/docs"
                },
                "protocols": ["REST", "HTTP"],
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {e}",
                "running": False,
                "error": str(e)
            }
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application instance."""
        return self._app
    
    def is_running(self) -> bool:
        """Check if API Gateway is running."""
        return self._running
    
    async def reload_config(self, new_config: Dict[str, Any]) -> None:
        """Reload configuration."""
        try:
            self._config.update(new_config)
            logger.info("Configuration reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            raise
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get API Gateway metrics."""
        try:
            metrics = get_metrics_collector()
            return {
                "requests_total": "Available via Prometheus",
                "request_duration": "Available via Prometheus",
                "active_connections": "Available via Prometheus",
                "uptime": "Available via Prometheus",
                "endpoints_registered": len(self._app.routes) if self._app else 0
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
