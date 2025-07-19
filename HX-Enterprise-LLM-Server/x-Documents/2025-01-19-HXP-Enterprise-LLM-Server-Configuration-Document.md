clear
# HXP-Enterprise LLM Server Configuration Document

**Document Version:** 1.0  
**Creation Date:** January 19, 2025  
**Server:** hx-llm-server-01 (192.168.10.29)  
**Project:** Citadel Alpha Infrastructure  
**Component:** HXP-Enterprise LLM Server  

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Hardware Specifications](#hardware-specifications)
3. [Operating System Configuration](#operating-system-configuration)
4. [Storage Configuration](#storage-configuration)
5. [GPU Configuration](#gpu-configuration)
6. [Network Configuration](#network-configuration)
7. [Software Stack](#software-stack)
8. [Directory Structure](#directory-structure)
9. [Infrastructure Connectivity](#infrastructure-connectivity)
10. [Security Configuration](#security-configuration)
11. [Performance Specifications](#performance-specifications)
12. [Maintenance Procedures](#maintenance-procedures)

---

## System Overview

### Server Information
- **Hostname:** hx-llm-server-01
- **IP Address:** 192.168.10.29/24
- **Role:** HXP-Enterprise LLM Server
- **Environment:** Production R&D
- **Architecture:** x86_64

### Purpose
The HXP-Enterprise LLM Server serves as the third critical component of the Citadel AI Operating System, providing enterprise-grade AI model inference services with high-performance GPU acceleration and comprehensive monitoring capabilities.

---

## Hardware Specifications

### CPU
- **Model:** Intel Core Ultra 9 285K
- **Architecture:** x86_64
- **Cores:** 24 (8P + 16E)
- **Threads:** 32
- **Base Frequency:** 3.2 GHz
- **Max Frequency:** 5.2 GHz
- **Cache:** 24MB L3 Cache
- **TDP:** 125W

### Memory
- **Total RAM:** 125GB
- **Type:** DDR5
- **Speed:** 5600 MT/s
- **Channels:** Dual Channel
- **ECC:** Non-ECC

### Storage
- **Primary NVMe:** 3.6TB (nvme0n1) - System and Models
- **Secondary NVMe:** 3.6TB (nvme1n1) - Unallocated
- **SATA Storage:** 7.3TB (sda) - Logs and Data
- **Boot Device:** NVMe (nvme1n1)

### GPU Configuration
- **Primary GPU:** NVIDIA GeForce RTX 4070 Ti SUPER (GPU 0)
  - **Memory:** 16GB GDDR6X
  - **CUDA Cores:** 8448
  - **Bus ID:** 00000000:02:00.0
  - **Power:** 285W TDP

- **Secondary GPU:** NVIDIA GeForce RTX 4070 Ti SUPER (GPU 1)
  - **Memory:** 16GB GDDR6X
  - **CUDA Cores:** 8448
  - **Bus ID:** 00000000:81:00.0
  - **Power:** 285W TDP

### Network
- **Interface:** Ethernet
- **Speed:** 1Gbps
- **IP Configuration:** Static
- **Subnet:** 192.168.10.0/24
- **Gateway:** 192.168.10.1

---

## Operating System Configuration

### System Information
- **OS:** Ubuntu 24.04 LTS (Noble Numbat)
- **Kernel:** 6.14.0-24-generic
- **Architecture:** x86_64
- **Last Updated:** January 19, 2025

### System Services
- **SSH:** Enabled and configured
- **Firewall:** UFW (Uncomplicated Firewall)
- **Systemd:** Active and operational
- **Automatic Updates:** Configured

### User Configuration
- **Primary User:** agent0
- **Sudo Access:** Enabled
- **Home Directory:** /home/agent0
- **Shell:** /bin/bash

---

## Storage Configuration

### Mount Points

#### Model Storage (High Performance)
- **Device:** /dev/nvme0n1p1
- **Mount Point:** /mnt/nvme0n1
- **Filesystem:** ext4
- **Size:** 3.6TB
- **Purpose:** AI Model Storage
- **UUID:** [Auto-generated]
- **fstab Entry:** /dev/nvme0n1p1 /mnt/nvme0n1 ext4 defaults 0 2

#### Log Storage (High Capacity)
- **Device:** /dev/sda1
- **Mount Point:** /mnt/sda
- **Filesystem:** ext4
- **Size:** 7.3TB
- **Purpose:** Log Files and Data Storage
- **UUID:** [Auto-generated]
- **fstab Entry:** /dev/sda1 /mnt/sda ext4 defaults 0 2

### Directory Structure

#### Model Directories
```
/mnt/nvme0n1/models/
├── mixtral-8x7b/
├── hermes-2/
├── openchat-3.5/
└── phi-3-mini/
```

#### Log Directories
```
/mnt/sda/logs/
├── inference/
├── system/
└── service/
```

### Storage Policy
- **Models:** Stored exclusively on NVMe storage for optimal performance
- **Logs:** Stored on SATA storage to preserve NVMe space
- **Root Filesystem:** No models or logs stored on root partition
- **Backup:** Separate backup storage configuration

---

## GPU Configuration

### NVIDIA Driver
- **Version:** 570.158.01
- **Installation Method:** Ubuntu repository
- **Status:** Active and loaded
- **Modules:** nvidia, nvidia_drm, nvidia_uvm, nvidia_modeset

### CUDA Configuration
- **CUDA Version:** 12.8
- **CUDA Toolkit:** 12.0.140
- **Installation Path:** /usr/local/cuda
- **Environment Variables:** Configured
- **Compatibility:** vLLM compatible

### GPU Monitoring
- **Tool:** nvidia-smi
- **Status:** Both GPUs operational
- **Temperature Monitoring:** Active
- **Power Management:** P0 state (maximum performance)
- **Memory Usage:** 0MB/16376MB per GPU

### GPU Optimization
- **Multi-GPU Support:** Enabled
- **CUDA Multi-Process Service:** Available
- **Memory Pooling:** Configured for vLLM
- **Tensor Parallelism:** Supported

---

## Network Configuration

### Network Interfaces
- **Primary Interface:** eth0
- **IP Address:** 192.168.10.29
- **Netmask:** 255.255.255.0
- **Gateway:** 192.168.10.1
- **DNS:** 8.8.8.8, 8.8.4.4

### Network Services
- **SSH:** Port 22 (Open)
- **HTTP/HTTPS:** Ports 80, 443 (Configured for API)
- **Custom Ports:** 8000-9000 (vLLM services)

### Infrastructure Connectivity
- **Vector Database Server:** 192.168.10.30 ✅ (Reachable)
- **SQL Database Server:** 192.168.10.35 ⏸️ (Pending validation)
- **Network Latency:** <1ms to local infrastructure

---

## Software Stack

### Core Software
- **Python:** 3.12.3 (Target version)
- **CUDA Toolkit:** 12.0.140
- **NVIDIA Drivers:** 570.158.01
- **Git:** Latest version
- **Build Tools:** gcc, g++, make

### AI/ML Libraries (To be installed)
- **vLLM:** 0.3.2 (Target version)
- **PyTorch:** CUDA-enabled version
- **Transformers:** Latest stable
- **Accelerate:** Latest version
- **Bitsandbytes:** Latest version

### System Utilities
- **htop:** System monitoring
- **iotop:** I/O monitoring
- **nethogs:** Network monitoring
- **ncdu:** Disk usage analysis

---

## Directory Structure

### Project Structure
```
/home/agent0/Citadel-Alpha-Infrastructure/
├── HX-Enterprise-LLM-Server/
│   ├── 0.0-Project-Management/
│   ├── 0.1-Project-Execution/
│   └── x-Documents/
└── [Other project components]
```

### System Directories
```
/opt/
├── models/ -> /mnt/nvme0n1/models/
├── citadel/ -> /mnt/sda/
├── cache/
└── backup/

/var/
├── log/citadel-llm/
└── [System logs]

/mnt/
├── nvme0n1/ (Model storage)
└── sda/ (Log storage)
```

---

## Infrastructure Connectivity

### External Dependencies
1. **Vector Database Server (192.168.10.30)**
   - **Service:** Qdrant Vector Database
   - **Port:** 6333
   - **Status:** ✅ Reachable
   - **Purpose:** Vector embeddings storage

2. **SQL Database Server (192.168.10.35)**
   - **Service:** PostgreSQL Database
   - **Port:** 5432
   - **Status:** ⏸️ Pending validation
   - **Purpose:** Metadata and user data storage

### Service Dependencies
- **Authentication Service:** TBD
- **Monitoring Service:** TBD
- **Load Balancer:** TBD
- **API Gateway:** TBD

---

## Security Configuration

### Access Control
- **SSH Access:** Key-based authentication preferred
- **Sudo Access:** Limited to agent0 user
- **File Permissions:** 755 for directories, 644 for files
- **User Isolation:** Dedicated user for AI services

### Network Security
- **Firewall:** UFW configured
- **Port Restrictions:** Only necessary ports open
- **Internal Network:** 192.168.10.0/24 trusted
- **External Access:** Restricted

### Data Security
- **Model Storage:** Encrypted at rest (if required)
- **Log Storage:** Access controlled
- **Backup Encryption:** TBD
- **API Security:** Authentication required

---

## Performance Specifications

### Computational Performance
- **CPU Performance:** 24 cores, 5.2GHz max
- **Memory Bandwidth:** DDR5 5600 MT/s
- **GPU Performance:** 2x RTX 4070 Ti SUPER
- **Storage I/O:** NVMe for models, SATA for logs

### AI Model Performance Targets
- **Mixtral-8x7B:** 50+ tokens/second
- **Hermes-2:** 40+ tokens/second
- **OpenChat-3.5:** 45+ tokens/second
- **Phi-3-Mini:** 60+ tokens/second

### System Performance
- **Concurrent Users:** 10+ simultaneous
- **Response Time:** <2 seconds
- **Uptime Target:** 99.9%
- **Throughput:** 1000+ requests/hour

---

## Maintenance Procedures

### Regular Maintenance
1. **System Updates:** Weekly security updates
2. **Log Rotation:** Daily log management
3. **Storage Monitoring:** Weekly disk usage check
4. **Performance Monitoring:** Continuous monitoring

### Backup Procedures
1. **Configuration Backup:** Daily
2. **Model Backup:** Weekly
3. **Log Backup:** Daily
4. **System Backup:** Weekly

### Emergency Procedures
1. **Service Restart:** Automated recovery
2. **GPU Reset:** Manual intervention if needed
3. **Storage Recovery:** From backup
4. **Network Recovery:** Failover procedures

### Monitoring
1. **System Health:** CPU, Memory, GPU usage
2. **Storage Health:** Disk space, I/O performance
3. **Network Health:** Connectivity, latency
4. **Service Health:** API availability, response times

---

## Configuration Validation

### Pre-Deployment Checklist
- [x] Hardware specifications verified
- [x] Operating system installed and updated
- [x] GPU drivers installed and functional
- [x] CUDA toolkit installed and tested
- [x] Storage configured and mounted
- [x] Network connectivity established
- [x] Directory structure created
- [x] Permissions configured

### Post-Deployment Validation
- [ ] AI models downloaded and tested
- [ ] vLLM services configured and running
- [ ] API endpoints functional
- [ ] Monitoring systems active
- [ ] Backup systems operational
- [ ] Security measures implemented
- [ ] Performance benchmarks completed

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-19 | Agent Zero | Initial configuration document |

---

## Contact Information

- **System Administrator:** Agent Zero
- **Project Manager:** [TBD]
- **Technical Lead:** [TBD]
- **Support Contact:** [TBD]

---

**Document Status:** Active  
**Last Updated:** January 19, 2025  
**Next Review:** February 19, 2025 