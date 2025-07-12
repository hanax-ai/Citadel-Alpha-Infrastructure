# 📝 Test Case: Citadel AI Integration Validation

## Test Case Information

**Test Case ID:** TC-P05-5.1  
**Test Case Name:** Validate Citadel AI Services Integration  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Integration  
**Test Category:** End-to-End  
**Test Priority:** Critical  
**Test Complexity:** High  
**Automation Status:** Semi-Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify database server foundation is ready for future Citadel AI service integration and supports anticipated AI workload operations

**Test Description:** Validates database foundation readiness, simulates expected AI workloads, tests network paths to future services, and ensures database infrastructure can support the full Citadel AI ecosystem when other servers are deployed.

**Business Value:** Ensures database foundation is properly established as the first server in the HXP infrastructure and ready for future AI service integration

---

## Requirements Traceability

**Related Tasks:**
- **Task 5.1:** Citadel AI Integration & API Connectivity
- **Task 5.2:** Production Deployment & Go-Live Support

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_5.1_Citadel_AI_Integration_API_Connectivity.md](../HXP-SQL-Database-Server-Task/Task_5.1_Citadel_AI_Integration_API_Connectivity.md)

---

## Test Prerequisites

**System Prerequisites:**
- PostgreSQL 17.5 fully configured and operational
- Redis 8.0.3 configured with AI caching strategies
- All security configurations implemented
- Network infrastructure configured for future service connectivity

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Network paths available to future service IPs (192.168.10.31, 192.168.10.29, 192.168.10.28, 192.168.10.33)
- Database user accounts prepared for future AI services
- Test data representing expected AI workloads

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | Network path readiness test | Future service IPs reachable | Foundation network |
| 2 | AI data foundation test | Database ready for AI data | Schema validation |
| 3 | Model storage foundation test | AI model infrastructure ready | Storage preparation |
| 4 | Simulated AI workload test | Database handles expected load | Load simulation |
| 5 | Future service account test | Database access ready | User preparation |

### Step 1: Network Path Readiness Testing
**Action:** Verify network infrastructure is ready for future Citadel AI services  
**Commands:**
```bash
# Test network paths to future service IPs
FUTURE_SERVICES=("192.168.10.31" "192.168.10.29" "192.168.10.28" "192.168.10.33")
SERVICE_NAMES=("Orchestration" "LLM-Server-1" "LLM-Server-2" "Development")

for i in "${!FUTURE_SERVICES[@]}"; do
    ip="${FUTURE_SERVICES[$i]}"
    name="${SERVICE_NAMES[$i]}"
    echo "Testing network path to future $name server ($ip)..."
    
    # Test ping connectivity (should work even if service not deployed)
    ping -c 3 -W 1 $ip && echo "✅ Network path to $name ready" || echo "❌ Network path to $name not available"
    
    # Test if ports would be reachable (basic network routing)
    nc -z -w1 $ip 22 2>/dev/null && echo "✅ SSH port accessible on $name" || echo "⚠️  $name not yet deployed (expected)"
done

# Verify our database server is properly registered in network
hostname -I | grep "192.168.10.35" && echo "✅ Database server IP configured correctly"

# Test DNS resolution readiness
nslookup hx-sql-database-server.hana-x.internal || echo "⚠️  DNS not yet configured (may be expected)"
```
**Expected Result:** Network paths available, routing configured  
**Verification:** Basic connectivity possible, infrastructure foundation ready

