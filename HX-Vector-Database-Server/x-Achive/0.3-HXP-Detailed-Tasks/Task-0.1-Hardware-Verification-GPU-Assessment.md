# Task Template

## Task Information

**Task Number:** 0.1  
**Task Title:** Hardware Verification and GPU Assessment  
**Created:** 2025-07-15  
**Assigned To:** Infrastructure Team  
**Priority:** High  
**Estimated Duration:** 60 minutes  

## Task Description

Verify server hardware specifications and assess dual GPU configuration for embedded model deployment, ensuring hardware meets performance and scalability requirements defined in the PRD. This task establishes the foundation for all subsequent GPU-dependent operations and validates that the hardware can support the target performance metrics.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Hardware verification with specific GPU, CPU, RAM, and storage checks |
| **Measurable** | ✅ | Clear success criteria with specific hardware specifications |
| **Achievable** | ✅ | Standard hardware verification procedures on existing server |
| **Relevant** | ✅ | Critical foundation for GPU-based AI model deployment |
| **Small** | ✅ | Single focused task on hardware verification only |
| **Testable** | ✅ | Objective verification commands with expected outputs |

## Prerequisites

**Hard Dependencies:**
- Physical server access to hx-vector-database-server (192.168.10.30)
- Ubuntu 24.04.2 LTS installed and accessible
- Network connectivity to server

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
# No environment variables required for hardware verification
```

**Configuration Files (.json/.yaml):**
```
# No configuration files required for hardware verification
```

**External Resources:**
- Physical access to hx-vector-database-server
- Network access to 192.168.10.30
- SSH access credentials

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 0.1.1 | CPU Verification | `lscpu \| grep -E "Model name\|CPU\\(s\\)\|Thread"` | Intel i9-9900K, 8 cores, 16 threads confirmed |
| 0.1.2 | Memory Verification | `free -h \| grep Mem` | 78GB RAM availability confirmed |
| 0.1.3 | GPU Detection | `lspci \| grep -i nvidia` | 2x NVIDIA GT 1030 GPUs detected |
| 0.1.4 | GPU Memory Check | `nvidia-smi --query-gpu=name,memory.total --format=csv` | 6GB VRAM per GPU confirmed |
| 0.1.5 | Storage Verification | `lsblk -f && df -h` | 21.8TB total storage verified |
| 0.1.6 | Network Interface | `ip a show eno1` | 192.168.10.30 IP configured |

## Success Criteria

**Primary Objectives:**
- [ ] Intel Core i9-9900K CPU verified with 8 cores/16 threads (NFR-PERF-001)
- [ ] 78GB RAM availability confirmed (NFR-SCALE-001)
- [ ] 2x NVIDIA GeForce GT 1030 GPUs detected with 6GB VRAM each (NFR-PERF-004)
- [ ] 21.8TB total storage verified (3.6TB NVMe + 18.2TB additional) (NFR-SCALE-001)
- [ ] Network interface eno1 configured at 192.168.10.30
- [ ] GPU compute capability 6.1 confirmed for CUDA compatibility

**Validation Commands:**
```bash
# CPU verification
lscpu | grep -E "Model name|CPU\(s\)|Thread"

# Memory verification
free -h | grep Mem

# GPU verification
lspci | grep -i nvidia
nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv

# Storage verification
lsblk -f
df -h

# Network verification
ip a show eno1
```

**Expected Outputs:**
```
CPU: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
CPU(s): 8
Thread(s) per core: 2

Mem: 78Gi

NVIDIA Corporation GP108 [GeForce GT 1030]
NVIDIA Corporation GP108 [GeForce GT 1030]

name, memory.total [MiB], compute_cap
GeForce GT 1030, 6144, 6.1
GeForce GT 1030, 6144, 6.1

Total storage: ~21.8TB across multiple devices
eno1: 192.168.10.30/24
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| GPU not detected | Low | High | Check physical connections, verify drivers |
| Insufficient VRAM | Medium | High | Validate model requirements, plan memory optimization |
| Storage capacity issues | Low | Medium | Verify storage allocation, plan data management |
| Network configuration issues | Low | Medium | Verify network settings, check routing |

## Rollback Procedures

**If Task Fails:**
1. Document specific hardware discrepancies found
2. No system changes made, so no rollback needed
3. Report hardware issues to infrastructure team

**Rollback Validation:**
```bash
# No rollback needed - read-only verification task
echo "Hardware verification task - no rollback required"
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Task created from enhanced implementation guide |

## Dependencies This Task Enables

**Next Tasks:**
- Task 0.2: Operating System Optimization and Updates
- Task 0.3: NVIDIA Driver and CUDA Installation
- Task 0.4: Python Environment and AI/ML Dependencies

**Parallel Candidates:**
- None (foundational task required for all subsequent tasks)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| nvidia-smi not found | Command not found error | Install NVIDIA drivers first, or use lspci for basic detection |
| GPU not detected | No NVIDIA devices in lspci | Check physical connections, verify PCIe slots |
| Memory discrepancy | Less than 78GB available | Check for hardware issues, verify BIOS settings |
| Storage not mounted | Missing storage devices | Check mount points, verify disk connections |

**Debug Commands:**
```bash
# System information
uname -a
cat /proc/cpuinfo | grep "model name" | head -1
cat /proc/meminfo | grep MemTotal

# Hardware detection
lshw -short
lspci -v
dmidecode -t memory

# Network diagnostics
ip route show
ping -c 3 192.168.10.1
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `Hardware_Verification_Results.md`
- [ ] Update hardware inventory documentation

**Result Document Location:**
- Save to: `/project/tasks/results/Hardware_Verification_Results.md`

**Notification Requirements:**
- [ ] Notify Task 0.2 owner that hardware verification is complete
- [ ] Update project status dashboard
- [ ] Communicate any hardware issues to infrastructure team

## Notes

This task is critical for validating that the hardware meets the PRD requirements before proceeding with software installation. Any discrepancies found should be resolved before continuing with the implementation.

Key hardware requirements validated:
- CPU: Intel i9-9900K (8 cores, 16 threads) for high-performance vector operations
- RAM: 78GB for large-scale vector storage and processing
- GPU: Dual GT 1030 (6GB each) for embedded AI model deployment
- Storage: 21.8TB for vector database storage and model files
- Network: Gigabit Ethernet for high-throughput operations

---

**PRD References:** NFR-PERF-004, NFR-SCALE-001  
**Phase:** 0 - Infrastructure Foundation  
**Status:** Not Started
