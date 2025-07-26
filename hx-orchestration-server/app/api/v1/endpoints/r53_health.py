"""
Health Check Endpoints - LLM-01 Compatible Patterns (R5.3 Compliance)
Provides comprehensive health monitoring and system status
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
import psutil
import asyncio
import aiohttp
import time

try:
    import asyncpg
except ImportError:
    asyncpg = None

from app.models.r53_api_models import HealthResponse, DetailedHealthResponse
from app.utils.r53_common_utilities import timing_decorator

router = APIRouter()

@router.get("/", response_model=HealthResponse)
@timing_decorator
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
@timing_decorator
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
            "memory_available_gb": memory.available / (1024**3),
            "load_average_1min": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        },
        service_status=services_status,
        uptime_seconds=get_uptime_seconds()
    )

@router.get("/services")
async def services_health_check():
    """Individual service health status"""
    services = await check_external_services()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "services": services,
        "overall_status": "healthy" if all(services.values()) else "degraded"
    }

async def check_external_services() -> Dict[str, bool]:
    """Check connectivity to external services"""
    checks = {
        "redis": check_redis_health(),
        "qdrant": check_qdrant_health(),
        "database": check_database_health(),
        "ollama": check_ollama_health()
    }
    
    # Run all checks concurrently with timeout
    results = await asyncio.gather(*checks.values(), return_exceptions=True)
    
    return {
        service: not isinstance(result, Exception) and result
        for service, result in zip(checks.keys(), results)
    }

async def check_redis_health() -> bool:
    """Check Redis connection health."""
    try:
        import redis.asyncio as redis
        # Connect to Redis with authentication
        client = redis.Redis(
            host="192.168.10.35", 
            port=6379, 
            password="Major8859!",
            db=0, 
            socket_connect_timeout=5
        )
        await client.ping()
        await client.close()
        return True
    except Exception:
        return False

async def check_qdrant_health() -> bool:
    """Check Qdrant vector database connectivity"""
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Connect to Qdrant at the vector database server
            async with session.get("http://192.168.10.30:6333/health") as response:
                return response.status == 200
    except Exception:
        return False

async def check_database_health() -> bool:
    """Check PostgreSQL database connectivity"""
    try:
        conn = await asyncpg.connect(
            host="192.168.10.35",
            port=5432,  # Direct PostgreSQL port
            database="citadel_llm_db",
            user="citadel_llm_user",
            password="CitadelLLM#2025$SecurePass!"
        )
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

async def check_ollama_health() -> bool:
    """Check Ollama service health."""
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                return response.status == 200
    except Exception:
        return False

def get_uptime_seconds() -> float:
    """Get application uptime in seconds"""
    # This would typically track from application startup
    # For now, return system boot time as approximation
    return time.time() - psutil.boot_time()

@router.get("/metrics/system")
async def system_metrics():
    """Detailed system performance metrics"""
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    network = psutil.net_io_counters()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
        },
        "memory": {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent": memory.percent
        },
        "swap": {
            "total_gb": swap.total / (1024**3),
            "used_gb": swap.used / (1024**3),
            "percent": swap.percent
        },
        "disk": {
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "percent": (disk.used / disk.total) * 100
        },
        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
    }
