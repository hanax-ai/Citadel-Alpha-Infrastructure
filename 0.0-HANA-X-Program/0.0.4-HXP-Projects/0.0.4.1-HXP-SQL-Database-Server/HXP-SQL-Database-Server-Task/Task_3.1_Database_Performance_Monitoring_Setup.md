# Task 3.1: Database Performance Monitoring Setup

## Task Information

**Task Number:** 3.1  
**Task Title:** Database Performance Monitoring Setup  
**Created:** 2025-07-12  
**Assigned To:** Monitoring Team / Database Administrator  
**Priority:** High  
**Estimated Duration:** 120 minutes  

## Task Description

Configure comprehensive performance monitoring for PostgreSQL and Redis databases. This task establishes monitoring agents, exports real-time metrics to Prometheus, creates performance dashboards in Grafana, and configures alert thresholds for performance and availability to ensure optimal database operations.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Install monitoring agents, configure Prometheus export, create Grafana dashboards |
| **Measurable** | ✅ | Metrics exported to Prometheus, dashboards functional, alerts triggering properly |
| **Achievable** | ✅ | Standard monitoring setup with proven tools and integrations |
| **Relevant** | ✅ | Critical for maintaining database performance and availability |
| **Small** | ✅ | Focused on monitoring configuration for existing database services |
| **Testable** | ✅ | Metrics validation, dashboard verification, alert testing |

## Prerequisites

**Hard Dependencies:**
- Task 2.3: Enterprise Integration & API Configuration (Complete)
- Prometheus server available at 192.168.10.37
- Grafana server available at 192.168.10.37

**Soft Dependencies:**
- Alert notification systems (email, Slack, etc.)

**Conditional Dependencies:**
- Network connectivity to monitoring server
- Prometheus scrape permissions

## Configuration Requirements

**Environment Variables (.env):**
```
# Monitoring Configuration
PROMETHEUS_SERVER=192.168.10.37:9090
GRAFANA_SERVER=192.168.10.37:3000
POSTGRES_EXPORTER_PORT=9187
REDIS_EXPORTER_PORT=9121

# Alert Configuration
ALERT_MANAGER_URL=192.168.10.37:9093
SMTP_SERVER=smtp.company.com
ALERT_EMAIL=dba-alerts@company.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/webhook

# Monitoring Thresholds
POSTGRES_CONNECTION_THRESHOLD=800
POSTGRES_SLOW_QUERY_THRESHOLD=1000
REDIS_MEMORY_THRESHOLD=6GB
REDIS_LATENCY_THRESHOLD=10
```

**Configuration Files (.json/.yaml):**
```
/opt/citadel/monitoring/postgres-exporter.yaml - PostgreSQL metrics configuration
/opt/citadel/monitoring/redis-exporter.yaml - Redis metrics configuration
/etc/systemd/system/postgres-exporter.service - PostgreSQL exporter service
/etc/systemd/system/redis-exporter.service - Redis exporter service
/opt/citadel/grafana/dashboards/database-performance.json - Grafana dashboard
/opt/citadel/prometheus/rules/database-alerts.yml - Alert rules
```

**External Resources:**
- PostgreSQL Exporter
- Redis Exporter
- Grafana dashboard templates
- Prometheus alert manager

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 3.1.1 | Install monitoring agents | Install and configure PostgreSQL and Redis exporters | Exporters running and collecting metrics |
| 3.1.2 | Configure Prometheus integration | Setup metrics export to Prometheus server | Metrics visible in Prometheus |
| 3.1.3 | Create Grafana dashboards | Build performance dashboards with key metrics | Dashboards displaying real-time data |
| 3.1.4 | Configure alerting rules | Setup performance and availability alerts | Alerts triggering on threshold breaches |
| 3.1.5 | Validate monitoring system | Test all monitoring components | Complete monitoring visibility achieved |

## Success Criteria

**Primary Objectives:**
- [ ] Monitoring agents installed and configured for both databases
- [ ] Real-time metrics exported to Prometheus (192.168.10.37)
- [ ] Performance dashboards created in Grafana with key database metrics
- [ ] Alert thresholds configured for performance and availability
- [ ] Monitoring system validated and operational
- [ ] Historical data retention configured (30 days minimum)

