"""
Health Check Endpoints

Provides health check endpoints for monitoring and load balancer health checks.
Implements both basic and detailed health checks with dependency validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import asyncio
from datetime import datetime

from app.core.services.monitoring_service import MonitoringService
from app.utils.performance_monitor import PerformanceMonitor

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model"""
    status: str
    timestamp: datetime
    version: str = "2.0.0"
    server: str = "hx-orchestration-server"


class DetailedHealthStatus(BaseModel):
    """Detailed health status with dependency checks"""
    status: str
    timestamp: datetime
    version: str = "2.0.0"
    server: str = "hx-orchestration-server"
    dependencies: Dict[str, Any]
    performance: Dict[str, Any]
    uptime: float


@router.get("/health/", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        HealthStatus: Basic health information
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """
    Comprehensive health check with enterprise orchestration status
    
    Returns:
        Detailed health information including service discovery, load balancer, and enterprise services
    """
    try:
        start_time = time.time()
        
        # Get orchestration components from app state
        service_discovery = getattr(request.app.state, 'service_discovery', None)
        load_balancer = getattr(request.app.state, 'load_balancer', None)
        failover_manager = getattr(request.app.state, 'failover_manager', None)
        monitoring = getattr(request.app.state, 'monitoring', None)
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "server": "hx-orchestration-server",
            "orchestration_capabilities": [
                "service_discovery",
                "load_balancing",
                "automatic_failover",
                "enterprise_routing",
                "llm_coordination"
            ]
        }
        
        # Service Discovery Status
        if service_discovery:
            try:
                service_status = await service_discovery.get_service_status()
                health_data["service_discovery"] = service_status
            except Exception as e:
                health_data["service_discovery"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            health_data["service_discovery"] = {
                "status": "not_initialized",
                "error": "Service discovery not available"
            }
        
        # Load Balancer Status
        if load_balancer:
            try:
                lb_stats = await load_balancer.get_load_balancer_stats()
                health_data["load_balancer"] = lb_stats
            except Exception as e:
                health_data["load_balancer"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            health_data["load_balancer"] = {
                "status": "not_initialized",
                "error": "Load balancer not available"
            }
        
        # Failover Manager Status
        if failover_manager:
            try:
                failover_stats = await failover_manager.get_failover_stats()
                health_data["failover_manager"] = failover_stats
            except Exception as e:
                health_data["failover_manager"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            health_data["failover_manager"] = {
                "status": "not_initialized",
                "error": "Failover manager not available"
            }
        
        # Enterprise Services Health Summary
        if service_discovery:
            try:
                healthy_llm_servers = await service_discovery.registry.get_healthy_services("llm_server")
                healthy_databases = await service_discovery.registry.get_healthy_services("vector_database")
                
                health_data["enterprise_services"] = {
                    "llm_servers": {
                        "total": len([s for s in service_discovery.registry.services.values() if s.get("type") == "llm_server"]),
                        "healthy": len(healthy_llm_servers),
                        "status": "healthy" if healthy_llm_servers else "degraded"
                    },
                    "databases": {
                        "total": len([s for s in service_discovery.registry.services.values() if s.get("type") in ["vector_database", "sql_database"]]),
                        "healthy": len(healthy_databases),
                        "status": "healthy" if healthy_databases else "degraded"
                    }
                }
            except Exception as e:
                health_data["enterprise_services"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Performance Metrics
        end_time = time.time()
        health_data["performance"] = {
            "health_check_duration_ms": round((end_time - start_time) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine overall health status
        components_healthy = True
        if service_discovery and health_data.get("service_discovery", {}).get("service_discovery", {}).get("status") != "running":
            components_healthy = False
        if not service_discovery:
            components_healthy = False
            
        health_data["status"] = "healthy" if components_healthy else "degraded"
        
        return health_data
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "2.0.0",
            "server": "hx-orchestration-server"
        }


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """
    Detailed health check with dependency validation
    
    Returns:
        DetailedHealthStatus: Comprehensive health information
    """
    start_time = time.time()
    
    # Check dependencies
    dependencies = {}
    try:
        monitoring = MonitoringService()
        dependencies = await monitoring.check_dependencies()
    except Exception as e:
        dependencies = {"error": str(e)}
    
    # Get performance metrics
    performance = {}
    try:
        perf_monitor = PerformanceMonitor()
        performance = await perf_monitor.get_current_metrics()
    except Exception as e:
        performance = {"error": str(e)}
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Determine overall status
    status = "healthy"
    if any(dep.get("status") == "unhealthy" for dep in dependencies.values() if isinstance(dep, dict)):
        status = "degraded"
    
    return DetailedHealthStatus(
        status=status,
        timestamp=datetime.utcnow(),
        dependencies=dependencies,
        performance=performance,
        uptime=performance.get("uptime", 0)
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration
    
    Returns:
        dict: Readiness status
    """
    try:
        # Quick dependency checks
        monitoring = MonitoringService()
        dependencies = await monitoring.check_critical_dependencies()
        
        if all(dep.get("status") == "healthy" for dep in dependencies.values()):
            return {"status": "ready", "timestamp": datetime.utcnow()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration
    
    Returns:
        dict: Liveness status
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}
