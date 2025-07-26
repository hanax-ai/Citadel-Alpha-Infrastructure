"""
Citadel LLM Settings Configuration
Centralized settings management using Pydantic for validation
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    host: str = Field("192.168.10.35", env="DATABASE_HOST")
    port: int = Field(5432, env="DATABASE_PORT") 
    database: str = Field("citadel_llm_db", env="DATABASE_NAME")
    username: str = Field("citadel_llm_user", env="DATABASE_USER")
    password: str = Field("CitadelLLM#2025$SecurePass!", env="DATABASE_PASSWORD")
    
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, env="DATABASE_POOL_RECYCLE")
    
    @property
    def url(self) -> str:
        """Get database connection URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_prefix = "DATABASE_"

class OllamaSettings(BaseSettings):
    """Ollama service configuration"""
    host: str = Field("localhost", env="OLLAMA_HOST")
    port: int = Field(11434, env="OLLAMA_PORT")
    api_url: str = Field("http://localhost:11434", env="OLLAMA_API_URL")
    
    timeout: int = Field(300, env="OLLAMA_TIMEOUT")
    max_retries: int = Field(3, env="OLLAMA_MAX_RETRIES")
    retry_delay: float = Field(1.0, env="OLLAMA_RETRY_DELAY")
    
    models_path: str = Field("/mnt/active_llm_models/.ollama", env="OLLAMA_MODELS_PATH")
    max_parallel: int = Field(2, env="OLLAMA_MAX_PARALLEL")
    max_loaded_models: int = Field(4, env="OLLAMA_MAX_LOADED_MODELS")
    
    class Config:
        env_prefix = "OLLAMA_"

