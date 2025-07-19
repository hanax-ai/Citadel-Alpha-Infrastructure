"""
Integration Testing Configuration

Manages configuration for integration testing of cross-service communication and external APIs.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CrossServiceConfig:
    """Cross-service integration configuration."""
    enabled: bool
    timeout_seconds: int
    retry_attempts: int
    concurrent_requests: Optional[int] = None
    test_scenarios: Optional[List[str]] = None


@dataclass
class ExternalAPIConfig:
    """External API integration configuration."""
    host: str
    port: int
    connection_timeout: int
    max_connections: int
    test_scenarios: Optional[List[str]] = None
    database: Optional[str] = None
    user: Optional[str] = None
    grpc_port: Optional[int] = None
    prometheus_port: Optional[int] = None
    grafana_port: Optional[int] = None
    alertmanager_port: Optional[int] = None
    node_exporter_port: Optional[int] = None


@dataclass
class DatabaseTestConfig:
    """Database test configuration."""
    enabled: bool
    pool_size: Optional[int] = None
    max_overflow: Optional[int] = None
    timeout: Optional[int] = None
    expected_schemas: Optional[List[str]] = None
    test_scenarios: Optional[List[str]] = None


class IntegrationTestConfig:
    """Integration testing configuration."""
    
    def __init__(self):
        """Initialize integration test configuration."""
        self._load_config()
        self._load_environment_variables()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = "/opt/citadel/config/testing/integration_tests.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                if config_data and 'integration_tests' in config_data:
                    self._config = config_data['integration_tests']
                else:
                    self._config = {}
        else:
            self._config = {}
    
    def _load_environment_variables(self) -> None:
        """Load environment variables."""
        # Load from .env file first
        env_file = "/opt/citadel/config/testing/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        
        self.test_environment = os.environ.get('INTEGRATION_TEST_ENVIRONMENT', 'development')
        self.test_timeout = int(os.environ.get('INTEGRATION_TEST_TIMEOUT', '300'))
        self.test_retries = int(os.environ.get('INTEGRATION_TEST_RETRIES', '3'))
        self.concurrent_requests = int(os.environ.get('INTEGRATION_TEST_CONCURRENT_REQUESTS', '10'))
    
    def get_cross_service_config(self, service_name: str) -> Optional[CrossServiceConfig]:
        """Get cross-service configuration."""
        if 'cross_service' in self._config and service_name in self._config['cross_service']:
            service_config = self._config['cross_service'][service_name]
            return CrossServiceConfig(
                enabled=service_config.get('enabled', True),
                timeout_seconds=service_config.get('timeout_seconds', 30),
                retry_attempts=service_config.get('retry_attempts', 3),
                concurrent_requests=service_config.get('concurrent_requests'),
                test_scenarios=service_config.get('test_scenarios', [])
            )
        return None
    
    def get_external_api_config(self, api_name: str) -> Optional[ExternalAPIConfig]:
        """Get external API configuration."""
        if 'external_apis' in self._config and api_name in self._config['external_apis']:
            api_config = self._config['external_apis'][api_name]
            return ExternalAPIConfig(
                host=api_config.get('host', 'localhost'),
                port=api_config.get('port', 8000),
                connection_timeout=api_config.get('connection_timeout', 30),
                max_connections=api_config.get('max_connections', 20),
                test_scenarios=api_config.get('test_scenarios', []),
                database=api_config.get('database'),
                user=api_config.get('user'),
                grpc_port=api_config.get('grpc_port'),
                prometheus_port=api_config.get('prometheus_port'),
                grafana_port=api_config.get('grafana_port'),
                alertmanager_port=api_config.get('alertmanager_port'),
                node_exporter_port=api_config.get('node_exporter_port')
            )
        return None
    
    def get_database_test_config(self, test_name: str) -> Optional[DatabaseTestConfig]:
        """Get database test configuration."""
        if 'database_tests' in self._config and test_name in self._config['database_tests']:
            test_config = self._config['database_tests'][test_name]
            return DatabaseTestConfig(
                enabled=test_config.get('enabled', True),
                pool_size=test_config.get('pool_size'),
                max_overflow=test_config.get('max_overflow'),
                timeout=test_config.get('timeout'),
                expected_schemas=test_config.get('expected_schemas'),
                test_scenarios=test_config.get('test_scenarios')
            )
        return None
    
    def get_all_cross_service_configs(self) -> Dict[str, CrossServiceConfig]:
        """Get all cross-service configurations."""
        configs = {}
        if 'cross_service' in self._config:
            for service_name in self._config['cross_service']:
                config = self.get_cross_service_config(service_name)
                if config:
                    configs[service_name] = config
        return configs
    
    def get_all_external_api_configs(self) -> Dict[str, ExternalAPIConfig]:
        """Get all external API configurations."""
        configs = {}
        if 'external_apis' in self._config:
            for api_name in self._config['external_apis']:
                config = self.get_external_api_config(api_name)
                if config:
                    configs[api_name] = config
        return configs
    
    def get_all_database_test_configs(self) -> Dict[str, DatabaseTestConfig]:
        """Get all database test configurations."""
        configs = {}
        if 'database_tests' in self._config:
            for test_name in self._config['database_tests']:
                config = self.get_database_test_config(test_name)
                if config:
                    configs[test_name] = config
        return configs
    
    def validate(self) -> bool:
        """Validate configuration."""
        try:
            # Check required environment variables
            required_env_vars = ['INTEGRATION_TEST_ENVIRONMENT']
            for var in required_env_vars:
                if not os.environ.get(var):
                    return False
            
            # Check configuration structure
            if not self._config:
                return False
            
            # Check cross-service configuration
            cross_service_configs = self.get_all_cross_service_configs()
            if not cross_service_configs:
                return False
            
            # Check external API configuration
            external_api_configs = self.get_all_external_api_configs()
            if not external_api_configs:
                return False
            
            # Check database test configuration
            database_test_configs = self.get_all_database_test_configs()
            if not database_test_configs:
                return False
            
            return True
        except Exception:
            return False
    
    def get_test_scenarios(self, category: str, name: str) -> List[str]:
        """Get test scenarios for a specific integration."""
        if category == 'cross_service':
            config = self.get_cross_service_config(name)
            return config.test_scenarios if config and config.test_scenarios else []
        elif category == 'external_apis':
            config = self.get_external_api_config(name)
            return config.test_scenarios if config and config.test_scenarios else []
        elif category == 'database_tests':
            config = self.get_database_test_config(name)
            return config.test_scenarios if config and config.test_scenarios else []
        return []
    
    def get_integration_timeout(self, category: str, name: str) -> int:
        """Get timeout for a specific integration."""
        if category == 'cross_service':
            config = self.get_cross_service_config(name)
            return config.timeout_seconds if config else 30
        elif category == 'external_apis':
            config = self.get_external_api_config(name)
            return config.connection_timeout if config else 30
        elif category == 'database_tests':
            config = self.get_database_test_config(name)
            return config.timeout if config and config.timeout else 30
        return 30 