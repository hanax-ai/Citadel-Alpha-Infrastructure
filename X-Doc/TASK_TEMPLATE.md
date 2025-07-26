# Task Startup Template for LLM-02 Implementation

## Pre-Task Checklist

**ALWAYS START WITH THIS CHECKLIST BEFORE ANY TASK:**

### 1. Rules Compliance ✅
- [ ] **I have reviewed the .rulesfile** (/opt/citadel-02/.rulesfile)
- [ ] No new virtual environments (use existing setup)
- [ ] Follow assigned task exactly (no freelancing)
- [ ] Server: hx-llm-server-02 (192.168.10.28)
- [ ] PostgreSQL: 192.168.10.35 (citadel_llm_user/citadel_llm_db)

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
- [ ] Reference implementation plan: `/opt/citadel-02/X-Doc/LLM-02 Implementation Detailed Task Plan.md`
- [ ] Check project README: `/opt/citadel-02/README.md`
- [ ] Review any existing task results: `/opt/citadel-02/X-Doc/results/`

---

## Task Execution Template

### Task Information
**Task Number:** [X.X]  
**Task Title:** [Specific Task Name]  
**Assigned Models:** [Specify which of the 5 deployed models are relevant]  
**Estimated Duration:** [X hours]  
**Priority:** [Critical/High/Medium/Low]

### SMART+ST Validation
- [ ] **Specific:** Clear requirements and deliverables defined
- [ ] **Measurable:** Success criteria and validation procedures identified  
- [ ] **Achievable:** Task scope realistic with available resources
- [ ] **Relevant:** Task contributes to LLM-02 business objectives
- [ ] **Small:** Task focused without unnecessary complexity
- [ ] **Testable:** Validation procedures defined and executable

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
1. **[Step 1]:** [Specific action with commands]
2. **[Step 2]:** [Specific action with commands]  
3. **[Step 3]:** [Specific action with commands]

#### Validation Phase
```bash
# Task-specific validation commands
[Insert specific validation commands for the task]

# System health check
curl -s http://localhost:11434/api/tags | jq '.'
systemctl status ollama
```

### Success Criteria
- [ ] [Specific success criterion 1]
- [ ] [Specific success criterion 2]
- [ ] [Specific success criterion 3]
- [ ] All models remain operational
- [ ] System performance maintained
- [ ] No disruption to existing services

### Expected Outputs
```
[Define expected command outputs and system responses]
```

### Risk Assessment & Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [Low/Med/High] | [Low/Med/High] | [Mitigation strategy] |

### Rollback Procedures
**If Task Fails:**
1. [Specific rollback step 1]
2. [Specific rollback step 2]
3. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
4. Document issues for analysis

### Post-Completion Actions
- [ ] Update task status in project documentation
- [ ] Create result summary: `/opt/citadel-02/X-Doc/results/Task_[X.X]_Results.md`
- [ ] Verify all models operational: `ollama list`
- [ ] Update project README if needed
- [ ] Notify next task dependencies

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
```

---

## Task Completion Confirmation

**Before marking task complete:**
- [ ] All success criteria met
- [ ] All validation commands passed
- [ ] System health verified
- [ ] Documentation updated
- [ ] Next task dependencies notified

**Completion Statement:**
"Task [X.X] completed successfully. All models operational, system health verified, documentation updated. Ready for next task in sequence."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0