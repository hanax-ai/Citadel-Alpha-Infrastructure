#!/bin/bash
# Citadel LLM-02 API Gateway Startup Script

cd /opt/citadel-02/src/api_gateway
export PYTHONPATH="/opt/citadel-02/src:$PYTHONPATH"

echo "Starting Citadel LLM-02 API Gateway..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
