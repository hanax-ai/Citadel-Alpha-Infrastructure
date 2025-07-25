import logging
from fastapi import APIRouter, HTTPException
from citadel_llm.services.sql_service import sql_service
import httpx
import asyncio
import time
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

# Health check configuration
HEALTH_CHECK_TIMEOUT = 5  # seconds
OLLAMA_HEALTH_ENDPOINTS = ["/api/tags", "/api/version"]

async def check_ollama_health(ollama_url: str) -> Dict[str, Any]:
    """
    Comprehensive Ollama health check with multiple validation points.
    """
    health_data = {
        "status": "unknown",
        "response_time_ms": None,
        "available_models": 0,
        "version": None,
        "error": None
    }
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            # Check /api/tags endpoint for model availability
            try:
                tags_response = await client.get(f"{ollama_url}/api/tags")
                tags_response.raise_for_status()
                tags_data = tags_response.json()
                
                if isinstance(tags_data, dict) and "models" in tags_data:
                    health_data["available_models"] = len(tags_data["models"])
                    health_data["status"] = "ok"
                else:
                    health_data["status"] = "degraded"
                    health_data["error"] = "Unexpected tags response format"
                    
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                health_data["status"] = "unavailable"
                health_data["error"] = f"Tags endpoint failed: {str(e)}"
                return health_data
            
            # Check /api/version endpoint for service info
            try:
                version_response = await client.get(f"{ollama_url}/api/version")
                if version_response.status_code == 200:
                    version_data = version_response.json()
                    health_data["version"] = version_data.get("version", "unknown")
            except Exception as e:
                logger.debug(f"Version endpoint check failed (non-critical): {e}")
            
            # Calculate response time
            end_time = time.time()
            health_data["response_time_ms"] = round((end_time - start_time) * 1000, 2)
            
    except asyncio.TimeoutError:
        health_data["status"] = "timeout"
        health_data["error"] = f"Health check timed out after {HEALTH_CHECK_TIMEOUT}s"
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = f"Unexpected error: {str(e)}"
        logger.error(f"Ollama health check error: {e}", exc_info=True)
    
    return health_data

