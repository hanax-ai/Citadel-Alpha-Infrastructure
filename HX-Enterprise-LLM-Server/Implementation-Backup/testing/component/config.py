"""
Component Testing Configuration

Manages configuration for component-level testing of AI models and infrastructure.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIModelConfig:
    """AI model component configuration."""
    port: int
    memory_limit_gb: int
    cpu_cores: int
    target_latency_ms: int
    target_throughput_rps: int
    model_path: str
    test_prompts: list


@dataclass
class InfrastructureConfig:
    """Infrastructure component configuration."""
    host: str
    port: int
    connection_timeout: int
    max_connections: int


@dataclass
class ComponentTestConfig:
    """Component testing configuration."""
    
    def __init__(self):
        """Initialize component test configuration."""
        self._load_config()
        self._load_environment_variables()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = "/opt/citadel/config/testing/component_tests.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                if config_data and 'component_tests' in config_data:
                    self._config = config_data['component_tests']
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
        
        self.test_environment = os.environ.get('COMPONENT_TEST_ENVIRONMENT', 'development')
        self.test_timeout = int(os.environ.get('COMPONENT_TEST_TIMEOUT', '300'))
        self.test_retries = int(os.environ.get('COMPONENT_TEST_RETRIES', '3'))
    
    def get_ai_model_config(self, model_name: str) -> Optional[AIModelConfig]:
        """Get AI model configuration."""
        if 'ai_models' in self._config and model_name in self._config['ai_models']:
            model_config = self._config['ai_models'][model_name]
            return AIModelConfig(
                port=model_config.get('port', 11400),
                memory_limit_gb=model_config.get('memory_limit_gb', 90),
                cpu_cores=model_config.get('cpu_cores', 8),
                target_latency_ms=model_config.get('target_latency_ms', 2000),
                target_throughput_rps=model_config.get('target_throughput_rps', 50),
                model_path=model_config.get('model_path', f'/opt/models/{model_name}'),
                test_prompts=model_config.get('test_prompts', [])
            )
        return None
    
    def get_infrastructure_config(self, component_name: str) -> Optional[InfrastructureConfig]:
        """Get infrastructure component configuration."""
        if 'infrastructure' in self._config and component_name in self._config['infrastructure']:
            infra_config = self._config['infrastructure'][component_name]
            return InfrastructureConfig(
                host=infra_config.get('host', 'localhost'),
                port=infra_config.get('port', 8000),
                connection_timeout=infra_config.get('connection_timeout', 30),
                max_connections=infra_config.get('max_connections', 20)
            )
        return None
    
    def get_all_ai_models(self) -> Dict[str, AIModelConfig]:
        """Get all AI model configurations."""
        models = {}
        if 'ai_models' in self._config:
            for model_name in self._config['ai_models']:
                config = self.get_ai_model_config(model_name)
                if config:
                    models[model_name] = config
        return models
    
    def get_all_infrastructure(self) -> Dict[str, InfrastructureConfig]:
        """Get all infrastructure configurations."""
        infrastructure = {}
        if 'infrastructure' in self._config:
            for component_name in self._config['infrastructure']:
                config = self.get_infrastructure_config(component_name)
                if config:
                    infrastructure[component_name] = config
        return infrastructure
    
    def validate(self) -> bool:
        """Validate configuration."""
        try:
            # Check required environment variables
            required_env_vars = ['COMPONENT_TEST_ENVIRONMENT']
            for var in required_env_vars:
                if not os.environ.get(var):
                    return False
            
            # Check configuration structure
            if not self._config:
                return False
            
            # Check AI models configuration
            ai_models = self.get_all_ai_models()
            if not ai_models:
                return False
            
            # Check infrastructure configuration
            infrastructure = self.get_all_infrastructure()
            if not infrastructure:
                return False
            
            return True
        except Exception:
            return False
    
    def get_test_prompts(self, model_name: str) -> list:
        """Get test prompts for a specific model."""
        model_config = self.get_ai_model_config(model_name)
        if model_config:
            return model_config.test_prompts
        return []
    
    def get_performance_targets(self, model_name: str) -> Dict[str, Any]:
        """Get performance targets for a specific model."""
        model_config = self.get_ai_model_config(model_name)
        if model_config:
            return {
                'latency_ms': model_config.target_latency_ms,
                'throughput_rps': model_config.target_throughput_rps,
                'memory_gb': model_config.memory_limit_gb,
                'cpu_cores': model_config.cpu_cores
            }
        return {} 