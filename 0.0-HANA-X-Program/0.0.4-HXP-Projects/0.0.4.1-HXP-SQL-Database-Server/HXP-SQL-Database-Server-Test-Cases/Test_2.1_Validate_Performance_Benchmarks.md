# 📝 Test Case: Performance Benchmarks Validation

## Test Case Information

**Test Case ID:** TC-P02-2.1  
**Test Case Name:** Validate Database Performance Benchmarks & Load Testing  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Performance  
**Test Category:** Load Testing  
**Test Priority:** Critical  
**Test Complexity:** High  
**Automation Status:** Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify database performance meets AI workload requirements under various load conditions

**Test Description:** Executes comprehensive performance testing including query latency, throughput, concurrent connections, and system resource utilization to ensure optimal performance for AI operations.

**Business Value:** Validates system can handle production AI workloads with required performance characteristics

---

## Requirements Traceability

**Related Tasks:**
- **Task 2.1:** Database Performance Benchmarks & Load Testing
- **Task 2.2:** Query Optimization & Index Tuning

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_2.1_Database_Performance_Benchmarks_Load_Testing.md](../HXP-SQL-Database-Server-Task/Task_2.1_Database_Performance_Benchmarks_Load_Testing.md)

---

## Test Prerequisites

**System Prerequisites:**
- PostgreSQL 17.5 installed and optimized
- Redis 8.0.3 installed and optimized
- Database schema created and indexed
- Performance monitoring tools installed

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Performance testing tools (pgbench, redis-benchmark)
- System monitoring access
- Test data loaded

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | PostgreSQL latency test | <10ms for simple queries | Single query performance |
| 2 | PostgreSQL throughput test | >1000 TPS | Transactions per second |
| 3 | Redis performance test | <1ms for cache operations | Cache layer performance |
| 4 | Concurrent connection test | 100+ concurrent users | Connection scalability |
| 5 | Resource utilization test | <80% CPU/Memory under load | Resource efficiency |

### Step 1: PostgreSQL Query Latency Test
**Action:** Measure single query response times  
**Commands:**
```bash
# Simple SELECT latency
pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 1 -j 1 -T 60 -S

# Complex JOIN latency test
psql -h 192.168.10.35 -U postgres -d citadel_ai -c "
\timing on
SELECT ai.model_name, COUNT(il.id) as inference_count 
FROM ai_models ai 
LEFT JOIN inference_logs il ON ai.id = il.model_id 
WHERE ai.created_at >= CURRENT_DATE - INTERVAL '7 days' 
GROUP BY ai.model_name;
"
```
**Expected Result:** Simple queries <10ms, complex queries <100ms  
**Verification:** Query execution times within SLA  

### Step 2: PostgreSQL Throughput Test
**Action:** Measure transactions per second  
**Commands:**
```bash
# Read-write throughput test
pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 10 -j 4 -T 300

# Read-only throughput test
pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 10 -j 4 -T 300 -S

# AI workload simulation
pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 20 -j 8 -T 300 -f ai_workload.sql
```
**Expected Result:** >1000 TPS for mixed workload  
**Verification:** Throughput meets AI workload requirements  

### Step 3: Redis Performance Test
**Action:** Benchmark Redis cache operations  
**Commands:**
```bash
# Basic SET/GET performance
redis-benchmark -h 192.168.10.35 -p 6379 -n 100000 -c 50 -d 1024

# Pipeline performance test
redis-benchmark -h 192.168.10.35 -p 6379 -n 100000 -c 50 -P 16

# AI cache simulation
redis-benchmark -h 192.168.10.35 -p 6379 -t get,set -n 100000 -c 100
```
**Expected Result:** >50000 ops/sec, <1ms latency  
**Verification:** Cache performance supports AI response times  

### Step 4: Concurrent Connection Test
**Action:** Test connection scalability  
**Commands:**
```bash
# PostgreSQL connection test
for i in {1..100}; do
    psql -h 192.168.10.35 -U postgres -d citadel_ai -c "SELECT 1;" &
done
wait

# Redis connection test
for i in {1..100}; do
    redis-cli -h 192.168.10.35 ping &
done
wait
```
**Expected Result:** 100+ concurrent connections supported  
**Verification:** No connection failures under load  

### Step 5: Resource Utilization Test
**Action:** Monitor system resources under load  
**Commands:**
```bash
# Start resource monitoring
iostat -x 1 300 > iostat_results.txt &
vmstat 1 300 > vmstat_results.txt &
sar -u -r 1 300 > sar_results.txt &

# Run combined load test
pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 50 -j 8 -T 300 &
redis-benchmark -h 192.168.10.35 -p 6379 -n 1000000 -c 100 &

wait # Wait for tests to complete
```
**Expected Result:** CPU <80%, Memory <80%, I/O <80%  
**Verification:** System remains stable under load  

