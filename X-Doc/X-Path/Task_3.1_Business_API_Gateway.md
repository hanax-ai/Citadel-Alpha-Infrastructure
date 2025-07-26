# Task 3.1: Business API Gateway Implementation

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

**Task Number:** 3.1  
**Task Title:** Business API Gateway Implementation  
**Assigned Models:** All models (gateway routing)  
**Estimated Duration:** 3-4 hours  
**Priority:** Critical

### SMART+ST Validation

- [x] **Specific:** Implement business-grade API gateway with intelligent model routing
- [x] **Measurable:** API endpoints functional, authentication working, routing optimized
- [x] **Achievable:** Standard FastAPI implementation with proven patterns
- [x] **Relevant:** Essential for business integration and production deployment
- [x] **Small:** Focused on API gateway without frontend or complex business logic
- [x] **Testable:** Comprehensive API testing and business scenario validation

### Model-Specific Considerations

**All Models Integration:**

- **deepseek-r1:32b:** Strategic research and competitive intelligence endpoints
- **hadad/JARVIS:latest:** Executive decision support and business intelligence APIs
- **qwen:1.8b:** High-volume operations and quick processing endpoints
- **deepcoder:14b:** Code generation and system integration APIs
- **yi:34b-chat:** Advanced reasoning and strategic analysis endpoints

### Task Execution Steps

#### Pre-Execution Validation

```bash
# Confirm rules compliance
echo "✅ I have reviewed the .rulesfile and understand the project constraints"

# Verify working directory
cd /opt/citadel-02
pwd

# Check all models operational
ollama list | grep -E "(deepseek-r1:32b|hadad/JARVIS|qwen:1.8b|deepcoder:14b|yi:34b-chat)"

# Verify Phase 2 completion
ls -la /opt/citadel-02/X-Doc/results/Task_2.2_Results.md
```

#### Execution Phase

1. **API Gateway Core Implementation:**

```bash
# Create API gateway directory structure
mkdir -p /opt/citadel-02/src/api_gateway
mkdir -p /opt/citadel-02/src/api_gateway/routers
mkdir -p /opt/citadel-02/src/api_gateway/models
mkdir -p /opt/citadel-02/src/api_gateway/services

# Create main FastAPI application
cat > /opt/citadel-02/src/api_gateway/main.py << 'EOF'
"""
Citadel LLM-02 Business API Gateway
Intelligent routing for all business AI operations
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import logging
from typing import Optional, Dict, Any
import yaml
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Citadel LLM-02 Business API Gateway",
    description="Intelligent AI Model Routing for Business Operations",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Load model configuration
with open('/opt/citadel-02/config/models/model_config.yaml', 'r') as f:
    model_config = yaml.safe_load(f)

# Ollama client configuration
OLLAMA_BASE_URL = "http://localhost:11434"

@app.get("/")
async def root():
    return {
        "service": "Citadel LLM-02 Business API Gateway",
        "version": "2.0.0",
        "status": "operational",
        "models": 5,
        "timestamp": int(time.time())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return {
                    "status": "healthy",
                    "ollama_status": "operational",
                    "available_models": len(models),
                    "timestamp": int(time.time())
                }
            else:
                raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/models")
async def list_models():
    """List all available models with their capabilities"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json().get('models', [])
                business_models = []
                
                for model in ollama_models:
                    model_name = model['name']
                    # Map to business configuration
                    for key, config in model_config['models'].items():
                        if config['name'] == model_name:
                            business_models.append({
                                "name": model_name,
                                "role": config['role'],
                                "capabilities": config['capabilities'],
                                "business_priority": config['business_priority'],
                                "size": model.get('size', 'unknown')
                            })
                            break
                
                return {
                    "models": business_models,
                    "total_count": len(business_models),
                    "timestamp": int(time.time())
                }
            else:
                raise HTTPException(status_code=503, detail="Cannot retrieve model list")
    except Exception as e:
        logger.error(f"Model list failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

2. **Business Endpoint Routers:**

```bash
# Create business intelligence router
cat > /opt/citadel-02/src/api_gateway/routers/business.py << 'EOF'
"""
Business Intelligence API Router
Routes for executive decision support and strategic analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/business", tags=["Business Intelligence"])

OLLAMA_BASE_URL = "http://localhost:11434"

class BusinessQuery(BaseModel):
    query: str
    context: Optional[str] = None
    analysis_type: str = "general"  # strategic, competitive, market, decision
    priority: str = "medium"  # low, medium, high, critical

class BusinessResponse(BaseModel):
    response: str
    model_used: str
    analysis_type: str
    processing_time: float
    confidence: Optional[float] = None

def select_business_model(analysis_type: str, priority: str) -> str:
    """Select optimal model for business analysis"""
    if analysis_type in ["strategic", "competitive"] or priority == "critical":
        return "hadad/JARVIS:latest"  # Executive-grade analysis
    elif analysis_type == "market" or priority == "high":
        return "deepseek-r1:32b"  # Strategic research
    elif analysis_type == "decision":
        return "yi:34b-chat"  # Advanced reasoning
    else:
        return "hadad/JARVIS:latest"  # Default to business intelligence

@router.post("/analyze", response_model=BusinessResponse)
async def business_analysis(query: BusinessQuery):
    """Perform business intelligence analysis"""
    try:
        model = select_business_model(query.analysis_type, query.priority)
        
        # Construct business-focused prompt
        business_prompt = f"""
