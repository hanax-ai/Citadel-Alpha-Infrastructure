#!/bin/bash
# Citadel LLM-02 Production Health Check

echo "=== CITADEL LLM-02 PRODUCTION HEALTH CHECK ==="
echo "Date: $(date)"
echo "Server: $(hostname)"
echo

# Check Ollama service
echo "1. Ollama Service Status:"
systemctl is-active ollama-02.service
curl -s http://localhost:11434/api/tags | jq '.models | length'
echo

# Check all models
echo "2. Model Availability:"
ollama list | grep -E "(deepseek-r1:32b|hadad/JARVIS|qwen:1.8b|deepcoder:14b|yi:34b-chat)" | wc -l
echo "Expected: 5 models"
echo

# Check API Gateway
echo "3. API Gateway Status:"
curl -s http://localhost:8000/health | jq '.status'
curl -s http://localhost:8000/integration-health | jq '.api_gateway'
echo

# Check external service connectivity
echo "4. External Service Connectivity:"
ping -c 1 192.168.10.35 > /dev/null && echo "✅ PostgreSQL reachable" || echo "❌ PostgreSQL unreachable"
ping -c 1 192.168.10.37 > /dev/null && echo "✅ Monitoring reachable" || echo "❌ Monitoring unreachable"
echo

# Check knowledge base
echo "5. Knowledge Base Status:"
curl -s http://localhost:8000/api/v2/business/integration-status | jq '.vector_database.total_vectors'
echo

# Check system resources
echo "6. System Resources:"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h /opt/citadel-02 | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo

echo "=== HEALTH CHECK COMPLETE ==="
