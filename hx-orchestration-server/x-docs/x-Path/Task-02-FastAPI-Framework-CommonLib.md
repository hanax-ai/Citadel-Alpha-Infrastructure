# Task 2: FastAPI Application Framework and Common Class Library

**Document Version:** 1.0  
**Date:** 2025-07-25  
**Author:** Manus AI  
**Project:** Citadel AI Operating System - Orchestration Server Implementation  
**Server:** hx-orchestration-server (192.168.10.31)  
**Purpose:** Phase 2A implementation - FastAPI framework and R5.3 common class library  
**Classification:** Production-Ready Implementation Task  
**Duration:** 4-6 hours  
**Priority:** CRITICAL  
**Dependencies:** Task 1 completion

---

## Task Overview

Implement the FastAPI application framework with comprehensive common class library (R5.3 compliance), establishing the foundation for orchestration services with standardized base classes, utility functions, and shared patterns.

### Key Deliverables

1. **FastAPI Application Framework**
   - Main application entry point (`main.py`)
   - API v1 structure with health endpoints
   - CORS middleware and request/response logging
   - OpenAPI documentation integration

2. **Common Class Library (R5.3 Implementation)**
   - Base service classes for consistent patterns
   - Shared utility functions and decorators
   - Standardized API models and validators
   - Configuration management framework

3. **Core Application Structure**
   - Modular API endpoints architecture
   - Dependency injection patterns
   - Error handling and exception framework

---

## Implementation Steps

### Step 2.1: Main FastAPI Application (1.5-2 hours)

**Objective:** Create the core FastAPI application with LLM-01 proven patterns

**Files to Create:**

**File:** `/main.py`
```python
"""
Citadel AI Orchestration Server - Main Application
FastAPI entry point with 8-worker uvicorn configuration
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
from datetime import datetime

from app.api.v1 import api_router
from app.api.middleware import LoggingMiddleware, MetricsMiddleware
from app.common.base_classes import BaseOrchestrationService
from app.utils.performance_monitor import MetricsCollector
from config.settings import get_settings

# Initialize settings and logging
settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize metrics collector
metrics_collector = MetricsCollector()

# FastAPI application with LLM-01 patterns
app = FastAPI(
    title="Citadel AI Orchestration Server",
    version="2.0.0",
    description="Production orchestration with FastAPI + Celery patterns",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS configuration for AG UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.10.38", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware, metrics_collector=metrics_collector)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("Citadel AI Orchestration Server starting up...")
    logger.info(f"Server: hx-orchestration-server (192.168.10.31)")
    logger.info(f"Configuration: {settings.environment}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger.info("Citadel AI Orchestration Server shutting down...")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown")
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
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # 8-worker uvicorn configuration (LLM-01 pattern)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=8,
        log_level=settings.log_level.lower(),
        access_log=True
    )
```

### Step 2.2: Common Class Library Implementation (2-2.5 hours)

**Objective:** Implement comprehensive R5.3 common class library