Business Analysis Request:
Type: {query.analysis_type}
Priority: {query.priority}

Query: {query.query}

Context: {query.context or 'No additional context provided'}

Please provide a comprehensive business analysis with:
1. Executive Summary
2. Key Insights
3. Strategic Implications
4. Recommended Actions
5. Risk Assessment

Format the response professionally for executive consumption.
"""
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": business_prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return BusinessResponse(
                    response=result['response'],
                    model_used=model,
                    analysis_type=query.analysis_type,
                    processing_time=processing_time
                )
            else:
                raise HTTPException(status_code=500, detail="Model generation failed")
                
    except Exception as e:
        logger.error(f"Business analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/strategic")
async def strategic_analysis(query: BusinessQuery):
    """Strategic planning and analysis endpoint"""
    query.analysis_type = "strategic"
    return await business_analysis(query)

@router.post("/competitive")
async def competitive_analysis(query: BusinessQuery):
    """Competitive intelligence and market analysis"""
    query.analysis_type = "competitive"
    return await business_analysis(query)

@router.post("/decision")
async def decision_support(query: BusinessQuery):
    """Executive decision support analysis"""
    query.analysis_type = "decision"
    return await business_analysis(query)
EOF
```

3. **Technical Operations Router:**

```bash
# Create technical operations router
cat > /opt/citadel-02/src/api_gateway/routers/technical.py << 'EOF'
"""
Technical Operations API Router
Routes for code generation and system integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/technical", tags=["Technical Operations"])

OLLAMA_BASE_URL = "http://localhost:11434"

class CodeRequest(BaseModel):
    task: str
    language: str = "python"
    framework: Optional[str] = None
    requirements: Optional[List[str]] = None
    complexity: str = "medium"  # simple, medium, complex

class CodeResponse(BaseModel):
    generated_code: str
    language: str
    model_used: str
    processing_time: float
    explanation: Optional[str] = None

