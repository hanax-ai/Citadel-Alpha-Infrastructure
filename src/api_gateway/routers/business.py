"""
Business Intelligence API Router
Routes for executive decision support and strategic analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import httpx
import logging
import time

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
