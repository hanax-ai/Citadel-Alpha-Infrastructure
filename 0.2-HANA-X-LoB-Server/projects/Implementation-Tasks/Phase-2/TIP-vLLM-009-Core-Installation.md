# 🚀 Task Implementation Plan (TIP-vLLM-009)

## Title: vLLM Core Installation (Phase 2, Task 2.1)

**Document ID:** TIP-vLLM-009  
**Version:** 1.0  
**Date:** 2025-01-10  
**Phase:** 2 - vLLM Installation & Configuration  
**Task Reference:** Task 2.1 from TL-vLLM-001  

---

## 🎯 Objective

Install latest stable vLLM version with all required dependencies on both hx-llm-server-01 (192.168.10.29) and hx-llm-server-02 (192.168.10.28).

---

## 📋 Prerequisites

**Dependencies:**
- Phase 1 Complete (Tasks 1.1-1.6)
- Python 3.12 virtual environments functional
- PyTorch with CUDA 12.4 support installed
- Configuration management system deployed

**Required Resources:**
- SSH access to both servers
- Active internet connection for package downloads
- Virtual environment activation capability

---

## 🛠️ Implementation Steps

### Step 1: Environment Validation
**Duration:** 5 minutes

```bash
# Verify virtual environment and Python version
source /opt/citadel/venv/bin/activate
python --version  # Should be 3.12.x
pip --version

# Verify PyTorch CUDA support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA devices: {torch.cuda.device_count()}')"
```

**Expected Output:**
- Python 3.12.x confirmed
- CUDA available: True
- CUDA devices: 2 (for each server)

### Step 2: vLLM Installation
**Duration:** 35 minutes

```bash
# Install vLLM from PyPI with CUDA support
pip install vllm

# Verify installation
pip show vllm

# Alternative: Install from source if needed
# git clone https://github.com/vllm-project/vllm.git
# cd vllm
# pip install -e .
```

**Key Components Installed:**
- vLLM core engine
- Ray backend for distributed inference
- FastAPI integration for API serving
- Transformers integration
- Required CUDA libraries

### Step 3: Dependency Resolution
**Duration:** 5 minutes

```bash
# Verify all vLLM dependencies
pip check

# Install additional requirements if needed
pip install ray>=2.5.0
pip install fastapi>=0.100.0
pip install uvicorn[standard]
pip install transformers>=4.35.0
```

**Critical Dependencies:**
- Ray: Distributed computing framework
- FastAPI: Web framework for API serving
- Transformers: Model handling and tokenization
- Uvicorn: ASGI server

### Step 4: Installation Verification
**Duration:** 5 minutes

```bash
# Test vLLM import
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"

# Test core components
python -c "from vllm import LLM, SamplingParams; print('vLLM core import successful')"
python -c "from vllm.entrypoints.api_server import app; print('API server import successful')"
```

**Validation Checks:**
- ✅ vLLM imports without errors
- ✅ Core classes accessible
- ✅ API server components functional
- ✅ Version information available

---

## 🔧 Configuration Files

### vLLM Installation Configuration
**File:** `/opt/citadel/configs/vllm_install.json`

```json
{
  "installation": {
    "method": "pypi",
    "version": "latest",
    "extras": ["cuda"],
    "verify_gpu": true
  },
  "dependencies": {
    "ray": ">=2.5.0",
    "fastapi": ">=0.100.0",
    "uvicorn": ">=0.18.0",
    "transformers": ">=4.35.0"
  },
  "validation": {
    "import_tests": [
      "vllm",
      "vllm.LLM",
      "vllm.SamplingParams",
      "vllm.entrypoints.api_server"
    ],
    "cuda_required": true,
    "min_gpu_count": 2
  }
}
```

### Installation Script
**File:** `/opt/citadel/scripts/install_vllm.sh`

```bash
#!/bin/bash
# vLLM Installation Script for Citadel Alpha Infrastructure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/opt/citadel/configs"
LOG_FILE="/opt/citadel/logs/vllm_install.log"

# Source configuration
source /opt/citadel/venv/bin/activate

echo "Starting vLLM installation..." | tee -a "$LOG_FILE"

# Install vLLM
echo "Installing vLLM..." | tee -a "$LOG_FILE"
pip install vllm 2>&1 | tee -a "$LOG_FILE"

# Install additional dependencies
echo "Installing additional dependencies..." | tee -a "$LOG_FILE"
pip install ray>=2.5.0 fastapi>=0.100.0 uvicorn[standard] transformers>=4.35.0 2>&1 | tee -a "$LOG_FILE"

# Verify installation
echo "Verifying installation..." | tee -a "$LOG_FILE"
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')" 2>&1 | tee -a "$LOG_FILE"
python -c "from vllm import LLM, SamplingParams; print('Core imports successful')" 2>&1 | tee -a "$LOG_FILE"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Devices: {torch.cuda.device_count()}')" 2>&1 | tee -a "$LOG_FILE"

echo "vLLM installation completed successfully!" | tee -a "$LOG_FILE"
```

