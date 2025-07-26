# Ollama Configuration for Citadel LLM System
# Location: /opt/citadel-02/config/ollama_config.md

## Server Configuration

**Service:** ollama-02.service (optimized for business operations)  
**Version:** 0.9.6  
**Status:** Active and operational  
**Port:** 11434  
**Host:** 0.0.0.0 (all interfaces)  

## Environment Variables

- `OLLAMA_MODELS=/mnt/active_llm_models/.ollama` - Custom models directory
- `OLLAMA_HOST=0.0.0.0:11434` - Network binding
- `OLLAMA_ORIGINS=*` - CORS configuration for web access
- `OLLAMA_NUM_PARALLEL=2` - Parallel request handling
- `OLLAMA_MAX_LOADED_MODELS=4` - Memory optimization
- `OLLAMA_FLASH_ATTENTION=1` - Performance optimization
- `CUDA_VISIBLE_DEVICES=0,1` - GPU acceleration
- `OLLAMA_DEBUG=1` - Enhanced logging

## Model Inventory

### Production Models (74GB total)

1. **deepseek-r1:32b** (19GB)
   - Role: Strategic Research & Intelligence
   - Quantization: Q4_K_M
   - Parameters: 32.8B
   - Use cases: Market analysis, competitive intelligence

2. **hadad/JARVIS:latest** (29GB)  
   - Role: Advanced Business Intelligence
   - Quantization: F16 (high precision)
   - Parameters: 14.8B
   - Use cases: Executive decision support, complex reasoning

3. **qwen:1.8b** (1.1GB)
   - Role: Lightweight Operations
   - Quantization: Q4_0
   - Parameters: 2B
   - Use cases: Quick responses, high-volume processing

4. **deepcoder:14b** (9.0GB)
   - Role: Code Generation
   - Quantization: Q4_K_M  
   - Parameters: 14.8B
   - Use cases: Software development, system integration

5. **yi:34b-chat** (19GB)
   - Role: Advanced Reasoning
   - Quantization: Q4_0
   - Parameters: 34B
   - Use cases: Complex problem solving, strategic analysis

## Performance Optimization

### Memory Management
- Maximum 4 models loaded simultaneously
- Automatic unloading after inactivity
- VRAM optimization enabled
- Flash attention for faster inference

### Parallel Processing
- 2 concurrent request streams
- Load balancing across available models
- GPU acceleration on CUDA devices 0,1

### Network Configuration
- All network interfaces accessible
- CORS enabled for web integration
- Standard port 11434 for API access

## API Endpoints

- **Health Check:** `GET http://localhost:11434/`
- **Model List:** `GET http://localhost:11434/api/tags`
- **Model Status:** `GET http://localhost:11434/api/ps`
- **Version Info:** `GET http://localhost:11434/api/version`
- **Generate:** `POST http://localhost:11434/api/generate`
- **Chat:** `POST http://localhost:11434/api/chat`

## Integration with Citadel

### Python Access
- Available via requests library in citadel_venv
- Direct API integration ready
- FastAPI gateway service configured

### Gateway Service
- Service: ollama-gateway-02.service
- Port: 8000 (business API)
- Environment: citadel_venv virtual environment
- Auto-restart enabled

## Monitoring

### System Health
- Service monitoring via systemd
- Debug logging enabled
- Performance metrics available
- Memory usage tracking

### Model Status
- Real-time model loading status
- VRAM usage monitoring  
- Request throughput tracking
- Error rate monitoring

## Troubleshooting

### Common Issues
- **Port conflicts:** Resolved by using ollama-02.service
- **Memory limits:** Automatic model unloading configured
- **GPU access:** CUDA devices properly configured
- **Network access:** All interfaces enabled

### Debug Commands
```bash
# Service status
sudo systemctl status ollama-02.service

# API health check  
curl http://localhost:11434/api/version

# Model status
curl http://localhost:11434/api/ps

# Service logs
sudo journalctl -u ollama-02.service -f
```

## Security Configuration

- Service runs as dedicated `ollama` user
- Models stored in protected directory
- Network access controlled
- Debug logging for audit trail

---

**Configuration Date:** 2025-07-25  
**Optimized for:** LLM-02 Business Operations  
**Compatible with:** Citadel LLM System v2.0
