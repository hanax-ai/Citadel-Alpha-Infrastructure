"""
Configuration Management Module

Configuration loading and validation following HXP Governance Coding Standards.
Implements Single Responsibility Principle for configuration management.

Author: Citadel AI Team
License: MIT
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import os
import yaml
import json
import logging
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration (Data encapsulation)."""
    host: str = "localhost"
    port: int = 6333
    timeout: int = 30
    collection_prefix: str = "hxp"
    batch_size: int = 100


@dataclass
class APIGatewayConfig:
    """API Gateway configuration (Data encapsulation)."""
    host: str = "0.0.0.0"
    rest_port: int = 8000
    graphql_port: int = 8001
    grpc_port: int = 8002
    cors_enabled: bool = True
    cors_origins: list = None
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60


@dataclass
class CacheConfig:
    """Cache configuration (Data encapsulation)."""
    enabled: bool = True
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 3600
    max_connections: int = 10
    compression_enabled: bool = True


@dataclass
class MetricsConfig:
    """Metrics configuration (Data encapsulation)."""
    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"
    collect_detailed: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration (Data encapsulation)."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


class VectorDatabaseConfig(BaseModel):
    """
    Main configuration class with validation.
    
    Implements configuration validation and type safety following
    HXP Governance Coding Standards.
    """
    
    # Database configuration
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database connection settings"
    )
    
    # API Gateway configuration
    api_gateway: APIGatewayConfig = Field(
        default_factory=APIGatewayConfig,
        description="API Gateway settings"
    )
    
    # Cache configuration
    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Cache settings"
    )
    
    # Metrics configuration
    metrics: MetricsConfig = Field(
        default_factory=MetricsConfig,
        description="Metrics collection settings"
    )
    
    # Logging configuration
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration"
    )
    
    # External models configuration
    external_models: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="External model configurations"
    )
    
    # Environment
    environment: str = Field(
        default="development",
        description="Environment name",
        regex="^(development|staging|production)$"
    )
    
    # Debug mode
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    @validator('database')
    def validate_database_config(cls, v):
        """Validate database configuration."""
        if not isinstance(v, DatabaseConfig):
            if isinstance(v, dict):
                v = DatabaseConfig(**v)
            else:
                raise ValueError("Invalid database configuration")
        
        if v.port < 1 or v.port > 65535:
            raise ValueError("Database port must be between 1 and 65535")
        
        if v.timeout < 1:
            raise ValueError("Database timeout must be positive")
        
        return v
    
    @validator('api_gateway')
    def validate_api_gateway_config(cls, v):
        """Validate API Gateway configuration."""
        if not isinstance(v, APIGatewayConfig):
            if isinstance(v, dict):
                v = APIGatewayConfig(**v)
            else:
                raise ValueError("Invalid API Gateway configuration")
        
        # Validate ports
        ports = [v.rest_port, v.graphql_port, v.grpc_port]
        if len(set(ports)) != len(ports):
            raise ValueError("API Gateway ports must be unique")
        
        for port in ports:
            if port < 1 or port > 65535:
                raise ValueError("API Gateway ports must be between 1 and 65535")
        
        return v
    
    @validator('cache')
    def validate_cache_config(cls, v):
        """Validate cache configuration."""
        if not isinstance(v, CacheConfig):
            if isinstance(v, dict):
                v = CacheConfig(**v)
            else:
                raise ValueError("Invalid cache configuration")
        
        if v.default_ttl < 0:
            raise ValueError("Cache TTL must be non-negative")
        
        if v.max_connections < 1:
            raise ValueError("Cache max connections must be positive")
        
        return v
    
    @validator('external_models')
    def validate_external_models(cls, v):
        """Validate external models configuration."""
        if not isinstance(v, dict):
            raise ValueError("External models configuration must be a dictionary")
        
        # Validate each model configuration
        for model_name, model_config in v.items():
            if not isinstance(model_config, dict):
                raise ValueError(f"Model {model_name} configuration must be a dictionary")
            
            required_fields = ['api_endpoint', 'model_type']
            for field in required_fields:
                if field not in model_config:
                    raise ValueError(f"Model {model_name} missing required field: {field}")
        
        return v
    
    def get_database_url(self) -> str:
        """Get database connection URL."""
        return f"http://{self.database.host}:{self.database.port}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        return self.cache.redis_url
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug or self.environment == "development"
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            DatabaseConfig: lambda v: v.__dict__,
            APIGatewayConfig: lambda v: v.__dict__,
            CacheConfig: lambda v: v.__dict__,
            MetricsConfig: lambda v: v.__dict__,
            LoggingConfig: lambda v: v.__dict__,
        }