class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration"""
    prometheus_url: str = Field("http://192.168.10.37:9090", env="PROMETHEUS_URL")
    grafana_url: str = Field("http://192.168.10.37:3000", env="GRAFANA_URL") 
    alertmanager_url: str = Field("http://192.168.10.37:9093", env="ALERTMANAGER_URL")
    node_exporter_url: str = Field("http://192.168.10.37:9100", env="NODE_EXPORTER_URL")
    
    metrics_enabled: bool = Field(True, env="METRICS_ENABLED")
    metrics_endpoint: str = Field("/metrics", env="METRICS_ENDPOINT")
    metrics_interval: int = Field(30, env="METRICS_INTERVAL")
    
    class Config:
        env_prefix = "MONITORING_"

class APIGatewaySettings(BaseSettings):
    """API Gateway configuration"""
    host: str = Field("0.0.0.0", env="GATEWAY_HOST")
    port: int = Field(8000, env="GATEWAY_PORT")
    
    workers: int = Field(4, env="GATEWAY_WORKERS")
    reload: bool = Field(False, env="GATEWAY_RELOAD")
    log_level: str = Field("info", env="GATEWAY_LOG_LEVEL")
    
    cors_enabled: bool = Field(True, env="GATEWAY_CORS_ENABLED")
    cors_origins: List[str] = Field(["*"], env="GATEWAY_CORS_ORIGINS")
    
    rate_limit_enabled: bool = Field(True, env="GATEWAY_RATE_LIMIT_ENABLED") 
    rate_limit_requests: int = Field(100, env="GATEWAY_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="GATEWAY_RATE_LIMIT_WINDOW")
    
    class Config:
        env_prefix = "GATEWAY_"

class LoggingSettings(BaseSettings):
    """Logging configuration"""
    level: str = Field("INFO", env="LOG_LEVEL")
    format: str = Field("json", env="LOG_FORMAT")
    
    file_enabled: bool = Field(True, env="LOG_FILE_ENABLED")
    file_path: str = Field("/opt/citadel-02/logs/citadel.log", env="LOG_FILE_PATH")
    file_max_size: str = Field("100MB", env="LOG_FILE_MAX_SIZE")
    file_backup_count: int = Field(5, env="LOG_FILE_BACKUP_COUNT")
    
    console_enabled: bool = Field(True, env="LOG_CONSOLE_ENABLED")
    include_body: bool = Field(False, env="LOG_INCLUDE_BODY")
    
    class Config:
        env_prefix = "LOG_"

class ModelSettings(BaseSettings):
    """AI Model configuration and routing"""
    default_model: str = Field("qwen:1.8b", env="DEFAULT_MODEL")
    
    # Model routing configuration
    lightweight_model: str = Field("qwen:1.8b", env="LIGHTWEIGHT_MODEL")
    code_model: str = Field("deepcoder:14b", env="CODE_MODEL")  
    research_model: str = Field("deepseek-r1:32b", env="RESEARCH_MODEL")
    business_model: str = Field("hadad/JARVIS:latest", env="BUSINESS_MODEL")
    reasoning_model: str = Field("yi:34b-chat", env="REASONING_MODEL")
    
    # Model-specific timeouts
    lightweight_timeout: int = Field(30, env="LIGHTWEIGHT_TIMEOUT")
    standard_timeout: int = Field(120, env="STANDARD_TIMEOUT") 
    complex_timeout: int = Field(300, env="COMPLEX_TIMEOUT")
    
    class Config:
        env_prefix = "MODEL_"

class CitadelSettings(BaseSettings):
    """Main Citadel configuration combining all settings"""
    
    # Environment configuration
    environment: Environment = Field(Environment.PRODUCTION, env="CITADEL_ENV")
    debug: bool = Field(False, env="CITADEL_DEBUG")
    testing: bool = Field(False, env="CITADEL_TESTING")
    
    # Project paths
    home_dir: Path = Field(Path("/opt/citadel-02"), env="CITADEL_HOME")
    config_dir: Path = Field(Path("/opt/citadel-02/config"), env="CITADEL_CONFIG_DIR")
    logs_dir: Path = Field(Path("/opt/citadel-02/logs"), env="CITADEL_LOGS_DIR")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    gateway: APIGatewaySettings = Field(default_factory=APIGatewaySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    
    # Security settings
    secret_key: str = Field("citadel-secret-key-change-in-production", env="CITADEL_SECRET_KEY")
    allowed_hosts: List[str] = Field(["*"], env="CITADEL_ALLOWED_HOSTS")
    
    @field_validator("home_dir", "config_dir", "logs_dir")
    @classmethod
    def validate_paths(cls, v):
        """Ensure paths exist"""
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    class Config:
        env_file = "/opt/citadel-02/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

# Global settings instance
settings = CitadelSettings()

# Convenience functions for easy access
def get_database_url() -> str:
    """Get database connection URL"""
    return settings.database.url

def get_ollama_url() -> str:
    """Get Ollama API URL"""
    return settings.ollama.api_url

def get_model_for_task(task_type: str) -> str:
    """Get appropriate model for task type"""
    model_mapping = {
        "lightweight": settings.models.lightweight_model,
        "code": settings.models.code_model,
        "research": settings.models.research_model,
        "business": settings.models.business_model,
        "reasoning": settings.models.reasoning_model,
    }
    return model_mapping.get(task_type, settings.models.default_model)

def get_timeout_for_model(model_name: str) -> int:
    """Get timeout for specific model"""
    if model_name == settings.models.lightweight_model:
        return settings.models.lightweight_timeout
    elif model_name in [settings.models.research_model, settings.models.reasoning_model]:
        return settings.models.complex_timeout
    else:
        return settings.models.standard_timeout

if __name__ == "__main__":
    # CLI interface for settings validation
    import sys
    import json
    
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        try:
            print("✅ Settings validation passed")
            print(f"Environment: {settings.environment}")
            print(f"Database URL: {settings.database.url[:50]}...")
            print(f"Ollama URL: {settings.ollama.api_url}")
            print(f"Default Model: {settings.models.default_model}")
            print(f"Debug Mode: {settings.debug}")
        except Exception as e:
            print(f"❌ Settings validation failed: {e}")
            sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "show":
        # Show configuration (excluding sensitive data)
        config_dict = settings.dict()
        config_dict["database"]["password"] = "***HIDDEN***"
        config_dict["secret_key"] = "***HIDDEN***"
        print(json.dumps(config_dict, indent=2, default=str))
    
    else:
        print("Usage: python settings.py [validate|show]")
