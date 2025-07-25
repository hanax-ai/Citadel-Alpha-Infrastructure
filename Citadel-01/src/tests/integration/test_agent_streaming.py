#!/usr/bin/env python3
"""
Test script for agent-specific streaming endpoints.
Demonstrates usage of voice, copilot, and GUI optimized endpoints.
"""

import asyncio
import aiohttp
import json
import time
from typing import AsyncGenerator

GATEWAY_URL = "http://localhost:8002"
TEST_MODEL = "phi3"

async def test_streaming_endpoint(endpoint: str, data: dict, agent_type: str):
    """Test a streaming endpoint and measure performance characteristics."""
    print(f"\n🚀 Testing {agent_type.upper()} Agent Endpoint: {endpoint}")
    print(f"📝 Request: {json.dumps(data, indent=2)}")
    
    start_time = time.time()
    first_token_time = None
    token_count = 0
    chunks_received = 0
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GATEWAY_URL}{endpoint}", json=data) as response:
                print(f"🔌 Connection established. Status: {response.status}")
                print(f"📊 Headers: {dict(response.headers)}")
                
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        chunk_data = chunk.decode('utf-8')
                        chunks_received += 1
                        
                        # Mark first token time
                        if first_token_time is None:
                            first_token_time = time.time()
                            print(f"⚡ First token received in {first_token_time - start_time:.3f}s")
                        
                        # Parse streaming chunks
                        for line in chunk_data.split('\n'):
                            if line.startswith('data: ') and not line.endswith('[DONE]'):
                                try:
                                    data_content = json.loads(line[6:])
                                    content = data_content.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    if content:
                                        token_count += len(content.split())
                                        print(f"📨 Chunk {chunks_received}: {repr(content[:50])}...")
                                except json.JSONDecodeError:
                                    continue
                        
                        # Show progress for different agent types
                        if agent_type == "voice" and chunks_received % 5 == 0:
                            print(f"🎙️  Voice agent: {chunks_received} chunks, {token_count} tokens")
                        elif agent_type == "copilot" and chunks_received % 3 == 0:
                            print(f"💻 Copilot agent: {chunks_received} chunks, {token_count} tokens") 
                        elif agent_type == "gui" and chunks_received % 2 == 0:
                            print(f"🖥️  GUI agent: {chunks_received} chunks, {token_count} tokens")
                
    except Exception as e:
        print(f"❌ Error testing {agent_type} endpoint: {e}")
        return
    
    total_time = time.time() - start_time
    time_to_first_token = first_token_time - start_time if first_token_time else 0
    
    print(f"\n📈 {agent_type.upper()} Agent Performance:")
    print(f"   ⏱️  Total time: {total_time:.3f}s")
    print(f"   ⚡ Time to first token: {time_to_first_token:.3f}s")
    print(f"   📦 Total chunks: {chunks_received}")
    print(f"   🔤 Estimated tokens: {token_count}")
    if chunks_received > 0:
        print(f"   📊 Avg chunk interval: {total_time/chunks_received:.3f}s")


async def test_voice_agent():
    """Test voice agent endpoint - optimized for real-time speech."""
    data = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": "Tell me a short joke in exactly 2 sentences."}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    await test_streaming_endpoint("/v1/voice/chat/completions", data, "voice")


async def test_copilot_agent():
    """Test copilot agent endpoint - optimized for code completion."""
    data = {
        "model": TEST_MODEL,
        "prompt": "def fibonacci(n):\n    # Generate fibonacci sequence up to n\n    ",
        "max_tokens": 150,
        "temperature": 0.2,
        "stop": ["\n\n"]
    }
    
    await test_streaming_endpoint("/v1/copilot/completions", data, "copilot")


async def test_gui_agent():
    """Test GUI agent endpoint - optimized for chat interfaces."""
    data = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that explains technical concepts clearly."},
            {"role": "user", "content": "Explain what API streaming is and why it's useful for user interfaces."}
        ],
        "max_tokens": 200,
        "temperature": 0.8
    }
    
    await test_streaming_endpoint("/v1/gui/chat/completions", data, "gui")


async def test_generic_agent():
    """Test generic agent endpoint with different agent types."""
    data = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": "Count from 1 to 5 slowly."}
        ],
        "max_tokens": 30
    }
    
    for agent_type in ["voice", "copilot", "gui"]:
        endpoint = f"/v1/agents/stream?agent_type={agent_type}"
        await test_streaming_endpoint(endpoint, data, f"generic-{agent_type}")


async def compare_streaming_vs_nonstreaming():
    """Compare streaming vs non-streaming performance."""
    data = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": "Write a haiku about technology."}
        ],
        "max_tokens": 50
    }
    
    print("\n🔄 COMPARISON: Streaming vs Non-Streaming")
    
    # Test non-streaming (original endpoint)
    print("\n📦 Testing NON-STREAMING endpoint:")
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GATEWAY_URL}/v1/chat/completions", json=data) as response:
                result = await response.json()
                total_time = time.time() - start_time
                content = result.get('message', {}).get('content', 'No content')
                print(f"   ⏱️  Total time: {total_time:.3f}s")
                print(f"   📝 Complete response: {repr(content[:100])}...")
                print(f"   🎯 User experience: Wait {total_time:.1f}s → Full response appears")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test streaming (GUI agent)
    print("\n🌊 Testing STREAMING endpoint (GUI agent):")
    await test_streaming_endpoint("/v1/gui/chat/completions", data, "gui")


async def main():
    """Run all agent endpoint tests."""
    print("🧪 CITADEL AGENT-SPECIFIC STREAMING ENDPOINT TESTS")
    print("=" * 60)
    
    print("\n🎯 Testing individual agent endpoints:")
    
    # Test each agent type
    await test_voice_agent()
    await test_copilot_agent() 
    await test_gui_agent()
    
    print("\n🔧 Testing generic agent endpoint:")
    await test_generic_agent()
    
    print("\n⚖️  Performance comparison:")
    await compare_streaming_vs_nonstreaming()
    
    print("\n✅ All agent endpoint tests completed!")
    print("\n📋 AGENT ENDPOINT SUMMARY:")
    print("   🎙️  /v1/voice/chat/completions     - Real-time voice (1 token chunks, 30s timeout)")
    print("   💻 /v1/copilot/completions        - IDE integration (5 token chunks, 60s timeout)")
    print("   🖥️  /v1/gui/chat/completions       - UI optimized (10 token chunks, 120s timeout)")
    print("   🔧 /v1/agents/stream              - Generic configurable (query param: agent_type)")
    print("   📦 /v1/chat/completions           - Enterprise audit (non-streaming, full logging)")


if __name__ == "__main__":
    asyncio.run(main())
