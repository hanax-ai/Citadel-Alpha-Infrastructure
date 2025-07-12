# Task 5.1: Citadel AI OS Service Integration

## Task Information

**Task Number:** 5.1  
**Task Title:** Citadel AI OS Service Integration  
**Created:** 2025-07-12  
**Assigned To:** DevOps Team / System Administrator  
**Priority:** High  
**Estimated Duration:** 90 minutes  

## Task Description

Integrate database services with unified Citadel AI OS service management. This task configures database services to be controlled via the unified service management system, enables status monitoring through centralized commands, implements centralized logging access, and establishes health validation through automated health check scripts.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Integrate with unified service management, centralized monitoring, and health checks |
| **Measurable** | ✅ | Service controls functional, status monitoring operational, health checks pass |
| **Achievable** | ✅ | Standard service integration with established management frameworks |
| **Relevant** | ✅ | Critical for unified Citadel AI OS management and operations |
| **Small** | ✅ | Focused on service integration with existing management infrastructure |
| **Testable** | ✅ | Service command tests, status verification, health check validation |

## Prerequisites

**Hard Dependencies:**
- Task 4.3: Integration & Load Testing (Complete)
- Citadel AI OS service management framework available

**Soft Dependencies:**
- Unified logging and monitoring infrastructure
- Service orchestration platform

**Conditional Dependencies:**
- Service management scripts and configurations
- Centralized health monitoring systems

## Configuration Requirements

**Environment Variables (.env):**
```
# Citadel AI OS Integration
CITADEL_SERVICE_NAME=citadel-ai-os
SERVICE_MANAGEMENT_PATH=/opt/citadel/services
HEALTH_CHECK_INTERVAL=30
SERVICE_TIMEOUT=60

# Database Service Configuration
POSTGRES_SERVICE_NAME=citadel-postgresql
REDIS_SERVICE_NAME=citadel-redis
PGPOOL_SERVICE_NAME=citadel-pgpool
SERVICE_GROUP=citadel-database

# Monitoring Integration
HEALTH_CHECK_SCRIPT=/opt/citadel/scripts/management/health_check.sh
LOG_AGGREGATION_PATH=/opt/citadel/logs
STATUS_ENDPOINT=http://localhost:8080/status
```

**Configuration Files (.json/.yaml):**
```
/etc/systemd/system/citadel-ai-os.service - Unified service definition
/opt/citadel/services/database-services.yaml - Database service configuration
/opt/citadel/scripts/management/health_check.sh - Health validation script
/opt/citadel/scripts/management/service_control.sh - Service control script
/etc/systemd/system/citadel-database.target - Service dependency target
```

**External Resources:**
- Systemd service management
- Health monitoring frameworks
- Log aggregation systems
- Service orchestration tools

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 5.1.1 | Configure unified service control | Setup citadel-ai-os service management | Services controlled via unified commands |
| 5.1.2 | Implement centralized status monitoring | Configure status monitoring integration | Status accessible via unified commands |
| 5.1.3 | Setup centralized logging access | Configure log aggregation and access | Logs accessible via centralized commands |
| 5.1.4 | Configure health validation system | Setup automated health check scripts | Health validation operational |
| 5.1.5 | Validate service integration | Test all unified management functions | All service management functions operational |

## Success Criteria

**Primary Objectives:**
- [ ] Database services controlled via `sudo systemctl start citadel-ai-os`
- [ ] Status monitoring through `sudo systemctl status citadel-ai-os`
- [ ] Centralized logging accessible via `journalctl -u citadel-ai-os -f`
- [ ] Health validation through `./scripts/management/health_check.sh`
- [ ] All database services integrated into unified management framework
- [ ] Service dependencies and startup order properly configured

**Validation Commands:**
```bash
# Test unified service control
sudo systemctl start citadel-ai-os
sudo systemctl stop citadel-ai-os
sudo systemctl restart citadel-ai-os

# Test status monitoring
sudo systemctl status citadel-ai-os
sudo systemctl is-active citadel-ai-os

# Test centralized logging
sudo journalctl -u citadel-ai-os -f --no-pager
sudo journalctl -u citadel-ai-os --since "1 hour ago"

# Test health validation
/opt/citadel/scripts/management/health_check.sh
/opt/citadel/scripts/management/health_check.sh --detailed

# Test service dependencies
systemctl list-dependencies citadel-ai-os
systemctl show citadel-ai-os
```

