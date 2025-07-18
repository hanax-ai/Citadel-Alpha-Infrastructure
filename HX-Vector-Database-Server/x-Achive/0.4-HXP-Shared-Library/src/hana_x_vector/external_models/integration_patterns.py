"""
External Model Integration Patterns Module

Integration patterns for external AI models following HXP Governance Coding Standards.
Implements Single Responsibility Principle for external model integration.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime, timedelta
import aiohttp
import json
from enum import Enum

from hana_x_vector.models.external_models import (
    ExternalModel, ModelResponse, IntegrationPattern, ExternalModelType
)
from hana_x_vector.utils.metrics import get_metrics_collector, monitor_performance
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


class ExternalModelIntegratorInterface(ABC):
    """
    Abstract interface for external model integrator (Abstraction principle).
    
    Defines the contract for external model integration without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def call_model(self, model: ExternalModel, request_data: Dict[str, Any]) -> ModelResponse:
        """Call external model with request data."""
        pass
    
    @abstractmethod
    async def health_check(self, model: ExternalModel) -> bool:
        """Check health of external model."""
        pass
    
    @abstractmethod
    async def get_model_info(self, model: ExternalModel) -> Dict[str, Any]:
        """Get model information."""
        pass


class RealTimeIntegrator(ExternalModelIntegratorInterface):
    """
    Real-time integration pattern (Single Responsibility Principle).
    
    Handles direct API calls to external models with immediate response.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize real-time integrator."""
        self._config = config
        self._session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    @monitor_performance("external_model_call")
    async def call_model(self, model: ExternalModel, request_data: Dict[str, Any]) -> ModelResponse:
        """
        Call external model with real-time API request.
        
        Args:
            model: External model configuration
            request_data: Request data to send to model
            
        Returns:
            ModelResponse with API response
        """
        start_time = datetime.now()
        
        try:
            session = await self._get_session()
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if model.api_key_name:
                import os
                api_key = os.getenv(model.api_key_name)
                if api_key:
                    if model.model_type == ExternalModelType.OPENAI_GPT4:
                        headers["Authorization"] = f"Bearer {api_key}"
                    elif model.model_type == ExternalModelType.ANTHROPIC_CLAUDE:
                        headers["x-api-key"] = api_key
                    elif model.model_type == ExternalModelType.COHERE_COMMAND:
                        headers["Authorization"] = f"Bearer {api_key}"
            
            # Make API call
            async with session.post(
                model.api_endpoint,
                json=request_data,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Extract token usage if available
                tokens_used = self._extract_token_usage(response_data, model.model_type)
                
                return ModelResponse(
                    model_id=model.id,
                    response_data=response_data,
                    success=response.status == 200,
                    error_message=None if response.status == 200 else f"HTTP {response.status}",
                    processing_time_ms=processing_time,
                    tokens_used=tokens_used,
                    cached=False
                )
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Real-time model call failed for {model.id}: {e}")
            
            return ModelResponse(
                model_id=model.id,
                response_data={},
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
                cached=False
            )
    
    def _extract_token_usage(self, response_data: Dict[str, Any], model_type: ExternalModelType) -> Optional[int]:
        """Extract token usage from response data."""
        try:
            if model_type in [ExternalModelType.OPENAI_GPT4, ExternalModelType.OPENAI_GPT35]:
                return response_data.get("usage", {}).get("total_tokens")
            elif model_type == ExternalModelType.ANTHROPIC_CLAUDE:
                return response_data.get("usage", {}).get("input_tokens", 0) + \
                       response_data.get("usage", {}).get("output_tokens", 0)
            elif model_type == ExternalModelType.COHERE_COMMAND:
                return response_data.get("meta", {}).get("tokens", {}).get("input_tokens", 0) + \
                       response_data.get("meta", {}).get("tokens", {}).get("output_tokens", 0)
        except:
            pass
        return None
    
    async def health_check(self, model: ExternalModel) -> bool:
        """Check health of external model."""
        try:
            # Simple health check with minimal request
            health_request = {"model": "test", "max_tokens": 1}
            response = await self.call_model(model, health_request)
            return response.success
        except:
            return False
    
    async def get_model_info(self, model: ExternalModel) -> Dict[str, Any]:
        """Get model information."""
        return {
            "id": model.id,
            "name": model.name,
            "type": model.model_type.value,
            "pattern": "real_time",
            "endpoint": model.api_endpoint,
            "capabilities": [cap.value for cap in model.capabilities]
        }
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()


class HybridIntegrator(ExternalModelIntegratorInterface):
    """
    Hybrid integration pattern (Single Responsibility Principle).
    
    Combines caching with real-time calls for optimal performance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize hybrid integrator."""
        self._config = config
        self._real_time_integrator = RealTimeIntegrator(config)
        self._cache = {}  # Simple in-memory cache (would use Redis in production)
        
    @monitor_performance("external_model_call_hybrid")
    async def call_model(self, model: ExternalModel, request_data: Dict[str, Any]) -> ModelResponse:
        """
        Call external model with hybrid caching strategy.
        
        Args:
            model: External model configuration
            request_data: Request data to send to model
            
        Returns:
            ModelResponse with cached or real-time response
        """
        try:
            # Generate cache key
            cache_key = model.get_cache_key(json.dumps(request_data, sort_keys=True))
            
            # Check cache first
            cached_response = self._get_from_cache(cache_key, model)
            if cached_response:
                cached_response.cached = True
                return cached_response
            
            # Make real-time call
            response = await self._real_time_integrator.call_model(model, request_data)
            
            # Cache successful responses
            if response.success and model.cache_ttl_seconds:
                self._store_in_cache(cache_key, response, model.cache_ttl_seconds)
            
            return response
            
        except Exception as e:
            logger.error(f"Hybrid model call failed for {model.id}: {e}")
            return ModelResponse(
                model_id=model.id,
                response_data={},
                success=False,
                error_message=str(e),
                cached=False
            )
    
    def _get_from_cache(self, cache_key: str, model: ExternalModel) -> Optional[ModelResponse]:
        """Get response from cache."""
        try:
            if cache_key in self._cache:
                cached_item = self._cache[cache_key]
                
                # Check if cache entry is still valid
                if datetime.now() < cached_item["expires_at"]:
                    return cached_item["response"]
                else:
                    # Remove expired entry
                    del self._cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    def _store_in_cache(self, cache_key: str, response: ModelResponse, ttl_seconds: int) -> None:
        """Store response in cache."""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[cache_key] = {
                "response": response,
                "expires_at": expires_at
            }
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    async def health_check(self, model: ExternalModel) -> bool:
        """Check health of external model."""
        return await self._real_time_integrator.health_check(model)
    
    async def get_model_info(self, model: ExternalModel) -> Dict[str, Any]:
        """Get model information."""
        info = await self._real_time_integrator.get_model_info(model)
        info["pattern"] = "hybrid"
        info["cache_enabled"] = True
        info["cache_ttl_seconds"] = model.cache_ttl_seconds
        return info
    
    async def close(self) -> None:
        """Close integrator resources."""
        await self._real_time_integrator.close()


class BulkIntegrator(ExternalModelIntegratorInterface):
    """
    Bulk integration pattern (Single Responsibility Principle).
    
    Handles batch processing for multiple requests to external models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize bulk integrator."""
        self._config = config
        self._real_time_integrator = RealTimeIntegrator(config)
        self._batch_queue = []
        self._batch_size = config.get("batch_size", 10)
        self._batch_timeout = config.get("batch_timeout", 5.0)
        
    async def call_model(self, model: ExternalModel, request_data: Dict[str, Any]) -> ModelResponse:
        """
        Call external model (individual requests are queued for batch processing).
        
        Args:
            model: External model configuration
            request_data: Request data to send to model
            
        Returns:
            ModelResponse with batch processing result
        """
        # For individual calls, fall back to real-time
        return await self._real_time_integrator.call_model(model, request_data)
    
    @monitor_performance("external_model_batch_call")
    async def call_model_batch(self, model: ExternalModel, requests: List[Dict[str, Any]]) -> List[ModelResponse]:
        """
        Call external model with batch of requests.
        
        Args:
            model: External model configuration
            requests: List of request data
            
        Returns:
            List of ModelResponse objects
        """
        try:
            responses = []
            
            # Process requests in batches
            for i in range(0, len(requests), self._batch_size):
                batch = requests[i:i + self._batch_size]
                batch_responses = await self._process_batch(model, batch)
                responses.extend(batch_responses)
            
            return responses
            
        except Exception as e:
            logger.error(f"Batch model call failed for {model.id}: {e}")
            return [
                ModelResponse(
                    model_id=model.id,
                    response_data={},
                    success=False,
                    error_message=str(e),
                    cached=False
                )
                for _ in requests
            ]
    
    async def _process_batch(self, model: ExternalModel, batch: List[Dict[str, Any]]) -> List[ModelResponse]:
        """Process a batch of requests."""
        try:
            # Create concurrent tasks for batch
            tasks = [
                self._real_time_integrator.call_model(model, request)
                for request in batch
            ]
            
            # Execute batch concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    processed_responses.append(
                        ModelResponse(
                            model_id=model.id,
                            response_data={},
                            success=False,
                            error_message=str(response),
                            cached=False
                        )
                    )
                else:
                    processed_responses.append(response)
            
            return processed_responses
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return [
                ModelResponse(
                    model_id=model.id,
                    response_data={},
                    success=False,
                    error_message=str(e),
                    cached=False
                )
                for _ in batch
            ]
    
    async def health_check(self, model: ExternalModel) -> bool:
        """Check health of external model."""
        return await self._real_time_integrator.health_check(model)
    
    async def get_model_info(self, model: ExternalModel) -> Dict[str, Any]:
        """Get model information."""
        info = await self._real_time_integrator.get_model_info(model)
        info["pattern"] = "bulk"
        info["batch_size"] = self._batch_size
        info["batch_timeout"] = self._batch_timeout
        return info
    
    async def close(self) -> None:
        """Close integrator resources."""
        await self._real_time_integrator.close()