### Step 2: AI Data Foundation Testing
**Action:** Test database readiness for future AI training data workflows  
**Commands:**
```bash
# Test AI database schema readiness
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
-- Verify AI tables exist and are ready
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name IN ('training_data', 'ai_models', 'inference_logs')
ORDER BY table_name, ordinal_position;
"

# Test sample AI data insertion (simulating future API calls)
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
-- Simulate future training data ingestion
INSERT INTO training_data (dataset_name, data_type, content, label, created_at) 
VALUES 
    ('foundation_test_dataset', 'text_classification', 'Sample text 1', 'positive', NOW()),
    ('foundation_test_dataset', 'text_classification', 'Sample text 2', 'negative', NOW());
"

# Verify database can handle AI data structures
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT COUNT(*) as sample_count 
FROM training_data 
WHERE dataset_name = 'foundation_test_dataset';
"

# Test JSON data handling for AI models
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
-- Test JSONB handling for AI metadata
INSERT INTO ai_models (model_name, model_type, parameters, created_at)
VALUES (
    'foundation_test_model',
    'transformer',
    '{"layers": 12, "hidden_size": 768, "vocab_size": 30000}'::jsonb,
    NOW()
);
"

# Verify performance with AI data types
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT 
    model_name,
    parameters->>'layers' as layers,
    parameters->>'hidden_size' as hidden_size
FROM ai_models 
WHERE model_name = 'foundation_test_model';
"
```
**Expected Result:** Database handles AI data structures efficiently  
**Verification:** AI data types and structures work correctly

### Step 3: AI Model Storage Testing
**Action:** Test AI model lifecycle management  
**Commands:**
```bash
# Upload AI model metadata
curl -k -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $CITADEL_API_TOKEN" \
     -d '{
       "model_name": "integration_test_model",
       "model_type": "transformer",
       "version": "1.0.0",
       "parameters": {
         "layers": 12,
         "hidden_size": 768,
         "vocab_size": 30000
       },
       "training_config": {
         "learning_rate": 0.001,
         "batch_size": 32,
         "epochs": 10
       }
     }' \
     https://citadel-ai-api.hana-x.internal/models/register

# Verify model registration
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT 
    model_name,
    model_type,
    version,
    created_at,
    status
FROM ai_models 
WHERE model_name = 'integration_test_model';
"

# Test model versioning
curl -k -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $CITADEL_API_TOKEN" \
     -d '{
       "model_name": "integration_test_model",
       "version": "1.1.0",
       "changes": ["improved accuracy", "reduced inference time"]
     }' \
     https://citadel-ai-api.hana-x.internal/models/version

# Test model retrieval
curl -k -H "Authorization: Bearer $CITADEL_API_TOKEN" \
     https://citadel-ai-api.hana-x.internal/models/integration_test_model/latest
```
**Expected Result:** Model lifecycle operations work correctly  
**Verification:** Model metadata stored and retrievable  

### Step 4: Inference Logging Testing
**Action:** Test real-time inference logging and caching  
**Commands:**
```bash
# Submit inference request
curl -k -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $CITADEL_API_TOKEN" \
     -d '{
       "model_name": "integration_test_model",
       "input_data": {
         "text": "This is a test inference request"
       },
       "session_id": "test_session_001"
     }' \
     https://citadel-ai-api.hana-x.internal/inference/predict

# Verify inference logging in PostgreSQL
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT 
    model_name,
    session_id,
    inference_time_ms,
    created_at
FROM inference_logs 
WHERE session_id = 'test_session_001'
ORDER BY created_at DESC
LIMIT 5;
"

# Check Redis caching for frequent queries
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" GET "inference:integration_test_model:cache_key"

# Test batch inference logging
for i in {1..10}; do
    curl -k -X POST \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $CITADEL_API_TOKEN" \
         -d "{
           \"model_name\": \"integration_test_model\",
           \"input_data\": {\"text\": \"Batch test $i\"},
           \"session_id\": \"batch_test_session\"
         }" \
         https://citadel-ai-api.hana-x.internal/inference/predict &
done
wait

# Verify batch logging performance
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT 
    COUNT(*) as total_inferences,
    AVG(inference_time_ms) as avg_time,
    MAX(inference_time_ms) as max_time,
    MIN(inference_time_ms) as min_time
FROM inference_logs 
WHERE session_id = 'batch_test_session';
"
```
**Expected Result:** Inference logging works with proper performance  
**Verification:** All inferences logged, caching operational  