**Expected Outputs:**
```
● citadel-ai-os.service - Citadel AI Operating System
   Loaded: loaded (/etc/systemd/system/citadel-ai-os.service; enabled)
   Active: active (running) since Fri 2025-07-12 12:00:00 UTC; 5min ago
   
active

Jul 12 12:00:00 citadel-db systemd[1]: Started Citadel AI Operating System
Jul 12 12:00:01 citadel-db citadel-ai-os[1234]: Database services initialized
Jul 12 12:00:02 citadel-db citadel-ai-os[1234]: Health checks passed

Health Check Results:
=====================
PostgreSQL: HEALTHY (Response: 15ms)
Redis: HEALTHY (Response: 2ms)
PgPool: HEALTHY (Active connections: 150)
Overall Status: HEALTHY

citadel-ai-os.service
├─citadel-postgresql.service
├─citadel-redis.service
└─citadel-pgpool.service
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Service startup failures | Medium | High | Implement proper dependency management and startup order |
| Health check false positives | Medium | Medium | Tune health check thresholds and implement retry logic |
| Logging configuration issues | Low | Medium | Test log aggregation and verify log rotation |
| Service management conflicts | Low | High | Ensure proper service isolation and dependency management |
| Performance impact from monitoring | Low | Medium | Optimize health check frequency and resource usage |

## Rollback Procedures

**If Task Fails:**
1. Stop unified service: `sudo systemctl stop citadel-ai-os`
2. Disable unified service: `sudo systemctl disable citadel-ai-os`
3. Restore individual services: `sudo systemctl start postgresql redis pgpool`
4. Remove service files: `sudo rm /etc/systemd/system/citadel-ai-os.service`
5. Reload systemd: `sudo systemctl daemon-reload`

**Rollback Validation:**
```bash
# Verify unified service is stopped and disabled
sudo systemctl status citadel-ai-os  # Should show inactive/disabled

# Verify individual services are running
sudo systemctl status postgresql redis pgpool
sudo -u postgres psql -c "SELECT 1;"
redis-cli ping

# Verify service files are removed
ls /etc/systemd/system/citadel-ai-os.service  # Should not exist
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Created | Pending | Task created from detailed task list |

## Dependencies This Task Enables

**Next Tasks:**
- Task 5.2: Operational Readiness & Documentation

**Parallel Candidates:**
- None (final integration step before operational readiness)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Service startup failures | citadel-ai-os fails to start | Check service dependencies and startup scripts |
| Health check failures | Health checks report unhealthy services | Verify service status and health check configuration |
| Logging not working | No logs appearing in journalctl | Check service configuration and log permissions |
| Status monitoring issues | Status commands show incorrect information | Verify service definitions and status scripts |
| Dependency conflicts | Services start in wrong order | Review and fix service dependencies |

**Debug Commands:**
```bash
# Debug service startup
sudo journalctl -u citadel-ai-os -f
sudo systemctl cat citadel-ai-os
sudo systemd-analyze verify citadel-ai-os.service

# Debug health checks
/opt/citadel/scripts/management/health_check.sh --debug
bash -x /opt/citadel/scripts/management/health_check.sh

# Debug logging
sudo journalctl --no-pager | grep citadel
ls -la /opt/citadel/logs/

# Debug service dependencies
systemctl list-dependencies citadel-ai-os --all
systemctl show citadel-ai-os --property=Requires,Wants,After,Before

# Check service status
systemctl is-system-running
systemctl --failed
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in 02-HXP-SQL-Database-Server-Task-List.md
- [ ] Create result summary document: `Task_5.1_Service_Integration_Results.md`
- [ ] Document unified service management procedures

**Result Document Location:**
- Save to: `/0.0.4.1-HXP-SQL-Database-Server/HXP-SQL-Database-Server-Task/results/Task_5.1_Service_Integration_Results.md`

**Notification Requirements:**
- [ ] Notify operations team of unified service management availability
- [ ] Update system administrators on new service control procedures
- [ ] Communicate integration completion to stakeholders

## Notes

- Unified service management simplifies operations and maintenance procedures
- Centralized logging provides consolidated view of all database service activities
- Health validation enables proactive monitoring and issue detection
- Service integration enables automated startup, shutdown, and dependency management
- Proper service management is essential for production operations and maintenance

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
