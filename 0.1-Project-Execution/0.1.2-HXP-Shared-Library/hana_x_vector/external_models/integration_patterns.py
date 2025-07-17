"""
Integration Pattern Manager
===========================

Manages different integration patterns for external AI models.
Supports real-time, hybrid, and bulk integration patterns.
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
from enum import Enum
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import ExternalModelError
from .model_clients import ModelClients
from .connection_pool import ConnectionPool


class IntegrationPattern(Enum):
    """Integration pattern types."""
    REAL_TIME = "real_time"
    HYBRID = "hybrid"
    BULK = "bulk"
    STREAMING = "streaming"


class IntegrationPatternManager:
    """
    Manages different integration patterns for external AI models.
    Provides flexible integration strategies for various use cases.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Integration configuration
        integration_config = config.get("external_models", {})
        self.default_pattern = IntegrationPattern(
            integration_config.get("default_pattern", "real_time")
        )
        self.timeout = integration_config.get("timeout", 30.0)
        self.max_retries = integration_config.get("max_retries", 3)
        self.retry_delay = integration_config.get("retry_delay", 1.0)
        
        # Model configuration
        self.model_configs = {
            "mixtral": {
                "server": "192.168.10.32",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 4096,
                "max_tokens": 8192
            },
            "hermes": {
                "server": "192.168.10.32",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 4096,
                "max_tokens": 4096
            },
            "llama": {
                "server": "192.168.10.32",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 4096,
                "max_tokens": 4096
            },
            "qwen": {
                "server": "192.168.10.32",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 4096,
                "max_tokens": 2048
            },
            "phi": {
                "server": "192.168.10.33",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 2560,
                "max_tokens": 2048
            },
            "gemma": {
                "server": "192.168.10.33",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 2048,
                "max_tokens": 2048
            },
            "deepseek": {
                "server": "192.168.10.33",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 4096,
                "max_tokens": 4096
            },
            "claude": {
                "server": "192.168.10.33",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 1536,
                "max_tokens": 8192
            },
            "general": {
                "server": "192.168.10.33",
                "port": 11400,
                "endpoint": "/v1/embeddings",
                "dimensions": 1536,
                "max_tokens": 512
            }
        }
        
        # Initialize components
        self.model_clients = ModelClients(config, self.model_configs)
        self.connection_pool = ConnectionPool(config, self.model_configs)
        
        # Pattern handlers
        self.pattern_handlers = {
            IntegrationPattern.REAL_TIME: self._handle_real_time,
            IntegrationPattern.HYBRID: self._handle_hybrid,
            IntegrationPattern.BULK: self._handle_bulk,
            IntegrationPattern.STREAMING: self._handle_streaming
        }
    
    async def startup(self):
        """Initialize integration pattern manager."""
        await self.model_clients.startup()
        await self.connection_pool.startup()
    
    async def shutdown(self):
        """Cleanup integration pattern manager."""
        await self.model_clients.shutdown()
        await self.connection_pool.shutdown()
    
    async def process_embedding_request(
        self,
        model_name: str,
        text_data: List[str],
        pattern: Optional[IntegrationPattern] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process embedding request using specified integration pattern.
        
        Args:
            model_name: Name of the AI model
            text_data: List of text to embed
            pattern: Integration pattern to use
            options: Additional options
            
        Returns:
            Dict with embedding results
        """
        start_time = time.time()
        pattern = pattern or self.default_pattern
        options = options or {}
        
        try:
            # Validate model
            if model_name not in self.model_configs:
                raise ExternalModelError(f"Unknown model: {model_name}")
            
            # Get pattern handler
            handler = self.pattern_handlers.get(pattern)
            if not handler:
                raise ExternalModelError(f"Unknown integration pattern: {pattern}")
            
            # Process request
            result = await handler(model_name, text_data, options)
            
            # Update metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("integration_request_duration", duration)
            self.metrics.increment_counter("integration_requests_total", 
                                         tags={"model": model_name, "pattern": pattern.value})
            
            return {
                "embeddings": result["embeddings"],
                "model": model_name,
                "pattern": pattern.value,
                "duration": duration,
                "processed_count": len(text_data)
            }
            
        except Exception as e:
            self.metrics.increment_counter("integration_request_errors",
                                         tags={"model": model_name, "pattern": pattern.value})
            raise ExternalModelError(f"Integration request failed: {str(e)}")
    
    async def process_batch_embeddings(
        self,
        requests: List[Dict[str, Any]],
        pattern: Optional[IntegrationPattern] = None
    ) -> Dict[str, Any]:
        """
        Process batch embedding requests.
        
        Args:
            requests: List of embedding requests
            pattern: Integration pattern to use
            
        Returns:
            Dict with batch results
        """
        start_time = time.time()
        pattern = pattern or IntegrationPattern.BULK
        
        try:
            # Group requests by model
            model_groups = {}
            for request in requests:
                model_name = request["model"]
                if model_name not in model_groups:
                    model_groups[model_name] = []
                model_groups[model_name].append(request)
            
            # Process each model group
            results = {}
            total_processed = 0
            
            for model_name, model_requests in model_groups.items():
                # Combine text data for batch processing
                all_text = []
                request_mapping = []
                
                for i, request in enumerate(model_requests):
                    text_data = request["text_data"]
                    request_mapping.extend([(i, j) for j in range(len(text_data))])
                    all_text.extend(text_data)
                
                # Process batch
                batch_result = await self.process_embedding_request(
                    model_name=model_name,
                    text_data=all_text,
                    pattern=pattern,
                    options={"batch_mode": True}
                )
                
                # Split results back to original requests
                embeddings = batch_result["embeddings"]
                model_results = []
                
                current_idx = 0
                for request in model_requests:
                    request_size = len(request["text_data"])
                    request_embeddings = embeddings[current_idx:current_idx + request_size]
                    current_idx += request_size
                    
                    model_results.append({
                        "request_id": request.get("request_id"),
                        "embeddings": request_embeddings,
                        "processed_count": request_size
                    })
                
                results[model_name] = model_results
                total_processed += len(all_text)
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_integration_duration", duration)
            self.metrics.increment_counter("batch_integration_requests", len(requests))
            
            return {
                "results": results,
                "total_processed": total_processed,
                "duration": duration,
                "pattern": pattern.value
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_integration_errors")
            raise ExternalModelError(f"Batch integration failed: {str(e)}")
    
    async def get_model_status(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of external models.
        
        Args:
            model_name: Optional specific model name
            
        Returns:
            Dict with model status information
        """
        try:
            if model_name:
                if model_name not in self.model_configs:
                    raise ExternalModelError(f"Unknown model: {model_name}")
                
                status = await self.model_clients.get_model_status(model_name)
                return {model_name: status}
            else:
                # Get status for all models
                statuses = {}
                for model in self.model_configs.keys():
                    try:
                        status = await self.model_clients.get_model_status(model)
                        statuses[model] = status
                    except Exception as e:
                        statuses[model] = {"status": "error", "error": str(e)}
                
                return statuses
                
        except Exception as e:
            raise ExternalModelError(f"Status check failed: {str(e)}")
    
    async def _handle_real_time(
        self,
        model_name: str,
        text_data: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle real-time integration pattern."""
        # Process immediately with low latency
        return await self.model_clients.get_embeddings(
            model_name=model_name,
            text_data=text_data,
            priority="high"
        )
    
    async def _handle_hybrid(
        self,
        model_name: str,
        text_data: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle hybrid integration pattern."""
        # Combine real-time and batch processing
        batch_size = options.get("batch_size", 100)
        
        if len(text_data) <= batch_size:
            # Process as real-time
            return await self._handle_real_time(model_name, text_data, options)
        else:
            # Process in batches
            return await self._handle_bulk(model_name, text_data, options)
    
    async def _handle_bulk(
        self,
        model_name: str,
        text_data: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle bulk integration pattern."""
        batch_size = options.get("batch_size", 1000)
        
        # Process in batches
        all_embeddings = []
        
        for i in range(0, len(text_data), batch_size):
            batch = text_data[i:i + batch_size]
            
            batch_result = await self.model_clients.get_embeddings(
                model_name=model_name,
                text_data=batch,
                priority="normal"
            )
            
            all_embeddings.extend(batch_result["embeddings"])
        
        return {"embeddings": all_embeddings}
    
    async def _handle_streaming(
        self,
        model_name: str,
        text_data: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle streaming integration pattern."""
        # Process with streaming for large datasets
        chunk_size = options.get("chunk_size", 50)
        
        async def stream_processor():
            for i in range(0, len(text_data), chunk_size):
                chunk = text_data[i:i + chunk_size]
                
                chunk_result = await self.model_clients.get_embeddings(
                    model_name=model_name,
                    text_data=chunk,
                    priority="normal"
                )
                
                yield chunk_result["embeddings"]
        
        # Collect all streaming results
        all_embeddings = []
        async for chunk_embeddings in stream_processor():
            all_embeddings.extend(chunk_embeddings)
        
        return {"embeddings": all_embeddings}
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration
        """
        if model_name not in self.model_configs:
            raise ExternalModelError(f"Unknown model: {model_name}")
        
        return self.model_configs[model_name].copy()
    
    def list_available_models(self) -> List[str]:
        """
        List all available models.
        
        Returns:
            List of model names
        """
        return list(self.model_configs.keys())
    
    def get_integration_patterns(self) -> List[str]:
        """
        Get list of available integration patterns.
        
        Returns:
            List of pattern names
        """
        return [pattern.value for pattern in IntegrationPattern]
    
    async def validate_model_connection(self, model_name: str) -> Dict[str, Any]:
        """
        Validate connection to a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Validation results
        """
        try:
            if model_name not in self.model_configs:
                raise ExternalModelError(f"Unknown model: {model_name}")
            
            # Test connection
            test_result = await self.model_clients.test_connection(model_name)
            
            return {
                "model": model_name,
                "status": "connected" if test_result["success"] else "failed",
                "latency": test_result.get("latency", 0),
                "error": test_result.get("error")
            }
            
        except Exception as e:
            return {
                "model": model_name,
                "status": "error",
                "error": str(e)
            }
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """
        Get integration metrics and statistics.
        
        Returns:
            Integration metrics
        """
        try:
            # Get connection pool metrics
            pool_metrics = await self.connection_pool.get_metrics()
            
            # Get model client metrics
            client_metrics = await self.model_clients.get_metrics()
            
            return {
                "connection_pool": pool_metrics,
                "model_clients": client_metrics,
                "available_models": len(self.model_configs),
                "supported_patterns": len(self.pattern_handlers)
            }
            
        except Exception as e:
            raise ExternalModelError(f"Metrics retrieval failed: {str(e)}")
