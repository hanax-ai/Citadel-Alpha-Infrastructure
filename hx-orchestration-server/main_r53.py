"""
Citadel AI Orchestration Server - Main Application (R5.3 Compliance)
FastAPI entry point with 8-worker uvicorn configuration following LLM-01 patterns
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from app.api.v1.endpoints import r53_health
from r53_middleware import LoggingMiddleware, MetricsMiddleware, SecurityMiddleware
from r53_base_classes import ServiceRegistry
from r53_common_utilities import config_manager, setup_logging
from config.settings import get_settings

# Initialize settings and logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize service registry
service_registry = ServiceRegistry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Citadel AI Orchestration Server starting up...")
    logger.info(f"Server: hx-orchestration-server (192.168.10.31)")
    logger.info(f"Configuration: {settings.ENVIRONMENT}")
    logger.info("R5.3 Common Class Library initialized")
    
    # Initialize orchestration services
    try:
        from app.core.orchestration.service_discovery import service_discovery
        await service_discovery.start_health_monitoring()
        logger.info("Enterprise orchestration services initialized")
    except Exception as e:
        logger.warning(f"Orchestration services not available: {e}")
    
    yield
    
    # Shutdown
    logger.info("Citadel AI Orchestration Server shutting down...")
    await service_registry.stop_all_services()
    
    # Stop orchestration services
    try:
        from app.core.orchestration.service_discovery import service_discovery
        await service_discovery.stop_health_monitoring()
        logger.info("Orchestration services stopped")
    except Exception as e:
        logger.warning(f"Error stopping orchestration services: {e}")

# FastAPI application with LLM-01 patterns
app = FastAPI(
    title="Citadel AI Orchestration Server",
    version="2.0.0",
    description="Production orchestration with FastAPI + Celery patterns (R5.3 Compliance)",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS configuration for AG UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.10.38",
        "http://192.168.10.38:3000",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom middleware (R5.3 compliance)
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include API routes
app.include_router(r53_health.router, prefix="/api/v1/health", tags=["health"])

# Import and include OpenAI endpoints
try:
    from app.api.v1.endpoints import openai_endpoints
    app.include_router(openai_endpoints.router, prefix="/v1", tags=["openai"])
    logger.info("OpenAI endpoints enabled")
except ImportError as e:
    logger.warning(f"OpenAI endpoints not available: {e}")

# Import and include orchestration endpoints
try:
    from app.api.v1.endpoints import orchestration
    app.include_router(orchestration.router, prefix="/api/v1", tags=["orchestration"])
    logger.info("Orchestration endpoints enabled")
except ImportError as e:
    logger.warning(f"Orchestration endpoints not available: {e}")

# Import and include RAG endpoints
try:
    from app.api.v1.endpoints import rag
    app.include_router(rag.router, prefix="/api/v1", tags=["rag"])
    logger.info("RAG endpoints enabled")
except ImportError as e:
    logger.warning(f"RAG endpoints not available: {e}")
except ImportError as e:
    logger.warning(f"RAG endpoints not available: {e}")

# Import and include embeddings endpoints
try:
    from app.api.v1.endpoints import embeddings
    app.include_router(embeddings.router, prefix="/api/v1", tags=["embeddings"])
    logger.info("Embeddings endpoints enabled")
except ImportError as e:
    logger.warning(f"Embeddings endpoints not available: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception: {exc} - Request ID: {request_id}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Endpoint not found",
            "error_code": "NOT_FOUND",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

# Health check endpoint (LLM-01 pattern)
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "citadel-orchestration-server",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "server": "hx-orchestration-server",
        "ip": "192.168.10.31",
        "framework": "FastAPI + R5.3 Common Class Library"
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Citadel AI Orchestration Server",
        "version": "2.0.0",
        "status": "operational",
        "server": "hx-orchestration-server",
        "ip": "192.168.10.31",
        "framework": "FastAPI + R5.3 Common Class Library",
        "compliance": "R5.3",
        "capabilities": [
            "business_process_automation",
            "ai_workflow_orchestration",
            "common_class_library",
            "standardized_base_classes",
            "shared_utility_functions",
            "configuration_management"
        ],
        "endpoints": {
            "health": "/health",
            "detailed_health": "/api/v1/health/detailed",
            "services_health": "/api/v1/health/services",
            "system_metrics": "/api/v1/health/metrics/system",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/api/v1/openapi.json"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API status and configuration"""
    return {
        "api_version": "v1",
        "framework": "FastAPI",
        "compliance": "R5.3 Common Class Library",
        "features": {
            "base_classes": True,
            "shared_utilities": True,
            "standardized_models": True,
            "middleware": True,
            "health_monitoring": True,
            "metrics_collection": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # 8-worker uvicorn configuration (LLM-01 pattern)
    uvicorn.run(
        "main_r53:app",
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflicts
        workers=8 if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        reload=settings.DEBUG
    )
