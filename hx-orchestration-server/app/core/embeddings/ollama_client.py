"""
Ollama Client for Embedding Model Integration
Provides comprehensive interface to Ollama embedding models with performance optimization
"""

import asyncio
import aiohttp
import logging
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json

from app.common.base_classes import BaseEmbeddingService
from app.utils.performance_monitor import PerformanceMonitor

@dataclass
class EmbeddingResult:
    """Result container for embedding operations"""
    embeddings: List[List[float]]
    model: str
    input_tokens: int
    processing_time: float
    cache_hit: bool = False

class OllamaClient(BaseEmbeddingService):
    """
    High-performance Ollama client for embedding generation
    Supports all five embedding models with intelligent routing
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ollama_client", config, "multi-model")
        
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.timeout = config.get("timeout", 30.0)
        self.max_retries = config.get("max_retries", 3)
        self.batch_size = config.get("batch_size", 10)
        
        # Available embedding models with their characteristics
        self.models = {
            "nomic-embed-text": {
                "max_tokens": 8192,
                "dimensions": 768,
                "speed": "fast",
                "quality": "high"
            },
            "mxbai-embed-large": {
                "max_tokens": 512,
                "dimensions": 1024,
                "speed": "medium",
                "quality": "highest"
            },
            "bge-m3": {
                "max_tokens": 8192,
                "dimensions": 1024,
                "speed": "medium",
                "quality": "high",
                "multilingual": True
            },
            "all-minilm": {
                "max_tokens": 512,
                "dimensions": 384,
                "speed": "fastest",
                "quality": "good"
            },
            "bge-large": {
                "max_tokens": 512,
                "dimensions": 1024,
                "speed": "medium",
                "quality": "high"
            }
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.performance_monitor = PerformanceMonitor()
        
    async def initialize(self) -> bool:
        """Initialize the Ollama client and verify model availability"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
            )
            
            # Verify Ollama is running and models are available
            available_models = await self._get_available_models()
            
            for model_name in self.models.keys():
                if model_name not in available_models:
                    self.logger.warning(f"Model {model_name} not found in Ollama")
                    
            self._health_status = "healthy"
            self.logger.info("Ollama client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def _get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model["name"].replace(":latest", "") for model in data.get("models", [])]
                return []
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return []
    
    def select_optimal_model(self, 
                           text_length: int, 
                           quality_priority: str = "balanced",
                           language: str = "en") -> str:
        """
        Intelligently select the optimal model based on requirements
        
        Args:
            text_length: Length of text to embed
            quality_priority: "speed", "quality", or "balanced"
            language: Language code for multilingual support
        """
        
        # For non-English text, prefer multilingual models
        if language != "en" and "bge-m3" in self.models:
            return "bge-m3"
        
        # For very long texts, prefer models with larger context windows
        if text_length > 4000:
            return "nomic-embed-text"
        
        # Selection based on priority
        if quality_priority == "speed":
            return "all-minilm"
        elif quality_priority == "quality":
            return "mxbai-embed-large"
        else:  # balanced
            if text_length < 200:
                return "all-minilm"
            elif text_length < 1000:
                return "bge-large"
            else:
                return "nomic-embed-text"
    
    async def generate_embeddings(self,
                                texts: Union[str, List[str]],
                                model: Optional[str] = None,
                                quality_priority: str = "balanced",
                                language: str = "en") -> EmbeddingResult:
        """
        Generate embeddings for text(s) using specified or optimal model
        
        Args:
            texts: Single text or list of texts to embed
            model: Specific model to use (auto-select if None)
            quality_priority: Priority for model selection
            language: Language for multilingual optimization
        """
        
        if isinstance(texts, str):
            texts = [texts]
        
        if not model:
            avg_length = sum(len(text) for text in texts) // len(texts)
            model = self.select_optimal_model(avg_length, quality_priority, language)
        
        start_time = time.time()
        
        try:
            # Process in batches if needed
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                batch_embeddings = await self._process_batch(batch, model)
                all_embeddings.extend(batch_embeddings)
            
            processing_time = time.time() - start_time
            
            # Update metrics
            self.embedding_count += len(texts)
            await self.performance_monitor.record_embedding_generation(
                model, len(texts), processing_time
            )
            
            return EmbeddingResult(
                embeddings=all_embeddings,
                model=model,
                input_tokens=sum(len(text.split()) for text in texts),
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def _process_batch(self, texts: List[str], model: str) -> List[List[float]]:
        """Process a batch of texts through Ollama"""
        embeddings = []
        
        for text in texts:
            embedding = await self._generate_single_embedding(text, model)
            embeddings.append(embedding)
        
        return embeddings
    
    async def _generate_single_embedding(self, text: str, model: str) -> List[float]:
        """Generate embedding for a single text"""
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data["embedding"]
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Ollama API error {response.status}: {error_text}")
                        
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        raise Exception(f"Failed to generate embedding after {self.max_retries} attempts")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for Ollama client"""
        try:
            # Test basic connectivity
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                ollama_healthy = response.status == 200
            
            # Test embedding generation
            test_embedding = await self._generate_single_embedding("test", "all-minilm")
            embedding_healthy = len(test_embedding) > 0
            
            available_models = await self._get_available_models()
            
            metrics = await self.get_embedding_metrics()
            
            return {
                "status": "healthy" if ollama_healthy and embedding_healthy else "unhealthy",
                "ollama_connection": ollama_healthy,
                "embedding_generation": embedding_healthy,
                "available_models": available_models,
                "configured_models": list(self.models.keys()),
                "performance_metrics": metrics,
                "uptime_seconds": (time.time() - self._start_time.timestamp())
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "uptime_seconds": (time.time() - self._start_time.timestamp())
            }
    
    async def list_models(self) -> List[str]:
        """List available embedding models"""
        try:
            available_models = await self._get_available_models()
            # Return intersection of configured models and available models
            return [model for model in self.models.keys() if model in available_models]
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            # Return configured models as fallback
            return list(self.models.keys())
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        
        info = self.models[model].copy()
        
        # Add runtime metrics if available
        try:
            metrics = await self.performance_monitor.get_model_metrics(model)
            info.update(metrics)
        except Exception:
            pass
            
        return info
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the Ollama client"""
        if self.session:
            await self.session.close()
        await super().shutdown()
        self.logger.info("Ollama client shut down gracefully")
