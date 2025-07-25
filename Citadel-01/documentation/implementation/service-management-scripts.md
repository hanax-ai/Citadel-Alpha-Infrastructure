# Citadel Service Management Scripts Documentation

## Overview

This document describes the comprehensive service management and monitoring scripts created for Citadel's operational robustness (Task 4.1).

## Available Scripts

### 1. Citadel Service Manager (`citadel-service-manager`)
**Location:** `/opt/citadel/bin/citadel-service-manager`

**Purpose:** Centralized service control for all Citadel components

**Features:**
- Service dependency management
- Graceful start/stop/restart operations
- Service status monitoring
- Auto-start configuration
- Health checks integration
- Comprehensive logging

**Usage:**
```bash
./citadel-service-manager {start|stop|restart|status|health|logs|enable|disable} [service_name]
```

**Examples:**
```bash
# Show all service status
./citadel-service-manager status

# Start all services
./citadel-service-manager start

# Restart specific service
./citadel-service-manager restart citadel-gateway

# Run health checks
./citadel-service-manager health
```

### 2. Citadel Health Monitor (`citadel-health-monitor`)
**Location:** `/opt/citadel/bin/citadel-health-monitor`

**Purpose:** Continuous health monitoring with alerting and automated recovery

**Features:**
- Real-time health monitoring
- Configurable alert thresholds
- Automated recovery procedures
- Slack and email notifications
- Service response time monitoring
- Resource usage tracking

**Configuration:**
- Check interval: 60 seconds (configurable)
- Alert threshold: 3 consecutive failures
- Recovery: Enabled by default
- Supports Slack webhooks and email alerts

**Usage:**
```bash
./citadel-health-monitor {monitor|check|status|test-alert}
```

**Examples:**
```bash
# Start continuous monitoring
./citadel-health-monitor monitor

# Single health check
./citadel-health-monitor check

# Show current status
./citadel-health-monitor status
```

### 3. Citadel Log Manager (`citadel-log-manager`)
**Location:** `/opt/citadel/bin/citadel-log-manager`

**Purpose:** Centralized log management, rotation, and analysis

**Features:**
- Log viewing and following
- Pattern searching across all logs
- Automatic log rotation
- Log archiving and cleanup
- Error pattern analysis
- Disk usage monitoring

**Usage:**
```bash
./citadel-log-manager {view|tail|search|rotate|archive|clean|analyze|summary}
```

**Examples:**
```bash
# View log summary
./citadel-log-manager summary

# Follow gateway logs
./citadel-log-manager tail gateway 100

# Search for errors
./citadel-log-manager search "ERROR"

# Analyze log patterns
./citadel-log-manager analyze gateway
```

### 4. Citadel Performance Monitor (`citadel-performance-monitor`)
**Location:** `/opt/citadel/bin/citadel-performance-monitor`

**Purpose:** Real-time performance monitoring and metrics collection

**Features:**
- CPU, memory, and disk monitoring
- Service response time tracking
- Interactive dashboard
- Performance alerts
- Stress testing capabilities
- Metrics logging and reporting

**Configuration:**
- Default interval: 5 seconds
- CPU alert threshold: 80%
- Memory alert threshold: 85%
- Disk alert threshold: 90%

**Usage:**
```bash
./citadel-performance-monitor {monitor|report|alerts|dashboard|stress-test}
```

**Examples:**
```bash
# Start real-time monitoring for 10 minutes
./citadel-performance-monitor monitor 600

# Interactive dashboard
./citadel-performance-monitor dashboard

# Generate performance report
./citadel-performance-monitor report

# Show current alerts
./citadel-performance-monitor alerts
```

### 5. Citadel Operations Center (`citadel-ops-center`)
**Location:** `/opt/citadel/bin/citadel-ops-center`

**Purpose:** Unified management console for all operational tools

**Features:**
- Interactive menu system
- Quick access to all tools
- Emergency recovery procedures
- Comprehensive system reporting
- Maintenance mode capabilities

**Usage:**
```bash
./citadel-ops-center
```

**Menu Options:**
1. Service Status & Control
2. Health Monitoring
3. Performance Monitoring
4. Log Management
5. Quick Health Check
6. Full System Report
7. Emergency Recovery
8. Maintenance Mode
9. Real-time Dashboard
10. Performance Analytics
11. Error Analysis
12. Service Dependencies

## System Integration

### Systemd Service
A systemd service is provided for continuous health monitoring:

**Location:** `/opt/citadel/config/services/citadel-health-monitor.service`

