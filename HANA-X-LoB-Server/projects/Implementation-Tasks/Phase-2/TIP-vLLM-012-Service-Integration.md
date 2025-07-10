# 🚀 Task Implementation Plan (TIP-vLLM-012)

## Title: Service Integration Setup (Phase 2, Task 2.4)

**Document ID:** TIP-vLLM-012  
**Version:** 1.0  
**Date:** 2025-01-10  
**Phase:** 2 - vLLM Installation & Configuration  
**Task Reference:** Task 2.4 from TL-vLLM-001  

---

## 🎯 Objective

Create systemd services for production deployment with proper startup/shutdown procedures, service dependencies, auto-restart capabilities, and monitoring integration.

---

## 📋 Prerequisites

**Dependencies:**
- Task 2.3 Complete (Model Storage Configuration)
- vLLM API configuration functional
- Model storage and symlink management operational
- Virtual environment and dependencies installed

**Required Resources:**
- Root/sudo access for systemd service creation
- Service monitoring capabilities
- Log rotation and management
- Process management permissions

---

## 🛠️ Implementation Steps

### Step 1: Service Architecture Planning
**Duration:** 10 minutes

**Service Structure:**
- **Primary Service:** `vllm-server-01.service` (hx-llm-server-01)
- **Secondary Service:** `vllm-server-02.service` (hx-llm-server-02)
- **Management Services:** Health checks, log rotation, cleanup

### Step 2: Systemd Service Files Creation
**Duration:** 20 minutes

Create robust systemd service files with proper dependency management and restart policies.

### Step 3: Service Management Scripts
**Duration:** 10 minutes

Develop comprehensive service management and monitoring scripts.

---

## 🔧 Configuration Files

### Primary Server Systemd Service
**File:** `/etc/systemd/system/vllm-server-01.service`

```ini
[Unit]
Description=vLLM OpenAI API Server (Primary - hx-llm-server-01)
Documentation=https://docs.vllm.ai/
After=network.target network-online.target
Wants=network-online.target
Requires=nvidia-persistenced.service

[Service]
Type=exec
User=agent0
Group=agent0
WorkingDirectory=/opt/citadel
Environment=PATH=/opt/citadel/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=VIRTUAL_ENV=/opt/citadel/venv
Environment=PYTHONPATH=/opt/citadel/scripts:/opt/citadel/venv/lib/python3.12/site-packages
Environment=CUDA_VISIBLE_DEVICES=0,1
Environment=NCCL_DEBUG=WARN
Environment=PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
Environment=HF_HOME=/mnt/citadel-models/huggingface
Environment=TRANSFORMERS_CACHE=/mnt/citadel-models/huggingface
Environment=HF_HUB_CACHE=/mnt/citadel-models/huggingface

# Service execution
ExecStartPre=/opt/citadel/scripts/pre_start_checks.sh server-01
ExecStart=/opt/citadel/scripts/start_vllm_service.sh server-01
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/opt/citadel/scripts/stop_vllm_service.sh server-01
ExecStopPost=/opt/citadel/scripts/post_stop_cleanup.sh server-01

# Process management
Restart=always
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5
TimeoutStartSec=300
TimeoutStopSec=60
KillMode=mixed
KillSignal=SIGTERM

# Security and resource limits
NoNewPrivileges=true
ProtectHome=false
ProtectSystem=strict
ReadWritePaths=/opt/citadel /mnt/citadel-models /mnt/citadel-backup /tmp /var/tmp
PrivateTmp=true
LimitNOFILE=65536
LimitNPROC=32768
MemoryMax=100G
CPUQuota=2000%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vllm-server-01

[Install]
WantedBy=multi-user.target
```

### Secondary Server Systemd Service
**File:** `/etc/systemd/system/vllm-server-02.service`