**File:** `/app/common/base_classes.py`
```python
"""
Common Base Classes for Orchestration Services (R5.3 Compliance)
Provides standardized base classes with consistent patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass

class BaseOrchestrationService(ABC):
    """Base class for all orchestration services with common patterns"""
    
    def __init__(self, service_name: str, config: Dict[str, Any]):
        self.service_name = service_name
        self.config = config
        self.logger = logging.getLogger(f"orchestration.{service_name}")
        self._health_status = "initializing"
        self._start_time = datetime.utcnow()
        self._metrics = {"requests": 0, "errors": 0, "last_activity": None}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize service resources and dependencies"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return comprehensive service health status"""
        pass
    
    async def shutdown(self) -> None:
        """Graceful shutdown with resource cleanup"""
        self._health_status = "shutting_down"
        self.logger.info(f"{self.service_name} shutting down gracefully")
    
    def record_activity(self):
        """Record service activity for monitoring"""
        self._metrics["requests"] += 1
        self._metrics["last_activity"] = datetime.utcnow()
    
    def record_error(self):
        """Record service error for monitoring"""
        self._metrics["errors"] += 1
    
    @property
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.utcnow() - self._start_time).total_seconds()

class BaseEmbeddingService(BaseOrchestrationService):
    """Specialized base class for embedding services"""
    
    def __init__(self, service_name: str, config: Dict[str, Any], model_name: str):
        super().__init__(service_name, config)
        self.model_name = model_name
        self._embedding_metrics = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "average_latency": 0.0,
            "model_load_time": None
        }
    
    async def get_embedding_metrics(self) -> Dict[str, Any]:
        """Return embedding-specific performance metrics"""
        hit_rate = (self._embedding_metrics["cache_hits"] / 
                   max(self._embedding_metrics["total_embeddings"], 1))
        
        return {
            "model_name": self.model_name,
            "total_embeddings": self._embedding_metrics["total_embeddings"],
            "cache_hit_rate": hit_rate,
            "average_latency_ms": self._embedding_metrics["average_latency"],
            "uptime_seconds": self.uptime_seconds,
            "model_loaded": self._embedding_metrics["model_load_time"] is not None
        }
    
    def record_embedding(self, latency_ms: float, cache_hit: bool = False):
        """Record embedding generation metrics"""
        self.record_activity()
        self._embedding_metrics["total_embeddings"] += 1
        if cache_hit:
            self._embedding_metrics["cache_hits"] += 1
        
        # Update running average latency
        current_avg = self._embedding_metrics["average_latency"]
        count = self._embedding_metrics["total_embeddings"]
        self._embedding_metrics["average_latency"] = (
            (current_avg * (count - 1) + latency_ms) / count
        )

@dataclass
class ServiceConfig:
    """Standard configuration data class"""
    service_name: str
    host: str = "localhost"
    port: int = 8000
    timeout: int = 30
    max_retries: int = 3
    debug: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility"""
        return {
            "service_name": self.service_name,
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "debug": self.debug
        }

class BaseAPIClient(ABC):
    """Base class for external API clients with common patterns"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"client.{config.service_name}")
        self._session = None
        self._connection_pool = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection and cleanup resources"""
        pass
    
    async def is_healthy(self) -> bool:
        """Check if service is healthy and reachable"""
        try:
            # Implement basic connectivity check
            return await self.health_check()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Implement service-specific health check"""
        pass
```

**File:** `/app/utils/common_utilities.py`
```python
"""
Shared Utility Functions and Classes (R5.3 Compliance)
Provides reusable functionality across orchestration components
"""
import hashlib
import json
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from functools import wraps

class CacheKeyGenerator:
    """Standardized cache key generation for consistent caching patterns"""
    
    @staticmethod
    def embedding_key(text: str, model: str, options: Optional[Dict] = None) -> str:
        """Generate consistent cache key for embedding operations"""
        content = f"{text}:{model}"
        if options:
            content += f":{json.dumps(options, sort_keys=True)}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"embedding:{hash_value}"
    
    @staticmethod
    def task_key(task_type: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for task results"""
        param_str = json.dumps(parameters, sort_keys=True)
        hash_value = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"task:{task_type}:{hash_value}"
    
    @staticmethod
    def session_key(user_id: str, session_data: Dict[str, Any]) -> str:
        """Generate cache key for user sessions"""
        content = f"{user_id}:{json.dumps(session_data, sort_keys=True)}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"session:{hash_value}"

class ConfigurationManager:
    """Centralized configuration management with environment variable support"""
    
    def __init__(self):
        self._config_cache = {}
        self._last_reload = datetime.utcnow()
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration settings"""
        return {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 8,
            "timeout": 300,
            "keepalive": 30
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration settings"""
        return {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "max_connections": 20,
            "socket_timeout": 30,
            "socket_connect_timeout": 30
        }
    
    def get_service_endpoints(self) -> Dict[str, str]:
        """Get external service endpoint configurations"""
        return {
            "llm01_endpoint": "http://192.168.10.34:8002",
            "llm02_endpoint": "http://192.168.10.28:8000",
            "qdrant_endpoint": "http://192.168.10.30:6333",
            "postgres_url": "postgresql://citadel_llm_user:CitadelLLM#2025$SecurePass!@192.168.10.35:5432/citadel_llm_db",
            "prometheus_endpoint": "http://192.168.10.37:9090"
        }
    
    def reload_config(self):
        """Reload configuration from environment and files"""
        self._config_cache.clear()
        self._last_reload = datetime.utcnow()

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0
) -> Any:
    """Shared retry mechanism with exponential backoff"""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                break
            
            delay = min(base_delay * (exponential_factor ** attempt), max_delay)
            await asyncio.sleep(delay)
    
    raise last_exception

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger = getattr(func, '__self__', None)
            if hasattr(logger, 'logger'):
                logger.logger.debug(f"{func.__name__} executed in {duration:.2f}ms")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            print(f"{func.__name__} executed in {duration:.2f}ms")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

class ConnectionPoolManager:
    """Shared HTTP connection pool management for external services"""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.connector = None
        self.session = None
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def get_session(self):
        """Context manager for HTTP session with connection pooling"""
        async with self._lock:
            if not self.session:
                self.connector = aiohttp.TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=20,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
                self.session = aiohttp.ClientSession(
                    connector=self.connector,
                    timeout=aiohttp.ClientTimeout(total=300)
                )
        
        try:
            yield self.session
        except Exception:
            # Don't close session on error, let it be reused
            raise
    
    async def close(self):
        """Close connection pool and cleanup resources"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
```

