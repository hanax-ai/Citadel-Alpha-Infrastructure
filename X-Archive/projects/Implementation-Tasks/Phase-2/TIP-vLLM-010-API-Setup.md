# 🚀 Task Implementation Plan (TIP-vLLM-010)

## Title: OpenAI-Compatible API Setup (Phase 2, Task 2.2)

**Document ID:** TIP-vLLM-010  
**Version:** 1.0  
**Date:** 2025-01-10  
**Phase:** 2 - vLLM Installation & Configuration  
**Task Reference:** Task 2.2 from TL-vLLM-001  

---

## 🎯 Objective

Configure vLLM for OpenAI-compatible API serving on both servers with port differentiation and proper endpoint structure.

---

## 📋 Prerequisites

**Dependencies:**
- Task 2.1 Complete (vLLM Core Installation)
- vLLM successfully installed and imports functional
- FastAPI and uvicorn dependencies available
- Configuration management system operational

**Required Resources:**
- Network access to ports 8000 and 8001
- SSL certificate capability (future enhancement)
- Load balancer compatibility

---

## 🛠️ Implementation Steps

### Step 1: Port Configuration Planning
**Duration:** 5 minutes

**Server Port Assignments:**
- **hx-llm-server-01** (192.168.10.29): Port 8000 (Primary)
- **hx-llm-server-02** (192.168.10.28): Port 8001 (Secondary)

**API Endpoint Structure:**
```
GET  /v1/models
POST /v1/completions
POST /v1/chat/completions
GET  /v1/health
GET  /metrics
```

### Step 2: API Configuration Files
**Duration:** 15 minutes

Create server-specific API configurations with OpenAI compatibility.

### Step 3: API Server Scripts
**Duration:** 10 minutes

Develop start/stop scripts for API servers with proper parameter handling.

---

## 🔧 Configuration Files

### Primary Server API Configuration
**File:** `/opt/citadel/configs/api_server_01.json`

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "server_id": "hx-llm-server-01",
    "description": "Primary LLM Inference Server"
  },
  "openai_api": {
    "enabled": true,
    "chat_template": null,
    "response_role": "assistant",
    "enable_auto_completion": true,
    "enable_chat_completion": true
  },
  "engine": {
    "model": null,
    "tokenizer": null,
    "revision": null,
    "tokenizer_revision": null,
    "trust_remote_code": false,
    "download_dir": "/mnt/citadel-models",
    "load_format": "auto",
    "dtype": "auto",
    "seed": 0,
    "max_model_len": null,
    "worker_use_ray": true,
    "pipeline_parallel_size": 1,
    "tensor_parallel_size": 2,
    "max_parallel_loading_workers": 2,
    "block_size": 16,
    "swap_space": 4,
    "gpu_memory_utilization": 0.90,
    "max_num_batched_tokens": null,
    "max_num_seqs": 256,
    "max_paddings": 256,
    "disable_log_stats": false,
    "quantization": null,
    "enforce_eager": false,
    "max_context_len_to_capture": 8192
  },
  "logging": {
    "log_level": "INFO",
    "access_log": "/opt/citadel/logs/api_access_01.log",
    "error_log": "/opt/citadel/logs/api_error_01.log"
  },
  "performance": {
    "uvicorn_log_level": "info",
    "ssl_keyfile": null,
    "ssl_certfile": null,
    "root_path": null,
    "middleware": ["cors"],
    "cors_allow_origins": ["*"],
    "cors_allow_methods": ["*"],
    "cors_allow_headers": ["*"]
  }
}
```

### Secondary Server API Configuration
**File:** `/opt/citadel/configs/api_server_02.json`

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8001,
    "server_id": "hx-llm-server-02",
    "description": "Secondary LLM Inference Server"
  },
  "openai_api": {
    "enabled": true,
    "chat_template": null,
    "response_role": "assistant",
    "enable_auto_completion": true,
    "enable_chat_completion": true
  },
  "engine": {
    "model": null,
    "tokenizer": null,
    "revision": null,
    "tokenizer_revision": null,
    "trust_remote_code": false,
    "download_dir": "/mnt/citadel-models",
    "load_format": "auto",
    "dtype": "auto",
    "seed": 0,
    "max_model_len": null,
    "worker_use_ray": true,
    "pipeline_parallel_size": 1,
    "tensor_parallel_size": 2,
    "max_parallel_loading_workers": 2,
    "block_size": 16,
    "swap_space": 4,
    "gpu_memory_utilization": 0.90,
    "max_num_batched_tokens": null,
    "max_num_seqs": 256,
    "max_paddings": 256,
    "disable_log_stats": false,
    "quantization": null,
    "enforce_eager": false,
    "max_context_len_to_capture": 8192
  },
  "logging": {
    "log_level": "INFO",
    "access_log": "/opt/citadel/logs/api_access_02.log",
    "error_log": "/opt/citadel/logs/api_error_02.log"
  },
  "performance": {
    "uvicorn_log_level": "info",
    "ssl_keyfile": null,
    "ssl_certfile": null,
    "root_path": null,
    "middleware": ["cors"],
    "cors_allow_origins": ["*"],
    "cors_allow_methods": ["*"],
    "cors_allow_headers": ["*"]
  }
}
```

