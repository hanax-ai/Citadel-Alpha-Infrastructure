# Task Template

## Task Information

**Task Number:** 0.3  
**Task Title:** NVIDIA Driver and CUDA Installation  
**Created:** 2025-07-15  
**Assigned To:** Infrastructure Team  
**Priority:** High  
**Estimated Duration:** 105 minutes  

## Task Description

Install and configure NVIDIA drivers and CUDA toolkit for dual GT 1030 GPU support, enabling GPU-accelerated AI model inference and embedding generation. This task establishes the foundation for all GPU-dependent operations including embedded model deployment and high-performance vector operations.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Clear NVIDIA driver and CUDA installation steps |
| **Measurable** | ✅ | Defined success criteria with GPU detection and CUDA functionality |
| **Achievable** | ✅ | Standard NVIDIA driver installation on Ubuntu 24.04.2 |
| **Relevant** | ✅ | Essential for GPU-accelerated AI model operations |
| **Small** | ✅ | Focused on NVIDIA/CUDA installation only |
| **Testable** | ✅ | Objective validation with nvidia-smi and CUDA samples |

## Prerequisites

**Hard Dependencies:**
- Task 0.1: Hardware Verification and GPU Assessment (100% complete)
- Task 0.2: Operating System Optimization and Updates (100% complete)
- 2x NVIDIA GeForce GT 1030 GPUs physically installed
- Internet connectivity for driver downloads

**Soft Dependencies:**
- System reboot capability for driver activation

**Conditional Dependencies:**
- Secure Boot disabled (if enabled, may require signed drivers)

## Configuration Requirements

**Environment Variables (.env):**
```
CUDA_HOME=/usr/local/cuda
PATH=$PATH:/usr/local/cuda/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
NVIDIA_VISIBLE_DEVICES=all
```

**Configuration Files (.json/.yaml):**
```
/etc/environment - System-wide CUDA environment variables
/etc/modprobe.d/blacklist-nouveau.conf - Nouveau driver blacklist
/etc/nvidia-container-runtime/config.toml - NVIDIA Container Runtime config
```

**External Resources:**
- NVIDIA driver repository
- CUDA toolkit packages
- NVIDIA Container Toolkit repository

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 0.3.1 | Nouveau Driver Blacklist | Blacklist open-source driver | Nouveau driver disabled |
| 0.3.2 | NVIDIA Repository Setup | Add NVIDIA package repository | Repository configured |
| 0.3.3 | NVIDIA Driver Installation | Install nvidia-driver-535+ | Driver installed and loaded |
| 0.3.4 | CUDA Toolkit Installation | Install cuda-toolkit-12-3 | CUDA toolkit functional |
| 0.3.5 | Environment Configuration | Configure CUDA environment variables | Environment variables set |
| 0.3.6 | Container Runtime Setup | Install NVIDIA Container Toolkit | Docker GPU support enabled |
| 0.3.7 | System Reboot | Reboot to activate drivers | Drivers active after reboot |

## Success Criteria

**Primary Objectives:**
- [ ] NVIDIA drivers 535+ installed and functional (NFR-PERF-004)
- [ ] CUDA toolkit 12.x installed and configured (NFR-PERF-004)
- [ ] Both GPUs detected and accessible via nvidia-smi (NFR-PERF-004)
- [ ] CUDA samples compiled and tested successfully (NFR-PERF-004)
- [ ] GPU memory monitoring tools installed (NFR-PERF-004)
- [ ] NVIDIA Container Toolkit installed for Docker GPU support (FR-VDB-002)
- [ ] Environment variables configured system-wide (NFR-PERF-004)

**Validation Commands:**
```bash
# GPU detection and driver status
nvidia-smi

# CUDA version verification
nvcc --version

# GPU memory and utilization monitoring
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv

# Docker GPU support test
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi

# CUDA environment verification
echo $CUDA_HOME
echo $PATH | grep cuda
```

