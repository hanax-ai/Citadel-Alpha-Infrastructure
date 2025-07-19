"""
Test Framework Configuration Class

Manages configuration for the HXP-Enterprise LLM Server test framework.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestFrameworkConfig:
    """Configuration class for the test framework."""
    
    name: str = "HXP-Enterprise-LLM-Test-Framework"
    version: str = "1.0.0"
    environment: str = "development"
    coverage_threshold: int = 95
    performance_timeout: int = 300
    security_scan_enabled: bool = True
    certification_levels: int = 4
    
    def __post_init__(self):
        """Load configuration from file after initialization."""
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = "/opt/citadel/config/testing/test_framework.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                if config_data and 'test_framework' in config_data:
                    self._update_from_dict(config_data['test_framework'])
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        try:
            assert self.coverage_threshold >= 0 and self.coverage_threshold <= 100
            assert self.performance_timeout > 0
            assert self.certification_levels >= 1 and self.certification_levels <= 4
            assert self.environment in ['development', 'staging', 'production']
            return True
        except AssertionError:
            return False
    
    def get_coverage_config(self) -> Dict[str, Any]:
        """Get coverage configuration."""
        return {
            'minimum_line_coverage': self.coverage_threshold,
            'minimum_branch_coverage': 90,
            'minimum_function_coverage': 95,
            'coverage_report_format': 'html'
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return {
            'latency_threshold_ms': 2000,
            'throughput_threshold_rps': 50,
            'memory_limit_gb': 90,
            'cpu_limit_cores': 8,
            'performance_timeout_seconds': self.performance_timeout
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'vulnerability_threshold': 0,
            'security_test_coverage': 100,
            'compliance_score': 100,
            'security_scan_enabled': self.security_scan_enabled
        }
    
    def get_certification_config(self) -> Dict[str, Any]:
        """Get certification configuration."""
        return {
            'component_level': True,
            'integration_level': True,
            'service_level': True,
            'system_level': True
        }
    
    def get_reporting_config(self) -> Dict[str, Any]:
        """Get reporting configuration."""
        return {
            'output_format': 'html',
            'output_directory': '/opt/citadel/reports/testing',
            'include_coverage': True,
            'include_performance': True,
            'include_security': True
        } 