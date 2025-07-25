# OpenWebUI Multi-Server Configuration Guide

## Current Gateway Status
**Note**: The Citadel API Gateway currently only connects to `localhost:11434`. To access models on both servers, you have two options:

## Option A: Direct Multi-Server Connection (Immediate Solution)

### Configuration for OpenWebUI `.env` file:
```bash
# Connect directly to both Ollama instances
OLLAMA_BASE_URLS=http://192.168.10.28:11434;http://192.168.10.29:11434

# Optional: Set custom port for OpenWebUI
WEBUI_PORT=8080

# Optional: Enable authentication
WEBUI_AUTH=False
```

### What this provides:
- **Load balancing**: OpenWebUI automatically distributes requests
- **Model aggregation**: All models from both servers appear in one interface
- **Failover**: If one server is down, requests go to the other
- **No gateway dependency**: Direct connection to Ollama instances

### Available Models (Verified):
**Both servers (192.168.10.28 and 192.168.10.29) have identical models:**
- **deepseek-r1:32b** (19 GB) - Advanced reasoning model
- **hadad/JARVIS:latest** (29 GB) - Large conversational AI
- **qwen:1.8b** (1.1 GB) - Lightweight efficient model
- **deepcoder:14b** (9.0 GB) - Code generation specialist
- **yi:34b-chat** (19 GB) - Large chat model

### Benefits of Load Balancing:
- **2x capacity**: Distribute requests across both servers
- **High availability**: Redundancy if one server fails
- **Better performance**: Parallel processing of multiple requests

## Option B: Enhanced Gateway with Load Balancing (Advanced Solution)

### What needs to be implemented:
1. **Multi-Backend Routing**: Route requests based on model or load balancing
2. **Health Checks**: Monitor both Ollama instances
3. **Model Discovery**: Auto-discover available models from both servers
4. **Request Distribution**: Smart load balancing algorithms

### Example enhanced routing logic:
```python
# Current gateway models (need updating)
VALID_MODELS = {
    "deepseek-r1", "jarvis", "qwen", "deepcoder", "yi-chat"
}

# Model-to-server mapping (both have same models, use load balancing)
OLLAMA_SERVERS = [
    "http://192.168.10.28:11434",
    "http://192.168.10.29:11434"
]

# Load balancing strategies:
# 1. Round-robin: Alternate between servers
# 2. Random: Random server selection
# 3. Health-based: Route to healthiest server
# 4. Model-specific: Pin certain models to specific servers
```

### Gateway Enhancement Required:
The current gateway only supports these models:
```python
# Current VALID_MODELS in gateway.py (needs update)
"phi3": "phi3:latest",
"openchat": "openchat:latest", 
"mixtral": "mixtral:latest",
"nous-hermes2-mixtral": "nous-hermes2-mixtral:latest",
"nomic-embed-text": "nomic-embed-text:latest"
```

**Should be updated to:**
```python
# Updated VALID_MODELS for actual deployed models
"deepseek-r1": "deepseek-r1:32b",
"jarvis": "hadad/JARVIS:latest",
"qwen": "qwen:1.8b",
"deepcoder": "deepcoder:14b",
"yi-chat": "yi:34b-chat"
```

## Recommendation

### For Immediate Access:
Use **Option A** - Configure OpenWebUI to connect directly to both servers using:
```bash
OLLAMA_BASE_URLS=http://192.168.10.28:11434;http://192.168.10.29:11434
```

### For Production Deployment:
Implement **Option B** - Enhanced Gateway with Load Balancing as the next advanced feature. This provides:
- Centralized request handling
- Advanced caching across all models
- Comprehensive monitoring and metrics
- Request authentication and rate limiting
- Unified API interface

## Checking Available Models

To see what models are available on each server:

### Server 192.168.10.28:
```bash
curl http://192.168.10.28:11434/api/tags
```

### Server 192.168.10.29:
```bash
curl http://192.168.10.29:11434/api/tags
```

This will show you exactly which models are installed on each server, helping you plan your configuration.
