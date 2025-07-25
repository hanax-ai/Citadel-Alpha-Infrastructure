# Post-Deployment Testing and Verification Guide

## Comprehensive testing procedures for Citadel LLM monitoring stack

## Overview

This guide provides systematic testing procedures to validate the complete monitoring infrastructure deployment, including Prometheus, Grafana, Alertmanager, and HX-Server-02 integration.

## Testing Phases

### Phase 1: Infrastructure Connectivity

#### Duration: 5-10 minutes

#### 1.1 Network Connectivity Tests

```bash
# Test basic connectivity to all services
nc -z 192.168.10.37 9090  # Prometheus
nc -z 192.168.10.37 3000  # Grafana
nc -z 192.168.10.37 9093  # Alertmanager
nc -z 192.168.10.28 8001  # HX-Server-02 Gateway

# Test with timeout
timeout 10 telnet 192.168.10.37 9090
```

#### 1.2 HTTP Endpoint Tests

```bash
# Prometheus
curl -s http://192.168.10.37:9090 | grep -i prometheus
curl -s http://192.168.10.37:9090/api/v1/status/config

# Grafana
curl -s http://192.168.10.37:3000 | grep -i grafana
curl -s http://192.168.10.37:3000/api/health

# Alertmanager
curl -s http://192.168.10.37:9093 | grep -i alertmanager
curl -s http://192.168.10.37:9093/api/v1/status

# HX-Server-02
curl -s http://192.168.10.28:8001/health
curl -s http://192.168.10.28:8001/metrics
```

### Phase 2: Service Discovery and Metrics Collection

#### Duration: 10-15 minutes (Phase 4)

#### 2.1 Prometheus Target Discovery

```bash
# Check targets status
curl -s http://192.168.10.37:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, health: .health}'

# Verify HX-Server-02 target
curl -s http://192.168.10.37:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.instance=="192.168.10.28:8001")'
```

#### 2.2 Metrics Availability

```bash
# Test key metrics
METRICS=(
    "up"
    "citadel_requests_total"
    "citadel_response_time_seconds"
    "citadel_active_connections"
    "citadel_db_connections"
    "citadel_llm_requests"
)

for metric in "${METRICS[@]}"; do
    echo "Testing metric: $metric"
    curl -s "http://192.168.10.37:9090/api/v1/query?query=$metric" | jq '.data.result[0]'
done
```

#### 2.3 Label and Dimension Verification

```bash
# Check metric labels
curl -s "http://192.168.10.37:9090/api/v1/label/__name__/values" | jq '.data[] | select(. | contains("citadel_"))'

# Check instance labels
curl -s "http://192.168.10.37:9090/api/v1/query?query=up" | jq '.data.result[] | .metric | {instance: .instance, job: .job}'
```

### Phase 3: Grafana Dashboard Validation

#### Duration: 15-20 minutes (Phase 3)

#### 3.1 Datasource Connectivity

```bash
# Test Prometheus datasource
curl -s -u admin:admin http://192.168.10.37:3000/api/datasources | jq '.[] | select(.type=="prometheus") | {name: .name, url: .url, access: .access}'

# Test datasource proxy
curl -s -u admin:admin "http://192.168.10.37:3000/api/datasources/proxy/1/api/v1/query?query=up"
```

#### 3.2 Dashboard Import Verification

```bash
# List all dashboards
curl -s -u admin:admin http://192.168.10.37:3000/api/search?type=dash-db | jq '.[] | {title: .title, uid: .uid, type: .type}'

# Test specific dashboard data
DASHBOARD_UID="llm-performance"  # Example UID
curl -s -u admin:admin "http://192.168.10.37:3000/api/dashboards/uid/$DASHBOARD_UID"
```

#### 3.3 Panel Data Validation

```bash
# Test panel queries (simulate Grafana panel requests)
QUERIES=(
    "rate(citadel_requests_total[5m])"
    "histogram_quantile(0.95, rate(citadel_response_time_seconds_bucket[5m]))"
    "citadel_active_connections"
    "rate(citadel_db_connections_total[5m])"
)

for query in "${QUERIES[@]}"; do
    echo "Testing query: $query"
    curl -s "http://192.168.10.37:9090/api/v1/query?query=$query" | jq '.data.result | length'
done
```

### Phase 4: Alert Rule Validation

#### Duration: 10-15 minutes (Phase 4: Alert Rule Validation)

#### 4.1 Alert Rules Status

```bash
# Check all alert rules
curl -s http://192.168.10.37:9090/api/v1/rules | jq '.data.groups[] | {name: .name, rules: (.rules | length)}'

# Check specific rule groups
curl -s http://192.168.10.37:9090/api/v1/rules | jq '.data.groups[] | select(.name=="citadel-alerts") | .rules[] | {alert: .name, state: .state}'
```

