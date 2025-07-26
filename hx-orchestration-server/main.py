"""
Citadel AI Operating System - Orchestration Hub v2.0
Main FastAPI Application Entry Point

Enterprise AI Runtime Environment for Business Process Automation
HANA-X Lab Infrastructure Integration (hx-orchestration-server: 192.168.10.31)
Architecture: Enterprise FastAPI + Celery + AI Frameworks
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api.v1.endpoints import embeddings, orchestration, health, metrics, auth, llm, business_automation
from app.api.middleware import setup_middleware
from app.core.services.monitoring_service import MonitoringService
from app.core.orchestration.service_discovery import service_discovery
from app.core.orchestration.load_balancer import LoadBalancer, FailoverManager
from app.core.business.workflow_engine import WorkflowEngine
from app.core.business.ai_decision_engine import AIDecisionEngine
from app.core.business.document_processor import DocumentProcessor
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting HX-Orchestration-Server...")
    
    # Initialize monitoring
    monitoring = MonitoringService()
    await monitoring.initialize()
    
    # Initialize service discovery
    logger.info("Initializing service discovery...")
    await service_discovery.initialize()
    
    # Initialize load balancer
    logger.info("Initializing load balancer...")
    load_balancer = LoadBalancer(service_discovery)
    failover_manager = FailoverManager(load_balancer)
    
    # Initialize business automation services
    logger.info("Initializing business automation services...")
    workflow_engine = WorkflowEngine()
    ai_decision_engine = AIDecisionEngine(service_discovery)
    document_processor = DocumentProcessor()
    
    await workflow_engine.initialize()
    await ai_decision_engine.initialize()
    await document_processor.initialize()
    
    # Store in app state for access by endpoints
    app.state.service_discovery = service_discovery
    app.state.load_balancer = load_balancer
    app.state.failover_manager = failover_manager
    app.state.monitoring = monitoring
    
    logger.info("Enterprise orchestration gateway initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HX-Orchestration-Server...")
    await service_discovery.shutdown()
    await monitoring.cleanup()


# Create FastAPI application
app = FastAPI(
    title="Citadel AI Operating System - Gateway",
    description="Enterprise AI Runtime Environment and Business Process Automation Gateway",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_middleware(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="", tags=["health"])
app.include_router(metrics.router, prefix="", tags=["metrics"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(embeddings.router, prefix="/v1", tags=["embeddings"])
app.include_router(orchestration.router, prefix="/v1", tags=["orchestration"])
app.include_router(llm.router, prefix="/v1", tags=["llm"])
app.include_router(business_automation.router, prefix="/v1", tags=["business_automation"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Citadel AI Operating System - Gateway",
        "version": "2.0.0",
        "status": "operational",
        "server": "hx-orchestration-server",
        "port": 8002,
        "role": "enterprise_gateway",
        "capabilities": [
            "business_process_automation",
            "ai_workflow_orchestration", 
            "ai_decision_engine",
            "document_processing",
            "multi_agent_coordination",
            "hana_x_lab_integration",
            "enterprise_security"
        ],
        "endpoints": {
            "health": "/health/",
            "metrics": "/metrics", 
            "embeddings": "/v1/embeddings",
            "orchestration": "/v1/orchestrate",
            "chat_completions": "/v1/chat/completions",
            "completions": "/v1/completions",
            "models": "/v1/models",
            "business_workflows": "/v1/business/workflows",
            "business_decisions": "/v1/business/decisions",
            "business_documents": "/v1/business/documents",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",           # Accept all interfaces
        port=8002,                # Production gateway port
        reload=settings.DEBUG,
        workers=8 if not settings.DEBUG else 1  # High-performance workers
    )
