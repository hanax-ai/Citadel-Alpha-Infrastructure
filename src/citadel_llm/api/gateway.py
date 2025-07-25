from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from citadel_llm.utils.config import load_config, get_database_config
from citadel_llm.services.sql_service import sql_service
from citadel_llm.services.vector_service import VectorService
from citadel_llm.api.middleware.logging import LoggingMiddleware
from citadel_llm.api.routes import health
from citadel_llm.models.request_models import ChatCompletionRequest, GenerateRequest, EmbeddingRequest
from citadel_llm.services.vector_service import VectorService
from citadel_llm.api.middleware.logging import LoggingMiddleware
from citadel_llm.api.routes import health
from citadel_llm.models.request_models import ChatCompletionRequest, GenerateRequest, EmbeddingRequest
import httpx
import json
import logging
import hashlib
import time
import asyncio
import redis.asyncio as redis

# Configure basic logging for initial startup messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = 3600  # 1 hour cache TTL for embeddings
CACHE_PREFIX = "citadel:embeddings:"

# Agent-specific streaming configuration
AGENT_CONFIGS = {
    "voice": {
        "chunk_size": 1,  # Single token for real-time speech
        "timeout": 30,    # Voice interactions should be quick
        "buffer_size": 50,
        "delay_ms": 10,   # 0.01s delays between chunks
    },
    "copilot": {
        "chunk_size": 5,  # 5-token chunks for smooth code appearance
        "timeout": 60,    # Complex code generation
        "buffer_size": 200,
        "delay_ms": 100,  # 0.1s delays for IDE rendering
    },
    "gui": {
        "chunk_size": 10, # 10-token chunks for efficient UI rendering
        "timeout": 120,   # Comprehensive responses
        "buffer_size": 500,
        "delay_ms": 200,  # 0.2s delays for chat bubbles
    }
}

# Global Redis client - will be initialized in lifespan
redis_client = None

async def get_cache_key(model: str, prompt: str) -> str:
    """Generate a cache key for embeddings based on model and prompt."""
    combined = f"{model}:{prompt}"
    return CACHE_PREFIX + hashlib.md5(combined.encode()).hexdigest()

async def get_cached_embedding(cache_key: str):
    """Get cached embedding from Redis."""
    try:
        if redis_client:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Failed to get cached embedding: {e}")
    return None

async def set_cached_embedding(cache_key: str, embedding_data: dict):
    """Set embedding data in Redis cache."""
    try:
        if redis_client:
            serialized_data = json.dumps(embedding_data)
            await redis_client.setex(cache_key, CACHE_TTL, serialized_data)
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

        # 4. Initialize Redis Cache (LLM-01 proven implementation)
        global redis_client
        try:
            redis_config = app_config.get('redis', {})
            redis_host = redis_config.get('host', 'localhost')
            redis_port = redis_config.get('port', 6379)
            redis_db = redis_config.get('cache_db', 1)  # Use separate DB for cache like LLM-01
            
            logger.info(f"Initializing Redis cache connection to {redis_host}:{redis_port}/{redis_db}...")
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            
            # Test Redis connection
            await redis_client.ping()
            logger.info("Redis cache connection established successfully.")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}. Caching will be disabled.")
            redis_client = None

        # Ensure Ollama model for embeddings is pulled if not already present
        # This is handled by manual model management for now
        pass

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
    await sql_service.close()
    logger.info("Application shutdown complete.")

# Initialize config here for middleware to pick it up on startup
initial_config = load_config() # Load config once for middleware init

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

# Register health routes
app.include_router(health.router, prefix="/health", tags=["Health"])

VALID_MODELS = {
    "yi-34b",
    "deepcoder", 
    "qwen",
    "jarvis",
    "deepseek"
}

# Map user-friendly model names to actual Ollama model names - Server-02 Business Models
MODEL_MAPPING = {
    "yi-34b": "yi:34b-chat",          # 19 GB - Business reasoning
    "deepcoder": "deepcoder:14b",     # 9.0 GB - Code generation  
    "qwen": "qwen:1.8b",              # 1.1 GB - High-volume operations
    "jarvis": "hadad/JARVIS:latest",  # 29 GB - Business assistant
    "deepseek": "deepseek-r1:32b"     # 19 GB - Research analysis
}

OLLAMA_API_URL = "http://localhost:11434/api/generate" # Default for completions
OLLAMA_CHAT_API_URL = "http://localhost:11434/api/chat" # Default for chat completions
OLLAMA_EMBEDDINGS_API_URL = "http://localhost:11434/api/embeddings" # LLM-01 proven embeddings endpoint

# Helper to route requests based on endpoint (completions vs chat vs embeddings)
def get_ollama_url(request_path: str):
    if "/chat/completions" in request_path:
        return OLLAMA_CHAT_API_URL
    elif "/embeddings" in request_path:
        return OLLAMA_EMBEDDINGS_API_URL
    return OLLAMA_API_URL

