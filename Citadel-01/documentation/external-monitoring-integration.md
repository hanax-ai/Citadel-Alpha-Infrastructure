# External Monitoring Integration for HX-Enterprise-AI-Infrastructure

This document describes the complete integration of HX-Enterprise-AI-Infrastructure with external Prometheus/Grafana monitoring at 192.168.10.37.

## Architecture Overview

```
External Monitoring Infrastructure (192.168.10.37)
├── Prometheus (:9090) - Metrics collection and alerting rules
├── Grafana (:3000) - Dashboard visualization and analysis
├── Alertmanager (:9093) - Alert routing and notifications
└── Node Exporter (:9100) - System metrics collection

HX-LLM-Server-01 (192.168.10.34) - Primary AI/ML Server
├── Citadel Gateway (:8002) - AI orchestration with metrics endpoints
├── TensorFlow Environment - TensorFlow 2.19.0 with GPU acceleration
├── PyTorch Environment - PyTorch 2.5.1+cu121 with GPU acceleration
├── Dual NVIDIA GeForce RTX 4070 Ti SUPER GPUs (Compute Capability 8.9)
├── CUDA Toolkit 12.9.86 with cuDNN 9.11.0
└── NVIDIA Driver 575.64.03

HX-Server-02 (192.168.10.31) - Secondary Infrastructure
├── Citadel Gateway (:8000) - Main application with metrics endpoints
├── Ollama Service (:11434) - LLM inference engine
├── PostgreSQL (:5432) - Database with monitoring
└── Redis (:6379) - Caching layer with monitoring
```

## Validated AI Environment (HX-LLM-Server-01)

### Hardware Configuration
- **GPUs**: 2x NVIDIA GeForce RTX 4070 Ti SUPER
- **Compute Capability**: 8.9
- **NVIDIA Driver**: 575.64.03
- **CUDA Toolkit**: 12.9.86
- **cuDNN**: 9.11.0

### Software Environment
- **Python**: 3.12.3
- **TensorFlow**: 2.19.0 (tensorflow_env) - GPU acceleration validated
- **PyTorch**: 2.5.1+cu121 (pytorch_env) - GPU acceleration validated
- **Environment Status**: Production-ready for AI/ML workloads

## Integration Components

### 1. Metrics Collection

**HX-LLM-Server-01 AI Metrics Endpoint: `:8002/metrics`**
- GPU metrics (temperature, utilization, memory, compute capability)
- AI framework metrics (TensorFlow/PyTorch operations, model performance)
- CUDA/cuDNN performance metrics
- Model inference latency and throughput
- Environment-specific metrics (pytorch_env, tensorflow_env)

**HX-Server-02 Citadel Metrics Endpoint: `:8000/metrics`**
- System metrics (CPU, memory, disk, network)
- Application metrics (request count, response time, errors)
- Database metrics (connections, query performance)
- Custom business metrics

**Health Check Endpoints:**
- `/health/` - Comprehensive health status including GPU status
- `/health/quick` - Fast health check
- `/health/ready` - Readiness probe with AI environment validation
- `/health/live` - Liveness probe
- `/health/gpu` - GPU-specific health monitoring

### 2. Alert Management

**Webhook Integration: `/webhooks/alerts`**
- Receives alerts from external Alertmanager
- Automated response system for critical alerts
- Alert history and statistics tracking
- Service restart automation for critical failures

**Alert Response Automation:**
- Service Down → Automatic service restart
- Disk Space Low → Log cleanup automation
- High Resource Usage → Performance monitoring
- Database Issues → Connection pool management

### 3. Configuration Files

#### Production Environment (`/opt/citadel/config/environments/production.yaml`)
```yaml
monitoring:
  external_prometheus_url: "http://192.168.10.37:9090"
  external_grafana_url: "http://192.168.10.37:3000"
  external_alertmanager_url: "http://192.168.10.37:9093"
  external_node_exporter_url: "http://192.168.10.37:9100"
  
  # HX-LLM-Server-01 Configuration
  hx_llm_server_01:
    metrics_endpoint: ":8002/metrics"
    gpu_monitoring: true
    ai_framework_monitoring: true
    environment_monitoring: ["pytorch_env", "tensorflow_env"]
    
  # HX-Server-02 Configuration  
  hx_server_02:
    metrics_endpoint: ":8000/metrics"
    
  metrics_interval: 30
  alerts_webhook: "/webhooks/alerts"
```

#### Prometheus Scrape Targets (`/opt/citadel/config/monitoring/prometheus/citadel-targets.yml`)
```yaml
# HX-LLM-Server-01 AI Infrastructure
- targets: ['192.168.10.34:8002']
  labels:
    job: citadel-ai-gateway
    cluster: hx-llm-server-01
    environment: production
    service: citadel-ai-gateway
    gpu_enabled: true
    
# HX-Server-02 Infrastructure  
- targets: ['192.168.10.31:8000']
  labels:
    job: citadel-gateway
    cluster: hx-server-02
    environment: production
    service: citadel-gateway
```

