"""
External Model Registry Module

Registry for managing external AI models following HXP Governance Coding Standards.
Implements Single Responsibility Principle for model registration and management.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime

from hana_x_vector.models.external_models import (
    ExternalModel, ExternalModelType, IntegrationPattern, ModelCapability, ModelUsageStats
)
from hana_x_vector.external_models.integration_patterns import ExternalModelIntegrator
from hana_x_vector.utils.metrics import get_metrics_collector, monitor_performance
from hana_x_vector.utils.logging import get_logger

logger = get_logger(__name__)


class ModelRegistryInterface(ABC):
    """
    Abstract interface for model registry (Abstraction principle).
    
    Defines the contract for model registration and management without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def register_model(self, model: ExternalModel) -> bool:
        """Register external model."""
        pass
    
    @abstractmethod
    async def unregister_model(self, model_id: str) -> bool:
        """Unregister external model."""
        pass
    
    @abstractmethod
    async def get_model(self, model_id: str) -> Optional[ExternalModel]:
        """Get model by ID."""
        pass
    
    @abstractmethod
    async def list_models(self, model_type: Optional[ExternalModelType] = None) -> List[ExternalModel]:
        """List all registered models."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of model registry."""
        pass


class ExternalModelRegistry(ModelRegistryInterface):
    """
    External model registry implementation (Single Responsibility Principle).
    
    Manages registration, configuration, and lifecycle of external AI models
    with health monitoring and usage tracking capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize external model registry.
        
        Args:
            config: Configuration dictionary containing registry settings
        """
        self._config = config or {}
        self._models: Dict[str, ExternalModel] = {}
        self._usage_stats: Dict[str, ModelUsageStats] = {}
        self._integrator = ExternalModelIntegrator(self._config)
        self._health_check_interval = self._config.get("health_check_interval", 60)
        self._health_check_task = None
        self._running = False
        
        # Initialize models from configuration
        self._init_models_from_config()
        
        logger.info("ExternalModelRegistry initialized")
    
    def _init_models_from_config(self) -> None:
        """Initialize models from configuration."""
        models_config = self._config.get("external_models", {})
        
        for model_name, model_config in models_config.items():
            try:
                model = ExternalModel(
                    name=model_name,
                    model_type=ExternalModelType(model_config["model_type"]),
                    api_endpoint=model_config["api_endpoint"],
                    api_key_name=model_config.get("api_key_name"),
                    capabilities=[ModelCapability(cap) for cap in model_config.get("capabilities", [])],
                    integration_pattern=IntegrationPattern(model_config.get("integration_pattern", "real_time")),
                    max_tokens=model_config.get("max_tokens", 4096),
                    rate_limit_rpm=model_config.get("rate_limit_rpm", 60),
                    timeout_seconds=model_config.get("timeout_seconds", 30),
                    retry_attempts=model_config.get("retry_attempts", 3),
                    cache_ttl_seconds=model_config.get("cache_ttl_seconds", 3600),
                    config=model_config.get("config", {})
                )
                
                self._models[model.id] = model
                self._usage_stats[model.id] = ModelUsageStats(model_id=model.id)
                
                logger.info(f"Model registered from config: {model_name} ({model.id})")
                
            except Exception as e:
                logger.error(f"Failed to initialize model {model_name} from config: {e}")
        
        logger.info(f"Initialized {len(self._models)} models from configuration")
    
    async def initialize_all(self) -> None:
        """Initialize all registered models."""
        try:
            # Start health check task
            if not self._running:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                self._running = True
            
            # Perform initial health check for all models
            for model in self._models.values():
                await self._check_model_health(model)
            
            logger.info("All models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown model registry."""
        try:
            # Stop health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close integrator
            await self._integrator.close()
            
            self._running = False
            logger.info("Model registry shutdown completed")
            
        except Exception as e:
            logger.error(f"Failed to shutdown model registry: {e}")
            raise
    
    @monitor_performance("register_model")
    async def register_model(self, model: ExternalModel) -> bool:
        """
        Register external model.
        
        Args:
            model: External model to register
            
        Returns:
            True if model registered successfully
        """
        try:
            # Validate model configuration
            if not self._validate_model(model):
                return False
            
            # Perform health check
            is_healthy = await self._integrator.health_check(model)
            if not is_healthy:
                logger.warning(f"Model {model.id} failed health check during registration")
            
            # Register model
            self._models[model.id] = model
            self._usage_stats[model.id] = ModelUsageStats(model_id=model.id)
            
            logger.info(f"Model registered: {model.name} ({model.id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model.id}: {e}")
            return False
    
    def _validate_model(self, model: ExternalModel) -> bool:
        """Validate model configuration."""
        try:
            # Check required fields
            if not model.name or not model.api_endpoint:
                logger.error(f"Model {model.id} missing required fields")
                return False
            
            # Check capabilities
            if not model.capabilities:
                logger.error(f"Model {model.id} has no capabilities defined")
                return False
            
            # Check API endpoint format
            if not model.api_endpoint.startswith(('http://', 'https://')):
                logger.error(f"Model {model.id} has invalid API endpoint format")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed for {model.id}: {e}")
            return False
    
    async def unregister_model(self, model_id: str) -> bool:
        """
        Unregister external model.
        
        Args:
            model_id: Model ID to unregister
            
        Returns:
            True if model unregistered successfully
        """
        try:
            if model_id in self._models:
                model = self._models.pop(model_id)
                self._usage_stats.pop(model_id, None)
                
                logger.info(f"Model unregistered: {model.name} ({model_id})")
                return True
            else:
                logger.warning(f"Model not found for unregistration: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to unregister model {model_id}: {e}")
            return False
    
    async def get_model(self, model_id: str) -> Optional[ExternalModel]:
        """
        Get model by ID.
        
        Args:
            model_id: Model ID to retrieve
            
        Returns:
            ExternalModel if found, None otherwise
        """
        return self._models.get(model_id)
    
    async def list_models(self, model_type: Optional[ExternalModelType] = None) -> List[ExternalModel]:
        """
        List all registered models.
        
        Args:
            model_type: Optional filter by model type
            
        Returns:
            List of registered models
        """
        models = list(self._models.values())
        
        if model_type:
            models = [model for model in models if model.model_type == model_type]
        
        return models
    
    async def list_active_models(self) -> List[ExternalModel]:
        """List only active models."""
        return [model for model in self._models.values() if model.is_active]
    
    async def get_models_by_capability(self, capability: ModelCapability) -> List[ExternalModel]:
        """Get models that support a specific capability."""
        return [
            model for model in self._models.values()
            if capability in model.capabilities and model.is_active
        ]
    
    async def call_model(self, model_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call external model through integrator.
        
        Args:
            model_id: Model ID to call
            request_data: Request data to send
            
        Returns:
            Model response data
        """
        try:
            model = await self.get_model(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")
            
            if not model.is_active:
                raise ValueError(f"Model not active: {model_id}")
            
            # Call model through integrator
            response = await self._integrator.call_model(model, request_data)
            
            # Update usage statistics
            await self._update_usage_stats(model_id, response.success, response.processing_time_ms, response.tokens_used)
            
            return response.dict()
            
        except Exception as e:
            logger.error(f"Model call failed for {model_id}: {e}")
            # Update failure statistics
            await self._update_usage_stats(model_id, False, 0, 0)
            raise
    
    async def _update_usage_stats(self, model_id: str, success: bool, processing_time_ms: float, tokens_used: Optional[int]) -> None:
        """Update usage statistics for model."""
        try:
            if model_id not in self._usage_stats:
                self._usage_stats[model_id] = ModelUsageStats(model_id=model_id)
            
            stats = self._usage_stats[model_id]
            stats.total_requests += 1
            
            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1
            
            if tokens_used:
                stats.total_tokens += tokens_used
            
            # Update average response time (exponential moving average)
            alpha = 0.1
            stats.average_response_time_ms = (
                alpha * processing_time_ms + (1 - alpha) * stats.average_response_time_ms
            )
            
            stats.last_used = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update usage stats for {model_id}: {e}")
    
    async def get_usage_stats(self, model_id: str) -> Optional[ModelUsageStats]:
        """Get usage statistics for model."""
        return self._usage_stats.get(model_id)
    
    async def get_all_usage_stats(self) -> Dict[str, ModelUsageStats]:
        """Get usage statistics for all models."""
        return self._usage_stats.copy()
    
    async def _health_check_loop(self) -> None:
        """Health check loop for all models."""
        while self._running:
            try:
                # Check health of all models
                for model in self._models.values():
                    await self._check_model_health(model)
                
                # Wait for next health check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _check_model_health(self, model: ExternalModel) -> None:
        """Check health of a single model."""
        try:
            is_healthy = await self._integrator.health_check(model)
            
            # Update model status based on health check
            # This would typically update a health status field
            
            # Record health check metrics
            metrics = get_metrics_collector()
            status = "healthy" if is_healthy else "unhealthy"
            metrics.record_external_model_call(
                model.id, "health_check", status, 0
            )
            
        except Exception as e:
            logger.error(f"Health check failed for model {model.id}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of model registry.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            total_models = len(self._models)
            active_models = len([m for m in self._models.values() if m.is_active])
            
            # Get model type distribution
            type_distribution = {}
            for model in self._models.values():
                model_type = model.model_type.value
                type_distribution[model_type] = type_distribution.get(model_type, 0) + 1
            
            # Get integration pattern distribution
            pattern_distribution = {}
            for model in self._models.values():
                pattern = model.integration_pattern.value
                pattern_distribution[pattern] = pattern_distribution.get(pattern, 0) + 1
            
            return {
                "status": "healthy" if self._running else "stopped",
                "message": "Model registry operational" if self._running else "Model registry stopped",
                "running": self._running,
                "models": {
                    "total": total_models,
                    "active": active_models,
                    "inactive": total_models - active_models
                },
                "distributions": {
                    "by_type": type_distribution,
                    "by_pattern": pattern_distribution
                },
                "health_check_interval": self._health_check_interval,
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
