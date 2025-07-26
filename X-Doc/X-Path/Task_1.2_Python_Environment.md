# Task 1.2: Python Environment and Dependencies Installation

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

**Task Number:** 1.2  
**Task Title:** Python Environment and Dependencies Installation  
**Assigned Models:** All models (dependency verification)  
**Estimated Duration:** 1-2 hours  
**Priority:** Critical

### SMART+ST Validation

- [x] **Specific:** Install Python 3.12 environment with comprehensive AI/ML dependencies
- [x] **Measurable:** Specific package versions and import verification procedures  
- [x] **Achievable:** Standard Python package installation with proven dependencies
- [x] **Relevant:** Essential Python environment for all AI model operations and business integrations
- [x] **Small:** Focused on Python environment without model deployment or business applications
- [x] **Testable:** Import tests and version verification for all critical dependencies

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

# Verify Task 1.1 completion
ls -la /opt/citadel-02/X-Doc/results/Task_1.1_Results.md
```

#### Execution Phase

1. **Python Environment Verification:**

```bash
# Verify Python 3.12 installation
python3 --version
python3 -c "import sys; print(sys.version_info)"
which python3
which pip3
```

2. **Citadel Virtual Environment Creation:**

```bash
# Create citadel_venv virtual environment as required by .rulesfile
cd /opt/citadel-02
python3 -m venv citadel_venv
source citadel_venv/bin/activate
pip install --upgrade pip
```

3. **Core API and Async Framework Dependencies:**

```bash
# Install API framework dependencies
source citadel_venv/bin/activate
pip install fastapi uvicorn pydantic requests httpx aiohttp asyncio-mqtt websockets
```

4. **Database and Caching Dependencies:**

```bash
# Install database connectivity
source citadel_venv/bin/activate
pip install psycopg2-binary sqlalchemy alembic redis
```

5. **AI/ML Framework Dependencies:**

```bash
# Install AI/ML libraries
source citadel_venv/bin/activate
pip install torch torchvision transformers huggingface-hub
```

6. **Development and Testing Dependencies:**

```bash
# Install development tools
source citadel_venv/bin/activate
pip install pytest pytest-asyncio pytest-mock black isort flake8 mypy
```

7. **Monitoring and Configuration Dependencies:**

```bash
# Install monitoring and config tools
source citadel_venv/bin/activate
pip install python-dotenv prometheus-client grafana-api
```

8. **Environment Setup:**

```bash
# Create activation script and save requirements
source citadel_venv/bin/activate
pip freeze > requirements.txt
chmod +x activate_citadel.sh
```

#### Validation Phase

```bash
# Verify all critical packages using citadel_venv
source citadel_venv/bin/activate
python -c "import fastapi, torch, transformers, psycopg2, requests; print('✅ All core dependencies successfully imported')"
python -c "import uvicorn, pydantic, httpx, aiohttp; print('✅ Web framework dependencies')"
python -c "import numpy, sqlalchemy, redis; print('✅ Data and database dependencies')"
python -c "import pytest, black, mypy; print('✅ Development dependencies')"
python -c "import prometheus_client; print('✅ Monitoring dependencies')"

# System health check
ollama list | grep -E "(deepseek-r1:32b|hadad/JARVIS|qwen:1.8b|deepcoder:14b|yi:34b-chat)"
curl -s http://localhost:11434/api/tags | jq '.'
systemctl status ollama
```

### Success Criteria

- [x] Python 3.12.x environment verified and optimized
- [x] All core AI/ML dependencies installed and importable
- [x] FastAPI, Uvicorn, and web framework dependencies ready
- [x] Database connectivity libraries (SQLAlchemy, psycopg2) installed
- [x] Monitoring and observability libraries available
- [x] Development and testing tools configured
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs

```text
Python 3.12.3
citadel_venv virtual environment created successfully
✅ All core dependencies successfully imported
✅ Web framework dependencies
✅ Data and database dependencies
✅ Development dependencies
✅ Monitoring dependencies
All packages imported successfully
Ollama service: active (running)
All 5 models operational
activate_citadel.sh script created and functional
requirements.txt generated with all dependencies
```

### Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Package installation failure | Low | Medium | Use pip3 install --user and verify versions |
| Dependency conflicts | Medium | Medium | Test imports after each installation group |
| System resource exhaustion | Low | Medium | Monitor disk space during installation |
| Service disruption | Low | Medium | Verify Ollama service throughout process |

### Rollback Procedures

**If Task Fails:**

1. Document package state: `pip3 list > package_state.log`
2. Verify core services: `systemctl status ollama`
3. Check model accessibility: `ollama list`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_1.2_Issues.md`

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_1.2_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 1.3 dependencies

### Troubleshooting Reference

**Common Issues:**

- **Package installation failure:** Check pip3 permissions and disk space
- **Import errors:** Verify package versions and dependencies
- **Permission issues:** Use --user flag for pip3 installations
- **Resource exhaustion:** Check `free -h` and `df -h`

**Debug Commands:**

```bash
# Package diagnostics
pip3 list | grep -E "(fastapi|torch|transformers|ollama)"
python3 -c "import sys; print(sys.path)"
which python3
pip3 show fastapi
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
"Task 1.2 completed successfully. Python 3.12 environment optimized with comprehensive AI/ML dependencies. All critical packages installed and verified: web frameworks, data science libraries, AI/ML tools, database connectivity, and monitoring capabilities. All models operational, system health verified, documentation updated. Ready for Task 1.3 - Ollama Installation and Configuration."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
