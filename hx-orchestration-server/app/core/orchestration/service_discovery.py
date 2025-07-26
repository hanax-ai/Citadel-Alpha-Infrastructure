"""
Service Discovery Module

Enterprise service discovery and health monitoring for distributed AI infrastructure.
Provides real-time service registration, health checking, and load balancing.
"""

from typing import Dict, List, Any, Optional
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Central service registry for enterprise infrastructure"""
    
    def __init__(self):
        self.services = {}
        self.health_status = {}
        self.last_health_check = {}
        
    async def register_service(
        self,
        service_id: str,
        service_config: Dict[str, Any]
    ) -> bool:
        """Register a service in the registry"""
        try:
            self.services[service_id] = {
                **service_config,
                "registered_at": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Registered service: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_id}: {e}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service configuration"""
        return self.services.get(service_id)
    
    async def get_healthy_services(
        self,
        service_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of healthy services"""
        healthy_services = []
        
        for service_id, config in self.services.items():
            if service_type and config.get("type") != service_type:
                continue
                
            health = self.health_status.get(service_id, {})
            if health.get("status") == "healthy":
                healthy_services.append({
                    "id": service_id,
                    "config": config,
                    "health": health
                })
        
        return healthy_services
    
    async def update_health_status(
        self,
        service_id: str,
        health_data: Dict[str, Any]
    ):
        """Update service health status"""
        self.health_status[service_id] = {
            **health_data,
            "last_updated": datetime.utcnow().isoformat()
        }
        self.last_health_check[service_id] = datetime.utcnow()


class ServiceDiscovery:
    """Service discovery and health monitoring orchestrator"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 10   # seconds
        self.running = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize service discovery system"""
        try:
            # Register known enterprise services
            await self._register_enterprise_services()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            self.running = True
            
            return {
                "service_discovery": "initialized",
                "registered_services": len(self.registry.services),
                "health_monitoring": "active",
                "initialization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize service discovery: {e}")
            raise
    
    async def _register_enterprise_services(self):
        """Register known enterprise services"""
        enterprise_services = {
            "llm_01": {
                "type": "llm_server",
                "hostname": "192.168.10.34",
                "port": 8002,
                "role": "Primary AI Gateway",
                "capabilities": ["chat_completion", "text_completion", "embeddings"],
                "models": ["phi3", "openchat", "mixtral", "nous-hermes2", "nomic-embed"]
            },
            "llm_02": {
                "type": "llm_server", 
                "hostname": "192.168.10.28",
                "port": 8000,
                "role": "Business AI Gateway",
                "capabilities": ["chat_completion", "business_intelligence"],
                "models": ["yi-34b", "deepcoder-14b", "imp-v1-3b", "deepseek-r1"]
            },
            "vector_db": {
                "type": "vector_database",
                "hostname": "192.168.10.30",
                "port": 6333,
                "role": "Vector Database",
                "capabilities": ["vector_storage", "similarity_search", "embeddings"]
            },
            "sql_db": {
                "type": "sql_database",
                "hostname": "192.168.10.35", 
                "port": 5432,
                "role": "SQL Database",
                "capabilities": ["data_storage", "metadata", "audit_logging"]
            },
            "metrics_server": {
                "type": "monitoring",
                "hostname": "192.168.10.37",
                "port": 9090,
                "role": "Metrics Server",
                "capabilities": ["metrics_collection", "monitoring", "alerting"]
            },
            "ag_ui": {
                "type": "user_interface",
                "hostname": "192.168.10.38",
                "port": 3000,
                "role": "AG UI Server",
                "capabilities": ["user_interface", "web_portal", "dashboard"]
            }
        }
        
        for service_id, config in enterprise_services.items():
            await self.registry.register_service(service_id, config)
    
    async def _start_health_monitoring(self):
        """Start background health monitoring"""
        asyncio.create_task(self._health_monitoring_loop())
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while self.running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _perform_health_checks(self):
        """Perform health checks on all registered services"""
        tasks = []
        
        for service_id in self.registry.services.keys():
            task = asyncio.create_task(
                self._check_service_health(service_id)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, service_id: str):
        """Check health of specific service"""
        try:
            service_config = self.registry.services[service_id]
            
            # Determine health check endpoint
            health_endpoint = self._get_health_endpoint(service_config)
            
            if not health_endpoint:
                # Skip health check for services without health endpoints
                return
            
            # Perform health check
            start_time = datetime.utcnow()
            
            async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                response = await client.get(health_endpoint)
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            # Process health check result
            if response.status_code == 200:
                health_data = {
                    "status": "healthy",
                    "response_time": response_time,
                    "last_check": datetime.utcnow().isoformat(),
                    "details": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                }
            else:
                health_data = {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "last_check": datetime.utcnow().isoformat(),
                    "error": f"HTTP {response.status_code}"
                }
            
            await self.registry.update_health_status(service_id, health_data)
            
        except asyncio.TimeoutError:
            await self.registry.update_health_status(service_id, {
                "status": "timeout",
                "last_check": datetime.utcnow().isoformat(),
                "error": "Health check timeout"
            })
            
        except Exception as e:
            await self.registry.update_health_status(service_id, {
                "status": "error",
                "last_check": datetime.utcnow().isoformat(),
                "error": str(e)
            })
    
    def _get_health_endpoint(self, service_config: Dict[str, Any]) -> Optional[str]:
        """Get health check endpoint for service"""
        hostname = service_config.get("hostname")
        port = service_config.get("port")
        service_type = service_config.get("type")
        
        if not hostname or not port:
            return None
        
        # Define health endpoints by service type
        health_endpoints = {
            "llm_server": "/health",
            "vector_database": "/",  # Qdrant root endpoint
            "sql_database": None,    # No HTTP health check
            "monitoring": "/api/v1/status/buildinfo",  # Prometheus
            "user_interface": "/"    # Basic HTTP check
        }
        
        endpoint = health_endpoints.get(service_type)
        if endpoint is None:
            return None
        
        protocol = "https" if port == 443 else "http"
        return f"{protocol}://{hostname}:{port}{endpoint}"
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        total_services = len(self.registry.services)
        healthy_services = await self.registry.get_healthy_services()
        
        return {
            "service_discovery": {
                "status": "running" if self.running else "stopped",
                "total_services": total_services,
                "healthy_services": len(healthy_services),
                "health_check_interval": self.health_check_interval
            },
            "services": {
                service_id: {
                    "config": config,
                    "health": self.registry.health_status.get(service_id, {"status": "unknown"})
                }
                for service_id, config in self.registry.services.items()
            },
            "summary": {
                "llm_servers": len([s for s in self.registry.services.values() if s.get("type") == "llm_server"]),
                "databases": len([s for s in self.registry.services.values() if s.get("type") in ["vector_database", "sql_database"]]),
                "monitoring": len([s for s in self.registry.services.values() if s.get("type") == "monitoring"]),
                "user_interfaces": len([s for s in self.registry.services.values() if s.get("type") == "user_interface"])
            }
        }
    
    async def shutdown(self):
        """Shutdown service discovery"""
        self.running = False
        logger.info("Service discovery shutting down")


# Global service discovery instance
service_discovery = ServiceDiscovery()
