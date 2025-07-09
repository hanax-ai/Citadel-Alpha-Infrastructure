# HANA-X Key Decisions Document (KDD)

## Project Context
- **Phase**: Infrastructure setup (plumbing, piping, configuration)
- **Primary Focus**: Setting up all 9 servers starting with hx-llm-server-01
- **Next Phase**: Backend development (after infrastructure is complete)

## Server Architecture Decisions

### 1. LLM Server Strategy
- **hx-llm-server-01 (192.168.10.29)**: Will run different models than server-02
- **hx-llm-server-02 (192.168.10.28)**: Will run different models than server-01
- **No Load Balancing**: Each server serves different models, not replicated
- **No Replication**: Each server has distinct model configuration

### 2. Monitoring Architecture
- **hx-metric-server (192.168.10.37)**: Centralized monitoring hub
- **Principle**: Keep minimum installations on each server
- **Strategy**: Run, monitor, and display all metrics from central metric server
- **Implementation**: Avoid heavy monitoring installations on individual servers

### 3. Security Posture (Dev/Test)
- **Current Phase**: Security kept to minimum during dev/test
- **Rationale**: Avoid security issues that could block development and testing
- **Note**: Security hardening will be addressed in later phases

## Server Landscape Reference
```
# --- HX Internal LAN Servers ---
192.168.10.29    hx-llm-server-01
192.168.10.28    hx-llm-server-02
192.168.10.30    hx-vector-database-server
192.168.10.31    hx-orchestration-server
192.168.10.33    hx-dev-server
192.168.10.34    hx-test-server
192.168.10.35    hx-sql-database-server
192.168.10.36    hx-dev-ops-server
192.168.10.37    hx-metric-server
```

## Infrastructure Setup Approach
- **Baseline**: hx-llm-server-01 setup must be perfect (sets baseline for others)
- **Execution**: Task-by-task approach with approval at each step
- **Documentation**: Following SMART+ST task creation guidelines
- **Testing**: Using pytest framework for validation
- **Configuration**: Externalized (.env, .json, .yaml) - no hardcoding

## Governance Documents Review Status
- ✅ AI_Operating_Rules_HanaX.md (v1.5) - Enhanced and implemented
- ✅ HanaX_Repo_Structure.md - Repository structure created
- ✅ OOP_Coding_Standards_&_Rules.md - Reviewed
- ✅ vllm_test_guidelines.md - Reviewed
- ✅ task_creation_guidelines.txt - Enhanced with dependencies section
- ✅ prd_vllm_model_install.txt - Reviewed
- ⏳ Remaining: 3 documents to review

## Key Principles
1. **Different Models Per Server**: No replication, each LLM server serves different models
2. **Centralized Monitoring**: All metrics flow to hx-metric-server
3. **Minimal Security**: Keep security minimal during dev/test phase
4. **Perfect Baseline**: hx-llm-server-01 must be executed perfectly
5. **Task-by-Task**: Follow lead, get approval before proceeding

---
*Last Updated: 2025-07-09*
