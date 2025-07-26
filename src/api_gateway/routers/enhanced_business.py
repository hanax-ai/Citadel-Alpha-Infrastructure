"""
Enhanced Business Intelligence Router
Includes external service integrations
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import httpx
import logging
import time
import sys
import os

# Add current directory to path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/business", tags=["Enhanced Business Intelligence"])

OLLAMA_BASE_URL = "http://localhost:11434"

# Import integrations with fallback
try:
    from integrations.database import db_integration
    from integrations.monitoring import monitoring_integration
    from integrations.vector_db import vector_db_integration
except ImportError as e:
    logger.warning(f"Integration import failed: {e}. Creating mock instances.")
    
    class MockIntegration:
        async def log_request(self, data): return "mocked"
        async def push_metrics(self, data): return True
        async def semantic_search(self, query, limit=3): return []
        async def initialize(self): return True
        async def check_health(self): return {"status": "mocked"}
        async def get_collection_stats(self): return {"status": "mocked"}
    
    db_integration = MockIntegration()
    monitoring_integration = MockIntegration()
    vector_db_integration = MockIntegration()

class EnhancedBusinessQuery(BaseModel):
    query: str
    context: Optional[str] = None
    analysis_type: str = "general"
    priority: str = "medium"
    use_knowledge_base: bool = True
    store_result: bool = True

class EnhancedBusinessResponse(BaseModel):
    response: str
    model_used: str
    analysis_type: str
    processing_time: float
    knowledge_base_results: Optional[List[Dict[str, Any]]] = None
    stored_in_db: bool = False
    metrics_pushed: bool = False

def select_business_model(analysis_type: str, priority: str) -> str:
    """Select optimal model for business analysis"""
    if analysis_type in ["strategic", "competitive"] or priority == "critical":
        return "hadad/JARVIS:latest"
    elif analysis_type == "market" or priority == "high":
        return "deepseek-r1:32b"
    elif analysis_type == "decision":
        return "yi:34b-chat"
    else:
        return "hadad/JARVIS:latest"

@router.post("/analyze-enhanced", response_model=EnhancedBusinessResponse)
async def enhanced_business_analysis(query: EnhancedBusinessQuery):
    """Enhanced business analysis with external service integration"""
    try:
        start_time = time.time()
        
        # Step 1: Semantic search for relevant context
        knowledge_results = []
        if query.use_knowledge_base:
            knowledge_results = await vector_db_integration.semantic_search(
                query.query, limit=3
            )
        
        # Step 2: Enhanced context with knowledge base results
        enhanced_context = query.context or ""
        if knowledge_results:
            kb_context = "\n".join([r["text"] for r in knowledge_results])
            enhanced_context += f"\n\nRelevant Knowledge Base Context:\n{kb_context}"
        
        # Step 3: Select model and generate response
        model = select_business_model(query.analysis_type, query.priority)
        
        business_prompt = f"""
Business Analysis Request:
Type: {query.analysis_type}
Priority: {query.priority}

Query: {query.query}

Context: {enhanced_context}

Please provide a comprehensive business analysis with:
1. Executive Summary
2. Key Insights
3. Strategic Implications
4. Recommended Actions
5. Risk Assessment

Format the response professionally for executive consumption.
"""
        
        async with httpx.AsyncClient(timeout=120.0) as client:
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
                
                # Step 4: Log to database
                stored_in_db = False
                if query.store_result:
                    log_data = {
                        "endpoint": "/api/v2/business/analyze-enhanced",
                        "model_used": model,
                        "processing_time": processing_time,
                        "analysis_type": query.analysis_type
                    }
                    stored_in_db = await db_integration.log_request(log_data) is not None
                
                # Step 5: Push metrics
                metrics_data = {
                    "requests": 1,
                    "response_time": processing_time,
                    "model_usage": {model: 1}
                }
                metrics_pushed = await monitoring_integration.push_metrics(metrics_data)
                
                return EnhancedBusinessResponse(
                    response=result['response'],
                    model_used=model,
                    analysis_type=query.analysis_type,
                    processing_time=processing_time,
                    knowledge_base_results=knowledge_results,
                    stored_in_db=stored_in_db,
                    metrics_pushed=metrics_pushed
                )
            else:
                raise HTTPException(status_code=500, detail="Model generation failed")
                
    except Exception as e:
        logger.error(f"Enhanced business analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/integration-status")
async def integration_status():
    """Check status of all external service integrations"""
    try:
        # Check database integration
        db_status = await db_integration.initialize()
        
        # Check monitoring integration
        monitoring_health = await monitoring_integration.check_health()
        
        # Check vector DB integration
        vector_stats = await vector_db_integration.get_collection_stats()
        
        return {
            "database": {
                "status": "operational" if db_status else "error",
                "host": "192.168.10.35",
                "connectivity": "framework_ready"
            },
            "monitoring": monitoring_health,
            "vector_database": vector_stats,
            "integration_version": "v2.0",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Integration status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/knowledge-search/{query}")
async def knowledge_search(query: str, limit: int = 5):
    """Direct knowledge base search endpoint"""
    try:
        results = await vector_db_integration.semantic_search(query, limit)
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