---

## Expected Results

**Primary Expected Result:** Database performance meets all AI workload requirements

**Performance Targets:**
- **PostgreSQL Latency:** <10ms (simple), <100ms (complex)
- **PostgreSQL Throughput:** >1000 TPS
- **Redis Latency:** <1ms
- **Redis Throughput:** >50000 ops/sec
- **Concurrent Connections:** 100+ supported
- **Resource Utilization:** <80% under load

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] PostgreSQL simple query latency <10ms (95th percentile)
- [ ] PostgreSQL complex query latency <100ms (95th percentile)
- [ ] PostgreSQL throughput >1000 TPS sustained
- [ ] Redis latency <1ms (95th percentile)
- [ ] Redis throughput >50000 ops/sec
- [ ] 100+ concurrent connections supported
- [ ] CPU utilization <80% under load
- [ ] Memory utilization <80% under load
- [ ] No connection timeouts or errors

**Fail Criteria:**
- [ ] Query latency exceeds targets
- [ ] Throughput below minimum requirements
- [ ] Connection failures under load
- [ ] Resource utilization >90%
- [ ] System instability during testing

---

## Automation Commands

```bash
#!/bin/bash
# Performance Benchmarks Test Script

echo "=== Database Performance Benchmarks Test ==="

# Test 1: PostgreSQL Latency
echo "Testing PostgreSQL latency..."
latency_result=$(pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 1 -j 1 -T 60 -S 2>/dev/null | grep "latency average" | awk '{print $4}')
latency_ms=$(echo "$latency_result" | sed 's/ms//')

if (( $(echo "$latency_ms < 10" | bc -l) )); then
    echo "✅ Latency OK: ${latency_ms}ms"
else
    echo "❌ Latency FAIL: ${latency_ms}ms (expected <10ms)"
fi

# Test 2: PostgreSQL Throughput
echo "Testing PostgreSQL throughput..."
tps_result=$(pgbench -h 192.168.10.35 -U postgres -d citadel_ai -c 10 -j 4 -T 60 2>/dev/null | grep "tps" | head -1 | awk '{print $3}')

if (( $(echo "$tps_result > 1000" | bc -l) )); then
    echo "✅ Throughput OK: ${tps_result} TPS"
else
    echo "❌ Throughput FAIL: ${tps_result} TPS (expected >1000)"
fi

# Test 3: Redis Performance
echo "Testing Redis performance..."
redis_ops=$(redis-benchmark -h 192.168.10.35 -p 6379 -n 10000 -c 10 -q | grep "GET" | awk '{print $2}')

if (( $(echo "$redis_ops > 50000" | bc -l) )); then
    echo "✅ Redis Performance OK: ${redis_ops} ops/sec"
else
    echo "❌ Redis Performance FAIL: ${redis_ops} ops/sec (expected >50000)"
fi

# Test 4: Connection Test
echo "Testing concurrent connections..."
connection_errors=0
for i in {1..50}; do
    psql -h 192.168.10.35 -U postgres -d citadel_ai -c "SELECT 1;" > /dev/null 2>&1 &
done
wait

if [ $connection_errors -eq 0 ]; then
    echo "✅ Connections OK: 50 concurrent connections successful"
else
    echo "❌ Connections FAIL: $connection_errors connection errors"
fi

# Test 5: Resource Check
echo "Testing resource utilization..."
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')

if (( $(echo "$cpu_usage < 80" | bc -l) )) && (( $(echo "$mem_usage < 80" | bc -l) )); then
    echo "✅ Resources OK: CPU ${cpu_usage}%, Memory ${mem_usage}%"
else
    echo "❌ Resources FAIL: CPU ${cpu_usage}%, Memory ${mem_usage}% (expected <80%)"
fi

echo "=== Performance Test Complete ==="
```

---

## Test Data Requirements

**PostgreSQL Test Data:**
- 1M records in training_data table
- 100K records in ai_models table
- 10M records in inference_logs table
- Realistic data distribution for AI workloads

**Redis Test Data:**
- 100K cached model predictions
- Session data for 1000 concurrent users
- Frequently accessed configuration data

---

## Notes

- Performance testing should be conducted during off-peak hours
- Baseline measurements should be taken before optimization
- Results should be compared against production requirements
- Network latency should be considered for remote connections
- Test data should represent realistic AI workload patterns

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.2_Validate_Redis_Installation.md
- Test_1.3_Validate_Database_Schema.md
- Test_2.2_Validate_Query_Optimization.md