### Step 2.3: API Structure and Middleware (1-1.5 hours)

**File:** `/app/api/v1/__init__.py`
```python
"""
API Version 1 Router Configuration
Provides centralized routing for all v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, embeddings, orchestration, metrics, auth

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
```

**File:** `/app/api/v1/endpoints/health.py`
```python
"""
Health Check Endpoints - LLM-01 Compatible Patterns
Provides comprehensive health monitoring and system status
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
import psutil
import asyncio

from app.utils.performance_monitor import MetricsCollector
from app.models.api_models import HealthResponse, DetailedHealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def basic_health_check():
    """Basic health check endpoint (LLM-01 pattern)"""
    return HealthResponse(
        status="healthy",
        service="citadel-orchestration-server",
        version="2.0.0",
        timestamp=datetime.utcnow(),
        server_ip="192.168.10.31"
    )

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with system metrics"""
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Service health checks
    services_status = await check_external_services()
    
    return DetailedHealthResponse(
        status="healthy" if all(services_status.values()) else "degraded",
        service="citadel-orchestration-server",
        version="2.0.0",
        timestamp=datetime.utcnow(),
        server_ip="192.168.10.31",
        system_metrics={
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "memory_available_gb": memory.available / (1024**3)
        },
        service_status=services_status,
        uptime_seconds=get_uptime_seconds()
    )

async def check_external_services() -> Dict[str, bool]:
    """Check connectivity to external services"""
    services = {
        "redis": check_redis_health(),
        "qdrant": check_qdrant_health(),
        "postgres": check_postgres_health()
    }
    
    # Run all checks concurrently
    results = await asyncio.gather(*services.values(), return_exceptions=True)
    
    return {
        service: not isinstance(result, Exception) and result
        for service, result in zip(services.keys(), results)
    }

async def check_redis_health() -> bool:
    """Check Redis connectivity"""
    try:
        import redis.asyncio as redis
        client = redis.Redis(host="localhost", port=6379, db=0)
        await client.ping()
        await client.close()
        return True
    except Exception:
        return False

async def check_qdrant_health() -> bool:
    """Check Qdrant connectivity"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://192.168.10.30:6333/health") as response:
                return response.status == 200
    except Exception:
        return False

async def check_postgres_health() -> bool:
    """Check PostgreSQL connectivity"""
    try:
        import asyncpg
        conn = await asyncpg.connect(
            "postgresql://citadel_llm_user:CitadelLLM#2025$SecurePass!@192.168.10.35:5432/citadel_llm_db"
        )
        await conn.execute("SELECT 1")
        await conn.close()
        return True
    except Exception:
        return False

def get_uptime_seconds() -> float:
    """Get application uptime in seconds"""
    # This would typically track from application startup
    return psutil.boot_time()
```

---

## Success Criteria

### FastAPI Framework
- ✅ Main application running on port 8000 with 8 workers
- ✅ Health endpoints responding with LLM-01 compatible format
- ✅ CORS configured for AG UI integration (192.168.10.38)
- ✅ Request/response logging with structured format
- ✅ OpenAPI documentation accessible at /docs

### Common Class Library (R5.3)
- ✅ Base classes implemented with consistent patterns
- ✅ Shared utility functions providing measurable code reuse
- ✅ Configuration management centralized with environment support
- ✅ Connection pooling and retry mechanisms standardized

### Code Quality
- ✅ All files under 500 lines (R5.4 compliance)
- ✅ OOP principles applied throughout (R5.1)
- ✅ Utility classes properly organized (R5.2)
- ✅ Comprehensive documentation and examples

---

## Next Steps

1. **Task 3:** Celery Task Queue Implementation
2. **Task 4:** Embedding Processing Framework
3. **Integration Testing:** Validate all endpoints and base classes
4. **Performance Baseline:** Establish metrics collection

**Dependencies for Next Task:**
- FastAPI application operational
- Common class library validated
- Health endpoints responding correctly
- Configuration management functional
