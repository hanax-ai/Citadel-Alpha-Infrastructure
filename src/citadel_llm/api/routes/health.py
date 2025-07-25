import logging
from fastapi import APIRouter, HTTPException
from citadel_llm.services.sql_service import sql_service
from citadel_llm.services.vector_service import VectorService
import httpx
import asyncio
import time

router = APIRouter()
logger = logging.getLogger(__name__)

# This is a basic Ollama health check. More sophisticated checks can be added.
async def check_ollama_health(ollama_url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{ollama_url}/api/tags")  # Lightweight endpoint
            response.raise_for_status()
            return True
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.warning(f"Ollama health check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Ollama health check: {e}", exc_info=True)
        return False

async def check_external_service_health(service_name: str, url: str, timeout: int = 3) -> dict:
    """Check health of external monitoring services"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            start_time = time.time()
            response = await client.get(url)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "unavailable",
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code
                }
    except Exception as e:
        logger.warning(f"{service_name} health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/", summary="Comprehensive system health check")
async def comprehensive_health_check():
    """
    Returns the health status of all integrated services including external monitoring.
    """
    # Get Ollama URL from app_config
    from citadel_llm.utils.config import load_config
    current_config = load_config()
    ollama_config = current_config.get('ollama', {})
    ollama_host = ollama_config.get('service', {}).get('host', 'localhost')
    ollama_port = ollama_config.get('service', {}).get('port', 11434)
    ollama_url = f"http://{ollama_host}:{ollama_port}"

    results = {}
    overall_status = "ok"
    
    # Get monitoring configuration
    monitoring_config = current_config.get('monitoring', {})
    external_monitoring = monitoring_config.get('external', {})

    # Check SQL Service
    try:
        sql_ok = await sql_service.health_check()
        if sql_ok:
            # Get basic status without pool info for now
            results["sql_database"] = {
                "status": "ok",
                "details": {"connection": "active"}
            }
        else:
            results["sql_database"] = {"status": "unavailable"}
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"Error checking SQL health: {e}", exc_info=True)
        results["sql_database"] = {"status": "error", "error": str(e)}
        overall_status = "error"

    # Check Vector Service
    try:
        vector_service = VectorService()
        vector_ok = await vector_service.health_check()
        results["vector_database"] = {"status": "ok" if vector_ok else "unavailable"}
        if not vector_ok:
            overall_status = "degraded" if overall_status != "error" else "error"
    except Exception as e:
        logger.error(f"Error checking Vector health: {e}", exc_info=True)
        results["vector_database"] = {"status": "error", "error": str(e)}
        overall_status = "error"

    # Check Ollama Service
    try:
        ollama_ok = await check_ollama_health(ollama_url)
        results["ollama_service"] = {"status": "ok" if ollama_ok else "unavailable"}
        if not ollama_ok:
            overall_status = "degraded" if overall_status != "error" else "error"
    except Exception as e:
        logger.error(f"Error checking Ollama health: {e}", exc_info=True)
        results["ollama_service"] = {"status": "error", "error": str(e)}
        overall_status = "error"

    # Check External Monitoring Services (192.168.10.37)
    external_services = {
        "prometheus": f"http://{external_monitoring.get('prometheus_host', '192.168.10.37')}:9090/-/healthy",
        "grafana": f"http://{external_monitoring.get('grafana_host', '192.168.10.37')}:3000/api/health",
        "alertmanager": f"http://{external_monitoring.get('alertmanager_host', '192.168.10.37')}:9093/-/healthy",
        "node_exporter": f"http://{external_monitoring.get('node_exporter_host', '192.168.10.37')}:9100/metrics"
    }

    # Check external services concurrently
    external_tasks = []
    for service_name, service_url in external_services.items():
        task = check_external_service_health(service_name, service_url)
        external_tasks.append((service_name, task))

    # Wait for all external service checks
    for service_name, task in external_tasks:
        try:
            result = await task
            results[f"external_{service_name}"] = result
            if result["status"] != "ok":
                # External monitoring issues are degraded, not error
                if overall_status == "ok":
                    overall_status = "degraded"
        except Exception as e:
            logger.warning(f"Failed to check {service_name}: {e}")
            results[f"external_{service_name}"] = {"status": "error", "error": str(e)}

    # Add system metadata
    results["system_info"] = {
        "environment": current_config.get('environment', 'production'),
        "version": "1.0.0",
        "server": "hx-llm-server-02",
        "timestamp": time.time()
    }

    # Return appropriate HTTP status based on overall health
    if overall_status == "error":
        raise HTTPException(status_code=503, detail={
            "status": overall_status, 
            "services": results,
            "message": "Critical services are unavailable"
        })
    elif overall_status == "degraded":
        raise HTTPException(status_code=200, detail={
            "status": overall_status,
            "services": results,
            "message": "Some services are experiencing issues"
        })

    return {"status": overall_status, "services": results}

@router.get("/simple", summary="Simple health check")
async def simple_health_check():
    """
    Lightweight health check for load balancers and basic monitoring.
    """
    return {"status": "ok", "timestamp": time.time()}

@router.get("/ready", summary="Readiness probe")
async def readiness_check():
    """
    Kubernetes-style readiness probe - checks if service can handle requests.
    """
    try:
        # Quick check of critical services only
        sql_ok = await sql_service.health_check()
        if not sql_ok:
            raise HTTPException(status_code=503, detail={"ready": False, "reason": "database_unavailable"})
        
        return {"ready": True, "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail={"ready": False, "reason": str(e)})

@router.get("/live", summary="Liveness probe")
async def liveness_check():
    """
    Kubernetes-style liveness probe - checks if service is alive.
    """
    return {"alive": True, "timestamp": time.time()}
