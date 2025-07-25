# HX-Server-02 Agent Streaming Implementation Specification

## Overview
This specification details the complete implementation of the enhanced Citadel API Gateway with agent-specific streaming endpoints on the HX-Server-02 (192.168.10.29) system. The implementation provides both enterprise-grade audit capabilities and real-time streaming for voice agents, Copilot-Kit integration, and GUI applications.

## Server Information
- **Server**: HX-Server-02 (192.168.10.29)
- **OS**: Ubuntu 22.04 LTS
- **Purpose**: Agent-optimized API Gateway with streaming capabilities
- **Network**: Internal LAN (192.168.10.0/24)

## Architecture Overview

### Dual-Mode Gateway Design
```
┌─────────────────────────────────────────────────────────────┐
│                  HX-Server-02 (192.168.10.29)             │
├─────────────────────────────────────────────────────────────┤
│  🌊 STREAMING ENDPOINTS (Real-time Agents)                 │
│  ├── /v1/voice/chat/completions (1 token, 30s timeout)     │
│  ├── /v1/copilot/completions (5 tokens, 60s timeout)       │
│  ├── /v1/gui/chat/completions (10 tokens, 120s timeout)    │
│  └── /v1/agents/stream?type=X (configurable)               │
│                                                             │
│  📦 ENTERPRISE ENDPOINTS (Audit/Compliance)                │
│  ├── /v1/chat/completions (non-streaming, full logging)    │
│  ├── /v1/completions (non-streaming completions)           │
│  └── /api/embeddings (221x Redis cache speedup)            │
│                                                             │
│  🔧 INFRASTRUCTURE                                          │
│  ├── PostgreSQL (conversation logging)                     │
│  ├── Redis (response caching)                              │
│  ├── Prometheus (metrics collection)                       │
│  └── Ollama (local LLM backend)                            │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: System Preparation

### 1.1 Server Setup
```bash
# Connect to HX-Server-02
ssh agent0@192.168.10.29

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    build-essential \
    git \
    curl \
    wget \
    postgresql-client \
    redis-tools \
    htop \
    tmux \
    vim

# Create citadel user if not exists
sudo useradd -m -s /bin/bash citadel
sudo usermod -aG sudo citadel
```

### 1.2 Directory Structure Creation
```bash
# Switch to citadel user
sudo su - citadel

# Create project structure
mkdir -p /opt/citadel/{src,config,logs,data,bin,documentation}
mkdir -p /opt/citadel/src/{citadel_llm,tests}
mkdir -p /opt/citadel/config/{services,secrets,environments}
mkdir -p /opt/citadel/logs/{gateway,monitoring,errors}
mkdir -p /opt/citadel/data/{cache,backups}

# Set proper permissions
sudo chown -R citadel:citadel /opt/citadel
chmod -R 755 /opt/citadel
chmod -R 750 /opt/citadel/config/secrets
```

## Phase 2: Infrastructure Services

### 2.1 PostgreSQL Database Setup
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create citadel database and user
sudo -u postgres psql << EOF
CREATE DATABASE citadel_gateway;
CREATE USER citadel WITH ENCRYPTED PASSWORD 'SecureGatewayPass2024!';
GRANT ALL PRIVILEGES ON DATABASE citadel_gateway TO citadel;
ALTER USER citadel CREATEDB;
\q
EOF

# Test connection
psql -h localhost -U citadel -d citadel_gateway -c "SELECT version();"
```

### 2.2 Redis Cache Setup
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis for production
sudo tee /etc/redis/redis.conf << EOF
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
save 900 1
save 300 10
save 60 10000
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
EOF

# Start and enable Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### 2.3 Ollama LLM Backend Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull required models
ollama pull phi3:latest
ollama pull openchat:latest
ollama pull mixtral:latest
ollama pull nous-hermes2-mixtral:latest
ollama pull nomic-embed-text:latest

# Verify models are available
ollama list
```

## Phase 3: Python Environment Setup

### 3.1 Virtual Environment Creation
```bash
cd /opt/citadel

# Create Python virtual environment
python3.12 -m venv citadel_venv

# Activate virtual environment
source citadel_venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 3.2 Python Dependencies Installation
```bash
# Install core dependencies
pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.25.2 \
    asyncpg==0.29.0 \
    redis==5.0.1 \
    prometheus-client==0.19.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    PyYAML==6.0.1 \
    python-jose[cryptography]==3.3.0 \
    bcrypt==4.1.2

# Install testing dependencies
pip install \
    pytest==7.4.3 \
    pytest-asyncio==0.21.1 \
    aiohttp==3.9.1 \
    httpx==0.25.2

# Create requirements.txt for reproducibility
pip freeze > requirements.txt
```

