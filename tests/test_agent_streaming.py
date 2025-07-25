#!/usr/bin/env python3
"""
Agent Streaming Endpoints Test Suite for Server-02
Tests voice, copilot, GUI, and generic streaming endpoints
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_MODEL = "qwen"  # Fast model for testing

class StreamingTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_streaming_endpoint(self, endpoint: str, agent_type: str, expected_chunk_pattern: str):
        """Test a streaming endpoint and measure performance"""
        print(f"\n🧪 Testing {agent_type} Agent: {endpoint}")
        print("-" * 60)
        
        # Prepare test data
        test_data = {
            "model": TEST_MODEL,
            "messages": [
                {"role": "user", "content": f"Give me a brief {agent_type} test response in about 20 words"}
            ],
            "max_tokens": 50
        }
        
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        chunks_received = 0
        total_content = ""
        first_chunk_time = None
        
        try:
            async with self.session.post(url, json=test_data) as response:
                if response.status != 200:
                    print(f"❌ HTTP Error: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                
                print(f"✅ Connection established ({response.status})")
                print(f"📡 Headers: {dict(response.headers)}")
                
                # Process streaming response
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: '):
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            time_to_first = first_chunk_time - start_time
                            print(f"⚡ Time to first chunk: {time_to_first:.3f}s")
                        
                        data_content = line_str[6:]  # Remove 'data: '
                        
                        if data_content == '[DONE]':
                            print(f"🏁 Stream completed")
                            break
                            
                        try:
                            chunk_data = json.loads(data_content)
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    total_content += content
                                    chunks_received += 1
                                    print(f"📦 Chunk {chunks_received}: '{content}' ({len(content)} chars)")
                                    
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
                
                total_time = time.time() - start_time
                
                print(f"\n📊 {agent_type} Agent Results:")
                print(f"   ✅ Total chunks: {chunks_received}")
                print(f"   ✅ Total content: {len(total_content)} characters")
                print(f"   ✅ Total time: {total_time:.3f}s")
                print(f"   ✅ Content preview: '{total_content[:100]}...'")
                
                if chunks_received > 0:
                    avg_chunk_time = total_time / chunks_received
                    print(f"   ✅ Average chunk time: {avg_chunk_time:.3f}s")
                
                return chunks_received > 0 and len(total_content) > 0
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def test_health_check(self):
        """Test gateway health before streaming tests"""
        print("🏥 Testing Gateway Health...")
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Gateway healthy: {health_data['status']}")
                    return True
                else:
                    print(f"❌ Gateway unhealthy: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def main():
    """Run comprehensive streaming tests"""
    print("🚀 Server-02 Agent Streaming Endpoint Test Suite")
    print("=" * 80)
    print(f"📡 Testing against: {BASE_URL}")
    print(f"🤖 Using model: {TEST_MODEL}")
    
    async with StreamingTester() as tester:
        # Test gateway health first
        if not await tester.test_health_check():
            print("❌ Gateway health check failed. Aborting tests.")
            sys.exit(1)
        
        # Test all streaming endpoints
        test_cases = [
            ("/v1/voice/chat/completions", "Voice", "single token"),
            ("/v1/copilot/completions", "Copilot", "5-token chunks"),
            ("/v1/gui/chat/completions", "GUI", "10-token chunks"),
            ("/v1/agents/stream?agent_type=voice", "Generic-Voice", "configurable"),
            ("/v1/agents/stream?agent_type=copilot", "Generic-Copilot", "configurable"),
            ("/v1/agents/stream?agent_type=gui", "Generic-GUI", "configurable"),
        ]
        
        results = []
        
        for endpoint, agent_type, pattern in test_cases:
            success = await tester.test_streaming_endpoint(endpoint, agent_type, pattern)
            results.append((agent_type, success))
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 Test Results Summary")
        print("=" * 80)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for agent_type, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} - {agent_type} Agent Streaming")
        
        print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL STREAMING ENDPOINTS WORKING!")
            print("✅ Voice agents ready for real-time speech synthesis")
            print("✅ Copilot agents ready for IDE integration")
            print("✅ GUI agents ready for chat interfaces")
            print("✅ Generic agents ready for custom development")
        else:
            print("⚠️ Some streaming endpoints need attention")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
