"""
Embedding Service Module

Core embedding generation service following HXP Governance Coding Standards.
Implements Single Responsibility Principle for embedding operations.

Author: Citadel AI Team
License: MIT
"""

from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from hana_x_vector.models.vector_models import EmbeddingRequest, EmbeddingResponse
from hana_x_vector.utils.metrics import monitor_performance

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Model information (Data encapsulation)."""
    name: str
    dimension: int
    max_length: int
    is_loaded: bool = False
    load_time: Optional[datetime] = None


class EmbeddingServiceInterface(ABC):
    """
    Abstract interface for embedding service (Abstraction principle).
    
    Defines the contract for embedding generation without exposing
    implementation details, following Interface Segregation Principle.
    """
    
    @abstractmethod
    async def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for text input."""
        pass
    
    @abstractmethod
    async def load_model(self, model_name: str) -> bool:
        """Load embedding model."""
        pass
    
    @abstractmethod
    async def unload_model(self, model_name: str) -> bool:
        """Unload embedding model."""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of embedding service."""
        pass


class EmbeddingService(EmbeddingServiceInterface):
    """
    Embedding service implementation (Single Responsibility Principle).
    
    Handles embedding generation with proper error handling, caching,
    and performance monitoring. Follows Open/Closed Principle by
    allowing extension through composition.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize embedding service.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self._config = config
        self._models: Dict[str, Any] = {}
        self._model_info: Dict[str, ModelInfo] = {}
        self._initialized = False
        
        # Configuration validation
        self._validate_config()
        
        logger.info("EmbeddingService initialized with configuration")
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_keys = ["models"]
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    async def initialize(self) -> None:
        """Initialize embedding service and load models."""
        try:
            # Initialize model configurations
            for model_name, model_config in self._config["models"].items():
                self._model_info[model_name] = ModelInfo(
                    name=model_name,
                    dimension=model_config.get("dimension", 384),
                    max_length=model_config.get("max_length", 512)
                )
            
            # Load default models if specified
            default_models = self._config.get("default_models", [])
            for model_name in default_models:
                await self.load_model(model_name)
            
            self._initialized = True
            logger.info("EmbeddingService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure embedding service is initialized."""
        if not self._initialized:
            raise RuntimeError("EmbeddingService not initialized. Call initialize() first.")
    
    @monitor_performance("generate_embeddings")
    async def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate embeddings for text input.
        
        Args:
            request: Embedding generation request
            
        Returns:
            EmbeddingResponse with generated embeddings
        """
        self._ensure_initialized()
        
        start_time = datetime.now()
        
        try:
            # Ensure model is loaded
            if not await self._ensure_model_loaded(request.model_name):
                raise ValueError(f"Model {request.model_name} not available")
            
            # Prepare text input
            texts = request.text if isinstance(request.text, list) else [request.text]
            
            # Generate embeddings
            embeddings = await self._generate_embeddings_batch(
                texts, request.model_name, request
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Get model info
            model_info = self._model_info[request.model_name]
            
            logger.info(f"Generated {len(embeddings)} embeddings using {request.model_name}")
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model_name=request.model_name,
                dimension=model_info.dimension,
                processing_time_ms=processing_time,
                token_count=self._estimate_token_count(texts),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def _ensure_model_loaded(self, model_name: str) -> bool:
        """Ensure model is loaded."""
        if model_name not in self._model_info:
            return False
        
        if not self._model_info[model_name].is_loaded:
            return await self.load_model(model_name)
        
        return True
    
    async def _generate_embeddings_batch(self, texts: List[str], model_name: str, 
                                       request: EmbeddingRequest) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        try:
            # Get model
            model = self._models[model_name]
            
            # Process in batches
            batch_size = request.batch_size
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                batch_embeddings = await self._process_batch(
                    batch_texts, model, request
                )
                embeddings.extend(batch_embeddings)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings batch: {e}")
            raise
    
    async def _process_batch(self, texts: List[str], model: Any, 
                           request: EmbeddingRequest) -> List[List[float]]:
        """Process a single batch of texts."""
        try:
            # This is a placeholder for actual model inference
            # In real implementation, this would call the actual model
            
            # Simulate embedding generation
            model_info = self._model_info[request.model_name]
            embeddings = []
            
            for text in texts:
                # Simulate embedding generation
                embedding = np.random.normal(0, 1, model_info.dimension).tolist()
                
                # Normalize if requested
                if request.normalize:
                    embedding = self._normalize_embedding(embedding)
                
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            raise
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """Normalize embedding vector."""
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        
        if norm == 0:
            return embedding
        
        return (embedding_array / norm).tolist()
    
    def _estimate_token_count(self, texts: List[str]) -> int:
        """Estimate token count for texts."""
        # Simple estimation: ~4 characters per token
        total_chars = sum(len(text) for text in texts)
        return total_chars // 4
    
    @monitor_performance("load_model")
    async def load_model(self, model_name: str) -> bool:
        """
        Load embedding model.
        
        Args:
            model_name: Name of model to load
            
        Returns:
            True if model loaded successfully
        """
        self._ensure_initialized()
        
        try:
            if model_name not in self._model_info:
                logger.error(f"Model {model_name} not configured")
                return False
            
            if self._model_info[model_name].is_loaded:
                logger.info(f"Model {model_name} already loaded")
                return True
            
            # Load model configuration
            model_config = self._config["models"][model_name]
            
            # Simulate model loading
            # In real implementation, this would load the actual model
            logger.info(f"Loading model {model_name}...")
            
            # Simulate loading time
            await asyncio.sleep(0.1)
            
            # Store model (placeholder)
            self._models[model_name] = {
                "name": model_name,
                "config": model_config,
                "loaded": True
            }
            
            # Update model info
            self._model_info[model_name].is_loaded = True
            self._model_info[model_name].load_time = datetime.now()
            
            logger.info(f"Model {model_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    @monitor_performance("unload_model")
    async def unload_model(self, model_name: str) -> bool:
        """
        Unload embedding model.
        
        Args:
            model_name: Name of model to unload
            
        Returns:
            True if model unloaded successfully
        """
        self._ensure_initialized()
        
        try:
            if model_name not in self._model_info:
                logger.error(f"Model {model_name} not configured")
                return False
            
            if not self._model_info[model_name].is_loaded:
                logger.info(f"Model {model_name} not loaded")
                return True
            
            # Unload model
            if model_name in self._models:
                del self._models[model_name]
            
            # Update model info
            self._model_info[model_name].is_loaded = False
            self._model_info[model_name].load_time = None
            
            logger.info(f"Model {model_name} unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of available model names
        """
        self._ensure_initialized()
        return list(self._model_info.keys())
    
    async def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models."""
        self._ensure_initialized()
        return [
            name for name, info in self._model_info.items() 
            if info.is_loaded
        ]
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self._ensure_initialized()
        
        if model_name not in self._model_info:
            return None
        
        info = self._model_info[model_name]
        return {
            "name": info.name,
            "dimension": info.dimension,
            "max_length": info.max_length,
            "is_loaded": info.is_loaded,
            "load_time": info.load_time.isoformat() if info.load_time else None
        }
    
    def is_connected(self) -> bool:
        """Check if service is connected and operational."""
        return self._initialized
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of embedding service.
        
        Returns:
            Dictionary containing health status and metrics
        """
        try:
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "message": "Not initialized",
                    "initialized": False
                }
            
            loaded_models = await self.get_loaded_models()
            available_models = await self.get_available_models()
            
            return {
                "status": "healthy",
                "message": "Embedding service operational",
                "initialized": True,
                "available_models": len(available_models),
                "loaded_models": len(loaded_models),
                "models": {
                    "available": available_models,
                    "loaded": loaded_models
                },
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {e}",
                "initialized": self._initialized,
                "error": str(e)
            }