## Phase 4: Core Application Implementation

### 4.1 Project Structure Deployment
```bash
# Copy source code structure from reference implementation
mkdir -p /opt/citadel/src/citadel_llm/{api,services,models,utils}
mkdir -p /opt/citadel/src/citadel_llm/api/middleware
mkdir -p /opt/citadel/src/tests/{integration,performance,unit}
```

### 4.2 Configuration Files Setup

#### 4.2.1 Database Configuration
```yaml
# /opt/citadel/config/environments/production.yaml
database:
  host: "localhost"
  port: 5432
  database: "citadel_gateway"
  user: "citadel"
  password: "SecureGatewayPass2024!"
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600

redis:
  host: "localhost"
  port: 6379
  database: 0
  max_connections: 20
  socket_timeout: 5
  socket_connect_timeout: 5

project:
  name: "citadel-gateway"
  environment: "production"
  log_level: "INFO"
  debug: false

integration:
  vector_db:
    provider: "qdrant"
    host: "localhost"
    port: 6333
    api_key_secret_name: "QDRANT_API_KEY"
```

#### 4.2.2 Model Routing Configuration
```yaml
# /opt/citadel/config/services/api-gateway/routing.yaml
model_aliases:
  phi3: "phi3:latest"
  openchat: "openchat:latest"
  mixtral: "mixtral:latest"
  nous-hermes2-mixtral: "nous-hermes2-mixtral:latest"
  nomic-embed-text: "nomic-embed-text:latest"

valid_models:
  - "phi3"
  - "openchat"
  - "mixtral"
  - "nous-hermes2-mixtral"
  - "nomic-embed-text"

agent_streaming_config:
  voice:
    chunk_size: 1
    timeout: 30.0
    buffer_size: 50
  copilot:
    chunk_size: 5
    timeout: 60.0
    buffer_size: 200
  gui:
    chunk_size: 10
    timeout: 120.0
    buffer_size: 500
```

### 4.3 Core Gateway Implementation

#### 4.3.1 Main Gateway File
```python
# /opt/citadel/src/citadel_llm/api/gateway.py
# [Full implementation from provided code - 1005 lines]
# This includes all agent-specific streaming endpoints and enterprise features
```

#### 4.3.2 Request Models
```python
# /opt/citadel/src/citadel_llm/models/request_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")

class GenerateRequest(BaseModel):
    model: str = Field(..., description="Model to use for generation")
    prompt: str = Field(..., description="Prompt for generation")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")

class EmbeddingRequest(BaseModel):
    model: str = Field(..., description="Model to use for embeddings")
    prompt: str = Field(..., description="Text to embed")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional options")
```

#### 4.3.3 Database Service
```python
# /opt/citadel/src/citadel_llm/services/sql_service.py
import asyncpg
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SQLService:
    def __init__(self):
        self.pool = None
        self.config = None

    async def initialize(self, config: Dict[str, Any]):
        """Initialize the SQL service with database connection pool."""
        self.config = config
        db_config = config.get('database', {})
        
        self.pool = await asyncpg.create_pool(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password'),
            min_size=5,
            max_size=db_config.get('pool_size', 10),
            command_timeout=30
        )
        
        logger.info("SQL Service initialized successfully")

    async def create_tables(self):
        """Create database tables if they don't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    model_name VARCHAR(255) NOT NULL,
                    title TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id),
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
            ''')

    async def save_conversation(self, user_id: str, model_name: str, title: str, metadata: Dict = None) -> int:
        """Save a conversation and return its ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                '''INSERT INTO conversations (user_id, model_name, title, metadata) 
                   VALUES ($1, $2, $3, $4) RETURNING id''',
                user_id, model_name, title, json.dumps(metadata or {})
            )
            return row['id']

    async def save_message(self, conversation_id: int, role: str, content: str, metadata: Dict = None):
        """Save a message to a conversation."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''INSERT INTO messages (conversation_id, role, content, metadata) 
                   VALUES ($1, $2, $3, $4)''',
                conversation_id, role, content, json.dumps(metadata or {})
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the database."""
        if not self.pool:
            return {"status": "unhealthy", "error": "No database connection"}
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
            return {
                "status": "healthy",
                "database": {
                    "database": self.config.get('database', {}).get('database'),
                    "user": self.config.get('database', {}).get('user')
                },
                "connection_pool": {
                    "size": self.pool.get_size(),
                    "max_size": self.pool.get_max_size()
                }
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()

# Global instance
sql_service = SQLService()
```

