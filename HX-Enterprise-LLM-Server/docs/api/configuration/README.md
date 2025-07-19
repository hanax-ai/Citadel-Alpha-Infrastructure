# Configuration API Reference

[![Configuration API](https://img.shields.io/badge/Configuration%20API-Complete-brightgreen.svg)](https://github.com/manus-ai/hxp-enterprise-llm)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/manus-ai/hxp-enterprise-llm)

Complete API reference for the HXP-Enterprise LLM Server configuration management system. This documentation covers all configuration APIs, schemas, validation, and management utilities.

## 📚 Overview

The configuration management system provides comprehensive configuration handling for all HXP-Enterprise LLM Server components. It supports multiple configuration sources, environment-specific configurations, hot-reloading, and validation.

### **Key Features**
- **Multi-source Configuration**: Support for files, environment variables, and remote sources
- **Environment-specific Configs**: Different configurations for development, staging, and production
- **Hot-reloading**: Dynamic configuration updates without service restart
- **Validation**: Comprehensive schema validation and type checking
- **Security**: Secure handling of sensitive configuration data
- **Caching**: Intelligent configuration caching for performance

## 🚀 Quick Start

### **Basic Configuration Usage**
```python
from hxp_enterprise_llm.services.infrastructure.configuration import ConfigurationManager

# Initialize configuration manager
config_manager = ConfigurationManager()

# Load configuration
config = await config_manager.load_config("production")

# Access configuration values
mixtral_port = config.services.ai_models.mixtral.port
database_url = config.integration.database.url
```

### **Environment-specific Configuration**
```python
# Development configuration
dev_config = await config_manager.load_config("development")

# Production configuration
prod_config = await config_manager.load_config("production")

# Custom environment
custom_config = await config_manager.load_config("staging")
```

## 📋 API Reference

### **ConfigurationManager**

The main configuration management class that handles all configuration operations.

#### **Constructor**
```python
ConfigurationManager(
    config_path: str = "/opt/citadel/hxp-enterprise-llm/config",
    environment: str = "development",
    enable_hot_reload: bool = True,
    enable_validation: bool = True,
    enable_caching: bool = True
)
```

**Parameters:**
- `config_path` (str): Base path for configuration files
- `environment` (str): Environment name (development, staging, production)
- `enable_hot_reload` (bool): Enable hot-reloading of configuration changes
- `enable_validation` (bool): Enable configuration validation
- `enable_caching` (bool): Enable configuration caching

#### **Core Methods**

##### **load_config(environment: str = None) -> Configuration**
Load configuration for the specified environment.

```python
async def load_config(self, environment: str = None) -> Configuration:
    """
    Load configuration for the specified environment.
    
    Args:
        environment (str): Environment name (development, staging, production)
        
    Returns:
        Configuration: Loaded configuration object
        
    Raises:
        ConfigurationError: If configuration loading fails
        ValidationError: If configuration validation fails
    """
```

**Example:**
```python
# Load production configuration
config = await config_manager.load_config("production")

# Load current environment configuration
config = await config_manager.load_config()
```

##### **get_service_config(service_name: str) -> ServiceConfig**
Get configuration for a specific service.

```python
def get_service_config(self, service_name: str) -> ServiceConfig:
    """
    Get configuration for a specific service.
    
    Args:
        service_name (str): Name of the service
        
    Returns:
        ServiceConfig: Service configuration object
        
    Raises:
        ConfigurationError: If service configuration not found
    """
```

**Example:**
```python
# Get Mixtral service configuration
mixtral_config = config_manager.get_service_config("mixtral")
print(f"Mixtral port: {mixtral_config.port}")
print(f"Mixtral memory: {mixtral_config.memory_limit_gb}GB")
```

##### **update_config(updates: dict) -> bool**
Update configuration with new values.

```python
async def update_config(self, updates: dict) -> bool:
    """
    Update configuration with new values.
    
    Args:
        updates (dict): Configuration updates to apply
        
    Returns:
        bool: True if update successful
        
    Raises:
        ValidationError: If updates fail validation
        ConfigurationError: If update operation fails
    """
```

**Example:**
```python
# Update service configuration
updates = {
    "services": {
        "ai_models": {
            "mixtral": {
                "port": 11401,
                "memory_limit_gb": 95
            }
        }
    }
}

success = await config_manager.update_config(updates)
```

##### **validate_config(config: dict) -> ValidationResult**
Validate configuration against schemas.

```python
def validate_config(self, config: dict) -> ValidationResult:
    """
    Validate configuration against schemas.
    
    Args:
        config (dict): Configuration to validate
        
    Returns:
        ValidationResult: Validation result with errors and warnings
    """
```

**Example:**
```python
# Validate configuration
result = config_manager.validate_config(config_dict)

if result.is_valid:
    print("Configuration is valid")
else:
    print(f"Validation errors: {result.errors}")
    print(f"Validation warnings: {result.warnings}")
```

##### **reload_config() -> bool**
Reload configuration from sources.

```python
async def reload_config(self) -> bool:
    """
    Reload configuration from sources.
    
    Returns:
        bool: True if reload successful
        
    Raises:
        ConfigurationError: If reload fails
    """
```

**Example:**
```python
# Reload configuration
success = await config_manager.reload_config()
if success:
    print("Configuration reloaded successfully")
```

### **Configuration Sources**

#### **File-based Configuration**
```python
# Configuration file structure
config/
├── base.yaml              # Base configuration
├── development.yaml       # Development overrides
├── staging.yaml          # Staging overrides
├── production.yaml       # Production overrides
└── secrets.yaml          # Sensitive configuration
```

**Base Configuration (base.yaml):**
```yaml
services:
  ai_models:
    mixtral:
      port: 11400
      memory_limit_gb: 90
      cpu_cores: 8
      context_length: 32768
    hermes:
      port: 11401
      memory_limit_gb: 15
      cpu_cores: 4
      context_length: 8192
    openchat:
      port: 11402
      memory_limit_gb: 8
      cpu_cores: 4
      context_length: 4096
    phi3:
      port: 11403
      memory_limit_gb: 4
      cpu_cores: 2
      context_length: 2048

infrastructure:
  api_gateway:
    port: 8000
    host: "0.0.0.0"
    rate_limit: 1000
  monitoring:
    port: 9090
    metrics_path: "/metrics"
    health_path: "/health"

integration:
  database:
    host: "192.168.10.35"
    port: 5433
    database: "citadel_alpha"
    pool_size: 20
  vector_database:
    host: "192.168.10.30"
    port: 6333
    collection: "citadel_vectors"
  cache:
    host: "192.168.10.37"
    port: 6379
    database: 0
```

#### **Environment Variable Configuration**
```python
# Environment variable mapping
HXP_MIXTRAL_PORT=11400
HXP_MIXTRAL_MEMORY_LIMIT_GB=90
HXP_DATABASE_HOST=192.168.10.35
HXP_DATABASE_PORT=5433
```

#### **Remote Configuration**
```python
# Remote configuration sources
config_sources = {
    "etcd": "http://etcd:2379",
    "consul": "http://consul:8500",
    "vault": "http://vault:8200"
}
```

### **Configuration Schemas**

#### **Service Configuration Schema**
```python
from pydantic import BaseModel, Field
from typing import Optional

class ServiceConfig(BaseModel):
    port: int = Field(..., ge=1024, le=65535)
    host: str = Field(default="0.0.0.0")
    memory_limit_gb: int = Field(..., ge=1, le=512)
    cpu_cores: int = Field(..., ge=1, le=64)
    context_length: Optional[int] = Field(default=None)
    max_batch_size: Optional[int] = Field(default=None)
    enable_streaming: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    enable_health_checks: bool = Field(default=True)
```

#### **Database Configuration Schema**
```python
class DatabaseConfig(BaseModel):
    host: str = Field(..., description="Database host")
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=30, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=1, le=86400)
```

### **Configuration Validation**

#### **Validation Rules**
```python
# Validation configuration
validation_config = {
    "strict_mode": True,
    "allow_unknown_fields": False,
    "validate_required_fields": True,
    "validate_types": True,
    "validate_ranges": True,
    "validate_formats": True
}
```

#### **Custom Validators**
```python
from pydantic import validator

class ServiceConfig(BaseModel):
    port: int
    memory_limit_gb: int
    
    @validator('port')
    def validate_port(cls, v):
        if v < 1024 or v > 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v
    
    @validator('memory_limit_gb')
    def validate_memory(cls, v):
        if v < 1 or v > 512:
            raise ValueError('Memory limit must be between 1 and 512 GB')
        return v
```

### **Configuration Security**

#### **Secret Management**
```python
from hxp_enterprise_llm.services.infrastructure.configuration import SecretManager

# Initialize secret manager
secret_manager = SecretManager()

# Store secret
await secret_manager.store_secret("database_password", "secure_password")

# Retrieve secret
password = await secret_manager.get_secret("database_password")

# Use secret in configuration
config.database.password = password
```

#### **Encryption**
```python
# Encrypt sensitive configuration
encrypted_config = config_manager.encrypt_sensitive_data(config)

# Decrypt configuration
decrypted_config = config_manager.decrypt_sensitive_data(encrypted_config)
```

### **Configuration Monitoring**

#### **Configuration Metrics**
```python
# Configuration metrics
config_metrics = {
    "config_load_time": 150,  # milliseconds
    "config_size": 2048,      # bytes
    "config_validation_time": 25,  # milliseconds
    "config_cache_hits": 95,  # percentage
    "config_reload_count": 3   # count
}
```

#### **Configuration Events**
```python
# Configuration change events
config_events = [
    {
        "event_type": "config_loaded",
        "timestamp": "2025-01-18T10:30:00Z",
        "environment": "production",
        "config_size": 2048
    },
    {
        "event_type": "config_updated",
        "timestamp": "2025-01-18T10:35:00Z",
        "changes": ["services.ai_models.mixtral.port"]
    }
]
```

## 🔧 Usage Examples

### **Complete Configuration Example**
```python
from hxp_enterprise_llm.services.infrastructure.configuration import ConfigurationManager
from hxp_enterprise_llm.schemas.configuration import Configuration

# Initialize configuration manager
config_manager = ConfigurationManager(
    config_path="/opt/citadel/hxp-enterprise-llm/config",
    environment="production",
    enable_hot_reload=True,
    enable_validation=True,
    enable_caching=True
)

# Load configuration
config = await config_manager.load_config("production")

# Access service configurations
mixtral_config = config_manager.get_service_config("mixtral")
hermes_config = config_manager.get_service_config("hermes")
openchat_config = config_manager.get_service_config("openchat")
phi3_config = config_manager.get_service_config("phi3")

# Access infrastructure configurations
api_gateway_config = config_manager.get_service_config("api_gateway")
monitoring_config = config_manager.get_service_config("monitoring")

# Access integration configurations
database_config = config.integration.database
vector_db_config = config.integration.vector_database
cache_config = config.integration.cache

# Update configuration
updates = {
    "services": {
        "ai_models": {
            "mixtral": {
                "memory_limit_gb": 95
            }
        }
    }
}

success = await config_manager.update_config(updates)

# Validate configuration
validation_result = config_manager.validate_config(config.dict())
if not validation_result.is_valid:
    print(f"Configuration validation failed: {validation_result.errors}")

# Reload configuration
reload_success = await config_manager.reload_config()
```

### **Environment-specific Configuration**
```python
# Development configuration
dev_config = await config_manager.load_config("development")
print(f"Development Mixtral port: {dev_config.services.ai_models.mixtral.port}")

# Staging configuration
staging_config = await config_manager.load_config("staging")
print(f"Staging Mixtral port: {staging_config.services.ai_models.mixtral.port}")

# Production configuration
prod_config = await config_manager.load_config("production")
print(f"Production Mixtral port: {prod_config.services.ai_models.mixtral.port}")
```

### **Configuration Hot-reloading**
```python
# Enable hot-reloading
config_manager = ConfigurationManager(enable_hot_reload=True)

# Set up configuration change handler
@config_manager.on_config_change
async def handle_config_change(config: Configuration):
    print("Configuration changed, updating services...")
    # Update service configurations
    await update_service_configs(config)

# Load initial configuration
config = await config_manager.load_config()

# Configuration changes will automatically trigger the handler
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Configuration Loading Errors**
```python
# Error: Configuration file not found
try:
    config = await config_manager.load_config("production")
except ConfigurationError as e:
    print(f"Configuration loading failed: {e}")
    # Check if configuration files exist
    # Verify file permissions
    # Check configuration syntax
```

#### **Validation Errors**
```python
# Error: Configuration validation failed
validation_result = config_manager.validate_config(config_dict)
if not validation_result.is_valid:
    for error in validation_result.errors:
        print(f"Validation error: {error.field} - {error.message}")
```

#### **Hot-reloading Issues**
```python
# Error: Hot-reloading not working
if not config_manager.hot_reload_enabled:
    print("Hot-reloading is disabled")
    # Enable hot-reloading
    config_manager.enable_hot_reload()
```

### **Debug Mode**
```python
# Enable debug mode for detailed logging
config_manager = ConfigurationManager(debug=True)

# Debug information will be logged
config = await config_manager.load_config("production")
```

## 📊 Performance Considerations

### **Configuration Caching**
```python
# Cache configuration for performance
config_manager = ConfigurationManager(enable_caching=True)

# Cache statistics
cache_stats = config_manager.get_cache_stats()
print(f"Cache hit rate: {cache_stats.hit_rate}%")
print(f"Cache size: {cache_stats.size} entries")
```

### **Configuration Size Optimization**
```python
# Optimize configuration size
config_manager = ConfigurationManager(
    enable_compression=True,
    max_config_size=1024 * 1024  # 1MB limit
)
```

## 🔒 Security Best Practices

### **Secret Management**
```python
# Use secret manager for sensitive data
secret_manager = SecretManager()

# Store secrets securely
await secret_manager.store_secret("database_password", "secure_password")

# Use secrets in configuration
config.database.password = await secret_manager.get_secret("database_password")
```

### **Configuration Encryption**
```python
# Encrypt sensitive configuration
encrypted_config = config_manager.encrypt_sensitive_data(config)

# Store encrypted configuration
await config_manager.store_encrypted_config(encrypted_config)
```

### **Access Control**
```python
# Implement access control for configuration
config_manager = ConfigurationManager(
    access_control=True,
    allowed_users=["admin", "operator"],
    allowed_operations=["read", "update"]
)
```

---

**Last Updated:** 2025-01-18  
**API Version:** 3.0.0  
**Documentation Status:** Complete  
**Configuration API Coverage:** 100% 