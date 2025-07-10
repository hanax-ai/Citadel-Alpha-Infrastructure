# 🐍 Task 1.2: Python Virtual Environment Creation

**Objective**: Create isolated Python environments for enterprise model deployment  
**Duration**: 30 minutes  
**Dependencies**: Task 1.1 Complete (Configuration Management)  
**Related Models**: DeepSeek-R1-Distill-Qwen-32B, Mixtral-8x7B-Instruct-v0.1, Yi-34B-Chat, openchat-3.5-0106  
**Success Criteria**: Virtual environments optimized for enterprise models, activated, dependencies isolated

## Prerequisites
- [ ] Task 1.1 completed successfully (Configuration system operational)
- [ ] Python 3.12 available on both servers
- [ ] SSH access to both servers with sudo privileges
- [ ] Configuration management system functional

## Step 1: Verify Python Environment - Both Servers
```bash
echo "🔍 Verifying Python environment on both servers..."

# Check Python version on server-01
echo "=== Python Environment - hx-llm-server-01 (192.168.10.29) ==="
ssh agent0@192.168.10.29 'python3 --version && which python3' && echo "✅ Python 01: AVAILABLE" || echo "❌ Python 01: MISSING"

# Check pip availability on server-01
ssh agent0@192.168.10.29 'pip3 --version' && echo "✅ Pip 01: AVAILABLE" || echo "❌ Pip 01: MISSING"

# Check Python version on server-02
echo "=== Python Environment - hx-llm-server-02 (192.168.10.28) ==="
ssh agent0@192.168.10.28 'python3 --version && which python3' && echo "✅ Python 02: AVAILABLE" || echo "❌ Python 02: MISSING"

# Check pip availability on server-02
ssh agent0@192.168.10.28 'pip3 --version' && echo "✅ Pip 02: AVAILABLE" || echo "❌ Pip 02: MISSING"

# Install venv if missing
ssh agent0@192.168.10.29 'python3 -m venv --help > /dev/null 2>&1' || ssh agent0@192.168.10.29 'sudo apt-get update && sudo apt-get install -y python3-venv'
ssh agent0@192.168.10.28 'python3 -m venv --help > /dev/null 2>&1' || ssh agent0@192.168.10.28 'sudo apt-get update && sudo apt-get install -y python3-venv'
```

## Step 2: Create Virtual Environment Structure - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Creating virtual environment structure on hx-llm-server-01..."

# Create virtual environments directory
ssh agent0@192.168.10.29 'mkdir -p /opt/citadel/venvs' && echo "✅ VEnv Directory 01: CREATED" || echo "❌ VEnv Directory 01: FAILED"

# Create main vLLM virtual environment
ssh agent0@192.168.10.29 'cd /opt/citadel/venvs && python3 -m venv citadel-vllm' && echo "✅ Main VEnv 01: CREATED" || echo "❌ Main VEnv 01: FAILED"

# Create admin/tools virtual environment
ssh agent0@192.168.10.29 'cd /opt/citadel/venvs && python3 -m venv citadel-admin' && echo "✅ Admin VEnv 01: CREATED" || echo "❌ Admin VEnv 01: FAILED"

# Verify virtual environment creation
ssh agent0@192.168.10.29 'ls -la /opt/citadel/venvs/' && echo "✅ VEnv Structure 01: VERIFIED" || echo "❌ VEnv Structure 01: FAILED"

# Test virtual environment activation
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python --version && deactivate' && echo "✅ VEnv Activation 01: FUNCTIONAL" || echo "❌ VEnv Activation 01: FAILED"
```

## Step 3: Upgrade pip and Install Base Dependencies - hx-llm-server-01
```bash
echo "🔍 Installing base dependencies in virtual environments on hx-llm-server-01..."

# Upgrade pip in main vLLM environment
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install --upgrade pip setuptools wheel' && echo "✅ Pip Upgrade VEnv 01: SUCCESS" || echo "❌ Pip Upgrade VEnv 01: FAILED"

# Install core dependencies in vLLM environment
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121' && echo "✅ PyTorch VEnv 01: INSTALLED" || echo "❌ PyTorch VEnv 01: FAILED"

# Install configuration dependencies in vLLM environment
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install pydantic pydantic-settings python-dotenv PyYAML' && echo "✅ Config Deps VEnv 01: INSTALLED" || echo "❌ Config Deps VEnv 01: FAILED"

# Upgrade pip in admin environment
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip install --upgrade pip setuptools wheel' && echo "✅ Pip Upgrade Admin 01: SUCCESS" || echo "❌ Pip Upgrade Admin 01: FAILED"

# Install admin tools in admin environment
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip install psutil GPUtil nvidia-ml-py3 requests fastapi uvicorn' && echo "✅ Admin Tools 01: INSTALLED" || echo "❌ Admin Tools 01: FAILED"
```

## Step 4: Create Virtual Environment Activation Scripts - hx-llm-server-01
```bash
echo "🔍 Creating virtual environment activation scripts on hx-llm-server-01..."

# Create vLLM environment activation script
ssh agent0@192.168.10.29 'cat > /opt/citadel/scripts/activate-vllm.sh << EOF
#!/bin/bash
# Activate Citadel vLLM Virtual Environment

echo "🐍 Activating Citadel vLLM Virtual Environment..."

# Source the virtual environment
source /opt/citadel/venvs/citadel-vllm/bin/activate

# Set environment variables
export CITADEL_ENV="vllm"
export CITADEL_VENV_PATH="/opt/citadel/venvs/citadel-vllm"
export PYTHONPATH="/opt/citadel/configs:\$PYTHONPATH"

# Load configuration
cd /opt/citadel/configs

echo "✅ Citadel vLLM environment activated"
echo "   Python: \$(which python)"
echo "   Version: \$(python --version)"
echo "   Environment: \$CITADEL_ENV"

# Optional: Start in config directory
# cd /opt/citadel/configs
EOF'

# Make script executable
ssh agent0@192.168.10.29 'chmod +x /opt/citadel/scripts/activate-vllm.sh' && echo "✅ vLLM Script 01: CREATED" || echo "❌ vLLM Script 01: FAILED"

# Create admin environment activation script
ssh agent0@192.168.10.29 'cat > /opt/citadel/scripts/activate-admin.sh << EOF
#!/bin/bash
# Activate Citadel Admin Virtual Environment

echo "🔧 Activating Citadel Admin Virtual Environment..."

# Source the virtual environment
source /opt/citadel/venvs/citadel-admin/bin/activate

# Set environment variables
export CITADEL_ENV="admin"
export CITADEL_VENV_PATH="/opt/citadel/venvs/citadel-admin"
export PYTHONPATH="/opt/citadel/configs:\$PYTHONPATH"

echo "✅ Citadel admin environment activated"
echo "   Python: \$(which python)"
echo "   Version: \$(python --version)"
echo "   Environment: \$CITADEL_ENV"

# Start in citadel root
cd /opt/citadel
EOF'

# Make script executable
ssh agent0@192.168.10.29 'chmod +x /opt/citadel/scripts/activate-admin.sh' && echo "✅ Admin Script 01: CREATED" || echo "❌ Admin Script 01: FAILED"

# Test activation scripts
ssh agent0@192.168.10.29 'source /opt/citadel/scripts/activate-vllm.sh && echo "vLLM environment test successful" && deactivate' && echo "✅ vLLM Script Test 01: SUCCESS" || echo "❌ vLLM Script Test 01: FAILED"
```

## Step 5: Install vLLM and Dependencies - hx-llm-server-01
```bash
echo "🔍 Installing vLLM in virtual environment on hx-llm-server-01..."

# Install vLLM with CUDA support
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install vllm' && echo "✅ vLLM Installation 01: SUCCESS" || echo "❌ vLLM Installation 01: FAILED"

# Install additional inference dependencies
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install transformers accelerate datasets tokenizers' && echo "✅ Inference Deps 01: INSTALLED" || echo "❌ Inference Deps 01: FAILED"

# Install API and web dependencies
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install fastapi uvicorn starlette aiofiles jinja2' && echo "✅ API Deps 01: INSTALLED" || echo "❌ API Deps 01: FAILED"

# Install monitoring and utilities
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install prometheus-client psutil GPUtil' && echo "✅ Monitoring Deps 01: INSTALLED" || echo "❌ Monitoring Deps 01: FAILED"

# Test vLLM installation
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm; print(f\"vLLM version: {vllm.__version__}\")"' && echo "✅ vLLM Test 01: SUCCESS" || echo "❌ vLLM Test 01: FAILED"
```

## Step 6: Create Requirements Files - hx-llm-server-01
```bash
echo "🔍 Creating requirements files on hx-llm-server-01..."

# Generate vLLM environment requirements
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip freeze > /opt/citadel/venvs/citadel-vllm-requirements.txt' && echo "✅ vLLM Requirements 01: GENERATED" || echo "❌ vLLM Requirements 01: FAILED"

# Generate admin environment requirements
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip freeze > /opt/citadel/venvs/citadel-admin-requirements.txt' && echo "✅ Admin Requirements 01: GENERATED" || echo "❌ Admin Requirements 01: FAILED"

# Create base requirements template (for new deployments)
ssh agent0@192.168.10.29 'cat > /opt/citadel/venvs/base-requirements.txt << EOF
# Base Citadel vLLM Requirements
# These are the core dependencies for Citadel vLLM deployment

# Core ML/AI Framework
torch>=2.1.0
torchvision>=0.16.0
torchaudio>=2.1.0

# vLLM and Inference
vllm>=0.2.0
transformers>=4.35.0
accelerate>=0.24.0
datasets>=2.14.0
tokenizers>=0.15.0

# Configuration Management
pydantic>=2.4.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
PyYAML>=6.0.0

# API and Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
starlette>=0.27.0
aiofiles>=23.2.0
jinja2>=3.1.0

# Monitoring and Utilities
prometheus-client>=0.19.0
psutil>=5.9.0
GPUtil>=1.4.0
nvidia-ml-py3>=7.352.0

# HTTP and Networking
requests>=2.31.0
httpx>=0.25.0

# Development and Testing (optional)
# pytest>=7.4.0
# pytest-asyncio>=0.21.0
# black>=23.0.0
# flake8>=6.0.0
EOF' && echo "✅ Base Requirements 01: CREATED" || echo "❌ Base Requirements 01: FAILED"
```

## Step 7: Replicate Environment on hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Replicating virtual environment setup on hx-llm-server-02..."

# Create virtual environments directory
ssh agent0@192.168.10.28 'mkdir -p /opt/citadel/venvs' && echo "✅ VEnv Directory 02: CREATED" || echo "❌ VEnv Directory 02: FAILED"

# Create virtual environments
ssh agent0@192.168.10.28 'cd /opt/citadel/venvs && python3 -m venv citadel-vllm && python3 -m venv citadel-admin' && echo "✅ VEnvs 02: CREATED" || echo "❌ VEnvs 02: FAILED"

# Copy requirements files from server-01
ssh agent0@192.168.10.29 'cd /opt/citadel/venvs && tar czf - *requirements.txt' | ssh agent0@192.168.10.28 'cd /opt/citadel/venvs && tar xzf -' && echo "✅ Requirements Copy 02: SUCCESS" || echo "❌ Requirements Copy 02: FAILED"

# Copy activation scripts from server-01
ssh agent0@192.168.10.29 'cd /opt/citadel/scripts && tar czf - activate-*.sh' | ssh agent0@192.168.10.28 'cd /opt/citadel/scripts && tar xzf -' && echo "✅ Scripts Copy 02: SUCCESS" || echo "❌ Scripts Copy 02: FAILED"

# Make scripts executable
ssh agent0@192.168.10.28 'chmod +x /opt/citadel/scripts/activate-*.sh' && echo "✅ Scripts Executable 02: SET" || echo "❌ Scripts Executable 02: FAILED"

# Upgrade pip in both environments
ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install --upgrade pip setuptools wheel' && echo "✅ Pip Upgrade vLLM 02: SUCCESS" || echo "❌ Pip Upgrade vLLM 02: FAILED"
ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip install --upgrade pip setuptools wheel' && echo "✅ Pip Upgrade Admin 02: SUCCESS" || echo "❌ Pip Upgrade Admin 02: FAILED"

# Install dependencies from requirements files
ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install -r /opt/citadel/venvs/base-requirements.txt' && echo "✅ vLLM Dependencies 02: INSTALLED" || echo "❌ vLLM Dependencies 02: FAILED"
ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip install psutil GPUtil nvidia-ml-py3 requests fastapi uvicorn' && echo "✅ Admin Dependencies 02: INSTALLED" || echo "❌ Admin Dependencies 02: FAILED"

# Test vLLM installation on server-02
ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm; print(f\"vLLM version: {vllm.__version__}\")"' && echo "✅ vLLM Test 02: SUCCESS" || echo "❌ vLLM Test 02: FAILED"
```

## Step 8: Create Environment Management Script - Both Servers
```bash
echo "🔍 Creating environment management script on both servers..."

# Create environment management script on server-01
ssh agent0@192.168.10.29 'cat > /opt/citadel/scripts/manage-env.sh << EOF
#!/bin/bash
# Citadel Virtual Environment Management Script

CITADEL_ROOT="/opt/citadel"
VENV_DIR="\$CITADEL_ROOT/venvs"

show_help() {
    echo "Citadel Virtual Environment Manager"
    echo "Usage: \$0 [COMMAND] [ENVIRONMENT]"
    echo ""
    echo "Commands:"
    echo "  activate [vllm|admin]    - Activate specified environment"
    echo "  status                   - Show environment status"
    echo "  list                     - List available environments"
    echo "  update [vllm|admin]      - Update environment dependencies"
    echo "  backup [vllm|admin]      - Backup environment requirements"
    echo "  help                     - Show this help"
    echo ""
    echo "Environments:"
    echo "  vllm    - Main vLLM inference environment"
    echo "  admin   - Administrative tools environment"
}

show_status() {
    echo "🔍 Citadel Virtual Environment Status"
    echo "======================================"
    
    for env in vllm admin; do
        env_path="\$VENV_DIR/citadel-\$env"
        if [ -d "\$env_path" ]; then
            echo "✅ citadel-\$env: AVAILABLE"
            echo "   Path: \$env_path"
            echo "   Python: \$env_path/bin/python"
            if [ -f "\$env_path/bin/python" ]; then
                version=\$(\$env_path/bin/python --version 2>&1)
                echo "   Version: \$version"
            fi
        else
            echo "❌ citadel-\$env: MISSING"
        fi
        echo ""
    done
}

list_environments() {
    echo "📋 Available Environments:"
    ls -la \$VENV_DIR/ 2>/dev/null | grep "^d" | awk "{print \"  - \" \$9}" | grep -v "^\s*-\s*\.$\|^\s*-\s*\.\.$"
}

update_environment() {
    local env=\$1
    if [ -z "\$env" ]; then
        echo "❌ Environment name required"
        return 1
    fi
    
    env_path="\$VENV_DIR/citadel-\$env"
    if [ ! -d "\$env_path" ]; then
        echo "❌ Environment citadel-\$env not found"
        return 1
    fi
    
    echo "🔄 Updating citadel-\$env environment..."
    source \$env_path/bin/activate
    pip install --upgrade pip setuptools wheel
    
    if [ "\$env" = "vllm" ]; then
        pip install --upgrade -r \$VENV_DIR/base-requirements.txt
    elif [ "\$env" = "admin" ]; then
        pip install --upgrade psutil GPUtil nvidia-ml-py3 requests fastapi uvicorn
    fi
    
    deactivate
    echo "✅ Environment updated successfully"
}

backup_requirements() {
    local env=\$1
    if [ -z "\$env" ]; then
        echo "❌ Environment name required"
        return 1
    fi
    
    env_path="\$VENV_DIR/citadel-\$env"
    if [ ! -d "\$env_path" ]; then
        echo "❌ Environment citadel-\$env not found"
        return 1
    fi
    
    timestamp=\$(date +"%Y%m%d_%H%M%S")
    backup_file="\$VENV_DIR/citadel-\$env-requirements-\$timestamp.txt"
    
    echo "💾 Backing up citadel-\$env requirements..."
    source \$env_path/bin/activate
    pip freeze > \$backup_file
    deactivate
    
    echo "✅ Requirements backed up to: \$backup_file"
}

# Main command processing
case "\$1" in
    "activate")
        if [ -z "\$2" ]; then
            echo "❌ Environment name required"
            echo "Available: vllm, admin"
            exit 1
        fi
        source \$CITADEL_ROOT/scripts/activate-\$2.sh
        ;;
    "status")
        show_status
        ;;
    "list")
        list_environments
        ;;
    "update")
        update_environment \$2
        ;;
    "backup")
        backup_requirements \$2
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: \$1"
        show_help
        exit 1
        ;;
esac
EOF'

# Make script executable
ssh agent0@192.168.10.29 'chmod +x /opt/citadel/scripts/manage-env.sh' && echo "✅ Env Manager 01: CREATED" || echo "❌ Env Manager 01: FAILED"

# Copy to server-02
ssh agent0@192.168.10.29 'cat /opt/citadel/scripts/manage-env.sh' | ssh agent0@192.168.10.28 'cat > /opt/citadel/scripts/manage-env.sh && chmod +x /opt/citadel/scripts/manage-env.sh' && echo "✅ Env Manager 02: CREATED" || echo "❌ Env Manager 02: FAILED"

# Test management script on both servers
ssh agent0@192.168.10.29 '/opt/citadel/scripts/manage-env.sh status' && echo "✅ Env Manager Test 01: SUCCESS" || echo "❌ Env Manager Test 01: FAILED"
ssh agent0@192.168.10.28 '/opt/citadel/scripts/manage-env.sh status' && echo "✅ Env Manager Test 02: SUCCESS" || echo "❌ Env Manager Test 02: FAILED"
```

## Step 9: Virtual Environment Validation and Report
```bash
echo "📊 Generating virtual environment deployment report..."

cat > /tmp/virtual-environment-report.md << EOF
# Virtual Environment Deployment Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **VEnv Directory**: $(ssh agent0@192.168.10.29 'test -d /opt/citadel/venvs && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Environment**: $(ssh agent0@192.168.10.29 'test -d /opt/citadel/venvs/citadel-vllm && echo "✅ CREATED" || echo "❌ MISSING"')
- **Admin Environment**: $(ssh agent0@192.168.10.29 'test -d /opt/citadel/venvs/citadel-admin && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Installation**: $(ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm" 2>/dev/null && echo "✅ INSTALLED" || echo "❌ MISSING"')
- **Activation Scripts**: $(ssh agent0@192.168.10.29 'test -x /opt/citadel/scripts/activate-vllm.sh && echo "✅ CREATED" || echo "❌ MISSING"')
- **Management Script**: $(ssh agent0@192.168.10.29 'test -x /opt/citadel/scripts/manage-env.sh && echo "✅ CREATED" || echo "❌ MISSING"')

## hx-llm-server-02 (192.168.10.28)
- **VEnv Directory**: $(ssh agent0@192.168.10.28 'test -d /opt/citadel/venvs && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Environment**: $(ssh agent0@192.168.10.28 'test -d /opt/citadel/venvs/citadel-vllm && echo "✅ CREATED" || echo "❌ MISSING"')
- **Admin Environment**: $(ssh agent0@192.168.10.28 'test -d /opt/citadel/venvs/citadel-admin && echo "✅ CREATED" || echo "❌ MISSING"')
- **vLLM Installation**: $(ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm" 2>/dev/null && echo "✅ INSTALLED" || echo "❌ MISSING"')
- **Activation Scripts**: $(ssh agent0@192.168.10.28 'test -x /opt/citadel/scripts/activate-vllm.sh && echo "✅ CREATED" || echo "❌ MISSING"')
- **Management Script**: $(ssh agent0@192.168.10.28 'test -x /opt/citadel/scripts/manage-env.sh && echo "✅ CREATED" || echo "❌ MISSING"')

## Environment Details
### vLLM Environment (Server-01)
$(ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && echo "Python: $(python --version)" && echo "vLLM: $(python -c "import vllm; print(vllm.__version__)" 2>/dev/null || echo "Not installed")" && deactivate' 2>/dev/null)

### vLLM Environment (Server-02)
$(ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && echo "Python: $(python --version)" && echo "vLLM: $(python -c "import vllm; print(vllm.__version__)" 2>/dev/null || echo "Not installed")" && deactivate' 2>/dev/null)

## Features Implemented
- **Isolated Environments**: ✅ Created separate vLLM and admin environments
- **vLLM Installation**: ✅ Full vLLM with CUDA support
- **Dependency Management**: ✅ Requirements files generated
- **Activation Scripts**: ✅ Easy environment activation
- **Management Tools**: ✅ Environment management script
- **Cross-Server Sync**: ✅ Consistent setup on both servers

## Environment Tests
- Server-01 vLLM Import: $(ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm; print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-02 vLLM Import: $(ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import vllm; print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-01 Config Import: $(ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && cd /opt/citadel/configs && python -c "from vllm_settings import load_citadel_settings; print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-02 Config Import: $(ssh agent0@192.168.10.28 'source /opt/citadel/venvs/citadel-vllm/bin/activate && cd /opt/citadel/configs && python -c "from vllm_settings import load_citadel_settings; print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
EOF

echo "📄 Virtual environment report saved to: /tmp/virtual-environment-report.md"
cat /tmp/virtual-environment-report.md
```

## Validation
Calculate virtual environment readiness:
- Verify virtual environments created on both servers
- Confirm vLLM successfully installed
- Test environment activation and scripts
- Validate dependency management system
- Check cross-server consistency
- If all components functional → Task SUCCESS

## Troubleshooting

**Virtual Environment Creation Issues:**
```bash
# Install python3-venv if missing
ssh agent0@192.168.10.29 'sudo apt-get update && sudo apt-get install -y python3-venv python3-dev'

# Check disk space
ssh agent0@192.168.10.29 'df -h /opt/citadel/'

# Recreate environment if corrupted
ssh agent0@192.168.10.29 'rm -rf /opt/citadel/venvs/citadel-vllm && python3 -m venv /opt/citadel/venvs/citadel-vllm'
```

**vLLM Installation Issues:**
```bash
# Install with specific CUDA version
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121'

# Check CUDA availability
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && python -c "import torch; print(f\"CUDA Available: {torch.cuda.is_available()}\")"'

# Install from wheel if needed
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install --pre vllm'
```

**Dependency Conflicts:**
```bash
# Create fresh environment
ssh agent0@192.168.10.29 'rm -rf /opt/citadel/venvs/citadel-vllm && python3 -m venv /opt/citadel/venvs/citadel-vllm'

# Install minimal dependencies first
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip install torch && pip install vllm'

# Check for conflicts
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-vllm/bin/activate && pip check'
```

## Post-Task Checklist
- [ ] Virtual environments created on both servers
- [ ] vLLM successfully installed in both environments
- [ ] Configuration management accessible from environments
- [ ] Activation scripts functional
- [ ] Environment management tools deployed
- [ ] Requirements files generated and synchronized
- [ ] Cross-server consistency validated

## Result Documentation
Document results in format:
```
Task 1.2 Results:
- hx-llm-server-01: VEnv [CREATED/FAILED], vLLM [INSTALLED/FAILED], Scripts [FUNCTIONAL/FAILED], Management [OPERATIONAL/FAILED]
- hx-llm-server-02: VEnv [CREATED/FAILED], vLLM [INSTALLED/FAILED], Scripts [FUNCTIONAL/FAILED], Management [OPERATIONAL/FAILED]
- Virtual Environment System: [OPERATIONAL/NEEDS_ATTENTION]
- Overall: [X/8] components functional ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 1.3: Logging and Monitoring System Setup
