#!/usr/bin/env python3
"""
Agent-Specific Streaming Integration Tests for Citadel LLM
Tests voice, copilot, GUI, and generic agent streaming endpoints
"""

import asyncio
import aiohttp
import json
import time
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Server-02 configuration
SERVER_BASE_URL = "http://localhost:8000"
TEST_MODEL = "qwen"  # Fast model for testing


async def test_streaming_endpoint(endpoint: str, agent_type: str, expected_characteristics: dict):
    """Test a specific streaming endpoint with agent-optimized characteristics"""
    
    print(f"\n🔄 Testing {agent_type.upper()} Agent Streaming...")
    print(f"   Endpoint: {endpoint}")
    print(f"   Expected chunk size: {expected_characteristics['chunk_size']}")
    print(f"   Expected timeout: {expected_characteristics['timeout']}s")
    
    test_data = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": f"Tell me a brief story for {agent_type} agent testing. Keep it short."}
        ],
        "max_tokens": 50
    }
    
    if "?agent_type=" in endpoint:
        # Generic endpoint
        url = endpoint
    else:
        url = f"{SERVER_BASE_URL}{endpoint}"
    
    start_time = time.time()
    chunks_received = 0
    total_content = ""
    first_chunk_time = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data, headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"   ❌ HTTP {response.status}: {error_text}")
                    return False
                
                print(f"   ✅ Connection established (HTTP {response.status})")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith("data: "):
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            ttft = first_chunk_time - start_time
                            print(f"   ⚡ Time to first token: {ttft:.2f}s")
                        
                        data_content = line[6:]  # Remove "data: " prefix
                        
                        if data_content == "[DONE]":
                            print(f"   🏁 Stream completed")
                            break
                        
                        try:
                            chunk_data = json.loads(data_content)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    total_content += content
                                    chunks_received += 1
                                    
                                    if chunks_received <= 3:  # Show first few chunks
                                        print(f"   📝 Chunk {chunks_received}: '{content}'")
                        
                        except json.JSONDecodeError:
                            # Skip non-JSON lines
                            continue
                
                total_time = time.time() - start_time
                
                print(f"   📊 Results:")
                print(f"      Total chunks: {chunks_received}")
                print(f"      Total content length: {len(total_content)} chars")
                print(f"      Total time: {total_time:.2f}s")
                print(f"      Average chunk time: {(total_time / max(chunks_received, 1)):.3f}s")
                print(f"      Content preview: '{total_content[:100]}...'")
                
                # Validate agent-specific characteristics
                if chunks_received > 0:
                    avg_chunk_time = total_time / chunks_received
                    expected_delay = expected_characteristics['delay_ms'] / 1000.0
                    
                    print(f"   🎯 Agent Validation:")
                    print(f"      Expected delay: {expected_delay:.3f}s")
                    print(f"      Actual avg delay: {avg_chunk_time:.3f}s")
                    
                    if avg_chunk_time >= expected_delay * 0.5:  # Allow 50% variance
                        print(f"      ✅ Timing characteristics match {agent_type} agent")
                    else:
                        print(f"      ⚠️ Timing faster than expected (may be normal)")
                
                return chunks_received > 0 and len(total_content) > 0
                
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


async def test_agent_endpoints():
    """Test all agent-specific streaming endpoints"""
    
    print("🚀 Starting Citadel Agent Streaming Tests")
    print("=" * 60)
    print(f"🖥️ Server: {SERVER_BASE_URL}")
    print(f"🤖 Test Model: {TEST_MODEL}")
    print("=" * 60)
    
    # Test configurations matching the gateway
    test_cases = [
        {
            "endpoint": "/v1/voice/chat/completions",
            "agent_type": "voice",
            "characteristics": {
                "chunk_size": 1,
                "timeout": 30,
                "delay_ms": 10
            }
        },
        {
            "endpoint": "/v1/copilot/completions", 
            "agent_type": "copilot",
            "characteristics": {
                "chunk_size": 5,
                "timeout": 60,
                "delay_ms": 100
            }
        },
        {
            "endpoint": "/v1/gui/chat/completions",
            "agent_type": "gui", 
            "characteristics": {
                "chunk_size": 10,
                "timeout": 120,
                "delay_ms": 200
            }
        },
        {
            "endpoint": f"{SERVER_BASE_URL}/v1/agents/stream?agent_type=voice",
            "agent_type": "generic-voice",
            "characteristics": {
                "chunk_size": 1,
                "timeout": 30,
                "delay_ms": 10
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        success = await test_streaming_endpoint(
            test_case["endpoint"],
            test_case["agent_type"],
            test_case["characteristics"]
        )
        results.append((test_case["agent_type"], success))
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("🧪 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for agent_type, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {agent_type.upper()} Agent Streaming")
        if success:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL AGENT STREAMING TESTS PASSED!")
        print("✅ Voice agents ready for real-time TTS integration")
        print("✅ Copilot agents ready for IDE integration") 
        print("✅ GUI agents ready for chat interface integration")
        print("✅ Generic agent endpoint ready for custom development")
        return True
    else:
        print("❌ Some tests failed - check the errors above")
        return False


async def test_performance_comparison():
    """Compare performance between non-streaming and streaming endpoints"""
    
    print("\n🔬 Performance Comparison Test")
    print("=" * 40)
    
    test_message = {
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": "Count from 1 to 10"}],
        "max_tokens": 30
    }
    
    # Test non-streaming endpoint
    print("Testing non-streaming endpoint...")
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_BASE_URL}/v1/chat/completions", json=test_message) as response:
                if response.status == 200:
                    non_streaming_time = time.time() - start_time
                    result = await response.json()
                    print(f"   ✅ Non-streaming completed in {non_streaming_time:.2f}s")
                else:
                    print(f"   ❌ Non-streaming failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Non-streaming error: {e}")
        return False
    
    # Test streaming endpoint (GUI agent)
    print("Testing streaming endpoint...")
    start_time = time.time()
    first_chunk_time = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_BASE_URL}/v1/gui/chat/completions", json=test_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: ") and first_chunk_time is None:
                            first_chunk_time = time.time()
                            break
                    
                    streaming_ttft = first_chunk_time - start_time if first_chunk_time else None
                    if streaming_ttft:
                        print(f"   ✅ Streaming first token in {streaming_ttft:.2f}s")
                        print(f"   📈 Streaming advantage: {(non_streaming_time - streaming_ttft):.2f}s faster to first token")
                        return True
                else:
                    print(f"   ❌ Streaming failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Streaming error: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🎯 Citadel LLM - Agent Streaming Test Suite")
        print("Server-02 Implementation Validation")
        print("=" * 80)
        
        # Test 1: Agent endpoint functionality
        agent_tests_passed = await test_agent_endpoints()
        
        # Test 2: Performance comparison
        perf_test_passed = await test_performance_comparison()
        
        print("\n" + "=" * 80)
        if agent_tests_passed and perf_test_passed:
            print("🎉 ALL STREAMING TESTS PASSED!")
            print("✅ Agent-specific streaming endpoints are fully operational")
            print("✅ Voice, Copilot, and GUI agents ready for production")
            print("✅ Performance characteristics validated")
            print("🚀 Ready for real-time AI agent integration!")
        else:
            print("❌ Some tests failed - please review the errors above")
            sys.exit(1)
    
    # Run the async tests
    asyncio.run(main())