---

## 🧪 Validation Tests

### Test 1: Import Validation
```python
#!/usr/bin/env python3
# File: /opt/citadel/scripts/test_vllm_imports.py

import sys
import traceback

def test_imports():
    """Test all critical vLLM imports."""
    test_imports = [
        'vllm',
        'vllm.LLM',
        'vllm.SamplingParams',
        'vllm.entrypoints.api_server',
        'vllm.engine.arg_utils',
        'vllm.model_executor.models'
    ]
    
    failed_imports = []
    
    for import_name in test_imports:
        try:
            __import__(import_name)
            print(f"✅ {import_name}")
        except ImportError as e:
            print(f"❌ {import_name}: {e}")
            failed_imports.append(import_name)
    
    return len(failed_imports) == 0

if __name__ == "__main__":
    if test_imports():
        print("All vLLM imports successful!")
        sys.exit(0)
    else:
        print("Some imports failed!")
        sys.exit(1)
```

### Test 2: Version Compatibility
```python
#!/usr/bin/env python3
# File: /opt/citadel/scripts/test_vllm_compatibility.py

import vllm
import torch
import transformers
import ray

def test_compatibility():
    """Test version compatibility of all components."""
    print(f"vLLM version: {vllm.__version__}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Transformers version: {transformers.__version__}")
    print(f"Ray version: {ray.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"GPU count: {torch.cuda.device_count()}")
    
    # Verify minimum requirements
    assert torch.cuda.is_available(), "CUDA not available"
    assert torch.cuda.device_count() >= 2, "Insufficient GPU count"
    
    print("✅ All compatibility checks passed!")

if __name__ == "__main__":
    test_compatibility()
```

---

## 📊 Success Criteria

### Primary Success Criteria
- [x] vLLM installed from PyPI or source
- [x] All vLLM dependencies resolved without conflicts
- [x] Installation verified with successful imports
- [x] Version compatibility confirmed with PyTorch CUDA

### Technical Requirements
- vLLM version: Latest stable (≥0.2.0)
- PyTorch compatibility: CUDA 12.4 support
- GPU detection: 2x NVIDIA RTX 4070 Ti SUPER per server
- Memory requirements: <50GB per installation

### Validation Metrics
- Import test success rate: 100%
- Dependency resolution: No conflicts
- GPU detection: 2 devices per server
- Installation time: <45 minutes

---

## 🚨 Troubleshooting Guide

### Issue: CUDA Version Mismatch
**Symptoms:** vLLM imports but CUDA not detected
**Solution:**
```bash
# Check CUDA version compatibility
nvidia-smi
nvcc --version
pip show torch | grep Version

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Issue: Memory Error During Installation
**Symptoms:** OOM error during pip install
**Solution:**
```bash
# Use no-cache-dir to reduce memory usage
pip install --no-cache-dir vllm

# Install with limited parallel builds
export MAX_JOBS=2
pip install vllm
```

### Issue: Import Errors After Installation
**Symptoms:** ModuleNotFoundError for vllm components
**Solution:**
```bash
# Verify virtual environment activation
which python
which pip

# Reinstall in development mode
pip uninstall vllm
pip install -e /path/to/vllm/source
```

---

## 📋 Execution Checklist

### Pre-Execution
- [ ] Virtual environment activated
- [ ] PyTorch CUDA support verified
- [ ] Internet connectivity confirmed
- [ ] Sufficient disk space available (>10GB)

### During Execution
- [ ] Monitor installation progress
- [ ] Check for dependency conflicts
- [ ] Verify GPU detection
- [ ] Test core imports

### Post-Execution
- [ ] Run validation test suite
- [ ] Document installed versions
- [ ] Update configuration files
- [ ] Prepare for next phase task

---

## 🔄 Rollback Procedure

### Emergency Rollback
```bash
# Create backup before installation
cp -r /opt/citadel/venv /opt/citadel/venv.backup

# Rollback if needed
rm -rf /opt/citadel/venv
mv /opt/citadel/venv.backup /opt/citadel/venv
```

### Partial Rollback
```bash
# Remove only vLLM
pip uninstall vllm -y

# Remove related packages
pip uninstall ray fastapi uvicorn -y
```

---

## 📈 Next Steps

**Immediate Next Task:** TIP-vLLM-010 (OpenAI-Compatible API Setup)

**Preparation for Next Phase:**
- vLLM core functionality validated
- API server components ready
- Configuration framework established
- GPU acceleration confirmed

---

*This implementation plan ensures robust vLLM core installation following Citadel Alpha Infrastructure standards and best practices.*
