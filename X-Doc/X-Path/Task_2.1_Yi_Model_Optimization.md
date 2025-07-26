# Task 2.1: Yi-34B Model Deployment and Optimization

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

**Task Number:** 2.1  
**Task Title:** Yi-34B Model Deployment and Optimization  
**Assigned Models:** yi:34b-chat (Advanced Reasoning)  
**Estimated Duration:** 2-3 hours  
**Priority:** High

### SMART+ST Validation

- [x] **Specific:** Optimize Yi-34B model for advanced reasoning and strategic analysis
- [x] **Measurable:** Model performance benchmarks and response quality verification
- [x] **Achievable:** Model already deployed, focusing on optimization and business integration
- [x] **Relevant:** Critical for advanced reasoning and strategic business decision support
- [x] **Small:** Focused on single model optimization without system-wide changes
- [x] **Testable:** Performance tests and business scenario validation

### Model-Specific Considerations

**Primary Model: yi:34b-chat (19GB)**

- **Role:** Advanced reasoning, complex problem solving, strategic analysis
- **Business Applications:** Strategic planning, complex decision support, analytical reasoning
- **Resource Requirements:** 36GB memory recommended, 19GB storage
- **Performance Targets:** <30s response time for complex queries, high reasoning accuracy

### Task Execution Steps

#### Pre-Execution Validation

```bash
# Confirm rules compliance
echo "✅ I have reviewed the .rulesfile and understand the project constraints"

# Verify working directory
cd /opt/citadel-02
pwd

# Check system status - Focus on Yi-34B model
ollama list | grep "yi:34b-chat"

# Verify Phase 1 completion
ls -la /opt/citadel-02/X-Doc/results/Task_1.4_Results.md
ls -la /opt/citadel-02/config/models/model_config.yaml
```

#### Execution Phase

1. **Yi-34B Model Status Verification:**

```bash
# Check Yi-34B model status and details
ollama list | grep "yi:34b-chat"
ollama show yi:34b-chat

# Verify model accessibility
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Hello, please introduce yourself briefly.","stream":false}' \
  | jq '.'
```

2. **Performance Baseline Testing:**

```bash
# Test basic reasoning capabilities
echo "Testing basic reasoning..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Analyze the pros and cons of implementing AI in business operations.","stream":false}' \
  | jq '.response' | head -20

# Test complex problem solving
echo "Testing complex problem solving..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"A company needs to choose between three strategic options: expand internationally, focus on product innovation, or acquire competitors. Provide a structured analysis framework.","stream":false}' \
  | jq '.response' | head -30

# Measure response time
echo "Measuring response time..."
time curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Explain the strategic implications of digital transformation for traditional businesses.","stream":false}' \
  > yi_response_time.log
```

3. **Business Integration Testing:**

```bash
# Test strategic analysis capabilities
echo "Testing strategic analysis..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Given the following scenario: A tech startup with 50 employees is considering raising Series B funding. What are the key factors they should consider and what analysis framework would you recommend?","stream":false}' \
  | jq '.response' > yi_strategic_test.log

# Test decision support scenarios
echo "Testing decision support..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"A manufacturing company faces supply chain disruptions. Analyze the situation using a risk assessment matrix and provide mitigation strategies.","stream":false}' \
  | jq '.response' > yi_decision_test.log
```

4. **Resource Usage Monitoring:**

```bash
# Monitor system resources during Yi-34B operations
echo "Monitoring resource usage during Yi-34B operations..."

# Check memory usage
free -h
ps aux | grep ollama | head -5

# Monitor during model operation
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Provide a comprehensive analysis of market segmentation strategies for a B2B SaaS company entering the European market.","stream":false}' \
  > /dev/null &

# Monitor resources while model is working
sleep 5
echo "Memory usage during operation:"
free -h
echo "CPU usage:"
top -bn1 | grep "Cpu(s)" | head -1
```

5. **Model Configuration Optimization:**

