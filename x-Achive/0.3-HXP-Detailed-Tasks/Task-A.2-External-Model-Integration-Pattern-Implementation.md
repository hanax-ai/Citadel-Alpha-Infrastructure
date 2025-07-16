# Task Template

## Task Information

**Task Number:** A.2  
**Task Title:** External Model Integration Pattern Implementation  
**Created:** 2025-07-15  
**Assigned To:** AI Integration Team  
**Priority:** CRITICAL  
**Estimated Duration:** 720 minutes (12 hours)  

## Task Description

Implement the three external AI model integration patterns as defined in the architecture: Real-time routing (3 models), Hybrid real-time + bulk (2 models), and Bulk write only (4 models). This addresses the critical architectural gap for proper external model integration with differentiated processing patterns based on model characteristics and usage requirements.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Clear integration patterns for all 9 external AI models |
| **Measurable** | ✅ | Defined success criteria with pattern-specific metrics |
| **Achievable** | ✅ | Standard integration patterns using proven methodologies |
| **Relevant** | ✅ | Critical for external model integration architecture |
| **Small** | ✅ | Focused on integration pattern implementation only |
| **Testable** | ✅ | Objective validation with pattern-specific testing |

## Prerequisites

**Hard Dependencies:**
- Task A.1: API Gateway Service Development (100% complete)
- Task 3.3: External AI Model Integration (100% complete)
- Task 3.2: Redis Caching Implementation (100% complete)

**Soft Dependencies:**
- Task 3.1: PostgreSQL Integration Setup (recommended for metadata tracking)

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
# External Model Endpoints
MIXTRAL_ENDPOINT=http://192.168.10.29:11400
HERMES_ENDPOINT=http://192.168.10.29:11401
YI34_ENDPOINT=http://192.168.10.28:11404
OPENCHAT_ENDPOINT=http://192.168.10.29:11402
PHI3_ENDPOINT=http://192.168.10.29:11403
DEEPCODER_ENDPOINT=http://192.168.10.28:11405
IMP_ENDPOINT=http://192.168.10.28:11406
DEEPSEEK_ENDPOINT=http://192.168.10.28:11407
GENERAL_ENDPOINT=http://192.168.10.31:8000

# Integration Pattern Configuration
REAL_TIME_TIMEOUT=30
HYBRID_URGENT_THRESHOLD=5
BULK_BATCH_SIZE=100
BULK_PROCESSING_INTERVAL=300
PATTERN_RETRY_ATTEMPTS=3
PATTERN_CIRCUIT_BREAKER_THRESHOLD=10
```

**Configuration Files (.json/.yaml):**
```
/opt/citadel/services/model_integration.py - Main integration service
/opt/citadel/config/integration_patterns.yaml - Pattern configuration
/opt/citadel/patterns/real_time_pattern.py - Real-time pattern implementation
/opt/citadel/patterns/hybrid_pattern.py - Hybrid pattern implementation
/opt/citadel/patterns/bulk_pattern.py - Bulk pattern implementation
/opt/citadel/queue/batch_queue.py - Batch processing queue
/opt/citadel/scripts/test_integration_patterns.sh - Pattern testing script
```

**External Resources:**
- aiohttp for HTTP client connections
- asyncio for asynchronous processing
- Redis for batch job queuing
- PostgreSQL for metadata tracking

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| A.2.1 | Pattern Framework | Setup integration pattern framework | Framework configured |
| A.2.2 | Real-time Pattern | Implement real-time routing for 3 models | Real-time pattern working |
| A.2.3 | Hybrid Pattern | Implement hybrid processing for 2 models | Hybrid pattern working |
| A.2.4 | Bulk Pattern | Implement bulk processing for 4 models | Bulk pattern working |
| A.2.5 | Model Configuration | Configure all 9 external models with patterns | Model configuration complete |
| A.2.6 | Metadata Tracking | Implement pattern-specific metadata tracking | Metadata tracking working |
| A.2.7 | Pattern Testing | Test all integration patterns end-to-end | Pattern testing complete |

## Success Criteria

**Primary Objectives:**
- [ ] All 9 external models configured with correct integration patterns (FR-EXT-001)
- [ ] Real-time routing functional for 3 models (phi3, openchat, general) (FR-EXT-002)
- [ ] Hybrid processing operational for 2 models (hermes, openchat) (FR-EXT-002)
- [ ] Bulk processing queue operational for 4 models (mixtral, yi34, deepcoder, imp, deepseek) (FR-EXT-003)
- [ ] Pattern-specific metadata tracking implemented (NFR-DATA-001)
- [ ] Circuit breaker patterns operational for all models (NFR-RELI-004)
- [ ] Integration pattern performance meets targets (NFR-PERF-001)
- [ ] Error handling and failover working across all patterns (NFR-RELI-003)

**Validation Commands:**
```bash
# Test real-time pattern models
curl -X POST "http://192.168.10.30:8000/api/v1/external/phi3/embed" -H "Content-Type: application/json" -d '{"text": "test embedding", "urgent": true}'
curl -X POST "http://192.168.10.30:8000/api/v1/external/general/embed" -H "Content-Type: application/json" -d '{"text": "test embedding", "urgent": true}'

