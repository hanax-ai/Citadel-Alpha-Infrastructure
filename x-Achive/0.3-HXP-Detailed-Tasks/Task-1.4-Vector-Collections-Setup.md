# Task Template

## Task Information

**Task Number:** 1.4  
**Task Title:** Vector Collections Setup  
**Created:** 2025-07-15  
**Assigned To:** Infrastructure Team  
**Priority:** High  
**Estimated Duration:** 75 minutes  

## Task Description

Create and configure vector collections for all AI models with proper schemas, including 9 external AI model collections and 4 embedded model collections. This task establishes the data structure foundation for storing and retrieving vector embeddings from all 13 AI models with optimized distance metrics and metadata schemas.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Clear collection creation with specific schemas for each model |
| **Measurable** | ✅ | Defined success criteria with collection verification |
| **Achievable** | ✅ | Standard Qdrant collection creation and configuration |
| **Relevant** | ✅ | Essential for vector storage and retrieval operations |
| **Small** | ✅ | Focused on collection setup only |
| **Testable** | ✅ | Objective validation with collection queries |

## Prerequisites

**Hard Dependencies:**
- Task 1.1: Qdrant Installation and Basic Configuration (100% complete)
- Task 1.2: Storage Configuration and Optimization (100% complete)
- Task 1.3: Qdrant Performance Tuning (100% complete)
- Qdrant service running and optimized

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
QDRANT_COLLECTIONS_CONFIG=/opt/qdrant/config/collections.yaml
EXTERNAL_MODELS_COUNT=9
EMBEDDED_MODELS_COUNT=4
TOTAL_COLLECTIONS=13
```

**Configuration Files (.json/.yaml):**
```
/opt/qdrant/config/collections.yaml - Collection definitions
/opt/citadel/scripts/create_collections.py - Collection creation script
/opt/citadel/scripts/verify_collections.py - Collection verification script
```

**External Resources:**
- Qdrant HTTP API
- Collection schema definitions

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 1.4.1 | External Model Collections | Create 9 collections for external AI models | All external collections created |
| 1.4.2 | Embedded Model Collections | Create 4 collections for embedded models | All embedded collections created |
| 1.4.3 | Metadata Schema Configuration | Configure metadata schemas for each collection | Schemas properly defined |
| 1.4.4 | Distance Metrics Setup | Configure Cosine similarity for all collections | Distance metrics optimized |
| 1.4.5 | Collection Health Verification | Verify all collections are healthy | All collections operational |
| 1.4.6 | Index Configuration | Configure vector indexing for performance | Indexing optimized |
| 1.4.7 | Collection Documentation | Document collection structure and usage | Documentation complete |

## Success Criteria

**Primary Objectives:**
- [ ] External AI model collections created (9 collections) (FR-VDB-001, FR-VDB-004):
  - mixtral_embeddings (4096D, Cosine)
  - hermes_documents (4096D, Cosine)
  - yi34_longcontext (4096D, Cosine)
  - mimo_multimodal (1024D, Cosine)
  - llama3_general (4096D, Cosine)
  - codellama_code (4096D, Cosine)
  - mistral_instruct (4096D, Cosine)
  - phi3_vision (3072D, Cosine)
  - gemma_lightweight (2048D, Cosine)
- [ ] Embedded model collections created (4 collections) (FR-VDB-002):
  - minilm_general (384D, Cosine)
  - phi3_mini_text (768D, Cosine)
  - e5_multilingual (384D, Cosine)
  - bge_quality (768D, Cosine)
- [ ] Metadata schemas configured for each collection (FR-VDB-006)
- [ ] Collection health verified (NFR-AVAIL-001)

**Validation Commands:**
```bash
# List all collections
curl -X GET "http://192.168.10.30:6333/collections"

# Verify specific collections
curl -X GET "http://192.168.10.30:6333/collections/mixtral_embeddings"
curl -X GET "http://192.168.10.30:6333/collections/minilm_general"

# Check collection count
curl -X GET "http://192.168.10.30:6333/collections" | jq '.result.collections | length'

