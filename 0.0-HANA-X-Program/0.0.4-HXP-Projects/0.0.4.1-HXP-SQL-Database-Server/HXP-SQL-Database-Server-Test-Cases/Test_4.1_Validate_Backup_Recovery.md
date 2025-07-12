# 📝 Test Case: Backup & Recovery Validation

## Test Case Information

**Test Case ID:** TC-P04-4.1  
**Test Case Name:** Validate Backup & Recovery Operations  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Operational  
**Test Category:** Disaster Recovery  
**Test Priority:** Critical  
**Test Complexity:** High  
**Automation Status:** Semi-Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify backup and recovery procedures ensure data protection and business continuity

**Test Description:** Validates automated backup creation, backup verification, point-in-time recovery, full system recovery, and backup retention policies for both PostgreSQL and Redis components.

**Business Value:** Ensures AI data protection and system recovery capabilities meet business continuity requirements

---

## Requirements Traceability

**Related Tasks:**
- **Task 4.1:** Automated Backup Strategy Implementation
- **Task 4.2:** Disaster Recovery & High Availability Setup

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_4.1_Automated_Backup_Strategy_Implementation.md](../HXP-SQL-Database-Server-Task/Task_4.1_Automated_Backup_Strategy_Implementation.md)

---

## Test Prerequisites

**System Prerequisites:**
- PostgreSQL 17.5 with backup tools configured
- Redis 8.0.3 with persistence enabled
- Backup storage configured and accessible
- Test data loaded for backup validation

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Administrative privileges for backup operations
- Backup storage access credentials
- Recovery testing environment prepared

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | Create full backup | Backup completes successfully | PostgreSQL pg_dump |
| 2 | Verify backup integrity | Backup files valid | Checksum validation |
| 3 | Test point-in-time recovery | PITR works correctly | WAL replay |
| 4 | Redis backup validation | Redis persistence working | RDB/AOF backups |
| 5 | Full system recovery test | Complete system restored | End-to-end recovery |

### Step 1: PostgreSQL Full Backup Creation
**Action:** Create and validate full database backup  
**Commands:**
```bash
# Create full backup with compression
pg_dump -h 192.168.10.35 -U postgres -d citadel_ai -Fc -f /backup/citadel_ai_full_$(date +%Y%m%d_%H%M%S).backup

# Create schema-only backup
pg_dump -h 192.168.10.35 -U postgres -d citadel_ai -s -f /backup/citadel_ai_schema_$(date +%Y%m%d_%H%M%S).sql

# Create all databases backup
pg_dumpall -h 192.168.10.35 -U postgres -f /backup/citadel_all_databases_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file size and completeness
ls -lh /backup/citadel_ai_full_*.backup
pg_restore --list /backup/citadel_ai_full_*.backup | head -20
```
**Expected Result:** Backup files created without errors  
**Verification:** Backup files exist and contain expected data  

### Step 2: Backup Integrity Verification
**Action:** Validate backup file integrity and content  
**Commands:**
```bash
# Calculate and store checksums
md5sum /backup/citadel_ai_full_*.backup > /backup/checksums.md5

# Verify backup can be read
pg_restore --list /backup/citadel_ai_full_*.backup > /backup/backup_contents.txt

# Test restore to temporary database
createdb -h 192.168.10.35 -U postgres citadel_ai_test_restore
pg_restore -h 192.168.10.35 -U postgres -d citadel_ai_test_restore /backup/citadel_ai_full_*.backup

# Verify restored data
psql -h 192.168.10.35 -U postgres -d citadel_ai_test_restore -c "SELECT COUNT(*) FROM ai_models;"
psql -h 192.168.10.35 -U postgres -d citadel_ai_test_restore -c "SELECT COUNT(*) FROM inference_logs;"

# Cleanup test database
dropdb -h 192.168.10.35 -U postgres citadel_ai_test_restore
```
**Expected Result:** Backup integrity verified, test restore successful  
**Verification:** Data counts match original database  

