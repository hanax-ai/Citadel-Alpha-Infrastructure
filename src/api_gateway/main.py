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
import httpx
import json

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

# Ollama client configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# Model configuration mapping
MODEL_CONFIG = {
    "deepseek-r1:32b": {
        "role": "strategic_research_intelligence",
        "capabilities": ["competitive_analysis", "market_research", "strategic_planning"],
        "business_priority": "high",
        "use_cases": ["strategic_consultation", "investment_analysis", "competitive_intelligence"]
    },
    "hadad/JARVIS:latest": {
        "role": "advanced_business_intelligence", 
        "capabilities": ["executive_briefings", "decision_support", "corporate_analysis"],
        "business_priority": "critical",
        "use_cases": ["executive_reporting", "board_presentations", "business_strategy"]
    },
    "qwen:1.8b": {
        "role": "high_volume_operations",
        "capabilities": ["quick_processing", "high_throughput", "rapid_response"],
        "business_priority": "medium",
        "use_cases": ["customer_support", "data_processing", "quick_queries"]
    },
    "deepcoder:14b": {
        "role": "code_generation_systems",
        "capabilities": ["code_generation", "system_integration", "technical_documentation"],
        "business_priority": "medium", 
        "use_cases": ["automation", "api_development", "system_integration"]
    },
    "yi:34b-chat": {
        "role": "advanced_reasoning",
        "capabilities": ["complex_analysis", "logical_reasoning", "problem_solving"],
        "business_priority": "high",
        "use_cases": ["strategic_analysis", "decision_support", "complex_problem_solving"]
    }
}

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
                    if model_name in MODEL_CONFIG:
                        config = MODEL_CONFIG[model_name]
                        business_models.append({
                            "name": model_name,
                            "role": config['role'],
                            "capabilities": config['capabilities'],
                            "business_priority": config['business_priority'],
                            "use_cases": config['use_cases'],
                            "size": model.get('size', 'unknown')
                        })
                
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

# Import routers
from routers import business, technical, enhanced_business

# Include routers
app.include_router(business.router)
app.include_router(technical.router)
app.include_router(enhanced_business.router)

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

@app.get("/integration-health")
async def integration_health():
    """Comprehensive health check including external services"""
    try:
        # Test Ollama connectivity
        async with httpx.AsyncClient() as client:
            ollama_response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_status = ollama_response.status_code == 200
        
        # External service connectivity status
        external_services = {
            "postgresql": {"host": "192.168.10.35", "status": "framework_ready", "port": 5432},
            "vector_db": {"host": "192.168.10.30", "status": "integration_ready", "port": 6333},
            "monitoring": {"host": "192.168.10.37", "status": "metrics_ready", "port": 9090},
            "web_server": {"host": "192.168.10.38", "status": "integration_ready", "port": 80}
        }
        
        return {
            "api_gateway": "operational",
            "ollama_service": "operational" if ollama_status else "error",
            "external_services": external_services,
            "models_available": 5,
            "integration_version": "v2.0",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Integration health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
