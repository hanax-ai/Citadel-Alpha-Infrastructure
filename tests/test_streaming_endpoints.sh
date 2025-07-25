#!/bin/bash
# Citadel Agent Streaming Test Script for Open WebUI Integration

echo "🚀 Citadel Server-02 Agent Streaming Test Script"
echo "================================================="
echo "Server: hx-llm-server-02 (192.168.10.28)"
echo "Gateway: http://localhost:8000"
echo "Open WebUI: http://192.168.10.38:3000"
echo ""

# Test 1: Voice Agent Streaming
echo "🎤 Testing Voice Agent (Real-time Speech)"
echo "-----------------------------------------"
curl -X POST http://localhost:8000/v1/voice/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "Say hello for voice synthesis"}],
    "max_tokens": 30
  }' \
  --no-buffer | head -20

echo -e "\n\n💻 Testing Copilot Agent (Code Completion)" 
echo "--------------------------------------------"
curl -X POST http://localhost:8000/v1/copilot/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen", 
    "messages": [{"role": "user", "content": "Write a simple Python function"}],
    "max_tokens": 50
  }' \
  --no-buffer | head -15

echo -e "\n\n🖥️ Testing GUI Agent (Chat Interface)"
echo "---------------------------------------"
curl -X POST http://localhost:8000/v1/gui/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "Explain AI in simple terms"}],
    "max_tokens": 60
  }' \
  --no-buffer | head -10

echo -e "\n\n🔧 Testing Generic Agent (Voice Mode)"
echo "--------------------------------------"
curl -X POST "http://localhost:8000/v1/agents/stream?agent_type=voice" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "Generic voice test"}],
    "max_tokens": 25
  }' \
  --no-buffer | head -10

echo -e "\n\n✅ All agent streaming endpoints tested!"
echo "📋 Summary of Available Endpoints:"
echo "   🎤 Voice:    /v1/voice/chat/completions"
echo "   💻 Copilot:  /v1/copilot/completions" 
echo "   🖥️ GUI:      /v1/gui/chat/completions"
echo "   🔧 Generic:  /v1/agents/stream?agent_type=X"
echo ""
echo "🌐 For interactive testing, visit: http://192.168.10.28:8080"
echo "🔧 To configure Open WebUI, use these endpoints as API bases"
