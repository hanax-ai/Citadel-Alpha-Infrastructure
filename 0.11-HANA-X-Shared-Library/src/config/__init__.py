"""
HANA-X Shared Library - Configuration Management

This module provides configuration management utilities that can be
reused across HANA-X infrastructure projects.
"""

__version__ = "0.1.0"
__author__ = "HANA-X Infrastructure Team"

from .base_config import (
    BaseConfigManager,
    ServerConfig,
    ModelConfig,
    PerformanceTargets,
    create_server_config,
    create_model_config,
    create_performance_targets
)

__all__ = [
    "BaseConfigManager",
    "ServerConfig",
    "ModelConfig", 
    "PerformanceTargets",
    "create_server_config",
    "create_model_config",
    "create_performance_targets"
]
