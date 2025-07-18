# Task Template

## Task Information

**Task Number:** 2.1  
**Task Title:** AI Model Downloads and Verification  
**Created:** 2025-07-15  
**Assigned To:** AI/ML Team  
**Priority:** High  
**Estimated Duration:** 90 minutes  

## Task Description

Download and verify the 4 embedded AI models (all-MiniLM-L6-v2, phi-3-mini, e5-small, bge-base) from Hugging Face Hub with integrity checks, model validation, and proper storage organization. This task ensures all required AI models are available locally for GPU deployment and embedding generation.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Clear model download and verification for 4 specific models |
| **Measurable** | ✅ | Defined success criteria with model validation tests |
| **Achievable** | ✅ | Standard model download using Hugging Face libraries |
| **Relevant** | ✅ | Essential for embedded AI model deployment |
| **Small** | ✅ | Focused on model download and verification only |
| **Testable** | ✅ | Objective validation with model loading and inference tests |

## Prerequisites

**Hard Dependencies:**
- Task 0.3: NVIDIA Driver and CUDA Installation (100% complete)
- Task 0.4: Python Environment and AI/ML Dependencies (100% complete)
- Hugging Face transformers library installed
- Sufficient storage space (>20GB) for model files

**Soft Dependencies:**
- Task 1.8: API Integration Testing (recommended for API readiness)

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
HUGGINGFACE_CACHE_DIR=/opt/citadel/models/cache
MODEL_STORAGE_PATH=/opt/citadel/models/embedded
HUGGINGFACE_TOKEN=<optional-for-private-models>
MODEL_DOWNLOAD_TIMEOUT=3600
MODEL_VERIFICATION_ENABLED=true
```

**Configuration Files (.json/.yaml):**
```
/opt/citadel/config/embedded_models.yaml - Model configuration and metadata
/opt/citadel/scripts/download_models.py - Model download automation script
/opt/citadel/scripts/verify_models.py - Model verification script
/opt/citadel/models/embedded/model_manifest.json - Downloaded model inventory
```

**External Resources:**
- Hugging Face Hub API
- transformers library
- torch library for model loading

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 2.1.1 | Storage Directory Setup | Create model storage directories | Directories properly configured |
| 2.1.2 | Model Download Script | Create automated download script | Download script functional |
| 2.1.3 | all-MiniLM-L6-v2 Download | Download general-purpose embedding model | Model downloaded and verified |
| 2.1.4 | phi-3-mini Download | Download lightweight text embedding model | Model downloaded and verified |
| 2.1.5 | e5-small Download | Download multilingual embedding model | Model downloaded and verified |
| 2.1.6 | bge-base Download | Download high-quality embedding model | Model downloaded and verified |
| 2.1.7 | Model Verification | Verify model integrity and functionality | All models verified |

## Success Criteria

**Primary Objectives:**
- [ ] All 4 embedded models downloaded successfully (FR-EMB-001)
- [ ] Model integrity verified with checksums and loading tests (FR-EMB-001)
- [ ] Model storage organized with proper directory structure (FR-EMB-001)
- [ ] Model metadata and configuration files created (FR-EMB-001)
- [ ] Model loading performance benchmarked (NFR-PERF-003)
- [ ] Storage usage optimized with proper caching (NFR-SCALE-002)
- [ ] Model manifest and inventory tracking implemented (FR-EMB-001)

**Validation Commands:**
```bash
# Verify model downloads
ls -la /opt/citadel/models/embedded/
du -sh /opt/citadel/models/embedded/*

# Test model loading
python -c "
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained('/opt/citadel/models/embedded/all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained('/opt/citadel/models/embedded/all-MiniLM-L6-v2')
print('all-MiniLM-L6-v2 loaded successfully')
"

# Run verification script
python /opt/citadel/scripts/verify_models.py

# Check model manifest
cat /opt/citadel/models/embedded/model_manifest.json

# Test inference capability
python -c "
import torch
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained('/opt/citadel/models/embedded/all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained('/opt/citadel/models/embedded/all-MiniLM-L6-v2')
inputs = tokenizer('Hello world', return_tensors='pt')
outputs = model(**inputs)
print(f'Output shape: {outputs.last_hidden_state.shape}')
"
```

**Expected Outputs:**
```
# Model directory listing
drwxr-xr-x 3 citadel citadel 4096 Jul 15 14:30 all-MiniLM-L6-v2/
drwxr-xr-x 3 citadel citadel 4096 Jul 15 14:30 phi-3-mini/
drwxr-xr-x 3 citadel citadel 4096 Jul 15 14:30 e5-small/
drwxr-xr-x 3 citadel citadel 4096 Jul 15 14:30 bge-base/

# Model sizes
90M     all-MiniLM-L6-v2
2.4G    phi-3-mini
134M    e5-small
436M    bge-base

# Model loading success
all-MiniLM-L6-v2 loaded successfully

# Verification script output
✓ all-MiniLM-L6-v2: Downloaded and verified
✓ phi-3-mini: Downloaded and verified
✓ e5-small: Downloaded and verified
✓ bge-base: Downloaded and verified
All models ready for deployment

# Inference test output
Output shape: torch.Size([1, 3, 384])
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Download failures | Medium | High | Implement retry logic, verify network connectivity |
| Storage space exhaustion | Low | High | Monitor disk usage, implement cleanup procedures |
| Model corruption | Low | Medium | Verify checksums, implement integrity checks |
| Network timeouts | Medium | Medium | Increase timeout values, implement resumable downloads |

## Rollback Procedures

**If Task Fails:**
1. Clean up partial downloads:
   ```bash
   sudo rm -rf /opt/citadel/models/embedded/*
   sudo rm -rf /opt/citadel/models/cache/*
   ```
2. Reset storage directories:
   ```bash
   sudo mkdir -p /opt/citadel/models/embedded
   sudo mkdir -p /opt/citadel/models/cache
   sudo chown -R citadel:citadel /opt/citadel/models/
   ```
3. Clear Hugging Face cache:
   ```bash
   python -c "from huggingface_hub import scan_cache_dir; scan_cache_dir().delete_revisions().execute()"
   ```

**Rollback Validation:**
```bash
# Verify rollback completion
ls -la /opt/citadel/models/embedded/  # Should be empty
df -h /opt/citadel/models/            # Should show freed space
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Task created from enhanced implementation guide |

## Dependencies This Task Enables

**Next Tasks:**
- Task 2.2: GPU Memory Allocation Strategy
- Task 2.3: FastAPI Embedding Service Setup
- Task 2.4: Model Loading and Optimization

**Parallel Candidates:**
- Task 2.2: GPU Memory Allocation Strategy (can run in parallel)
- Task 3.1: PostgreSQL Integration Setup (can run in parallel)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Download timeouts | Incomplete model downloads | Increase timeout, check network stability |
| Storage permission errors | Access denied during download | Fix directory permissions, check ownership |
| Model loading failures | Import errors or tensor issues | Verify model integrity, check dependencies |
| Cache corruption | Inconsistent model behavior | Clear cache, re-download models |

**Debug Commands:**
```bash
# Network connectivity test
curl -I https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# Storage diagnostics
df -h /opt/citadel/models/
ls -la /opt/citadel/models/embedded/

# Python environment check
python -c "import transformers; print(transformers.__version__)"
python -c "import torch; print(torch.__version__)"

# Model loading debug
python -c "
from transformers import AutoModel
try:
    model = AutoModel.from_pretrained('/opt/citadel/models/embedded/all-MiniLM-L6-v2')
    print('Model loaded successfully')
except Exception as e:
    print(f'Error: {e}')
"
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `AI_Model_Downloads_Verification_Results.md`
- [ ] Update model inventory and documentation

**Result Document Location:**
- Save to: `/project/tasks/results/AI_Model_Downloads_Verification_Results.md`

**Notification Requirements:**
- [ ] Notify Task 2.2 owner that models are ready for GPU allocation
- [ ] Update project status dashboard
- [ ] Communicate model availability to development team

## Notes

This task establishes the foundation for embedded AI model deployment by ensuring all required models are downloaded, verified, and ready for GPU deployment. The systematic approach includes integrity verification and performance benchmarking to ensure model quality.

**Key model details:**
- **all-MiniLM-L6-v2**: 384-dimensional embeddings, general-purpose, 90MB
- **phi-3-mini**: Lightweight text embeddings, optimized for efficiency, 2.4GB
- **e5-small**: Multilingual embeddings, 134MB
- **bge-base**: High-quality embeddings, 436MB

The models are organized in a structured directory layout with proper metadata tracking, enabling efficient GPU allocation and model management in subsequent tasks.

---

**PRD References:** FR-EMB-001, NFR-PERF-003, NFR-SCALE-002  
**Phase:** 2 - Embedded AI Model Deployment  
**Status:** Not Started
