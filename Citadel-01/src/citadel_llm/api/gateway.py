from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse # Added StreamingResponse import
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from citadel_llm.utils.config import load_config, get_database_config
from citadel_llm.services.sql_service import sql_service
from citadel_llm.services.vector_service import VectorService
from citadel_llm.services.redis_service import redis_service
from citadel_llm.api.middleware.logging import LoggingMiddleware
from citadel_llm.api.middleware.metrics import PrometheusMetricsMiddleware, set_metrics_middleware, get_metrics_middleware
from citadel_llm.api.routes import management, health, webhooks, metrics
from citadel_llm.models.request_models import ChatCompletionRequest, GenerateRequest, EmbeddingRequest
import httpx
import json
import logging
import hashlib
import time
import asyncio
from typing import AsyncGenerator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Configure basic logging for initial startup messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = 3600  # 1 hour cache TTL for embeddings
CACHE_PREFIX = "citadel:embeddings:"

async def get_cache_key(model: str, prompt: str) -> str:
    """Generate a cache key for embeddings based on model and prompt."""
    combined = f"{model}:{prompt}"
    return CACHE_PREFIX + hashlib.md5(combined.encode()).hexdigest()

async def get_cached_embedding(cache_key: str):
    """Get cached embedding from Redis."""
    try:
        if redis_service._client:
            cached_data = await redis_service._client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Failed to get cached embedding: {e}")
    return None

async def set_cached_embedding(cache_key: str, embedding_data: dict):
    """Set embedding data in Redis cache."""
    try:
        if redis_service._client:
            serialized_data = json.dumps(embedding_data)
            await redis_service._client.setex(cache_key, CACHE_TTL, serialized_data)
            logger.info(f"Cached embedding with key: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to cache embedding: {e}")

# Global config variable
app_config = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global app_config
    try:
        # 1. Load Configuration
        logger.info("Loading application configuration...")
        app_config = load_config()
        logger.info("Configuration loaded successfully.")

        # 2. Initialize SQL Service
        db_config = get_database_config(app_config)
        
        if not db_config or not db_config.get('password'):
            logger.error("SQL database configuration or password missing. SQL service will not be initialized.")
        else:
            logger.info("Initializing SQL Service...")
            await sql_service.initialize()
            logger.info("SQL Service initialized. Creating tables if they don't exist...")
            await sql_service.create_tables()
            logger.info("SQL database tables ensured.")

            # Test SQL health check
            health_result = await sql_service.health_check()
            if isinstance(health_result, dict) and health_result.get('status') == 'healthy':
                logger.info("SQL Service health check passed.")
            else:
                logger.error("SQL Service health check failed after initialization!")

        # 3. Initialize Vector Service
        integration_config = app_config.get('integration', {})
        vector_db_config = integration_config.get('vector_db', {})
        qdrant_api_key = app_config.get(vector_db_config.get('api_key_secret_name', 'QDRANT_API_KEY'), None)
        ollama_url = "http://localhost:11434"  # Default Ollama URL
        
        if not vector_db_config:
            logger.error("Vector database configuration missing. Vector service will not be initialized.")
        else:
            logger.info("Initializing Vector Service...")
            try:
                await VectorService.initialize(vector_db_config, ollama_url, qdrant_api_key)
                logger.info("Vector Service initialized.")

                # Test Vector health check
                if not await VectorService.health_check():
                    logger.error("Vector Service health check failed after initialization!")
                else:
                    logger.info("Vector Service health check passed.")
            except Exception as e:
                logger.error(f"Failed to initialize Vector Service: {e}")
                # Continue startup even if vector service fails

        # 4. Initialize Redis Service
        logger.info("Initializing Redis Service...")
        try:
            await redis_service.initialize(app_config)
            
            # Test Redis health check
            redis_health = await redis_service.health_check()
            if redis_health.get('status') == 'healthy':
                logger.info("Redis Service health check passed.")
            else:
                logger.warning(f"Redis Service health check failed: {redis_health}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis Service: {e}")
            # Continue startup even if Redis service fails

    except Exception as e:
        logger.critical(f"Failed during application startup: {e}", exc_info=True)
        # Re-raise to prevent app from starting in a bad state
        raise

    yield # Application runs

    # Clean up resources on shutdown
    logger.info("Shutting down application. Closing services...")
    try:
        await VectorService.close()
    except:
        pass
    try:
        await redis_service.close()
    except:
        pass
    await sql_service.close()
    logger.info("Application shutdown complete.")