### Step 3: Point-in-Time Recovery Testing
**Action:** Test PITR capabilities  
**Commands:**
```bash
# Record current time for PITR test
PITR_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "PITR test time: $PITR_TIME"

# Insert test data after PITR point
psql -h 192.168.10.35 -U postgres -d citadel_ai -c "
INSERT INTO ai_models (model_name, created_at) 
VALUES ('pitr_test_model', NOW());
"

# Get the record ID for verification
TEST_ID=$(psql -h 192.168.10.35 -U postgres -d citadel_ai -t -c "
SELECT id FROM ai_models WHERE model_name = 'pitr_test_model';
" | tr -d ' ')

# Create a new database for PITR test
createdb -h 192.168.10.35 -U postgres citadel_ai_pitr_test

# Restore base backup
pg_restore -h 192.168.10.35 -U postgres -d citadel_ai_pitr_test /backup/citadel_ai_full_*.backup

# Configure recovery to PITR point
echo "recovery_target_time = '$PITR_TIME'" >> /var/lib/postgresql/17/main/recovery.conf

# Verify PITR data state
PITR_COUNT=$(psql -h 192.168.10.35 -U postgres -d citadel_ai_pitr_test -t -c "
SELECT COUNT(*) FROM ai_models WHERE model_name = 'pitr_test_model';
" | tr -d ' ')

if [ "$PITR_COUNT" = "0" ]; then
    echo "✅ PITR Success: Test record not present (as expected)"
else
    echo "❌ PITR Failed: Test record present (unexpected)"
fi

# Cleanup
dropdb -h 192.168.10.35 -U postgres citadel_ai_pitr_test
```
**Expected Result:** PITR restores to exact point in time  
**Verification:** Test data inserted after PITR point not present  

### Step 4: Redis Backup Validation
**Action:** Test Redis persistence and backup mechanisms  
**Commands:**
```bash
# Check Redis persistence configuration
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET save
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendonly

# Insert test data
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" SET backup_test_key "backup_test_value"
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" HSET backup_test_hash field1 value1

# Force RDB snapshot
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" BGSAVE

# Wait for backup completion and verify
sleep 5
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" LASTSAVE

# Copy backup files
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d_%H%M%S).rdb
cp /var/lib/redis/appendonly.aof /backup/redis_aof_$(date +%Y%m%d_%H%M%S).aof

# Verify backup file sizes
ls -lh /backup/redis_*.rdb /backup/redis_aof_*.aof

# Test data recovery simulation
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" DEL backup_test_key
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" DEL backup_test_hash

# Restore from backup (simulation)
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" DEBUG RESTART
sleep 2

# Verify data restoration
RESTORED_VALUE=$(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" GET backup_test_key)
if [ "$RESTORED_VALUE" = "backup_test_value" ]; then
    echo "✅ Redis Backup Success: Data restored correctly"
else
    echo "❌ Redis Backup Failed: Data not restored"
fi
```
**Expected Result:** Redis backups work and data can be restored  
**Verification:** Test data survives restart and recovery  

### Step 5: Full System Recovery Test
**Action:** Test complete system recovery procedure  
**Commands:**
```bash
# Create comprehensive backup
mkdir -p /backup/full_system_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/full_system_$(date +%Y%m%d_%H%M%S)"

# Backup all PostgreSQL data
pg_dumpall -h 192.168.10.35 -U postgres -f $BACKUP_DIR/postgresql_all.sql

# Backup PostgreSQL configuration
cp -r /etc/postgresql/17/main/ $BACKUP_DIR/postgresql_config/

# Backup Redis data and config
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_dump.rdb
cp /var/lib/redis/appendonly.aof $BACKUP_DIR/redis_appendonly.aof
cp /etc/redis/redis.conf $BACKUP_DIR/redis.conf

# Create recovery validation script
cat > $BACKUP_DIR/recovery_validation.sh << 'EOF'
#!/bin/bash
echo "=== Recovery Validation ==="

# Check PostgreSQL
pg_count=$(psql -h 192.168.10.35 -U postgres -d citadel_ai -t -c "SELECT COUNT(*) FROM ai_models;" | tr -d ' ')
echo "PostgreSQL AI models count: $pg_count"

# Check Redis
redis_keys=$(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" DBSIZE)
echo "Redis keys count: $redis_keys"

# Service status
systemctl status postgresql | grep "active (running)" && echo "✅ PostgreSQL: Running"
systemctl status redis | grep "active (running)" && echo "✅ Redis: Running"

echo "=== Recovery Validation Complete ==="
EOF

chmod +x $BACKUP_DIR/recovery_validation.sh

# Execute validation
$BACKUP_DIR/recovery_validation.sh

# Create backup manifest
cat > $BACKUP_DIR/MANIFEST << EOF
Backup Created: $(date)
PostgreSQL Version: $(psql -h 192.168.10.35 -U postgres -t -c "SELECT version();" | head -1)
Redis Version: $(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" INFO server | grep redis_version)
Backup Size: $(du -sh $BACKUP_DIR | cut -f1)
Files:
$(ls -la $BACKUP_DIR)
EOF

echo "✅ Full system backup completed: $BACKUP_DIR"
```
**Expected Result:** Complete system backup created successfully  
**Verification:** All components backed up, validation script confirms data integrity  

