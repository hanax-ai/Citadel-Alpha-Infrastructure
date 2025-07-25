# External Monitoring Integration for HX-Server-02

This document describes the complete integration of HX-Server-02 Citadel infrastructure with external Prometheus/Grafana monitoring at 192.168.10.37.

## Architecture Overview

```
External Monitoring Infrastructure (192.168.10.37)
├── Prometheus (:9090) - Metrics collection and alerting rules
├── Grafana (:3000) - Dashboard visualization and analysis
├── Alertmanager (:9093) - Alert routing and notifications
└── Node Exporter (:9100) - System metrics collection

HX-Server-02 (192.168.10.31)
├── Citadel Gateway (:8000) - Main application with metrics endpoints
├── Ollama Service (:11434) - LLM inference engine
├── PostgreSQL (:5432) - Database with monitoring
└── Redis (:6379) - Caching layer with monitoring
```

## Integration Components

### 1. Metrics Collection

**Citadel Metrics Endpoint: `/metrics`**
- System metrics (CPU, memory, disk, network)
- GPU metrics (temperature, utilization, memory)
- Application metrics (request count, response time, errors)
- Database metrics (connections, query performance)
- Custom business metrics

**Health Check Endpoints:**
- `/health/` - Comprehensive health status
- `/health/quick` - Fast health check
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

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
  metrics_endpoint: "/metrics"
  metrics_interval: 30
  alerts_webhook: "/webhooks/alerts"
```

#### Prometheus Scrape Targets (`/opt/citadel/config/monitoring/prometheus/citadel-targets.yml`)
```yaml
- targets: ['192.168.10.31:8000']
  labels:
    job: citadel-gateway
    cluster: hx-server-02
    environment: production
    service: citadel-gateway
```

#### Alert Rules (`/opt/citadel/config/monitoring/prometheus/citadel-alerts.yml`)
- Service availability monitoring
- Resource utilization thresholds
- Performance degradation detection
- Database health monitoring
- GPU temperature monitoring

### 4. Grafana Dashboards

**Available Dashboards:**
- HX-Server-02 System Overview
- Citadel Application Metrics
- GPU Performance Monitoring
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
2. Network connectivity between HX-Server-02 and monitoring infrastructure
3. Citadel application deployed and running
4. Administrative access to both systems

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
  # Citadel Gateway metrics
  - job_name: 'citadel-hx-server-02'
    static_configs:
      - targets: ['192.168.10.31:8000']
        labels:
          cluster: 'hx-server-02'
          environment: 'production'
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  # Citadel health monitoring
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
# Test webhook integration
/opt/citadel/bin/test-webhook-integration

# Check metrics endpoint
curl http://192.168.10.31:8000/metrics

# Verify health checks
curl http://192.168.10.31:8000/health/

# Check active alerts
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
- **DiskSpaceLow** → Log cleanup automation
- **DatabaseConnectionsFull** → Connection pool restart
- **GPUTemperatureHigh** → Thermal throttling

### Warning Alerts (Monitoring)
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