#### 4.2 Alert Evaluation

```bash
# Check currently firing alerts
curl -s http://192.168.10.37:9090/api/v1/alerts | jq '.data.alerts[] | {alertname: .labels.alertname, state: .state, value: .value}'

# Test alert query expressions
ALERT_QUERIES=(
    "up{job=\"citadel-gateway\"} == 0"
    "rate(citadel_requests_total{status=\"500\"}[5m]) > 0.1"
    "citadel_response_time_seconds{quantile=\"0.95\"} > 2"
)

for query in "${ALERT_QUERIES[@]}"; do
    echo "Testing alert query: $query"
    curl -s "http://192.168.10.37:9090/api/v1/query?query=$query" | jq '.data.result'
done
```

### Phase 5: Alertmanager Integration

#### Duration: 10-15 minutes (Phase 5: Alertmanager Integration)

#### 5.1 Alertmanager Configuration

```bash
# Check Alertmanager status
curl -s http://192.168.10.37:9093/api/v1/status | jq '.data | {cluster: .cluster, uptime: .uptime}'

# Verify receivers configuration
curl -s http://192.168.10.37:9093/api/v1/status | jq '.data.configYAML' | grep -A 10 "receivers:"
```

#### 5.2 Webhook Testing

```bash
# Test webhook endpoints
WEBHOOK_URLS=(
    "http://192.168.10.28:8001/webhooks/alerts"
    "http://192.168.10.31:8002/webhooks/alerts"
)

for url in "${WEBHOOK_URLS[@]}"; do
    echo "Testing webhook: $url"
    curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d '{"test": "alert", "status": "resolved"}' \
        -w "Status: %{http_code}\n"
done
```

#### 5.3 Silence and Inhibition Testing

```bash
# Check active silences
curl -s http://192.168.10.37:9093/api/v1/silences | jq '.data[] | {id: .id, status: .status.state, matchers: .matchers}'

# Test silence creation (example)
curl -X POST http://192.168.10.37:9093/api/v1/silences \
    -H "Content-Type: application/json" \
    -d '{
        "matchers": [{"name": "alertname", "value": "TestAlert", "isRegex": false}],
        "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
        "endsAt": "'$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%S.%3NZ)'",
        "createdBy": "test-validation",
        "comment": "Validation test silence"
    }'
```

### Phase 6: Auto-Recovery Testing

#### Duration: 15-20 minutes

#### 6.1 Service Recovery Simulation

```bash
# Test automatic restart functionality
ssh root@192.168.10.28 "
    echo 'Testing auto-recovery...'
    
    # Get current PID
    CURRENT_PID=\$(systemctl show citadel-gateway --property MainPID --value)
    echo 'Current PID: '\$CURRENT_PID
    
    # Kill the process (simulate crash)
    kill -9 \$CURRENT_PID
    echo 'Process killed, waiting for restart...'
    
    # Wait for restart
    sleep 10
    
    # Check new PID
    NEW_PID=\$(systemctl show citadel-gateway --property MainPID --value)
    echo 'New PID: '\$NEW_PID
    
    # Verify service is running
    systemctl is-active citadel-gateway
    
    # Check restart count
    systemctl show citadel-gateway --property NRestarts --value
"
```

#### 6.2 Health Check Recovery

```bash
# Monitor health during recovery
for i in {1..20}; do
    echo "Health check attempt $i:"
    curl -s http://192.168.10.28:8001/health | jq '.status' || echo "Not responding"
    sleep 3
done
```

### Phase 7: Load Testing and Performance

#### Duration: 20-30 minutes

#### 7.1 Metrics Under Load

```bash
# Generate load and monitor metrics
for i in {1..100}; do
    curl -s http://192.168.10.28:8001/api/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model": "test", "messages": [{"role": "user", "content": "test"}]}' &
done

# Wait for requests to complete
wait

# Check metrics impact
sleep 30
curl -s "http://192.168.10.37:9090/api/v1/query?query=rate(citadel_requests_total[1m])" | jq '.data.result[0].value[1]'
```

#### 7.2 Resource Monitoring

```bash
# Monitor resource usage during load
ssh root@192.168.10.28 "
    echo 'CPU and Memory usage:'
    top -bn1 | grep citadel
    
    echo 'Connection counts:'
    netstat -an | grep :8001 | wc -l
    
    echo 'Disk I/O:'
    iostat -x 1 1 | grep -A 1 'Device'
"
```

### Phase 8: Data Retention and Storage

#### Duration: 10-15 minutes

#### 8.1 Prometheus Data Retention

