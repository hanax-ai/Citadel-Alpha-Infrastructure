# Task 1.2: Redis 8.0.3 Installation & Base Configuration

## Task Information

**Task Number:** 1.2  
**Task Title:** Redis 8.0.3 Installation & Base Configuration  
**Created:** 2025-07-12  
**Assigned To:** System Administrator  
**Priority:** High  
**Estimated Duration:** 75 minutes  

## Task Description

Install and configure Redis 8.0.3 for optimal performance on the hx-sql-database-server (192.168.10.35). This task establishes the high-performance caching layer that supports all AI workloads, session management, and real-time analytics within the Citadel AI Operating System architecture.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Install Redis 8.0.3 with enterprise configuration on 192.168.10.35 |
| **Measurable** | ✅ | Redis responds to ping, info command shows version 8.0.3, all data structures verified |
| **Achievable** | ✅ | Redis 8.0.3 is stable and compatible with Ubuntu 24.04 LTS |
| **Relevant** | ✅ | Critical component for AI workload caching and session management |
| **Small** | ✅ | Single component installation with base configuration |
| **Testable** | ✅ | Connection tests, performance validation, data structure verification |

## Prerequisites

**Hard Dependencies:**
- Task 0.1: Hardware & Network Infrastructure Validation (Complete)
- Task 0.2: Security Framework & Access Control Setup (Complete)

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
REDIS_PASSWORD=<secure_password>
REDIS_PORT=6379
REDIS_MAX_MEMORY=8gb
REDIS_BIND_ADDRESS=192.168.10.35
```

**Configuration Files (.json/.yaml):**
```
/etc/redis/redis.conf - Main Redis configuration
/etc/systemd/system/redis.service - Redis systemd service configuration
/etc/security/limits.conf - System limits for Redis optimization
```

**External Resources:**
- Redis 8.0.3 package repository
- SSL certificates for secure connections

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 1.2.1 | Install Redis 8.0.3 | `sudo apt update && sudo apt install redis-server=8.0.3*` | Redis service installed and running |
| 1.2.2 | Configure memory optimization | Edit /etc/redis/redis.conf for enterprise workloads | Memory settings optimized for 8GB allocation |
| 1.2.3 | Enable persistence | Configure RDB and AOF persistence | Persistence enabled and validated |
| 1.2.4 | Security hardening | Configure authentication and network binding | Authentication enabled, bound to 192.168.10.35 |
| 1.2.5 | Service configuration | Configure systemd service for auto-start | Service enabled and starts on boot |

## Success Criteria

**Primary Objectives:**
- [ ] Redis 8.0.3 installed and running with enterprise configuration
- [ ] Memory optimization configured for enterprise workloads (8GB allocation)
- [ ] Persistence enabled for critical session data (RDB + AOF)
- [ ] All Redis data structures and pub/sub functionality verified
- [ ] Service accessible from network and responds to commands

**Validation Commands:**
```bash
# Verify Redis installation and version
redis-cli --version
sudo systemctl status redis

# Test Redis connectivity and functionality
redis-cli ping
redis-cli info server
redis-cli info memory

# Test data structures
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli lpush test_list "item1" "item2"
redis-cli lrange test_list 0 -1

# Test pub/sub functionality
redis-cli publish test_channel "test_message"
```

**Expected Outputs:**
```
redis-cli 8.0.3
● redis.service - Advanced key-value store
   Active: active (running)

PONG
redis_version:8.0.3
used_memory_human:2.50M
maxmemory_human:8.00G

OK
"test_value"
(integer) 2
1) "item2"
2) "item1"
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Memory exhaustion under load | Medium | High | Configure appropriate maxmemory and eviction policies |
| Data loss on restart | Low | High | Enable both RDB and AOF persistence |
| Security vulnerabilities | Medium | High | Configure authentication, bind to specific IP, firewall rules |
| Performance degradation | Low | Medium | Optimize memory allocation and disable unnecessary features |

## Rollback Procedures

**If Task Fails:**
1. Stop Redis service: `sudo systemctl stop redis`
2. Remove Redis packages: `sudo apt remove redis-server redis-tools`
3. Remove configuration files: `sudo rm -rf /etc/redis/`
4. Remove data directory: `sudo rm -rf /var/lib/redis/`
5. Restore original system state

**Rollback Validation:**
```bash
# Verify Redis is completely removed
sudo systemctl status redis  # Should show "could not be found"
redis-cli ping  # Should show "command not found"
ls /etc/redis/  # Should show "No such file or directory"
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Created | Pending | Task created from detailed task list |

## Dependencies This Task Enables

**Next Tasks:**
- Task 1.3: Initial Database Schema & Configuration Management
- Task 2.1: High Availability & Clustering Configuration

**Parallel Candidates:**
- None (Task 1.1 should be completed first for proper sequencing)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Redis fails to start | Service status shows failed | Check configuration syntax, verify permissions |
| Memory warnings | Redis logs show memory errors | Adjust maxmemory settings in redis.conf |
| Connection refused | Cannot connect via redis-cli | Verify bind address and firewall rules |
| Performance issues | Slow response times | Check memory usage, optimize configuration |

**Debug Commands:**
```bash
# Check Redis service status and logs
sudo systemctl status redis
sudo journalctl -u redis -f

# Check Redis configuration
redis-cli config get "*"
redis-cli info all

# Monitor Redis performance
redis-cli --latency-history
redis-cli monitor
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in 02-HXP-SQL-Database-Server-Task-List.md
- [ ] Create result summary document: `Task_1.2_Redis_Installation_Results.md`
- [ ] Update Redis configuration documentation

**Result Document Location:**
- Save to: `/0.0.4.1-HXP-SQL-Database-Server/HXP-SQL-Database-Server-Task/results/Task_1.2_Redis_Installation_Results.md`

**Notification Requirements:**
- [ ] Notify Task 1.3 owner that Redis is ready for schema configuration
- [ ] Update project status dashboard
- [ ] Communicate Redis availability to dependent services

## Notes

- Redis 8.0.3 includes enhanced security features and performance improvements
- Memory optimization is critical for supporting concurrent AI workloads
- Persistence configuration balances performance with data durability requirements
- Network binding to 192.168.10.35 enables secure access from other Citadel AI services

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