#### 4.3.4 Redis Service
```python
# /opt/citadel/src/citadel_llm/services/redis_service.py
import redis.asyncio as redis
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self._client = None
        self.config = None

    async def initialize(self, config: Dict[str, Any]):
        """Initialize Redis connection."""
        self.config = config
        redis_config = config.get('redis', {})
        
        self._client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('database', 0),
            max_connections=redis_config.get('max_connections', 20),
            socket_timeout=redis_config.get('socket_timeout', 5),
            socket_connect_timeout=redis_config.get('socket_connect_timeout', 5),
            decode_responses=True
        )
        
        # Test connection
        await self._client.ping()
        logger.info("Redis Service initialized successfully")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis."""
        if not self._client:
            return {"status": "unhealthy", "error": "No Redis connection"}
        
        try:
            await self._client.ping()
            info = await self._client.info()
            
            return {
                "status": "healthy",
                "redis_version": info.get('redis_version'),
                "used_memory": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients')
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()

# Global instance
redis_service = RedisService()
```

### 4.4 Configuration Utilities
```python
# /opt/citadel/src/citadel_llm/utils/config.py
import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML files."""
    config_dir = "/opt/citadel/config"
    env = os.getenv("CITADEL_ENV", "production")
    
    # Load base configuration
    base_config_path = os.path.join(config_dir, "environments", f"{env}.yaml")
    
    try:
        with open(base_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration for environment: {env}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {base_config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise

def get_database_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract database configuration."""
    return config.get('database', {})
```

## Phase 5: Monitoring and Metrics

### 5.1 Prometheus Metrics Implementation
```python
# /opt/citadel/src/citadel_llm/api/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time
import logging

logger = logging.getLogger(__name__)

class PrometheusMetricsMiddleware:
    def __init__(self):
        # HTTP request metrics
        self.http_requests_total = Counter(
            'citadel_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'citadel_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Ollama-specific metrics
        self.ollama_requests_total = Counter(
            'citadel_ollama_requests_total',
            'Total requests to Ollama',
            ['model', 'endpoint_type']
        )
        
        self.ollama_request_duration = Histogram(
            'citadel_ollama_request_duration_seconds',
            'Ollama request duration in seconds',
            ['model', 'endpoint_type']
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'citadel_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']
        )
        
        # Agent-specific metrics
        self.agent_requests_total = Counter(
            'citadel_agent_requests_total',
            'Total agent requests',
            ['agent_type', 'model']
        )
        
        self.streaming_connections = Gauge(
            'citadel_streaming_connections_active',
            'Active streaming connections',
            ['agent_type']
        )

    def record_ollama_request(self, model: str, endpoint_type: str, duration: float, status_code: int):
        """Record Ollama request metrics."""
        self.ollama_requests_total.labels(model=model, endpoint_type=endpoint_type).inc()
        self.ollama_request_duration.labels(model=model, endpoint_type=endpoint_type).observe(duration)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        self.cache_operations_total.labels(operation='get', result='hit').inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        self.cache_operations_total.labels(operation='get', result='miss').inc()

    def record_cache_operation(self, operation: str, duration: float, result: str):
        """Record cache operation."""
        self.cache_operations_total.labels(operation=operation, result=result).inc()

# Global metrics instance
metrics_middleware = PrometheusMetricsMiddleware()

def get_metrics_middleware():
    return metrics_middleware

def set_metrics_middleware(middleware):
    global metrics_middleware
    metrics_middleware = middleware
```

## Phase 6: Service Configuration

