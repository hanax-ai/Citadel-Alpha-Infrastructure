# 📝 Test Case: Database Schema Validation

## Test Case Information

**Test Case ID:** TC-P01-1.3  
**Test Case Name:** Validate Initial Database Schema & Configuration Management  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Integration  
**Test Category:** Functional  
**Test Priority:** Critical  
**Test Complexity:** Moderate  
**Automation Status:** Semi-Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify database schema is correctly created and optimized for AI workloads and Citadel operations

**Test Description:** Validates the creation of initial database schema including AI-specific tables, indexes, partitioning strategies, and configuration management structures for optimal performance.

**Business Value:** Ensures database structure supports AI data processing, analytics, and operational requirements

---

## Requirements Traceability

**Related Tasks:**
- **Task 1.3:** Initial Database Schema & Configuration Management

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_1.3_Initial_Database_Schema_Configuration_Management.md](../HXP-SQL-Database-Server-Task/Task_1.3_Initial_Database_Schema_Configuration_Management.md)

---

## Test Prerequisites

**System Prerequisites:**
- PostgreSQL 17.5 installed and running
- Redis 8.0.3 installed and running
- Administrative database access

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Database superuser privileges
- Schema migration tools configured

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | Verify database creation | Citadel databases exist | Check all required DBs |
| 2 | Validate schema structure | All tables created | AI workload tables |
| 3 | Check indexes and constraints | Optimal indexing | Performance optimization |
| 4 | Test partitioning strategy | Partitions configured | Time-based partitioning |
| 5 | Validate configuration tables | Config management ready | System configuration |

### Step 1: Database Creation Verification
**Action:** Check required databases exist  
**Commands:**
```sql
\l -- List all databases
\c citadel_ai -- Connect to AI database
\c citadel_config -- Connect to config database
\c citadel_analytics -- Connect to analytics database
```
**Expected Result:** All Citadel databases present  
**Verification:** Databases exist and are accessible  

### Step 2: Schema Structure Validation
**Action:** Verify table structure  
**Commands:**
```sql
\c citadel_ai
\dt -- List tables
\d+ ai_models -- Describe AI models table
\d+ training_data -- Describe training data table
\d+ inference_logs -- Describe inference logs table
```
**Expected Result:** All AI workload tables exist with correct structure  
**Verification:** Tables have required columns and data types  

### Step 3: Index and Constraint Verification
**Action:** Check performance optimizations  
**Commands:**
```sql
-- Check indexes
\di -- List indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';

-- Check constraints
SELECT conname, contype FROM pg_constraint WHERE conrelid IN (
    SELECT oid FROM pg_class WHERE relname IN ('ai_models', 'training_data', 'inference_logs')
);
```
**Expected Result:** Optimal indexes and constraints configured  
**Verification:** Performance-critical indexes exist  

### Step 4: Partitioning Strategy Test
**Action:** Validate table partitioning  
**Commands:**
```sql
-- Check partitioned tables
SELECT schemaname, tablename, partitionname 
FROM pg_partitions 
WHERE tablename LIKE '%_log%' OR tablename LIKE '%_data%';

-- Test partition pruning
EXPLAIN (BUFFERS, ANALYZE) 
SELECT * FROM inference_logs 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';
```
**Expected Result:** Time-based partitioning working correctly  
**Verification:** Partition pruning reduces scan time  

### Step 5: Configuration Management Validation
**Action:** Test configuration tables  
**Commands:**
```sql
\c citadel_config
\dt -- List configuration tables
SELECT * FROM system_config LIMIT 5;
SELECT * FROM feature_flags LIMIT 5;
INSERT INTO system_config (key, value) VALUES ('test_key', 'test_value');
SELECT value FROM system_config WHERE key = 'test_key';
DELETE FROM system_config WHERE key = 'test_key';
```
**Expected Result:** Configuration management operational  
**Verification:** CRUD operations work correctly  

---

## Expected Results

**Primary Expected Result:** Database schema is correctly implemented and optimized for AI workloads

**Performance Expectations:**
- **Schema Creation:** <30 seconds
- **Index Queries:** <10ms for lookups
- **Partition Pruning:** >90% scan reduction
- **Config Operations:** <5ms response time

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] All required databases (citadel_ai, citadel_config, citadel_analytics) exist
- [ ] AI workload tables created with correct structure
- [ ] Performance indexes configured and operational
- [ ] Time-based partitioning working correctly
- [ ] Configuration management tables functional
- [ ] CRUD operations perform within SLA requirements

**Fail Criteria:**
- [ ] Missing required databases or tables
- [ ] Incorrect table structure or data types
- [ ] Missing or ineffective indexes
- [ ] Partitioning not configured or not working
- [ ] Configuration management operations fail

---

## Automation Commands

```bash
#!/bin/bash
# Database Schema Validation Test Script

echo "=== Database Schema Validation Test ==="

# Test 1: Database Existence
echo "Testing database existence..."
databases=$(sudo -u postgres psql -t -c "\l" | grep citadel | wc -l)
if [ "$databases" -ge 3 ]; then
    echo "✅ Databases OK: Found $databases Citadel databases"
else
    echo "❌ Databases FAIL: Expected at least 3, found $databases"
fi

# Test 2: Table Structure
echo "Testing table structure..."
ai_tables=$(sudo -u postgres psql -d citadel_ai -t -c "\dt" | grep -E "(ai_models|training_data|inference_logs)" | wc -l)
if [ "$ai_tables" -ge 3 ]; then
    echo "✅ Tables OK: AI workload tables present"
else
    echo "❌ Tables FAIL: Missing AI workload tables"
fi

# Test 3: Index Verification
echo "Testing indexes..."
indexes=$(sudo -u postgres psql -d citadel_ai -t -c "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public';" | tr -d ' ')
if [ "$indexes" -gt 0 ]; then
    echo "✅ Indexes OK: $indexes indexes found"
else
    echo "❌ Indexes FAIL: No indexes found"
fi

# Test 4: Configuration Tables
echo "Testing configuration management..."
config_test=$(sudo -u postgres psql -d citadel_config -t -c "
INSERT INTO system_config (key, value) VALUES ('test_automation', 'test_value');
SELECT value FROM system_config WHERE key = 'test_automation';
DELETE FROM system_config WHERE key = 'test_automation';
" 2>/dev/null | tr -d ' ')

if [ "$config_test" = "test_value" ]; then
    echo "✅ Configuration OK: CRUD operations working"
else
    echo "❌ Configuration FAIL: CRUD operations not working"
fi

# Test 5: Basic Performance
echo "Testing basic performance..."
start_time=$(date +%s%N)
sudo -u postgres psql -d citadel_ai -c "SELECT 1;" > /dev/null 2>&1
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds

if [ $duration -lt 100 ]; then
    echo "✅ Performance OK: ${duration}ms"
else
    echo "❌ Performance FAIL: ${duration}ms (expected <100ms)"
fi

echo "=== Test Complete ==="
```

---

## Notes

- This test case validates the core database schema for AI workloads
- Partitioning strategy is critical for handling large AI datasets
- Configuration management enables dynamic system behavior
- Test should be executed after both PostgreSQL and Redis installations
- Schema validation ensures optimal performance for AI operations

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.2_Validate_Redis_Installation.md
- Test_2.1_Validate_Performance_Benchmarks.md
- Test_3.1_Validate_Security_Configuration.md