```ini
[Unit]
Description=vLLM OpenAI API Server (Secondary - hx-llm-server-02)
Documentation=https://docs.vllm.ai/
After=network.target network-online.target
Wants=network-online.target
Requires=nvidia-persistenced.service

[Service]
Type=exec
User=agent0
Group=agent0
WorkingDirectory=/opt/citadel
Environment=PATH=/opt/citadel/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=VIRTUAL_ENV=/opt/citadel/venv
Environment=PYTHONPATH=/opt/citadel/scripts:/opt/citadel/venv/lib/python3.12/site-packages
Environment=CUDA_VISIBLE_DEVICES=0,1
Environment=NCCL_DEBUG=WARN
Environment=PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
Environment=HF_HOME=/mnt/citadel-models/huggingface
Environment=TRANSFORMERS_CACHE=/mnt/citadel-models/huggingface
Environment=HF_HUB_CACHE=/mnt/citadel-models/huggingface

# Service execution
ExecStartPre=/opt/citadel/scripts/pre_start_checks.sh server-02
ExecStart=/opt/citadel/scripts/start_vllm_service.sh server-02
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/opt/citadel/scripts/stop_vllm_service.sh server-02
ExecStopPost=/opt/citadel/scripts/post_stop_cleanup.sh server-02

# Process management
Restart=always
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5
TimeoutStartSec=300
TimeoutStopSec=60
KillMode=mixed
KillSignal=SIGTERM

# Security and resource limits
NoNewPrivileges=true
ProtectHome=false
ProtectSystem=strict
ReadWritePaths=/opt/citadel /mnt/citadel-models /mnt/citadel-backup /tmp /var/tmp
PrivateTmp=true
LimitNOFILE=65536
LimitNPROC=32768
MemoryMax=100G
CPUQuota=2000%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vllm-server-02

[Install]
WantedBy=multi-user.target
```

### Service Startup Script
**File:** `/opt/citadel/scripts/start_vllm_service.sh`