class ExternalModelIntegrator:
    """
    Main external model integrator (Facade pattern).
    
    Provides unified interface to all integration patterns following
    Single Responsibility Principle for integration coordination.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize external model integrator."""
        self._config = config
        self._integrators = {
            IntegrationPattern.REAL_TIME: RealTimeIntegrator(config),
            IntegrationPattern.HYBRID: HybridIntegrator(config),
            IntegrationPattern.BULK: BulkIntegrator(config)
        }
        
        logger.info("ExternalModelIntegrator initialized")
    
    async def call_model(self, model: ExternalModel, request_data: Dict[str, Any]) -> ModelResponse:
        """
        Call external model using appropriate integration pattern.
        
        Args:
            model: External model configuration
            request_data: Request data to send to model
            
        Returns:
            ModelResponse with API response
        """
        try:
            integrator = self._integrators[model.integration_pattern]
            return await integrator.call_model(model, request_data)
            
        except Exception as e:
            logger.error(f"Model integration failed for {model.id}: {e}")
            return ModelResponse(
                model_id=model.id,
                response_data={},
                success=False,
                error_message=str(e),
                cached=False
            )
    
    async def call_model_batch(self, model: ExternalModel, requests: List[Dict[str, Any]]) -> List[ModelResponse]:
        """Call external model with batch of requests."""
        try:
            if model.integration_pattern == IntegrationPattern.BULK:
                bulk_integrator = self._integrators[IntegrationPattern.BULK]
                return await bulk_integrator.call_model_batch(model, requests)
            else:
                # Fall back to individual calls
                integrator = self._integrators[model.integration_pattern]
                tasks = [integrator.call_model(model, request) for request in requests]
                return await asyncio.gather(*tasks)
                
        except Exception as e:
            logger.error(f"Batch model integration failed for {model.id}: {e}")
            return [
                ModelResponse(
                    model_id=model.id,
                    response_data={},
                    success=False,
                    error_message=str(e),
                    cached=False
                )
                for _ in requests
            ]
    
    async def health_check(self, model: ExternalModel) -> bool:
        """Check health of external model."""
        try:
            integrator = self._integrators[model.integration_pattern]
            return await integrator.health_check(model)
        except:
            return False
    
    async def get_model_info(self, model: ExternalModel) -> Dict[str, Any]:
        """Get model information."""
        try:
            integrator = self._integrators[model.integration_pattern]
            return await integrator.get_model_info(model)
        except Exception as e:
            logger.error(f"Failed to get model info for {model.id}: {e}")
            return {"error": str(e)}
    
    async def close(self) -> None:
        """Close all integrator resources."""
        for integrator in self._integrators.values():
            await integrator.close()
