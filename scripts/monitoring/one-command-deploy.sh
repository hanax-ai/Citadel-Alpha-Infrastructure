#!/bin/bash

set -e

# Automated Deployment Script for Citadel Monitoring
# Version: 2.0
# Date: July 24, 2025

METRICS_SERVER="192.168.10.37"
HX_SERVER_02="192.168.10.28"
USER="agent0"

echo "🚀 ONE-COMMAND DEPLOYMENT: Citadel Monitoring Stack"
echo "=================================================="
echo "Target: ${METRICS_SERVER} | Source: ${HX_SERVER_02}"
echo "Timestamp: $(date)"
echo ""

# Create temporary configuration directory
CONFIG_DIR="/tmp/citadel-monitoring-deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "${CONFIG_DIR}"/{prometheus,alertmanager,grafana,dashboards,scripts}

# Generate Prometheus configuration for metrics server
cat > "${CONFIG_DIR}/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    cluster: 'citadel-production'
    datacenter: 'hx-internal'

rule_files:
  - "/etc/prometheus/rules/citadel-alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:
  # Node Exporter - System Metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: 
          - '192.168.10.31:9100'  # HX-Server-01
          - '192.168.10.28:9100'  # HX-Server-02
          - '192.168.10.35:9100'  # PostgreSQL Server
          - '192.168.10.37:9100'  # Metrics Server
        labels:
          cluster: 'citadel-infrastructure'

  # Citadel API Gateway - HX-Server-01
  - job_name: 'citadel-gateway-01'
    static_configs:
      - targets: ['192.168.10.31:8002']
        labels:
          instance: 'hx-server-01'
          service: 'citadel-gateway'
          environment: 'production'
    metrics_path: '/metrics'
    scrape_interval: 15s

  # Citadel API Gateway - HX-Server-02  
  - job_name: 'citadel-gateway-02'
    static_configs:
      - targets: ['192.168.10.28:8001']
        labels:
          instance: 'hx-server-02'
          service: 'citadel-gateway'
          environment: 'production'
    metrics_path: '/metrics'
    scrape_interval: 15s

  # Ollama Service Monitoring
  - job_name: 'ollama-service'
    static_configs:
      - targets: 
          - '192.168.10.31:11434'  # HX-Server-01
          - '192.168.10.28:11434'  # HX-Server-02
        labels:
          service: 'ollama'
    metrics_path: '/metrics'
    scrape_interval: 30s

  # PostgreSQL Exporter
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['192.168.10.35:9187']
        labels:
          service: 'postgresql'
          database: 'citadel_llm_db'
    scrape_interval: 30s
EOF

# Generate alert rules
cat > "${CONFIG_DIR}/prometheus/citadel-alerts.yml" << 'EOF'
groups:
  - name: citadel-infrastructure
    rules:
      # Service Health Monitoring
      - alert: CitadelGatewayDown_HX02
        expr: up{job="citadel-gateway-02"} == 0
        for: 1m
        labels:
          severity: critical
          component: api-gateway
          instance: hx-server-02
        annotations:
          summary: "Citadel API Gateway is down on HX-Server-02"
          description: "Citadel Gateway on HX-Server-02 (192.168.10.28) has been down for more than 1 minute"

      - alert: OllamaServiceDown_HX02
        expr: up{job="ollama-service",instance=~".*28.*"} == 0
        for: 2m
        labels:
          severity: critical
          component: llm-service
          instance: hx-server-02
        annotations:
          summary: "Ollama LLM service is down on HX-Server-02"
          description: "Ollama service on HX-Server-02 has been down for more than 2 minutes"

      # Performance Monitoring
      - alert: HighResponseTime_HX02
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="citadel-gateway-02"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
          component: performance
          instance: hx-server-02
        annotations:
          summary: "High API response time on HX-Server-02"
          description: "95th percentile response time is {{ $value }}s on HX-Server-02"

      - alert: HighErrorRate_HX02
        expr: rate(http_requests_total{job="citadel-gateway-02",status=~"5.."}[5m]) / rate(http_requests_total{job="citadel-gateway-02"}[5m]) > 0.05
        for: 3m
        labels:
          severity: warning
          component: reliability
          instance: hx-server-02
        annotations:
          summary: "High error rate detected on HX-Server-02"
          description: "Error rate is {{ $value | humanizePercentage }} on HX-Server-02"

      # Resource Monitoring
      - alert: HighCPUUsage_HX02
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle",instance=~".*28.*"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
          component: resources
          instance: hx-server-02
        annotations:
          summary: "High CPU usage on HX-Server-02"
          description: "CPU usage is {{ $value }}% on HX-Server-02"

      - alert: HighMemoryUsage_HX02
        expr: (1 - (node_memory_MemAvailable_bytes{instance=~".*28.*"} / node_memory_MemTotal_bytes{instance=~".*28.*"})) * 100 > 90
        for: 5m
        labels:
          severity: critical
          component: resources
          instance: hx-server-02
        annotations:
          summary: "High memory usage on HX-Server-02"
          description: "Memory usage is {{ $value }}% on HX-Server-02"
EOF

# Generate Alertmanager configuration
cat > "${CONFIG_DIR}/alertmanager/alertmanager.yml" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@citadel.local'

route:
  group_by: ['alertname', 'cluster', 'instance']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'citadel-webhook'
  routes:
    - match:
        severity: critical
      receiver: 'citadel-critical'
      repeat_interval: 15m
    - match:
        instance: hx-server-02
      receiver: 'hx-server-02-alerts'

