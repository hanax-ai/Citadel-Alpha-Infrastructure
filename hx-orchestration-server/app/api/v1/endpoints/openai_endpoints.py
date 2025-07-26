"""
OpenAI-Compatible API Endpoints
Enterprise gateway with intelligent routing and load balancing
"""

import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for OpenAI compatibility

class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: str = Field(..., description="Model to use")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens")
    temperature: Optional[float] = Field(default=0.7, description="Temperature")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")

class CompletionRequest(BaseModel):
    """OpenAI-compatible completion request"""
    model: str = Field(..., description="Model to use")
    prompt: str = Field(..., description="Prompt text")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens")
    temperature: Optional[float] = Field(default=0.7, description="Temperature")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")

class EmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request"""
    input: Union[str, List[str]] = Field(..., description="Text to embed")
    model: str = Field(default="nomic-embed-text", description="Embedding model")

class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    """Completion choice"""
    index: int
    message: Optional[ChatMessage] = None
    text: Optional[str] = None
    finish_reason: str

class ModelInfo(BaseModel):
    """Model information"""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "citadel-ai"

# Server configuration and load balancing
class ServerRegistry:
    """Enterprise server registry with health monitoring"""
    
    def __init__(self):
        self.servers = {
            "llm-01": {
                "url": "http://192.168.10.34:8002",
                "models": ["phi3", "mixtral", "openchat", "nous-hermes2"],
                "type": "llm",
                "healthy": True,
                "last_check": datetime.utcnow()
            },
            "llm-02": {
                "url": "http://192.168.10.28:8000", 
                "models": ["business-models", "phi3"],
                "type": "llm",
                "healthy": True,
                "last_check": datetime.utcnow()
            },
            "orchestration": {
                "url": "http://localhost:11434",
                "models": ["nomic-embed-text", "mxbai-embed-large", "bge-m3", "all-minilm"],
                "type": "embedding",
                "healthy": True,
                "last_check": datetime.utcnow()
            }
        }
    
    async def select_optimal_server(self, model: str, request_type: str = "completion") -> Dict[str, Any]:
        """Select optimal server based on model and load"""
        available_servers = []
        
        for server_id, server in self.servers.items():
            if model in server["models"] and server["healthy"]:
                if request_type == "embedding" and server["type"] == "embedding":
                    available_servers.append((server_id, server))
                elif request_type in ["completion", "chat"] and server["type"] == "llm":
                    available_servers.append((server_id, server))
        
        if not available_servers:
            # Fallback to any healthy LLM server for completion requests
            if request_type in ["completion", "chat"]:
                for server_id, server in self.servers.items():
                    if server["type"] == "llm" and server["healthy"]:
                        available_servers.append((server_id, server))
            
            if not available_servers:
                raise HTTPException(
                    status_code=503, 
                    detail=f"No healthy servers available for model '{model}'"
                )
        
        # Simple round-robin selection (could be enhanced with load metrics)
        selected_id, selected_server = available_servers[0]
        return {
            "id": selected_id,
            "url": selected_server["url"],
            "model": model
        }

    async def check_server_health(self, server_id: str, server: Dict[str, Any]) -> bool:
        """Check server health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if server["type"] == "embedding":
                    # Test Ollama health
                    response = await client.get(f"{server['url']}/api/tags")
                else:
                    # Test LLM server health
                    response = await client.get(f"{server['url']}/health")
                
                healthy = response.status_code == 200
                server["healthy"] = healthy
                server["last_check"] = datetime.utcnow()
                return healthy
        except Exception as e:
            logger.warning(f"Health check failed for {server_id}: {e}")
            server["healthy"] = False
            server["last_check"] = datetime.utcnow()
            return False

# Global server registry
server_registry = ServerRegistry()

