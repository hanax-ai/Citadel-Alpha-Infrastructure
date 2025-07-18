"""
Configuration Manager
====================

Centralized configuration management for the HANA-X Vector Database Shared Library.
Handles environment-based configuration with validation and defaults.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from .exceptions import ValidationError


@dataclass
class QdrantConfig:
    """Qdrant configuration."""
    host: str = "192.168.10.30"
    port: int = 6333
    grpc_port: int = 6334
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    collection_timeout: float = 60.0
    batch_size: int = 1000
    max_connections: int = 100


@dataclass
class CacheConfig:
    """Cache configuration."""
    host: str = "192.168.10.35"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    timeout: float = 5.0
    max_connections: int = 50
    ttl_default: int = 3600  # 1 hour
    ttl_search: int = 300    # 5 minutes
    ttl_metadata: int = 1800 # 30 minutes
    ttl_collections: int = 7200  # 2 hours


@dataclass
class ExternalModelConfig:
    """External model configuration."""
    server_1: str = "192.168.10.32"
    server_2: str = "192.168.10.33"
    port: int = 11400
    timeout: float = 30.0
    retry_attempts: int = 2
    retry_delay: float = 2.0
    max_connections: int = 20
    connection_timeout: float = 10.0
    read_timeout: float = 60.0
    models: Dict[str, str] = field(default_factory=lambda: {
        "mixtral": "192.168.10.32",
        "hermes": "192.168.10.32",
        "phi": "192.168.10.33",
        "claude": "192.168.10.33",
        "llama": "192.168.10.32",
        "gemma": "192.168.10.33",
        "qwen": "192.168.10.32",
        "mistral": "192.168.10.33",
        "codellama": "192.168.10.32"
    })


@dataclass
class APIGatewayConfig:
    """API Gateway configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: float = 30.0
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    cors_origins: list = field(default_factory=lambda: ["*"])
    rate_limit_requests: int = 1000
    rate_limit_window: int = 60
    auth_enabled: bool = True
    api_keys: list = field(default_factory=lambda: ["dev-key-001", "test-key-002"])
    ip_allowlist: list = field(default_factory=lambda: ["192.168.10.0/24", "127.0.0.1"])


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    metrics_enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: float = 30.0
    health_check_timeout: float = 10.0
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    max_log_file_size: int = 100 * 1024 * 1024  # 100MB
    log_backup_count: int = 5
    prometheus_enabled: bool = True
    grafana_enabled: bool = True


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    max_batch_size: int = 10000
    max_concurrent_requests: int = 100
    search_timeout: float = 10.0
    insert_timeout: float = 30.0
    update_timeout: float = 30.0
    delete_timeout: float = 15.0
    parallel_search_limit: int = 10
    cache_warming_enabled: bool = True
    connection_pool_size: int = 50