receivers:
  - name: 'citadel-webhook'
    webhook_configs:
      - url: 'http://192.168.10.31:8002/webhooks/alerts'
        send_resolved: true
      - url: 'http://192.168.10.28:8001/webhooks/alerts'
        send_resolved: true

  - name: 'citadel-critical'
    webhook_configs:
      - url: 'http://192.168.10.31:8002/webhooks/alerts'
        send_resolved: true
        title: 'CRITICAL: {{ .GroupLabels.alertname }}'
      - url: 'http://192.168.10.28:8001/webhooks/alerts'
        send_resolved: true
        title: 'CRITICAL: {{ .GroupLabels.alertname }}'

  - name: 'hx-server-02-alerts'
    webhook_configs:
      - url: 'http://192.168.10.28:8001/webhooks/alerts'
        send_resolved: true
        title: 'HX-Server-02: {{ .GroupLabels.alertname }}'
EOF

# Copy existing dashboard files
if [ -d "/opt/citadel-02/frameworks/monitoring/dashboards" ]; then
    cp -r /opt/citadel-02/frameworks/monitoring/dashboards/* "${CONFIG_DIR}/dashboards/" 2>/dev/null || true
fi

if [ -d "/opt/citadel-02/frameworks/monitoring/local-dashboards" ]; then
    cp -r /opt/citadel-02/frameworks/monitoring/local-dashboards/* "${CONFIG_DIR}/dashboards/" 2>/dev/null || true
fi

echo "📦 Configuration package prepared: ${CONFIG_DIR}"

# Test connectivity
echo "🔍 Testing connectivity to metrics server..."
if ! ping -c 1 "${METRICS_SERVER}" &> /dev/null; then
    echo "❌ Cannot reach metrics server ${METRICS_SERVER}"
    exit 1
fi

if ! ssh -o ConnectTimeout=5 "${USER}@${METRICS_SERVER}" "echo 'SSH OK'" &> /dev/null; then
    echo "❌ Cannot SSH to ${USER}@${METRICS_SERVER}"
    echo "Please ensure SSH key authentication is configured"
    exit 1
fi

echo "✅ Connectivity tests passed"

# Copy to metrics server
echo "📤 Copying configuration to metrics server..."
scp -r "${CONFIG_DIR}" "${USER}@${METRICS_SERVER}:/tmp/"

# Deploy on metrics server
echo "🔧 Deploying configurations on metrics server..."
ssh "${USER}@${METRICS_SERVER}" "
    set -e
    
    # Create backup
    BACKUP_DIR=\"/tmp/citadel-backup-\$(date +%Y%m%d-%H%M%S)\"
    mkdir -p \"\${BACKUP_DIR}\"
    sudo cp /etc/prometheus/prometheus.yml \"\${BACKUP_DIR}/\" 2>/dev/null || true
    sudo cp /etc/alertmanager/alertmanager.yml \"\${BACKUP_DIR}/\" 2>/dev/null || true
    echo \"Backup created: \${BACKUP_DIR}\"
    
    # Create directories
    sudo mkdir -p /etc/prometheus/rules
    
    # Install configurations
    sudo cp /tmp/$(basename ${CONFIG_DIR})/prometheus/prometheus.yml /etc/prometheus/
    sudo cp /tmp/$(basename ${CONFIG_DIR})/prometheus/citadel-alerts.yml /etc/prometheus/rules/
    sudo cp /tmp/$(basename ${CONFIG_DIR})/alertmanager/alertmanager.yml /etc/alertmanager/
    
    # Validate configurations
    sudo promtool check config /etc/prometheus/prometheus.yml
    sudo promtool check rules /etc/prometheus/rules/citadel-alerts.yml
    sudo amtool check-config /etc/alertmanager/alertmanager.yml
    
    # Restart services
    sudo systemctl restart prometheus
    sudo systemctl restart alertmanager
    sudo systemctl restart grafana-server
    
    # Verify services
    sleep 5
    sudo systemctl is-active prometheus
    sudo systemctl is-active alertmanager
    sudo systemctl is-active grafana-server
    
    # Copy dashboards for manual import
    sudo mkdir -p /var/lib/grafana/dashboards/citadel
    sudo cp /tmp/$(basename ${CONFIG_DIR})/dashboards/*.json /var/lib/grafana/dashboards/citadel/ 2>/dev/null || true
    sudo chown -R grafana:grafana /var/lib/grafana/dashboards/citadel/
    
    echo 'Services restarted successfully'
"

# Cleanup
rm -rf "${CONFIG_DIR}"

echo ""
echo "🎯 DEPLOYMENT COMPLETE!"
echo "======================"
echo "✅ Prometheus configuration deployed and validated"
echo "✅ Alertmanager rules activated"
echo "✅ Services restarted successfully"
echo "✅ Dashboards prepared for import"
echo ""
echo "🌐 Access URLs:"
echo "  • Prometheus: http://${METRICS_SERVER}:9090"
echo "  • Grafana: http://${METRICS_SERVER}:3000 (admin/admin)"
echo "  • Alertmanager: http://${METRICS_SERVER}:9093"
echo "  • HX-Server-02 Health: http://${HX_SERVER_02}:8001/health/"
echo ""
echo "📋 Next Steps:"
echo "1. Import dashboards through Grafana UI"
echo "2. Verify targets are UP in Prometheus"
echo "3. Test alert notifications"
echo ""

# Run validation
echo "🧪 Running post-deployment validation..."
sleep 10
/opt/citadel-02/scripts/monitoring/comprehensive-validation.sh

echo ""
echo "🚀 ONE-COMMAND DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "Deployment timestamp: $(date)"