def generate_id(prefix: str = "req") -> str:
    """Generate unique request ID"""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation)"""
    return len(text.split()) * 1.3

async def route_chat_completion(server: Dict[str, Any], request: ChatCompletionRequest) -> Dict[str, Any]:
    """Route chat completion to selected server"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Convert to server-specific format
            payload = {
                "model": request.model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
            
            response = await client.post(
                f"{server['url']}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        logger.error(f"Chat completion routing failed: {e}")
        raise HTTPException(status_code=502, detail=f"Upstream server error: {str(e)}")

async def route_completion(server: Dict[str, Any], request: CompletionRequest) -> Dict[str, Any]:
    """Route text completion to selected server"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
            
            response = await client.post(
                f"{server['url']}/v1/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        logger.error(f"Completion routing failed: {e}")
        raise HTTPException(status_code=502, detail=f"Upstream server error: {str(e)}")

async def generate_embeddings(server: Dict[str, Any], request: EmbeddingRequest) -> Dict[str, Any]:
    """Generate embeddings using Ollama"""
    try:
        texts = [request.input] if isinstance(request.input, str) else request.input
        embeddings = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                response = await client.post(
                    f"{server['url']}/api/embeddings",
                    json={
                        "model": request.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["embedding"])
        
        # Format as OpenAI-compatible response
        data = [
            {
                "object": "embedding",
                "embedding": emb,
                "index": i
            }
            for i, emb in enumerate(embeddings)
        ]
        
        total_tokens = sum(estimate_tokens(text) for text in texts)
        
        return {
            "object": "list",
            "data": data,
            "model": request.model,
            "usage": {
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=502, detail=f"Embedding server error: {str(e)}")

# OpenAI-compatible endpoints

@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions with enterprise routing"""
    try:
        # Select optimal server
        server = await server_registry.select_optimal_server(request.model, "chat")
        
        # Route request
        response = await route_chat_completion(server, request)
        
        # Ensure OpenAI-compatible format
        if "id" not in response:
            response["id"] = f"chatcmpl-{generate_id()}"
        if "object" not in response:
            response["object"] = "chat.completion"
        if "created" not in response:
            response["created"] = int(datetime.utcnow().timestamp())
        
        logger.info(f"Chat completion served by {server['id']} for model {request.model}")
        return response
        
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/completions")
async def completions(request: CompletionRequest):
    """OpenAI-compatible text completions with load balancing"""
    try:
        # Select optimal server
        server = await server_registry.select_optimal_server(request.model, "completion")
        
        # Route request
        response = await route_completion(server, request)
        
        # Ensure OpenAI-compatible format
        if "id" not in response:
            response["id"] = f"cmpl-{generate_id()}"
        if "object" not in response:
            response["object"] = "text_completion"
        if "created" not in response:
            response["created"] = int(datetime.utcnow().timestamp())
        
        logger.info(f"Completion served by {server['id']} for model {request.model}")
        return response
        
    except Exception as e:
        logger.error(f"Completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/models")
async def list_models():
    """Aggregated model metadata from all enterprise servers"""
    try:
        models = []
        
        for server_id, server in server_registry.servers.items():
            if server["healthy"]:
                for model in server["models"]:
                    models.append({
                        "id": model,
                        "object": "model",
                        "created": int(datetime.utcnow().timestamp()),
                        "owned_by": "citadel-ai",
                        "permission": [],
                        "root": model,
                        "parent": None,
                        "server": server_id
                    })
        
        return {
            "object": "list",
            "data": models
        }
        
    except Exception as e:
        logger.error(f"Model listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/embeddings")
async def create_embeddings(request: EmbeddingRequest):
    """Text embeddings with intelligent server selection"""
    try:
        # Select embedding server
        server = await server_registry.select_optimal_server(request.model, "embedding")
        
        # Generate embeddings
        response = await generate_embeddings(server, request)
        
        logger.info(f"Embeddings generated by {server['id']} for model {request.model}")
        return response
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health and monitoring endpoints

@router.get("/v1/health")
async def openai_health_check():
    """Health check for OpenAI endpoints"""
    try:
        healthy_servers = 0
        total_servers = len(server_registry.servers)
        
        # Check all servers
        for server_id, server in server_registry.servers.items():
            is_healthy = await server_registry.check_server_health(server_id, server)
            if is_healthy:
                healthy_servers += 1
        
        status = "healthy" if healthy_servers == total_servers else "degraded" if healthy_servers > 0 else "unhealthy"
        
        return {
            "status": status,
            "servers": {
                "total": total_servers,
                "healthy": healthy_servers,
                "unhealthy": total_servers - healthy_servers
            },
            "endpoints": [
                "/v1/chat/completions",
                "/v1/completions", 
                "/v1/models",
                "/v1/embeddings"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/v1/servers")
async def list_servers():
    """List all registered enterprise servers"""
    try:
        servers_info = {}
        
        for server_id, server in server_registry.servers.items():
            await server_registry.check_server_health(server_id, server)
            servers_info[server_id] = {
                "url": server["url"],
                "models": server["models"],
                "type": server["type"],
                "healthy": server["healthy"],
                "last_check": server["last_check"].isoformat()
            }
        
        return {
            "servers": servers_info,
            "total_servers": len(servers_info),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Server listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
