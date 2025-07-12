# Task 1.1: PostgreSQL 17.5 Installation & Base Configuration

## Task Information

**Task Number:** 1.1  
**Task Title:** PostgreSQL 17.5 Installation & Base Configuration  
**Created:** 2025-07-12  
**Assigned To:** Database Team  
**Priority:** High  
**Estimated Duration:** 90 minutes  

## Task Description

Install and configure PostgreSQL 17.5 with enterprise features on Ubuntu 24.04 LTS. This task establishes the core relational database service for the Citadel AI Operating System, including enterprise extensions, security hardening, and initial performance optimization for AI workloads.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | PostgreSQL 17.5 installation with defined enterprise extensions and security configuration |
| **Measurable** | ✅ | Success criteria include version verification, service status, connection tests |
| **Achievable** | ✅ | Standard PostgreSQL installation using official repositories and proven procedures |
| **Relevant** | ✅ | Core database component required for all AI services and business applications |
| **Small** | ✅ | Focused on PostgreSQL installation only, no clustering or advanced features |
| **Testable** | ✅ | Specific validation commands and functional tests clearly defined |

## Prerequisites

**Hard Dependencies:**
- Task 0.1: Hardware & Network Infrastructure Validation (must be 100% complete)
- Task 0.2: Security Framework & Access Control Setup (must be 100% complete)

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
POSTGRES_VERSION=17
POSTGRES_PORT=5432
POSTGRES_DATA_DIR=/var/lib/postgresql/17/main
POSTGRES_CONFIG_DIR=/etc/postgresql/17/main
POSTGRES_LOG_DIR=/var/log/postgresql
POSTGRES_USER=postgres
DB_ADMIN_USER=citadel_admin
DB_ADMIN_PASS=$(openssl rand -base64 32)
SSL_CERT_PATH=/etc/ssl/certs/hx-sql-database.crt
SSL_KEY_PATH=/etc/ssl/private/hx-sql-database.key
```

**Configuration Files (.json/.yaml):**
```
config/postgresql.conf - Main PostgreSQL configuration
config/pg_hba.conf - Host-based authentication rules
config/postgres-extensions.sql - Enterprise extensions installation script
```

**External Resources:**
- PostgreSQL official APT repository
- Enterprise SSL certificates (from Task 0.2)
- Database initialization scripts
- Performance tuning templates

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 1.1.1 | PostgreSQL Repository Setup | `sudo apt update`<br>`sudo apt install -y wget ca-certificates`<br>`wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -`<br>`echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list` | Repository added, GPG key verified |
| 1.1.2 | PostgreSQL 17.5 Installation | `sudo apt update`<br>`sudo apt install postgresql-17 postgresql-client-17 postgresql-contrib-17 -y` | PostgreSQL 17.5 installed, service running |
| 1.1.3 | Initial Security Configuration | `sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$(openssl rand -base64 32)';"` | postgres user password set, SSL enabled |
| 1.1.4 | Enterprise Extensions Setup | `sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"`<br>`sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"` | Core extensions installed and functional |
| 1.1.5 | Basic Performance Tuning | Edit `/etc/postgresql/17/main/postgresql.conf`<br>Set `shared_buffers = 8GB`, `effective_cache_size = 24GB` | Configuration optimized for hardware specs |

## Success Criteria

**Primary Objectives:**
- [ ] PostgreSQL 17.5 installed and running successfully
- [ ] Database service responds to local and network connections
- [ ] Enterprise extensions (JSON/JSONB, full-text search, analytics) operational
- [ ] SSL encryption enabled for all connections
- [ ] Initial security hardening implemented

**Validation Commands:**
```bash
# Verify PostgreSQL version and status
ssh citadel@192.168.10.35 'sudo systemctl status postgresql'
ssh citadel@192.168.10.35 'sudo -u postgres psql -c "SELECT version();"'

# Test local connection
ssh citadel@192.168.10.35 'sudo -u postgres psql -c "SELECT current_database();"'

# Test network connection (from another server)
psql -h 192.168.10.35 -U postgres -c "SELECT 1;" 

# Verify extensions
ssh citadel@192.168.10.35 'sudo -u postgres psql -c "SELECT name FROM pg_available_extensions WHERE installed_version IS NOT NULL;"'

# Check SSL configuration
ssh citadel@192.168.10.35 'sudo -u postgres psql -c "SHOW ssl;"'
```