# Test hybrid pattern models
curl -X POST "http://192.168.10.30:8000/api/v1/external/hermes/embed" -H "Content-Type: application/json" -d '{"text": "test embedding", "urgent": true}'
curl -X POST "http://192.168.10.30:8000/api/v1/external/hermes/embed" -H "Content-Type: application/json" -d '{"text": "test embedding", "urgent": false}'

# Test bulk pattern models
curl -X POST "http://192.168.10.30:8000/api/v1/external/mixtral/embed" -H "Content-Type: application/json" -d '{"texts": ["text1", "text2", "text3"], "batch": true}'
curl -X POST "http://192.168.10.30:8000/api/v1/external/yi34/embed" -H "Content-Type: application/json" -d '{"texts": ["text1", "text2"], "batch": true}'

# Check integration pattern status
curl -X GET "http://192.168.10.30:8000/api/v1/external/patterns/status"

# Check batch queue status
curl -X GET "http://192.168.10.30:8000/api/v1/external/batch/queue/status"

# Test pattern failover
curl -X POST "http://192.168.10.30:8000/api/v1/external/test/failover" -H "Content-Type: application/json" -d '{"model": "phi3", "simulate_failure": true}'

# Run comprehensive pattern test
cd /opt/citadel/scripts
./test_integration_patterns.sh --all-patterns --verbose
```

**Expected Outputs:**
```
# Real-time pattern response (phi3)
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "model": "phi3",
  "pattern": "real_time",
  "processing_time_ms": 85.2,
  "endpoint": "http://192.168.10.29:11403",
  "metadata": {
    "pattern_type": "real_time",
    "urgent": true,
    "processed_at": "2025-07-15T14:30:00Z"
  }
}

# Hybrid pattern response (hermes - urgent)
{
  "embedding": [0.234, -0.567, 0.890, ...],
  "model": "hermes",
  "pattern": "hybrid",
  "processing_mode": "real_time",
  "processing_time_ms": 92.4,
  "endpoint": "http://192.168.10.29:11401",
  "metadata": {
    "pattern_type": "hybrid",
    "urgent": true,
    "processed_at": "2025-07-15T14:30:00Z"
  }
}

# Hybrid pattern response (hermes - non-urgent)
{
  "status": "queued",
  "model": "hermes",
  "pattern": "hybrid",
  "processing_mode": "bulk",
  "batch_id": "batch_hermes_20250715_143000",
  "estimated_completion": "2025-07-15T14:35:00Z",
  "queue_position": 3,
  "metadata": {
    "pattern_type": "hybrid",
    "urgent": false,
    "queued_at": "2025-07-15T14:30:00Z"
  }
}

