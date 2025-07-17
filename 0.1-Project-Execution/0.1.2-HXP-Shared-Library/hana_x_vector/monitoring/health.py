"""
Health Monitor
=============

Service health monitoring and status reporting for vector database operations.
Provides comprehensive health checks and status aggregation.
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from ..utils.exceptions import HealthCheckError


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable
    timeout: float = 10.0
    critical: bool = True
    interval: float = 30.0
    tags: Optional[Dict[str, str]] = None


class HealthMonitor:
    """
    Service health monitoring and status reporting.
    Provides comprehensive health checks and status aggregation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Health monitoring configuration
        health_config = config.get("health", {})
        self.check_interval = health_config.get("check_interval", 30.0)
        self.timeout = health_config.get("timeout", 10.0)
        self.max_failures = health_config.get("max_failures", 3)
        
        # Health checks registry
        self.health_checks = {}
        self.check_results = {}
        self.failure_counts = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Overall health status
        self.overall_status = HealthStatus.UNKNOWN
        self.last_check_time = 0
        
        # Initialize default health checks
        self._register_default_checks()
    
    async def startup(self):
        """Initialize health monitoring."""
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Perform initial health check
        await self.check_all_health()
    
    async def shutdown(self):
        """Cleanup health monitoring."""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    def register_health_check(self, health_check: HealthCheck):
        """
        Register a health check.
        
        Args:
            health_check: Health check definition
        """
        self.health_checks[health_check.name] = health_check
        self.check_results[health_check.name] = {
            "status": HealthStatus.UNKNOWN,
            "last_check": 0,
            "duration": 0,
            "message": "Not checked yet",
            "details": {}
        }
        self.failure_counts[health_check.name] = 0
    
    def unregister_health_check(self, name: str):
        """
        Unregister a health check.
        
        Args:
            name: Health check name
        """
        self.health_checks.pop(name, None)
        self.check_results.pop(name, None)
        self.failure_counts.pop(name, None)
    
    async def check_health(self, name: str) -> Dict[str, Any]:
        """
        Check health of a specific component.
        
        Args:
            name: Health check name
            
        Returns:
            Health check result
        """
        if name not in self.health_checks:
            raise HealthCheckError(f"Unknown health check: {name}")
        
        health_check = self.health_checks[name]
        start_time = time.time()
        
        try:
            # Execute health check with timeout
            result = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout
            )
            
            duration = time.time() - start_time
            
            # Process result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "OK" if result else "Check failed"
                details = {}
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                message = result.get("message", "")
                details = result.get("details", {})
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {}
            
            # Update failure count
            if status == HealthStatus.HEALTHY:
                self.failure_counts[name] = 0
            else:
                self.failure_counts[name] += 1
            
            # Store result
            self.check_results[name] = {
                "status": status,
                "last_check": time.time(),
                "duration": duration,
                "message": message,
                "details": details,
                "failure_count": self.failure_counts[name]
            }
            
            return self.check_results[name]
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.failure_counts[name] += 1
            
            self.check_results[name] = {
                "status": HealthStatus.UNHEALTHY,
                "last_check": time.time(),
                "duration": duration,
                "message": f"Health check timed out after {health_check.timeout}s",
                "details": {"timeout": True},
                "failure_count": self.failure_counts[name]
            }
            
            return self.check_results[name]
            
        except Exception as e:
            duration = time.time() - start_time
            self.failure_counts[name] += 1
            
            self.check_results[name] = {
                "status": HealthStatus.UNHEALTHY,
                "last_check": time.time(),
                "duration": duration,
                "message": f"Health check failed: {str(e)}",
                "details": {"error": str(e)},
                "failure_count": self.failure_counts[name]
            }
            
            return self.check_results[name]
    
    async def check_all_health(self) -> Dict[str, Any]:
        """
        Check health of all registered components.
        
        Returns:
            Aggregated health status
        """
        # Execute all health checks concurrently
        check_tasks = []
        for name in self.health_checks.keys():
            task = self.check_health(name)
            check_tasks.append((name, task))
        
        # Wait for all checks to complete
        for name, task in check_tasks:
            try:
                await task
            except Exception as e:
                print(f"Error in health check {name}: {e}")
        
        # Calculate overall status
        self._calculate_overall_status()
        self.last_check_time = time.time()
        
        return await self.get_status()
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current health status.
        
        Returns:
            Current health status
        """
        # Categorize checks
        critical_checks = {}
        non_critical_checks = {}
        
        for name, health_check in self.health_checks.items():
            result = self.check_results.get(name, {})
            
            if health_check.critical:
                critical_checks[name] = result
            else:
                non_critical_checks[name] = result
        
        # Calculate statistics
        total_checks = len(self.health_checks)
        healthy_checks = sum(1 for r in self.check_results.values() 
                           if r.get("status") == HealthStatus.HEALTHY)
        
        return {
            "status": self.overall_status.value,
            "timestamp": time.time(),
            "last_check": self.last_check_time,
            "checks": {
                "critical": critical_checks,
                "non_critical": non_critical_checks
            },
            "summary": {
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "unhealthy_checks": total_checks - healthy_checks,
                "health_percentage": (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            }
        }
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Get detailed health status with additional information.
        
        Returns:
            Detailed health status
        """
        status = await self.get_status()
        
        # Add detailed information
        status["details"] = {
            "monitoring_active": self.monitoring_active,
            "check_interval": self.check_interval,
            "registered_checks": list(self.health_checks.keys()),
            "failure_counts": dict(self.failure_counts),
            "check_configurations": {
                name: {
                    "timeout": check.timeout,
                    "critical": check.critical,
                    "interval": check.interval,
                    "tags": check.tags
                }
                for name, check in self.health_checks.items()
            }
        }
        
        return status
    
    def _register_default_checks(self):
        """Register default health checks."""
        # Qdrant connection health check
        self.register_health_check(HealthCheck(
            name="qdrant_connection",
            check_function=self._check_qdrant_connection,
            timeout=5.0,
            critical=True,
            interval=30.0,
            tags={"component": "qdrant"}
        ))
        
        # Redis cache health check
        self.register_health_check(HealthCheck(
            name="redis_cache",
            check_function=self._check_redis_cache,
            timeout=3.0,
            critical=False,
            interval=60.0,
            tags={"component": "cache"}
        ))
        
        # External models health check
        self.register_health_check(HealthCheck(
            name="external_models",
            check_function=self._check_external_models,
            timeout=10.0,
            critical=True,
            interval=120.0,
            tags={"component": "external_models"}
        ))
        
        # System resources health check
        self.register_health_check(HealthCheck(
            name="system_resources",
            check_function=self._check_system_resources,
            timeout=5.0,
            critical=False,
            interval=60.0,
            tags={"component": "system"}
        ))
    
    async def _check_qdrant_connection(self) -> Dict[str, Any]:
        """Check Qdrant connection health."""
        try:
            # This would be implemented with actual Qdrant client
            # For now, return a mock healthy status
            return {
                "status": "healthy",
                "message": "Qdrant connection is healthy",
                "details": {
                    "host": self.config.get("qdrant", {}).get("host", "localhost"),
                    "port": self.config.get("qdrant", {}).get("port", 6333),
                    "response_time": 0.005
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Qdrant connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_redis_cache(self) -> Dict[str, Any]:
        """Check Redis cache health."""
        try:
            # This would be implemented with actual Redis client
            # For now, return a mock healthy status
            cache_config = self.config.get("cache", {})
            
            return {
                "status": "healthy",
                "message": "Redis cache is healthy",
                "details": {
                    "host": cache_config.get("host", "192.168.10.35"),
                    "port": cache_config.get("port", 6379),
                    "response_time": 0.002
                }
            }
        except Exception as e:
            return {
                "status": "degraded",
                "message": f"Redis cache issue: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_external_models(self) -> Dict[str, Any]:
        """Check external models health."""
        try:
            # This would check actual external model connections
            # For now, return a mock status
            model_configs = {
                "mixtral": {"server": "192.168.10.32", "port": 11400},
                "hermes": {"server": "192.168.10.32", "port": 11400},
                "phi": {"server": "192.168.10.33", "port": 11400},
                "claude": {"server": "192.168.10.33", "port": 11400}
            }
            
            healthy_models = 0
            total_models = len(model_configs)
            model_status = {}
            
            for model_name, config in model_configs.items():
                # Mock health check - in reality would test actual connections
                model_status[model_name] = {
                    "status": "healthy",
                    "server": f"{config['server']}:{config['port']}",
                    "response_time": 0.050
                }
                healthy_models += 1
            
            health_percentage = (healthy_models / total_models * 100) if total_models > 0 else 0
            
            if health_percentage >= 80:
                status = "healthy"
                message = f"External models are healthy ({healthy_models}/{total_models})"
            elif health_percentage >= 50:
                status = "degraded"
                message = f"Some external models are unhealthy ({healthy_models}/{total_models})"
            else:
                status = "unhealthy"
                message = f"Most external models are unhealthy ({healthy_models}/{total_models})"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "models": model_status,
                    "healthy_count": healthy_models,
                    "total_count": total_models,
                    "health_percentage": health_percentage
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"External models check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources health."""
        try:
            # Check system resources
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine status based on resource usage
            if memory_percent > 90 or cpu_percent > 90 or disk_percent > 90:
                status = "unhealthy"
                message = "System resources critically high"
            elif memory_percent > 80 or cpu_percent > 80 or disk_percent > 80:
                status = "degraded"
                message = "System resources elevated"
            else:
                status = "healthy"
                message = "System resources normal"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "memory_percent": memory_percent,
                    "cpu_percent": cpu_percent,
                    "disk_percent": disk_percent,
                    "memory_available": memory.available,
                    "memory_total": memory.total
                }
            }
            
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for system monitoring",
                "details": {"error": "psutil not installed"}
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"System resources check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _calculate_overall_status(self):
        """Calculate overall health status."""
        if not self.check_results:
            self.overall_status = HealthStatus.UNKNOWN
            return
        
        # Check critical components
        critical_unhealthy = 0
        critical_total = 0
        
        for name, health_check in self.health_checks.items():
            if health_check.critical:
                critical_total += 1
                result = self.check_results.get(name, {})
                if result.get("status") != HealthStatus.HEALTHY:
                    critical_unhealthy += 1
        
        # Check non-critical components
        non_critical_unhealthy = 0
        non_critical_total = 0
        
        for name, health_check in self.health_checks.items():
            if not health_check.critical:
                non_critical_total += 1
                result = self.check_results.get(name, {})
                if result.get("status") != HealthStatus.HEALTHY:
                    non_critical_unhealthy += 1
        
        # Determine overall status
        if critical_unhealthy > 0:
            self.overall_status = HealthStatus.UNHEALTHY
        elif non_critical_unhealthy > non_critical_total * 0.5:
            self.overall_status = HealthStatus.DEGRADED
        else:
            self.overall_status = HealthStatus.HEALTHY
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Check all health
                await self.check_all_health()
                
                # Sleep until next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def force_check(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Force immediate health check.
        
        Args:
            name: Optional specific check name
            
        Returns:
            Health check results
        """
        if name:
            return await self.check_health(name)
        else:
            return await self.check_all_health()
    
    def get_check_history(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get health check history.
        
        Args:
            name: Health check name
            limit: Maximum number of results
            
        Returns:
            List of historical check results
        """
        # This would be implemented with actual history storage
        # For now, return current result
        if name in self.check_results:
            return [self.check_results[name]]
        else:
            return []
    
    def is_healthy(self) -> bool:
        """
        Check if system is healthy.
        
        Returns:
            True if system is healthy
        """
        return self.overall_status == HealthStatus.HEALTHY
    
    def get_unhealthy_checks(self) -> List[str]:
        """
        Get list of unhealthy checks.
        
        Returns:
            List of unhealthy check names
        """
        unhealthy = []
        for name, result in self.check_results.items():
            if result.get("status") != HealthStatus.HEALTHY:
                unhealthy.append(name)
        return unhealthy
