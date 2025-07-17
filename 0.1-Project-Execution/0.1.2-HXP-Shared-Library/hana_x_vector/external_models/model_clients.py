"""
Model Clients
============

Client connections to external AI models.
Provides standardized interface for embedding generation.
"""

from typing import Dict, Any, List, Optional
import asyncio
import time
import aiohttp
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import ExternalModelError
from .connection_pool import ConnectionPool


class ModelClients:
    """
    Client connections to external AI models.
    Provides standardized interface for embedding generation across different models.
    """
    
    def __init__(self, config: Dict[str, Any], model_configs: Dict[str, Any]):
        self.config = config
        self.model_configs = model_configs
        self.metrics = MetricsCollector()
        
        # Client configuration
        client_config = config.get("model_clients", {})
        self.timeout = client_config.get("timeout", 30.0)
        self.max_retries = client_config.get("max_retries", 3)
        self.retry_delay = client_config.get("retry_delay", 1.0)
        
        # Connection pool
        self.connection_pool = ConnectionPool(config, model_configs)
        
        # HTTP session
        self.session = None
    
    async def startup(self):
        """Initialize model clients."""
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Initialize connection pool
        await self.connection_pool.startup()
    
    async def shutdown(self):
        """Cleanup model clients."""
        if self.session:
            await self.session.close()
        
        await self.connection_pool.shutdown()
    
    async def get_embeddings(
        self,
        model_name: str,
        text_data: List[str],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Get embeddings from external model.
        
        Args:
            model_name: Name of the model
            text_data: List of text to embed
            priority: Request priority
            
        Returns:
            Dict with embeddings and metadata
        """
        start_time = time.time()
        
        try:
            # Validate model
            if model_name not in self.model_configs:
                raise ExternalModelError(f"Unknown model: {model_name}")
            
            model_config = self.model_configs[model_name]
            
            # Get connection from pool
            connection = await self.connection_pool.get_connection(model_name)
            
            try:
                # Prepare request
                request_data = {
                    "input": text_data,
                    "model": model_name,
                    "encoding_format": "float"
                }
                
                # Make request with retry logic
                response_data = await self._make_request_with_retry(
                    connection, model_config, request_data
                )
                
                # Extract embeddings
                embeddings = []
                for item in response_data.get("data", []):
                    embeddings.append(item["embedding"])
                
                # Update metrics
                duration = time.time() - start_time
                self.metrics.record_histogram("model_request_duration", duration,
                                            tags={"model": model_name})
                self.metrics.increment_counter("model_requests_total",
                                             tags={"model": model_name, "status": "success"})
                
                return {
                    "embeddings": embeddings,
                    "model": model_name,
                    "duration": duration,
                    "token_count": response_data.get("usage", {}).get("total_tokens", 0)
                }
                
            finally:
                # Return connection to pool
                await self.connection_pool.return_connection(model_name, connection)
                
        except Exception as e:
            self.metrics.increment_counter("model_requests_total",
                                         tags={"model": model_name, "status": "error"})
            raise ExternalModelError(f"Embedding request failed for {model_name}: {str(e)}")
    
    async def test_connection(self, model_name: str) -> Dict[str, Any]:
        """
        Test connection to a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Connection test results
        """
        start_time = time.time()
        
        try:
            # Test with simple embedding request
            test_result = await self.get_embeddings(
                model_name=model_name,
                text_data=["test connection"],
                priority="high"
            )
            
            latency = time.time() - start_time
            
            return {
                "success": True,
                "latency": latency,
                "model": model_name,
                "embedding_dimensions": len(test_result["embeddings"][0]) if test_result["embeddings"] else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name,
                "latency": time.time() - start_time
            }
    
    async def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """
        Get status of a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model status information
        """
        try:
            if model_name not in self.model_configs:
                return {
                    "status": "unknown",
                    "error": f"Model {model_name} not configured"
                }
            
            model_config = self.model_configs[model_name]
            
            # Test connection
            connection_test = await self.test_connection(model_name)
            
            # Get connection pool status
            pool_status = await self.connection_pool.get_pool_status(model_name)
            
            return {
                "status": "healthy" if connection_test["success"] else "unhealthy",
                "model": model_name,
                "server": f"{model_config['server']}:{model_config['port']}",
                "dimensions": model_config["dimensions"],
                "connection_test": connection_test,
                "connection_pool": pool_status
            }
            
        except Exception as e:
            return {
                "status": "error",
                "model": model_name,
                "error": str(e)
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get client metrics.
        
        Returns:
            Client metrics
        """
        try:
            # Get connection pool metrics
            pool_metrics = await self.connection_pool.get_metrics()
            
            # Get model-specific metrics
            model_metrics = {}
            for model_name in self.model_configs.keys():
                model_metrics[model_name] = {
                    "configured": True,
                    "dimensions": self.model_configs[model_name]["dimensions"],
                    "server": f"{self.model_configs[model_name]['server']}:{self.model_configs[model_name]['port']}"
                }
            
            return {
                "total_models": len(self.model_configs),
                "connection_pool": pool_metrics,
                "models": model_metrics,
                "session_active": self.session is not None and not self.session.closed
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "total_models": len(self.model_configs)
            }
    
    async def _make_request_with_retry(
        self,
        connection: aiohttp.ClientSession,
        model_config: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Construct URL
                url = f"http://{model_config['server']}:{model_config['port']}{model_config['endpoint']}"
                
                # Make request
                async with connection.post(url, json=request_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise ExternalModelError(f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries - 1:
                    break
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # All retries failed
        raise last_exception
    
    async def batch_embeddings(
        self,
        requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process batch embedding requests.
        
        Args:
            requests: List of embedding requests
            
        Returns:
            Batch results
        """
        start_time = time.time()
        
        try:
            # Process requests concurrently
            tasks = []
            for request in requests:
                task = self.get_embeddings(
                    model_name=request["model"],
                    text_data=request["text_data"],
                    priority=request.get("priority", "normal")
                )
                tasks.append(task)
            
            # Execute batch
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_results.append({
                        "request_index": i,
                        "error": str(result)
                    })
                else:
                    successful_results.append({
                        "request_index": i,
                        "result": result
                    })
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_request_duration", duration)
            self.metrics.increment_counter("batch_requests_total", len(requests))
            
            return {
                "successful": successful_results,
                "failed": failed_results,
                "total_requests": len(requests),
                "success_rate": len(successful_results) / len(requests) if requests else 0,
                "duration": duration
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_request_errors")
            raise ExternalModelError(f"Batch processing failed: {str(e)}")
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information
        """
        try:
            if model_name not in self.model_configs:
                raise ExternalModelError(f"Unknown model: {model_name}")
            
            config = self.model_configs[model_name]
            
            # Test connection to get actual capabilities
            connection_test = await self.test_connection(model_name)
            
            return {
                "name": model_name,
                "server": config["server"],
                "port": config["port"],
                "endpoint": config["endpoint"],
                "dimensions": config["dimensions"],
                "max_tokens": config["max_tokens"],
                "status": "healthy" if connection_test["success"] else "unhealthy",
                "actual_dimensions": connection_test.get("embedding_dimensions", 0),
                "latency": connection_test.get("latency", 0)
            }
            
        except Exception as e:
            raise ExternalModelError(f"Model info retrieval failed: {str(e)}")
    
    async def validate_all_models(self) -> Dict[str, Any]:
        """
        Validate connections to all configured models.
        
        Returns:
            Validation results for all models
        """
        try:
            validation_results = {}
            
            # Test all models concurrently
            tasks = []
            for model_name in self.model_configs.keys():
                task = self.test_connection(model_name)
                tasks.append((model_name, task))
            
            # Execute validation tests
            for model_name, task in tasks:
                try:
                    result = await task
                    validation_results[model_name] = result
                except Exception as e:
                    validation_results[model_name] = {
                        "success": False,
                        "error": str(e),
                        "model": model_name
                    }
            
            # Calculate summary statistics
            total_models = len(validation_results)
            healthy_models = sum(1 for r in validation_results.values() if r["success"])
            
            return {
                "results": validation_results,
                "summary": {
                    "total_models": total_models,
                    "healthy_models": healthy_models,
                    "unhealthy_models": total_models - healthy_models,
                    "health_rate": healthy_models / total_models if total_models > 0 else 0
                }
            }
            
        except Exception as e:
            raise ExternalModelError(f"Model validation failed: {str(e)}")