# Helper to map user model names to Ollama model names
def get_ollama_model_name(user_model: str) -> str:
    """
    Enhanced model mapping for Server-02 business models.
    """
    # Use hardcoded mapping for Server-02 business models
    mapped_model = MODEL_MAPPING.get(user_model, user_model)
    if mapped_model != user_model:
        logger.info(f"Hardcoded mapping '{user_model}' to '{mapped_model}'")
    return mapped_model


# API endpoint utilities
def get_model_mapping(user_model: str) -> str:
    """Map user-friendly model names to actual Ollama model names"""
    mapped_model = MODEL_MAPPING.get(user_model, user_model)
    if mapped_model != user_model:
        logger.info(f"Hardcoded mapping '{user_model}' to '{mapped_model}'")
    return mapped_model


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
    
    if cached_result:
        logger.info(f"Serving cached embedding for model: {embedding_request.model}")
        return JSONResponse(status_code=200, content=cached_result)
    
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
            
            # Parse response
            response_data = ollama_response.json()
            
            logger.info(f"Embeddings model {embedding_request.model} response status: {ollama_response.status_code}")
            
            # Cache the result for future requests
            cache_start_time = time.time()
            await set_cached_embedding(cache_key, response_data)
            cache_duration = time.time() - cache_start_time
            
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


# Agent-Specific Streaming Helper Functions
async def stream_ollama_response(
    agent_type: str,
    model: str,
    messages: list,
    max_tokens: int = 150,
    conversation_id: str = None
):
    """
    Stream response from Ollama with agent-specific optimizations.
    """
    config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["gui"])
    ollama_model = get_ollama_model_name(model)
    
    # Convert messages to dictionary format for Ollama
    ollama_messages = []
    for msg in messages:
        if hasattr(msg, 'model_dump'):
            # Pydantic model
            ollama_messages.append(msg.model_dump())
        elif isinstance(msg, dict):
            ollama_messages.append(msg)
        else:
            # Assume it has role and content attributes
            ollama_messages.append({"role": msg.role, "content": msg.content})
    
    # Prepare request body for Ollama
    body = {
        "model": ollama_model,
        "messages": ollama_messages,
        "stream": True,
        "max_tokens": max_tokens
    }
    
    logger.info(f"Starting {agent_type} streaming for model: {model} (mapped to {ollama_model})")
    
    complete_content = ""
    chunk_count = 0
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=config["timeout"]) as client:
            async with client.stream("POST", OLLAMA_CHAT_API_URL, json=body) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="Ollama streaming failed")
                
                # Buffer for chunking
                token_buffer = []
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            # Parse Ollama streaming response
                            if line.startswith("data: "):
                                line = line[6:]  # Remove "data: " prefix
                            
                            if line.strip() == "[DONE]":
                                # Send any remaining tokens in buffer
                                if token_buffer:
                                    buffered_content = " ".join(token_buffer)
                                    complete_content += buffered_content
                                    
                                    yield f"data: {json.dumps({'choices': [{'delta': {'content': buffered_content}, 'index': 0, 'finish_reason': None}]})}\n\n"
                                    
                                    # Agent-specific delay
                                    await asyncio.sleep(config["delay_ms"] / 1000.0)
                                
                                # Send completion signal
                                yield f"data: {json.dumps({'choices': [{'delta': {}, 'index': 0, 'finish_reason': 'stop'}]})}\n\n"
                                yield "data: [DONE]\n\n"
                                break
                            
                            # Parse JSON response
                            chunk_data = json.loads(line)
                            
                            if "message" in chunk_data and "content" in chunk_data["message"]:
                                content = chunk_data["message"]["content"]
                                if content:
                                    # Add to token buffer
                                    token_buffer.append(content)
                                    complete_content += content
                                    
                                    # Send chunk when buffer reaches configured size
                                    if len(token_buffer) >= config["chunk_size"]:
                                        buffered_content = " ".join(token_buffer)
                                        
                                        # Send OpenAI-compatible streaming response
                                        streaming_chunk = {
                                            "choices": [{
                                                "delta": {"content": buffered_content},
                                                "index": 0,
                                                "finish_reason": None
                                            }]
                                        }
                                        
                                        yield f"data: {json.dumps(streaming_chunk)}\n\n"
                                        chunk_count += 1
                                        
                                        # Clear buffer and add agent-specific delay
                                        token_buffer = []
                                        await asyncio.sleep(config["delay_ms"] / 1000.0)
                                        
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
                        except Exception as e:
                            logger.warning(f"Error processing stream chunk: {e}")
                            continue
    
    except Exception as e:
        logger.error(f"Streaming error for {agent_type}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return
    
    # Log complete response to database
    if conversation_id and complete_content:
        try:
            duration_ms = int((time.time() - start_time) * 1000)
            await sql_service.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=complete_content,
                tokens_used=len(complete_content.split()),
                model_name=model,
                metadata={
                    "agent_type": agent_type,
                    "streaming": True,
                    "chunk_count": chunk_count,
                    "duration_ms": duration_ms,
                    "chunk_size": config["chunk_size"]
                }
            )
            logger.info(f"Logged {agent_type} streaming response: {len(complete_content)} chars, {chunk_count} chunks")
        except Exception as e:
            logger.warning(f"Failed to log streaming response: {e}")


