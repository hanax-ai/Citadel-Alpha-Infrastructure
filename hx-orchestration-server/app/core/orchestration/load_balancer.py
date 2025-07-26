"""
Load Balancer Module

Enterprise load balancing for distributed AI services.
Provides intelligent request routing, health-aware distribution, and failover capabilities.
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime, timedelta
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class LoadBalancingStrategy:
    """Base class for load balancing strategies"""
    
    async def select_server(
        self,
        available_servers: List[Dict[str, Any]],
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Select optimal server for request"""
        raise NotImplementedError


class RoundRobinStrategy(LoadBalancingStrategy):
    """Round-robin load balancing strategy"""
    
    def __init__(self):
        self.counters = defaultdict(int)
    
    async def select_server(
        self,
        available_servers: List[Dict[str, Any]],
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        if not available_servers:
            return None
        
        service_type = request_context.get("service_type", "default") if request_context else "default"
        
        # Get current counter and increment
        current = self.counters[service_type]
        self.counters[service_type] = (current + 1) % len(available_servers)
        
        return available_servers[current]


class WeightedResponseTimeStrategy(LoadBalancingStrategy):
    """Weighted response time load balancing strategy"""
    
    async def select_server(
        self,
        available_servers: List[Dict[str, Any]],
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        if not available_servers:
            return None
        
        # Select server with best response time
        best_server = available_servers[0]
        best_response_time = float('inf')
        
        for server in available_servers:
            health = server.get("health", {})
            response_time = health.get("response_time", float('inf'))
            
            if response_time < best_response_time:
                best_response_time = response_time
                best_server = server
        
        return best_server


class LeastConnectionsStrategy(LoadBalancingStrategy):
    """Least connections load balancing strategy"""
    
    def __init__(self):
        self.connection_counts = defaultdict(int)
    
    async def select_server(
        self,
        available_servers: List[Dict[str, Any]],
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        if not available_servers:
            return None
        
        # Select server with least connections
        best_server = available_servers[0]
        least_connections = float('inf')
        
        for server in available_servers:
            server_id = server.get("id", "unknown")
            connections = self.connection_counts[server_id]
            
            if connections < least_connections:
                least_connections = connections
                best_server = server
        
        return best_server
    
    def increment_connections(self, server_id: str):
        """Increment connection count for server"""
        self.connection_counts[server_id] += 1
    
    def decrement_connections(self, server_id: str):
        """Decrement connection count for server"""
        if self.connection_counts[server_id] > 0:
            self.connection_counts[server_id] -= 1


class IntelligentStrategy(LoadBalancingStrategy):
    """Intelligent load balancing with multiple factors"""
    
    async def select_server(
        self,
        available_servers: List[Dict[str, Any]],
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        if not available_servers:
            return None
        
        request_context = request_context or {}
        
        # Score each server based on multiple factors
        scored_servers = []
        
        for server in available_servers:
            score = await self._calculate_server_score(server, request_context)
            scored_servers.append((server, score))
        
        # Sort by score (higher is better)
        scored_servers.sort(key=lambda x: x[1], reverse=True)
        
        return scored_servers[0][0]
    
    async def _calculate_server_score(
        self,
        server: Dict[str, Any],
        request_context: Dict[str, Any]
    ) -> float:
        """Calculate server score based on multiple factors"""
        score = 0.0
        
        config = server.get("config", {})
        health = server.get("health", {})
        
        # Health status factor (40% weight)
        if health.get("status") == "healthy":
            score += 0.4
        
        # Response time factor (30% weight)
        response_time = health.get("response_time", float('inf'))
        if response_time < float('inf'):
            # Better response time = higher score
            score += 0.3 * max(0, 1 - (response_time / 10.0))
        
        # Capability matching factor (20% weight)
        required_capability = request_context.get("required_capability")
        if required_capability:
            capabilities = config.get("capabilities", [])
            if required_capability in capabilities:
                score += 0.2
        
        # Model availability factor (10% weight)
        required_model = request_context.get("model")
        if required_model:
            models = config.get("models", [])
            if required_model in models:
                score += 0.1
        
        return score


class LoadBalancer:
    """Enterprise load balancer for AI services"""
    
    def __init__(self, service_discovery):
        self.service_discovery = service_discovery
        self.strategies = {
            "round_robin": RoundRobinStrategy(),
            "response_time": WeightedResponseTimeStrategy(),
            "least_connections": LeastConnectionsStrategy(),
            "intelligent": IntelligentStrategy()
        }
        self.default_strategy = "intelligent"
        self.request_stats = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        })
    
    async def select_server(
        self,
        service_type: str,
        request_context: Dict[str, Any] = None,
        strategy: str = None
    ) -> Optional[Dict[str, Any]]:
        """Select optimal server for request"""
        try:
            # Get healthy services of the specified type
            healthy_services = await self.service_discovery.registry.get_healthy_services(
                service_type=service_type
            )
            
            if not healthy_services:
                logger.warning(f"No healthy services of type {service_type} available")
                return None
            
            # Use specified strategy or default
            strategy_name = strategy or self.default_strategy
            load_balancing_strategy = self.strategies.get(strategy_name)
            
            if not load_balancing_strategy:
                logger.warning(f"Unknown strategy {strategy_name}, using default")
                load_balancing_strategy = self.strategies[self.default_strategy]
            
            # Add service type to request context
            if request_context is None:
                request_context = {}
            request_context["service_type"] = service_type
            
            # Select server using strategy
            selected_server = await load_balancing_strategy.select_server(
                healthy_services, request_context
            )
            
            if selected_server:
                # Update request tracking
                if isinstance(load_balancing_strategy, LeastConnectionsStrategy):
                    load_balancing_strategy.increment_connections(selected_server["id"])
            
            return selected_server
            
        except Exception as e:
            logger.error(f"Load balancer error: {e}")
            return None
    
    async def release_server(self, server: Dict[str, Any], success: bool = True):
        """Release server after request completion"""
        try:
            server_id = server.get("id")
            if not server_id:
                return
            
            # Update statistics
            stats = self.request_stats[server_id]
            stats["total_requests"] += 1
            
            if success:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
            
            # Update connection count for least connections strategy
            if isinstance(self.strategies["least_connections"], LeastConnectionsStrategy):
                self.strategies["least_connections"].decrement_connections(server_id)
                
        except Exception as e:
            logger.error(f"Error releasing server: {e}")
    
    async def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        total_requests = sum(
            stats["total_requests"] for stats in self.request_stats.values()
        )
        
        return {
            "load_balancer": {
                "default_strategy": self.default_strategy,
                "available_strategies": list(self.strategies.keys()),
                "total_requests": total_requests
            },
            "server_stats": dict(self.request_stats),
            "strategies": {
                name: {
                    "type": strategy.__class__.__name__,
                    "description": strategy.__doc__ or "No description"
                }
                for name, strategy in self.strategies.items()
            }
        }
    
    async def configure_strategy(
        self,
        service_type: str,
        strategy: str,
        parameters: Dict[str, Any] = None
    ) -> bool:
        """Configure load balancing strategy for service type"""
        try:
            if strategy not in self.strategies:
                logger.error(f"Unknown strategy: {strategy}")
                return False
            
            # Strategy configuration would be implemented here
            # For now, we just log the configuration
            logger.info(f"Configured {strategy} strategy for {service_type}")
            return True
            
        except Exception as e:
            logger.error(f"Strategy configuration error: {e}")
            return False


class FailoverManager:
    """Manages failover scenarios and service recovery"""
    
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
        self.failover_history = []
        self.max_history = 100
    
    async def handle_service_failure(
        self,
        failed_server: Dict[str, Any],
        service_type: str,
        request_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Handle service failure and select backup server"""
        try:
            failed_server_id = failed_server.get("id", "unknown")
            
            # Log failover event
            failover_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "failed_server": failed_server_id,
                "service_type": service_type,
                "reason": "service_failure"
            }
            
            # Get alternative server
            backup_server = await self.load_balancer.select_server(
                service_type=service_type,
                request_context=request_context
            )
            
            if backup_server and backup_server.get("id") != failed_server_id:
                failover_event["backup_server"] = backup_server.get("id")
                failover_event["status"] = "success"
                
                logger.info(f"Failover successful: {failed_server_id} -> {backup_server.get('id')}")
                
            else:
                failover_event["status"] = "failed"
                failover_event["reason"] = "no_backup_available"
                
                logger.error(f"Failover failed: no backup server available for {service_type}")
            
            # Record failover event
            self.failover_history.append(failover_event)
            if len(self.failover_history) > self.max_history:
                self.failover_history.pop(0)
            
            return backup_server
            
        except Exception as e:
            logger.error(f"Failover handling error: {e}")
            return None
    
    async def get_failover_stats(self) -> Dict[str, Any]:
        """Get failover statistics"""
        if not self.failover_history:
            return {
                "total_failovers": 0,
                "successful_failovers": 0,
                "failed_failovers": 0,
                "recent_events": []
            }
        
        successful = len([e for e in self.failover_history if e.get("status") == "success"])
        failed = len([e for e in self.failover_history if e.get("status") == "failed"])
        
        return {
            "total_failovers": len(self.failover_history),
            "successful_failovers": successful,
            "failed_failovers": failed,
            "success_rate": successful / len(self.failover_history) if self.failover_history else 0,
            "recent_events": self.failover_history[-10:]  # Last 10 events
        }
