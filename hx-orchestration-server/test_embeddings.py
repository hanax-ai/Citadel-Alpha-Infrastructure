#!/usr/bin/env python3
"""
Simple test script to debug the embeddings endpoint
"""
import asyncio
import sys
import os
sys.path.append('/opt/citadel-orca/hx-orchestration-server')

async def test_embedding_components():
    """Test individual embedding components"""
    print("Testing embedding components...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from app.core.embeddings.ollama_client import OllamaClient
        from app.core.embeddings.cache_manager import CacheManager
        from app.core.embeddings.batch_processor import BatchProcessor
        print("   ✓ All imports successful")
        
        # Test Ollama client
        print("2. Testing Ollama client...")
        ollama_client = OllamaClient()
        await ollama_client.initialize()
        print("   ✓ Ollama client initialized")
        
        # Test a simple embedding
        print("3. Testing embedding generation...")
        embeddings = await ollama_client.generate_embeddings(["Hello world"], "nomic-embed-text")
        print(f"   ✓ Generated {len(embeddings)} embeddings")
        print(f"   ✓ Embedding dimension: {len(embeddings[0])}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_embedding_components())