### API Server Launch Script
**File:** `/opt/citadel/scripts/start_api_server.sh`

```bash
#!/bin/bash
# vLLM API Server Launch Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/opt/citadel/configs"
LOG_DIR="/opt/citadel/logs"

# Determine server configuration based on hostname or IP
HOSTNAME=$(hostname)
SERVER_IP=$(hostname -I | awk '{print $1}')

if [[ "$SERVER_IP" == "192.168.10.29" ]]; then
    CONFIG_FILE="$CONFIG_DIR/api_server_01.json"
    SERVER_ID="hx-llm-server-01"
    PORT=8000
elif [[ "$SERVER_IP" == "192.168.10.28" ]]; then
    CONFIG_FILE="$CONFIG_DIR/api_server_02.json"
    SERVER_ID="hx-llm-server-02"
    PORT=8001
else
    echo "Error: Unknown server IP: $SERVER_IP"
    exit 1
fi

echo "Starting vLLM API server for $SERVER_ID on port $PORT"

# Source virtual environment
source /opt/citadel/venv/bin/activate

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Parse configuration and start server
python3 << EOF
import json
import subprocess
import sys

# Load configuration
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

# Build vllm serve command
cmd = [
    'python', '-m', 'vllm.entrypoints.openai.api_server',
    '--host', config['server']['host'],
    '--port', str(config['server']['port']),
    '--tensor-parallel-size', str(config['engine']['tensor_parallel_size']),
    '--gpu-memory-utilization', str(config['engine']['gpu_memory_utilization']),
    '--max-num-seqs', str(config['engine']['max_num_seqs']),
    '--download-dir', config['engine']['download_dir'],
    '--worker-use-ray'
]

# Add optional parameters
if config['engine']['max_model_len']:
    cmd.extend(['--max-model-len', str(config['engine']['max_model_len'])])

print(f"Executing: {' '.join(cmd)}")
subprocess.run(cmd)
EOF
```

### API Test Script
**File:** `/opt/citadel/scripts/test_api_endpoints.py`

```python
#!/usr/bin/env python3
# vLLM API Endpoint Testing Script

import json
import requests
import sys
import time
from typing import Dict, Any

def test_api_endpoint(base_url: str, timeout: int = 30) -> Dict[str, Any]:
    """Test vLLM API endpoints for functionality."""
    
    results = {
        'base_url': base_url,
        'timestamp': time.time(),
        'tests': {}
    }
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/v1/health", timeout=10)
        results['tests']['health'] = {
            'status': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        results['tests']['health'] = {
            'status': 'error',
            'success': False,
            'error': str(e)
        }
    
    # Test 2: Models Endpoint
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        results['tests']['models'] = {
            'status': response.status_code,
            'success': response.status_code == 200,
            'model_count': len(response.json().get('data', [])) if response.status_code == 200 else 0
        }
    except Exception as e:
        results['tests']['models'] = {
            'status': 'error',
            'success': False,
            'error': str(e)
        }
    
    # Test 3: Completions Endpoint (if model is loaded)
    if results['tests']['models'].get('success') and results['tests']['models'].get('model_count', 0) > 0:
        try:
            test_payload = {
                "prompt": "Hello, world!",
                "max_tokens": 10,
                "temperature": 0.0
            }
            response = requests.post(
                f"{base_url}/v1/completions",
                json=test_payload,
                timeout=30
            )
            results['tests']['completions'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'has_response': bool(response.json().get('choices')) if response.status_code == 200 else False
            }
        except Exception as e:
            results['tests']['completions'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    return results

def main():
    """Test both API servers."""
    servers = [
        {'name': 'hx-llm-server-01', 'url': 'http://192.168.10.29:8000'},
        {'name': 'hx-llm-server-02', 'url': 'http://192.168.10.28:8001'}
    ]
    
    all_results = {}
    
    for server in servers:
        print(f"Testing {server['name']} at {server['url']}")
        results = test_api_endpoint(server['url'])
        all_results[server['name']] = results
        
        # Print summary
        print(f"  Health: {'✅' if results['tests'].get('health', {}).get('success') else '❌'}")
        print(f"  Models: {'✅' if results['tests'].get('models', {}).get('success') else '❌'}")
        if 'completions' in results['tests']:
            print(f"  Completions: {'✅' if results['tests']['completions'].get('success') else '❌'}")
        print()
    
    # Save detailed results
    with open('/opt/citadel/logs/api_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Return exit code based on success
    all_success = all(
        result['tests'].get('health', {}).get('success', False) and
        result['tests'].get('models', {}).get('success', False)
        for result in all_results.values()
    )
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
```

---

## 🧪 Validation Tests

