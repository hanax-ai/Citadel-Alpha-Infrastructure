#!/usr/bin/env python3
"""
Citadel Server-02 Test Suite Runner
Comprehensive testing for all system components
"""

import asyncio
import subprocess
import sys
import time
import requests
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_header(title):
    """Print a formatted test section header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(test_name, success, details=""):
    """Print formatted test result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

async def test_gateway_health():
    """Test gateway health endpoint"""
    print_header("Gateway Health Check")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print_result("Gateway Health", True, f"Status: {health_data.get('status', 'unknown')}")
            
            # Check individual services
            services = health_data.get('services', {})
            for service, status in services.items():
                if isinstance(status, str):
                    print_result(f"  {service}", status == "ok", f"Status: {status}")
            
            return True
        else:
            print_result("Gateway Health", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Gateway Health", False, f"Connection error: {e}")
        return False

async def test_business_models():
    """Test all Server-02 business models"""
    print_header("Business Model Testing")
    
    models = ["qwen", "yi-34b", "deepcoder", "jarvis", "deepseek"]
    results = []
    
    for model in models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"Test {model} model"}],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                print_result(f"Model {model}", True, f"Response time: {duration:.2f}s")
                results.append(True)
            else:
                print_result(f"Model {model}", False, f"HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_result(f"Model {model}", False, f"Error: {e}")
            results.append(False)
    
    return all(results)

async def test_cache_performance():
    """Test embeddings cache performance"""
    print_header("Cache Performance Testing")
    
    try:
        # Run the existing cache test
        result = subprocess.run([
            sys.executable, "performance/test_cache.py"
        ], cwd="/opt/citadel-02/tests", capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("Cache Performance Test Output:")
            print(result.stdout)
            print_result("Cache Performance", True)
            return True
        else:
            print_result("Cache Performance", False, f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_result("Cache Performance", False, f"Error: {e}")
        return False

async def test_sql_integration():
    """Test SQL database integration"""
    print_header("SQL Integration Testing")
    
    try:
        # Run the SQL integration test
        result = subprocess.run([
            sys.executable, "integration/test_sql_integration.py"
        ], cwd="/opt/citadel-02/tests", capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("SQL Integration Test Output:")
            print(result.stdout)
            print_result("SQL Integration", True)
            return True
        else:
            print_result("SQL Integration", False, f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_result("SQL Integration", False, f"Error: {e}")
        return False

async def test_embeddings_endpoint():
    """Test embeddings endpoint functionality"""
    print_header("Embeddings Endpoint Testing")
    
    try:
        payload = {
            "model": "qwen",
            "prompt": "Test embedding generation for Server-02"
        }
        
        response = requests.post(
            "http://localhost:8000/api/embeddings",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "embedding" in data and data["embedding"]:
                print_result("Embeddings Endpoint", True, f"Generated {len(data['embedding'])} dimensions")
                return True
            else:
                print_result("Embeddings Endpoint", False, "No embedding data in response")
                return False
        else:
            print_result("Embeddings Endpoint", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Embeddings Endpoint", False, f"Error: {e}")
        return False

async def run_comprehensive_test_suite():
    """Run the complete test suite"""
    print("🚀 Starting Citadel Server-02 Comprehensive Test Suite")
    print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Server: hx-llm-server-02 (192.168.10.28)")
    
    test_results = []
    
    # Run all test categories
    test_results.append(await test_gateway_health())
    test_results.append(await test_business_models())
    test_results.append(await test_embeddings_endpoint())
    test_results.append(await test_cache_performance())
    test_results.append(await test_sql_integration())
    
    # Summary
    print_header("Test Suite Summary")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Server-02 is fully operational!")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test_suite())
    sys.exit(0 if success else 1)