# Bulk pattern response (mixtral)
{
  "status": "queued",
  "model": "mixtral",
  "pattern": "bulk_only",
  "batch_id": "batch_mixtral_20250715_143000",
  "items_count": 3,
  "estimated_completion": "2025-07-15T14:35:00Z",
  "queue_position": 1,
  "metadata": {
    "pattern_type": "bulk_only",
    "batch_size": 3,
    "queued_at": "2025-07-15T14:30:00Z"
  }
}

# Integration pattern status
{
  "patterns": {
    "real_time": {
      "models": ["phi3", "openchat", "general"],
      "active_requests": 5,
      "success_rate": 98.5,
      "avg_response_time_ms": 87.3
    },
    "hybrid": {
      "models": ["hermes", "openchat"],
      "real_time_requests": 12,
      "bulk_requests": 8,
      "success_rate": 97.2,
      "avg_response_time_ms": 89.1
    },
    "bulk_only": {
      "models": ["mixtral", "yi34", "deepcoder", "imp", "deepseek"],
      "queued_batches": 3,
      "processing_batches": 1,
      "completed_batches": 45,
      "success_rate": 99.1,
      "avg_batch_processing_time_ms": 2340.5
    }
  },
  "circuit_breakers": {
    "phi3": {"status": "closed", "failure_count": 0},
    "hermes": {"status": "closed", "failure_count": 1},
    "mixtral": {"status": "closed", "failure_count": 0},
    "yi34": {"status": "closed", "failure_count": 0},
    "openchat": {"status": "closed", "failure_count": 0},
    "deepcoder": {"status": "closed", "failure_count": 0},
    "imp": {"status": "closed", "failure_count": 0},
    "deepseek": {"status": "closed", "failure_count": 0},
    "general": {"status": "closed", "failure_count": 0}
  }
}

# Batch queue status
{
  "queue_status": {
    "total_jobs": 12,
    "pending_jobs": 3,
    "processing_jobs": 1,
    "completed_jobs": 8,
    "failed_jobs": 0
  },
  "processing_stats": {
    "avg_processing_time_seconds": 234.5,
    "items_per_minute": 125.3,
    "success_rate": 99.1
  },
  "model_queues": {
    "mixtral": {"pending": 1, "processing": 0},
    "yi34": {"pending": 0, "processing": 1},
    "deepcoder": {"pending": 1, "processing": 0},
    "imp": {"pending": 1, "processing": 0},
    "deepseek": {"pending": 0, "processing": 0}
  }
}

# Pattern test results
Integration Pattern Test Results:
================================

Real-time Pattern Tests:
✅ phi3: 50/50 requests successful (100%)
✅ openchat: 48/50 requests successful (96%)
✅ general: 50/50 requests successful (100%)

Hybrid Pattern Tests:
✅ hermes (urgent): 25/25 requests successful (100%)
✅ hermes (bulk): 25/25 requests queued successfully (100%)
✅ openchat (urgent): 24/25 requests successful (96%)
✅ openchat (bulk): 25/25 requests queued successfully (100%)

Bulk Pattern Tests:
✅ mixtral: 5/5 batches processed successfully (100%)
✅ yi34: 5/5 batches processed successfully (100%)
✅ deepcoder: 4/5 batches processed successfully (80%)
✅ imp: 5/5 batches processed successfully (100%)
✅ deepseek: 5/5 batches processed successfully (100%)

Circuit Breaker Tests:
✅ All models: Circuit breakers functional
✅ Failover: Automatic failover working
✅ Recovery: Circuit breaker recovery working

Performance Summary:
- Real-time average latency: 87.3ms
- Hybrid real-time average latency: 89.1ms
- Bulk processing throughput: 125.3 items/minute
- Overall success rate: 98.2%
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| External model endpoint failures | Medium | High | Implement circuit breakers, failover mechanisms |
| Batch processing queue overflow | Medium | Medium | Implement queue monitoring, backpressure handling |
| Pattern configuration errors | Medium | High | Comprehensive testing, configuration validation |
| Performance degradation under load | Medium | High | Load testing, performance monitoring, optimization |

