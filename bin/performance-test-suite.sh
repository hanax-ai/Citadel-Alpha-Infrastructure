#!/bin/bash
# Citadel LLM-02 Performance Test Suite

echo "=== CITADEL LLM-02 PERFORMANCE TEST SUITE ==="
echo "Starting comprehensive performance validation..."

# Check if API Gateway is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ API Gateway not running - please start it first"
    exit 1
else
    echo "✅ API Gateway running"
fi

# Test 1: Quick Processing (Qwen) - Target: <5s
echo
echo "Test 1: Quick Processing Performance..."
start_time=$(date +%s.%N)
curl -s -X POST http://localhost:8000/api/v1/technical/quick-process \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What are the key benefits of AI in business?"}' > /dev/null
end_time=$(date +%s.%N)
qwen_time=$(echo "$end_time - $start_time" | bc)
echo "Qwen Response Time: ${qwen_time}s (Target: <5s)"

# Test 2: Code Generation (DeepCoder) - Target: <60s
echo
echo "Test 2: Code Generation Performance..."
start_time=$(date +%s.%N)
curl -s -X POST http://localhost:8000/api/v1/technical/generate-code \
  -H "Content-Type: application/json" \
  -d '{"task":"Create a simple REST API endpoint","language":"python","complexity":"simple"}' > /dev/null
end_time=$(date +%s.%N)
deepcoder_time=$(echo "$end_time - $start_time" | bc)
echo "DeepCoder Response Time: ${deepcoder_time}s (Target: <60s)"

# Test 3: Business Intelligence (JARVIS) - Target: <90s
echo
echo "Test 3: Business Intelligence Performance..."
start_time=$(date +%s.%N)
curl -s -X POST http://localhost:8000/api/v1/business/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"Executive summary of AI market trends","analysis_type":"strategic","priority":"high"}' > /dev/null
end_time=$(date +%s.%N)
jarvis_time=$(echo "$end_time - $start_time" | bc)
echo "JARVIS Response Time: ${jarvis_time}s (Target: <90s)"

# Test 4: Enhanced Business Analysis with Knowledge Base
echo
echo "Test 4: Enhanced Business Analysis Performance..."
start_time=$(date +%s.%N)
curl -s -X POST http://localhost:8000/api/v2/business/analyze-enhanced \
  -H "Content-Type: application/json" \
  -d '{"query":"Manufacturing AI implementation strategy","analysis_type":"strategic","priority":"high","use_knowledge_base":true}' > /dev/null
end_time=$(date +%s.%N)
enhanced_time=$(echo "$end_time - $start_time" | bc)
echo "Enhanced Analysis Response Time: ${enhanced_time}s"

# Test 5: Knowledge Base Search
echo
echo "Test 5: Knowledge Base Search Performance..."
start_time=$(date +%s.%N)
curl -s http://localhost:8000/api/v2/business/knowledge-search/manufacturing%20AI > /dev/null
end_time=$(date +%s.%N)
kb_time=$(echo "$end_time - $start_time" | bc)
echo "Knowledge Base Search Time: ${kb_time}s (Target: <2s)"

# Performance Summary
echo
echo "=== PERFORMANCE SUMMARY ==="
echo "Qwen (Quick Processing): ${qwen_time}s"
echo "DeepCoder (Code Generation): ${deepcoder_time}s"
echo "JARVIS (Business Intelligence): ${jarvis_time}s"
echo "Enhanced Analysis: ${enhanced_time}s"
echo "Knowledge Base Search: ${kb_time}s"

echo
echo "=== PERFORMANCE TEST COMPLETE ==="
