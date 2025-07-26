"""
Application Settings Configuration

Centralized configuration management for HX-Orchestration-Server.
Uses environment variables with sensible defaults for all settings.

Server: hx-orchestration-server (192.168.10.31)
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8080, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Identity
    SERVER_NAME: str = Field(default="hx-orchestration-server", env="SERVER_NAME")
    SERVER_IP: str = Field(default="192.168.10.31", env="SERVER_IP")
    
    # Security
    SECRET_KEY: str = Field(default="development-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://citadel:password@192.168.10.35:5432/orchestration",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # External Services
    LLM_01_URL: str = Field(default="http://192.168.10.34:8002", env="LLM_01_URL")
    LLM_02_URL: str = Field(default="http://192.168.10.28:8000", env="LLM_02_URL")
    QDRANT_URL: str = Field(default="http://192.168.10.30:6333", env="QDRANT_URL")
    OLLAMA_URL: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=8000, env="PROMETHEUS_PORT")
    GRAFANA_URL: str = Field(default="http://192.168.10.37:3000", env="GRAFANA_URL")
    PROMETHEUS_URL: str = Field(default="http://192.168.10.37:9090", env="PROMETHEUS_URL")
    
    # Embedding Configuration
    DEFAULT_EMBEDDING_MODEL: str = Field(default="nomic-embed-text", env="DEFAULT_EMBEDDING_MODEL")
    MAX_EMBEDDING_BATCH_SIZE: int = Field(default=100, env="MAX_EMBEDDING_BATCH_SIZE")
    EMBEDDING_CACHE_TTL: int = Field(default=3600, env="EMBEDDING_CACHE_TTL")
    
    # RAG Configuration
    DEFAULT_RAG_COLLECTION: str = Field(default="rag_documents", env="DEFAULT_RAG_COLLECTION")
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    MAX_CONTEXT_LENGTH: int = Field(default=8000, env="MAX_CONTEXT_LENGTH")
    
    # Performance
    HTTP_TIMEOUT: int = Field(default=30, env="HTTP_TIMEOUT")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    CONNECTION_POOL_SIZE: int = Field(default=100, env="CONNECTION_POOL_SIZE")
    MAX_CONCURRENT_REQUESTS: int = Field(default=1000, env="MAX_CONCURRENT_REQUESTS")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    CIRCUIT_BREAKER_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_THRESHOLD")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