### 6.1 Systemd Service Setup
```ini
# /etc/systemd/system/citadel-gateway.service
[Unit]
Description=Citadel LLM API Gateway
After=network.target postgresql.service redis.service ollama.service
Requires=postgresql.service redis.service

[Service]
Type=exec
User=citadel
Group=citadel
WorkingDirectory=/opt/citadel
Environment=CITADEL_ENV=production
Environment=PYTHONPATH=/opt/citadel/src
ExecStartPre=/bin/bash -c 'source /opt/citadel/citadel_venv/bin/activate'
ExecStart=/opt/citadel/citadel_venv/bin/uvicorn citadel_llm.api.gateway:app --host 0.0.0.0 --port 8002 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 6.2 Nginx Reverse Proxy Configuration
```nginx
# /etc/nginx/sites-available/citadel-gateway
server {
    listen 80;
    server_name 192.168.10.29;
    
    # Standard endpoints
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Streaming endpoints with special configuration
    location ~ ^/v1/(voice|copilot|gui|agents) {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streaming-specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
        
        # Enable chunked transfer encoding
        chunked_transfer_encoding on;
        
        # Disable proxy buffering for real-time streaming
        proxy_request_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

## Phase 7: Testing Implementation

### 7.1 Agent Streaming Test Suite
```python
# /opt/citadel/src/tests/integration/test_agent_streaming.py
# [Full test implementation from provided code]
```

### 7.2 Performance Validation Test
```python
# /opt/citadel/src/tests/performance/test_cache.py
# [Cache performance test from provided code]
```

### 7.3 Health Check Test
```python
# /opt/citadel/src/tests/integration/test_health_checks.py
import pytest
import httpx
import asyncio

@pytest.mark.asyncio
async def test_gateway_health():
    """Test gateway health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://192.168.10.29:8002/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] in ["ok", "degraded"]
        assert "services" in health_data
        
        services = health_data["services"]
        assert "sql_database" in services
        assert "redis" in services
        assert "ollama" in services

@pytest.mark.asyncio
async def test_agent_endpoints_availability():
    """Test that all agent endpoints are available."""
    endpoints = [
        "/v1/voice/chat/completions",
        "/v1/copilot/completions", 
        "/v1/gui/chat/completions",
        "/v1/agents/stream"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            # Test OPTIONS request (CORS preflight)
            response = await client.options(f"http://192.168.10.29:8002{endpoint}")
            assert response.status_code in [200, 405]  # 405 is acceptable for OPTIONS
```

## Phase 8: Deployment Process

### 8.1 Pre-deployment Checklist
```bash
# Verify all services are running
sudo systemctl status postgresql
sudo systemctl status redis-server  
sudo systemctl status ollama

# Test database connectivity
psql -h localhost -U citadel -d citadel_gateway -c "SELECT version();"

# Test Redis connectivity
redis-cli ping

# Test Ollama models
ollama list

# Verify Python environment
source /opt/citadel/citadel_venv/bin/activate
python -c "import fastapi, httpx, asyncpg, redis; print('All dependencies OK')"
```

### 8.2 Application Deployment
```bash
# Deploy source code
cd /opt/citadel
source citadel_venv/bin/activate

# Set environment variables
export CITADEL_ENV=production
export PYTHONPATH=/opt/citadel/src

# Initialize database tables
python -c "
import asyncio
import sys
sys.path.append('/opt/citadel/src')
from citadel_llm.utils.config import load_config, get_database_config
from citadel_llm.services.sql_service import sql_service

async def init_db():
    config = load_config()
    await sql_service.initialize(config)
    await sql_service.create_tables()
    print('Database initialized successfully')

asyncio.run(init_db())
"

# Test gateway import
python -c "
import sys
sys.path.append('/opt/citadel/src')
from citadel_llm.api.gateway import app
print('✅ Gateway imported successfully')
"
```

### 8.3 Service Startup
```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable citadel-gateway
sudo systemctl start citadel-gateway

# Check service status
sudo systemctl status citadel-gateway

# View logs
sudo journalctl -u citadel-gateway -f

# Enable Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## Phase 9: Validation and Testing

### 9.1 Endpoint Validation
```bash
# Test health endpoint
curl http://192.168.10.29:8002/health

# Test metrics endpoint
curl http://192.168.10.29:8002/metrics

# Test enterprise (non-streaming) endpoint
curl -X POST http://192.168.10.29:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'

# Test voice agent streaming endpoint
curl -X POST http://192.168.10.29:8002/v1/voice/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3", 
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "max_tokens": 50
  }'

# Test GUI agent streaming endpoint
curl -X POST http://192.168.10.29:8002/v1/gui/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "messages": [{"role": "user", "content": "Explain AI"}],
    "max_tokens": 100
  }'

# Test Copilot agent streaming endpoint
curl -X POST http://192.168.10.29:8002/v1/copilot/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "prompt": "def fibonacci(n):\n    ",
    "max_tokens": 100
  }'
```

### 9.2 Performance Testing
```bash
# Run cache performance test
cd /opt/citadel
source citadel_venv/bin/activate
python src/tests/performance/test_cache.py

# Run agent streaming tests
python src/tests/integration/test_agent_streaming.py

# Run health check tests
pytest src/tests/integration/test_health_checks.py -v
```

### 9.3 Load Testing
```bash
# Install Apache Bench for load testing
sudo apt install apache2-utils

