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

@router.post("/reasoning")
async def advanced_reasoning(query: dict):
    """Advanced reasoning using Yi model"""
    try:
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "yi:34b-chat",
                    "prompt": query.get('prompt', ''),
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    "response": result['response'],
                    "model_used": "yi:34b-chat",
                    "processing_time": processing_time,
                    "optimized_for": "advanced_reasoning"
                }
            else:
                raise HTTPException(status_code=500, detail="Reasoning failed")
                
    except Exception as e:
        logger.error(f"Advanced reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning failed: {str(e)}")