async def check_sql_health() -> Dict[str, Any]:
    """
    Enhanced SQL database health check with connection pool status.
    """
    health_data = {
        "status": "unknown",
        "response_time_ms": None,
        "pool_status": None,
        "error": None
    }
    
    start_time = time.time()
    
    try:
        # Check basic connectivity
        health_result = await sql_service.health_check()
        
        if isinstance(health_result, dict):
            # Detailed health check response
            if health_result.get("status") == "healthy":
                health_data["status"] = "ok"
                
                # Get connection pool information if available
                if "connection_pool" in health_result:
                    pool_info = health_result["connection_pool"]
                    health_data["pool_status"] = {
                        "size": pool_info.get("size", 0),
                        "max_size": pool_info.get("max_size", 0),
                        "min_size": pool_info.get("min_size", 0),
                        "idle_connections": pool_info.get("idle_connections", 0)
                    }
            else:
                health_data["status"] = "unavailable"
                health_data["error"] = health_result.get("error", "Database health check failed")
        elif health_result is True:
            # Simple boolean response
            health_data["status"] = "ok"
        else:
            health_data["status"] = "unavailable"
            health_data["error"] = "Database connectivity check failed"
            
        # Calculate response time
        end_time = time.time()
        health_data["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = f"SQL health check error: {str(e)}"
        logger.error(f"SQL health check error: {e}", exc_info=True)
    
    return health_data

async def check_redis_health() -> Dict[str, Any]:
    """
    Redis cache health check with performance metrics.
    """
    health_data = {
        "status": "unknown",
        "response_time_ms": None,
        "memory_usage": None,
        "connected_clients": None,
        "error": None
    }
    
    start_time = time.time()
    
    try:
        # Import redis service if available
        try:
            from citadel_llm.services.redis_service import redis_service
            
            # Use the health_check method from redis_service
            redis_health = await redis_service.health_check()
            
            if redis_health.get("status") == "healthy":
                health_data["status"] = "ok"
                health_data["memory_usage"] = redis_health.get("used_memory")
                health_data["connected_clients"] = redis_health.get("connected_clients")
            else:
                health_data["status"] = "unavailable"
                health_data["error"] = redis_health.get("error", "Redis health check failed")
                
        except ImportError:
            health_data["status"] = "not_configured"
            health_data["error"] = "Redis service not configured"
        
        # Calculate response time
        end_time = time.time()
        health_data["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = f"Redis health check error: {str(e)}"
        logger.error(f"Redis health check error: {e}", exc_info=True)
    
    return health_data

async def check_system_resources() -> Dict[str, Any]:
    """
    System resource health check using management endpoints.
    """
    health_data = {
        "status": "unknown",
        "cpu_usage": None,
        "memory_usage": None,
        "disk_usage": None,
        "gpu_status": None,
        "error": None
    }
    
    try:
        # Use management endpoints to get system resources
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get("http://localhost:8002/management/system/resources")
            
            if response.status_code == 200:
                resource_data = response.json()
                
                health_data["cpu_usage"] = resource_data.get("cpu_percent")
                health_data["memory_usage"] = resource_data.get("memory", {}).get("percent")
                health_data["disk_usage"] = resource_data.get("disk_root", {}).get("percent")
                
                # GPU status
                gpu_info = resource_data.get("gpu_info", [])
                if gpu_info:
                    health_data["gpu_status"] = f"{len(gpu_info)} GPU(s) available"
                else:
                    health_data["gpu_status"] = "No GPU detected"
                
                # Determine overall system health based on thresholds
                cpu_critical = health_data["cpu_usage"] and health_data["cpu_usage"] > 90
                memory_critical = health_data["memory_usage"] and health_data["memory_usage"] > 95
                disk_critical = health_data["disk_usage"] and health_data["disk_usage"] > 95
                
                if cpu_critical or memory_critical or disk_critical:
                    health_data["status"] = "critical"
                    health_data["error"] = "System resources critically high"
                elif (health_data["cpu_usage"] and health_data["cpu_usage"] > 80) or \
                     (health_data["memory_usage"] and health_data["memory_usage"] > 85) or \
                     (health_data["disk_usage"] and health_data["disk_usage"] > 90):
                    health_data["status"] = "warning"
                    health_data["error"] = "System resources elevated"
                else:
                    health_data["status"] = "ok"
            else:
                health_data["status"] = "unavailable"
                health_data["error"] = f"Resource endpoint returned {response.status_code}"
                
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = f"System resource check error: {str(e)}"
        logger.error(f"System resource health check error: {e}", exc_info=True)
    
    return health_data

@router.get("/", summary="Comprehensive system health check")
async def comprehensive_health_check():
    """
    Returns the health status of all integrated services with detailed metrics.
    """
    # Load configuration for Ollama URL
    try:
        from citadel_llm.utils.config import load_config
        current_config = load_config()
        ollama_config = current_config.get('ollama', {})
        ollama_host = ollama_config.get('service', {}).get('host', 'localhost')
        ollama_port = ollama_config.get('service', {}).get('port', 11434)
        ollama_url = f"http://{ollama_host}:{ollama_port}"
    except Exception as e:
        logger.error(f"Error loading config for health check: {e}")
        ollama_url = "http://localhost:11434"  # fallback

    # Perform all health checks concurrently
    start_time = time.time()
    
    try:
        # Run health checks concurrently for better performance
        sql_task = check_sql_health()
        ollama_task = check_ollama_health(ollama_url)
        redis_task = check_redis_health()
        system_task = check_system_resources()
        
        sql_health, ollama_health, redis_health, system_health = await asyncio.gather(
            sql_task, ollama_task, redis_task, system_task,
            return_exceptions=True
        )
        
        # Handle any exceptions from the health checks
        services = {}
        
        if isinstance(sql_health, Exception):
            services["sql_database"] = {"status": "error", "error": str(sql_health)}
        else:
            services["sql_database"] = sql_health
            
        if isinstance(ollama_health, Exception):
            services["ollama_service"] = {"status": "error", "error": str(ollama_health)}
        else:
            services["ollama_service"] = ollama_health
            
        if isinstance(redis_health, Exception):
            services["redis_cache"] = {"status": "error", "error": str(redis_health)}
        else:
            services["redis_cache"] = redis_health
            
        if isinstance(system_health, Exception):
            services["system_resources"] = {"status": "error", "error": str(system_health)}
        else:
            services["system_resources"] = system_health
        
        # Determine overall system status
        service_statuses = [service.get("status", "unknown") for service in services.values()]
        
        if "error" in service_statuses or "timeout" in service_statuses:
            overall_status = "error"
        elif "critical" in service_statuses:
            overall_status = "critical"
        elif "unavailable" in service_statuses:
            overall_status = "degraded"
        elif "warning" in service_statuses:
            overall_status = "warning"
        else:
            overall_status = "ok"
        
        # Calculate total health check time
        total_time = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "status": overall_status,
            "timestamp": time.time(),
            "check_duration_ms": total_time,
            "services": services,
            "summary": {
                "total_services": len(services),
                "healthy": len([s for s in service_statuses if s == "ok"]),
                "degraded": len([s for s in service_statuses if s in ["warning", "degraded"]]),
                "unhealthy": len([s for s in service_statuses if s in ["error", "critical", "unavailable"]])
            }
        }
        
        # Return appropriate HTTP status based on overall health
        if overall_status in ["error", "critical"]:
            raise HTTPException(status_code=503, detail=response)
        elif overall_status in ["degraded", "warning"]:
            raise HTTPException(status_code=200, detail=response)  # Still 200 but with warnings
        
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "error": f"Health check system failure: {str(e)}",
                "timestamp": time.time()
            }
        )

@router.get("/quick", summary="Quick health check")
async def quick_health_check():
    """
    Fast health check for load balancer/monitoring systems.
    Only checks critical services with minimal overhead.
    """
    try:
        # Quick checks with shorter timeouts
        async with httpx.AsyncClient(timeout=2) as client:
            # Check if gateway is responding
            response = await client.get("http://localhost:8002/management/system/ollama-status")
            
            if response.status_code == 200:
                return {"status": "ok", "timestamp": time.time()}
            else:
                raise HTTPException(
                    status_code=503, 
                    detail={"status": "error", "error": "Core services unavailable"}
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "error": str(e)}
        )

@router.get("/ready", summary="Readiness probe for Kubernetes/container orchestration")
async def readiness_check():
    """
    Kubernetes-style readiness check. Returns 200 only when all critical services are ready.
    """
    try:
        # Check minimal required services for readiness
        sql_healthy = await sql_service.health_check()
        
        async with httpx.AsyncClient(timeout=3) as client:
            ollama_response = await client.get("http://localhost:11434/api/tags")
            ollama_healthy = ollama_response.status_code == 200
        
        if sql_healthy and ollama_healthy:
            return {"status": "ready", "timestamp": time.time()}
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "not_ready",
                    "sql": sql_healthy,
                    "ollama": ollama_healthy
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "error": str(e)}
        )

@router.get("/live", summary="Liveness probe for Kubernetes/container orchestration")
async def liveness_check():
    """
    Kubernetes-style liveness check. Returns 200 if the application is alive and running.
    """
    return {"status": "alive", "timestamp": time.time()}