#### Alert Rules (`/opt/citadel/config/monitoring/prometheus/citadel-alerts.yml`)
- Service availability monitoring (both HX-LLM-Server-01 and HX-Server-02)
- Resource utilization thresholds
- Performance degradation detection
- Database health monitoring
- GPU temperature and utilization monitoring
- AI framework performance monitoring
- CUDA/cuDNN operational status
- Model inference performance thresholds

### 4. Grafana Dashboards

**Available Dashboards:**
- HX-Enterprise-AI-Infrastructure Overview
- HX-LLM-Server-01 AI Performance Monitoring
- GPU Performance and Temperature Analysis
- TensorFlow/PyTorch Environment Metrics
- HX-Server-02 System Overview
- Citadel Application Metrics
- Database Performance Analysis
- Alert Management Dashboard

**Dashboard Features:**
- Real-time metrics visualization
- Historical trend analysis
- Performance correlation views
- Alert status monitoring
- Automated anomaly detection

## Deployment Process

### Prerequisites
1. External monitoring infrastructure running at 192.168.10.37
2. Network connectivity between HX-Enterprise-AI-Infrastructure and monitoring infrastructure
3. HX-LLM-Server-01 AI environment validated (TensorFlow 2.19.0, PyTorch 2.5.1+cu121)
4. HX-Server-02 Citadel application deployed and running
5. Administrative access to both systems

### Step 1: Deploy Citadel Monitoring Integration
```bash
cd /opt/citadel
./bin/deploy-external-monitoring
```

This script will:
- Test connectivity to external infrastructure
- Deploy monitoring configuration
- Setup metrics endpoints
- Configure webhook integration
- Verify all components are working

### Step 2: Configure External Prometheus

Add to `/etc/prometheus/prometheus.yml` on 192.168.10.37:

```yaml
scrape_configs:
  # HX-LLM-Server-01 AI Gateway metrics
  - job_name: 'citadel-ai-hx-llm-server-01'
    static_configs:
      - targets: ['192.168.10.34:8002']
        labels:
          cluster: 'hx-llm-server-01'
          environment: 'production'
          gpu_enabled: 'true'
          ai_frameworks: 'tensorflow,pytorch'
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s

  # HX-LLM-Server-01 GPU health monitoring
  - job_name: 'citadel-gpu-hx-llm-server-01'
    static_configs:
      - targets: ['192.168.10.34:8002']
        labels:
          cluster: 'hx-llm-server-01'
          environment: 'production'
          gpu_model: 'rtx-4070-ti-super'
    metrics_path: '/health/gpu'
    scrape_interval: 10s
    scrape_timeout: 5s

  # HX-Server-02 Citadel Gateway metrics
  - job_name: 'citadel-hx-server-02'
    static_configs:
      - targets: ['192.168.10.31:8000']
        labels:
          cluster: 'hx-server-02'
          environment: 'production'
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  # HX-Server-02 health monitoring
  - job_name: 'citadel-health-hx-server-02'
    static_configs:
      - targets: ['192.168.10.31:8000']
        labels:
          cluster: 'hx-server-02'
          environment: 'production'
    metrics_path: '/health/'
    scrape_interval: 15s
    scrape_timeout: 5s
```

### Step 3: Configure External Alertmanager

Add to `/etc/alertmanager/alertmanager.yml` on 192.168.10.37:

```yaml
receivers:
  - name: 'citadel-hx-llm-server-01-webhook'
    webhook_configs:
      - url: 'http://192.168.10.34:8002/webhooks/alerts'
        send_resolved: true
        http_config:
          basic_auth:
            username: 'alertmanager'
            password: 'webhook-secret-key'
            
  - name: 'citadel-hx-server-02-webhook'
    webhook_configs:
      - url: 'http://192.168.10.31:8000/webhooks/alerts'
        send_resolved: true
        http_config:
          basic_auth:
            username: 'alertmanager'
            password: 'webhook-secret-key'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'web.hook'
  routes:
    - match:
        cluster: hx-llm-server-01
      receiver: 'citadel-hx-llm-server-01-webhook'
      group_wait: 5s
      repeat_interval: 3m
    - match:
        cluster: hx-server-02
      receiver: 'citadel-hx-server-02-webhook'
      group_wait: 10s
      repeat_interval: 5m
```

### Step 4: Import Grafana Dashboards

1. Open http://192.168.10.37:3000
2. Login with admin/admin
3. Navigate to '+' → Import
4. Upload dashboard JSON files from `/opt/citadel/config/monitoring/grafana/dashboards/`

### Step 5: Verify Integration

