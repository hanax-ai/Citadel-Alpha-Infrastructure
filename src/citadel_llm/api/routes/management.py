import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional

from citadel_llm.utils.config import load_config # To get app_config if needed (though app.state is better)

# In a real application, you might use an auth dependency here
# async def get_current_active_user():
#     # Dummy dependency for R&D environment
#     return "agent0"

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_ollama_base_url():
    """Helper to get Ollama base URL from config."""
    # It's better to pass app_config via Depends or app.state for FastAPI
    # For simplicity in this example, we'll reload it, but be aware of performance impact.
    # In a production app, the lifespan function should store it in app.state.
    current_config = load_config() 
    ollama_config = current_config.get('ollama', {})
    host = ollama_config.get('service', {}).get('host', 'localhost')
    port = ollama_config.get('service', {}).get('port', 11434)
    return f"http://{host}:{port}"

@router.get("/models/list", summary="List available Ollama models")
async def list_ollama_models():
    """
    Lists all models available to the Ollama service.
    Corresponds to `ollama list` command or GET /api/tags.
    """
    ollama_url = await get_ollama_base_url()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            models_data = response.json()
            return {"models": models_data.get("models", [])}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama for model list: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama service: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama returned error for model list: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama service error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error listing Ollama models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while listing models.")

@router.post("/models/pull", summary="Pull (download) an Ollama model")
async def pull_ollama_model(model_name: str, stream: bool = False):
    """
    Pulls a specified Ollama model.
    Corresponds to `ollama pull <model_name>`.
    """
    ollama_url = await get_ollama_base_url()
    payload = {"name": model_name, "stream": stream} # stream=True for long-running pull messages
    try:
        async with httpx.AsyncClient(timeout=None) as client: # Timeout=None for long pulls
            response = await client.post(f"{ollama_url}/api/pull", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama for model pull: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama service: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama returned error for model pull: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama service error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error pulling Ollama model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while pulling model.")

@router.post("/models/delete", summary="Delete an Ollama model")
async def delete_ollama_model(model_name: str):
    """
    Deletes a specified Ollama model.
    Corresponds to `ollama rm <model_name>`.
    """
    ollama_url = await get_ollama_base_url()
    payload = {"name": model_name}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.delete(f"{ollama_url}/api/delete", json=payload)
            response.raise_for_status()
            # Ollama delete typically returns an empty 200 OK or 204 No Content
            return {"status": "success", "message": f"Model '{model_name}' deleted."}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama for model delete: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama service: {e}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
        logger.error(f"Ollama returned error for model delete: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama service error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error deleting Ollama model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while deleting model.")

@router.get("/models/{model_name}/info", summary="Get details for a specific Ollama model")
async def get_ollama_model_info(model_name: str):
    """
    Gets detailed information for a specific Ollama model.
    Corresponds to `ollama show <model_name>`.
    """
    ollama_url = await get_ollama_base_url()
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{ollama_url}/api/show", json={"name": model_name})
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama for model info: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama service: {e}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
        logger.error(f"Ollama returned error for model info: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama service error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error getting Ollama model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching model info.")

@router.get("/system/ollama-status", summary="Get Ollama service status")
async def get_ollama_status():
    """
    Checks if the Ollama service is reachable and responsive.
    """
    ollama_url = await get_ollama_base_url()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            # Use a lightweight endpoint to check connectivity
            response = await client.get(f"{ollama_url}/api/tags") 
            response.raise_for_status()
            return {"status": "ok", "message": "Ollama service is up and responsive."}
    except httpx.RequestError as e:
        logger.error(f"Ollama service is not reachable: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Ollama service is down or unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama service returned non-200 status during status check: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ollama service responded with error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error checking Ollama status.")