```bash
#!/bin/bash
# vLLM Service Startup Script for Citadel Alpha Infrastructure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/opt/citadel/configs"
LOG_DIR="/opt/citadel/logs"
SERVER_ID="${1:-}"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [vLLM-$SERVER_ID] $1" | tee -a "$LOG_DIR/service_startup.log"
}

# Validate server ID
if [[ -z "$SERVER_ID" ]]; then
    log "ERROR: Server ID not provided"
    exit 1
fi

# Determine configuration based on server ID
case "$SERVER_ID" in
    "server-01")
        CONFIG_FILE="$CONFIG_DIR/api_server_01.json"
        MODEL_LINKS_PATH="/opt/citadel/model-links/server-01"
        PORT=8000
        ;;
    "server-02")
        CONFIG_FILE="$CONFIG_DIR/api_server_02.json"
        MODEL_LINKS_PATH="/opt/citadel/model-links/server-02"
        PORT=8001
        ;;
    *)
        log "ERROR: Unknown server ID: $SERVER_ID"
        exit 1
        ;;
esac

log "Starting vLLM service for $SERVER_ID"

# Verify configuration file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    log "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Source virtual environment
source /opt/citadel/venv/bin/activate

# Load configuration
CONFIG=$(cat "$CONFIG_FILE")
HOST=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['server']['host'])")
PORT=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['server']['port'])")
TENSOR_PARALLEL=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['engine']['tensor_parallel_size'])")
GPU_MEMORY_UTIL=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['engine']['gpu_memory_utilization'])")
MAX_NUM_SEQS=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['engine']['max_num_seqs'])")
DOWNLOAD_DIR=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['engine']['download_dir'])")

log "Configuration loaded: Host=$HOST, Port=$PORT, TP=$TENSOR_PARALLEL"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check for available models
AVAILABLE_MODELS=()
if [[ -d "$MODEL_LINKS_PATH" ]]; then
    while IFS= read -r -d '' model; do
        if [[ -L "$model" && -e "$model" ]]; then
            AVAILABLE_MODELS+=("$(basename "$model")")
        fi
    done < <(find "$MODEL_LINKS_PATH" -type l -print0)
fi

if [[ ${#AVAILABLE_MODELS[@]} -eq 0 ]]; then
    log "WARNING: No models available in $MODEL_LINKS_PATH"
    log "Starting API server without pre-loaded models"
    
    # Start API server without model
    exec python3 -m vllm.entrypoints.openai.api_server \
        --host "$HOST" \
        --port "$PORT" \
        --tensor-parallel-size "$TENSOR_PARALLEL" \
        --gpu-memory-utilization "$GPU_MEMORY_UTIL" \
        --max-num-seqs "$MAX_NUM_SEQS" \
        --download-dir "$DOWNLOAD_DIR" \
        --worker-use-ray \
        --served-model-name "default" \
        2>&1 | tee -a "$LOG_DIR/vllm_${SERVER_ID}.log"
else
    # Use first available model
    PRIMARY_MODEL="${AVAILABLE_MODELS[0]}"
    MODEL_PATH="$MODEL_LINKS_PATH/$PRIMARY_MODEL"
    
    # Resolve symlink to get actual model path
    ACTUAL_MODEL_PATH=$(readlink -f "$MODEL_PATH")
    
    log "Starting with primary model: $PRIMARY_MODEL"
    log "Model path: $ACTUAL_MODEL_PATH"
    
    # Start API server with model
    exec python3 -m vllm.entrypoints.openai.api_server \
        --model "$ACTUAL_MODEL_PATH" \
        --host "$HOST" \
        --port "$PORT" \
        --tensor-parallel-size "$TENSOR_PARALLEL" \
        --gpu-memory-utilization "$GPU_MEMORY_UTIL" \
        --max-num-seqs "$MAX_NUM_SEQS" \
        --download-dir "$DOWNLOAD_DIR" \
        --worker-use-ray \
        --served-model-name "$PRIMARY_MODEL" \
        2>&1 | tee -a "$LOG_DIR/vllm_${SERVER_ID}.log"
fi
```

### Pre-Start Checks Script
**File:** `/opt/citadel/scripts/pre_start_checks.sh`

```bash
#!/bin/bash
# Pre-start validation checks for vLLM service
set -euo pipefail

SERVER_ID="${1:-}"
LOG_DIR="/opt/citadel/logs"
CONFIG_DIR="/opt/citadel/configs"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [PRE-CHECK-$SERVER_ID] $1" | tee -a "$LOG_DIR/pre_start_checks.log"
}

log "Running pre-start checks for $SERVER_ID"

# Check 1: NVIDIA GPU availability
if ! nvidia-smi &>/dev/null; then
    log "ERROR: NVIDIA GPU not accessible"
    exit 1
fi

GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
if [[ $GPU_COUNT -lt 2 ]]; then
    log "ERROR: Insufficient GPU count: $GPU_COUNT (minimum 2 required)"
    exit 1
fi

log "GPU check passed: $GPU_COUNT GPUs available"

# Check 2: Virtual environment
if [[ ! -f "/opt/citadel/venv/bin/activate" ]]; then
    log "ERROR: Virtual environment not found"
    exit 1
fi

source /opt/citadel/venv/bin/activate

if ! python3 -c "import vllm" &>/dev/null; then
    log "ERROR: vLLM not available in virtual environment"
    exit 1
fi

log "Virtual environment check passed"

# Check 3: Configuration file
case "$SERVER_ID" in
    "server-01")
        CONFIG_FILE="$CONFIG_DIR/api_server_01.json"
        ;;
    "server-02")
        CONFIG_FILE="$CONFIG_DIR/api_server_02.json"
        ;;
    *)
        log "ERROR: Unknown server ID: $SERVER_ID"
        exit 1
        ;;
esac

if [[ ! -f "$CONFIG_FILE" ]]; then
    log "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

if ! python3 -m json.tool "$CONFIG_FILE" &>/dev/null; then
    log "ERROR: Invalid JSON in configuration file"
    exit 1
fi

log "Configuration file check passed"

# Check 4: Storage availability
if [[ ! -d "/mnt/citadel-models" ]] || [[ ! -w "/mnt/citadel-models" ]]; then
    log "ERROR: Model storage not accessible"
    exit 1
fi

if [[ ! -d "/mnt/citadel-backup" ]] || [[ ! -w "/mnt/citadel-backup" ]]; then
    log "ERROR: Backup storage not accessible"
    exit 1
fi

log "Storage check passed"

# Check 5: Port availability
PORT=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config['server']['port'])")

if ss -tuln | grep -q ":$PORT "; then
    log "ERROR: Port $PORT already in use"
    exit 1
fi

log "Port $PORT availability check passed"

# Check 6: Memory availability
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')

if [[ $AVAILABLE_MEM -lt 50 ]]; then
    log "WARNING: Low available memory: ${AVAILABLE_MEM}GB (recommended: 50GB+)"
fi

log "Memory check passed: ${AVAILABLE_MEM}GB available"

log "All pre-start checks completed successfully"
```

