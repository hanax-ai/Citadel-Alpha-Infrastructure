# Agent-Specific Streaming Endpoints

The Citadel API Gateway now provides **agent-optimized streaming endpoints** designed for real-time AI applications including voice agents, Copilot-Kit integration, and GUI interfaces.

## Architecture Overview

### Hybrid Approach
- **Non-streaming endpoints**: Enterprise audit, complete logging, Redis caching
- **Streaming endpoints**: Real-time agent experiences with background logging

### Agent-Specific Optimizations

| Agent Type | Endpoint | Chunk Size | Timeout | Use Case |
|------------|----------|------------|---------|----------|
| **Voice** | `/v1/voice/chat/completions` | 1 token | 30s | Real-time speech synthesis |
| **Copilot** | `/v1/copilot/completions` | 5 tokens | 60s | IDE code completion |
| **GUI** | `/v1/gui/chat/completions` | 10 tokens | 120s | Chat interface display |
| **Generic** | `/v1/agents/stream?agent_type=X` | Configurable | Variable | Flexible agent development |

## Endpoint Specifications

### Voice Agent Endpoint
**POST** `/v1/voice/chat/completions`

Optimized for real-time voice interactions:
- **Single token streaming** for immediate speech synthesis
- **30-second timeout** for responsive voice UX
- **Minimal buffering** (50 tokens) for low latency
- **0.01s delays** between chunks to prevent audio buffer overflow

```bash
curl -X POST http://localhost:8002/v1/voice/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "messages": [
      {"role": "user", "content": "Tell me a quick joke"}
    ],
    "max_tokens": 50
  }'
```

**Response Format:**
```
data: {"choices":[{"delta":{"content":"Why"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" did"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" the"},"index":0,"finish_reason":null}]}

data: [DONE]
```

### Copilot Agent Endpoint
**POST** `/v1/copilot/completions`

Optimized for IDE integration and code completion:
- **5-token chunks** for smooth code appearance
- **60-second timeout** for complex code generation
- **Medium buffering** (200 tokens) for context preservation
- **Code-aware formatting** for better IDE display

```bash
curl -X POST http://localhost:8002/v1/copilot/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "prompt": "def fibonacci(n):\n    # Generate fibonacci sequence\n    ",
    "max_tokens": 150,
    "temperature": 0.2,
    "stop": ["\n\n"]
  }'
```

### GUI Agent Endpoint
**POST** `/v1/gui/chat/completions`

Optimized for chat interfaces and web applications:
- **10-token chunks** for efficient UI rendering
- **120-second timeout** for comprehensive responses
- **Large buffering** (500 tokens) for better user experience
- **UI-friendly formatting** for chat bubbles

```bash
curl -X POST http://localhost:8002/v1/gui/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain machine learning in simple terms."}
    ],
    "max_tokens": 200
  }'
```

### Generic Agent Endpoint
**POST** `/v1/agents/stream?agent_type={voice|copilot|gui}`

Configurable endpoint for custom agent development:
- **Dynamic agent type** via query parameter
- **Inherits configuration** from specified agent type
- **Flexible development** for new agent types

```bash
curl -X POST "http://localhost:8002/v1/agents/stream?agent_type=voice" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Enterprise Features Maintained

### Database Logging
All streaming responses are **aggregated and logged** to PostgreSQL:
```python
# Complete conversation audit trail preserved
await sql_service.save_message(
    conversation_id=conversation_id,
    role="assistant", 
    content=complete_content,  # Full aggregated response
    metadata={
        "agent_type": "voice",
        "streaming": True,
        "token_count": 150,
        "chunk_count": 25
    }
)
```

### Prometheus Metrics
Streaming endpoints include **comprehensive monitoring**:
- **Stream-specific metrics**: `ollama_request_duration{endpoint_type="streaming_voice"}`
- **Agent performance tracking**: Response times by agent type
- **Token throughput**: Tokens per second for each agent type
- **Error rates**: Agent-specific error monitoring

### Redis Caching
While streaming responses can't be cached during streaming, the gateway:
- **Caches complete responses** after streaming completes
- **Serves cached responses** for identical requests
- **Maintains cache performance** for repeated agent interactions

## Integration Examples

### Voice Agent Integration
```python
import asyncio
import aiohttp