**Expected Outputs:**
```
# nvidia-smi output
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.3  |
|-------------------------------+----------------------+----------------------+
|   0  GeForce GT 1030     Off  | 00000000:01:00.0 Off |                  N/A |
|   1  GeForce GT 1030     Off  | 00000000:02:00.0 Off |                  N/A |
+-------------------------------+----------------------+----------------------+

# CUDA version
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2023 NVIDIA Corporation
Built on Mon_Apr__3_17:16:06_PDT_2023
Cuda compilation tools, release 12.3, V12.3.xxx

# Environment variables
CUDA_HOME=/usr/local/cuda
PATH includes /usr/local/cuda/bin
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Driver installation failure | Medium | High | Use multiple installation methods, check compatibility |
| CUDA compilation issues | Medium | Medium | Verify GCC version compatibility, use supported versions |
| GPU not detected after reboot | Low | High | Check physical connections, verify driver loading |
| Container runtime conflicts | Low | Medium | Test Docker GPU support, verify runtime configuration |

## Rollback Procedures

**If Task Fails:**
1. Remove NVIDIA drivers:
   ```bash
   sudo apt remove --purge nvidia-*
   sudo apt autoremove
   ```
2. Remove CUDA toolkit:
   ```bash
   sudo apt remove --purge cuda-*
   sudo rm -rf /usr/local/cuda*
   ```
3. Restore nouveau driver:
   ```bash
   sudo rm /etc/modprobe.d/blacklist-nouveau.conf
   sudo update-initramfs -u
   ```
4. Reboot system:
   ```bash
   sudo reboot
   ```

**Rollback Validation:**
```bash
# Verify rollback completion
lsmod | grep nouveau
nvidia-smi  # Should fail
nvcc --version  # Should fail
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-15 | Created | Pending | Task created from enhanced implementation guide |

## Dependencies This Task Enables

**Next Tasks:**
- Task 0.4: Python Environment and AI/ML Dependencies
- Task 2.1: AI Model Downloads and Verification
- Task 2.2: GPU Memory Allocation and Model Loading Strategy

**Parallel Candidates:**
- None (GPU drivers required for all GPU-dependent tasks)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Driver installation fails | Package conflicts, dependency errors | Use `apt --fix-broken install`, check repository |
| GPU not detected | nvidia-smi fails, no GPU in lspci | Check physical connections, verify driver loading |
| CUDA compilation errors | nvcc fails, missing libraries | Install build-essential, check GCC version |
| Container runtime issues | Docker GPU access fails | Restart docker service, verify runtime config |

**Debug Commands:**
```bash
# Driver diagnostics
lsmod | grep nvidia
dmesg | grep -i nvidia
journalctl -u nvidia-persistenced

# Hardware detection
lspci | grep -i nvidia
lshw -c display

# CUDA diagnostics
ls -la /usr/local/cuda*
ldconfig -p | grep cuda

# Container runtime diagnostics
docker info | grep -i nvidia
nvidia-container-cli info
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `NVIDIA_CUDA_Installation_Results.md`
- [ ] Update GPU configuration documentation

**Result Document Location:**
- Save to: `/project/tasks/results/NVIDIA_CUDA_Installation_Results.md`

**Notification Requirements:**
- [ ] Notify Task 0.4 owner that GPU drivers are ready
- [ ] Update project status dashboard
- [ ] Communicate GPU availability to AI model deployment team

## Notes

This task is critical for enabling all GPU-accelerated operations in the vector database server. The GT 1030 GPUs provide sufficient compute capability (6.1) for embedding model inference while being power-efficient for continuous operation.

Key considerations:
- GT 1030 GPUs have 6GB VRAM each (12GB total) suitable for embedding models
- CUDA 12.3 provides optimal performance for PyTorch and Transformers
- Container runtime enables GPU access within Docker containers
- Environment variables ensure system-wide CUDA availability

The installation process requires a system reboot to fully activate the drivers. Plan accordingly for any running services or processes.

---

**PRD References:** NFR-PERF-004, FR-VDB-002  
**Phase:** 0 - Infrastructure Foundation  
**Status:** Not Started
