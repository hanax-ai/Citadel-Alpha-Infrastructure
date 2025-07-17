"""
Connection Pool
==============

Connection pooling and management for external AI model connections.
Provides efficient connection reuse and load balancing.
"""

from typing import Dict, Any, Optional
import asyncio
import time
from collections import defaultdict
import aiohttp
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import ExternalModelError


class ConnectionPool:
    """
    Connection pool manager for external AI model connections.
    Provides efficient connection reuse and load balancing.
    """
    
    def __init__(self, config: Dict[str, Any], model_configs: Dict[str, Any]):
        self.config = config
        self.model_configs = model_configs
        self.metrics = MetricsCollector()
        
        # Pool configuration
        pool_config = config.get("connection_pool", {})
        self.max_connections_per_model = pool_config.get("max_connections_per_model", 10)
        self.min_connections_per_model = pool_config.get("min_connections_per_model", 2)
        self.connection_timeout = pool_config.get("connection_timeout", 30.0)
        self.idle_timeout = pool_config.get("idle_timeout", 300.0)  # 5 minutes
        self.max_retries = pool_config.get("max_retries", 3)
        
        # Connection pools per model
        self.pools = {}
        self.pool_stats = defaultdict(lambda: {
            "active_connections": 0,
            "idle_connections": 0,
            "total_requests": 0,
            "failed_requests": 0,
            "last_used": 0
        })
        
        # Connection tracking
        self.active_connections = defaultdict(set)
        self.idle_connections = defaultdict(list)
        self.connection_locks = defaultdict(asyncio.Lock)
        
        # Background tasks
        self.cleanup_task = None
        self.health_check_task = None
    
    async def startup(self):
        """Initialize connection pool."""
        # Initialize pools for each model
        for model_name in self.model_configs.keys():
            await self._initialize_model_pool(model_name)
        
        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_idle_connections())
        self.health_check_task = asyncio.create_task(self._health_check_connections())
    
    async def shutdown(self):
        """Cleanup connection pool."""
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Close all connections
        for model_name in self.model_configs.keys():
            await self._close_model_pool(model_name)
    
    async def get_connection(self, model_name: str) -> aiohttp.ClientSession:
        """
        Get a connection from the pool.
        
        Args:
            model_name: Name of the model
            
        Returns:
            HTTP client session
        """
        if model_name not in self.model_configs:
            raise ExternalModelError(f"Unknown model: {model_name}")
        
        async with self.connection_locks[model_name]:
            # Try to get idle connection first
            if self.idle_connections[model_name]:
                connection = self.idle_connections[model_name].pop()
                self.active_connections[model_name].add(connection)
                self.pool_stats[model_name]["idle_connections"] -= 1
                self.pool_stats[model_name]["active_connections"] += 1
                return connection
            
            # Create new connection if under limit
            if len(self.active_connections[model_name]) < self.max_connections_per_model:
                connection = await self._create_connection(model_name)
                self.active_connections[model_name].add(connection)
                self.pool_stats[model_name]["active_connections"] += 1
                return connection
            
            # Wait for available connection
            return await self._wait_for_connection(model_name)
    
    async def return_connection(
        self,
        model_name: str,
        connection: aiohttp.ClientSession
    ):
        """
        Return a connection to the pool.
        
        Args:
            model_name: Name of the model
            connection: HTTP client session to return
        """
        if model_name not in self.model_configs:
            return
        
        async with self.connection_locks[model_name]:
            if connection in self.active_connections[model_name]:
                self.active_connections[model_name].remove(connection)
                self.pool_stats[model_name]["active_connections"] -= 1
                
                # Check if connection is still healthy
                if not connection.closed:
                    self.idle_connections[model_name].append(connection)
                    self.pool_stats[model_name]["idle_connections"] += 1
                    self.pool_stats[model_name]["last_used"] = time.time()
                else:
                    # Connection is closed, don't return to pool
                    await connection.close()
    
    async def get_pool_status(self, model_name: str) -> Dict[str, Any]:
        """
        Get status of connection pool for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Pool status information
        """
        if model_name not in self.model_configs:
            return {"error": f"Unknown model: {model_name}"}
        
        stats = self.pool_stats[model_name]
        
        return {
            "model": model_name,
            "active_connections": stats["active_connections"],
            "idle_connections": stats["idle_connections"],
            "total_connections": stats["active_connections"] + stats["idle_connections"],
            "max_connections": self.max_connections_per_model,
            "total_requests": stats["total_requests"],
            "failed_requests": stats["failed_requests"],
            "success_rate": (stats["total_requests"] - stats["failed_requests"]) / stats["total_requests"] if stats["total_requests"] > 0 else 0,
            "last_used": stats["last_used"]
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get connection pool metrics.
        
        Returns:
            Pool metrics
        """
        total_active = sum(stats["active_connections"] for stats in self.pool_stats.values())
        total_idle = sum(stats["idle_connections"] for stats in self.pool_stats.values())
        total_requests = sum(stats["total_requests"] for stats in self.pool_stats.values())
        total_failures = sum(stats["failed_requests"] for stats in self.pool_stats.values())
        
        model_stats = {}
        for model_name in self.model_configs.keys():
            model_stats[model_name] = await self.get_pool_status(model_name)
        
        return {
            "total_active_connections": total_active,
            "total_idle_connections": total_idle,
            "total_connections": total_active + total_idle,
            "total_requests": total_requests,
            "total_failures": total_failures,
            "overall_success_rate": (total_requests - total_failures) / total_requests if total_requests > 0 else 0,
            "models": model_stats
        }
    
    async def _initialize_model_pool(self, model_name: str):
        """Initialize connection pool for a model."""
        # Create minimum connections
        for _ in range(self.min_connections_per_model):
            try:
                connection = await self._create_connection(model_name)
                self.idle_connections[model_name].append(connection)
                self.pool_stats[model_name]["idle_connections"] += 1
            except Exception as e:
                print(f"Warning: Failed to create initial connection for {model_name}: {e}")
    
    async def _close_model_pool(self, model_name: str):
        """Close all connections for a model."""
        # Close active connections
        for connection in list(self.active_connections[model_name]):
            try:
                await connection.close()
            except Exception:
                pass
        self.active_connections[model_name].clear()
        
        # Close idle connections
        for connection in self.idle_connections[model_name]:
            try:
                await connection.close()
            except Exception:
                pass
        self.idle_connections[model_name].clear()
        
        # Reset stats
        self.pool_stats[model_name] = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_requests": 0,
            "failed_requests": 0,
            "last_used": 0
        }
    
    async def _create_connection(self, model_name: str) -> aiohttp.ClientSession:
        """Create a new connection for a model."""
        model_config = self.model_configs[model_name]
        
        # Configure connection
        timeout = aiohttp.ClientTimeout(total=self.connection_timeout)
        connector = aiohttp.TCPConnector(
            limit=self.max_connections_per_model,
            limit_per_host=self.max_connections_per_model,
            keepalive_timeout=self.idle_timeout
        )
        
        # Create session
        session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "HANA-X-Vector-Database/2.0.0"
            }
        )
        
        return session
    
    async def _wait_for_connection(self, model_name: str) -> aiohttp.ClientSession:
        """Wait for an available connection."""
        # Simple implementation - in production, use proper queuing
        max_wait_time = 30.0  # 30 seconds
        wait_interval = 0.1   # 100ms
        waited = 0
        
        while waited < max_wait_time:
            # Check if connection became available
            if self.idle_connections[model_name]:
                connection = self.idle_connections[model_name].pop()
                self.active_connections[model_name].add(connection)
                self.pool_stats[model_name]["idle_connections"] -= 1
                self.pool_stats[model_name]["active_connections"] += 1
                return connection
            
            # Check if we can create new connection
            if len(self.active_connections[model_name]) < self.max_connections_per_model:
                connection = await self._create_connection(model_name)
                self.active_connections[model_name].add(connection)
                self.pool_stats[model_name]["active_connections"] += 1
                return connection
            
            # Wait and retry
            await asyncio.sleep(wait_interval)
            waited += wait_interval
        
        raise ExternalModelError(f"Timeout waiting for connection to {model_name}")
    
    async def _cleanup_idle_connections(self):
        """Background task to cleanup idle connections."""
        while True:
            try:
                current_time = time.time()
                
                for model_name in self.model_configs.keys():
                    async with self.connection_locks[model_name]:
                        # Check idle connections
                        connections_to_remove = []
                        
                        for connection in self.idle_connections[model_name]:
                            # Check if connection is too old or closed
                            if (connection.closed or 
                                current_time - self.pool_stats[model_name]["last_used"] > self.idle_timeout):
                                connections_to_remove.append(connection)
                        
                        # Remove old connections
                        for connection in connections_to_remove:
                            self.idle_connections[model_name].remove(connection)
                            self.pool_stats[model_name]["idle_connections"] -= 1
                            
                            try:
                                await connection.close()
                            except Exception:
                                pass
                        
                        # Ensure minimum connections
                        current_total = (self.pool_stats[model_name]["active_connections"] + 
                                       self.pool_stats[model_name]["idle_connections"])
                        
                        if current_total < self.min_connections_per_model:
                            needed = self.min_connections_per_model - current_total
                            for _ in range(needed):
                                try:
                                    connection = await self._create_connection(model_name)
                                    self.idle_connections[model_name].append(connection)
                                    self.pool_stats[model_name]["idle_connections"] += 1
                                except Exception as e:
                                    print(f"Warning: Failed to create connection for {model_name}: {e}")
                                    break
                
                # Update metrics
                self.metrics.record_gauge("connection_pool_active", 
                                        sum(stats["active_connections"] for stats in self.pool_stats.values()))
                self.metrics.record_gauge("connection_pool_idle",
                                        sum(stats["idle_connections"] for stats in self.pool_stats.values()))
                
                # Sleep before next cleanup
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in connection cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_connections(self):
        """Background task to health check connections."""
        while True:
            try:
                for model_name in self.model_configs.keys():
                    # Simple health check - test a connection
                    try:
                        connection = await self.get_connection(model_name)
                        
                        # Test connection with simple request
                        model_config = self.model_configs[model_name]
                        url = f"http://{model_config['server']}:{model_config['port']}/health"
                        
                        try:
                            async with connection.get(url) as response:
                                if response.status == 200:
                                    self.metrics.increment_counter("connection_health_checks_success",
                                                                 tags={"model": model_name})
                                else:
                                    self.metrics.increment_counter("connection_health_checks_failed",
                                                                 tags={"model": model_name})
                        except Exception:
                            self.metrics.increment_counter("connection_health_checks_failed",
                                                         tags={"model": model_name})
                        
                        # Return connection
                        await self.return_connection(model_name, connection)
                        
                    except Exception as e:
                        print(f"Health check failed for {model_name}: {e}")
                        self.metrics.increment_counter("connection_health_checks_failed",
                                                     tags={"model": model_name})
                
                # Sleep before next health check
                await asyncio.sleep(300)  # Health check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in health check: {e}")
                await asyncio.sleep(300)
    
    async def invalidate_connections(self, model_name: str):
        """
        Invalidate all connections for a model.
        
        Args:
            model_name: Name of the model
        """
        if model_name not in self.model_configs:
            return
        
        async with self.connection_locks[model_name]:
            # Close all connections
            await self._close_model_pool(model_name)
            
            # Reinitialize pool
            await self._initialize_model_pool(model_name)
    
    async def scale_pool(self, model_name: str, target_size: int):
        """
        Scale connection pool for a model.
        
        Args:
            model_name: Name of the model
            target_size: Target number of connections
        """
        if model_name not in self.model_configs:
            return
        
        target_size = min(target_size, self.max_connections_per_model)
        
        async with self.connection_locks[model_name]:
            current_size = (self.pool_stats[model_name]["active_connections"] + 
                          self.pool_stats[model_name]["idle_connections"])
            
            if target_size > current_size:
                # Add connections
                needed = target_size - current_size
                for _ in range(needed):
                    try:
                        connection = await self._create_connection(model_name)
                        self.idle_connections[model_name].append(connection)
                        self.pool_stats[model_name]["idle_connections"] += 1
                    except Exception as e:
                        print(f"Warning: Failed to scale up connection for {model_name}: {e}")
                        break
            
            elif target_size < current_size:
                # Remove idle connections
                to_remove = min(current_size - target_size, 
                              self.pool_stats[model_name]["idle_connections"])
                
                for _ in range(to_remove):
                    if self.idle_connections[model_name]:
                        connection = self.idle_connections[model_name].pop()
                        self.pool_stats[model_name]["idle_connections"] -= 1
                        
                        try:
                            await connection.close()
                        except Exception:
                            pass