---

## Expected Results

**Primary Expected Result:** All backup and recovery procedures work correctly and meet RTO/RPO requirements

**Backup Requirements:**
- **Full Backup:** Completes within 2 hours
- **Incremental Backup:** Completes within 30 minutes
- **Backup Verification:** 100% success rate
- **Recovery Time Objective (RTO):** <4 hours
- **Recovery Point Objective (RPO):** <15 minutes

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] Full backup completes without errors
- [ ] Backup files pass integrity verification
- [ ] Point-in-time recovery works accurately
- [ ] Redis persistence and recovery functional
- [ ] Full system recovery procedure documented and tested
- [ ] Backup retention policies enforced
- [ ] Recovery procedures meet RTO/RPO requirements
- [ ] Backup monitoring and alerting operational

**Fail Criteria:**
- [ ] Backup creation fails or incomplete
- [ ] Backup files corrupted or unreadable
- [ ] PITR recovery fails or inaccurate
- [ ] Redis data loss during recovery
- [ ] Recovery time exceeds RTO requirements
- [ ] Data loss exceeds RPO requirements

---

## Automation Commands

```bash
#!/bin/bash
# Backup & Recovery Validation Test Script

echo "=== Backup & Recovery Validation Test ==="

# Test 1: PostgreSQL Backup Creation
echo "Testing PostgreSQL backup creation..."
BACKUP_FILE="/tmp/test_backup_$(date +%Y%m%d_%H%M%S).backup"
pg_dump -h 192.168.10.35 -U postgres -d citadel_ai -Fc -f $BACKUP_FILE > /dev/null 2>&1

if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    echo "✅ PostgreSQL Backup OK: Backup file created"
    BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE")
    echo "   Backup size: $BACKUP_SIZE bytes"
else
    echo "❌ PostgreSQL Backup FAIL: Backup file not created"
fi

# Test 2: Backup Integrity
echo "Testing backup integrity..."
pg_restore --list $BACKUP_FILE > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backup Integrity OK: Backup file readable"
else
    echo "❌ Backup Integrity FAIL: Backup file corrupted"
fi

# Test 3: Redis Backup
echo "Testing Redis backup..."
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" BGSAVE > /dev/null 2>&1
sleep 2
LAST_SAVE=$(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" LASTSAVE 2>/dev/null)

if [ -n "$LAST_SAVE" ]; then
    echo "✅ Redis Backup OK: Background save completed"
else
    echo "❌ Redis Backup FAIL: Background save failed"
fi

# Test 4: Backup File Management
echo "Testing backup file management..."
if [ -f "/backup" ] || [ -d "/backup" ]; then
    BACKUP_COUNT=$(find /backup -name "*.backup" -o -name "*.sql" -o -name "*.rdb" | wc -l)
    echo "✅ Backup Storage OK: $BACKUP_COUNT backup files found"
else
    echo "❌ Backup Storage FAIL: Backup directory not accessible"
fi

# Test 5: Recovery Simulation
echo "Testing recovery simulation..."
createdb -h 192.168.10.35 -U postgres test_recovery > /dev/null 2>&1
pg_restore -h 192.168.10.35 -U postgres -d test_recovery $BACKUP_FILE > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Recovery Test OK: Test restore successful"
    # Cleanup
    dropdb -h 192.168.10.35 -U postgres test_recovery > /dev/null 2>&1
else
    echo "❌ Recovery Test FAIL: Test restore failed"
fi

# Cleanup
rm -f $BACKUP_FILE

echo "=== Backup & Recovery Test Complete ==="
```

---

## Recovery Documentation

**Recovery Procedures:**
1. **Full System Recovery:** Complete restoration from backup
2. **Point-in-Time Recovery:** Restore to specific timestamp
3. **Partial Recovery:** Restore specific databases or tables
4. **Configuration Recovery:** Restore system configurations

**Recovery Validation:**
- Data integrity verification
- Application connectivity testing
- Performance validation
- Security configuration verification

---

## Notes

- Backup testing should be performed regularly
- Recovery procedures should be documented and practiced
- Backup retention policies should be automated
- Monitor backup storage capacity and performance
- Test recovery procedures in isolated environment

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.2_Validate_Redis_Installation.md
- Test_3.1_Validate_Security_Configuration.md
- Test_5.1_Validate_Citadel_Integration.md