**Installation:**
```bash
sudo cp /opt/citadel/config/services/citadel-health-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable citadel-health-monitor
sudo systemctl start citadel-health-monitor
```

### Log Directories
All scripts create and use organized log directories:

```
/opt/citadel/logs/
├── monitoring/
│   ├── health-check.log
│   ├── health-monitor.log
│   ├── service-management.log
│   └── performance-metrics.log
├── gateway/
├── backup/
├── deployment/
├── errors/
├── access/
├── audit/
└── archive/
```

### Service Dependencies
The service manager understands and respects service dependencies:

```
postgresql → (base service)
redis-server → (base service)
ollama → (base service)
nginx → postgresql, redis-server, ollama
citadel-gateway → postgresql, redis-server, ollama
```

## Monitoring Capabilities

### Health Checks
- Service status verification
- API endpoint response checks
- Database connectivity tests
- Redis connectivity tests
- System resource monitoring

### Performance Metrics
- CPU usage tracking
- Memory utilization monitoring
- Disk space monitoring
- Network connection statistics
- Service response times
- Process-specific metrics

### Alerting
- Configurable threshold-based alerts
- Slack webhook integration
- Email notification support
- Automated recovery actions
- Alert escalation procedures

## Maintenance Operations

### Log Management
- Automatic log rotation when files exceed 100MB
- Archive creation with timestamps
- Cleanup of logs older than 30 days
- Compression of archived logs

### Performance Optimization
- Real-time resource monitoring
- Stress testing capabilities
- Performance trend analysis
- Resource bottleneck identification

### Recovery Procedures
- Automated service restart on failure
- Emergency recovery mode
- Service dependency restoration
- Health verification post-recovery

## Security Features

### Access Control
- Scripts check for appropriate permissions
- Systemd service runs with minimal privileges
- Log file access restrictions
- Secure credential handling

### Monitoring
- Security event logging
- Failed service attempt tracking
- Unauthorized access detection
- Audit trail maintenance

## Customization

### Configuration Files
Most settings can be customized by editing the script variables:

- Alert thresholds
- Check intervals
- Retention periods
- Service definitions
- Notification endpoints

### Extension Points
- Custom health check endpoints
- Additional service definitions
- Custom alert handlers
- Extended metrics collection

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure scripts are executable: `chmod +x /opt/citadel/bin/*`
   - Run with appropriate privileges for systemd operations

2. **Service Not Found Errors**
   - Verify service names match systemd service files
   - Update service arrays in scripts if needed

3. **Health Check Failures**
   - Verify endpoints are accessible
   - Check network connectivity
   - Validate credentials for database connections

4. **Log Issues**
   - Ensure log directories exist
   - Check disk space availability
   - Verify write permissions

### Debugging
Enable debug mode by setting environment variables:

```bash
export LOG_LEVEL=DEBUG
export VERBOSE=true
```

## Integration with Existing Systems

### API Gateway Integration
Health monitoring integrates with the existing health endpoints:
- `/health/` - Comprehensive health check
- `/health/quick` - Fast health verification
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

### Database Integration
Connects to the configured PostgreSQL database:
- Host: 192.168.10.35
- Database: citadel_llm_db
- User: citadel_llm_user
- Uses credentials from `/opt/citadel/config/secrets/database-credentials.yaml`

### Service Integration
Monitors and manages all Citadel services:
- PostgreSQL database
- Redis cache
- Ollama LLM service
- Nginx web server
- Citadel Gateway application

## Future Enhancements

### Planned Features
- Grafana dashboard integration
- Prometheus metrics export
- Advanced alerting rules
- Automated scaling recommendations
- Predictive failure analysis
- Integration with cloud monitoring services

### Extensibility
The scripts are designed for easy extension:
- Modular architecture
- Configuration-driven behavior
- Plugin-style health checks
- Customizable alert handlers

## Conclusion

This comprehensive service management system provides:

✅ **Complete Service Control** - Start, stop, restart, and monitor all services
✅ **Proactive Health Monitoring** - Continuous monitoring with automated recovery
✅ **Centralized Log Management** - Unified logging, rotation, and analysis
✅ **Performance Monitoring** - Real-time metrics and alerting
✅ **Unified Operations Interface** - Single point of access for all operations
✅ **Emergency Recovery** - Automated and manual recovery procedures
✅ **Comprehensive Reporting** - Detailed system status and performance reports

The system is production-ready and provides the operational robustness required for HX-Server-02's mission-critical deployment.
