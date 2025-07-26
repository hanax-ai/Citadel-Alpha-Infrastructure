# LLM-02 Operations Manual

## Table of Contents
1. [System Startup and Shutdown](#system-startup-and-shutdown)
2. [Model Management](#model-management)
3. [API Gateway Operations](#api-gateway-operations)
4. [Monitoring and Health Checks](#monitoring-and-health-checks)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Emergency Procedures](#emergency-procedures)

## System Startup and Shutdown

### Normal Startup Procedure

1. **Environment Activation**
   ```bash
   cd /opt/citadel-02
   source activate_citadel.sh
   ```

2. **Health Check Before Startup**
   ```bash
   ./bin/production-health-check.sh
   ```

3. **Start Core Services**
   ```bash
   sudo systemctl start citadel-api-gateway
   sudo systemctl start citadel-model-manager
   sudo systemctl start citadel-monitoring
   ```

4. **Verify Model Availability**
   ```bash
   ollama list
   ./bin/citadel-status
   ```

5. **Start API Gateway**
   ```bash
   ./bin/start-api-gateway.sh
   ```

### Normal Shutdown Procedure

1. **Graceful API Gateway Shutdown**
   ```bash
   sudo systemctl stop citadel-api-gateway
   ```

2. **Stop Model Services**
   ```bash
   sudo systemctl stop citadel-model-manager
   ```

3. **Stop Supporting Services**
   ```bash
   sudo systemctl stop citadel-monitoring
   ```

## Model Management

### Available Models

| Model | Purpose | Resource Requirements | Status Command |
|-------|---------|----------------------|----------------|
| Yi-34B | Strategic Analysis | 32GB RAM, 4 CPU cores | `ollama show yi:34b` |
| DeepCoder-14B | Code Generation | 16GB RAM, 2 CPU cores | `ollama show deepcoder:14b` |
| Qwen-1.8B | Operational Efficiency | 4GB RAM, 1 CPU core | `ollama show qwen:1.8b` |
| DeepSeek-R1 | Competitive Intelligence | 24GB RAM, 3 CPU cores | `ollama show deepseek-r1` |
| JARVIS | Executive Intelligence | 20GB RAM, 3 CPU cores | `ollama show jarvis` |

### Model Operations

#### Check Model Status
```bash
# Check all models
ollama list

# Check specific model
ollama show <model-name>

# Check model performance
./bin/performance-test-suite.sh <model-name>
```

#### Restart Individual Model
```bash
# Stop model
ollama stop <model-name>

# Start model
ollama run <model-name>

# Verify model functionality
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "<model-name>", "prompt": "test", "stream": false}'
```

#### Model Health Monitoring
```bash
# Continuous health monitoring
./bin/citadel-health-monitor

# Performance metrics
./bin/citadel-status --performance

# Resource utilization
./bin/citadel-status --resources
```

## API Gateway Operations

### Gateway Management

#### Start API Gateway
```bash
# Standard startup
./bin/start-api-gateway.sh

# Debug mode startup
./bin/start-api-gateway.sh --debug

# Specify custom port
./bin/start-api-gateway.sh --port 8080
```

#### Gateway Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health status
curl http://localhost:8000/api/v2/health/detailed

# Model availability check
curl http://localhost:8000/api/v2/models/status
```

#### API Endpoint Testing
```bash
# Strategic analysis endpoint
curl -X POST http://localhost:8000/api/v2/strategic-analysis \
  -H "Content-Type: application/json" \
  -d '{"query": "analyze market trends", "model": "yi:34b"}'

# Code generation endpoint
curl -X POST http://localhost:8000/api/v2/code-generation \
  -H "Content-Type: application/json" \
  -d '{"query": "create REST API", "model": "deepcoder:14b"}'

# Operational efficiency endpoint
curl -X POST http://localhost:8000/api/v2/operational-efficiency \
  -H "Content-Type: application/json" \
  -d '{"query": "optimize performance", "model": "qwen:1.8b"}'
```

## Monitoring and Health Checks

### System Health Dashboard

#### Access Monitoring Interface
- **Executive Dashboard**: http://192.168.10.38/executive
- **Technical Dashboard**: http://192.168.10.37/technical
- **API Gateway Metrics**: http://localhost:8000/metrics

#### Key Metrics to Monitor

1. **Response Times**
   - Strategic Analysis: < 5 seconds
   - Code Generation: < 3 seconds
   - Operational Efficiency: < 1 second
   - Competitive Intelligence: < 7 seconds
   - Executive Intelligence: < 4 seconds

2. **Resource Utilization**
   - CPU Usage: < 80%
   - Memory Usage: < 85%
   - Disk Usage: < 90%
   - Network Latency: < 100ms

3. **Business Intelligence Metrics**
   - Request Volume: Track daily/hourly patterns
   - Success Rate: > 99%
   - User Satisfaction: Track query resolution rates

### Automated Monitoring

#### Enable Continuous Monitoring
```bash
# Start monitoring daemon
sudo systemctl enable citadel-monitoring
sudo systemctl start citadel-monitoring

# Verify monitoring status
./bin/citadel-health-monitor --status
```

#### Alert Configuration
```bash
# Configure email alerts
./bin/citadel-config --alerts --email admin@company.com

# Configure Slack alerts
./bin/citadel-config --alerts --slack webhook-url

# Test alert system
./bin/citadel-health-monitor --test-alerts
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Model Not Responding

**Symptoms:**
- API calls timeout
- Model status shows "not available"
- High CPU usage on model process

**Diagnosis:**
```bash
# Check model status
ollama list
ollama show <model-name>

# Check resource usage
top -p $(pgrep ollama)
df -h
free -h
```

**Solution:**
```bash
# Restart specific model
ollama stop <model-name>
sleep 10
ollama run <model-name>

# If issue persists, restart Ollama service
sudo systemctl restart ollama
```

#### Issue: API Gateway Connection Errors

**Symptoms:**
- Connection refused errors
- Gateway not responding to health checks
- 502/503 HTTP errors

**Diagnosis:**
```bash
# Check gateway process
ps aux | grep api-gateway
netstat -tlnp | grep :8000

# Check gateway logs
tail -f logs/gateway/api-gateway.log
```

**Solution:**
```bash
# Restart API gateway
sudo systemctl restart citadel-api-gateway

# If issue persists, restart with debug mode
./bin/start-api-gateway.sh --debug --log-level DEBUG
```

#### Issue: Poor Response Performance

**Symptoms:**
- Response times > expected thresholds
- High latency in business intelligence queries
- Users reporting slow responses

**Diagnosis:**
```bash
# Check system resources
./bin/citadel-status --performance
./bin/performance-test-suite.sh

# Check model-specific performance
curl -w "@time_format.txt" -X POST http://localhost:8000/api/v2/strategic-analysis
```

**Solution:**
```bash
# Optimize model allocation
./bin/citadel-config --optimize-resources

# Clear caches if needed
./bin/citadel-service-manager --clear-cache

# Consider scaling up resources
./bin/citadel-config --scale-up <model-name>
```

#### Issue: External Service Integration Failures

**Symptoms:**
- PostgreSQL connection errors
- Vector database timeouts
- Monitoring service unavailable

**Diagnosis:**
```bash
# Test external connections
./scripts/validate-monitoring-config.sh

# Check network connectivity
ping 192.168.10.35  # PostgreSQL
ping 192.168.10.30  # Vector DB
ping 192.168.10.37  # Monitoring
```

**Solution:**
```bash
# Restart external service connections
./bin/citadel-service-manager --restart-integrations

# Verify service configurations
./bin/citadel-config --validate-external-services
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Maintenance
```bash
# Check system health
./bin/production-health-check.sh

# Review error logs
tail -100 logs/errors/error.log

# Check disk space
df -h
du -sh logs/
```

#### Weekly Maintenance
```bash
# Performance analysis
./bin/performance-test-suite.sh --full-report

# Log rotation
./bin/citadel-service-manager --rotate-logs

# Security updates check
./bin/citadel-config --check-security-updates
```

#### Monthly Maintenance
```bash
# Full system backup
./bin/citadel-service-manager --backup-system

# Performance optimization
./bin/citadel-config --optimize-performance

# Model performance analysis
./bin/performance-test-suite.sh --benchmark-all-models
```

### Configuration Updates

#### Update Model Configuration
```bash
# Edit model configurations
vim config/models/model_config.yaml

# Validate configuration
./bin/citadel-config --validate

# Apply configuration changes
./bin/citadel-service-manager --reload-config
```

#### Update API Gateway Configuration
```bash
# Edit gateway configuration
vim config/services/api_gateway.yaml

# Test configuration
./bin/citadel-config --test-gateway-config

# Apply changes with zero downtime
./bin/citadel-deploy --rolling-update gateway
```

## Emergency Procedures

### Critical System Failure

#### Immediate Response
1. **Assess Impact**
   ```bash
   ./bin/citadel-status --emergency-check
   ```

2. **Notify Stakeholders**
   ```bash
   ./bin/citadel-config --emergency-notify
   ```

3. **Implement Temporary Solutions**
   ```bash
   # Redirect to backup systems if available
   ./bin/citadel-deploy --failover
   ```

#### Recovery Procedures
1. **Diagnose Root Cause**
   ```bash
   # Collect diagnostic information
   ./bin/citadel-health-monitor --emergency-diagnostic
   
   # Review critical logs
   tail -1000 logs/system/system.log
   tail -1000 logs/errors/critical.log
   ```

2. **Implement Fix**
   ```bash
   # Apply emergency patches
   ./bin/citadel-deploy --emergency-patch
   
   # Restart affected services
   ./bin/citadel-service-manager --emergency-restart
   ```

3. **Verify Recovery**
   ```bash
   # Comprehensive system test
   ./bin/production-health-check.sh --full
   
   # Test all business intelligence endpoints
   ./bin/performance-test-suite.sh --verify-recovery
   ```

### Data Recovery

#### Vector Database Recovery
```bash
# Restore from backup
./bin/citadel-service-manager --restore-vectors --backup-date YYYY-MM-DD

# Rebuild vector collections if needed
./bin/citadel-service-manager --rebuild-vectors
```

#### Configuration Recovery
```bash
# Restore configuration from backup
./bin/citadel-config --restore-config --backup-date YYYY-MM-DD

# Reset to default configuration if needed
./bin/citadel-config --factory-reset --confirm
```

### Contact Information

#### Emergency Contacts
- **System Administrator**: admin@company.com
- **Technical Lead**: tech-lead@company.com
- **Business Stakeholder**: business@company.com

#### Support Resources
- **Documentation**: /opt/citadel-02/documentation/
- **Log Files**: /opt/citadel-02/logs/
- **Configuration**: /opt/citadel-02/config/

This operations manual provides comprehensive guidance for managing the LLM-02 system in production environments. For additional support, refer to the system architecture documentation and API reference guides.
