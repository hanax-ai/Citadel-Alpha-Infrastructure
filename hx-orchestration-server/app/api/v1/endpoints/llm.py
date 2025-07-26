"""
LLM API Endpoints

OpenAI-compatible LLM endpoints for chat completions, text completions, and model management.
Provides enterprise routing, load balancing, and intelligent model selection.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal
from datetime import datetime
import asyncio
import httpx
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")


class CompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    prompt: Union[str, List[str]] = Field(..., description="Prompt(s) to complete")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")


class Choice(BaseModel):
    index: int = Field(..., description="Choice index")
    message: Optional[ChatMessage] = Field(None, description="Chat message (for chat completions)")
    text: Optional[str] = Field(None, description="Generated text (for completions)")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


class Usage(BaseModel):
    prompt_tokens: int = Field(..., description="Tokens in prompt")
    completion_tokens: int = Field(..., description="Tokens in completion")
    total_tokens: int = Field(..., description="Total tokens")


class CompletionResponse(BaseModel):
    id: str = Field(..., description="Completion ID")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[Choice] = Field(..., description="Completion choices")
    usage: Optional[Usage] = Field(None, description="Token usage")


class ModelInfo(BaseModel):
    id: str = Field(..., description="Model identifier")
    object: str = Field("model", description="Object type")
    created: int = Field(..., description="Model creation timestamp")
    owned_by: str = Field(..., description="Model owner")
    root: Optional[str] = Field(None, description="Root model")
    parent: Optional[str] = Field(None, description="Parent model")
    permission: Optional[List[Dict[str, Any]]] = Field(None, description="Model permissions")


class ModelsResponse(BaseModel):
    object: str = Field("list", description="Object type")
    data: List[ModelInfo] = Field(..., description="Available models")


# Enterprise server configuration
ENTERPRISE_SERVERS = {
    "llm_01": {
        "hostname": "192.168.10.34",
        "port": 8002,
        "role": "Primary AI Gateway",
        "models": ["phi3", "openchat", "mixtral", "nous-hermes2", "nomic-embed"],
        "specializations": ["general_purpose", "embeddings"]
    },
    "llm_02": {
        "hostname": "192.168.10.28", 
        "port": 8000,
        "role": "Business AI Gateway",
        "models": ["yi-34b", "deepcoder-14b", "imp-v1-3b", "deepseek-r1"],
        "specializations": ["business_intelligence", "code_generation"]
    }
}


class EnterpriseOrchestrator:
    """Enterprise LLM orchestration with service discovery and load balancing"""
    
    @staticmethod
    async def get_optimal_server(
        request: Request,
        model_name: str, 
        request_type: str = "chat"
    ) -> Optional[Dict[str, Any]]:
        """Get optimal server using service discovery and load balancing"""
        try:
            load_balancer = request.app.state.load_balancer
            
            # Prepare request context
            request_context = {
                "model": model_name,
                "request_type": request_type,
                "required_capability": "chat_completion" if request_type == "chat" else "text_completion"
            }
            
            # Use load balancer to select optimal server
            selected_server = await load_balancer.select_server(
                service_type="llm_server",
                request_context=request_context
            )
            
            return selected_server
            
        except Exception as e:
            logger.error(f"Failed to get optimal server: {e}")
            return None
    
    @staticmethod
    async def route_request_with_failover(
        request: Request,
        endpoint: str,
        server: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request with automatic failover"""
        try:
            # Attempt primary request
            result = await EnterpriseOrchestrator._execute_request(
                server, endpoint, request_data
            )
            
            # Mark request as successful
            await request.app.state.load_balancer.release_server(server, success=True)
            
            return result
            
        except Exception as primary_error:
            logger.warning(f"Primary server {server.get('id')} failed: {primary_error}")
            
            # Mark request as failed
            await request.app.state.load_balancer.release_server(server, success=False)
            
            # Attempt failover
            failover_manager = request.app.state.failover_manager
            backup_server = await failover_manager.handle_service_failure(
                failed_server=server,
                service_type="llm_server",
                request_context={"endpoint": endpoint}
            )
            
            if backup_server:
                try:
                    # Attempt request with backup server
                    result = await EnterpriseOrchestrator._execute_request(
                        backup_server, endpoint, request_data
                    )
                    
                    await request.app.state.load_balancer.release_server(backup_server, success=True)
                    return result
                    
                except Exception as backup_error:
                    await request.app.state.load_balancer.release_server(backup_server, success=False)
                    logger.error(f"Backup server {backup_server.get('id')} also failed: {backup_error}")
            
            # If both primary and backup failed, raise the original error
            raise HTTPException(
                status_code=503,
                detail=f"All available servers failed. Primary error: {str(primary_error)}"
            )
    
    @staticmethod
    async def _execute_request(
        server: Dict[str, Any],
        endpoint: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute request on specific server"""
        config = server["config"]
        url = f"http://{config['hostname']}:{config['port']}{endpoint}"
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=request_data)
            
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Server request failed: {response.status_code} - {response.text}")


@router.post("/chat/completions", response_model=CompletionResponse)
async def chat_completions(request_data: ChatCompletionRequest, request: Request):
    """
    OpenAI-compatible chat completions endpoint with enterprise routing
    """
    try:
        # Get optimal server using enterprise orchestration
        server = await EnterpriseOrchestrator.get_optimal_server(
            request, request_data.model, "chat"
        )
        
        if not server:
            raise HTTPException(
                status_code=503,
                detail="No healthy LLM servers available"
            )
        
        # Route request with automatic failover
        result = await EnterpriseOrchestrator.route_request_with_failover(
            request, "/v1/chat/completions", server, request_data.dict()
        )
        
        # Ensure response has required fields
        if "id" not in result:
            result["id"] = f"chatcmpl-{datetime.utcnow().isoformat()}"
        if "object" not in result:
            result["object"] = "chat.completion"
        if "created" not in result:
            result["created"] = int(datetime.utcnow().timestamp())
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat completion failed: {str(e)}"
        )


@router.post("/completions", response_model=CompletionResponse)
async def text_completions(request_data: CompletionRequest, request: Request):
    """
    OpenAI-compatible text completions endpoint with load balancing
    """
    try:
        # Get optimal server using enterprise orchestration
        server = await EnterpriseOrchestrator.get_optimal_server(
            request, request_data.model, "completion"
        )
        
        if not server:
            raise HTTPException(
                status_code=503,
                detail="No healthy LLM servers available"
            )
        
        # Route request with automatic failover
        result = await EnterpriseOrchestrator.route_request_with_failover(
            request, "/v1/completions", server, request_data.dict()
        )
        
        # Ensure response has required fields
        if "id" not in result:
            result["id"] = f"cmpl-{datetime.utcnow().isoformat()}"
        if "object" not in result:
            result["object"] = "text_completion"
        if "created" not in result:
            result["created"] = int(datetime.utcnow().timestamp())
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text completion error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Text completion failed: {str(e)}"
        )


@router.get("/models", response_model=ModelsResponse)
async def list_models(request: Request):
    """
    OpenAI-compatible models endpoint - aggregated model metadata from all servers
    """
    try:
        all_models = []
        
        # Get all healthy LLM servers from service discovery
        service_discovery = request.app.state.service_discovery
        healthy_servers = await service_discovery.registry.get_healthy_services("llm_server")
        
        for server in healthy_servers:
            try:
                config = server["config"]
                
                # Try to get models from server
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"http://{config['hostname']}:{config['port']}/v1/models"
                    )
                    
                if response.status_code == 200:
                    server_models = response.json()
                    if "data" in server_models:
                        # Add server info to each model
                        for model in server_models["data"]:
                            model["server"] = server["id"]
                            model["server_role"] = config.get("role", "unknown")
                        all_models.extend(server_models["data"])
                        
            except Exception as e:
                logger.warning(f"Failed to get models from {server['id']}: {e}")
                
                # Fallback to configured models
                for model_name in config.get("models", []):
                    all_models.append({
                        "id": model_name,
                        "object": "model",
                        "created": int(datetime.utcnow().timestamp()),
                        "owned_by": config.get("role", "unknown"),
                        "server": server["id"]
                    })
        
        # If no models from servers, provide default set
        if not all_models:
            default_models = [
                {
                    "id": "gpt-3.5-turbo",
                    "object": "model",
                    "created": int(datetime.utcnow().timestamp()),
                    "owned_by": "citadel-orchestration",
                    "server": "fallback"
                },
                {
                    "id": "text-davinci-003",
                    "object": "model", 
                    "created": int(datetime.utcnow().timestamp()),
                    "owned_by": "citadel-orchestration",
                    "server": "fallback"
                }
            ]
            all_models = default_models
        
        return {
            "object": "list",
            "data": all_models
        }
        
    except Exception as e:
        logger.error(f"Models listing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/models/{model_id}")
async def get_model(model_id: str, request: Request):
    """Get specific model information"""
    try:
        # Get all models and find the requested one
        models_response = await list_models(request)
        
        for model in models_response.data:
            if model.id == model_id:
                return model
                
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model: {str(e)}"
        )


@router.get("/health/llm")
async def llm_health(request: Request):
    """LLM orchestration health check"""
    try:
        service_discovery = request.app.state.service_discovery
        load_balancer = request.app.state.load_balancer
        failover_manager = request.app.state.failover_manager
        
        # Get service status
        service_status = await service_discovery.get_service_status()
        load_balancer_stats = await load_balancer.get_load_balancer_stats()
        failover_stats = await failover_manager.get_failover_stats()
        
        # Get healthy LLM servers
        healthy_llm_servers = await service_discovery.registry.get_healthy_services("llm_server")
        
        return {
            "status": "healthy" if healthy_llm_servers else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "service_discovery": service_status["service_discovery"],
            "enterprise_servers": {
                "total_llm_servers": len([s for s in service_discovery.registry.services.values() if s.get("type") == "llm_server"]),
                "healthy_llm_servers": len(healthy_llm_servers),
                "servers": [
                    {
                        "id": server["id"],
                        "status": server["health"]["status"],
                        "role": server["config"]["role"],
                        "response_time": server["health"].get("response_time", "unknown")
                    }
                    for server in healthy_llm_servers
                ]
            },
            "load_balancer": load_balancer_stats["load_balancer"],
            "failover": failover_stats,
            "capabilities": [
                "chat_completions",
                "text_completions", 
                "model_management",
                "enterprise_routing",
                "load_balancing",
                "automatic_failover",
                "service_discovery"
            ]
        }
        
    except Exception as e:
        logger.error(f"LLM health check error: {e}", exc_info=True)
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