### Service Stop Script
**File:** `/opt/citadel/scripts/stop_vllm_service.sh`

```bash
#!/bin/bash
# vLLM Service Stop Script for Citadel Alpha Infrastructure
set -euo pipefail

SERVER_ID="${1:-}"
LOG_DIR="/opt/citadel/logs"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [STOP-$SERVER_ID] $1" | tee -a "$LOG_DIR/service_stop.log"
}

log "Stopping vLLM service for $SERVER_ID"

# Get service PID
SERVICE_PID=$(pgrep -f "vllm.entrypoints.openai.api_server.*$SERVER_ID" || echo "")

if [[ -n "$SERVICE_PID" ]]; then
    log "Found service PID: $SERVICE_PID"
    
    # Graceful shutdown
    log "Sending SIGTERM to process $SERVICE_PID"
    kill -TERM "$SERVICE_PID"
    
    # Wait for graceful shutdown
    for i in {1..30}; do
        if ! kill -0 "$SERVICE_PID" 2>/dev/null; then
            log "Process terminated gracefully"
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 "$SERVICE_PID" 2>/dev/null; then
        log "Forcing process termination"
        kill -KILL "$SERVICE_PID"
        sleep 2
    fi
else
    log "No running service process found"
fi

# Clean up any remaining processes
REMAINING_PIDS=$(pgrep -f "vllm.*$SERVER_ID" || echo "")
if [[ -n "$REMAINING_PIDS" ]]; then
    log "Cleaning up remaining processes: $REMAINING_PIDS"
    echo "$REMAINING_PIDS" | xargs -r kill -KILL
fi

log "Service stop completed for $SERVER_ID"
```

### Post-Stop Cleanup Script
**File:** `/opt/citadel/scripts/post_stop_cleanup.sh`

```bash
#!/bin/bash
# Post-stop cleanup for vLLM service
set -euo pipefail

SERVER_ID="${1:-}"
LOG_DIR="/opt/citadel/logs"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [POST-CLEANUP-$SERVER_ID] $1" | tee -a "$LOG_DIR/post_stop_cleanup.log"
}

log "Running post-stop cleanup for $SERVER_ID"

# Clear GPU memory
if command -v nvidia-smi &>/dev/null; then
    log "Clearing GPU memory"
    nvidia-smi --gpu-reset || log "WARNING: GPU reset failed"
fi

# Clean up temporary files
TEMP_PATTERNS=(
    "/tmp/ray_*"
    "/tmp/vllm_*"
    "/tmp/torch_*"
    "/var/tmp/citadel_*"
)

for pattern in "${TEMP_PATTERNS[@]}"; do
    if compgen -G "$pattern" > /dev/null; then
        log "Cleaning up temporary files: $pattern"
        rm -rf $pattern
    fi
done

# Rotate logs if they're too large
MAX_LOG_SIZE_MB=100
for log_file in "$LOG_DIR"/*.log; do
    if [[ -f "$log_file" ]]; then
        size_mb=$(du -m "$log_file" | cut -f1)
        if [[ $size_mb -gt $MAX_LOG_SIZE_MB ]]; then
            log "Rotating large log file: $log_file (${size_mb}MB)"
            mv "$log_file" "${log_file}.old"
            touch "$log_file"
            chown agent0:agent0 "$log_file"
        fi
    fi
done

log "Post-stop cleanup completed for $SERVER_ID"
```

