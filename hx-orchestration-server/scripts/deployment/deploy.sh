#!/bin/bash

# HX-Orchestration-Server Deployment Script
# Deploys and configures the orchestration server on hx-orchestration-server (192.168.10.31)

set -euo pipefail

# Configuration
PROJECT_DIR="/opt/citadel-orca/hx-orchestration-server"
VENV_DIR="/opt/citadel-venv"
SERVICE_USER="citadel"
LOG_FILE="/var/log/citadel-deployment.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Main deployment function
main() {
    log "Starting HX-Orchestration-Server deployment..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        error_exit "This script must be run as root"
    fi
    
    # Verify we're on the correct server
    HOSTNAME=$(hostname)
    if [[ "$HOSTNAME" != "hx-orchestration-server" ]]; then
        log "WARNING: Expected hostname 'hx-orchestration-server', got '$HOSTNAME'"
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Stop existing services
    stop_services
    
    # Install dependencies
    install_dependencies
    
    # Setup virtual environment
    setup_virtualenv
    
    # Install SystemD services
    install_systemd_services
    
    # Create configuration
    setup_configuration
    
    # Set permissions
    set_permissions
    
    # Start services
    start_services
    
    # Verify deployment
    verify_deployment
    
    log "Deployment completed successfully!"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python version
    python3 --version | grep -q "3.12" || error_exit "Python 3.12 required"
    
    # Check if project directory exists
    [[ -d "$PROJECT_DIR" ]] || error_exit "Project directory $PROJECT_DIR not found"
    
    # Check if virtual environment exists
    [[ -d "$VENV_DIR" ]] || error_exit "Virtual environment $VENV_DIR not found"
    
    log "Prerequisites check passed"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        redis-server \
        postgresql-client \
        nginx \
        supervisor \
        htop \
        curl \
        jq
    
    log "System dependencies installed"
}

# Setup virtual environment
setup_virtualenv() {
    log "Setting up virtual environment..."
    
    # Activate virtual environment and install packages
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    log "Virtual environment setup completed"
}

# Stop existing services
stop_services() {
    log "Stopping existing services..."
    
    systemctl stop citadel-celery.service 2>/dev/null || true
    systemctl stop citadel-orchestration.service 2>/dev/null || true
    
    log "Services stopped"
}

# Install SystemD services
install_systemd_services() {
    log "Installing SystemD services..."
    
    # Copy service files
    cp "$PROJECT_DIR/systemd/"*.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable citadel-redis.service
    systemctl enable citadel-orchestration.service
    systemctl enable citadel-celery.service
    
    log "SystemD services installed"
}

# Setup configuration
setup_configuration() {
    log "Setting up configuration..."
    
    cd "$PROJECT_DIR"
    
    # Create .env from example if it doesn't exist
    if [[ ! -f .env ]]; then
        cp .env.example .env
        log "Created .env from example - please review and customize"
    fi
    
    # Create log directory
    mkdir -p logs
    
    log "Configuration setup completed"
}

# Set permissions
set_permissions() {
    log "Setting permissions..."
    
    # Create citadel user if it doesn't exist
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false "$SERVICE_USER"
        log "Created user: $SERVICE_USER"
    fi
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
    
    # Set log permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR/logs"
    chmod 755 "$PROJECT_DIR/logs"
    
    log "Permissions set"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start Redis first
    systemctl start citadel-redis.service
    sleep 2
    
    # Start main application
    systemctl start citadel-orchestration.service
    sleep 5
    
    # Start Celery workers
    systemctl start citadel-celery.service
    sleep 2
    
    log "Services started"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check service status
    for service in citadel-redis citadel-orchestration citadel-celery; do
        if systemctl is-active --quiet "$service.service"; then
            log "✓ $service is running"
        else
            error_exit "✗ $service is not running"
        fi
    done
    
    # Check API health
    sleep 10  # Give services time to start
    
    if curl -f -s http://localhost:8080/health/ > /dev/null; then
        log "✓ API health check passed"
    else
        error_exit "✗ API health check failed"
    fi
    
    # Check metrics endpoint
    if curl -f -s http://localhost:8080/metrics > /dev/null; then
        log "✓ Metrics endpoint accessible"
    else
        log "⚠ Metrics endpoint not accessible (may be normal during startup)"
    fi
    
    log "Deployment verification completed"
}

# Run main function
main "$@"
