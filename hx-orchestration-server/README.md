# HX-Orchestration-Server

**Version:** 2.0  
**Server:** hx-orchestration-server (192.168.10.31)  
**Architecture:** 3-Layer FastAPI + Celery (Production Pattern)  

## Overview

HX-Orchestration-Server is a high-performance orchestration and embedding processing server that coordinates AI workflows across the Citadel infrastructure. Built with FastAPI and Celery, it provides OpenAI-compatible embedding endpoints and advanced workflow orchestration capabilities.

## Quick Start

### Prerequisites
- Ubuntu 24.04 LTS
- Python 3.12.3
- Existing `citadel_venv` virtual environment

### Installation

1. Activate the virtual environment:
   ```bash
   source /opt/citadel-venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start services:
   ```bash
   # Start FastAPI server
   python main.py
   
   # Start Celery worker (in another terminal)
   celery -A celery_app worker --loglevel=info
   ```

## API Endpoints

- **Embeddings:** `POST /v1/embeddings` (OpenAI compatible)
- **Orchestration:** `POST /v1/orchestrate`
- **Health:** `GET /health/`
- **Metrics:** `GET /metrics` (Prometheus)

## Architecture

### Core Components
- **FastAPI Application:** High-performance API gateway
- **Celery Workers:** Distributed task processing
- **Orchestration Engine:** Workflow coordination
- **Embedding Framework:** Multi-model embedding processing

### External Integrations
- **LLM Services:** LLM-01 (192.168.10.34:8002), LLM-02 (192.168.10.28:8000)
- **Vector Database:** Qdrant (192.168.10.30:6333)
- **Metadata Storage:** PostgreSQL (192.168.10.35:5432)
- **Monitoring:** Prometheus (192.168.10.37:9090)

## Development

See `docs/development/setup.md` for detailed development setup instructions.

## Documentation

- **API Documentation:** `docs/api/`
- **Operations Guide:** `docs/operations/`
- **Architecture:** `docs/architecture/`

## Monitoring

Access monitoring dashboards:
- **Grafana:** http://192.168.10.37:3000
- **Prometheus:** http://192.168.10.37:9090

## Support

For operational issues, see `docs/operations/troubleshooting.md`.
