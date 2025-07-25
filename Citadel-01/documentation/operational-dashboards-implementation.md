# Operational Dashboards Implementation Guide
## HX-Metrics-Server (192.168.10.37) Deployment

### Overview
This document provides complete implementation instructions for setting up operational dashboards on the HX-Metrics-Server (192.168.10.37) using the monitoring infrastructure developed for the Citadel LLM system.

---

## 🏗️ **Infrastructure Overview**

### **Target Server**: `192.168.10.37` (hx-metrics-server)
- **Prometheus**: `http://192.168.10.37:9090`
- **Grafana**: `http://192.168.10.37:3000` (admin/admin)
- **Alertmanager**: `http://192.168.10.37:9093`
- **Node Exporter**: `http://192.168.10.37:9100`

### **Monitored Targets**
- **HX-Server-02 (192.168.10.34)**: Citadel Gateway, Ollama, System Metrics
- **PostgreSQL Server (192.168.10.35)**: Database Metrics
- **External Services**: Network connectivity, API endpoints

---

## 📋 **Pre-Deployment Checklist**

### **1. Configuration Files Ready for Transfer**
```bash
# Core monitoring configurations
/opt/citadel/config/monitoring/prometheus/prometheus.yml
/opt/citadel/config/monitoring/prometheus/citadel-targets.yml
/opt/citadel/config/monitoring/prometheus/rules/citadel-alerts.yml

# Grafana configurations
/opt/citadel/config/monitoring/grafana/datasources/datasources.yaml
/opt/citadel/config/monitoring/grafana/dashboards/citadel-overview.json
/opt/citadel/config/monitoring/grafana/dashboards/citadel-ai-performance.json

# Alerting configuration
/opt/citadel/config/monitoring/alertmanager-webhook-config.yml
```

### **2. Placeholder Directories Created**
```bash
✅ /opt/citadel/frameworks/monitoring/dashboards/
✅ All monitoring configuration validated
✅ Service definitions reviewed
```

---

## 🚀 **Implementation Steps**

### **Phase 1: Server Preparation (192.168.10.37)**

#### **1.1 Directory Structure Setup**
```bash
# On hx-metrics-server (192.168.10.37)
sudo mkdir -p /opt/citadel-monitoring/{prometheus,grafana,alertmanager}
sudo mkdir -p /opt/citadel-monitoring/prometheus/{data,config,rules}
sudo mkdir -p /opt/citadel-monitoring/grafana/{data,dashboards,datasources}
sudo mkdir -p /opt/citadel-monitoring/alertmanager/{data,config}

# Set ownership
sudo chown -R prometheus:prometheus /opt/citadel-monitoring/prometheus/
sudo chown -R grafana:grafana /opt/citadel-monitoring/grafana/
sudo chown -R alertmanager:alertmanager /opt/citadel-monitoring/alertmanager/
```

#### **1.2 Install Monitoring Stack**
```bash
# Install Prometheus
sudo apt update
sudo apt install -y prometheus prometheus-node-exporter

# Install Grafana
sudo apt install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt update
sudo apt install -y grafana

# Install Alertmanager
sudo apt install -y prometheus-alertmanager

# Enable services
sudo systemctl enable prometheus grafana-server prometheus-node-exporter prometheus-alertmanager
```

### **Phase 2: Configuration Deployment**

#### **2.1 Prometheus Configuration**
```bash
# Deploy main Prometheus config
scp /opt/citadel/config/monitoring/prometheus/prometheus.yml \
    192.168.10.37:/opt/citadel-monitoring/prometheus/config/

# Deploy targets configuration
scp /opt/citadel/config/monitoring/prometheus/citadel-targets.yml \
    192.168.10.37:/opt/citadel-monitoring/prometheus/config/

# Deploy alerting rules
scp /opt/citadel/config/monitoring/prometheus/rules/citadel-alerts.yml \
    192.168.10.37:/opt/citadel-monitoring/prometheus/rules/

# Update Prometheus service configuration
sudo systemctl edit prometheus --full
```