### Step 5: AI Workload Performance Testing
**Action:** Test performance under realistic AI workloads  
**Commands:**
```bash
# Simulate realistic AI workload
cat > ai_workload_test.sh << 'EOF'
#!/bin/bash
echo "=== AI Workload Performance Test ==="

# Configuration
CONCURRENT_USERS=50
TEST_DURATION=300 # 5 minutes
API_ENDPOINT="https://citadel-ai-api.hana-x.internal"

# Function for AI workload simulation
simulate_ai_user() {
    local user_id=$1
    local session_id="perf_test_${user_id}_$$"
    
    for ((i=1; i<=20; i++)); do
        # Model inference
        curl -k -s -X POST \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer $CITADEL_API_TOKEN" \
             -d "{
               \"model_name\": \"integration_test_model\",
               \"input_data\": {\"text\": \"Performance test $i user $user_id\"},
               \"session_id\": \"$session_id\"
             }" \
             $API_ENDPOINT/inference/predict > /dev/null
        
        # Training data query
        curl -k -s -H "Authorization: Bearer $CITADEL_API_TOKEN" \
             "$API_ENDPOINT/data/query?limit=10&offset=$((i*10))" > /dev/null
        
        sleep 0.5
    done
}

# Start monitoring
iostat -x 1 $TEST_DURATION > /tmp/ai_workload_iostat.log &
vmstat 1 $TEST_DURATION > /tmp/ai_workload_vmstat.log &

# Launch concurrent users
for ((u=1; u<=$CONCURRENT_USERS; u++)); do
    simulate_ai_user $u &
done

echo "Started $CONCURRENT_USERS concurrent AI users..."
wait

echo "=== AI Workload Test Complete ==="

# Analyze performance
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
SELECT 
    COUNT(*) as total_inferences,
    AVG(inference_time_ms) as avg_inference_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY inference_time_ms) as p95_time,
    MIN(created_at) as test_start,
    MAX(created_at) as test_end
FROM inference_logs 
WHERE session_id LIKE 'perf_test_%'
AND created_at >= NOW() - INTERVAL '10 minutes';
"
EOF

chmod +x ai_workload_test.sh
./ai_workload_test.sh

# Database performance analysis
psql -h 192.168.10.35 -U postgres -d citadel_ai -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_tup_hot_upd as hot_updates
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
ORDER BY n_tup_ins DESC;
"

# Redis performance analysis
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" INFO stats | grep -E "(total_commands_processed|instantaneous_ops_per_sec)"
```
**Expected Result:** System handles AI workload within performance targets  
**Verification:** Response times <100ms, throughput >1000 ops/sec  

---

## Expected Results

**Primary Expected Result:** Database server fully integrates with Citadel AI ecosystem and supports production AI workloads

**Integration Requirements:**
- **API Connectivity:** 100% uptime to Citadel services
- **Data Ingestion:** >1000 records/second sustained
- **Model Operations:** <50ms for model metadata operations
- **Inference Logging:** <10ms overhead for logging
- **Cache Hit Rate:** >80% for frequent AI queries

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] Network paths to future service IPs are accessible
- [ ] Database foundation handles AI data structures correctly
- [ ] AI model storage infrastructure ready
- [ ] Simulated AI workloads perform within targets
- [ ] Database user accounts prepared for future services
- [ ] Redis caching infrastructure operational
- [ ] No foundation setup errors or data corruption
- [ ] System stability maintained under simulated AI loads

**Fail Criteria:**
- [ ] Network infrastructure not ready for future services
- [ ] Database cannot handle AI data structures
- [ ] AI infrastructure foundation incomplete
- [ ] Performance below minimum requirements for AI workloads
- [ ] User account preparation incomplete
- [ ] Foundation setup errors or instability

---

## Automation Commands