**Validation Commands:**
```bash
# Verify exporters are running
sudo systemctl status postgres-exporter
sudo systemctl status redis-exporter
curl http://192.168.10.35:9187/metrics
curl http://192.168.10.35:9121/metrics

# Test Prometheus scraping
curl http://192.168.10.37:9090/api/v1/targets
curl http://192.168.10.37:9090/api/v1/query?query=pg_up

# Verify Grafana dashboards
curl -s http://192.168.10.37:3000/api/dashboards/db/database-performance

# Test alerting
curl -X POST http://192.168.10.37:9093/api/v1/alerts

# Check metrics collection
prometheus_query "rate(pg_stat_database_tup_inserted_total[5m])"
prometheus_query "redis_connected_clients"
```

**Expected Outputs:**
```
● postgres-exporter.service - PostgreSQL Metrics Exporter
   Active: active (running)

# HELP pg_up Whether the PostgreSQL server is up.
pg_up 1

{
  "activeTargets": [
    {
      "labels": {"instance": "192.168.10.35:9187", "job": "postgres"},
      "health": "up"
    }
  ]
}

{"dashboard": {"title": "Database Performance"}}

pg_stat_database_tup_inserted_total 1234.56
redis_connected_clients 42
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Monitoring overhead | Medium | Medium | Optimize collection intervals and metric selection |
| Alert fatigue | Medium | Medium | Properly tune thresholds and implement alert grouping |
| Network connectivity issues | Low | High | Implement local metric storage and buffering |
| Storage space for metrics | Medium | Medium | Configure retention policies and data compression |
| False positive alerts | Medium | Medium | Test and refine alert thresholds based on baselines |

## Rollback Procedures

**If Task Fails:**
1. Stop monitoring services: `sudo systemctl stop postgres-exporter redis-exporter`
2. Remove exporter configurations: `sudo rm -rf /opt/citadel/monitoring/`
3. Remove systemd services: `sudo rm /etc/systemd/system/*-exporter.service`
4. Remove Prometheus targets: Edit prometheus.yml to remove database targets
5. Reload systemd: `sudo systemctl daemon-reload`

**Rollback Validation:**
```bash
# Verify exporters are stopped
sudo systemctl status postgres-exporter  # Should show inactive
sudo systemctl status redis-exporter     # Should show inactive

# Verify metrics endpoints are unavailable
curl http://192.168.10.35:9187/metrics  # Should fail

# Check Prometheus targets
curl http://192.168.10.37:9090/api/v1/targets  # Should not show database targets
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Created | Pending | Task created from detailed task list |

## Dependencies This Task Enables

**Next Tasks:**
- Task 3.2: Centralized Logging & Audit Implementation
- Task 3.3: Performance Optimization & Tuning

**Parallel Candidates:**
- Task 3.2: Centralized Logging & Audit Implementation (can run in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Exporter connection failures | Metrics show "down" status | Check database credentials and connectivity |
| Missing metrics in Prometheus | Targets not scraped | Verify scrape configuration and network access |
| Dashboard not loading | Grafana shows no data | Check data source configuration and queries |
| Alerts not triggering | No notifications received | Verify alert rules and notification channels |
| High monitoring overhead | Database performance impact | Reduce collection frequency and metric scope |

**Debug Commands:**
```bash
# Debug PostgreSQL exporter
sudo journalctl -u postgres-exporter -f
curl -v http://192.168.10.35:9187/metrics

# Debug Redis exporter
sudo journalctl -u redis-exporter -f
curl -v http://192.168.10.35:9121/metrics

# Check Prometheus configuration
curl http://192.168.10.37:9090/api/v1/status/config
curl http://192.168.10.37:9090/api/v1/status/targets

# Debug Grafana
sudo journalctl -u grafana-server -f
curl -v http://192.168.10.37:3000/api/health

# Test database connectivity from exporters
psql -h 192.168.10.35 -U postgres_exporter -d postgres -c "SELECT 1;"
redis-cli -h 192.168.10.35 ping
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in 02-HXP-SQL-Database-Server-Task-List.md
- [ ] Create result summary document: `Task_3.1_Monitoring_Setup_Results.md`
- [ ] Document monitoring endpoints and dashboard URLs

**Result Document Location:**
- Save to: `/0.0.4.1-HXP-SQL-Database-Server/HXP-SQL-Database-Server-Task/results/Task_3.1_Monitoring_Setup_Results.md`

**Notification Requirements:**
- [ ] Notify operations team of monitoring dashboard availability
- [ ] Update alert notification groups with new database alerts
- [ ] Communicate monitoring endpoints to development teams

## Notes

- Performance monitoring is essential for maintaining database SLA and identifying issues proactively
- Real-time metrics enable rapid response to performance degradation or availability issues
- Historical data collection supports capacity planning and trend analysis
- Alert thresholds should be based on actual performance baselines rather than arbitrary values
- Dashboard design should focus on key performance indicators relevant to AI workloads

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
