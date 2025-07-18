# Task Template

## Task Information

**Task Number:** 2.3  
**Task Title:** FastAPI Embedding Service Setup  
**Created:** 2025-07-15  
**Assigned To:** Development Team  
**Priority:** High  
**Estimated Duration:** 180 minutes  

## Task Description

Implement FastAPI-based embedding service that provides REST endpoints for text-to-vector conversion using the 4 embedded AI models with GPU acceleration, batch processing, and performance optimization. This service acts as the primary interface for generating embeddings from text input using the locally deployed AI models.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Clear FastAPI service for embedding generation |
| **Measurable** | ✅ | Defined success criteria with API endpoints and performance metrics |
| **Achievable** | ✅ | Standard FastAPI implementation with AI model integration |
| **Relevant** | ✅ | Essential for embedding generation functionality |
| **Small** | ✅ | Focused on embedding service implementation only |
| **Testable** | ✅ | Objective validation with API testing and performance benchmarks |

## Prerequisites

**Hard Dependencies:**
- Task 0.4: Python Environment and AI/ML Dependencies (100% complete)
- Task 2.1: AI Model Downloads and Verification (100% complete)
- Task 2.2: GPU Memory Allocation Strategy (100% complete)
- FastAPI and uvicorn libraries installed

**Soft Dependencies:**
- Task 1.8: API Integration Testing (recommended for API consistency)

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
EMBEDDING_SERVICE_HOST=0.0.0.0
EMBEDDING_SERVICE_PORT=8000
MAX_BATCH_SIZE=32
MAX_SEQUENCE_LENGTH=512
DEFAULT_MODEL=all-MiniLM-L6-v2
ENABLE_ASYNC_PROCESSING=true
EMBEDDING_CACHE_TTL=3600
```

**Configuration Files (.json/.yaml):**
```
/opt/citadel/services/embedding_api.py - FastAPI embedding service
/opt/citadel/services/embedding_processor.py - Embedding processing logic
/opt/citadel/services/batch_processor.py - Batch processing implementation
/opt/citadel/config/embedding_models.yaml - Model configuration
/opt/citadel/schemas/embedding_schemas.py - Pydantic schemas for API
```

**External Resources:**
- FastAPI framework
- uvicorn ASGI server
- transformers library
- torch for GPU acceleration

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 2.3.1 | FastAPI Application Setup | Create FastAPI application structure | FastAPI app initialized |
| 2.3.2 | API Schema Definition | Define Pydantic schemas for requests/responses | Schemas properly defined |
| 2.3.3 | Embedding Endpoints | Implement embedding generation endpoints | Endpoints functional |
| 2.3.4 | Batch Processing | Implement batch embedding processing | Batch processing working |
| 2.3.5 | Model Integration | Integrate with GPU memory allocation system | Model integration complete |
| 2.3.6 | Performance Optimization | Implement caching and async processing | Performance optimized |
| 2.3.7 | Health and Monitoring | Implement health checks and metrics | Monitoring operational |

## Success Criteria

**Primary Objectives:**
- [ ] FastAPI embedding service deployed on port 8000 (FR-EMB-003)
- [ ] Single text embedding endpoint implemented (/embed) (FR-EMB-003)
- [ ] Batch text embedding endpoint implemented (/embed/batch) (FR-EMB-003)
- [ ] Model selection endpoint implemented (/embed/model/{model_name}) (FR-EMB-003)
- [ ] Health check endpoint implemented (/health) (FR-EMB-003)
- [ ] GPU acceleration integrated with memory allocation system (FR-EMB-002)
- [ ] Batch processing optimized for throughput (NFR-PERF-003)
- [ ] Response time <100ms for single embeddings (NFR-PERF-003)

**Validation Commands:**
```bash
# Service health check
curl -X GET "http://192.168.10.30:8000/health"

# Single embedding test
curl -X POST "http://192.168.10.30:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "model": "all-MiniLM-L6-v2"}'

# Batch embedding test
curl -X POST "http://192.168.10.30:8000/embed/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello world", "How are you?"], "model": "all-MiniLM-L6-v2"}'

# Model-specific endpoint test
curl -X POST "http://192.168.10.30:8000/embed/model/phi-3-mini" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test embedding"}'

# Performance benchmark
curl -X POST "http://192.168.10.30:8000/embed/benchmark" \
  -H "Content-Type: application/json" \
  -d '{"batch_sizes": [1, 8, 16, 32], "iterations": 100}'
```

**Expected Outputs:**
```
# Health check response
{
  "status": "healthy",
  "models_loaded": 4,
  "gpu_utilization": {
    "gpu_0": 75,
    "gpu_1": 68
  },
  "uptime": "2h 15m"
}