app = FastAPI(
    title="Citadel LLM API Gateway",
    description="OpenAI-compatible API Gateway for Ollama LLM Services",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware with default config (will be populated during lifespan)
app.add_middleware(LoggingMiddleware, config={})

# Add metrics middleware for Prometheus integration
app.add_middleware(PrometheusMetricsMiddleware, config={})

# Register management routes
app.include_router(management.router, prefix="/management", tags=["Management"])

# Register health routes
app.include_router(health.router, prefix="/health", tags=["Health"])

# Register webhook routes for external monitoring integration
app.include_router(webhooks.webhooks_router, prefix="", tags=["Webhooks"])

# Register metrics routes for Prometheus scraping
app.include_router(metrics.metrics_router, prefix="", tags=["Metrics"])

VALID_MODELS = {
    "phi3",
    "openchat",
    "mixtral",
    "nous-hermes2-mixtral",
    "nomic-embed-text"
}

# Map user-friendly model names to actual Ollama model names
MODEL_MAPPING = {
    "phi3": "phi3:latest",
    "openchat": "openchat:latest", 
    "mixtral": "mixtral:latest",
    "nous-hermes2-mixtral": "nous-hermes2-mixtral:latest",
    "nomic-embed-text": "nomic-embed-text:latest"
}

OLLAMA_API_URL = "http://localhost:11434/api/generate" # Default for completions
OLLAMA_CHAT_API_URL = "http://localhost:11434/api/chat" # Default for chat completions
OLLAMA_EMBEDDINGS_API_URL = "http://localhost:11434/api/embeddings" # Default for embeddings

# Agent-specific streaming configuration
AGENT_STREAMING_CONFIG = {
    "voice": {
        "chunk_size": 1,  # Single tokens for real-time voice
        "timeout": 30.0,  # Voice interactions should be faster
        "buffer_size": 50  # Small buffer for low latency
    },
    "copilot": {
        "chunk_size": 5,  # Small chunks for IDE integration
        "timeout": 60.0,  # Code generation can take longer
        "buffer_size": 200  # Medium buffer for code context
    },
    "gui": {
        "chunk_size": 10,  # Larger chunks for UI display
        "timeout": 120.0,  # UI can handle longer responses
        "buffer_size": 500  # Larger buffer for better UI experience
    }
}

# Helper to route requests based on endpoint (completions vs chat vs embeddings)
def get_ollama_url(request_path: str):
    if "/chat/completions" in request_path:
        return OLLAMA_CHAT_API_URL
    elif "/embeddings" in request_path:
        return OLLAMA_EMBEDDINGS_API_URL
    return OLLAMA_API_URL

# Helper to map user model names to Ollama model names using routing config
def get_ollama_model_name(user_model: str) -> str:
    """
    Enhanced model mapping using routing.yaml configuration.
    Falls back to hardcoded MODEL_MAPPING if routing config not available.
    """
    # Try to get model aliases from routing config
    routing_config_path = "/opt/citadel/config/services/api-gateway/routing.yaml"
    try:
        import yaml
        import os
        if os.path.exists(routing_config_path):
            with open(routing_config_path, 'r') as f:
                routing_config = yaml.safe_load(f)
                model_aliases = routing_config.get('model_aliases', {})
                if user_model in model_aliases:
                    logger.info(f"Routing alias '{user_model}' to actual model '{model_aliases[user_model]}'")
                    return model_aliases[user_model]
    except Exception as e:
        logger.warning(f"Could not load routing config, falling back to hardcoded mapping: {e}")
    
    # Fallback to hardcoded mapping
    mapped_model = MODEL_MAPPING.get(user_model, user_model)
    if mapped_model != user_model:
        logger.info(f"Hardcoded mapping '{user_model}' to '{mapped_model}'")
    return mapped_model


async def stream_ollama_response(
    ollama_response: httpx.Response,
    agent_type: str,
    conversation_id: str = None,
    request_path: str = ""
) -> AsyncGenerator[str, None]:
    """
    Stream Ollama response with agent-specific optimizations.
    Aggregates chunks for database logging while streaming to client.
    """
    config = AGENT_STREAMING_CONFIG.get(agent_type, AGENT_STREAMING_CONFIG["gui"])
    chunk_buffer = []
    token_count = 0
    complete_content = ""
    
    try:
        async for chunk in ollama_response.aiter_lines():
            if chunk:
                try:
                    # Parse the streaming response line
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]  # Remove "data: " prefix
                    
                    if chunk.strip() == "[DONE]":
                        break
                        
                    chunk_data = json.loads(chunk)
                    
                    # Extract content based on endpoint type
                    content = ""
                    if "/chat/completions" in request_path:
                        content = chunk_data.get("message", {}).get("content", "")
                    else:
                        content = chunk_data.get("response", "")
                    
                    if content:
                        complete_content += content
                        chunk_buffer.append(content)
                        token_count += 1
                        
                        # Send chunks based on agent-specific configuration
                        if len(chunk_buffer) >= config["chunk_size"]:
                            combined_chunk = "".join(chunk_buffer)
                            
                            # Format as Server-Sent Event
                            sse_data = {
                                "choices": [{
                                    "delta": {"content": combined_chunk},
                                    "index": 0,
                                    "finish_reason": None
                                }]
                            }
                            
                            yield f"data: {json.dumps(sse_data)}\n\n"
                            chunk_buffer = []
                            
                            # Add small delay for voice agents to prevent overwhelming
                            if agent_type == "voice":
                                await asyncio.sleep(0.01)
                                
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse streaming chunk: {chunk}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error in streaming response for {agent_type}: {e}")
        
    # Send any remaining buffered content
    if chunk_buffer:
        combined_chunk = "".join(chunk_buffer)
        sse_data = {
            "choices": [{
                "delta": {"content": combined_chunk},
                "index": 0,
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(sse_data)}\n\n"
    
    # Send completion marker
    completion_data = {
        "choices": [{
            "delta": {},
            "index": 0,
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(completion_data)}\n\n"
    yield "data: [DONE]\n\n"
    
    # Log complete response to database for audit trail
    if conversation_id and complete_content:
        try:
            await sql_service.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=complete_content,
                metadata={
                    "agent_type": agent_type,
                    "streaming": True,
                    "token_count": token_count,
                    "chunk_count": len(chunk_buffer)
                }
            )
            logger.info(f"Logged streaming response for conversation {conversation_id} ({agent_type} agent)")
        except Exception as e:
            logger.warning(f"Failed to log streaming response to database: {e}")


async def _handle_agent_streaming_proxy(
    request_path: str,
    model: str,
    ollama_model: str,
    body: dict,
    ollama_target_url: str,
    request: Request,
    agent_type: str
):
    """
    Shared implementation for agent-specific streaming proxies.
    Maintains enterprise logging while enabling real-time streaming.
    """
    config = AGENT_STREAMING_CONFIG[agent_type]
    
    # Log request to database
    conversation_id = None
    request_metadata = {
        "endpoint": request_path,
        "model": model,
        "ollama_model": ollama_model,
        "agent_type": agent_type,
        "streaming": True,
        "ollama_url": ollama_target_url,
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    try:
        conversation_id = await sql_service.save_conversation(
            user_id="anonymous",
            model_name=model,
            title=f"{agent_type.title()} agent session with {model}",
            metadata=request_metadata
        )
        logger.info(f"Created streaming conversation {conversation_id} for {agent_type} agent with model {model}")
    except Exception as e:
        logger.warning(f"Failed to log conversation to database: {e}")
    
    logger.info(f"Forwarding streaming request to {agent_type} agent: {model} (mapped to {ollama_model}) at {ollama_target_url}")
    
    try:
        # Get metrics middleware for recording
        metrics = get_metrics_middleware()
        request_start_time = time.time()
        
        # Forward streaming request to Ollama
        async with httpx.AsyncClient(timeout=config["timeout"]) as client:
            async with client.stream("POST", ollama_target_url, json=body) as ollama_response:
                ollama_response.raise_for_status()
                
                # Record metrics
                if metrics:
                    metrics.record_ollama_request(
                        model=model,
                        endpoint_type=f'streaming_{agent_type}',
                        duration=time.time() - request_start_time,
                        status_code=ollama_response.status_code
                    )
                
                # Return streaming response
                return StreamingResponse(
                    stream_ollama_response(
                        ollama_response, 
                        agent_type, 
                        conversation_id, 
                        request_path
                    ),
                    media_type="text/plain",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Agent-Type": agent_type,
                        "X-Conversation-ID": str(conversation_id) if conversation_id else "unknown"
                    }
                )

    except httpx.TimeoutException as e:
        logger.error(f"Timeout connecting to Ollama for {agent_type} agent with model {model}: {e}")
        raise HTTPException(status_code=504, detail=f"Gateway Timeout: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error connecting to Ollama for {agent_type} agent with model {model}: {e}")
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")
    except Exception as e:
        logger.exception(f"Unhandled error in {agent_type} agent streaming proxy")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus exposition format.
    """
    try:
        metrics_data = generate_latest()
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST,
            headers={"Content-Type": CONTENT_TYPE_LATEST}
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate metrics")


@app.post("/v1/chat/completions")
async def proxy_chat_to_ollama(request: Request, chat_request: ChatCompletionRequest):
    """
    Proxy OpenAI-compatible chat completions requests to Ollama.
    Intentionally disables streaming and logs conversations to database.
    """
    request_path = str(request.url.path)
    
    # Validate model exists
    if chat_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model: {chat_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(chat_request.model)
    
    # Convert to dictionary for Ollama request
    body = chat_request.model_dump()
    body["model"] = ollama_model  # Update with mapped model name

    # Force streaming to false (critical design decision)
    original_stream = chat_request.stream
    body["stream"] = False  # Always force stream=false
    if original_stream:
        logger.warning(f"Streaming requested for {chat_request.model}, but API Gateway is configured for non-streaming. Setting stream=false.")

    # Get Ollama URL based on endpoint
    ollama_target_url = get_ollama_url(request_path)
    
    # Debug: Log the exact request we're sending to Ollama
    logger.info(f"Sending to Ollama: {json.dumps(body)[:200]}...")
    
    # Delegate to shared implementation
    return await _handle_ollama_proxy(
        request_path=request_path,
        model=chat_request.model,
        ollama_model=ollama_model,
        original_stream=original_stream,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request
    )


@app.post("/v1/completions") 
async def proxy_completions_to_ollama(request: Request, generate_request: GenerateRequest):
    """
    Proxy OpenAI-compatible completions requests to Ollama.
    Intentionally disables streaming and logs conversations to database.
    """
    request_path = str(request.url.path)
    
    # Validate model exists
    if generate_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model: {generate_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(generate_request.model)
    
    # Convert to dictionary for Ollama request
    body = generate_request.model_dump()
    body["model"] = ollama_model  # Update with mapped model name

    # Force streaming to false (critical design decision)
    original_stream = generate_request.stream
    body["stream"] = False  # Always force stream=false
    if original_stream:
        logger.warning(f"Streaming requested for {generate_request.model}, but API Gateway is configured for non-streaming. Setting stream=false.")

    # Get Ollama URL based on endpoint
    ollama_target_url = get_ollama_url(request_path)
    
    # Debug: Log the exact request we're sending to Ollama
    logger.info(f"Sending to Ollama: {json.dumps(body)[:200]}...")
    
    # Delegate to shared implementation
    return await _handle_ollama_proxy(
        request_path=request_path,
        model=generate_request.model,
        ollama_model=ollama_model,
        original_stream=original_stream,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request
    )


async def _handle_ollama_proxy(
    request_path: str,
    model: str,
    ollama_model: str,
    original_stream: bool,
    body: dict,
    ollama_target_url: str,
    request: Request
):
    """
    Shared implementation for proxying requests to Ollama.
    Handles conversation logging and response processing.
    """
    
    # Log request to database
    conversation_id = None
    request_metadata = {
        "endpoint": request_path,
        "model": model,
        "ollama_model": ollama_model,  # Log both user and ollama model names
        "original_stream_requested": original_stream,
        "ollama_url": ollama_target_url,
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    try:
        conversation_id = await sql_service.save_conversation(
            user_id="anonymous",  # Default user ID for API gateway
            model_name=model,
            title=f"Chat session with {model}",
            metadata=request_metadata
        )
        logger.info(f"Created conversation {conversation_id} for model {model}")
    except Exception as e:
        logger.warning(f"Failed to log conversation to database: {e}")
    
    logger.info(f"Forwarding non-streaming request to model: {model} (mapped to {ollama_model}) at {ollama_target_url}")
    
    try:
        # Forward request to Ollama
        async with httpx.AsyncClient(timeout=3600.0) as client:
            ollama_response = await client.post(ollama_target_url, json=body)
            
            # Get raw response text for debugging
            response_text = ollama_response.text
            logger.info(f"Raw Ollama response length: {len(response_text)}")
            logger.info(f"Raw Ollama response: {response_text[:500]}...")
            
            # Parse JSON more robustly
            try:
                # Handle potential multiple JSON objects or extra whitespace
                response_text = response_text.strip()
                
                # Since we force stream=false, we should expect a single JSON response
                # But check if there are multiple lines just in case
                if '\n' in response_text and not body.get("stream", False):
                    # Multiple lines when we expected single response - take the last complete JSON
                    lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                    if lines:
                        # Try to parse the last non-empty line for streaming responses
                        response_data = json.loads(lines[-1])
                    else:
                        response_data = json.loads(response_text)
                else:
                    # Single JSON response (expected for stream=false)
                    response_data = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parsing error. Raw response: {response_text}")
                raise HTTPException(status_code=500, detail=f"Invalid JSON from Ollama: {json_err}")

            # Debug: Log the parsed response
            logger.info(f"Parsed Ollama response: {json.dumps(response_data)[:300]}...")
            
            logger.info(f"Model {model} response status: {ollama_response.status_code}")
            
            # Log response to database
            if conversation_id:
                try:
                    response_metadata = {
                        "status_code": ollama_response.status_code,
                        "response_size": len(str(response_data)),
                        "ollama_headers": dict(ollama_response.headers)
                    }
                    
                    # Extract content based on endpoint type
                    content = ""
                    if "/chat/completions" in request_path:
                        content = response_data.get("message", {}).get("content", "")
                    else:
                        content = response_data.get("response", "")
                    
                    await sql_service.save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=content,
                        metadata=response_metadata
                    )
                    logger.info(f"Logged response for conversation {conversation_id}")
                except Exception as e:
                    logger.warning(f"Failed to log response to database: {e}")
            
            # Return standard JSON response
            return JSONResponse(status_code=ollama_response.status_code, content=response_data)

    except httpx.TimeoutException as e:
        logger.error(f"Timeout connecting to Ollama for model {model}: {e}")
        raise HTTPException(status_code=504, detail=f"Gateway Timeout: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error connecting to Ollama for model {model}: {e}")
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")
    except Exception as e:
        logger.exception("Unhandled error in API proxy")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# ============================================================================
# AGENT-SPECIFIC STREAMING ENDPOINTS
# ============================================================================

@app.post("/v1/voice/chat/completions")
async def proxy_voice_chat_to_ollama(request: Request, chat_request: ChatCompletionRequest):
    """
    Voice agent optimized streaming endpoint.
    - Single token chunks for real-time speech synthesis
    - Low latency configuration (30s timeout)
    - Optimized for voice interaction patterns
    """
    request_path = str(request.url.path)
    
    # Validate model exists
    if chat_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model for voice agent: {chat_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(chat_request.model)
    
    # Convert to dictionary for Ollama request
    body = chat_request.model_dump()
    body["model"] = ollama_model
    body["stream"] = True  # Force streaming for voice agents
    
    # Get Ollama URL
    ollama_target_url = get_ollama_url(request_path)
    
    logger.info(f"Voice agent streaming request: {json.dumps(body)[:200]}...")
    
    return await _handle_agent_streaming_proxy(
        request_path=request_path,
        model=chat_request.model,
        ollama_model=ollama_model,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request,
        agent_type="voice"
    )


@app.post("/v1/copilot/completions")
async def proxy_copilot_completions_to_ollama(request: Request, generate_request: GenerateRequest):
    """
    Copilot agent optimized streaming endpoint.
    - Small chunks (5 tokens) for IDE integration
    - Medium latency tolerance (60s timeout)
    - Optimized for code completion patterns
    """
    request_path = str(request.url.path)
    
    # Validate model exists
    if generate_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model for copilot agent: {generate_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(generate_request.model)
    
    # Convert to dictionary for Ollama request
    body = generate_request.model_dump()
    body["model"] = ollama_model
    body["stream"] = True  # Force streaming for copilot agents
    
    # Get Ollama URL
    ollama_target_url = get_ollama_url(request_path)
    
    logger.info(f"Copilot agent streaming request: {json.dumps(body)[:200]}...")
    
    return await _handle_agent_streaming_proxy(
        request_path=request_path,
        model=generate_request.model,
        ollama_model=ollama_model,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request,
        agent_type="copilot"
    )


@app.post("/v1/gui/chat/completions")
async def proxy_gui_chat_to_ollama(request: Request, chat_request: ChatCompletionRequest):
    """
    GUI agent optimized streaming endpoint.
    - Larger chunks (10 tokens) for UI display efficiency
    - Higher latency tolerance (120s timeout)
    - Optimized for chat interface patterns
    """
    request_path = str(request.url.path)
    
    # Validate model exists
    if chat_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model for GUI agent: {chat_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(chat_request.model)
    
    # Convert to dictionary for Ollama request
    body = chat_request.model_dump()
    body["model"] = ollama_model
    body["stream"] = True  # Force streaming for GUI agents
    
    # Get Ollama URL
    ollama_target_url = get_ollama_url(request_path)
    
    logger.info(f"GUI agent streaming request: {json.dumps(body)[:200]}...")
    
    return await _handle_agent_streaming_proxy(
        request_path=request_path,
        model=chat_request.model,
        ollama_model=ollama_model,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request,
        agent_type="gui"
    )


@app.post("/v1/agents/stream")
async def proxy_generic_agent_streaming(
    request: Request, 
    chat_request: ChatCompletionRequest,
    agent_type: str = "gui"
):
    """
    Generic agent streaming endpoint with configurable agent type.
    Allows dynamic agent type specification via query parameter.
    
    Usage: POST /v1/agents/stream?agent_type=voice
    """
    if agent_type not in AGENT_STREAMING_CONFIG:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown agent type: {agent_type}. Supported: {list(AGENT_STREAMING_CONFIG.keys())}"
        )
    
    request_path = str(request.url.path)
    
    # Validate model exists
    if chat_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown model for {agent_type} agent: {chat_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(chat_request.model)
    
    # Convert to dictionary for Ollama request
    body = chat_request.model_dump()
    body["model"] = ollama_model
    body["stream"] = True  # Force streaming for all agents
    
    # Get Ollama URL
    ollama_target_url = get_ollama_url("/v1/chat/completions")
    
    logger.info(f"Generic {agent_type} agent streaming request: {json.dumps(body)[:200]}...")
    
    return await _handle_agent_streaming_proxy(
        request_path=request_path,
        model=chat_request.model,
        ollama_model=ollama_model,
        body=body,
        ollama_target_url=ollama_target_url,
        request=request,
        agent_type=agent_type
    )


# ============================================================================
# EXISTING NON-STREAMING ENDPOINTS (Enterprise/Audit focused)
# ============================================================================


@app.post("/api/embeddings")
async def proxy_embeddings_to_ollama(request: Request, embedding_request: EmbeddingRequest):
    """
    Proxy embeddings requests to Ollama with caching.
    Provides caching and logging for embedding requests.
    Embeddings are cached for 1 hour as they are deterministic for the same input.
    """
    # Validate model exists
    if embedding_request.model not in VALID_MODELS:
        logger.warning(f"Rejected unknown embeddings model: {embedding_request.model}")
        raise HTTPException(status_code=400, detail="Unknown or missing model")

    # Map to actual Ollama model name
    ollama_model = get_ollama_model_name(embedding_request.model)
    
    # Generate cache key
    cache_key = await get_cache_key(ollama_model, embedding_request.prompt)
    
    # Try to get cached result first
    cache_start_time = time.time()
    cached_result = await get_cached_embedding(cache_key)
    cache_duration = time.time() - cache_start_time
    
    # Get metrics middleware for recording
    metrics = get_metrics_middleware()
    
    if cached_result:
        logger.info(f"Serving cached embedding for model: {embedding_request.model}")
        
        # Record cache hit metrics
        if metrics:
            metrics.record_cache_hit('embeddings')
            metrics.record_cache_operation('get', cache_duration, 'hit')
        
        return JSONResponse(status_code=200, content=cached_result)
    
    # Record cache miss
    if metrics:
        metrics.record_cache_miss('embeddings')
        metrics.record_cache_operation('get', cache_duration, 'miss')
    
    # Convert to dictionary for Ollama request
    body = embedding_request.model_dump()
    body["model"] = ollama_model

    # Get Ollama URL for embeddings
    ollama_target_url = get_ollama_url("/api/embeddings")
    
    logger.info(f"Forwarding embeddings request to model: {embedding_request.model} (mapped to {ollama_model}) at {ollama_target_url}")
    
    try:
        # Forward request to Ollama
        ollama_start_time = time.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            ollama_response = await client.post(ollama_target_url, json=body)
            ollama_response.raise_for_status()
            
            # Record Ollama request metrics
            ollama_duration = time.time() - ollama_start_time
            if metrics:
                metrics.record_ollama_request(
                    model=embedding_request.model,
                    endpoint_type='embeddings',
                    duration=ollama_duration,
                    status_code=ollama_response.status_code
                )
            
            # Parse response
            response_data = ollama_response.json()
            
            logger.info(f"Embeddings model {embedding_request.model} response status: {ollama_response.status_code}")
            
            # Cache the result for future requests
            cache_start_time = time.time()
            await set_cached_embedding(cache_key, response_data)
            cache_duration = time.time() - cache_start_time
            
            # Record cache set operation
            if metrics:
                metrics.record_cache_operation('set', cache_duration, 'success')
            
            # Return the embeddings response
            return JSONResponse(status_code=ollama_response.status_code, content=response_data)

    except httpx.TimeoutException as e:
        logger.error(f"Timeout connecting to Ollama for embeddings model {embedding_request.model}: {e}")
        raise HTTPException(status_code=504, detail=f"Gateway Timeout: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error connecting to Ollama for embeddings model {embedding_request.model}: {e}")
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")
    except Exception as e:
        logger.exception("Unhandled error in embeddings proxy")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
