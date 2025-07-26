"""
Embeddings API Endpoints

OpenAI-compatible embedding endpoints for text processing.
Enhanced with RAG pipeline integration and vector storage.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Any, Dict
import time
import asyncio
from datetime import datetime
import logging

from app.core.embeddings.rag_pipeline import rag_pipeline
from app.services.vector_service import qdrant_service
from app.utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

router = APIRouter()


class EmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request"""
    input: Union[str, List[str]] = Field(..., description="Text to embed")
    model: str = Field(default="nomic-embed-text", description="Model to use")
    encoding_format: str = Field(default="float", description="Encoding format")
    user: Optional[str] = Field(default=None, description="User identifier")


class EmbeddingUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    total_tokens: int


class EmbeddingData(BaseModel):
    """Single embedding result"""
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    """OpenAI-compatible embedding response"""
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: EmbeddingUsage


class AsyncEmbeddingResponse(BaseModel):
    """Async embedding response"""
    task_id: str
    status: str
    estimated_completion: Optional[datetime]


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    background_tasks: BackgroundTasks
):
    """
    Create embeddings for the given input
    
    OpenAI-compatible endpoint that generates embeddings using RAG pipeline.
    Supports both single strings and batches of text with optional vector storage.
    
    Args:
        request: Embedding request with text and model
        background_tasks: FastAPI background tasks
        
    Returns:
        EmbeddingResponse: OpenAI-compatible embedding response
    """
    start_time = time.time()
    
    try:
        # Validate and normalize input
        texts = [request.input] if isinstance(request.input, str) else request.input
        
        # Generate embeddings using RAG pipeline
        embeddings = await rag_pipeline.generate_embeddings(
            text=texts,
            model=request.model
        )
        
        # Build response data
        data = [
            EmbeddingData(embedding=emb, index=i)
            for i, emb in enumerate(embeddings)
        ]
        
        # Calculate usage (approximate)
        total_tokens = sum(len(text.split()) for text in texts)
        usage = EmbeddingUsage(
            prompt_tokens=total_tokens,
            total_tokens=total_tokens
        )
        
        # Log performance
        processing_time = time.time() - start_time
        logger.info(f"Generated {len(embeddings)} embeddings in {processing_time:.2f}s using {request.model}")
        
        return EmbeddingResponse(
            data=data,
            model=request.model,
            usage=usage
        )
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@router.post("/embeddings/async", response_model=AsyncEmbeddingResponse)
async def create_embeddings_async(request: EmbeddingRequest):
    """
    Create embeddings asynchronously for large batches
    
    For large text batches, this endpoint queues the work and returns
    a task ID for later retrieval.
    
    Args:
        request: Embedding request with text and model
        
    Returns:
        AsyncEmbeddingResponse: Task information for async processing
    """
    try:
        texts = [request.input] if isinstance(request.input, str) else request.input
        validate_input_length(texts)
        
        # Queue async task
        task = process_embeddings_async.delay(
            texts=texts,
            model=request.model,
            user=request.user
        )
        
        # Estimate completion time (rough calculation)
        estimated_seconds = len(texts) * 0.1  # 100ms per text estimate
        estimated_completion = datetime.utcnow().replace(
            second=int(datetime.utcnow().second + estimated_seconds)
        )
        
        return AsyncEmbeddingResponse(
            task_id=task.id,
            status="queued",
            estimated_completion=estimated_completion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue embedding task: {str(e)}"
        )


@router.get("/embeddings/task/{task_id}")
async def get_embedding_task_status(task_id: str):
    """
    Get status of async embedding task
    
    Args:
        task_id: Task identifier from async request
        
    Returns:
        dict: Task status and result if completed
    """
    try:
        from celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            return {"status": "pending", "task_id": task_id}
        elif task.state == "PROGRESS":
            return {
                "status": "processing",
                "task_id": task_id,
                "progress": task.info.get("current", 0),
                "total": task.info.get("total", 0)
            }
        elif task.state == "SUCCESS":
            return {
                "status": "completed",
                "task_id": task_id,
                "result": task.result
            }
        else:
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(task.info)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )
