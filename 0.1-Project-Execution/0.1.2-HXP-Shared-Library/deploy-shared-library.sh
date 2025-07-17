#!/bin/bash

# HANA-X Vector Database Shared Library Deployment Script
# Deploys the shared library to the Vector Database Server (192.168.10.30)

set -e  # Exit on any error

echo "=== HANA-X VECTOR DATABASE SHARED LIBRARY DEPLOYMENT ==="
echo "Target Server: Vector Database Server (192.168.10.30)"
echo "Date: $(date)"
echo ""

# Configuration
VECTOR_DB_SERVER="192.168.10.30"
SHARED_LIB_SOURCE="/home/agent0/Citadel-Alpha-Infrastructure/0.1-Project-Execution/0.1.2-HXP-Shared-Library"
DEPLOYMENT_TARGET="/opt/qdrant/shared-library"
PYTHON_ENV="/opt/qdrant/venv"
SERVICE_USER="qdrant"

# Deployment options
DEPLOYMENT_MODE="${1:-local}"  # local, remote, or package

echo "=== 1. PRE-DEPLOYMENT VALIDATION ==="

# Validate source directory
if [ ! -d "$SHARED_LIB_SOURCE" ]; then
    echo "❌ ERROR: Shared library source directory not found: $SHARED_LIB_SOURCE"
    exit 1
fi

# Validate shared library structure
required_files=(
    "hana_x_vector/__init__.py"
    "requirements.txt"
    "README.md"
    "setup.py"
)

echo "Validating shared library structure..."
for file in "${required_files[@]}"; do
    if [ -f "$SHARED_LIB_SOURCE/$file" ]; then
        echo "✅ $file - Present"
    else
        echo "❌ $file - Missing"
        if [ "$file" = "setup.py" ]; then
            echo "Creating setup.py..."
            cat > "$SHARED_LIB_SOURCE/setup.py" << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hana-x-vector",
    version="1.0.0",
    author="X-AI Infrastructure Engineer",
    author_email="infrastructure@hanax-ai.com",
    description="HANA-X Vector Database Shared Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hana-x-vector=hana_x_vector.cli:main",
        ],
    },
)
EOF
            echo "✅ setup.py - Created"
        fi
    fi
done

