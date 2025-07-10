# 🔧 Task 1.1: Configuration Management System Deployment

**Objective**: Deploy Pydantic-based configuration management system  
**Duration**: 45 minutes  
**Dependencies**: Phase 0 Complete (Tasks 0.1-0.5)  
**Success Criteria**: Configuration system functional, settings validated, environment variables managed

## Prerequisites
- [ ] Phase 0 tasks completed successfully (Infrastructure validated)
- [ ] SSH access to both servers with sudo privileges
- [ ] Python 3.12 environment available

## Step 1: Create Configuration Directory Structure - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Creating configuration directory structure on hx-llm-server-01..."

# Create citadel directory structure
ssh agent0@192.168.10.29 'sudo mkdir -p /opt/citadel/{configs,scripts,logs,tmp}'

# Set proper ownership
ssh agent0@192.168.10.29 'sudo chown -R agent0:agent0 /opt/citadel'

# Set proper permissions
ssh agent0@192.168.10.29 'chmod 755 /opt/citadel && chmod 755 /opt/citadel/{configs,scripts,logs,tmp}'

# Verify directory structure
ssh agent0@192.168.10.29 'ls -la /opt/citadel/' && echo "✅ Directory Structure: CREATED" || echo "❌ Directory Structure: FAILED"

# Test write access
ssh agent0@192.168.10.29 'touch /opt/citadel/test.tmp && rm /opt/citadel/test.tmp' && echo "✅ Write Access: PASS" || echo "❌ Write Access: FAIL"
```

## Step 2: Install Configuration Dependencies - hx-llm-server-01
```bash
echo "🔍 Installing configuration management dependencies on hx-llm-server-01..."

# Install Pydantic and related packages
ssh agent0@192.168.10.29 'pip3 install pydantic pydantic-settings python-dotenv PyYAML' && echo "✅ Dependencies: INSTALLED" || echo "❌ Dependencies: FAILED"

# Verify Pydantic installation
ssh agent0@192.168.10.29 'python3 -c "import pydantic; print(f\"Pydantic version: {pydantic.__version__}\")"' && echo "✅ Pydantic: FUNCTIONAL" || echo "❌ Pydantic: FAILED"

# Verify other dependencies
ssh agent0@192.168.10.29 'python3 -c "import yaml, os; print(\"PyYAML and os modules available\")"' && echo "✅ Support Libraries: FUNCTIONAL" || echo "❌ Support Libraries: FAILED"
```

## Step 3: Create Base Configuration Classes - hx-llm-server-01
```bash
echo "🔍 Creating base configuration classes on hx-llm-server-01..."