```bash
#!/bin/bash
# Database Foundation Readiness Test Script

echo "=== Database Foundation Readiness Test ==="

# Test 1: Network Infrastructure
echo "Testing network infrastructure for future services..."
FUTURE_SERVICES=("192.168.10.31" "192.168.10.29" "192.168.10.28" "192.168.10.33")
network_ready=0

for ip in "${FUTURE_SERVICES[@]}"; do
    ping -c 1 -W 1 $ip > /dev/null 2>&1 && ((network_ready++))
done

if [ $network_ready -ge 2 ]; then
    echo "✅ Network Infrastructure OK: $network_ready/4 future service paths ready"
else
    echo "❌ Network Infrastructure FAIL: Only $network_ready/4 paths ready"
fi

# Test 2: Database Foundation
echo "Testing database foundation for AI workloads..."
db_test=$(psql -h 192.168.10.35 -U citadel_app -d citadel_ai -t -c "SELECT COUNT(*) FROM ai_models;" 2>/dev/null | tr -d ' ')

if [ "$db_test" -ge 0 ] 2>/dev/null; then
    echo "✅ Database Foundation OK: AI tables accessible"
else
    echo "❌ Database Foundation FAIL: AI tables not accessible"
fi

# Test 3: AI Model Infrastructure
echo "Testing AI model infrastructure..."
model_test=$(psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "
INSERT INTO ai_models (model_name, model_type, parameters) 
VALUES ('foundation_test', 'test', '{\"test\": true}'::jsonb);
SELECT model_name FROM ai_models WHERE model_name = 'foundation_test';
" 2>/dev/null | grep 'foundation_test')

if [ -n "$model_test" ]; then
    echo "✅ AI Model Infrastructure OK: Model storage working"
    # Cleanup
    psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "DELETE FROM ai_models WHERE model_name = 'foundation_test';" > /dev/null 2>&1
else
    echo "❌ AI Model Infrastructure FAIL: Model storage not working"
fi

# Test 4: Inference Logging
echo "Testing inference logging..."
inference_test=$(curl -k -s -o /dev/null -w "%{http_code}" \
                      -H "Content-Type: application/json" \
                      -H "Authorization: Bearer $CITADEL_API_TOKEN" \
                      -d '{
                        "model_name": "test_integration_model",
                        "input_data": {"text": "test"},
                        "session_id": "integration_test"
                      }' \
                      https://citadel-ai-api.hana-x.internal/inference/predict 2>/dev/null)

if [ "$inference_test" = "200" ]; then
    echo "✅ Inference Logging OK: Inference request processed"
else
    echo "❌ Inference Logging FAIL: HTTP $inference_test"
fi

# Test 5: Performance Check
echo "Testing AI workload performance..."
start_time=$(date +%s%N)
for i in {1..10}; do
    curl -k -s -H "Authorization: Bearer $CITADEL_API_TOKEN" \
         https://citadel-ai-api.hana-x.internal/models/list > /dev/null 2>&1 &
done
wait
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds

if [ $duration -lt 5000 ]; then
    echo "✅ Performance OK: 10 concurrent requests in ${duration}ms"
else
    echo "❌ Performance FAIL: ${duration}ms (expected <5000ms)"
fi

# Test 6: Redis Cache Integration
echo "Testing Redis cache integration..."
cache_status=$(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" ping 2>/dev/null)
if [ "$cache_status" = "PONG" ]; then
    echo "✅ Cache Integration OK: Redis accessible for AI caching"
else
    echo "❌ Cache Integration FAIL: Redis not accessible"
fi

echo "=== Database Foundation Test Complete ==="
```

---

## Integration Test Data

**Test Datasets:**
- Sample training data (1000 records)
- Model metadata for 5 different AI models
- Inference logs for performance testing
- Configuration data for AI services

**Performance Baselines:**
- API response time: <100ms
- Data ingestion rate: >1000 records/sec
- Model operations: <50ms
- Cache hit rate: >80%

---

## Notes

- This is the **FIRST SERVER** in the HXP infrastructure deployment
- Future service integration will be tested when those servers are deployed
- Focus on establishing solid foundation for AI workloads
- Network path testing ensures infrastructure is ready for expansion
- Database performance testing simulates expected AI service loads
- All test data should be cleaned up after foundation testing

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.2_Validate_Redis_Installation.md
- Test_2.1_Validate_Performance_Benchmarks.md
- Test_3.1_Validate_Security_Configuration.md
- Test_4.1_Validate_Backup_Recovery.md
