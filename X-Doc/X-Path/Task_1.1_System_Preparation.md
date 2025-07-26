# Task 1.1: System Preparation and Base Configuration

## Pre-Task Checklist

**ALWAYS START WITH THIS CHECKLIST BEFORE ANY TASK:**

### 1. Rules Compliance ✅
- [x] **I have reviewed the .rulesfile** (/opt/citadel-02/.rulesfile)
- [x] No new virtual environments (use existing setup)
- [x] Follow assigned task exactly (no freelancing)
- [x] Server: hx-llm-server-02 (192.168.10.28)
- [x] PostgreSQL: 192.168.10.35 (citadel_llm_user/citadel_llm_db)

### 2. Current System State Validation ✅
```bash
# Verify current location and permissions
pwd  # Should be /opt/citadel-02 or subdirectory
whoami  # Should be agent0

# Check available models (ACTUAL DEPLOYED MODELS)
ollama list
# Expected models:
# - deepseek-r1:32b (19GB) - Strategic Research & Intelligence
# - hadad/JARVIS:latest (29GB) - Advanced Business Intelligence  
# - qwen:1.8b (1.1GB) - Lightweight Operations
# - deepcoder:14b (9.0GB) - Code Generation
# - yi:34b-chat (19GB) - Advanced Reasoning

# Verify system resources
free -h
df -h /opt/citadel-02
```

### 3. Environment Validation ✅
```bash
# Check Python environment
python3 --version  # Should be 3.12.x
which python3

# Verify Ollama service
systemctl status ollama
curl -s http://localhost:11434/api/tags | jq '.'

# Check network connectivity to Citadel services
ping -c 2 192.168.10.35  # SQL Database
ping -c 2 192.168.10.30  # Vector Database  
ping -c 2 192.168.10.37  # Metrics Server
ping -c 2 192.168.10.38  # Web Server
```

### 4. Documentation Reference ✅
- [x] Reference implementation plan: `/opt/citadel-02/X-Doc/LLM-02 Implementation Detailed Task Plan.md`
- [x] Check project README: `/opt/citadel-02/README.md`
- [x] Review any existing task results: `/opt/citadel-02/X-Doc/results/`

---

## Task Execution Template

### Task Information
**Task Number:** 1.1  
**Task Title:** System Preparation and Base Configuration for LLM-02 Server  
**Assigned Models:** All models (verification only)  
**Estimated Duration:** 2-3 hours  
**Priority:** Critical

### SMART+ST Validation
- [x] **Specific:** Clear system configuration requirements with defined security and performance parameters
- [x] **Measurable:** Specific validation commands and performance benchmarks for completion verification  
- [x] **Achievable:** Standard system administration tasks with proven procedures and established patterns
- [x] **Relevant:** Essential foundation for all subsequent LLM-02 deployment and business integration activities
- [x] **Small:** Focused on system preparation without AI model deployment or business application configuration
- [x] **Testable:** Comprehensive validation procedures with specific success criteria and performance metrics

### Model-Specific Considerations

**Available Models and Their Roles:**
- **deepseek-r1:32b (19GB):** Strategic research, competitive intelligence, market analysis
- **hadad/JARVIS:latest (29GB):** Advanced business intelligence, executive decision support
- **qwen:1.8b (1.1GB):** High-volume operations, quick processing, efficient tasks
- **deepcoder:14b (9.0GB):** Code generation, software development, system integration
- **yi:34b-chat (19GB):** Advanced reasoning, complex problem solving, strategic analysis

### Task Execution Steps

#### Pre-Execution Validation
```bash
# Confirm rules compliance
echo "✅ I have reviewed the .rulesfile and understand the project constraints"

# Verify working directory
cd /opt/citadel-02
pwd

# Check system status
ollama list | grep -E "(deepseek-r1:32b|hadad/JARVIS|qwen:1.8b|deepcoder:14b|yi:34b-chat)"
```

#### Execution Phase
1. **System Information Verification:**
```bash
# Verify Ubuntu version and system information
lsb_release -a
uname -a
hostnamectl
```

2. **User and Group Configuration:**
```bash
# Verify user configuration
id agent0
groups agent0
ls -la /home/agent0/
```

3. **Network Configuration Validation:**
```bash
# Check network configuration
ip addr show
ip route show
cat /etc/hosts
ping -c 3 192.168.10.35  # SQL Database
ping -c 3 192.168.10.30  # Vector Database
ping -c 3 192.168.10.37  # Metrics Server
ping -c 3 192.168.10.38  # Web Server
```

4. **Storage Configuration Assessment:**
```bash
# Check storage and filesystem
df -h
mount | grep -E "(ext4|xfs)"
du -sh /opt/citadel-02/
ls -la /opt/citadel-02/
```

5. **Security Configuration Review:**
```bash
# Check security settings
sudo ufw status
systemctl status ssh
sudo netstat -tlnp | grep -E "(22|8000|11434)"
```

6. **System Performance Baseline:**
```bash
# Establish performance baseline
free -h
cat /proc/cpuinfo | grep -E "(model name|processor|cores)"
cat /proc/meminfo | head -10
iostat -x 1 3
```

#### Validation Phase
```bash
# Comprehensive system health check
systemctl status ollama
curl -s http://localhost:11434/api/tags | jq '.'
python3 --version
which python3
pip3 list | grep -E "(ollama|fastapi|uvicorn)"
```

### Success Criteria
- [x] Ubuntu 24.04 LTS system verified and optimized
- [x] User agent0 properly configured with citadel group membership
- [x] Network connectivity to all Citadel services confirmed (192.168.10.x)
- [x] Storage configuration supports large model requirements (>100GB available)
- [x] Security configuration meets enterprise standards
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs
```
Ubuntu 24.04.x LTS
Python 3.12.x
agent0:citadel user configuration confirmed
Network connectivity: 192.168.10.35, 192.168.10.30, 192.168.10.37, 192.168.10.38
Storage: >100GB available in /opt/citadel-02
Ollama service: active (running)
All 5 models operational
```

### Risk Assessment & Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Network connectivity failure | Low | High | Verify network configuration and test all endpoints |
| Storage insufficient | Medium | High | Monitor disk usage and expand if needed |
| Service disruption | Low | Medium | Validate all services before and after changes |
| Permission issues | Low | Medium | Verify user/group configuration and file permissions |

### Rollback Procedures
**If Task Fails:**
1. Document current system state: `systemctl status ollama > system_state.log`
2. Verify all models still accessible: `ollama list`
3. Check service status: `systemctl status ollama`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_1.1_Issues.md`

### Post-Completion Actions
- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_1.1_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 1.2 dependencies

### Troubleshooting Reference
**Common Issues:**
- **Model not responding:** `systemctl restart ollama`
- **Permission issues:** Check file ownership and agent0 permissions
- **Network connectivity:** Verify Citadel service availability
- **Resource exhaustion:** Check `free -h` and `df -h`

**Debug Commands:**
```bash
# System diagnostics
journalctl -u ollama --no-pager -n 20
ps aux | grep ollama
netstat -tlnp | grep 11434
systemctl list-failed
```

---

## Task Completion Confirmation

**Before marking task complete:**
- [x] All success criteria met
- [x] All validation commands passed
- [x] System health verified
- [x] Documentation updated
- [x] Next task dependencies notified

**Completion Statement:**
"Task 1.1 completed successfully. System foundation prepared and verified. Ubuntu 24.04 LTS optimized, user configuration validated, network connectivity confirmed to all Citadel services, storage sufficient for model requirements. All models operational, system health verified, documentation updated. Ready for Task 1.2 - Python Environment and Dependencies Installation."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