## Rollback Procedures

**If Task Fails:**
1. Stop integration service:
   ```bash
   pkill -f model_integration.py
   sudo systemctl stop model-integration
   ```
2. Remove pattern configurations:
   ```bash
   sudo rm -rf /opt/citadel/services/model_integration.py
   sudo rm -rf /opt/citadel/config/integration_patterns.yaml
   sudo rm -rf /opt/citadel/patterns/
   ```
3. Restore basic external model integration:
   ```bash
   # Restart basic external model service
   sudo systemctl restart external-model-service
   ```

**Rollback Validation:**
```bash
# Verify integration service is stopped
ps aux | grep model_integration  # Should show no processes

# Verify basic external model access still works
curl -X GET "http://192.168.10.29:11400/health"  # Mixtral
curl -X GET "http://192.168.10.29:11401/health"  # Hermes
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Critical path addendum task for external model patterns |

## Dependencies This Task Enables

**Next Tasks:**
- Task A.3: Request Router and Load Balancer Implementation
- Task B.3: Batch Processing Framework Implementation

**Existing Tasks to Update:**
- Task 3.9: External Model Testing (add pattern-specific testing)
- Task 4.2: Performance Benchmarking (add pattern performance tests)
- Task 4.3: Load Testing with Locust (add pattern load testing)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Pattern routing failures | Requests not using correct pattern | Verify pattern configuration, check model mapping |
| Batch queue overflow | Bulk requests timing out | Increase queue capacity, optimize processing |
| Circuit breaker triggering | High failure rates for specific models | Check model endpoints, adjust thresholds |
| Metadata tracking issues | Missing or incorrect metadata | Verify database connections, check tracking logic |

**Debug Commands:**
```bash
# Integration service diagnostics
python model_integration.py --debug --verbose
journalctl -u model-integration -f

# Check external model connectivity
curl -X GET "http://192.168.10.29:11400/health"  # Mixtral
curl -X GET "http://192.168.10.29:11401/health"  # Hermes
curl -X GET "http://192.168.10.28:11404/health"  # Yi-34B

# Monitor batch queue
redis-cli -h 192.168.10.35 -p 6379 llen batch_queue
redis-cli -h 192.168.10.35 -p 6379 lrange batch_queue 0 -1

# Check pattern performance
curl -X GET "http://192.168.10.30:8000/api/v1/external/patterns/metrics"
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `External_Model_Integration_Pattern_Results.md`
- [ ] Update external model integration documentation

**Result Document Location:**
- Save to: `/project/tasks/results/External_Model_Integration_Pattern_Results.md`

**Notification Requirements:**
- [ ] Notify Task A.3 owner that integration patterns are operational
- [ ] Update project status dashboard
- [ ] Provide pattern documentation to AI integration team

## Notes

This task implements the three critical external AI model integration patterns that address the architectural gap for proper external model integration. The patterns provide differentiated processing based on model characteristics and usage requirements.

**Key integration patterns:**
- **Real-time Pattern**: Immediate processing for 3 models (phi3, openchat, general)
- **Hybrid Pattern**: Dual-mode processing for 2 models (hermes, openchat)
- **Bulk Pattern**: Batch processing for 4 models (mixtral, yi34, deepcoder, imp, deepseek)
- **Circuit Breakers**: Automatic failover and recovery for all models
- **Metadata Tracking**: Pattern-specific metadata and performance tracking
- **Queue Management**: Efficient batch processing queue management

The integration patterns enable optimal utilization of external AI models while maintaining performance and reliability requirements.

---

**PRD References:** FR-EXT-001, FR-EXT-002, FR-EXT-003, NFR-DATA-001, NFR-RELI-004, NFR-PERF-001, NFR-RELI-003  
**Phase:** Addendum Phase A - Unified API Gateway Implementation  
**Status:** Not Started