# Test non-streaming endpoint under load
ab -n 100 -c 10 -T application/json -p /tmp/test_payload.json \
   http://192.168.10.29:8002/v1/chat/completions

# Create test payload
cat > /tmp/test_payload.json << EOF
{
  "model": "phi3",
  "messages": [{"role": "user", "content": "Hello"}],
  "max_tokens": 20
}
EOF
```

## Phase 10: Monitoring and Maintenance

### 10.1 Log Monitoring Setup
```bash
# Create log rotation configuration
sudo tee /etc/logrotate.d/citadel-gateway << EOF
/opt/citadel/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 citadel citadel
}
EOF

# Setup log monitoring script
cat > /opt/citadel/bin/monitor-logs.sh << 'EOF'
#!/bin/bash
# Monitor gateway logs for errors
tail -f /var/log/syslog | grep citadel-gateway | while read line; do
    if echo "$line" | grep -i error; then
        echo "$(date): ERROR detected in gateway logs: $line" >> /opt/citadel/logs/error-alerts.log
    fi
done
EOF

chmod +x /opt/citadel/bin/monitor-logs.sh
```

### 10.2 Health Monitoring
```bash
# Create health check script
cat > /opt/citadel/bin/health-check.sh << 'EOF'
#!/bin/bash
# Comprehensive health check script

echo "=== Citadel Gateway Health Check ==="
echo "Timestamp: $(date)"

# Check service status
echo "Gateway Service Status:"
systemctl is-active citadel-gateway

# Check HTTP endpoint
echo "HTTP Health Check:"
curl -s http://localhost:8002/health | jq .status 2>/dev/null || echo "FAILED"

# Check database
echo "Database Health:"
sudo -u citadel psql -h localhost -U citadel -d citadel_gateway -c "SELECT 1;" > /dev/null 2>&1 && echo "OK" || echo "FAILED"

# Check Redis
echo "Redis Health:"
redis-cli ping 2>/dev/null || echo "FAILED"

# Check Ollama
echo "Ollama Health:"
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "OK" || echo "FAILED"

# Check disk space
echo "Disk Usage:"
df -h /opt/citadel | tail -1

# Check memory usage
echo "Memory Usage:"
free -h | grep Mem

echo "=== Health Check Complete ==="
EOF

chmod +x /opt/citadel/bin/health-check.sh

# Add to crontab for regular monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/citadel/bin/health-check.sh >> /opt/citadel/logs/health-check.log 2>&1") | crontab -
```

### 10.3 Backup Strategy
```bash
# Create database backup script
cat > /opt/citadel/bin/backup-database.sh << 'EOF'
#!/bin/bash
# Database backup script

BACKUP_DIR="/opt/citadel/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="citadel_gateway_backup_${DATE}.sql"

mkdir -p "$BACKUP_DIR"

echo "Creating database backup: $BACKUP_FILE"
pg_dump -h localhost -U citadel citadel_gateway > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
EOF

chmod +x /opt/citadel/bin/backup-database.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/citadel/bin/backup-database.sh >> /opt/citadel/logs/backup.log 2>&1") | crontab -
```

## Phase 11: Security Configuration

### 11.1 Firewall Setup
```bash
# Configure UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow gateway port from internal network only
sudo ufw allow from 192.168.10.0/24 to any port 8002

# Allow database connections from localhost only
sudo ufw allow from 127.0.0.1 to any port 5432

# Allow Redis connections from localhost only  
sudo ufw allow from 127.0.0.1 to any port 6379

# Allow Ollama connections from localhost only
sudo ufw allow from 127.0.0.1 to any port 11434

# Show status
sudo ufw status numbered
```

### 11.2 SSL/TLS Configuration (Optional)
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Generate SSL certificate (if domain is available)
# sudo certbot --nginx -d your-domain.com

# For internal use, create self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/citadel-gateway.key \
    -out /etc/ssl/certs/citadel-gateway.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.10.29"

# Update Nginx configuration for HTTPS
sudo tee /etc/nginx/sites-available/citadel-gateway-ssl << EOF
server {
    listen 443 ssl;
    server_name 192.168.10.29;
    
    ssl_certificate /etc/ssl/certs/citadel-gateway.crt;
    ssl_certificate_key /etc/ssl/private/citadel-gateway.key;
    
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    server_name 192.168.10.29;
    return 301 https://\$server_name\$request_uri;
}
EOF

sudo ln -sf /etc/nginx/sites-available/citadel-gateway-ssl /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Phase 12: Documentation and Handover

### 12.1 Operational Documentation
```markdown
# /opt/citadel/documentation/operations/README.md

