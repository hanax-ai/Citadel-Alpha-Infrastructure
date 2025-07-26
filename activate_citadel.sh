#!/bin/bash
# Citadel LLM Virtual Environment Activation Script
# This script activates the citadel_venv virtual environment as required by .rulesfile

echo "🚀 Activating Citadel LLM Virtual Environment..."
source /opt/citadel-02/citadel_venv/bin/activate

echo "✅ citadel_venv is now active"
echo "📍 Python path: $(which python)"
echo "📍 Python version: $(python --version)"
echo "📍 Virtual environment: $VIRTUAL_ENV"
echo ""
echo "💡 To deactivate: type 'deactivate'"
echo "💡 Key packages installed: FastAPI, PyTorch, Transformers, PostgreSQL, Redis, Testing suite"