def load_config(config_path: Union[str, Path]) -> VectorDatabaseConfig:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file (YAML or JSON)
        
    Returns:
        VectorDatabaseConfig instance
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        ValueError: If configuration is invalid
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        # Load environment variables
        config_data = _load_environment_variables(config_data)
        
        # Create and validate configuration
        config = VectorDatabaseConfig(**config_data)
        
        logger.info(f"Configuration loaded successfully from {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        raise ValueError(f"Invalid configuration: {e}")


def _load_environment_variables(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load environment variables into configuration.
    
    Args:
        config_data: Configuration dictionary
        
    Returns:
        Updated configuration with environment variables
    """
    # Database environment variables
    if 'database' not in config_data:
        config_data['database'] = {}
    
    db_config = config_data['database']
    db_config['host'] = os.getenv('HXP_DB_HOST', db_config.get('host', 'localhost'))
    db_config['port'] = int(os.getenv('HXP_DB_PORT', db_config.get('port', 6333)))
    
    # API Gateway environment variables
    if 'api_gateway' not in config_data:
        config_data['api_gateway'] = {}
    
    api_config = config_data['api_gateway']
    api_config['host'] = os.getenv('HXP_API_HOST', api_config.get('host', '0.0.0.0'))
    api_config['rest_port'] = int(os.getenv('HXP_REST_PORT', api_config.get('rest_port', 8000)))
    api_config['graphql_port'] = int(os.getenv('HXP_GRAPHQL_PORT', api_config.get('graphql_port', 8001)))
    api_config['grpc_port'] = int(os.getenv('HXP_GRPC_PORT', api_config.get('grpc_port', 8002)))
    
    # Cache environment variables
    if 'cache' not in config_data:
        config_data['cache'] = {}
    
    cache_config = config_data['cache']
    cache_config['redis_url'] = os.getenv('HXP_REDIS_URL', cache_config.get('redis_url', 'redis://localhost:6379'))
    cache_config['enabled'] = os.getenv('HXP_CACHE_ENABLED', str(cache_config.get('enabled', True))).lower() == 'true'
    
    # Environment and debug
    config_data['environment'] = os.getenv('HXP_ENVIRONMENT', config_data.get('environment', 'development'))
    config_data['debug'] = os.getenv('HXP_DEBUG', str(config_data.get('debug', False))).lower() == 'true'
    
    return config_data


def create_default_config() -> VectorDatabaseConfig:
    """
    Create default configuration.
    
    Returns:
        VectorDatabaseConfig with default values
    """
    return VectorDatabaseConfig()


def save_config(config: VectorDatabaseConfig, config_path: Union[str, Path]) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration to save
        config_path: Path to save configuration file
    """
    config_path = Path(config_path)
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        config_data = config.dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif config_path.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        logger.info(f"Configuration saved to {config_path}")
        
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_path}: {e}")
        raise


def validate_config(config_data: Dict[str, Any]) -> bool:
    """
    Validate configuration data.
    
    Args:
        config_data: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        VectorDatabaseConfig(**config_data)
        return True
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


# Configuration singleton for global access
_global_config: Optional[VectorDatabaseConfig] = None


def get_config() -> VectorDatabaseConfig:
    """
    Get global configuration instance.
    
    Returns:
        Global VectorDatabaseConfig instance
    """
    global _global_config
    
    if _global_config is None:
        _global_config = create_default_config()
    
    return _global_config


def set_config(config: VectorDatabaseConfig) -> None:
    """
    Set global configuration instance.
    
    Args:
        config: Configuration to set as global
    """
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset global configuration to default."""
    global _global_config
    _global_config = None