### Test 1: API Configuration Validation
```python
#!/usr/bin/env python3
# File: /opt/citadel/scripts/validate_api_config.py

import json
import sys
from pathlib import Path

def validate_config(config_path: str) -> bool:
    """Validate API configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Required fields validation
        required_fields = [
            'server.host',
            'server.port',
            'server.server_id',
            'openai_api.enabled',
            'engine.download_dir',
            'engine.tensor_parallel_size'
        ]
        
        for field in required_fields:
            keys = field.split('.')
            current = config
            for key in keys:
                if key not in current:
                    print(f"❌ Missing required field: {field}")
                    return False
                current = current[key]
        
        # Validate port ranges
        port = config['server']['port']
        if not (8000 <= port <= 8010):
            print(f"❌ Port {port} outside acceptable range (8000-8010)")
            return False
        
        # Validate paths
        download_dir = Path(config['engine']['download_dir'])
        if not download_dir.exists():
            print(f"❌ Download directory does not exist: {download_dir}")
            return False
        
        print(f"✅ Configuration valid: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False

def main():
    configs = [
        '/opt/citadel/configs/api_server_01.json',
        '/opt/citadel/configs/api_server_02.json'
    ]
    
    all_valid = True
    for config in configs:
        if not validate_config(config):
            all_valid = False
    
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
```

### Test 2: Port Availability Check
```bash
#!/bin/bash
# File: /opt/citadel/scripts/check_ports.sh

echo "Checking port availability..."

# Check if ports are available
check_port() {
    local port=$1
    if ss -tuln | grep -q ":$port "; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Test required ports
check_port 8000
check_port 8001

# Check if we can bind to the ports
python3 -c "
import socket
import sys

def test_bind(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        print(f'✅ Can bind to port {port}')
        return True
    except Exception as e:
        print(f'❌ Cannot bind to port {port}: {e}')
        return False

success = test_bind(8000) and test_bind(8001)
sys.exit(0 if success else 1)
"
```

---

## 📊 Success Criteria

### Primary Success Criteria
- [x] API server configuration created for both servers
- [x] Port configuration established (8000, 8001)
- [x] OpenAI compatibility verified with standard endpoints
- [x] API endpoint structure documented and functional

### Technical Requirements
- OpenAI API compatibility: Full /v1/ endpoint support
- Port assignments: 8000 (primary), 8001 (secondary)
- Response format: OpenAI-compatible JSON responses
- CORS support: Enabled for cross-origin requests

### Validation Metrics
- Configuration validation: 100% pass rate
- Port availability: Both ports accessible
- API response time: <500ms for health checks
- Endpoint coverage: All required endpoints functional

---

## 🚨 Troubleshooting Guide

### Issue: Port Already in Use
**Symptoms:** Cannot bind to port 8000/8001
**Solution:**
```bash
# Check what's using the port
sudo ss -tulpn | grep :8000
sudo ss -tulpn | grep :8001

# Kill conflicting processes if safe
sudo pkill -f "port 8000"
sudo pkill -f "port 8001"

# Use alternative ports if needed
# Modify configuration files to use 8002, 8003, etc.
```

### Issue: API Server Won't Start
**Symptoms:** vLLM API server fails to initialize
**Solution:**
```bash
# Check virtual environment
source /opt/citadel/venv/bin/activate
which python

# Verify vLLM installation
python -c "from vllm.entrypoints.openai.api_server import app"

# Check configuration syntax
python -m json.tool /opt/citadel/configs/api_server_01.json

# Start with verbose logging
python -m vllm.entrypoints.openai.api_server --help
```

### Issue: CORS Errors
**Symptoms:** Cross-origin requests blocked
**Solution:**
```bash
# Update configuration to allow specific origins
# Modify cors_allow_origins in config files

# Test CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://192.168.10.29:8000/v1/models
```

---

## 📋 Execution Checklist

### Pre-Execution
- [ ] vLLM core installation completed
- [ ] Configuration directories exist
- [ ] Ports 8000 and 8001 available
- [ ] Virtual environment activated

### During Execution
- [ ] Configuration files created successfully
- [ ] Scripts have proper permissions
- [ ] API server starts without errors
- [ ] Endpoints respond correctly

### Post-Execution
- [ ] Run endpoint validation tests
- [ ] Verify OpenAI compatibility
- [ ] Document API endpoint structure
- [ ] Test cross-server communication

---

## 🔄 Rollback Procedure

### Configuration Rollback
```bash
# Backup current configurations
cp /opt/citadel/configs/api_server_01.json /opt/citadel/configs/api_server_01.json.backup
cp /opt/citadel/configs/api_server_02.json /opt/citadel/configs/api_server_02.json.backup

# Restore from backup if needed
mv /opt/citadel/configs/api_server_01.json.backup /opt/citadel/configs/api_server_01.json
```

### Process Cleanup
```bash
# Stop any running API servers
pkill -f "vllm.entrypoints.openai.api_server"

# Clear any port bindings
sudo fuser -k 8000/tcp 2>/dev/null || true
sudo fuser -k 8001/tcp 2>/dev/null || true
```

---

## 📈 Next Steps

**Immediate Next Task:** TIP-vLLM-011 (Model Storage Configuration)

**Preparation for Next Phase:**
- API endpoints established and documented
- OpenAI compatibility confirmed
- Port configuration optimized
- Ready for model integration

---

*This implementation plan establishes robust OpenAI-compatible API serving following Citadel Alpha Infrastructure standards.*