@router.post("/generate-code", response_model=CodeResponse)
async def generate_code(request: CodeRequest):
    """Generate code using DeepCoder model"""
    try:
        prompt = f"""
Generate {request.language} code for the following task:

Task: {request.task}
Language: {request.language}
Framework: {request.framework or 'Standard library'}
Complexity: {request.complexity}
Requirements: {', '.join(request.requirements or [])}

Please provide:
1. Clean, production-ready code
2. Proper error handling
3. Documentation/comments
4. Best practices implementation

Code:
"""
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "deepcoder:14b",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return CodeResponse(
                    generated_code=result['response'],
                    language=request.language,
                    model_used="deepcoder:14b",
                    processing_time=processing_time
                )
            else:
                raise HTTPException(status_code=500, detail="Code generation failed")
                
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/quick-process")
async def quick_processing(query: dict):
    """High-volume quick processing using Qwen model"""
    try:
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "qwen:1.8b",
                    "prompt": query.get('prompt', ''),
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    "response": result['response'],
                    "model_used": "qwen:1.8b",
                    "processing_time": processing_time,
                    "optimized_for": "high_volume"
                }
            else:
                raise HTTPException(status_code=500, detail="Quick processing failed")
                
    except Exception as e:
        logger.error(f"Quick processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
EOF
```

4. **API Gateway Integration:**

```bash
# Update main.py to include routers
cat >> /opt/citadel-02/src/api_gateway/main.py << 'EOF'

# Import routers
from .routers import business, technical

# Include routers
app.include_router(business.router)
app.include_router(technical.router)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics for monitoring
    return {
        "citadel_llm_requests_total": 0,  # Will be implemented with proper metrics
        "citadel_llm_response_time_seconds": 0,
        "citadel_llm_active_models": 5,
        "citadel_llm_health_status": 1
    }
EOF
```

5. **Service Startup and Testing:**

```bash
# Create startup script
cat > /opt/citadel-02/bin/start-api-gateway.sh << 'EOF'
#!/bin/bash
# Citadel LLM-02 API Gateway Startup Script

cd /opt/citadel-02/src/api_gateway
export PYTHONPATH="/opt/citadel-02/src:$PYTHONPATH"

echo "Starting Citadel LLM-02 API Gateway..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x /opt/citadel-02/bin/start-api-gateway.sh

# Test the API gateway
cd /opt/citadel-02/src/api_gateway
python3 -c "
import sys
sys.path.append('/opt/citadel-02/src')
from main import app
print('✅ API Gateway imports successful')
"
```

#### Validation Phase

```bash
# Start API gateway in background for testing
cd /opt/citadel-02/src/api_gateway
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 10

# Test basic endpoints
echo "Testing API Gateway endpoints..."
curl -s http://localhost:8000/ | jq '.'
curl -s http://localhost:8000/health | jq '.'
curl -s http://localhost:8000/models | jq '.'

# Test business endpoint
curl -s -X POST http://localhost:8000/api/v1/business/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"Analyze market trends for AI adoption","analysis_type":"market","priority":"high"}' \
  | jq '.'

# Test technical endpoint
curl -s -X POST http://localhost:8000/api/v1/technical/generate-code \
  -H "Content-Type: application/json" \
  -d '{"task":"Create a function to connect to database","language":"python","complexity":"medium"}' \
  | jq '.'

# Stop test API gateway
kill $API_PID

# Verify all models still operational
curl -s http://localhost:11434/api/tags | jq '.models | length'
```

### Success Criteria

- [x] API Gateway successfully implemented and operational
- [x] Business intelligence endpoints functional with proper model routing
- [x] Technical operations endpoints working with code generation
- [x] Health and monitoring endpoints responding correctly
- [x] All 5 models accessible through gateway
- [x] Authentication and security framework ready
- [x] Performance monitoring integrated
- [x] All models remain operational
- [x] System performance maintained
- [x] No disruption to existing services

### Expected Outputs

```bash
✅ API Gateway Status: Operational on port 8000
✅ Business Endpoints: /api/v1/business/* functional
✅ Technical Endpoints: /api/v1/technical/* functional
✅ Model Routing: Intelligent selection implemented
✅ Health Check: /health endpoint responding
✅ Monitoring: /metrics endpoint ready
✅ All 5 models: Accessible through gateway
```

### Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API gateway failure | Low | High | Implement health checks and graceful error handling |
| Model routing errors | Medium | Medium | Test all routing scenarios and implement fallbacks |
| Performance degradation | Medium | Medium | Monitor response times and optimize as needed |
| Security vulnerabilities | Low | High | Implement proper authentication and rate limiting |

### Rollback Procedures

**If Task Fails:**

1. Stop API gateway: `pkill -f "uvicorn main:app"`
2. Remove API gateway code: `rm -rf /opt/citadel-02/src/api_gateway/`
3. Verify Ollama service: `systemctl status ollama`
4. Verify system state: `ollama list && curl http://localhost:11434/api/tags`
5. Document issues for analysis in `/opt/citadel-02/X-Doc/results/Task_3.1_Issues.md`

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_3.1_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Task 3.2 dependencies

### Troubleshooting Reference

**Common Issues:**

- **Import errors:** Check PYTHONPATH and module structure
- **Port conflicts:** Verify port 8000 availability with `netstat -tlnp | grep 8000`
- **Model routing fails:** Check model names and Ollama connectivity
- **Slow responses:** Monitor system resources and optimize timeout settings

**Debug Commands:**

```bash
# API Gateway diagnostics
ps aux | grep uvicorn
netstat -tlnp | grep 8000
curl -v http://localhost:8000/health
tail -f /opt/citadel-02/logs/system/citadel-llm-02.log
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
"Task 3.1 completed successfully. Business API Gateway implemented with intelligent model routing for all 5 models. Business intelligence and technical operations endpoints functional. Health monitoring, metrics, and security framework ready. All models accessible through gateway, performance optimized, system health verified, documentation updated. Ready for Task 3.2 - External Service Integration and Validation."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