# Agent-Specific Streaming Endpoints

@app.post("/v1/voice/chat/completions")
async def voice_chat_streaming(request: Request, chat_request: ChatCompletionRequest):
    """
    Voice agent optimized streaming endpoint.
    Single token streaming for real-time speech synthesis.
    """
    # Validate model
    if chat_request.model not in VALID_MODELS:
        raise HTTPException(status_code=400, detail="Unknown or missing model")
    
    # Create conversation for logging
    conversation_id = None
    try:
        conversation_id = await sql_service.save_conversation(
            user_id="voice_agent",
            model_name=chat_request.model,
            title="Voice Agent Session",
            metadata={
                "agent_type": "voice",
                "endpoint": "/v1/voice/chat/completions",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}")
    
    # Return streaming response
    return StreamingResponse(
        stream_ollama_response(
            agent_type="voice",
            model=chat_request.model,
            messages=chat_request.messages,
            max_tokens=getattr(chat_request, 'max_tokens', 50),
            conversation_id=conversation_id
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@app.post("/v1/copilot/completions")
async def copilot_streaming(request: Request, chat_request: ChatCompletionRequest):
    """
    Copilot agent optimized streaming endpoint.
    5-token chunks for smooth code completion in IDEs.
    """
    # Validate model
    if chat_request.model not in VALID_MODELS:
        raise HTTPException(status_code=400, detail="Unknown or missing model")
    
    # Create conversation for logging
    conversation_id = None
    try:
        conversation_id = await sql_service.save_conversation(
            user_id="copilot_agent",
            model_name=chat_request.model,
            title="Copilot Code Session",
            metadata={
                "agent_type": "copilot",
                "endpoint": "/v1/copilot/completions",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}")
    
    # Return streaming response
    return StreamingResponse(
        stream_ollama_response(
            agent_type="copilot",
            model=chat_request.model,
            messages=chat_request.messages,
            max_tokens=getattr(chat_request, 'max_tokens', 150),
            conversation_id=conversation_id
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@app.post("/v1/gui/chat/completions")
async def gui_chat_streaming(request: Request, chat_request: ChatCompletionRequest):
    """
    GUI agent optimized streaming endpoint.
    10-token chunks for efficient chat interface rendering.
    """
    # Validate model
    if chat_request.model not in VALID_MODELS:
        raise HTTPException(status_code=400, detail="Unknown or missing model")
    
    # Create conversation for logging
    conversation_id = None
    try:
        conversation_id = await sql_service.save_conversation(
            user_id="gui_agent",
            model_name=chat_request.model,
            title="GUI Chat Session",
            metadata={
                "agent_type": "gui",
                "endpoint": "/v1/gui/chat/completions",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}")
    
    # Return streaming response
    return StreamingResponse(
        stream_ollama_response(
            agent_type="gui",
            model=chat_request.model,
            messages=chat_request.messages,
            max_tokens=getattr(chat_request, 'max_tokens', 200),
            conversation_id=conversation_id
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@app.post("/v1/agents/stream")
async def generic_agent_streaming(
    request: Request, 
    chat_request: ChatCompletionRequest,
    agent_type: str = Query(default="gui", description="Agent type: voice, copilot, or gui")
):
    """
    Generic agent streaming endpoint with configurable agent type.
    Flexible development endpoint for custom agent types.
    """
    # Validate agent type
    if agent_type not in AGENT_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
    
    # Validate model
    if chat_request.model not in VALID_MODELS:
        raise HTTPException(status_code=400, detail="Unknown or missing model")
    
    # Create conversation for logging
    conversation_id = None
    try:
        conversation_id = await sql_service.save_conversation(
            user_id=f"{agent_type}_agent",
            model_name=chat_request.model,
            title=f"{agent_type.title()} Agent Session",
            metadata={
                "agent_type": agent_type,
                "endpoint": "/v1/agents/stream",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}")
    
    # Return streaming response
    return StreamingResponse(
        stream_ollama_response(
            agent_type=agent_type,
            model=chat_request.model,
            messages=chat_request.messages,
            max_tokens=getattr(chat_request, 'max_tokens', 200),
            conversation_id=conversation_id
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