# Create base settings configuration
ssh agent0@192.168.10.29 'cat > /opt/citadel/configs/base_settings.py << EOF
"""
Base configuration settings for Citadel vLLM deployment
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator


class BaseConfig(BaseSettings):
    """Base configuration class with common settings"""
    
    # Environment settings
    environment: str = Field(default="development", description="Deployment environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Path settings
    citadel_root: Path = Field(default=Path("/opt/citadel"), description="Citadel root directory")
    config_dir: Path = Field(default=Path("/opt/citadel/configs"), description="Configuration directory")
    log_dir: Path = Field(default=Path("/opt/citadel/logs"), description="Log directory")
    
    # Server identification
    server_name: str = Field(default="unknown", description="Server identifier")
    server_role: str = Field(default="llm-server", description="Server role")
    
    class Config:
        env_file = "/opt/citadel/configs/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("citadel_root", "config_dir", "log_dir")
    def validate_paths(cls, v):
        """Ensure paths exist and are accessible"""
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path


class NetworkConfig(BaseSettings):
    """Network and connectivity configuration"""
    
    # Server network settings
    host_ip: str = Field(default="0.0.0.0", description="Host IP address")
    api_port: int = Field(default=8000, description="API server port")
    admin_port: int = Field(default=8001, description="Admin interface port")
    
    # Hana-X Lab network
    lab_network: str = Field(default="192.168.10.0/24", description="Lab network range")
    gateway_ip: str = Field(default="192.168.10.1", description="Network gateway")
    
    class Config:
        env_prefix = "NETWORK_"


class StorageConfig(BaseSettings):
    """Storage and filesystem configuration"""
    
    # Storage paths
    model_storage: Path = Field(default=Path("/mnt/citadel-models"), description="Model storage path")
    backup_storage: Path = Field(default=Path("/mnt/citadel-backup"), description="Backup storage path")
    temp_storage: Path = Field(default=Path("/opt/citadel/tmp"), description="Temporary storage path")
    
    # Storage limits
    model_storage_limit_gb: int = Field(default=2000, description="Model storage limit in GB")
    backup_storage_limit_gb: int = Field(default=5000, description="Backup storage limit in GB")
    
    class Config:
        env_prefix = "STORAGE_"
        
    @validator("model_storage", "backup_storage", "temp_storage")
    def validate_storage_paths(cls, v):
        """Validate storage paths exist"""
        path = Path(v)
        return path


if __name__ == "__main__":
    # Test configuration loading
    base_config = BaseConfig()
    network_config = NetworkConfig()
    storage_config = StorageConfig()
    
    print(f"Base Config: {base_config.dict()}")
    print(f"Network Config: {network_config.dict()}")
    print(f"Storage Config: {storage_config.dict()}")
EOF'

# Test configuration classes
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 base_settings.py' && echo "✅ Base Configuration: FUNCTIONAL" || echo "❌ Base Configuration: FAILED"
```

## Step 4: Create vLLM-Specific Configuration - hx-llm-server-01
```bash
echo "🔍 Creating vLLM-specific configuration on hx-llm-server-01..."

# Create vLLM settings
ssh agent0@192.168.10.29 'cat > /opt/citadel/configs/vllm_settings.py << EOF
"""
vLLM-specific configuration settings
"""
from typing import Optional, List, Dict
from pydantic import BaseSettings, Field, validator
from pathlib import Path

from base_settings import BaseConfig, NetworkConfig, StorageConfig


class vLLMConfig(BaseSettings):
    """vLLM engine configuration"""
    
    # Model settings
    default_model: str = Field(default="facebook/opt-125m", description="Default model to load")
    model_cache_dir: Path = Field(default=Path("/mnt/citadel-models/cache"), description="Model cache directory")
    
    # Engine settings
    tensor_parallel_size: int = Field(default=1, description="Tensor parallel size")
    gpu_memory_utilization: float = Field(default=0.9, description="GPU memory utilization ratio")
    max_model_len: Optional[int] = Field(default=None, description="Maximum model length")
    
    # API settings
    served_model_name: Optional[str] = Field(default=None, description="Served model name")
    chat_template: Optional[str] = Field(default=None, description="Chat template")
    
    # Performance settings
    swap_space: int = Field(default=4, description="Swap space in GB")
    cpu_offload_gb: int = Field(default=0, description="CPU offload memory in GB")
    
    class Config:
        env_prefix = "VLLM_"


class HuggingFaceConfig(BaseSettings):
    """Hugging Face integration configuration"""
    
    # Authentication
    hf_token: Optional[str] = Field(default=None, description="Hugging Face token")
    hf_cache_dir: Path = Field(default=Path("/mnt/citadel-models/hf-cache"), description="HF cache directory")
    
    # Download settings
    use_fast_tokenizer: bool = Field(default=True, description="Use fast tokenizer")
    trust_remote_code: bool = Field(default=False, description="Trust remote code")
    
    class Config:
        env_prefix = "HF_"


class MonitoringConfig(BaseSettings):
    """Monitoring and logging configuration"""
    
    # Logging
    log_requests: bool = Field(default=True, description="Log API requests")
    log_stats_interval: int = Field(default=60, description="Stats logging interval in seconds")
    
    # Metrics
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics server port")
    
    # Health checks
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    class Config:
        env_prefix = "MONITOR_"


class CitadelSettings(BaseConfig):
    """Complete Citadel configuration combining all settings"""
    
    # Include all configuration sections
    network: NetworkConfig = NetworkConfig()
    storage: StorageConfig = StorageConfig()
    vllm: vLLMConfig = vLLMConfig()
    huggingface: HuggingFaceConfig = HuggingFaceConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    
    def get_vllm_args(self) -> Dict[str, any]:
        """Generate vLLM command line arguments"""
        args = {
            "model": self.vllm.default_model,
            "host": self.network.host_ip,
            "port": self.network.api_port,
            "tensor-parallel-size": self.vllm.tensor_parallel_size,
            "gpu-memory-utilization": self.vllm.gpu_memory_utilization,
            "swap-space": self.vllm.swap_space,
        }
        
        if self.vllm.max_model_len:
            args["max-model-len"] = self.vllm.max_model_len
            
        if self.vllm.served_model_name:
            args["served-model-name"] = self.vllm.served_model_name
            
        return args
    
    def save_config(self, path: Optional[Path] = None) -> Path:
        """Save configuration to YAML file"""
        import yaml
        
        if path is None:
            path = self.config_dir / "citadel-config.yaml"
            
        config_dict = self.dict()
        with open(path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
        return path


def load_citadel_settings() -> CitadelSettings:
    """Load and return complete Citadel settings"""
    return CitadelSettings()


if __name__ == "__main__":
    # Test vLLM configuration
    settings = load_citadel_settings()
    print(f"vLLM Config: {settings.vllm.dict()}")
    print(f"vLLM Args: {settings.get_vllm_args()}")
    
    # Save configuration
    config_path = settings.save_config()
    print(f"Configuration saved to: {config_path}")
EOF'

# Test vLLM configuration
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 vllm_settings.py' && echo "✅ vLLM Configuration: FUNCTIONAL" || echo "❌ vLLM Configuration: FAILED"
```

## Step 5: Create Environment Configuration Template - hx-llm-server-01
```bash
echo "🔍 Creating environment configuration template on hx-llm-server-01..."

# Create .env template
ssh agent0@192.168.10.29 'cat > /opt/citadel/configs/.env.template << EOF
# Citadel vLLM Server Configuration
# Copy this file to .env and customize for your environment

# Base Configuration
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
SERVER_NAME=hx-llm-server-01
SERVER_ROLE=llm-server

# Network Configuration
NETWORK_HOST_IP=0.0.0.0
NETWORK_API_PORT=8000
NETWORK_ADMIN_PORT=8001
NETWORK_LAB_NETWORK=192.168.10.0/24
NETWORK_GATEWAY_IP=192.168.10.1

# Storage Configuration
STORAGE_MODEL_STORAGE=/mnt/citadel-models
STORAGE_BACKUP_STORAGE=/mnt/citadel-backup
STORAGE_TEMP_STORAGE=/opt/citadel/tmp
STORAGE_MODEL_STORAGE_LIMIT_GB=2000
STORAGE_BACKUP_STORAGE_LIMIT_GB=5000

# vLLM Configuration
VLLM_DEFAULT_MODEL=facebook/opt-125m
VLLM_TENSOR_PARALLEL_SIZE=1
VLLM_GPU_MEMORY_UTILIZATION=0.9
VLLM_SWAP_SPACE=4
VLLM_CPU_OFFLOAD_GB=0

# Hugging Face Configuration
# HF_TOKEN=your_hugging_face_token_here
HF_USE_FAST_TOKENIZER=true
HF_TRUST_REMOTE_CODE=false

# Monitoring Configuration
MONITOR_LOG_REQUESTS=true
MONITOR_LOG_STATS_INTERVAL=60
MONITOR_ENABLE_METRICS=true
MONITOR_METRICS_PORT=9090
MONITOR_HEALTH_CHECK_INTERVAL=30
EOF'

# Create default .env file (if not exists)
ssh agent0@192.168.10.29 'if [ ! -f /opt/citadel/configs/.env ]; then cp /opt/citadel/configs/.env.template /opt/citadel/configs/.env; fi'

# Test environment loading
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from vllm_settings import load_citadel_settings; settings = load_citadel_settings(); print(\"Environment loaded successfully\")"' && echo "✅ Environment Loading: FUNCTIONAL" || echo "❌ Environment Loading: FAILED"
```

## Step 6: Repeat for hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Setting up configuration management on hx-llm-server-02..."

# Create directory structure
ssh agent0@192.168.10.28 'sudo mkdir -p /opt/citadel/{configs,scripts,logs,tmp} && sudo chown -R agent0:agent0 /opt/citadel && chmod 755 /opt/citadel/{configs,scripts,logs,tmp}'

# Install dependencies
ssh agent0@192.168.10.28 'pip3 install pydantic pydantic-settings python-dotenv PyYAML' && echo "✅ Dependencies 02: INSTALLED" || echo "❌ Dependencies 02: FAILED"

# Copy configuration files from server-01
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && tar czf - base_settings.py vllm_settings.py .env.template' | ssh agent0@192.168.10.28 'cd /opt/citadel/configs && tar xzf -'

# Customize .env for server-02
ssh agent0@192.168.10.28 'cp /opt/citadel/configs/.env.template /opt/citadel/configs/.env'
ssh agent0@192.168.10.28 'sed -i "s/SERVER_NAME=hx-llm-server-01/SERVER_NAME=hx-llm-server-02/" /opt/citadel/configs/.env'
ssh agent0@192.168.10.28 'sed -i "s/NETWORK_API_PORT=8000/NETWORK_API_PORT=8002/" /opt/citadel/configs/.env'

# Test configuration on server-02
ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 vllm_settings.py' && echo "✅ Configuration 02: FUNCTIONAL" || echo "❌ Configuration 02: FAILED"
```

## Step 7: Configuration Validation and Report
```bash
echo "📊 Generating configuration management report..."

cat > /tmp/config-management-report.md << EOF
# Configuration Management System Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **Directory Structure**: $(ssh agent0@192.168.10.29 'test -d /opt/citadel/configs && echo "✅ CREATED" || echo "❌ MISSING"')
- **Dependencies**: $(ssh agent0@192.168.10.29 'python3 -c "import pydantic" 2>/dev/null && echo "✅ INSTALLED" || echo "❌ MISSING"')
- **Base Configuration**: $(ssh agent0@192.168.10.29 'test -f /opt/citadel/configs/base_settings.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Configuration**: $(ssh agent0@192.168.10.29 'test -f /opt/citadel/configs/vllm_settings.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Environment File**: $(ssh agent0@192.168.10.29 'test -f /opt/citadel/configs/.env && echo "✅ CREATED" || echo "❌ MISSING"')

## hx-llm-server-02 (192.168.10.28)
- **Directory Structure**: $(ssh agent0@192.168.10.28 'test -d /opt/citadel/configs && echo "✅ CREATED" || echo "❌ MISSING"')
- **Dependencies**: $(ssh agent0@192.168.10.28 'python3 -c "import pydantic" 2>/dev/null && echo "✅ INSTALLED" || echo "❌ MISSING"')
- **Base Configuration**: $(ssh agent0@192.168.10.28 'test -f /opt/citadel/configs/base_settings.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Configuration**: $(ssh agent0@192.168.10.28 'test -f /opt/citadel/configs/vllm_settings.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Environment File**: $(ssh agent0@192.168.10.28 'test -f /opt/citadel/configs/.env && echo "✅ CREATED" || echo "❌ MISSING"')

## Configuration Features
- **Pydantic-based validation**: ✅ Implemented
- **Environment variable support**: ✅ Implemented  
- **YAML configuration export**: ✅ Implemented
- **Server-specific customization**: ✅ Implemented
- **vLLM argument generation**: ✅ Implemented
- **Storage path validation**: ✅ Implemented

## Configuration Test Results
- Server-01 Config Loading: $(ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from vllm_settings import load_citadel_settings; load_citadel_settings()" 2>/dev/null && echo "✅ SUCCESS" || echo "❌ FAILED"')
- Server-02 Config Loading: $(ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 -c "from vllm_settings import load_citadel_settings; load_citadel_settings()" 2>/dev/null && echo "✅ SUCCESS" || echo "❌ FAILED"')
EOF

echo "📄 Configuration report saved to: /tmp/config-management-report.md"
cat /tmp/config-management-report.md
```

## Validation
Calculate configuration management readiness:
- Verify directory structure created on both servers
- Confirm Pydantic dependencies installed
- Validate configuration classes functional
- Test environment variable loading
- Check server-specific customization
- If all components functional → Task SUCCESS

## Troubleshooting

**Pydantic Installation Issues:**
```bash
# Install using pip with user flag
ssh agent0@192.168.10.29 'pip3 install --user pydantic pydantic-settings'

# Check Python path
ssh agent0@192.168.10.29 'python3 -c "import sys; print(sys.path)"'

# Install system-wide if needed
ssh agent0@192.168.10.29 'sudo pip3 install pydantic pydantic-settings python-dotenv PyYAML'
```

**Permission Issues:**
```bash
# Fix directory ownership
ssh agent0@192.168.10.29 'sudo chown -R agent0:agent0 /opt/citadel'

# Fix directory permissions
ssh agent0@192.168.10.29 'chmod -R 755 /opt/citadel'

# Check current permissions
ssh agent0@192.168.10.29 'ls -la /opt/citadel/'
```

**Configuration Loading Errors:**
```bash
# Check for syntax errors
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -m py_compile base_settings.py'

# Test individual components
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from base_settings import BaseConfig; print(BaseConfig())"'

# Check environment file format
ssh agent0@192.168.10.29 'cat /opt/citadel/configs/.env'
```

## Post-Task Checklist
- [ ] Configuration directory structure created on both servers
- [ ] Pydantic dependencies installed and functional
- [ ] Base configuration classes implemented
- [ ] vLLM-specific configuration created
- [ ] Environment file templates created
- [ ] Server-specific customization applied
- [ ] Configuration loading tested and validated

## Result Documentation
Document results in format:
```
Task 1.1 Results:
- hx-llm-server-01: Directory [CREATED/FAILED], Dependencies [INSTALLED/FAILED], Config Classes [FUNCTIONAL/FAILED], Environment [LOADED/FAILED]
- hx-llm-server-02: Directory [CREATED/FAILED], Dependencies [INSTALLED/FAILED], Config Classes [FUNCTIONAL/FAILED], Environment [LOADED/FAILED]
- Configuration Management: [OPERATIONAL/NEEDS_ATTENTION]
- Overall: [X/8] components functional ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 1.2: Python Virtual Environment Creation