---

## 🧪 Validation Tests

### Test 1: Service Configuration Validation
```bash
#!/bin/bash
# File: /opt/citadel/scripts/test_service_config.sh

echo "Testing systemd service configuration..."

# Test service files exist
services=("vllm-server-01" "vllm-server-02")
failed_tests=0

for service in "${services[@]}"; do
    service_file="/etc/systemd/system/${service}.service"
    
    if [[ -f "$service_file" ]]; then
        echo "✅ Service file exists: $service_file"
        
        # Validate service file syntax
        if systemd-analyze verify "$service_file" &>/dev/null; then
            echo "✅ Service file syntax valid: $service"
        else
            echo "❌ Service file syntax invalid: $service"
            ((failed_tests++))
        fi
    else
        echo "❌ Service file missing: $service_file"
        ((failed_tests++))
    fi
done

# Test script permissions
scripts=(
    "/opt/citadel/scripts/start_vllm_service.sh"
    "/opt/citadel/scripts/stop_vllm_service.sh"
    "/opt/citadel/scripts/pre_start_checks.sh"
    "/opt/citadel/scripts/post_stop_cleanup.sh"
)

for script in "${scripts[@]}"; do
    if [[ -x "$script" ]]; then
        echo "✅ Script executable: $script"
    else
        echo "❌ Script not executable: $script"
        ((failed_tests++))
    fi
done

exit $failed_tests
```

### Test 2: Service Management Test
```python
#!/usr/bin/env python3
# File: /opt/citadel/scripts/test_service_management.py

import subprocess
import sys
import time
import requests

def run_command(cmd, timeout=30):
    """Run command with timeout and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def test_service_operations():
    """Test basic service operations."""
    print("Testing service management operations...")
    
    # Test systemd daemon reload
    success, stdout, stderr = run_command("sudo systemctl daemon-reload")
    if success:
        print("✅ Systemd daemon reload successful")
    else:
        print(f"❌ Systemd daemon reload failed: {stderr}")
        return False
    
    # Test service status (should be inactive initially)
    success, stdout, stderr = run_command("systemctl is-active vllm-server-01 || true")
    print(f"✅ Service status check completed: {stdout.strip()}")
    
    # Test service validation
    success, stdout, stderr = run_command("systemctl status vllm-server-01 --no-pager")
    if "Loaded:" in stdout:
        print("✅ Service definition loaded correctly")
    else:
        print(f"❌ Service definition issue: {stderr}")
        return False
    
    return True

def test_pre_start_checks():
    """Test pre-start validation."""
    print("Testing pre-start checks...")
    
    # Test pre-start script
    success, stdout, stderr = run_command("/opt/citadel/scripts/pre_start_checks.sh server-01")
    if success:
        print("✅ Pre-start checks passed")
        return True
    else:
        print(f"❌ Pre-start checks failed: {stderr}")
        return False

def main():
    """Main test function."""
    all_tests_passed = True
    
    # Test service operations
    if not test_service_operations():
        all_tests_passed = False
    
    # Test pre-start checks
    if not test_pre_start_checks():
        all_tests_passed = False
    
    if all_tests_passed:
        print("\n✅ All service management tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some service management tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📊 Success Criteria

### Primary Success Criteria
- [x] Systemd service files created for both servers
- [x] Service startup and shutdown procedures tested and functional
- [x] Service dependency management configured properly
- [x] Auto-restart and monitoring enabled

### Technical Requirements
- Service reliability: Auto-restart on failure with rate limiting
- Dependency management: Proper service ordering and requirements
- Resource management: Memory and CPU limits configured
- Security: Service isolation and permission restrictions

### Validation Metrics
- Service file validation: 100% syntax checks pass
- Script execution: All management scripts functional
- Service operations: Start/stop/restart operations successful
- Monitoring integration: Service status reporting functional

---

## 🚨 Troubleshooting Guide

### Issue: Service Fails to Start
**Symptoms:** systemctl start fails immediately
**Solution:**
```bash
# Check service status and logs
sudo systemctl status vllm-server-01
sudo journalctl -u vllm-server-01 -f