# Citadel Gateway Operations Guide

## Service Management
- Start: `sudo systemctl start citadel-gateway`
- Stop: `sudo systemctl stop citadel-gateway`
- Restart: `sudo systemctl restart citadel-gateway`
- Status: `sudo systemctl status citadel-gateway`
- Logs: `sudo journalctl -u citadel-gateway -f`

## Health Checks
- Manual: `/opt/citadel/bin/health-check.sh`
- HTTP: `curl http://192.168.10.29:8002/health`
- Metrics: `curl http://192.168.10.29:8002/metrics`

## Troubleshooting
1. Check service status
2. Review logs
3. Verify database connection
4. Check Redis status
5. Verify Ollama models

## Agent Endpoints
- Voice: `/v1/voice/chat/completions` (real-time streaming)
- Copilot: `/v1/copilot/completions` (IDE integration)
- GUI: `/v1/gui/chat/completions` (chat interfaces)
- Generic: `/v1/agents/stream?agent_type=X`

## Enterprise Endpoints
- Chat: `/v1/chat/completions` (non-streaming, full audit)
- Completions: `/v1/completions` (non-streaming)
- Embeddings: `/api/embeddings` (cached, 221x speedup)
```

### 12.2 API Documentation
```markdown
# /opt/citadel/documentation/api/README.md

# Citadel Gateway API Documentation

## Base URL
- HTTP: `http://192.168.10.29:8002`
- HTTPS: `https://192.168.10.29` (if SSL configured)

## Authentication
Currently no authentication required (internal network only).

## Rate Limiting
No rate limiting implemented (controlled by network access).

## Supported Models
- phi3
- openchat  
- mixtral
- nous-hermes2-mixtral
- nomic-embed-text

## Agent-Specific Endpoints

### Voice Agent Streaming
Real-time streaming optimized for voice synthesis.

**Endpoint:** `POST /v1/voice/chat/completions`
**Features:**
- 1 token chunks for immediate response
- 30-second timeout for quick interactions
- Minimal buffering for low latency

### Copilot Agent Streaming  
Streaming optimized for IDE code completion.

**Endpoint:** `POST /v1/copilot/completions`
**Features:**
- 5 token chunks for smooth code appearance
- 60-second timeout for complex generation
- Code-aware formatting

### GUI Agent Streaming
Streaming optimized for chat interfaces.

**Endpoint:** `POST /v1/gui/chat/completions`
**Features:**
- 10 token chunks for UI efficiency
- 120-second timeout for comprehensive responses
- Chat-optimized formatting

## Enterprise Endpoints

### Non-Streaming Chat
Complete response with full audit logging.

**Endpoint:** `POST /v1/chat/completions`
**Features:**
- Complete conversation logging
- Response caching
- Enterprise audit trail

### Cached Embeddings
High-performance embeddings with Redis caching.

**Endpoint:** `POST /api/embeddings`
**Features:**
- 221x cache speedup
- 1-hour cache TTL
- Automatic cache management
```

## Conclusion

This implementation specification provides a complete roadmap for deploying the enhanced Citadel API Gateway with agent-specific streaming capabilities on HX-Server-02. The system provides:

### ✅ Dual-Mode Architecture
- **Streaming endpoints** for real-time agent experiences
- **Enterprise endpoints** for audit and compliance
- **Unified monitoring** across all endpoints

### ✅ Agent Optimizations
- **Voice agents**: 1-token streaming, 30s timeout
- **Copilot integration**: 5-token chunks, 60s timeout  
- **GUI applications**: 10-token chunks, 120s timeout
- **Generic agents**: Configurable parameters

### ✅ Enterprise Features
- **PostgreSQL logging**: Complete conversation audit trail
- **Redis caching**: 221x performance improvement
- **Prometheus metrics**: Comprehensive monitoring
- **Health checks**: Multi-service status monitoring

### ✅ Production Readiness
- **Systemd service**: Automatic startup and monitoring
- **Nginx proxy**: Load balancing and SSL termination
- **Security**: Firewall configuration and access control
- **Monitoring**: Health checks, logging, and alerting
- **Maintenance**: Backup strategy and log rotation

The implementation maintains backward compatibility with existing OpenAI-compatible clients while enabling new streaming capabilities for modern agent applications including voice assistants, Copilot-Kit integration, and interactive GUI applications.