**Expected Outputs:**
```
Service: postgresql.service - PostgreSQL RDBMS (active/running)
Version: PostgreSQL 17.5 on x86_64-pc-linux-gnu
Connection: Current database: postgres
Network: Successfully connected
Extensions: pgcrypto, pg_stat_statements, plpgsql (minimum)
SSL: ssl | on
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Package installation failures | Low | High | Use official PostgreSQL repository, verify package integrity |
| Service startup failures | Medium | High | Check system resources, review PostgreSQL logs |
| SSL configuration errors | Medium | Medium | Use certificates from Task 0.2, validate configuration syntax |
| Performance issues | Medium | Medium | Apply conservative tuning initially, monitor and adjust |
| Authentication problems | Low | High | Test both local and network authentication thoroughly |

## Rollback Procedures

**If Task Fails:**
1. Stop PostgreSQL service: `sudo systemctl stop postgresql`
2. Remove PostgreSQL packages: `sudo apt remove postgresql-17 postgresql-client-17 postgresql-contrib-17 -y`
3. Clean data directories: `sudo rm -rf /var/lib/postgresql/17 /etc/postgresql/17`
4. Remove repository: `sudo rm /etc/apt/sources.list.d/pgdg.list`
5. Update package cache: `sudo apt update`

**Rollback Validation:**
```bash
# Verify service removal
ssh citadel@192.168.10.35 'systemctl is-active postgresql'  # Should show inactive

# Check package removal
ssh citadel@192.168.10.35 'dpkg -l | grep postgresql'  # Should be empty or show only old versions

# Verify directory cleanup
ssh citadel@192.168.10.35 'ls -la /var/lib/postgresql/17 /etc/postgresql/17'  # Should show "No such file"

# Check port availability
ssh citadel@192.168.10.35 'ss -tuln | grep 5432'  # Should be empty
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Task Created | Ready | Template applied, ready for execution after Prerequisites |

## Dependencies This Task Enables

**Next Tasks:**
- Task 1.2: Redis 8.0.3 Installation & Base Configuration
- Task 1.3: Initial Database Schema & Configuration Management
- Task 2.1: High Availability & Clustering Configuration

**Parallel Candidates:**
- Task 1.2: Redis 8.0.3 Installation & Base Configuration (can run simultaneously after this completes)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Package installation fails | apt errors, dependency conflicts | Clear package cache: `sudo apt clean`, retry installation |
| Service won't start | systemctl start fails | Check logs: `sudo journalctl -u postgresql -n 50`, verify configuration |
| SSL connection errors | SSL handshake failures | Verify certificate paths, check file permissions |
| Memory allocation errors | shared_memory errors in logs | Reduce shared_buffers setting, check available memory |
| Network connection refused | Connection timeout from external hosts | Verify pg_hba.conf, check firewall rules |

**Debug Commands:**
```bash
# Check PostgreSQL logs
ssh citadel@192.168.10.35 'sudo tail -f /var/log/postgresql/postgresql-17-main.log'

# Verify configuration syntax
ssh citadel@192.168.10.35 'sudo -u postgres /usr/lib/postgresql/17/bin/postgres --check-config'

# Check listening ports
ssh citadel@192.168.10.35 'sudo ss -tuln | grep 5432'

# Test configuration reload
ssh citadel@192.168.10.35 'sudo systemctl reload postgresql'

# Check available memory
ssh citadel@192.168.10.35 'free -h; cat /proc/meminfo | grep -E "(MemTotal|MemAvailable)"'
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in `02-HXP-SQL-Database-Server-Task-List.md`
- [ ] Create result summary document: `Task_1.1_PostgreSQL_17.5_Installation_Base_Configuration_Results.md`
- [ ] Update database inventory documentation

**Result Document Location:**
- Save to: `/0.0-HANA-X-Program/0.0.4-HXP-Projects/0.0.4.1-HXP-SQL-Database-Server/tasks/results/Task_1.1_Results.md`

**Notification Requirements:**
- [ ] Notify Redis installation team that PostgreSQL is ready for parallel installation
- [ ] Update database status dashboard
- [ ] Communicate PostgreSQL readiness to application development teams

## Notes

PostgreSQL 17.5 provides the foundation for all relational data storage in the Citadel AI system. The installation includes enterprise-grade extensions optimized for AI workloads including JSON/JSONB processing, full-text search capabilities, and advanced analytics functions.

Configuration parameters are set conservatively for initial deployment. Performance tuning will be refined in Task 3.3 based on actual workload patterns. The SSL configuration integrates with certificates established in Task 0.2 to ensure encrypted connections for all database access.

This installation supports the target performance requirements of P95 query latency <50ms and 1000+ concurrent connections through proper shared memory allocation and connection pooling preparation.

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
