"""
Service Orchestration Module

Service orchestration and coordination following HXP Governance Coding Standards.
Implements Single Responsibility Principle for service lifecycle management.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from hana_x_vector.utils.metrics import get_metrics_collector, monitor_performance
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration (State encapsulation)."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceInfo:
    """Service information (Data encapsulation)."""
    name: str
    status: ServiceStatus
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    error_message: Optional[str] = None
    health_check_url: Optional[str] = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class ServiceInterface(ABC):
    """
    Abstract interface for managed services (Abstraction principle).
    
    Defines the contract for services managed by the orchestrator.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        pass
    
    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get service information."""
        pass


class ServiceOrchestratorInterface(ABC):
    """
    Abstract interface for service orchestrator (Abstraction principle).
    
    Defines the contract for service orchestration without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def register_service(self, service: ServiceInterface) -> None:
        """Register a service for orchestration."""
        pass
    
    @abstractmethod
    async def unregister_service(self, service_name: str) -> None:
        """Unregister a service."""
        pass
    
    @abstractmethod
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        pass
    
    @abstractmethod
    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        pass
    
    @abstractmethod
    async def start_all_services(self) -> None:
        """Start all registered services."""
        pass
    
    @abstractmethod
    async def stop_all_services(self) -> None:
        """Stop all registered services."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check orchestrator health."""
        pass


