# Task 2.2: DeepCoder-14B Model Deployment and Configuration

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

**Task Number:** 2.2  
**Task Title:** DeepCoder-14B Model Deployment and Configuration  
**Assigned Models:** deepcoder:14b (Code Generation)  
**Estimated Duration:** 2-3 hours  
**Priority:** High

### SMART+ST Validation

- [x] **Specific:** Optimize DeepCoder-14B model for code generation and system integration
- [x] **Measurable:** Code quality metrics and generation performance validation
- [x] **Achievable:** Model already deployed, focusing on optimization and business applications
- [x] **Relevant:** Essential for software development and business automation tasks
- [x] **Small:** Focused on single model optimization for coding capabilities
- [x] **Testable:** Code generation tests and integration scenario validation

### Model-Specific Considerations

**Primary Model: deepcoder:14b (9.0GB)**

- **Role:** Code generation, software development, system integration
- **Business Applications:** Automation scripting, API development, system integration code
- **Resource Requirements:** 16GB memory recommended, 9GB storage
- **Performance Targets:** <20s response time for code generation, syntactically correct output

### Task Execution Steps

#### Pre-Execution Validation

```bash
# Confirm rules compliance
echo "✅ I have reviewed the .rulesfile and understand the project constraints"

# Verify working directory
cd /opt/citadel-02
pwd

# Check system status - Focus on DeepCoder model
ollama list | grep "deepcoder:14b"

# Verify Task 2.1 completion
ls -la /opt/citadel-02/X-Doc/results/Task_2.1_Results.md
```

#### Execution Phase

1. **DeepCoder Model Status Verification:**

```bash
# Check DeepCoder model status and details
ollama list | grep "deepcoder:14b"
ollama show deepcoder:14b

# Verify model accessibility
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"def hello_world():\n    print(\"Hello, World!\")","stream":false}' \
  | jq '.'
```

2. **Code Generation Testing:**

```bash
# Test Python code generation
echo "Testing Python code generation..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Create a Python function that connects to PostgreSQL database and executes a query:","stream":false}' \
  | jq '.response' > deepcoder_python_test.log

# Test API endpoint creation
echo "Testing API endpoint generation..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Create a FastAPI endpoint that accepts a POST request with JSON data and returns a processed response:","stream":false}' \
  | jq '.response' > deepcoder_api_test.log

# Test system integration code
echo "Testing system integration code..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Write Python code to integrate with Ollama API and process multiple model responses:","stream":false}' \
  | jq '.response' > deepcoder_integration_test.log
```

3. **Business Automation Scenarios:**

```bash
# Test business automation scripting
echo "Testing business automation..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Create a Python script that automates report generation from database queries and sends email notifications:","stream":false}' \
  | jq '.response' > deepcoder_automation_test.log

# Test monitoring and logging code
echo "Testing monitoring code generation..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Write Python code for system monitoring that checks service health and logs metrics to Prometheus:","stream":false}' \
  | jq '.response' > deepcoder_monitoring_test.log
```

4. **Performance and Quality Assessment:**

```bash
# Measure code generation response time
echo "Measuring code generation performance..."
time curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Create a complete Python class for handling database connections with connection pooling and error handling:","stream":false}' \
  > deepcoder_performance_test.log

# Test code completion capabilities
echo "Testing code completion..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Complete this Python function:\ndef process_llm_response(response_data):\n    # Process the response from LLM model\n    # Extract relevant information\n    # Return structured data\n","stream":false}' \
  | jq '.response' > deepcoder_completion_test.log
```

5. **Business Integration Configuration:**

