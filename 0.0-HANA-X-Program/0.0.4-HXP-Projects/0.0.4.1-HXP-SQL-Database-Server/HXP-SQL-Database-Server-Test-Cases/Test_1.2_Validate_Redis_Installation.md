# 📝 Test Case: Redis 8.0.3 Installation Validation

## Test Case Information

**Test Case ID:** TC-P01-1.2  
**Test Case Name:** Validate Redis 8.0.3 Installation and Basic Functionality  
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

**Purpose:** Verify Redis 8.0.3 is correctly installed, running, and accessible for high-performance caching operations

**Test Description:** Validates the installation of Redis 8.0.3, confirms service status, tests basic caching operations, and verifies performance characteristics for AI workload requirements.

**Business Value:** Ensures the high-performance caching layer is operational for AI data processing and response optimization

---

## Requirements Traceability

**Related Tasks:**
- **Task 1.2:** Redis 8.0.3 Installation & Performance Optimization

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_1.2_Redis_8.0.3_Installation_Performance_Optimization.md](../HXP-SQL-Database-Server-Task/Task_1.2_Redis_8.0.3_Installation_Performance_Optimization.md)

---

## Test Prerequisites

**System Prerequisites:**
- Ubuntu 24.04 LTS installed on 192.168.10.35
- PostgreSQL 17.5 installation completed
- Network connectivity established

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Administrative privileges for Redis operations
- Memory allocation configured for Redis

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | Check Redis service status | Service active and running | Use systemctl |
| 2 | Verify Redis version | Redis 8.0.3 installed | Check exact version |
| 3 | Test Redis connectivity | Successful connection | Local and remote |
| 4 | Validate basic operations | SET/GET operations work | Basic caching |
| 5 | Test performance metrics | Response times <1ms | Performance validation |

### Step 1: Service Status Verification
**Action:** Check Redis service status  
**Command:** `sudo systemctl status redis`  
**Expected Result:** Service shows "active (running)" status  
**Verification:** Service status output shows no errors  

### Step 2: Version Validation
**Action:** Verify Redis version  
**Command:** `redis-cli --version`  
**Expected Result:** Output shows "redis-cli 8.0.3"  
**Verification:** Version string contains correct version number  

### Step 3: Connectivity Testing
**Action:** Test Redis connections  
**Commands:** 
```bash
# Local connection test
redis-cli ping

# Remote connection test (if configured)
redis-cli -h 192.168.10.35 -p 6379 ping
```
**Expected Result:** Both connections return "PONG"  
**Verification:** No connection errors, ping returns expected result  

### Step 4: Basic Operations Test
**Action:** Test SET/GET operations  
**Commands:**
```bash
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key
```
**Expected Result:** All operations complete successfully  
**Verification:** Value stored and retrieved correctly  

### Step 5: Performance Validation
**Action:** Test response times  
**Command:** `redis-cli --latency-history -h 192.168.10.35`  
**Expected Result:** Average latency <1ms  
**Verification:** Performance meets AI workload requirements  

---

## Expected Results

**Primary Expected Result:** Redis 8.0.3 is installed, running, and performing optimally

**Performance Expectations:**
- **Connection Time:** <1 second
- **SET/GET Operations:** <1ms response time
- **Service Start Time:** <10 seconds
- **Memory Usage:** Within configured limits

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] Redis service status shows "active (running)"
- [ ] Version output shows "redis-cli 8.0.3"
- [ ] Redis connections succeed (local and remote)
- [ ] Basic operations (SET, GET, DEL) work correctly
- [ ] Response times meet performance requirements (<1ms)
- [ ] No critical errors in Redis logs

**Fail Criteria:**
- [ ] Redis service is not running or shows errors
- [ ] Version is not 8.0.3 or shows incorrect version
- [ ] Redis connections fail
- [ ] Basic operations fail or return errors
- [ ] Performance does not meet requirements

---

## Automation Commands

```bash
#!/bin/bash
# Redis Installation Test Script

echo "=== Redis 8.0.3 Installation Test ==="

# Test 1: Service Status
echo "Testing Redis service status..."
sudo systemctl status redis --no-pager | grep "active (running)" && echo "✅ Service OK" || echo "❌ Service FAIL"

# Test 2: Version Check
echo "Testing Redis version..."
version=$(redis-cli --version | grep "8.0.3")
if [ -n "$version" ]; then
    echo "✅ Version OK: Redis 8.0.3"
else
    echo "❌ Version FAIL: Expected Redis 8.0.3"
fi

# Test 3: Connectivity
echo "Testing Redis connectivity..."
response=$(redis-cli ping 2>/dev/null)
if [ "$response" = "PONG" ]; then
    echo "✅ Connectivity OK"
else
    echo "❌ Connectivity FAIL"
fi

# Test 4: Basic Operations
echo "Testing basic operations..."
redis-cli set test_automation_key "test_value" > /dev/null 2>&1
retrieved=$(redis-cli get test_automation_key 2>/dev/null)
redis-cli del test_automation_key > /dev/null 2>&1

if [ "$retrieved" = "test_value" ]; then
    echo "✅ Basic Operations OK"
else
    echo "❌ Basic Operations FAIL"
fi

# Test 5: Performance Check
echo "Testing performance..."
start_time=$(date +%s%N)
redis-cli set perf_test "performance_value" > /dev/null 2>&1
redis-cli get perf_test > /dev/null 2>&1
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
redis-cli del perf_test > /dev/null 2>&1

if [ $duration -lt 10 ]; then
    echo "✅ Performance OK: ${duration}ms"
else
    echo "❌ Performance FAIL: ${duration}ms (expected <10ms)"
fi

echo "=== Test Complete ==="
```

---

## Notes

- This test case covers the fundamental Redis installation validation
- Performance testing focuses on latency requirements for AI workloads
- Test should be executed immediately after Task 1.2 completion
- Any failures should be investigated before proceeding with caching-dependent features

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.3_Validate_Database_Schema.md
- Test_2.1_Validate_Performance_Benchmarks.md