**Prometheus Service Configuration:**
```ini
[Unit]
Description=Prometheus Server
Documentation=https://prometheus.io/docs/
After=network-online.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/usr/bin/prometheus \
  --config.file=/opt/citadel-monitoring/prometheus/config/prometheus.yml \
  --storage.tsdb.path=/opt/citadel-monitoring/prometheus/data \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090 \
  --web.external-url=http://192.168.10.37:9090 \
  --storage.tsdb.retention.time=30d

Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

#### **2.2 Grafana Configuration**
```bash
# Deploy datasource configuration
scp /opt/citadel/config/monitoring/grafana/datasources/datasources.yaml \
    192.168.10.37:/opt/citadel-monitoring/grafana/datasources/

# Deploy dashboard configurations
scp /opt/citadel/config/monitoring/grafana/dashboards/*.json \
    192.168.10.37:/opt/citadel-monitoring/grafana/dashboards/
```

**Grafana Configuration (/etc/grafana/grafana.ini):**
```ini
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = 192.168.10.37

[paths]
data = /opt/citadel-monitoring/grafana/data
provisioning = /opt/citadel-monitoring/grafana

[security]
admin_user = admin
admin_password = admin

[dashboards]
default_home_dashboard_path = /opt/citadel-monitoring/grafana/dashboards/citadel-overview.json
```

#### **2.3 Alertmanager Configuration**
```bash
# Deploy alerting configuration
scp /opt/citadel/config/monitoring/alertmanager-webhook-config.yml \
    192.168.10.37:/opt/citadel-monitoring/alertmanager/config/alertmanager.yml
```

### **Phase 3: Service Deployment**

#### **3.1 Start and Verify Services**
```bash
# On hx-metrics-server (192.168.10.37)
sudo systemctl restart prometheus grafana-server prometheus-alertmanager prometheus-node-exporter
sudo systemctl status prometheus grafana-server prometheus-alertmanager

# Verify ports are listening
sudo netstat -tlnp | grep -E "(9090|3000|9093|9100)"
```

#### **3.2 Configure Service Monitoring**
```bash
# Test Prometheus targets
curl http://192.168.10.37:9090/api/v1/targets

# Test Grafana access
curl http://192.168.10.37:3000/api/health

# Test Alertmanager
curl http://192.168.10.37:9093/api/v1/status
```

---

## 📊 **Dashboard Configurations**

### **Available Dashboards**

#### **1. Citadel System Overview Dashboard**
- **Path**: `/opt/citadel/config/monitoring/grafana/dashboards/citadel-overview.json`
- **Metrics**: System health, service status, resource utilization
- **Panels**: 
  - Service availability (Gateway, PostgreSQL, Redis, Ollama)
  - CPU and memory usage
  - Network connectivity
  - Request rates and response times

#### **2. AI Performance Dashboard**
- **Path**: `/opt/citadel/config/monitoring/grafana/dashboards/citadel-ai-performance.json`
- **Metrics**: AI model performance, inference times, token rates
- **Panels**:
  - Model response times
  - Token generation rates
  - Queue depths
  - Error rates by model

### **Metrics Collection Points**

#### **Primary Scrape Targets**
```yaml
# From prometheus.yml
scrape_configs:
  - job_name: 'citadel-gateway'
    static_configs:
      - targets: ['192.168.10.34:8002']  # HX-Server-02
    metrics_path: '/metrics'

  - job_name: 'ollama'
    static_configs:
      - targets: ['192.168.10.34:11434']  # Ollama service
    
  - job_name: 'postgresql'
    static_configs:
      - targets: ['192.168.10.35:9187']  # PostgreSQL exporter
    
  - job_name: 'node-exporter-hx-server-02'
    static_configs:
      - targets: ['192.168.10.34:9100']  # System metrics
```

---

## 🔔 **Alerting Configuration**

### **Alert Rules Implemented**
```yaml
# From citadel-alerts.yml
groups:
  - name: citadel.rules
    rules:
      - alert: CitadelGatewayDown
        expr: up{job="citadel-hx-server-02-gateway"} == 0
        for: 1m
        labels:
          severity: critical
          service: gateway
        annotations:
          summary: "Citadel Gateway is down"
          
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          service: system
```

### **Webhook Integration**
- **Endpoint**: `http://192.168.10.34:8002/webhooks/alertmanager`
- **Authentication**: Basic auth or API key
- **Response Actions**: Automated service restart, notification escalation

---

## 🧪 **Testing and Validation**

### **Phase 4: Comprehensive Testing**

#### **4.1 Connectivity Tests**
```bash
# Test from metrics server to targets
curl -s http://192.168.10.34:8002/health/
curl -s http://192.168.10.34:9100/metrics | head -20
curl -s http://192.168.10.35:9187/metrics | head -20

# Test metrics collection
curl -s http://192.168.10.37:9090/api/v1/query?query=up
```

#### **4.2 Dashboard Validation**
```bash
# Access Grafana
open http://192.168.10.37:3000

# Verify dashboards loaded
curl -s -u admin:admin http://192.168.10.37:3000/api/search?query=citadel

# Test dashboard data
curl -s -u admin:admin \
  "http://192.168.10.37:3000/api/datasources/proxy/1/api/v1/query?query=up"
```

#### **4.3 Alert Testing**
```bash
# Trigger test alert (simulate service down)
sudo systemctl stop citadel-gateway  # On HX-Server-02

# Verify alert fires in Alertmanager
curl http://192.168.10.37:9093/api/v1/alerts

# Check webhook delivery
tail -f /opt/citadel/logs/api-gateway/service.log  # On HX-Server-02
```

---

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] HX-Metrics-Server (192.168.10.37) accessible
- [ ] All configuration files validated
- [ ] Network connectivity confirmed between servers
- [ ] Service accounts and permissions configured

### **Deployment**
- [ ] Monitoring stack installed (Prometheus, Grafana, Alertmanager)
- [ ] Configuration files deployed and validated
- [ ] Services started and verified
- [ ] Dashboard provisioning completed

### **Post-Deployment**
- [ ] All scrape targets showing as UP in Prometheus
- [ ] Grafana dashboards loading with data
- [ ] Alert rules loaded and operational
- [ ] Webhook integration tested
- [ ] Performance benchmarks established

### **Validation**
- [ ] System overview dashboard functional
- [ ] AI performance metrics visible
- [ ] Alerting working end-to-end
- [ ] Historical data retention confirmed
- [ ] Access controls and security verified

---

## 🔧 **Maintenance and Operations**

### **Regular Tasks**
- **Daily**: Check dashboard functionality, verify alert status
- **Weekly**: Review metrics trends, validate backup procedures
- **Monthly**: Update configurations, security patches, capacity planning

### **Troubleshooting**
```bash
# Service status checks
sudo systemctl status prometheus grafana-server prometheus-alertmanager

# Log analysis
sudo journalctl -u prometheus -f
sudo journalctl -u grafana-server -f

# Metrics validation
curl http://192.168.10.37:9090/api/v1/targets
curl http://192.168.10.37:9090/api/v1/rules
```

### **Backup Procedures**
```bash
# Backup Prometheus data
sudo tar -czf /backup/prometheus-$(date +%Y%m%d).tar.gz \
  /opt/citadel-monitoring/prometheus/data/

# Backup Grafana configuration
sudo tar -czf /backup/grafana-$(date +%Y%m%d).tar.gz \
  /opt/citadel-monitoring/grafana/
```

---

## 🎯 **Success Metrics**

### **Operational Goals**
- **Uptime Monitoring**: 99.9% service availability
- **Response Time**: Dashboard load < 2 seconds
- **Alert Latency**: Notifications within 60 seconds
- **Data Retention**: 30 days of metrics history

### **Performance Indicators**
- All critical services showing GREEN status
- Zero false positive alerts
- 100% alert delivery success rate
- Dashboard query response < 1 second

---

This comprehensive guide provides everything needed to implement operational dashboards on the HX-Metrics-Server, leveraging all the monitoring infrastructure developed for the Citadel LLM system.