```bash
# Check Prometheus storage metrics
curl -s "http://192.168.10.37:9090/api/v1/query?query=prometheus_tsdb_head_samples_appended_total" | jq '.data.result[0].value[1]'

# Check disk usage
ssh root@192.168.10.37 "
    df -h /var/lib/prometheus
    du -sh /var/lib/prometheus/data
"
```

#### 8.2 Grafana Data Storage

```bash
# Check Grafana database
ssh root@192.168.10.37 "
    sqlite3 /var/lib/grafana/grafana.db '.tables'
    sqlite3 /var/lib/grafana/grafana.db 'SELECT COUNT(*) FROM dashboard;'
"
```

## Automated Validation Script

The complete validation can be run using the automated script:

```bash
# Run comprehensive validation
/opt/citadel-02/scripts/monitoring/validation-suite.sh

# Run with verbose output
/opt/citadel-02/scripts/monitoring/validation-suite.sh 2>&1 | tee validation-results.log
```

## Success Criteria

### ✅ Minimum Requirements

- All services accessible (Prometheus, Grafana, Alertmanager, HX-Server-02)
- Metrics collection active (>95% of expected metrics)
- Dashboards loading with data
- Alert rules loaded and evaluating
- Auto-recovery functional (service restarts within 10 seconds)

### 🎯 Optimal Performance

- Response times <500ms for all endpoints
- Metrics collection at 15-second intervals
- Dashboard refresh <2 seconds
- Alert evaluation <1 minute
- Auto-recovery <5 seconds
- Zero data loss during recovery

### 🔍 Troubleshooting Checklist

#### Service Not Starting

```bash
# Check service status
systemctl status prometheus grafana-server alertmanager citadel-gateway

# Check logs
journalctl -u prometheus -f
journalctl -u grafana-server -f
journalctl -u alertmanager -f
journalctl -u citadel-gateway -f

# Check ports
netstat -tuln | grep -E ':(9090|3000|9093|8001)'
```

#### Metrics Not Collecting

```bash
# Check Prometheus targets
curl -s http://192.168.10.37:9090/api/v1/targets

# Check firewall
ufw status
iptables -L

# Check network connectivity
ping 192.168.10.28
traceroute 192.168.10.28
```

#### Dashboards Not Loading

```bash
# Check Grafana logs
tail -f /var/log/grafana/grafana.log

# Check datasource connection
curl -s -u admin:admin http://192.168.10.37:3000/api/datasources/proxy/1/api/v1/status/config

# Verify dashboard files
ls -la /var/lib/grafana/dashboards/
```

#### Alerts Not Firing

```bash
# Check alert rules syntax
curl -s http://192.168.10.37:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.state=="INVALID")'

# Test alert queries manually
curl -s "http://192.168.10.37:9090/api/v1/query?query=up{job=\"citadel-gateway\"} == 0"

# Check Alertmanager routing
curl -s http://192.168.10.37:9093/api/v1/status | jq '.data.configYAML'
```

## Performance Benchmarks

### Expected Metrics Volume

- **Total metrics per scrape**: ~500-1000 metrics
- **Scrape frequency**: Every 15 seconds
- **Data points per hour**: ~240,000-480,000
- **Storage growth**: ~100-500MB per day

### Response Time Targets

- **Prometheus queries**: <200ms (simple), <2s (complex)
- **Grafana dashboard load**: <3s
- **Alert evaluation**: <30s
- **Webhook delivery**: <5s

### Resource Usage Expectations

- **CPU**: 10-30% average, 50% peak
- **Memory**: 2-8GB depending on retention
- **Disk I/O**: <100 IOPS sustained
- **Network**: <10Mbps sustained

## Maintenance and Monitoring

### Daily Checks

```bash
# Quick health check
curl -s http://192.168.10.37:9090/-/healthy
curl -s http://192.168.10.37:3000/api/health
curl -s http://192.168.10.37:9093/-/healthy
curl -s http://192.168.10.28:8001/health

# Check for failed alerts
curl -s http://192.168.10.37:9090/api/v1/alerts | jq '.data.alerts[] | select(.state=="firing")'
```

### Weekly Checks

```bash
# Storage usage
df -h /var/lib/prometheus /var/lib/grafana

# Log rotation
find /var/log -name "*.log" -size +100M

# Performance metrics
curl -s "http://192.168.10.37:9090/api/v1/query?query=rate(prometheus_engine_query_duration_seconds_sum[7d])"
```

### Monthly Maintenance

```bash
# Cleanup old data
# (Handled automatically by retention policies)

# Update dashboards
# (Manual process - import new JSON files)

# Review and optimize alert rules
# (Review alert frequency and accuracy)

# Capacity planning
# (Monitor growth trends and resource usage)
```

This comprehensive testing guide ensures complete validation of the monitoring infrastructure and provides ongoing maintenance procedures for optimal performance.
