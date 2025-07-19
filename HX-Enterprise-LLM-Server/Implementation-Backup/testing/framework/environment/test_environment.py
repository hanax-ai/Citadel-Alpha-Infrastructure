"""
Test Environment Management

Manages environment variables and external service connectivity for testing.
"""

import os
import socket
import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestEnvironment:
    """Test environment management class."""
    
    def __init__(self):
        """Initialize test environment."""
        self._load_environment_variables()
    
    def _load_environment_variables(self) -> None:
        """Load environment variables from .env file."""
        env_file = "/opt/citadel/config/testing/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    def get_environment_variable(self, key: str, default: str = "") -> str:
        """Get environment variable value."""
        return os.environ.get(key, default)
    
    def validate(self) -> bool:
        """Validate test environment configuration."""
        try:
            # Check required environment variables
            required_vars = [
                'TEST_ENVIRONMENT',
                'TEST_SERVER_IP',
                'TEST_SERVER_HOSTNAME'
            ]
            
            for var in required_vars:
                if not self.get_environment_variable(var):
                    return False
            
            # Check external service connectivity
            if not self.test_database_connectivity():
                return False
            
            if not self.test_vector_db_connectivity():
                return False
            
            return True
        except Exception:
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity."""
        try:
            host = self.get_environment_variable('TEST_DATABASE_HOST', '192.168.10.35')
            port = int(self.get_environment_variable('TEST_DATABASE_PORT', '5433'))
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
        except Exception:
            return False
    
    def test_vector_db_connectivity(self) -> bool:
        """Test vector database connectivity."""
        try:
            host = self.get_environment_variable('TEST_VECTOR_DB_HOST', '192.168.10.30')
            port = int(self.get_environment_variable('TEST_VECTOR_DB_PORT', '6333'))
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
        except Exception:
            return False
    
    def test_metrics_connectivity(self) -> bool:
        """Test metrics server connectivity."""
        try:
            host = self.get_environment_variable('TEST_METRICS_HOST', '192.168.10.37')
            port = int(self.get_environment_variable('TEST_PROMETHEUS_PORT', '9090'))
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
        except Exception:
            return False
    
    def get_server_info(self) -> Dict[str, str]:
        """Get server information."""
        return {
            'hostname': self.get_environment_variable('TEST_SERVER_HOSTNAME', 'hx-llm-server-01'),
            'ip': self.get_environment_variable('TEST_SERVER_IP', '192.168.10.29'),
            'environment': self.get_environment_variable('TEST_ENVIRONMENT', 'development')
        }
    
    def get_external_services(self) -> Dict[str, Dict[str, str]]:
        """Get external service configuration."""
        return {
            'database': {
                'host': self.get_environment_variable('TEST_DATABASE_HOST', '192.168.10.35'),
                'port': self.get_environment_variable('TEST_DATABASE_PORT', '5433'),
                'name': self.get_environment_variable('TEST_DATABASE_NAME', 'citadel_ai'),
                'user': self.get_environment_variable('TEST_DATABASE_USER', 'citadel_admin')
            },
            'vector_db': {
                'host': self.get_environment_variable('TEST_VECTOR_DB_HOST', '192.168.10.30'),
                'port': self.get_environment_variable('TEST_VECTOR_DB_PORT', '6333'),
                'grpc_port': self.get_environment_variable('TEST_VECTOR_DB_GRPC_PORT', '6334')
            },
            'metrics': {
                'host': self.get_environment_variable('TEST_METRICS_HOST', '192.168.10.37'),
                'prometheus_port': self.get_environment_variable('TEST_PROMETHEUS_PORT', '9090'),
                'grafana_port': self.get_environment_variable('TEST_GRAFANA_PORT', '3000')
            }
        } 