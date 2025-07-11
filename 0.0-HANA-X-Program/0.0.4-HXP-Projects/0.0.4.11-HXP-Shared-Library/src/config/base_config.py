"""
Base configuration management utilities for HANA-X infrastructure.

This module provides common configuration patterns and utilities that can be
reused across Enterprise and LoB server projects.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Base server configuration dataclass."""
    name: str
    ip: str
    port: int
    server_id: str
    description: str = ""


@dataclass
class ModelConfig:
    """Base model configuration dataclass."""
    model_name: str
    model_type: str
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.85
    max_num_seqs: int = 256
    max_model_len: int = 16384
    quantization: Optional[str] = None
    specialization: Optional[str] = None
    supported_languages: Optional[List[str]] = None


@dataclass
class PerformanceTargets:
    """Performance targets configuration."""
    max_latency_ms: int
    min_throughput_rps: int
    min_gpu_utilization: int
    max_memory_utilization: int
    availability_target: float


class BaseConfigManager(ABC):
    """
    Abstract base class for configuration management.
    
    Provides common configuration loading, validation, and management
    patterns for HANA-X infrastructure projects.
    """
    
    def __init__(self, config_dir: Union[str, Path]):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._cached_configs: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def get_default_config(self, config_type: str) -> Dict[str, Any]:
        """
        Get default configuration for specified type.
        
        Args:
            config_type: Type of configuration to retrieve
            
        Returns:
            Default configuration dictionary
        """
        pass
    
    def load_config(self, config_type: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load configuration from file with caching.
        
        Args:
            config_type: Type of configuration to load
            use_cache: Whether to use cached configuration
            
        Returns:
            Configuration dictionary
        """
        if use_cache and config_type in self._cached_configs:
            return self._cached_configs[config_type]
        
        config_file = self.config_dir / f"{config_type}_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded {config_type} configuration from {config_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load {config_type} config: {e}")
                config = self.get_default_config(config_type)
        else:
            logger.info(f"No {config_type} config file found, using defaults")
            config = self.get_default_config(config_type)
        
        # Apply environment variable overrides
        config = self._apply_env_overrides(config, config_type)
        
        # Cache the configuration
        self._cached_configs[config_type] = config
        
        return config
    
    def save_config(self, config_type: str, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config_type: Type of configuration to save
            config: Configuration dictionary to save
        """
        config_file = self.config_dir / f"{config_type}_config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved {config_type} configuration to {config_file}")
            
            # Update cache
            self._cached_configs[config_type] = config
            
        except IOError as e:
            logger.error(f"Failed to save {config_type} config: {e}")
            raise
    
    def validate_config(self, config_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate configuration dictionary.
        
        Args:
            config_type: Type of configuration to validate
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Basic validation - check required sections exist
            required_sections = self._get_required_sections(config_type)
            
            for section in required_sections:
                if section not in config:
                    logger.error(f"Missing required section '{section}' in {config_type} config")
                    return False
            
            # Type-specific validation
            return self._validate_config_specific(config_type, config)
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def merge_configs(self, base_config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration with overrides using deep update.
        
        Args:
            base_config: Base configuration dictionary
            overrides: Override values to apply
            
        Returns:
            Merged configuration dictionary
        """
        merged = base_config.copy()
        self._deep_update(merged, overrides)
        return merged
    
    def backup_config(self, config_type: str) -> Path:
        """
        Create backup of configuration file.
        
        Args:
            config_type: Type of configuration to backup
            
        Returns:
            Path to backup file
        """
        config_file = self.config_dir / f"{config_type}_config.json"
        backup_file = self.config_dir / f"{config_type}_config_backup.json"
        
        if config_file.exists():
            import shutil
            shutil.copy2(config_file, backup_file)
            logger.info(f"Created backup: {backup_file}")
        
        return backup_file
    
    def restore_config(self, config_type: str) -> bool:
        """
        Restore configuration from backup.
        
        Args:
            config_type: Type of configuration to restore
            
        Returns:
            True if restore was successful, False otherwise
        """
        backup_file = self.config_dir / f"{config_type}_config_backup.json"
        config_file = self.config_dir / f"{config_type}_config.json"
        
        if backup_file.exists():
            import shutil
            shutil.copy2(backup_file, config_file)
            logger.info(f"Restored {config_type} config from backup")
            
            # Clear cache to force reload
            self._cached_configs.pop(config_type, None)
            
            return True
        else:
            logger.warning(f"No backup found for {config_type} config")
            return False
    
    def _apply_env_overrides(self, config: Dict[str, Any], config_type: str) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        
        Args:
            config: Configuration dictionary
            config_type: Type of configuration
            
        Returns:
            Configuration with environment overrides applied
        """
        env_prefix = f"{config_type.upper()}_"
        
        # Common environment variable mappings
        env_mappings = {
            f"{env_prefix}SERVER_PORT": ["server", "port"],
            f"{env_prefix}SERVER_HOST": ["server", "host"],
            f"{env_prefix}MODEL_NAME": ["engine", "model"],
            f"{env_prefix}GPU_MEMORY": ["engine", "gpu_memory_utilization"],
            f"{env_prefix}MAX_SEQS": ["engine", "max_num_seqs"],
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Type conversion
                if config_path[-1] in ["port", "max_num_seqs"]:
                    value = int(value)
                elif config_path[-1] == "gpu_memory_utilization":
                    value = float(value)
                
                # Apply the override
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[config_path[-1]] = value
                
                logger.info(f"Applied env override: {env_var} = {value}")
        
        return config
    
    def _get_required_sections(self, config_type: str) -> List[str]:
        """
        Get required sections for configuration type.
        
        Args:
            config_type: Type of configuration
            
        Returns:
            List of required section names
        """
        common_sections = {
            "api_server": ["server", "engine"],
            "storage": ["storage", "servers"],
            "security": ["authentication", "audit"],
            "development": ["features", "supported_languages"],
        }
        
        return common_sections.get(config_type, [])
    
    @abstractmethod
    def _validate_config_specific(self, config_type: str, config: Dict[str, Any]) -> bool:
        """
        Perform config-type specific validation.
        
        Args:
            config_type: Type of configuration
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @staticmethod
    def _deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        Recursively update nested dictionary.
        
        Args:
            base_dict: Base dictionary to update
            update_dict: Updates to apply
        """
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                BaseConfigManager._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


def create_server_config(
    name: str,
    ip: str,
    port: int,
    server_id: str,
    description: str = ""
) -> ServerConfig:
    """
    Create a server configuration object.
    
    Args:
        name: Server name
        ip: Server IP address
        port: Server port
        server_id: Unique server identifier
        description: Server description
        
    Returns:
        ServerConfig object
    """
    return ServerConfig(
        name=name,
        ip=ip,
        port=port,
        server_id=server_id,
        description=description
    )


def create_model_config(
    model_name: str,
    model_type: str,
    **kwargs
) -> ModelConfig:
    """
    Create a model configuration object.
    
    Args:
        model_name: Name of the model
        model_type: Type of model
        **kwargs: Additional model configuration parameters
        
    Returns:
        ModelConfig object
    """
    return ModelConfig(
        model_name=model_name,
        model_type=model_type,
        **kwargs
    )


def create_performance_targets(
    max_latency_ms: int,
    min_throughput_rps: int,
    min_gpu_utilization: int,
    max_memory_utilization: int,
    availability_target: float
) -> PerformanceTargets:
    """
    Create performance targets configuration.
    
    Args:
        max_latency_ms: Maximum acceptable latency in milliseconds
        min_throughput_rps: Minimum throughput in requests per second
        min_gpu_utilization: Minimum GPU utilization percentage
        max_memory_utilization: Maximum memory utilization percentage
        availability_target: Target availability percentage
        
    Returns:
        PerformanceTargets object
    """
    return PerformanceTargets(
        max_latency_ms=max_latency_ms,
        min_throughput_rps=min_throughput_rps,
        min_gpu_utilization=min_gpu_utilization,
        max_memory_utilization=max_memory_utilization,
        availability_target=availability_target
    )