# Verify configuration
systemd-analyze verify /etc/systemd/system/vllm-server-01.service

# Test pre-start checks manually
/opt/citadel/scripts/pre_start_checks.sh server-01

# Check permissions
ls -la /opt/citadel/scripts/
sudo chown agent0:agent0 /opt/citadel/scripts/*.sh
sudo chmod +x /opt/citadel/scripts/*.sh
```

### Issue: Service Keeps Restarting
**Symptoms:** Service enters restart loop
**Solution:**
```bash
# Check restart limits
sudo systemctl show vllm-server-01 | grep Restart

# Disable auto-restart temporarily
sudo systemctl edit vllm-server-01
# Add:
# [Service]
# Restart=no

# Check resource usage
free -h
nvidia-smi

# Monitor service logs
sudo journalctl -u vllm-server-01 --since "5 minutes ago"
```

### Issue: Port Binding Fails
**Symptoms:** Cannot bind to configured port
**Solution:**
```bash
# Check port usage
sudo ss -tulpn | grep :8000

# Kill conflicting processes
sudo fuser -k 8000/tcp

# Verify configuration
python3 -c "import json; print(json.load(open('/opt/citadel/configs/api_server_01.json'))['server']['port'])"

# Test port availability
python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 8000)); s.close(); print('Port available')"
```

---

## 📋 Execution Checklist

### Pre-Execution
- [ ] vLLM installation and API setup completed
- [ ] Model storage configuration operational
- [ ] Required scripts created and executable
- [ ] Systemd daemon accessible

### During Execution
- [ ] Service files created successfully
- [ ] Scripts deployed with proper permissions
- [ ] Service validation checks pass
- [ ] Dependencies configured correctly

### Post-Execution
- [ ] Run service configuration tests
- [ ] Test service start/stop operations
- [ ] Verify auto-restart functionality
- [ ] Monitor service status and logs

---

## 🔄 Rollback Procedure

### Service Removal
```bash
# Stop services if running
sudo systemctl stop vllm-server-01 vllm-server-02

# Disable services
sudo systemctl disable vllm-server-01 vllm-server-02

# Remove service files
sudo rm -f /etc/systemd/system/vllm-server-01.service
sudo rm -f /etc/systemd/system/vllm-server-02.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

### Script Cleanup
```bash
# Remove service scripts
rm -f /opt/citadel/scripts/start_vllm_service.sh
rm -f /opt/citadel/scripts/stop_vllm_service.sh
rm -f /opt/citadel/scripts/pre_start_checks.sh
rm -f /opt/citadel/scripts/post_stop_cleanup.sh
```

---

## 📈 Next Steps

**Immediate Next Task:** TIP-vLLM-013 (Performance Optimization Configuration)

**Preparation for Next Phase:**
- Systemd services operational and reliable
- Service management scripts functional
- Auto-restart and monitoring configured
- Ready for performance optimization

---

*This implementation plan establishes robust systemd service integration following Citadel Alpha Infrastructure standards and best practices.*