class ServiceOrchestrator(ServiceOrchestratorInterface):
    """
    Service orchestrator implementation (Single Responsibility Principle).
    
    Manages service lifecycle, dependencies, health monitoring, and
    coordinated startup/shutdown sequences.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize service orchestrator.
        
        Args:
            config: Configuration dictionary containing orchestrator settings
        """
        self._config = config
        self._services: Dict[str, ServiceInterface] = {}
        self._service_info: Dict[str, ServiceInfo] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        self._health_check_interval = config.get("health_check_interval", 30)
        self._recovery_attempts = config.get("recovery_attempts", 3)
        self._health_check_task = None
        self._running = False
        
        logger.info("ServiceOrchestrator initialized")
    
    async def initialize(self) -> None:
        """Initialize service orchestrator."""
        try:
            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
            self._running = True
            
            logger.info("Service orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize service orchestrator: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown service orchestrator."""
        try:
            # Stop all services
            await self.stop_all_services()
            
            # Stop health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            self._running = False
            logger.info("Service orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Failed to shutdown service orchestrator: {e}")
            raise
    
    @monitor_performance("register_service")
    async def register_service(self, service: ServiceInterface) -> None:
        """
        Register a service for orchestration.
        
        Args:
            service: Service to register
        """
        try:
            service_info = service.get_service_info()
            service_name = service_info.name
            
            # Register service
            self._services[service_name] = service
            self._service_info[service_name] = service_info
            
            # Build dependency graph
            self._dependency_graph[service_name] = service_info.dependencies.copy()
            
            logger.info(f"Service registered: {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            raise
    
    async def unregister_service(self, service_name: str) -> None:
        """
        Unregister a service.
        
        Args:
            service_name: Name of service to unregister
        """
        try:
            if service_name in self._services:
                # Stop service if running
                if self._service_info[service_name].status == ServiceStatus.RUNNING:
                    await self.stop_service(service_name)
                
                # Remove from registry
                del self._services[service_name]
                del self._service_info[service_name]
                del self._dependency_graph[service_name]
                
                logger.info(f"Service unregistered: {service_name}")
            else:
                logger.warning(f"Service not found for unregistration: {service_name}")
                
        except Exception as e:
            logger.error(f"Failed to unregister service {service_name}: {e}")
            raise
    
    @monitor_performance("start_service")
    async def start_service(self, service_name: str) -> bool:
        """
        Start a specific service.
        
        Args:
            service_name: Name of service to start
            
        Returns:
            True if service started successfully
        """
        try:
            if service_name not in self._services:
                logger.error(f"Service not found: {service_name}")
                return False
            
            service_info = self._service_info[service_name]
            
            # Check if already running
            if service_info.status == ServiceStatus.RUNNING:
                logger.info(f"Service already running: {service_name}")
                return True
            
            # Start dependencies first
            for dependency in service_info.dependencies:
                if not await self.start_service(dependency):
                    logger.error(f"Failed to start dependency {dependency} for service {service_name}")
                    return False
            
            # Update status
            service_info.status = ServiceStatus.STARTING
            service_info.start_time = datetime.now()
            service_info.error_message = None
            
            # Start service
            service = self._services[service_name]
            await service.start()
            
            # Update status
            service_info.status = ServiceStatus.RUNNING
            
            logger.info(f"Service started: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            
            # Update error status
            if service_name in self._service_info:
                self._service_info[service_name].status = ServiceStatus.ERROR
                self._service_info[service_name].error_message = str(e)
            
            return False
    
    @monitor_performance("stop_service")
    async def stop_service(self, service_name: str) -> bool:
        """
        Stop a specific service.
        
        Args:
            service_name: Name of service to stop
            
        Returns:
            True if service stopped successfully
        """
        try:
            if service_name not in self._services:
                logger.error(f"Service not found: {service_name}")
                return False
            
            service_info = self._service_info[service_name]
            
            # Check if already stopped
            if service_info.status == ServiceStatus.STOPPED:
                logger.info(f"Service already stopped: {service_name}")
                return True
            
            # Stop dependent services first
            dependent_services = self._get_dependent_services(service_name)
            for dependent in dependent_services:
                await self.stop_service(dependent)
            
            # Update status
            service_info.status = ServiceStatus.STOPPING
            
            # Stop service
            service = self._services[service_name]
            await service.stop()
            
            # Update status
            service_info.status = ServiceStatus.STOPPED
            service_info.stop_time = datetime.now()
            
            logger.info(f"Service stopped: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            
            # Update error status
            if service_name in self._service_info:
                self._service_info[service_name].status = ServiceStatus.ERROR
                self._service_info[service_name].error_message = str(e)
            
            return False
    
    def _get_dependent_services(self, service_name: str) -> List[str]:
        """Get services that depend on the given service."""
        dependents = []
        for name, dependencies in self._dependency_graph.items():
            if service_name in dependencies:
                dependents.append(name)
        return dependents
    
    async def start_all_services(self) -> None:
        """Start all registered services in dependency order."""
        try:
            # Get startup order based on dependencies
            startup_order = self._get_startup_order()
            
            for service_name in startup_order:
                success = await self.start_service(service_name)
                if not success:
                    logger.error(f"Failed to start service {service_name}, stopping startup sequence")
                    break
            
            logger.info("All services startup sequence completed")
            
        except Exception as e:
            logger.error(f"Failed to start all services: {e}")
            raise
    
    async def stop_all_services(self) -> None:
        """Stop all registered services in reverse dependency order."""
        try:
            # Get shutdown order (reverse of startup order)
            startup_order = self._get_startup_order()
            shutdown_order = list(reversed(startup_order))
            
            for service_name in shutdown_order:
                await self.stop_service(service_name)
            
            logger.info("All services shutdown sequence completed")
            
        except Exception as e:
            logger.error(f"Failed to stop all services: {e}")
            raise
    
    def _get_startup_order(self) -> List[str]:
        """Get service startup order based on dependencies (topological sort)."""
        try:
            # Simple topological sort implementation
            visited = set()
            temp_visited = set()
            order = []
            
            def visit(service_name: str):
                if service_name in temp_visited:
                    raise ValueError(f"Circular dependency detected involving {service_name}")
                
                if service_name not in visited:
                    temp_visited.add(service_name)
                    
                    # Visit dependencies first
                    for dependency in self._dependency_graph.get(service_name, []):
                        if dependency in self._services:
                            visit(dependency)
                    
                    temp_visited.remove(service_name)
                    visited.add(service_name)
                    order.append(service_name)
            
            # Visit all services
            for service_name in self._services.keys():
                if service_name not in visited:
                    visit(service_name)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to determine startup order: {e}")
            # Fallback to simple order
            return list(self._services.keys())
    
    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop for all services."""
        while self._running:
            try:
                # Check health of all services
                for service_name, service in self._services.items():
                    await self._check_service_health(service_name, service)
                
                # Wait for next health check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _check_service_health(self, service_name: str, service: ServiceInterface) -> None:
        """Check health of a single service."""
        try:
            service_info = self._service_info[service_name]
            
            # Skip health check if service is not running
            if service_info.status != ServiceStatus.RUNNING:
                return
            
            # Perform health check
            health_result = await service.health_check()
            
            # Check if service is healthy
            is_healthy = health_result.get("status") == "healthy"
            
            if not is_healthy:
                logger.warning(f"Service {service_name} failed health check: {health_result}")
                
                # Attempt recovery if configured
                if self._recovery_attempts > 0:
                    await self._attempt_service_recovery(service_name)
            
            # Record health check metrics
            metrics = get_metrics_collector()
            status = "healthy" if is_healthy else "unhealthy"
            metrics.record_external_model_call(
                service_name, "health_check", status, 0
            )
            
        except Exception as e:
            logger.error(f"Health check failed for service {service_name}: {e}")
    
    async def _attempt_service_recovery(self, service_name: str) -> None:
        """Attempt to recover a failed service."""
        try:
            logger.info(f"Attempting recovery for service: {service_name}")
            
            # Stop and restart the service
            await self.stop_service(service_name)
            await asyncio.sleep(1)  # Brief pause
            success = await self.start_service(service_name)
            
            if success:
                logger.info(f"Service recovery successful: {service_name}")
            else:
                logger.error(f"Service recovery failed: {service_name}")
                
        except Exception as e:
            logger.error(f"Service recovery attempt failed for {service_name}: {e}")
    
    async def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service."""
        if service_name not in self._service_info:
            return None
        
        service_info = self._service_info[service_name]
        return {
            "name": service_info.name,
            "status": service_info.status.value,
            "start_time": service_info.start_time.isoformat() if service_info.start_time else None,
            "stop_time": service_info.stop_time.isoformat() if service_info.stop_time else None,
            "error_message": service_info.error_message,
            "dependencies": service_info.dependencies,
            "metadata": service_info.metadata
        }
    
    async def get_all_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        status = {}
        for service_name in self._services.keys():
            status[service_name] = await self.get_service_status(service_name)
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of service orchestrator.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            total_services = len(self._services)
            running_services = sum(
                1 for info in self._service_info.values()
                if info.status == ServiceStatus.RUNNING
            )
            error_services = sum(
                1 for info in self._service_info.values()
                if info.status == ServiceStatus.ERROR
            )
            
            return {
                "status": "healthy" if self._running else "stopped",
                "message": "Service orchestrator operational" if self._running else "Service orchestrator stopped",
                "running": self._running,
                "services": {
                    "total": total_services,
                    "running": running_services,
                    "error": error_services,
                    "stopped": total_services - running_services - error_services
                },
                "health_check_interval": self._health_check_interval,
                "recovery_attempts": self._recovery_attempts,
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
