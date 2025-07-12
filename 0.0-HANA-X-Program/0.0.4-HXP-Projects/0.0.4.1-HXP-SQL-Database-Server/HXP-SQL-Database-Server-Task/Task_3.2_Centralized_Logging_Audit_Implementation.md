# Task 3.2: Centralized Logging & Audit Implementation

## Task Information

**Task Number:** 3.2  
**Task Title:** Centralized Logging & Audit Implementation  
**Created:** 2025-07-12  
**Assigned To:** Security Team / Database Administrator  
**Priority:** High  
**Estimated Duration:** 105 minutes  

## Task Description

Implement security and access logging for comprehensive audit trails. This task configures audit logs for all database operations and access events, establishes centralized log aggregation via Loki integration, implements security access control logs, and configures anomaly detection and alerting for the Citadel AI database infrastructure.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Configure audit logging, centralized aggregation, security logs, and anomaly detection |
| **Measurable** | ✅ | All database operations logged, logs aggregated in Loki, security events captured |
| **Achievable** | ✅ | Standard logging and audit configuration with proven tools |
| **Relevant** | ✅ | Critical for security compliance and operational visibility |
| **Small** | ✅ | Focused on logging and audit configuration for existing services |
| **Testable** | ✅ | Log generation tests, aggregation verification, alert validation |

## Prerequisites

**Hard Dependencies:**
- Task 3.1: Database Performance Monitoring Setup (Complete)
- Loki logging server available (integrated with monitoring stack)

**Soft Dependencies:**
- SIEM integration capabilities
- Log retention storage

**Conditional Dependencies:**
- Network connectivity to log aggregation server
- Log shipping agents and configurations

## Configuration Requirements

**Environment Variables (.env):**
```
# Logging Configuration
LOKI_SERVER=192.168.10.37:3100
LOG_RETENTION_DAYS=90
LOG_LEVEL=INFO
AUDIT_LOG_ENABLED=true

# PostgreSQL Logging
POSTGRES_LOG_DESTINATION=csvlog
POSTGRES_LOG_CONNECTIONS=on
POSTGRES_LOG_DISCONNECTIONS=on
POSTGRES_LOG_STATEMENT=all
POSTGRES_LOG_MIN_DURATION=100

# Redis Logging
REDIS_LOG_LEVEL=notice
REDIS_SYSLOG_ENABLED=yes
REDIS_SLOWLOG_MAX_LEN=1000

# Security Logging
SECURITY_LOG_PATH=/var/log/citadel/security.log
FAILED_AUTH_THRESHOLD=5
ANOMALY_DETECTION_ENABLED=true
```

**Configuration Files (.json/.yaml):**
```
/etc/postgresql/17/main/postgresql.conf - PostgreSQL logging configuration
/etc/redis/redis.conf - Redis logging configuration
/opt/citadel/logging/promtail.yaml - Log shipping configuration
/opt/citadel/logging/loki-config.yaml - Loki integration settings
/opt/citadel/security/audit-rules.yaml - Security audit rules
/etc/rsyslog.d/citadel-database.conf - System log routing
```

**External Resources:**
- Promtail for log shipping
- Loki for log aggregation
- Security audit frameworks
- Anomaly detection tools (e.g., fail2ban)

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 3.2.1 | Configure database audit logging | Enable comprehensive logging in PostgreSQL and Redis | All operations and access events logged |
| 3.2.2 | Setup log aggregation | Configure Promtail and Loki integration | Logs flowing to centralized system |
| 3.2.3 | Implement security logging | Configure access control and security event logging | Security events captured and alerted |
| 3.2.4 | Configure anomaly detection | Setup automated anomaly detection and alerting | Suspicious activities detected automatically |
| 3.2.5 | Validate audit system | Test logging, aggregation, and alerting | Complete audit trail operational |

## Success Criteria

**Primary Objectives:**
- [ ] Audit logs configured for all database operations and access events
- [ ] Centralized log aggregation via Loki integration operational
- [ ] Security access control logs implemented
- [ ] Anomaly detection and alerting configured
- [ ] Log retention policies implemented (90 days minimum)
- [ ] Audit trail integrity verification enabled

**Validation Commands:**
```bash
# Verify PostgreSQL logging
sudo tail -f /var/log/postgresql/postgresql-17-main.log
sudo -u postgres psql -c "SELECT name, setting FROM pg_settings WHERE name LIKE 'log%';"

# Verify Redis logging
sudo tail -f /var/log/redis/redis-server.log
redis-cli SLOWLOG GET 10

# Test log aggregation
curl -G -s "http://192.168.10.37:3100/loki/api/v1/query" --data-urlencode 'query={job="postgresql"}'

# Check security logging
sudo tail -f /var/log/citadel/security.log
sudo journalctl -u fail2ban -f

# Verify audit events
sudo ausearch -m SYSCALL -f /var/lib/postgresql
psql -h 192.168.10.35 -U invalid_user -d citadel_ai  # Generate failed auth event
```

