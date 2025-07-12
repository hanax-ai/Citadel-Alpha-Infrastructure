# 📝 Test Case: PostgreSQL 17.5 Installation Validation

## Test Case Information

**Test Case ID:** TC-P01-1.1  
**Test Case Name:** Validate PostgreSQL 17.5 Installation and Basic Functionality  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Integration  
**Test Category:** Functional  
**Test Priority:** Critical  
**Test Complexity:** Simple  
**Automation Status:** Semi-Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify PostgreSQL 17.5 is correctly installed, running, and accessible for Citadel AI operations

**Test Description:** Validates the installation of PostgreSQL 17.5 with enterprise extensions, confirms service status, and tests basic database operations including connectivity and initial schema creation.

**Business Value:** Ensures the core relational database service is operational for AI workloads

---

## Requirements Traceability

**Related Tasks:**
- **Task 1.1:** PostgreSQL 17.5 Installation & Base Configuration
- **Task 1.3:** Initial Database Schema & Configuration Management

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_1.1_PostgreSQL_17.5_Installation_Base_Configuration.md](../HXP-SQL-Database-Server-Task/Task_1.1_PostgreSQL_17.5_Installation_Base_Configuration.md)

---

## Test Prerequisites

**System Prerequisites:**
- Ubuntu 24.04 LTS installed on 192.168.10.35
- Network connectivity established
- Security framework configured

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Administrative privileges for PostgreSQL operations

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | Check PostgreSQL service status | Service active and running | Use systemctl |
| 2 | Verify PostgreSQL version | PostgreSQL 17.5 installed | Check exact version |
| 3 | Test database connectivity | Successful connection | Local and remote |
| 4 | Validate enterprise extensions | Extensions loaded | JSON, full-text search |
| 5 | Create test database | Database created successfully | Basic operations |

### Step 1: Service Status Verification
**Action:** Check PostgreSQL service status  
**Command:** `sudo systemctl status postgresql`  
**Expected Result:** Service shows "active (running)" status  
**Verification:** Service status output shows no errors  

### Step 2: Version Validation
**Action:** Verify PostgreSQL version  
**Command:** `sudo -u postgres psql -c "SELECT version();"`  
**Expected Result:** Output shows "PostgreSQL 17.5"  
**Verification:** Version string contains correct version number  

### Step 3: Connectivity Testing
**Action:** Test database connections  
**Commands:** 
```bash
# Local connection test
sudo -u postgres psql -c "SELECT 1;"

# Remote connection test (if configured)
psql -h 192.168.10.35 -U postgres -c "SELECT 1;"
```
**Expected Result:** Both connections succeed, return "1"  
**Verification:** No connection errors, query returns expected result  

### Step 4: Extensions Validation
**Action:** Check enterprise extensions  
**Command:** `sudo -u postgres psql -c "\dx"`  
**Expected Result:** Extensions like jsonb, pg_trgm visible  
**Verification:** Required extensions are installed and loaded  

### Step 5: Basic Operations Test
**Action:** Create test database and table  
**Commands:**
```sql
CREATE DATABASE test_citadel_ai;
\c test_citadel_ai;
CREATE TABLE test_table (id SERIAL PRIMARY KEY, data JSONB);
INSERT INTO test_table (data) VALUES ('{"test": "data"}');
SELECT * FROM test_table;
```
**Expected Result:** All operations complete successfully  
**Verification:** Data inserted and retrieved correctly  

---

## Expected Results

**Primary Expected Result:** PostgreSQL 17.5 is installed, running, and fully functional

**Performance Expectations:**
- **Connection Time:** <2 seconds
- **Query Response:** <100ms for basic queries
- **Service Start Time:** <30 seconds

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] PostgreSQL service status shows "active (running)"
- [ ] Version output shows "PostgreSQL 17.5"
- [ ] Database connections succeed (local and remote)
- [ ] Required enterprise extensions are loaded
- [ ] Basic database operations (CREATE, INSERT, SELECT) work correctly
- [ ] No critical errors in PostgreSQL logs

**Fail Criteria:**
- [ ] PostgreSQL service is not running or shows errors
- [ ] Version is not 17.5 or shows incorrect version
- [ ] Database connections fail
- [ ] Required extensions are missing
- [ ] Basic operations fail or return errors

---

## Automation Commands

```bash
#!/bin/bash
# PostgreSQL Installation Test Script

echo "=== PostgreSQL 17.5 Installation Test ==="

# Test 1: Service Status
echo "Testing PostgreSQL service status..."
sudo systemctl status postgresql --no-pager | grep "active (running)" && echo "✅ Service OK" || echo "❌ Service FAIL"

# Test 2: Version Check
echo "Testing PostgreSQL version..."
version=$(sudo -u postgres psql -t -c "SELECT version();" | grep "PostgreSQL 17.5")
if [ -n "$version" ]; then
    echo "✅ Version OK: PostgreSQL 17.5"
else
    echo "❌ Version FAIL: Expected PostgreSQL 17.5"
fi

# Test 3: Connectivity
echo "Testing database connectivity..."
sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1 && echo "✅ Connectivity OK" || echo "❌ Connectivity FAIL"

# Test 4: Basic Operations
echo "Testing basic operations..."
sudo -u postgres psql -c "
CREATE DATABASE IF NOT EXISTS test_citadel_ai;
" > /dev/null 2>&1 && echo "✅ Basic Operations OK" || echo "❌ Basic Operations FAIL"

echo "=== Test Complete ==="
```

---

## Notes

- This test case covers the fundamental PostgreSQL installation validation
- Additional performance and integration testing will be covered in separate test cases
- Test should be executed immediately after Task 1.1 completion
- Any failures should block subsequent database-dependent tasks

---

**Related Test Cases:**
- Test_1.2_Validate_Redis_Installation.md
- Test_1.3_Validate_Database_Schema.md
- Test_2.1_Validate_Performance_Benchmarks.md