# Verify collection schemas
python /opt/citadel/scripts/verify_collections.py
```

**Expected Outputs:**
```
# Collections list showing all 13 collections
{
  "result": {
    "collections": [
      {
        "name": "mixtral_embeddings",
        "status": "green",
        "vectors_count": 0,
        "indexed_vectors_count": 0,
        "points_count": 0,
        "segments_count": 1
      },
      ... (12 more collections)
    ]
  }
}

# Collection count
13

# Collection detail showing proper configuration
{
  "result": {
    "status": "green",
    "optimizer_status": "ok",
    "vectors_count": 0,
    "indexed_vectors_count": 0,
    "points_count": 0,
    "segments_count": 1,
    "config": {
      "params": {
        "vectors": {
          "size": 4096,
          "distance": "Cosine"
        }
      }
    }
  }
}
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Collection creation failure | Low | High | Verify Qdrant health, check configuration syntax |
| Schema mismatch | Medium | Medium | Validate schemas before creation, test with sample data |
| Performance degradation | Low | Medium | Monitor collection performance, optimize if needed |
| Storage capacity issues | Low | Medium | Monitor disk usage, plan for data growth |

## Rollback Procedures

**If Task Fails:**
1. Delete created collections:
   ```bash
   # Delete all collections
   for collection in mixtral_embeddings hermes_documents yi34_longcontext mimo_multimodal llama3_general codellama_code mistral_instruct phi3_vision gemma_lightweight minilm_general phi3_mini_text e5_multilingual bge_quality; do
     curl -X DELETE "http://192.168.10.30:6333/collections/$collection"
   done
   ```
2. Verify deletion:
   ```bash
   curl -X GET "http://192.168.10.30:6333/collections"
   ```

**Rollback Validation:**
```bash
# Verify rollback completion
curl -X GET "http://192.168.10.30:6333/collections" | jq '.result.collections | length'
# Should return 0
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Task created from enhanced implementation guide |

## Dependencies This Task Enables

**Next Tasks:**
- Task 1.5: Basic Backup Configuration
- Task 2.1: AI Model Downloads and Verification
- Task 2.3: FastAPI Embedding Service Implementation

**Parallel Candidates:**
- Task 1.6: GraphQL API Implementation (can start in parallel)
- Task 1.7: gRPC Service Implementation (can start in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Collection creation fails | HTTP 400/500 errors | Check JSON syntax, verify Qdrant health |
| Schema validation errors | Invalid configuration | Validate vector dimensions, check distance metrics |
| Performance issues | Slow collection operations | Optimize indexing, check resource usage |
| Storage errors | Disk space warnings | Check available storage, clean up if needed |

**Debug Commands:**
```bash
# Qdrant health check
curl -X GET "http://192.168.10.30:6333/health"

# Collection diagnostics
curl -X GET "http://192.168.10.30:6333/collections/{collection_name}"

# Storage usage
df -h /opt/qdrant/

# Service logs
journalctl -u qdrant -f
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `Vector_Collections_Setup_Results.md`
- [ ] Update vector database schema documentation

**Result Document Location:**
- Save to: `/project/tasks/results/Vector_Collections_Setup_Results.md`

**Notification Requirements:**
- [ ] Notify Task 1.5 owner that collections are ready
- [ ] Update project status dashboard
- [ ] Communicate collection schemas to development team

## Notes

This task establishes the complete vector collection structure for all 13 AI models in the Citadel AI ecosystem. The collections are organized by model type and optimized for their specific vector dimensions and use cases.

**External Model Collections (9):**
- High-dimensional vectors (2048D-4096D) for advanced AI models
- Optimized for complex semantic understanding and generation tasks
- Cosine similarity for semantic similarity matching

**Embedded Model Collections (4):**
- Lower-dimensional vectors (384D-768D) for efficient local processing
- Optimized for real-time embedding generation and retrieval
- Balanced performance and resource utilization

All collections use Cosine similarity distance metric, which is optimal for semantic similarity tasks and provides consistent results across different vector dimensions.

---

**PRD References:** FR-VDB-001, FR-VDB-002, FR-VDB-004, FR-VDB-006, NFR-AVAIL-001  
**Phase:** 1 - Qdrant Vector Database Setup  
**Status:** Not Started
