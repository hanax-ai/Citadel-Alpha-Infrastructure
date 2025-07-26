#!/usr/bin/env python3
"""
Citadel Configuration Manager
Centralized configuration management for LLM-02 system
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class ConfigPaths:
    """Configuration file paths"""
    home: Path = Path("/opt/citadel-02")
    config: Path = Path("/opt/citadel-02/config")
    global_config: Path = Path("/opt/citadel-02/config/global")
    environments: Path = Path("/opt/citadel-02/config/environments")
    secrets: Path = Path("/opt/citadel-02/config/secrets")
    services: Path = Path("/opt/citadel-02/config/services")

class CitadelConfig:
    """Centralized configuration manager for Citadel LLM system"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.paths = ConfigPaths()
        self._config_cache = {}
        
        # Load environment variables
        env_file = self.paths.home / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            
    def load_global_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if "global" not in self._config_cache:
            global_file = self.paths.global_config / "citadel.yaml"
            self._config_cache["global"] = self._load_yaml(global_file)
        return self._config_cache["global"]
    
    def load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        cache_key = f"env_{self.environment}"
        if cache_key not in self._config_cache:
            env_file = self.paths.environments / f"{self.environment}.yaml"
            self._config_cache[cache_key] = self._load_yaml(env_file)
        return self._config_cache[cache_key]
    
    def load_secrets(self) -> Dict[str, Any]:
        """Load secrets configuration"""
        if "secrets" not in self._config_cache:
            secrets_file = self.paths.secrets / "database-credentials.yaml"
            self._config_cache["secrets"] = self._load_yaml(secrets_file)
        return self._config_cache["secrets"]
    
    def get_merged_config(self) -> Dict[str, Any]:
        """Get merged configuration from all sources"""
        global_config = self.load_global_config()
        env_config = self.load_environment_config()
        
        # Deep merge configurations
        merged = self._deep_merge(global_config, env_config)
        
        # Add runtime information
        import sys
        from datetime import datetime
        merged["runtime"] = {
            "environment": self.environment,
            "config_loaded_at": str(datetime.now()),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "working_directory": str(Path.cwd()),
            "virtual_env": os.environ.get("VIRTUAL_ENV", "system"),
        }
        
        return merged
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration with secrets"""
        secrets = self.load_secrets()
        env_config = self.load_environment_config()
        
        return {
            "host": "192.168.10.35",
            "port": 5432,
            "database": "citadel_llm_db", 
            "username": "citadel_llm_user",
            "password": secrets.get("database", {}).get("password"),
            "pool_size": env_config.get("database", {}).get("pool_size", 10),
            "max_overflow": env_config.get("database", {}).get("max_overflow", 20),
        }
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama service configuration"""
        env_config = self.load_environment_config()
        
        return {
            "host": "localhost",
            "port": 11434,
            "api_url": "http://localhost:11434",
            "models_path": "/mnt/active_llm_models/.ollama",
            "max_parallel": 2,
            "max_loaded_models": 4,
            "timeout": env_config.get("ollama_service", {}).get("timeout", 300),
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring and observability configuration"""
        env_config = self.load_environment_config()
        
        return {
            "prometheus": {
                "url": "http://192.168.10.37:9090",
                "enabled": True,
                "metrics_endpoint": "/metrics",
            },
            "grafana": {
                "url": "http://192.168.10.37:3000",
                "username": "admin",
                "password": "admin",
                "enabled": True,
            },
            "alertmanager": {
                "url": "http://192.168.10.37:9093",
                "enabled": True,
            },
            "node_exporter": {
                "url": "http://192.168.10.37:9100",
                "enabled": True,
            },
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration and mappings"""
        return {
            "models": {
                "deepseek-r1:32b": {
                    "role": "Strategic Research & Intelligence",
                    "size": "19GB",
                    "parameters": "32.8B",
                    "quantization": "Q4_K_M",
                    "use_cases": ["market_analysis", "competitive_intelligence", "strategic_research"]
                },
                "hadad/JARVIS:latest": {
                    "role": "Advanced Business Intelligence", 
                    "size": "29GB",
                    "parameters": "14.8B",
                    "quantization": "F16",
                    "use_cases": ["executive_support", "complex_reasoning", "business_intelligence"]
                },
                "qwen:1.8b": {
                    "role": "Lightweight Operations",
                    "size": "1.1GB", 
                    "parameters": "2B",
                    "quantization": "Q4_0",
                    "use_cases": ["quick_responses", "high_volume", "efficient_processing"]
                },
                "deepcoder:14b": {
                    "role": "Code Generation",
                    "size": "9.0GB",
                    "parameters": "14.8B", 
                    "quantization": "Q4_K_M",
                    "use_cases": ["code_generation", "software_development", "system_integration"]
                },
                "yi:34b-chat": {
                    "role": "Advanced Reasoning",
                    "size": "19GB",
                    "parameters": "34B",
                    "quantization": "Q4_0", 
                    "use_cases": ["complex_reasoning", "problem_solving", "strategic_analysis"]
                }
            },
            "default_model": "qwen:1.8b",
            "model_routing": {
                "lightweight": "qwen:1.8b",
                "code": "deepcoder:14b", 
                "research": "deepseek-r1:32b",
                "business": "hadad/JARVIS:latest",
                "reasoning": "yi:34b-chat"
            }
        }
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration completeness"""
        validation_results = {}
        
        try:
            # Test global config
            global_config = self.load_global_config()
            validation_results["global_config"] = bool(global_config)
            
            # Test environment config
            env_config = self.load_environment_config()
            validation_results["environment_config"] = bool(env_config)
            
            # Test database config
            db_config = self.get_database_config()
            validation_results["database_config"] = all([
                db_config.get("host"),
                db_config.get("database"),
                db_config.get("username"),
                db_config.get("password")
            ])
            
            # Test Ollama config
            ollama_config = self.get_ollama_config()
            validation_results["ollama_config"] = bool(ollama_config.get("api_url"))
            
            # Test monitoring config
            monitoring_config = self.get_monitoring_config()
            validation_results["monitoring_config"] = bool(monitoring_config.get("prometheus"))
            
        except Exception as e:
            validation_results["error"] = str(e)
            
        return validation_results
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Configuration file not found: {file_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return {}
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

# Convenience functions for easy access
def get_config(environment: str = "production") -> CitadelConfig:
    """Get configuration manager instance"""
    return CitadelConfig(environment)

def get_database_url(environment: str = "production") -> str:
    """Get database connection URL"""
    config = get_config(environment)
    db_config = config.get_database_config()
    
    return f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

def get_ollama_url(environment: str = "production") -> str:
    """Get Ollama API URL"""
    config = get_config(environment)
    ollama_config = config.get_ollama_config()
    return ollama_config["api_url"]

if __name__ == "__main__":
    # CLI interface for configuration management
    import sys
    from datetime import datetime
    
    if len(sys.argv) < 2:
        print("Usage: python config_manager.py [command]")
        print("Commands: validate, show, test")
        sys.exit(1)
    
    command = sys.argv[1]
    environment = sys.argv[2] if len(sys.argv) > 2 else "production"
    
    config = CitadelConfig(environment)
    
    if command == "validate":
        results = config.validate_config()
        print(f"Configuration validation for {environment}:")
        for key, value in results.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
            
    elif command == "show":
        merged_config = config.get_merged_config()
        print(json.dumps(merged_config, indent=2, default=str))
        
    elif command == "test":
        try:
            # Test database connection
            db_url = get_database_url(environment)
            print(f"✅ Database URL: {db_url[:50]}...")
            
            # Test Ollama connection
            ollama_url = get_ollama_url(environment) 
            print(f"✅ Ollama URL: {ollama_url}")
            
            print("✅ Configuration test completed successfully")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