```bash
# Review current Yi-34B configuration
cat /opt/citadel-02/config/models/model_config.yaml | grep -A 10 "yi_chat:"

# Create Yi-34B specific optimization settings
mkdir -p /opt/citadel-02/config/models/yi/
cat > /opt/citadel-02/config/models/yi/optimization.yaml << 'EOF'
# Yi-34B Optimization Configuration
model: "yi:34b-chat"
role: "advanced_reasoning"

optimization:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 4096
  context_length: 32768
  
business_settings:
  strategic_analysis: true
  decision_support: true
  complex_reasoning: true
  analytical_framework: true
  
performance:
  target_response_time: 30
  memory_allocation: "36GB"
  concurrent_requests: 2
  
use_cases:
  - strategic_planning
  - market_analysis
  - risk_assessment
  - decision_matrices
  - competitive_analysis
  - business_intelligence
EOF

# Set proper permissions
chown agent0:citadel /opt/citadel-02/config/models/yi/optimization.yaml
chmod 640 /opt/citadel-02/config/models/yi/optimization.yaml
```

#### Validation Phase

```bash
# Comprehensive Yi-34B validation
echo "Validating Yi-34B optimization..."

# Verify model responsiveness
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Test","stream":false}' \
  | jq '.response'

# Check if model handles complex queries
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"yi:34b-chat","prompt":"Analyze the ROI implications of implementing an enterprise AI platform across multiple business units.","stream":false}' \
  | jq '.response' | wc -w

# Verify configuration files
python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/models/yi/optimization.yaml'))"

# System health check
systemctl status ollama
curl -s http://localhost:11434/api/tags | jq '.models[] | select(.name=="yi:34b-chat")'
```

### Success Criteria

- [x] Yi-34B model responding correctly and optimally
- [x] Response time for complex queries under 30 seconds
- [x] Model demonstrates advanced reasoning capabilities
- [x] Strategic analysis and decision support functions validated
- [x] Business scenario testing completed successfully
- [x] Resource usage within acceptable parameters
- [x] Optimization configuration files created and validated
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs

```bash
✅ Yi-34B Model Status: Active and Optimized
✅ Response Time: <30 seconds for complex queries
✅ Reasoning Quality: High-quality strategic analysis
✅ Business Integration: Decision support validated
✅ Resource Usage: Within limits (Memory: 36GB allocated)
✅ Configuration: Optimization settings applied
✅ All 5 models: Operational
```

### Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| High memory usage | Medium | Medium | Monitor system resources and optimize parameters |
| Slow response times | Low | Medium | Adjust model parameters and validate performance |
| Model unresponsive | Low | High | Restart Ollama service if needed |
| Configuration errors | Low | Low | Validate YAML syntax before applying |

### Rollback Procedures

**If Task Fails:**

1. Restore default Yi-34B settings: `rm -f /opt/citadel-02/config/models/yi/optimization.yaml`
2. Restart Ollama service: `sudo systemctl restart ollama`
3. Verify model accessibility: `ollama list | grep yi:34b-chat`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_2.1_Issues.md`

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_2.1_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 2.2 dependencies

### Troubleshooting Reference

**Common Issues:**

- **Slow responses:** Check available memory and reduce concurrent requests
- **Model errors:** Verify model integrity with `ollama show yi:34b-chat`
- **High memory usage:** Monitor with `free -h` and adjust optimization settings
- **Configuration issues:** Validate YAML syntax and file permissions

**Debug Commands:**

```bash
# Yi-34B diagnostics
ollama show yi:34b-chat
curl -v http://localhost:11434/api/generate -d '{"model":"yi:34b-chat","prompt":"test","stream":false}'
ps aux | grep ollama
journalctl -u ollama -f | grep yi
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
"Task 2.1 completed successfully. Yi-34B model optimized for advanced reasoning and strategic analysis. Response times under 30 seconds, high-quality reasoning capabilities validated, business scenario testing successful. Resource usage within limits, optimization configuration applied. All models operational, system health verified, documentation updated. Ready for Task 2.2 - DeepCoder-14B Model Deployment and Configuration."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