class ConfigManager:
    """
    Centralized configuration management.
    Handles environment-based configuration with validation and defaults.
    """
    
    def __init__(self, config_file: Optional[str] = None, env_prefix: str = "HANA_X"):
        self.config_file = config_file
        self.env_prefix = env_prefix
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment."""
        # Load default configuration
        self._config = self._get_default_config()
        
        # Load from file if specified
        if self.config_file and os.path.exists(self.config_file):
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "qdrant": QdrantConfig().__dict__,
            "cache": CacheConfig().__dict__,
            "external_models": ExternalModelConfig().__dict__,
            "api_gateway": APIGatewayConfig().__dict__,
            "monitoring": MonitoringConfig().__dict__,
            "performance": PerformanceConfig().__dict__
        }
    
    def _load_from_file(self):
        """Load configuration from file."""
        try:
            file_path = Path(self.config_file)
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    file_config = json.load(f)
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                with open(file_path, 'r') as f:
                    file_config = yaml.safe_load(f)
            else:
                raise ValidationError(f"Unsupported config file format: {file_path.suffix}")
            
            # Merge with existing config
            self._deep_merge(self._config, file_config)
            
        except Exception as e:
            raise ValidationError(f"Failed to load config file {self.config_file}: {str(e)}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Mapping of environment variables to config paths
        env_mappings = {
            # Qdrant
            f"{self.env_prefix}_QDRANT_HOST": ("qdrant", "host"),
            f"{self.env_prefix}_QDRANT_PORT": ("qdrant", "port"),
            f"{self.env_prefix}_QDRANT_GRPC_PORT": ("qdrant", "grpc_port"),
            f"{self.env_prefix}_QDRANT_TIMEOUT": ("qdrant", "timeout"),
            f"{self.env_prefix}_QDRANT_BATCH_SIZE": ("qdrant", "batch_size"),
            
            # Cache
            f"{self.env_prefix}_CACHE_HOST": ("cache", "host"),
            f"{self.env_prefix}_CACHE_PORT": ("cache", "port"),
            f"{self.env_prefix}_CACHE_DB": ("cache", "db"),
            f"{self.env_prefix}_CACHE_PASSWORD": ("cache", "password"),
            f"{self.env_prefix}_CACHE_TTL_DEFAULT": ("cache", "ttl_default"),
            
            # External Models
            f"{self.env_prefix}_MODELS_SERVER_1": ("external_models", "server_1"),
            f"{self.env_prefix}_MODELS_SERVER_2": ("external_models", "server_2"),
            f"{self.env_prefix}_MODELS_PORT": ("external_models", "port"),
            f"{self.env_prefix}_MODELS_TIMEOUT": ("external_models", "timeout"),
            
            # API Gateway
            f"{self.env_prefix}_API_HOST": ("api_gateway", "host"),
            f"{self.env_prefix}_API_PORT": ("api_gateway", "port"),
            f"{self.env_prefix}_API_WORKERS": ("api_gateway", "workers"),
            f"{self.env_prefix}_API_RATE_LIMIT": ("api_gateway", "rate_limit_requests"),
            
            # Monitoring
            f"{self.env_prefix}_LOG_LEVEL": ("monitoring", "log_level"),
            f"{self.env_prefix}_LOG_FORMAT": ("monitoring", "log_format"),
            f"{self.env_prefix}_LOG_FILE": ("monitoring", "log_file"),
            f"{self.env_prefix}_METRICS_PORT": ("monitoring", "metrics_port"),
            
            # Performance
            f"{self.env_prefix}_MAX_BATCH_SIZE": ("performance", "max_batch_size"),
            f"{self.env_prefix}_MAX_CONCURRENT": ("performance", "max_concurrent_requests"),
            f"{self.env_prefix}_SEARCH_TIMEOUT": ("performance", "search_timeout")
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert value to appropriate type
                converted_value = self._convert_env_value(value, section, key)
                self._config[section][key] = converted_value
    
    def _convert_env_value(self, value: str, section: str, key: str) -> Any:
        """Convert environment variable value to appropriate type."""
        # Get the default value to determine type
        default_value = self._config[section][key]
        
        if isinstance(default_value, bool):
            return value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(default_value, int):
            return int(value)
        elif isinstance(default_value, float):
            return float(value)
        elif isinstance(default_value, list):
            return [item.strip() for item in value.split(',')]
        else:
            return value
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate Qdrant config
        qdrant_config = self._config["qdrant"]
        if not isinstance(qdrant_config["port"], int) or qdrant_config["port"] <= 0:
            raise ValidationError("Qdrant port must be a positive integer")
        
        if not isinstance(qdrant_config["timeout"], (int, float)) or qdrant_config["timeout"] <= 0:
            raise ValidationError("Qdrant timeout must be a positive number")
        
        # Validate Cache config
        cache_config = self._config["cache"]
        if not isinstance(cache_config["port"], int) or cache_config["port"] <= 0:
            raise ValidationError("Cache port must be a positive integer")
        
        # Validate API Gateway config
        api_config = self._config["api_gateway"]
        if not isinstance(api_config["port"], int) or api_config["port"] <= 0:
            raise ValidationError("API Gateway port must be a positive integer")
        
        if not isinstance(api_config["workers"], int) or api_config["workers"] <= 0:
            raise ValidationError("API Gateway workers must be a positive integer")
        
        # Validate Performance config
        perf_config = self._config["performance"]
        if not isinstance(perf_config["max_batch_size"], int) or perf_config["max_batch_size"] <= 0:
            raise ValidationError("Max batch size must be a positive integer")
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if section not in self._config:
            return default
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def get_qdrant_config(self) -> QdrantConfig:
        """Get Qdrant configuration."""
        config_dict = self._config["qdrant"]
        return QdrantConfig(**config_dict)
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        config_dict = self._config["cache"]
        return CacheConfig(**config_dict)
    
    def get_external_models_config(self) -> ExternalModelConfig:
        """Get external models configuration."""
        config_dict = self._config["external_models"]
        return ExternalModelConfig(**config_dict)
    
    def get_api_gateway_config(self) -> APIGatewayConfig:
        """Get API Gateway configuration."""
        config_dict = self._config["api_gateway"]
        return APIGatewayConfig(**config_dict)
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        config_dict = self._config["monitoring"]
        return MonitoringConfig(**config_dict)
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        config_dict = self._config["performance"]
        return PerformanceConfig(**config_dict)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
    
    def reload(self):
        """Reload configuration."""
        self._load_config()
    
    def save_to_file(self, file_path: str, format: str = "json"):
        """
        Save configuration to file.
        
        Args:
            file_path: Output file path
            format: File format (json or yaml)
        """
        try:
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(self._config, f, indent=2)
            elif format.lower() in ["yaml", "yml"]:
                with open(file_path, 'w') as f:
                    yaml.dump(self._config, f, default_flow_style=False)
            else:
                raise ValidationError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise ValidationError(f"Failed to save config to {file_path}: {str(e)}")
    
    def validate_connection_config(self, section: str) -> bool:
        """
        Validate connection configuration.
        
        Args:
            section: Configuration section to validate
            
        Returns:
            True if valid
        """
        if section == "qdrant":
            config = self.get_qdrant_config()
            # Basic validation - in production would test actual connection
            return (
                isinstance(config.host, str) and 
                isinstance(config.port, int) and 
                config.port > 0 and 
                config.timeout > 0
            )
        
        elif section == "cache":
            config = self.get_cache_config()
            return (
                isinstance(config.host, str) and 
                isinstance(config.port, int) and 
                config.port > 0 and 
                config.timeout > 0
            )
        
        elif section == "external_models":
            config = self.get_external_models_config()
            return (
                isinstance(config.server_1, str) and 
                isinstance(config.server_2, str) and 
                isinstance(config.port, int) and 
                config.port > 0 and 
                config.timeout > 0
            )
        
        return False
    
    def get_connection_string(self, service: str) -> str:
        """
        Get connection string for a service.
        
        Args:
            service: Service name
            
        Returns:
            Connection string
        """
        if service == "qdrant":
            config = self.get_qdrant_config()
            return f"http://{config.host}:{config.port}"
        
        elif service == "qdrant_grpc":
            config = self.get_qdrant_config()
            return f"{config.host}:{config.grpc_port}"
        
        elif service == "cache":
            config = self.get_cache_config()
            return f"redis://{config.host}:{config.port}/{config.db}"
        
        elif service == "external_models_1":
            config = self.get_external_models_config()
            return f"http://{config.server_1}:{config.port}"
        
        elif service == "external_models_2":
            config = self.get_external_models_config()
            return f"http://{config.server_2}:{config.port}"
        
        else:
            raise ValidationError(f"Unknown service: {service}")
    
    def get_model_server(self, model_name: str) -> str:
        """
        Get server for a specific model.
        
        Args:
            model_name: Model name
            
        Returns:
            Server address
        """
        config = self.get_external_models_config()
        server_ip = config.models.get(model_name)
        
        if not server_ip:
            raise ValidationError(f"Unknown model: {model_name}")
        
        return f"http://{server_ip}:{config.port}"
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """
        Update configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
        """
        self._deep_merge(self._config, config_dict)
        self._validate_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._config = self._get_default_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary.
        
        Returns:
            Configuration summary
        """
        return {
            "qdrant": {
                "host": self._config["qdrant"]["host"],
                "port": self._config["qdrant"]["port"],
                "grpc_port": self._config["qdrant"]["grpc_port"]
            },
            "cache": {
                "host": self._config["cache"]["host"],
                "port": self._config["cache"]["port"],
                "db": self._config["cache"]["db"]
            },
            "external_models": {
                "server_1": self._config["external_models"]["server_1"],
                "server_2": self._config["external_models"]["server_2"],
                "port": self._config["external_models"]["port"],
                "models": list(self._config["external_models"]["models"].keys())
            },
            "api_gateway": {
                "host": self._config["api_gateway"]["host"],
                "port": self._config["api_gateway"]["port"],
                "workers": self._config["api_gateway"]["workers"]
            },
            "monitoring": {
                "log_level": self._config["monitoring"]["log_level"],
                "metrics_enabled": self._config["monitoring"]["metrics_enabled"],
                "metrics_port": self._config["monitoring"]["metrics_port"]
            }
        }
