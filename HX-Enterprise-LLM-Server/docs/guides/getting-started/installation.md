# Installation Guide - HXP-Enterprise LLM Server

[![Installation Guide](https://img.shields.io/badge/Installation%20Guide-Complete-brightgreen.svg)](https://github.com/manus-ai/hxp-enterprise-llm)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/manus-ai/hxp-enterprise-llm)

Complete installation guide for the HXP-Enterprise LLM Server modular architecture library. This guide covers system requirements, installation methods, configuration setup, and post-installation verification.

## 📋 Prerequisites

### **System Requirements**

#### **Hardware Requirements**
| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 8 cores | 16 cores | 32+ cores |
| **RAM** | 32 GB | 64 GB | 128+ GB |
| **Storage** | 500 GB SSD | 1 TB NVMe | 2+ TB NVMe |
| **Network** | 1 Gbps | 10 Gbps | 25+ Gbps |
| **GPU** | Optional | NVIDIA RTX 4090 | NVIDIA H100 |

#### **Software Requirements**
- **Operating System**: Ubuntu 24.04 LTS (recommended)
- **Python**: 3.11+ (required)
- **Docker**: 24.0+ (optional, for containerized deployment)
- **Git**: 2.40+ (required for source installation)

#### **System Dependencies**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    cmake \
    ninja-build
```

### **Network Requirements**
- **Port 8000**: API Gateway (external access)
- **Port 11400**: Mixtral-8x7B Service
- **Port 11401**: Hermes-2 Service
- **Port 11402**: OpenChat-3.5 Service
- **Port 11403**: Phi-3-Mini Service
- **Port 9090**: Monitoring (Prometheus)
- **Port 3000**: Monitoring (Grafana)

### **External Service Dependencies**
- **PostgreSQL Database**: 192.168.10.35:5433
- **Vector Database (Qdrant)**: 192.168.10.30:6333
- **Cache (Redis)**: 192.168.10.37:6379

## 🚀 Installation Methods

### **Method 1: Automated Installation (Recommended)**

#### **Quick Install Script**
```bash
# Download and run the automated installation script
curl -fsSL https://raw.githubusercontent.com/manus-ai/hxp-enterprise-llm/main/install.sh | bash

# Or download and run manually
wget https://raw.githubusercontent.com/manus-ai/hxp-enterprise-llm/main/install.sh
chmod +x install.sh
./install.sh
```

#### **Installation Options**
```bash
# Install with specific options
./install.sh \
    --environment production \
    --install-path /opt/citadel/hxp-enterprise-llm \
    --enable-gpu \
    --enable-monitoring \
    --enable-security
```

### **Method 2: Manual Installation**

#### **Step 1: Clone Repository**
```bash
# Clone the repository
git clone https://github.com/manus-ai/hxp-enterprise-llm.git
cd hxp-enterprise-llm

# Checkout the latest release
git checkout v3.0.0
```

#### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### **Step 3: Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### **Step 4: Install AI Model Dependencies**
```bash
# Install vLLM for AI model serving
pip install vllm==0.3.2

# Install CUDA dependencies (if using GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### **Method 3: Docker Installation**

#### **Docker Compose Setup**
```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  hxp-enterprise-llm:
    image: manus-ai/hxp-enterprise-llm:3.0.0
    container_name: hxp-enterprise-llm
    ports:
      - "8000:8000"      # API Gateway
      - "11400:11400"    # Mixtral Service
      - "11401:11401"    # Hermes Service
      - "11402:11402"    # OpenChat Service
      - "11403:11403"    # Phi-3 Service
      - "9090:9090"      # Prometheus
      - "3000:3000"      # Grafana
    volumes:
      - ./config:/opt/citadel/hxp-enterprise-llm/config
      - ./models:/opt/citadel/hxp-enterprise-llm/models
      - ./logs:/opt/citadel/hxp-enterprise-llm/logs
    environment:
      - HXP_ENVIRONMENT=production
      - HXP_ENABLE_GPU=true
      - HXP_ENABLE_MONITORING=true
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
EOF

# Start services
docker-compose up -d
```

## ⚙️ Configuration Setup

### **Step 1: Create Configuration Directory**
```bash
# Create configuration directory
sudo mkdir -p /opt/citadel/hxp-enterprise-llm/config
sudo chown -R $USER:$USER /opt/citadel/hxp-enterprise-llm/config
```

### **Step 2: Generate Configuration Files**
```bash
# Generate base configuration
python -m hxp_enterprise_llm.config.generate_config \
    --environment production \
    --output /opt/citadel/hxp-enterprise-llm/config/base.yaml

# Generate environment-specific configurations
python -m hxp_enterprise_llm.config.generate_config \
    --environment development \
    --output /opt/citadel/hxp-enterprise-llm/config/development.yaml

python -m hxp_enterprise_llm.config.generate_config \
    --environment production \
    --output /opt/citadel/hxp-enterprise-llm/config/production.yaml
```

### **Step 3: Configure Environment Variables**
```bash
# Create environment file
cat > /opt/citadel/hxp-enterprise-llm/.env << 'EOF'
# Environment Configuration
HXP_ENVIRONMENT=production
HXP_CONFIG_PATH=/opt/citadel/hxp-enterprise-llm/config
HXP_MODELS_PATH=/opt/citadel/hxp-enterprise-llm/models
HXP_LOGS_PATH=/opt/citadel/hxp-enterprise-llm/logs

# Database Configuration
HXP_DATABASE_HOST=192.168.10.35
HXP_DATABASE_PORT=5433
HXP_DATABASE_NAME=citadel_alpha
HXP_DATABASE_USER=citadel_user
HXP_DATABASE_PASSWORD=secure_password

# Vector Database Configuration
HXP_VECTOR_DB_HOST=192.168.10.30
HXP_VECTOR_DB_PORT=6333
HXP_VECTOR_DB_COLLECTION=citadel_vectors

# Cache Configuration
HXP_CACHE_HOST=192.168.10.37
HXP_CACHE_PORT=6379
HXP_CACHE_DATABASE=0

# Security Configuration
HXP_API_KEY=your_secure_api_key_here
HXP_ENABLE_SSL=true
HXP_SSL_CERT_PATH=/opt/citadel/hxp-enterprise-llm/ssl/cert.pem
HXP_SSL_KEY_PATH=/opt/citadel/hxp-enterprise-llm/ssl/key.pem

# Monitoring Configuration
HXP_ENABLE_MONITORING=true
HXP_PROMETHEUS_PORT=9090
HXP_GRAFANA_PORT=3000
EOF
```

### **Step 4: Download AI Models**
```bash
# Create models directory
mkdir -p /opt/citadel/hxp-enterprise-llm/models

# Download Mixtral-8x7B model
python -m hxp_enterprise_llm.models.download \
    --model mixtral-8x7b-instruct \
    --output /opt/citadel/hxp-enterprise-llm/models/mixtral

# Download Hermes-2 model
python -m hxp_enterprise_llm.models.download \
    --model NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO \
    --output /opt/citadel/hxp-enterprise-llm/models/hermes

# Download OpenChat-3.5 model
python -m hxp_enterprise_llm.models.download \
    --model openchat/openchat-3.5-0106 \
    --output /opt/citadel/hxp-enterprise-llm/models/openchat

# Download Phi-3-Mini model
python -m hxp_enterprise_llm.models.download \
    --model microsoft/Phi-3-mini-4k-instruct \
    --output /opt/citadel/hxp-enterprise-llm/models/phi3
```

## 🔧 Service Setup

### **Systemd Service Configuration**

#### **Create Service Files**
```bash
# Create systemd service directory
sudo mkdir -p /etc/systemd/system

# Create API Gateway service
sudo tee /etc/systemd/system/citadel-api-gateway.service > /dev/null << 'EOF'
[Unit]
Description=HXP Enterprise LLM API Gateway
After=network.target
Wants=network.target

[Service]
Type=simple
User=citadel
Group=citadel
WorkingDirectory=/opt/citadel/hxp-enterprise-llm
Environment=PATH=/opt/citadel/hxp-enterprise-llm/venv/bin
ExecStart=/opt/citadel/hxp-enterprise-llm/venv/bin/python -m hxp_enterprise_llm.services.infrastructure.api_gateway
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create Mixtral service
sudo tee /etc/systemd/system/citadel-mixtral.service > /dev/null << 'EOF'
[Unit]
Description=HXP Enterprise LLM Mixtral Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=citadel
Group=citadel
WorkingDirectory=/opt/citadel/hxp-enterprise-llm
Environment=PATH=/opt/citadel/hxp-enterprise-llm/venv/bin
ExecStart=/opt/citadel/hxp-enterprise-llm/venv/bin/python -m hxp_enterprise_llm.services.ai_models.mixtral
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring service
sudo tee /etc/systemd/system/citadel-monitoring.service > /dev/null << 'EOF'
[Unit]
Description=HXP Enterprise LLM Monitoring
After=network.target
Wants=network.target

[Service]
Type=simple
User=citadel
Group=citadel
WorkingDirectory=/opt/citadel/hxp-enterprise-llm
Environment=PATH=/opt/citadel/hxp-enterprise-llm/venv/bin
ExecStart=/opt/citadel/hxp-enterprise-llm/venv/bin/python -m hxp_enterprise_llm.services.infrastructure.monitoring
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

#### **Enable and Start Services**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable citadel-api-gateway.service
sudo systemctl enable citadel-mixtral.service
sudo systemctl enable citadel-monitoring.service

# Start services
sudo systemctl start citadel-api-gateway.service
sudo systemctl start citadel-mixtral.service
sudo systemctl start citadel-monitoring.service
```

### **Docker Service Configuration**

#### **Create Docker Services**
```bash
# Create Docker Compose services
cat > docker-compose.services.yml << 'EOF'
version: '3.8'

services:
  api-gateway:
    image: manus-ai/hxp-api-gateway:3.0.0
    container_name: citadel-api-gateway
    ports:
      - "8000:8000"
    volumes:
      - ./config:/opt/citadel/hxp-enterprise-llm/config
    environment:
      - HXP_ENVIRONMENT=production
    restart: unless-stopped

  mixtral:
    image: manus-ai/hxp-mixtral:3.0.0
    container_name: citadel-mixtral
    ports:
      - "11400:11400"
    volumes:
      - ./models/mixtral:/opt/citadel/hxp-enterprise-llm/models/mixtral
      - ./config:/opt/citadel/hxp-enterprise-llm/config
    environment:
      - HXP_ENVIRONMENT=production
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  monitoring:
    image: manus-ai/hxp-monitoring:3.0.0
    container_name: citadel-monitoring
    ports:
      - "9090:9090"
      - "3000:3000"
    volumes:
      - ./config:/opt/citadel/hxp-enterprise-llm/config
    environment:
      - HXP_ENVIRONMENT=production
    restart: unless-stopped
EOF

# Start services
docker-compose -f docker-compose.services.yml up -d
```

## ✅ Verification

### **Step 1: Check Service Status**
```bash
# Check systemd service status
sudo systemctl status citadel-api-gateway.service
sudo systemctl status citadel-mixtral.service
sudo systemctl status citadel-monitoring.service

# Check Docker service status
docker ps | grep citadel
```

### **Step 2: Test API Endpoints**
```bash
# Test API Gateway health
curl -X GET http://localhost:8000/health

# Test Mixtral service
curl -X POST http://localhost:11400/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "prompt": "Hello, how are you?",
    "max_tokens": 100,
    "temperature": 0.7
  }'

# Test monitoring endpoints
curl -X GET http://localhost:9090/metrics
curl -X GET http://localhost:3000/api/health
```

### **Step 3: Verify Configuration**
```bash
# Verify configuration loading
python -c "
from hxp_enterprise_llm.services.infrastructure.configuration import ConfigurationManager
config_manager = ConfigurationManager()
config = config_manager.load_config('production')
print('Configuration loaded successfully')
print(f'Mixtral port: {config.services.ai_models.mixtral.port}')
print(f'API Gateway port: {config.infrastructure.api_gateway.port}')
"
```

### **Step 4: Run Health Checks**
```bash
# Run comprehensive health checks
python -m hxp_enterprise_llm.health.run_health_checks \
    --environment production \
    --verbose
```

## 🔒 Post-Installation Security Setup

### **Step 1: Configure Firewall**
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HXP services
sudo ufw allow 8000/tcp   # API Gateway
sudo ufw allow 11400/tcp  # Mixtral
sudo ufw allow 11401/tcp  # Hermes
sudo ufw allow 11402/tcp  # OpenChat
sudo ufw allow 11403/tcp  # Phi-3
sudo ufw allow 9090/tcp   # Prometheus
sudo ufw allow 3000/tcp   # Grafana

# Check firewall status
sudo ufw status
```

### **Step 2: Configure SSL/TLS**
```bash
# Generate SSL certificate (self-signed for development)
sudo mkdir -p /opt/citadel/hxp-enterprise-llm/ssl
cd /opt/citadel/hxp-enterprise-llm/ssl

# Generate private key
sudo openssl genrsa -out key.pem 2048

# Generate certificate
sudo openssl req -new -x509 -key key.pem -out cert.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set permissions
sudo chmod 600 key.pem
sudo chmod 644 cert.pem
sudo chown citadel:citadel *.pem
```

### **Step 3: Configure API Authentication**
```bash
# Generate secure API key
python -c "
import secrets
api_key = secrets.token_urlsafe(32)
print(f'Generated API key: {api_key}')
"

# Update configuration with API key
python -m hxp_enterprise_llm.config.update_secret \
    --key api_key \
    --value your_generated_api_key \
    --environment production
```

## 📊 Monitoring Setup

### **Step 1: Configure Prometheus**
```bash
# Create Prometheus configuration
cat > /opt/citadel/hxp-enterprise-llm/config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'hxp-api-gateway'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'hxp-mixtral'
    static_configs:
      - targets: ['localhost:11400']
    metrics_path: '/metrics'

  - job_name: 'hxp-monitoring'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
EOF
```

### **Step 2: Configure Grafana**
```bash
# Create Grafana configuration
cat > /opt/citadel/hxp-enterprise-llm/config/grafana.ini << 'EOF'
[server]
http_port = 3000
domain = localhost

[security]
admin_user = admin
admin_password = secure_password

[database]
type = sqlite3
path = /opt/citadel/hxp-enterprise-llm/data/grafana.db
EOF
```

### **Step 3: Import Dashboards**
```bash
# Import HXP dashboards
python -m hxp_enterprise_llm.monitoring.import_dashboards \
    --grafana-url http://localhost:3000 \
    --username admin \
    --password secure_password
```

## 🚨 Troubleshooting

### **Common Installation Issues**

#### **Issue: Python Version Not Found**
```bash
# Solution: Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-dev python3.11-venv

# Verify installation
python3.11 --version
```

#### **Issue: CUDA Not Available**
```bash
# Solution: Install CUDA drivers
sudo apt install nvidia-driver-535 nvidia-cuda-toolkit

# Verify CUDA installation
nvidia-smi
nvcc --version
```

#### **Issue: Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill the process or change the port
sudo kill -9 <PID>
```

#### **Issue: Permission Denied**
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/citadel/hxp-enterprise-llm
sudo chmod -R 755 /opt/citadel/hxp-enterprise-llm
```

### **Debug Mode**
```bash
# Enable debug mode for detailed logging
export HXP_DEBUG=true
export HXP_LOG_LEVEL=DEBUG

# Run services with debug logging
python -m hxp_enterprise_llm.services.infrastructure.api_gateway --debug
```

### **Performance Issues**
```bash
# Check system resources
htop
nvidia-smi
df -h

# Check service logs
sudo journalctl -u citadel-api-gateway.service -f
sudo journalctl -u citadel-mixtral.service -f
```

## 📈 Next Steps

### **1. Configuration Optimization**
- [Configuration Guide](configuration.md) - Advanced configuration options
- [Performance Tuning](performance-tuning.md) - Optimize for your hardware
- [Security Hardening](security.md) - Additional security measures

### **2. Monitoring and Alerting**
- [Monitoring Guide](monitoring.md) - Set up comprehensive monitoring
- [Alerting Configuration](alerting.md) - Configure alerts and notifications
- [Dashboard Customization](dashboards.md) - Customize monitoring dashboards

### **3. Integration and Deployment**
- [API Integration](api-integration.md) - Integrate with external applications
- [Deployment Guide](deployment.md) - Production deployment strategies
- [Scaling Guide](scaling.md) - Scale your deployment

### **4. Development and Testing**
- [Development Setup](development-setup.md) - Set up development environment
- [Testing Guide](testing.md) - Run tests and validation
- [Contribution Guide](contributing.md) - Contribute to the project

## 📞 Support

### **Getting Help**
- **Documentation**: [Complete Documentation](https://docs.hxp-enterprise-llm.com)
- **GitHub Issues**: [Report Issues](https://github.com/manus-ai/hxp-enterprise-llm/issues)
- **Discussions**: [Community Q&A](https://github.com/manus-ai/hxp-enterprise-llm/discussions)
- **Email Support**: [support@hxp-enterprise-llm.com](mailto:support@hxp-enterprise-llm.com)

### **Community Resources**
- **GitHub Repository**: [Source Code](https://github.com/manus-ai/hxp-enterprise-llm)
- **Docker Hub**: [Container Images](https://hub.docker.com/r/manus-ai/hxp-enterprise-llm)
- **PyPI**: [Python Package](https://pypi.org/project/hxp-enterprise-llm)

---

**Last Updated:** 2025-01-18  
**Version:** 3.0.0  
**Installation Guide Status:** Complete  
**Tested On:** Ubuntu 24.04 LTS 