# Function definitions
function deploy_local() {
    echo "=== LOCAL DEPLOYMENT ==="
    
    # Create deployment directory
    echo "Creating deployment directory..."
    sudo mkdir -p "$DEPLOYMENT_TARGET"
    
    # Copy shared library
    echo "Copying shared library..."
    sudo cp -r "$SHARED_LIB_SOURCE"/* "$DEPLOYMENT_TARGET/"
    
    # Create Python virtual environment
    echo "Creating Python virtual environment..."
    sudo python3.12 -m venv "$PYTHON_ENV"
    
    # Set ownership
    echo "Setting ownership..."
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$DEPLOYMENT_TARGET"
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$PYTHON_ENV"
    
    # Install shared library
    echo "Installing shared library..."
    sudo -u "$SERVICE_USER" "$PYTHON_ENV/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$PYTHON_ENV/bin/pip" install -e "$DEPLOYMENT_TARGET"
    
    # Validate installation
    validate_installation
}

function deploy_remote() {
    echo "=== REMOTE DEPLOYMENT ==="
    
    # Check SSH connectivity
    echo "Testing SSH connectivity to $VECTOR_DB_SERVER..."
    if ! ssh -o ConnectTimeout=5 "$VECTOR_DB_SERVER" "echo 'SSH connection successful'"; then
        echo "❌ ERROR: Cannot connect to $VECTOR_DB_SERVER via SSH"
        exit 1
    fi
    
    # Create remote deployment directory
    echo "Creating remote deployment directory..."
    ssh "$VECTOR_DB_SERVER" "sudo mkdir -p $DEPLOYMENT_TARGET"
    
    # Copy shared library to remote server
    echo "Copying shared library to remote server..."
    scp -r "$SHARED_LIB_SOURCE"/* "$VECTOR_DB_SERVER:$DEPLOYMENT_TARGET/"
    
    # Remote installation script
    echo "Executing remote installation..."
    ssh "$VECTOR_DB_SERVER" << 'REMOTE_SCRIPT'
        # Create Python virtual environment
        sudo python3.12 -m venv /opt/qdrant/venv
        
        # Set ownership
        sudo chown -R qdrant:qdrant /opt/qdrant/shared-library
        sudo chown -R qdrant:qdrant /opt/qdrant/venv
        
        # Install shared library
        sudo -u qdrant /opt/qdrant/venv/bin/pip install --upgrade pip
        sudo -u qdrant /opt/qdrant/venv/bin/pip install -e /opt/qdrant/shared-library
        
        # Validate installation
        sudo -u qdrant /opt/qdrant/venv/bin/python -c "import hana_x_vector; print('✅ Shared library imported successfully')"
REMOTE_SCRIPT
    
    echo "✅ Remote deployment completed"
}

function deploy_package() {
    echo "=== PACKAGE DEPLOYMENT ==="
    
    # Create distribution directory
    DIST_DIR="$SHARED_LIB_SOURCE/dist"
    mkdir -p "$DIST_DIR"
    
    # Build distribution package
    echo "Building distribution package..."
    cd "$SHARED_LIB_SOURCE"
    python setup.py sdist bdist_wheel
    
    # Create deployment archive
    echo "Creating deployment archive..."
    tar -czf "$DIST_DIR/hana-x-vector-deployment.tar.gz" \
        -C "$SHARED_LIB_SOURCE" \
        hana_x_vector/ \
        requirements.txt \
        README.md \
        setup.py \
        VALIDATION_SUMMARY.md
    
    echo "✅ Package created: $DIST_DIR/hana-x-vector-deployment.tar.gz"
    echo "✅ Wheel package: $DIST_DIR/hana_x_vector-1.0.0-py3-none-any.whl"
    
    # Create installation instructions
    cat > "$DIST_DIR/INSTALL.md" << 'EOF'
# HANA-X Vector Database Shared Library Installation

## Installation on Vector Database Server (192.168.10.30)

### Method 1: From Wheel Package
```bash
# Copy wheel to server
scp dist/hana_x_vector-1.0.0-py3-none-any.whl 192.168.10.30:/tmp/

# Install on server
ssh 192.168.10.30
sudo -u qdrant /opt/qdrant/venv/bin/pip install /tmp/hana_x_vector-1.0.0-py3-none-any.whl
```

### Method 2: From Source Archive
```bash
# Copy and extract archive
scp dist/hana-x-vector-deployment.tar.gz 192.168.10.30:/tmp/
ssh 192.168.10.30
sudo mkdir -p /opt/qdrant/shared-library
sudo tar -xzf /tmp/hana-x-vector-deployment.tar.gz -C /opt/qdrant/shared-library
sudo chown -R qdrant:qdrant /opt/qdrant/shared-library
sudo -u qdrant /opt/qdrant/venv/bin/pip install -e /opt/qdrant/shared-library
```

### Validation
```bash
sudo -u qdrant /opt/qdrant/venv/bin/python -c "import hana_x_vector; print('Installation successful')"
```
EOF
    
    echo "✅ Installation instructions: $DIST_DIR/INSTALL.md"
}

function validate_installation() {
    echo ""
    echo "=== 3. INSTALLATION VALIDATION ==="
    
    # Test Python import
    echo "Testing Python import..."
    if sudo -u "$SERVICE_USER" "$PYTHON_ENV/bin/python" -c "import hana_x_vector; print('✅ hana_x_vector imported successfully')"; then
        echo "✅ Core library import successful"
    else
        echo "❌ Core library import failed"
        exit 1
    fi
    
    # Test individual components
    components=(
        "hana_x_vector.gateway"
        "hana_x_vector.vector_ops"
        "hana_x_vector.qdrant"
        "hana_x_vector.external_models"
        "hana_x_vector.monitoring"
        "hana_x_vector.utils"
        "hana_x_vector.schemas"
    )
    
    echo "Testing component imports..."
    for component in "${components[@]}"; do
        if sudo -u "$SERVICE_USER" "$PYTHON_ENV/bin/python" -c "import $component; print('✅ $component')"; then
            echo "✅ $component - OK"
        else
            echo "❌ $component - FAILED"
        fi
    done
    
    # Test configuration
    echo "Testing configuration..."
    sudo -u "$SERVICE_USER" "$PYTHON_ENV/bin/python" -c "
from hana_x_vector.utils import ConfigManager
config = ConfigManager()
print('✅ Configuration manager initialized')
print(f'✅ Qdrant URL: {config.get_qdrant_url()}')
print(f'✅ Redis URL: {config.get_redis_url()}')
"
    
    echo ""
    echo "=== 4. POST-DEPLOYMENT ACTIONS ==="
    
    # Create systemd service environment file
    echo "Creating systemd environment file..."
    sudo tee /opt/qdrant/shared-library.env << 'EOF'
# HANA-X Vector Database Shared Library Environment
PYTHONPATH=/opt/qdrant/shared-library
HANA_X_QDRANT_URL=http://localhost:6333
HANA_X_REDIS_URL=redis://192.168.10.35:6379
HANA_X_POSTGRES_URL=postgresql://citadel_admin@192.168.10.35:5432/citadel_ai
HANA_X_LOG_LEVEL=INFO
HANA_X_ENVIRONMENT=production
EOF
    
    # Update systemd services to use shared library
    echo "Updating systemd service configuration..."
    sudo tee /etc/systemd/system/qdrant-gateway.service << 'EOF'
[Unit]
Description=HANA-X Vector Database API Gateway
After=network.target qdrant.service
Requires=qdrant.service

[Service]
Type=simple
User=qdrant
Group=qdrant
WorkingDirectory=/opt/qdrant
Environment=PYTHONPATH=/opt/qdrant/shared-library
EnvironmentFile=/opt/qdrant/shared-library.env
ExecStart=/opt/qdrant/venv/bin/python -m hana_x_vector.gateway.api_gateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    echo "✅ Systemd service configuration updated"
    echo ""
    echo "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
    echo "Shared library deployed to: $DEPLOYMENT_TARGET"
    echo "Python environment: $PYTHON_ENV"
    echo "Service user: $SERVICE_USER"
    echo ""
    echo "Next steps:"
    echo "1. Start Qdrant service: sudo systemctl start qdrant"
    echo "2. Start API Gateway: sudo systemctl start qdrant-gateway"
    echo "3. Verify services: sudo systemctl status qdrant qdrant-gateway"
    echo "4. Test API endpoints: curl http://localhost:8000/health"
}

echo ""
echo "=== 2. DEPLOYMENT MODE: $DEPLOYMENT_MODE ==="

# Execute deployment based on mode
case $DEPLOYMENT_MODE in
    "local")
        echo "Local deployment mode - Installing on current server"
        deploy_local
        ;;
    "remote")
        echo "Remote deployment mode - Deploying to Vector Database Server"
        deploy_remote
        ;;
    "package")
        echo "Package deployment mode - Creating distribution package"
        deploy_package
        ;;
    *)
        echo "❌ ERROR: Invalid deployment mode. Use: local, remote, or package"
        exit 1
        ;;
esac

echo ""
echo "=== DEPLOYMENT SUMMARY ==="
echo "Mode: $DEPLOYMENT_MODE"
echo "Status: ✅ COMPLETED"
echo "Date: $(date)"
echo ""
echo "For troubleshooting, check:"
echo "- Deployment logs: /var/log/qdrant/"
echo "- Service status: systemctl status qdrant-gateway"
echo "- Python environment: $PYTHON_ENV/bin/python"