async def stream_voice_response(prompt: str):
    data = {
        "model": "phi3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8002/v1/voice/chat/completions", json=data) as response:
            async for chunk in response.content.iter_chunked(1024):
                # Process single tokens for immediate TTS
                for token in parse_stream_chunk(chunk):
                    await text_to_speech(token)  # Real-time synthesis
```

### Copilot-Kit Integration
```typescript
import { CopilotKit } from "@copilotkit/react-core";

const copilotConfig = {
  url: "http://localhost:8002/v1/copilot/completions",
  headers: {
    "Content-Type": "application/json"
  }
};

// CopilotKit will automatically handle streaming
<CopilotKit runtimeUrl={copilotConfig.url}>
  <YourCodeEditor />
</CopilotKit>
```

### GUI Chat Integration
```jsx
import React, { useState } from 'react';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  
  const sendMessage = async (content) => {
    const response = await fetch('http://localhost:8002/v1/gui/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'phi3',
        messages: [...messages, { role: 'user', content }]
      })
    });
    
    // Handle streaming response for real-time chat bubble updates
    const reader = response.body.getReader();
    let assistantMessage = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = new TextDecoder().decode(value);
      const content = parseStreamChunk(chunk);
      assistantMessage += content;
      
      // Update chat bubble in real-time
      setMessages(prev => updateLastMessage(prev, assistantMessage));
    }
  };
  
  return <ChatBubbles messages={messages} onSend={sendMessage} />;
}
```

## Performance Characteristics

### Voice Agent Performance
- **Time to first token**: ~0.5-1.0 seconds
- **Token latency**: ~10-50ms per token
- **Ideal for**: Real-time conversation, TTS integration
- **Timeout**: 30 seconds (voice interactions should be quick)

### Copilot Agent Performance  
- **Time to first token**: ~1.0-2.0 seconds
- **Chunk latency**: ~100-200ms per 5-token chunk
- **Ideal for**: Code completion, IDE integration
- **Timeout**: 60 seconds (code generation can be complex)

### GUI Agent Performance
- **Time to first token**: ~1.0-2.0 seconds  
- **Chunk latency**: ~200-500ms per 10-token chunk
- **Ideal for**: Chat interfaces, web applications
- **Timeout**: 120 seconds (comprehensive responses)

## Migration Guide

### From Non-Streaming to Agent Streaming

**Before (Non-streaming):**
```bash
curl -X POST http://localhost:8002/v1/chat/completions \
  -d '{"model": "phi3", "messages": [...]}'
# Wait 10+ seconds → Complete response
```

**After (Agent streaming):**
```bash
curl -X POST http://localhost:8002/v1/gui/chat/completions \
  -d '{"model": "phi3", "messages": [...]}'
# Immediate stream → Real-time tokens → Complete in same total time
```

### Maintaining Enterprise Compliance
- **Non-streaming endpoints preserved** for audit/compliance use cases
- **Complete conversation logging** maintained for all streaming endpoints
- **Redis caching** continues for performance optimization
- **Prometheus monitoring** enhanced with agent-specific metrics

## Testing

Run the comprehensive test suite:
```bash
cd /opt/citadel
python src/tests/integration/test_agent_streaming.py
```

This will test:
- ✅ Voice agent real-time streaming
- ✅ Copilot agent code completion patterns  
- ✅ GUI agent chat interface optimization
- ✅ Generic agent endpoint flexibility
- ✅ Performance comparison with non-streaming endpoints

## Next Steps

1. **Copilot-Kit Integration**: Use `/v1/copilot/completions` for IDE features
2. **Voice Agent Development**: Implement TTS with `/v1/voice/chat/completions`
3. **AGUI Implementation**: Build chat interfaces with `/v1/gui/chat/completions`
4. **Custom Agents**: Develop new agent types using `/v1/agents/stream`

The gateway now supports both **enterprise audit requirements** (non-streaming) and **real-time agent experiences** (streaming) in a single, unified platform.