# Single embedding response
{
  "embedding": [0.1234, -0.5678, 0.9012, ...],
  "model": "all-MiniLM-L6-v2",
  "dimensions": 384,
  "processing_time_ms": 45
}

# Batch embedding response
{
  "embeddings": [
    [0.1234, -0.5678, 0.9012, ...],
    [0.2345, -0.6789, 0.0123, ...]
  ],
  "model": "all-MiniLM-L6-v2",
  "dimensions": 384,
  "batch_size": 2,
  "processing_time_ms": 78
}

# Performance benchmark
{
  "results": {
    "batch_1": {"avg_time_ms": 45, "throughput_per_sec": 22},
    "batch_8": {"avg_time_ms": 120, "throughput_per_sec": 67},
    "batch_16": {"avg_time_ms": 200, "throughput_per_sec": 80},
    "batch_32": {"avg_time_ms": 350, "throughput_per_sec": 91}
  }
}
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| GPU memory overflow | Medium | High | Implement batch size limits, memory monitoring |
| Model loading failures | Low | Medium | Implement retry logic, fallback mechanisms |
| API performance degradation | Medium | Medium | Implement caching, optimize batch processing |
| Concurrent request handling | Medium | Medium | Implement proper async handling, request queuing |

## Rollback Procedures

**If Task Fails:**
1. Stop embedding service:
   ```bash
   sudo systemctl stop embedding-service
   ```
2. Remove service files:
   ```bash
   sudo rm /opt/citadel/services/embedding_api.py
   sudo rm /opt/citadel/services/embedding_processor.py
   sudo rm /opt/citadel/services/batch_processor.py
   ```
3. Remove systemd service:
   ```bash
   sudo rm /etc/systemd/system/embedding-service.service
   sudo systemctl daemon-reload
   ```

**Rollback Validation:**
```bash
# Verify rollback completion
sudo systemctl status embedding-service  # Should show inactive
curl -X GET "http://192.168.10.30:8000/health"  # Should fail
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Task created from enhanced implementation guide |

## Dependencies This Task Enables

**Next Tasks:**
- Task 2.4: Model Loading and Optimization
- Task 2.5: Embedding Generation Pipeline
- Task 2.6: Model Management API

**Parallel Candidates:**
- Task 3.1: PostgreSQL Integration Setup (can run in parallel)
- Task 3.2: Redis Caching Implementation (can run in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Service startup failures | FastAPI won't start | Check port availability, verify dependencies |
| GPU memory errors | CUDA out of memory | Reduce batch size, implement memory monitoring |
| Model loading timeouts | Slow API responses | Optimize model loading, implement caching |
| Request timeout errors | API timeouts | Increase timeout values, optimize processing |

**Debug Commands:**
```bash
# Service diagnostics
sudo systemctl status embedding-service
journalctl -u embedding-service -f

# API testing
curl -X GET "http://192.168.10.30:8000/docs"  # FastAPI docs
curl -X GET "http://192.168.10.30:8000/openapi.json"

# Performance monitoring
htop
nvidia-smi -l 1

# Python environment check
source /opt/citadel/env/bin/activate
python -c "import fastapi; print(fastapi.__version__)"
python -c "import uvicorn; print(uvicorn.__version__)"
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `FastAPI_Embedding_Service_Setup_Results.md`
- [ ] Update API documentation with embedding endpoints

**Result Document Location:**
- Save to: `/project/tasks/results/FastAPI_Embedding_Service_Setup_Results.md`

**Notification Requirements:**
- [ ] Notify Task 2.4 owner that embedding service is ready
- [ ] Update project status dashboard
- [ ] Communicate embedding API endpoints to development team

## Notes

This task implements a high-performance FastAPI-based embedding service that provides efficient text-to-vector conversion using the locally deployed AI models. The service is optimized for both single and batch processing scenarios with GPU acceleration.

**Key service features:**
- **Multiple Endpoints**: Single, batch, and model-specific embedding endpoints
- **GPU Acceleration**: Integrated with GPU memory allocation system
- **Batch Processing**: Optimized for high-throughput scenarios
- **Async Processing**: Non-blocking request handling
- **Health Monitoring**: Comprehensive health checks and metrics
- **Performance Optimization**: Caching and response time optimization

The embedding service provides the core functionality for converting text input into vector embeddings, enabling semantic search and similarity operations in the vector database.

---

**PRD References:** FR-EMB-003, FR-EMB-002, NFR-PERF-003  
**Phase:** 2 - Embedded AI Model Deployment  
**Status:** Not Started