```bash
# Create DeepCoder specific configuration
mkdir -p /opt/citadel-02/config/models/deepcoder/
cat > /opt/citadel-02/config/models/deepcoder/configuration.yaml << 'EOF'
# DeepCoder-14B Configuration
model: "deepcoder:14b"
role: "code_generation"

optimization:
  temperature: 0.3
  top_p: 0.95
  max_tokens: 2048
  context_length: 8192
  
coding_settings:
  language_support:
    - python
    - javascript
    - sql
    - yaml
    - bash
  frameworks:
    - fastapi
    - flask
    - sqlalchemy
    - ollama
  
business_applications:
  automation_scripts: true
  api_development: true
  system_integration: true
  monitoring_code: true
  database_operations: true
  
performance:
  target_response_time: 20
  memory_allocation: "16GB"
  concurrent_requests: 3
  
quality_checks:
  syntax_validation: true
  best_practices: true
  security_considerations: true
  documentation_generation: true
EOF

# Set proper permissions
chown agent0:citadel /opt/citadel-02/config/models/deepcoder/configuration.yaml
chmod 640 /opt/citadel-02/config/models/deepcoder/configuration.yaml
```

#### Validation Phase

```bash
# Comprehensive DeepCoder validation
echo "Validating DeepCoder optimization..."

# Verify model responsiveness
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"print(\"test\")","stream":false}' \
  | jq '.response'

# Check code quality in generated responses
echo "Checking code quality..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepcoder:14b","prompt":"Create a Python function to validate email addresses using regex:","stream":false}' \
  | jq '.response' | grep -E "(def |import |return)"

# Verify configuration files
python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/models/deepcoder/configuration.yaml'))"

# System health check
systemctl status ollama
curl -s http://localhost:11434/api/tags | jq '.models[] | select(.name=="deepcoder:14b")'
```

### Success Criteria

- [x] DeepCoder model responding correctly with quality code generation
- [x] Response time for code generation under 20 seconds
- [x] Generated code syntactically correct and follows best practices
- [x] Business automation and integration scenarios validated
- [x] API development and system integration capabilities confirmed
- [x] Performance within acceptable parameters
- [x] Configuration files created and validated
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs

```bash
✅ DeepCoder Model Status: Active and Optimized
✅ Code Generation: High-quality, syntactically correct
✅ Response Time: <20 seconds for complex code requests
✅ Business Integration: Automation scenarios validated
✅ API Development: FastAPI endpoints generated successfully
✅ Configuration: Optimization settings applied
✅ All 5 models: Operational
```

### Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Generated code errors | Medium | Medium | Implement code validation and testing procedures |
| Slow response times | Low | Medium | Optimize temperature and token settings |
| Model unresponsive | Low | High | Monitor service status and restart if needed |
| Poor code quality | Low | Medium | Fine-tune model parameters for code generation |

### Rollback Procedures

**If Task Fails:**

1. Remove DeepCoder configuration: `rm -rf /opt/citadel-02/config/models/deepcoder/`
2. Restart Ollama service: `sudo systemctl restart ollama`
3. Verify model accessibility: `ollama list | grep deepcoder:14b`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_2.2_Issues.md`

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_2.2_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 2.3 dependencies

### Troubleshooting Reference

**Common Issues:**

- **Poor code quality:** Adjust temperature (lower for more deterministic code)
- **Slow generation:** Check available memory and reduce max_tokens if needed
- **Syntax errors:** Verify model prompt formatting and context
- **Model errors:** Check model integrity with `ollama show deepcoder:14b`

**Debug Commands:**

```bash
# DeepCoder diagnostics
ollama show deepcoder:14b
curl -v http://localhost:11434/api/generate -d '{"model":"deepcoder:14b","prompt":"test","stream":false}'
tail -f /opt/citadel-02/logs/system/citadel-llm-02.log | grep deepcoder
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
"Task 2.2 completed successfully. DeepCoder-14B model optimized for code generation and system integration. Code quality high, response times under 20 seconds, business automation scenarios validated. API development and integration capabilities confirmed. Configuration applied, all models operational, system health verified, documentation updated. Ready for Task 2.3 - Qwen Model Deployment for High-Volume Operations."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
