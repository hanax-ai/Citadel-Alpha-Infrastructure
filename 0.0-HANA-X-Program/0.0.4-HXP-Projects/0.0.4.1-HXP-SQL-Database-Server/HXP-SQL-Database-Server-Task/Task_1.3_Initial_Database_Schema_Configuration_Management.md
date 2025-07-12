# Task 1.3: Initial Database Schema & Configuration Management

## Task Information

**Task Number:** 1.3  
**Task Title:** Initial Database Schema & Configuration Management  
**Created:** 2025-07-12  
**Assigned To:** Database Administrator  
**Priority:** High  
**Estimated Duration:** 105 minutes  

## Task Description

Establish schema management and configuration frameworks for both PostgreSQL and Redis. This task creates the foundational database schemas for AI applications, implements version control for database changes, and configures connection pooling middleware to support enterprise-scale concurrent access.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Implement schema versioning, configuration management, AI schemas, and connection pooling |
| **Measurable** | ✅ | Schema deployment tests pass, configuration validation succeeds, connection pool operational |
| **Achievable** | ✅ | Standard database administration tasks with established tools |
| **Relevant** | ✅ | Essential for AI application data storage and enterprise database management |
| **Small** | ✅ | Focused on initial schema setup and management framework |
| **Testable** | ✅ | Schema migration tests, configuration validation, connection pool verification |

## Prerequisites

**Hard Dependencies:**
- Task 1.1: PostgreSQL 17.5 Installation & Base Configuration (Complete)
- Task 1.2: Redis 8.0.3 Installation & Base Configuration (Complete)

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
POSTGRES_DB=citadel_ai
POSTGRES_USER=citadel_admin
POSTGRES_PASSWORD=<secure_password>
POSTGRES_HOST=192.168.10.35
POSTGRES_PORT=5432
REDIS_URL=redis://192.168.10.35:6379
PGPOOL_PORT=5433
PGPOOL_MAX_CONNECTIONS=1000
```

**Configuration Files (.json/.yaml):**
```
/etc/postgresql/17/main/postgresql.conf - PostgreSQL main configuration
/etc/pgpool-II/pgpool.conf - Connection pool configuration
/var/lib/postgresql/schemas/ - Schema migration directory
/opt/citadel/config/database.yaml - Application database configuration
```

**External Resources:**
- Flyway or similar migration tool
- PgPool-II for connection pooling
- Schema definition files for AI applications

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 1.3.1 | Install migration tools | Install Flyway for schema versioning | Migration tool ready for use |
| 1.3.2 | Create initial AI schemas | Create schemas for AI models, sessions, logs | Core schemas created and verified |
| 1.3.3 | Configure connection pooling | Install and configure PgPool-II | Connection pool operational with 1000+ connections |
| 1.3.4 | Setup configuration management | Create centralized config management | Configuration files versioned and deployable |
| 1.3.5 | Validate schema deployment | Test migration and rollback procedures | Schema changes can be applied and rolled back |

## Success Criteria

**Primary Objectives:**
- [ ] Schema versioning and migration capabilities implemented
- [ ] Configuration management system established
- [ ] Initial database schemas for AI applications created
- [ ] Connection pooling middleware configured for 1000+ concurrent connections
- [ ] Schema deployment and rollback procedures validated

**Validation Commands:**
```bash
# Verify PostgreSQL schemas
sudo -u postgres psql -c "\l"
sudo -u postgres psql -d citadel_ai -c "\dt"

# Test connection pooling
psql -h 192.168.10.35 -p 5433 -U citadel_admin -d citadel_ai -c "SELECT version();"

# Verify schema migration
flyway info -url=jdbc:postgresql://192.168.10.35:5432/citadel_ai

# Test Redis schema access
redis-cli -h 192.168.10.35 info keyspace

# Validate configuration
cat /opt/citadel/config/database.yaml
```

**Expected Outputs:**
```
Database citadel_ai created
ai_models | table | citadel_admin
ai_sessions | table | citadel_admin
PostgreSQL 17.5 on x86_64-linux-gnu
Schema version: 1.0.0
db0:keys=0,expires=0
Configuration validated successfully
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Schema migration failure | Low | High | Test migrations on staging environment first |
| Connection pool exhaustion | Medium | High | Monitor connection usage, implement proper limits |
| Configuration conflicts | Medium | Medium | Use centralized configuration management |
| Data corruption during migration | Low | High | Always backup before schema changes |

## Rollback Procedures

**If Task Fails:**
1. Stop connection pool: `sudo systemctl stop pgpool`
2. Restore database backup: `sudo -u postgres pg_restore backup.sql`
3. Remove migration artifacts: `rm -rf /var/lib/postgresql/schemas/`
4. Reset PostgreSQL configuration: `sudo cp postgresql.conf.backup postgresql.conf`
5. Restart PostgreSQL: `sudo systemctl restart postgresql`

**Rollback Validation:**
```bash
# Verify rollback completion
sudo -u postgres psql -c "\l" | grep citadel_ai  # Should show original state
sudo systemctl status pgpool  # Should be stopped
flyway info  # Should show previous version
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Created | Pending | Task created from detailed task list |

## Dependencies This Task Enables

**Next Tasks:**
- Task 2.1: High Availability & Clustering Configuration
- Task 2.3: Enterprise Integration & API Configuration

**Parallel Candidates:**
- Task 2.2: Backup & Recovery System Implementation (can run in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Migration tool fails | Flyway connection errors | Verify database credentials and connectivity |
| Connection pool errors | PgPool startup failures | Check configuration syntax and port conflicts |
| Schema creation fails | SQL syntax errors | Validate schema SQL files before deployment |
| Configuration mismatch | Application connection failures | Verify environment variables and config files |

**Debug Commands:**
```bash
# Check database connectivity
sudo -u postgres psql -c "SELECT 1;"
telnet 192.168.10.35 5432

# Debug connection pooling
sudo journalctl -u pgpool -f
pgpool -n -d

# Validate schema files
sudo -u postgres psql -d citadel_ai -f schema.sql --dry-run

# Check configuration
sudo systemctl status postgresql
sudo systemctl status pgpool
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in 02-HXP-SQL-Database-Server-Task-List.md
- [ ] Create result summary document: `Task_1.3_Schema_Management_Results.md`
- [ ] Document schema structure and migration procedures

**Result Document Location:**
- Save to: `/0.0.4.1-HXP-SQL-Database-Server/HXP-SQL-Database-Server-Task/results/Task_1.3_Schema_Management_Results.md`

**Notification Requirements:**
- [ ] Notify Phase 2 task owners that database foundation is ready
- [ ] Update project status dashboard
- [ ] Communicate schema availability to development teams

## Notes

- Schema versioning enables safe database evolution across environments
- Connection pooling is critical for supporting 1000+ concurrent AI workload connections
- Initial AI schemas should include tables for model metadata, training data, and session management
- Configuration management ensures consistent deployment across development, staging, and production

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