**Expected Outputs:**
```
2025-07-12 12:00:00.000 UTC [1234] LOG: connection authorized: user=citadel_admin database=citadel_ai
2025-07-12 12:00:01.000 UTC [1234] LOG: statement: SELECT version();

1) 1) (integer) 123456
   2) (integer) 1000
   3) 1) "SELECT"

{
  "status": "success",
  "data": {
    "result": [
      {
        "stream": {"job": "postgresql"},
        "values": [["1642000000000000000", "connection authorized"]]
      }
    ]
  }
}

SECURITY_EVENT: Failed authentication attempt from 192.168.10.31
fail2ban.filter: INFO    [postgresql] Found 192.168.10.31
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Log storage exhaustion | Medium | High | Implement log rotation and retention policies |
| Performance impact from logging | Medium | Medium | Optimize log levels and asynchronous logging |
| Log tampering or deletion | Low | High | Implement log integrity checks and secure storage |
| Sensitive data in logs | Medium | High | Configure log sanitization and encryption |
| Alert fatigue from false positives | Medium | Medium | Tune anomaly detection thresholds |

## Rollback Procedures

**If Task Fails:**
1. Disable verbose logging: Reset PostgreSQL and Redis log levels to minimal
2. Stop log shipping: `sudo systemctl stop promtail`
3. Remove audit configurations: `sudo rm -f /opt/citadel/security/audit-rules.yaml`
4. Reset logging configuration: `sudo cp postgresql.conf.backup postgresql.conf`
5. Restart database services: `sudo systemctl restart postgresql redis`

**Rollback Validation:**
```bash
# Verify logging is reduced
sudo tail -f /var/log/postgresql/postgresql-17-main.log  # Should show minimal logs
sudo systemctl status promtail  # Should be stopped

# Verify audit system is disabled
sudo ausearch -m SYSCALL -f /var/lib/postgresql  # Should show no new events
sudo systemctl status fail2ban  # Should be stopped or not monitoring database
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Created | Pending | Task created from detailed task list |

## Dependencies This Task Enables

**Next Tasks:**
- Task 3.3: Performance Optimization & Tuning
- Task 4.2: Security & Compliance Validation

**Parallel Candidates:**
- Task 3.3: Performance Optimization & Tuning (can run in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Log shipping failures | Logs not appearing in Loki | Check Promtail configuration and network connectivity |
| Excessive log volume | High disk usage, performance impact | Adjust log levels and implement proper rotation |
| Missing security events | Security incidents not logged | Verify audit rules and permissions |
| False positive alerts | Too many anomaly alerts | Tune detection thresholds and baseline behavior |
| Log parsing errors | Garbled or incomplete logs | Fix log format configuration and encoding |

**Debug Commands:**
```bash
# Debug log shipping
sudo journalctl -u promtail -f
curl -v http://192.168.10.37:3100/ready

# Check log file permissions and rotation
ls -la /var/log/postgresql/
sudo logrotate -d /etc/logrotate.d/postgresql

# Debug audit system
sudo ausearch -m SYSCALL -ts recent
sudo systemctl status auditd

# Test anomaly detection
sudo fail2ban-client status postgresql
sudo tail -f /var/log/fail2ban.log

# Check disk usage for logs
df -h /var/log/
du -sh /var/log/postgresql/
du -sh /var/log/redis/
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in 02-HXP-SQL-Database-Server-Task-List.md
- [ ] Create result summary document: `Task_3.2_Logging_Audit_Results.md`
- [ ] Document log retention policies and audit procedures

**Result Document Location:**
- Save to: `/0.0.4.1-HXP-SQL-Database-Server/HXP-SQL-Database-Server-Task/results/Task_3.2_Logging_Audit_Results.md`

**Notification Requirements:**
- [ ] Notify security team of audit logging implementation
- [ ] Update compliance team about audit trail capabilities
- [ ] Communicate log aggregation endpoints to operations team

## Notes

- Comprehensive audit logging is essential for security compliance and incident investigation
- Centralized log aggregation enables correlation across multiple systems and services
- Security event logging provides early warning of potential threats and attacks
- Anomaly detection helps identify unusual patterns that may indicate security issues
- Log retention policies must balance storage costs with compliance requirements

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
