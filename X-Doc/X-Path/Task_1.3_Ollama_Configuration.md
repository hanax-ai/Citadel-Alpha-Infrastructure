# Task 1.3: Ollama Installation and Configuration

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

**Task Number:** 1.3  
**Task Title:** Ollama Installation and Configuration  
**Assigned Models:** All models (service optimization)  
**Estimated Duration:** 1-2 hours  
**Priority:** Critical

### SMART+ST Validation

- [x] **Specific:** Optimize Ollama service configuration for business-grade AI operations
- [x] **Measurable:** Service performance metrics and model response verification
- [x] **Achievable:** Ollama already installed, focusing on optimization and validation
- [x] **Relevant:** Essential service optimization for all AI model operations
- [x] **Small:** Focused on service configuration without new model deployment
- [x] **Testable:** Service status checks and model response validation

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

# Verify previous tasks completion
ls -la /opt/citadel-02/X-Doc/results/Task_1.1_Results.md
ls -la /opt/citadel-02/X-Doc/results/Task_1.2_Results.md
```

#### Execution Phase

1. **Ollama Service Status Verification:**

```bash
# Check current Ollama installation and status
systemctl status ollama
ollama --version
which ollama
ps aux | grep ollama
```

2. **Service Configuration Optimization:**

```bash
# Verify Ollama configuration
cat /etc/systemd/system/ollama.service
systemctl cat ollama.service

# Check service listening configuration
netstat -tlnp | grep 11434
ss -tlnp | grep 11434
```

3. **Model Inventory and Health Check:**

```bash
# Comprehensive model verification
ollama list
curl -s http://localhost:11434/api/tags | jq '.'

# Test each model responsiveness
echo "Testing deepseek-r1:32b..."
curl -s -X POST http://localhost:11434/api/generate -d '{"model":"deepseek-r1:32b","prompt":"Hello","stream":false}' | jq '.'

echo "Testing hadad/JARVIS:latest..."
curl -s -X POST http://localhost:11434/api/generate -d '{"model":"hadad/JARVIS:latest","prompt":"Hello","stream":false}' | jq '.'

echo "Testing qwen:1.8b..."
curl -s -X POST http://localhost:11434/api/generate -d '{"model":"qwen:1.8b","prompt":"Hello","stream":false}' | jq '.'

echo "Testing deepcoder:14b..."
curl -s -X POST http://localhost:11434/api/generate -d '{"model":"deepcoder:14b","prompt":"Hello","stream":false}' | jq '.'

echo "Testing yi:34b-chat..."
curl -s -X POST http://localhost:11434/api/generate -d '{"model":"yi:34b-chat","prompt":"Hello","stream":false}' | jq '.'
```

4. **Performance and Resource Monitoring:**

```bash
# Monitor system resources during model operations
free -h
df -h
iostat -x 1 3

# Check Ollama service logs
journalctl -u ollama --no-pager -n 20
```

5. **Business Configuration Optimization:**

```bash
# Create Ollama configuration directory if needed
mkdir -p /home/agent0/.ollama
chown agent0:citadel /home/agent0/.ollama

# Verify environment variables
env | grep -i ollama
echo $OLLAMA_HOST
echo $OLLAMA_ORIGINS
```

#### Validation Phase

```bash
# Comprehensive service validation
systemctl is-active ollama
systemctl is-enabled ollama
curl -s http://localhost:11434/api/version | jq '.'
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# Model accessibility verification
ollama list | wc -l  # Should show 5 models
curl -s http://localhost:11434/api/tags | jq '.models | length'  # Should be 5
```

### Success Criteria

- [x] Ollama service running and optimized for business operations
- [x] All 5 models (deepseek-r1:32b, hadad/JARVIS, qwen:1.8b, deepcoder:14b, yi:34b-chat) responsive
- [x] Service configuration supports high-performance AI operations
- [x] API endpoints accessible and responding correctly
- [x] System resources adequate for concurrent model operations
- [x] Service logs show healthy operation status
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs

```bash
● ollama.service - Ollama Service
   Active: active (running)
   
Model verification:
✅ deepseek-r1:32b responding
✅ hadad/JARVIS:latest responding  
✅ qwen:1.8b responding
✅ deepcoder:14b responding
✅ yi:34b-chat responding

API Status: 200 OK
Models Count: 5
Service Health: Optimal
```

### Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Service interruption | Low | High | Monitor service status throughout task |
| Model unresponsive | Low | Medium | Test each model individually and restart if needed |
| Resource exhaustion | Medium | Medium | Monitor system resources during testing |
| Configuration corruption | Low | High | Backup current configuration before changes |

### Rollback Procedures

**If Task Fails:**

1. Restart Ollama service: `sudo systemctl restart ollama`
2. Verify service status: `systemctl status ollama`
3. Check model accessibility: `ollama list`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_1.3_Issues.md`

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_1.3_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 1.4 dependencies

### Troubleshooting Reference

**Common Issues:**

- **Service not responding:** `sudo systemctl restart ollama`
- **Port conflicts:** Check `netstat -tlnp | grep 11434`
- **Model loading issues:** Check available memory and disk space
- **API errors:** Verify service logs with `journalctl -u ollama -f`

**Debug Commands:**

```bash
# Service diagnostics
systemctl status ollama --no-pager -l
journalctl -u ollama --no-pager -n 50
curl -v http://localhost:11434/api/version
ollama ps
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
"Task 1.3 completed successfully. Ollama service optimized and verified for business-grade AI operations. All 5 models (deepseek-r1:32b, hadad/JARVIS, qwen:1.8b, deepcoder:14b, yi:34b-chat) responding correctly. Service configuration supports high-performance operations, API endpoints verified, system resources adequate. All models operational, system health verified, documentation updated. Ready for Task 1.4 - Configuration Management System Implementation."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