```bash
# Test HX-LLM-Server-01 AI integration
curl http://192.168.10.34:8002/metrics
curl http://192.168.10.34:8002/health/gpu
curl http://192.168.10.34:8002/health/

# Test HX-Server-02 integration
/opt/citadel/bin/test-webhook-integration
curl http://192.168.10.31:8000/metrics
curl http://192.168.10.31:8000/health/

# Check active alerts
curl http://192.168.10.34:8002/webhooks/alerts/active
curl http://192.168.10.31:8000/webhooks/alerts/active
```

## Monitoring Endpoints

### Metrics Endpoints
- `GET /metrics` - Prometheus metrics endpoint
- `GET /health/` - Comprehensive health check with metrics
- `GET /health/quick` - Fast health status
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### Webhook Endpoints
- `POST /webhooks/alerts` - Receive alerts from Alertmanager
- `GET /webhooks/alerts/active` - View currently active alerts
- `GET /webhooks/alerts/history` - View alert history
- `GET /webhooks/alerts/stats` - View alert statistics
- `DELETE /webhooks/alerts/history` - Clear alert history

### Management Endpoints
- `GET /management/status` - Service status overview
- `POST /management/restart` - Restart services
- `GET /management/logs` - View application logs
- `GET /management/performance` - Performance metrics

## Alert Rules and Automation

### Critical Alerts (Immediate Response)
- **ServiceDown** → Automatic service restart
- **GPUTemperatureHigh** → Thermal throttling and workload reduction
- **GPUMemoryFull** → Model optimization and memory cleanup
- **AIFrameworkError** → Environment restart and validation
- **CUDAError** → GPU driver validation and restart
- **DiskSpaceLow** → Log cleanup automation
- **DatabaseConnectionsFull** → Connection pool restart

### Warning Alerts (Monitoring)
- **HighGPUUtilization** → Performance monitoring and optimization
- **ModelInferenceSlow** → Model performance analysis
- **HighCPUUsage** → Performance monitoring
- **HighMemoryUsage** → Memory analysis
- **HighResponseTime** → Performance optimization
- **DatabaseSlowQueries** → Query optimization

### Alert Response Actions
1. **Immediate Response**: Automated fixes for critical issues
2. **Escalation**: Notification to operations team
3. **Documentation**: Alert history and root cause analysis
4. **Prevention**: Automated prevention measures

## Security Considerations

### Network Security
- Firewall rules allowing monitoring traffic
- Secure communication between systems
- Authentication for webhook endpoints
- Rate limiting for API endpoints

### Access Control
- Role-based access to monitoring systems
- Audit logging for administrative actions
- Secure credential management
- Network segmentation

### Data Privacy
- Metric data anonymization
- Secure storage of monitoring data
- Compliance with data retention policies
- Encrypted communication channels

## Troubleshooting

### Common Issues

**1. Metrics Not Appearing in Prometheus**
```bash
# Check if metrics endpoint is responding
curl http://192.168.10.31:8000/metrics

# Check Prometheus configuration
curl http://192.168.10.37:9090/api/v1/targets

# Verify network connectivity
telnet 192.168.10.31 8000
```

**2. Webhooks Not Receiving Alerts**
```bash
# Test webhook endpoint
curl -X POST http://192.168.10.31:8000/webhooks/alerts \
  -H "Content-Type: application/json" \
  -d '{"alerts": []}'

# Check Alertmanager configuration
curl http://192.168.10.37:9093/api/v1/status

# Verify Citadel logs
tail -f /opt/citadel/logs/gateway.log
```

**3. Dashboard Not Loading Data**
```bash
# Check Grafana data source
curl http://192.168.10.37:3000/api/datasources

# Verify Prometheus connectivity from Grafana
curl http://192.168.10.37:9090/api/v1/query?query=up

# Check dashboard JSON configuration
```

### Log Analysis
```bash
# Citadel application logs
tail -f /opt/citadel/logs/gateway.log

# Service manager logs
journalctl -u citadel-metrics-exporter -f

# System logs
tail -f /var/log/syslog | grep citadel
```

## Maintenance

### Regular Tasks
- Monitor alert frequency and adjust thresholds
- Review and update dashboard configurations
- Analyze performance trends and optimize
- Update monitoring rules based on system changes

### Backup and Recovery
- Regular backup of monitoring configurations
- Database backup for historical metrics
- Dashboard configuration backup
- Alert rule backup and versioning

### Performance Optimization
- Optimize scrape intervals based on system load
- Tune alert thresholds to reduce noise
- Implement metric retention policies
- Monitor monitoring system performance

## Contact and Support

For issues with external monitoring integration:
1. Check this documentation for troubleshooting steps
2. Review application logs for error details
3. Test individual components for isolation
4. Escalate to infrastructure team if needed

## Changelog

- **2024-01-20**: Initial external monitoring integration
- **2024-01-20**: Added webhook automation for alert response
- **2024-01-20**: Deployed comprehensive Grafana dashboards
- **2024-01-20**: Integrated with external Prometheus/Alertmanager
