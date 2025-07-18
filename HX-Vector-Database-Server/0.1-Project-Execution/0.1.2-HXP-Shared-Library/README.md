# HANA-X Vector Database Shared Library

A comprehensive Python package for vector database operations with multi-protocol API support, external model integration, and advanced monitoring capabilities.

## Overview

The HANA-X Vector Database Shared Library provides a unified interface for vector database operations using Qdrant as the backend. It supports multiple API protocols (REST, GraphQL, gRPC), external AI model integration, advanced caching, and comprehensive monitoring.

## Architecture

The library is organized into the following layers:

### 🚪 Gateway Layer (`hana_x_vector.gateway`)
- **Unified API Gateway**: Multi-protocol support (REST, GraphQL, gRPC)
- **REST Handler**: FastAPI-based REST endpoints
- **GraphQL Handler**: Strawberry GraphQL implementation
- **gRPC Handler**: High-performance gRPC service
- **Middleware**: Authentication, validation, caching, rate limiting

### ⚡ Vector Operations Layer (`hana_x_vector.vector_ops`)
- **Operations Manager**: Core vector CRUD operations
- **Search Engine**: Advanced similarity search with multiple algorithms
- **Batch Processor**: High-performance batch operations
- **Cache Manager**: Redis-based caching with multiple strategies

### 🗄️ Qdrant Integration Layer (`hana_x_vector.qdrant`)
- **Client Wrapper**: Optimized Qdrant client with retry logic
- **Collections Manager**: Collection lifecycle management
- **Index Optimizer**: Automatic index optimization
- **Configuration Manager**: Connection and performance tuning

### 🤖 External Models Layer (`hana_x_vector.external_models`)
- **Integration Patterns**: Real-time, hybrid, bulk, streaming patterns
- **Model Clients**: HTTP clients for 9 external AI models
- **Connection Pool**: Efficient connection management

### 📊 Monitoring Layer (`hana_x_vector.monitoring`)
- **Metrics Collector**: Prometheus metrics integration
- **Health Monitor**: Comprehensive health checks
- **Structured Logger**: JSON-based operational logging

### 🛠️ Utilities Layer (`hana_x_vector.utils`)
- **Configuration Manager**: Environment-based configuration
- **Custom Exceptions**: Comprehensive error handling
- **Validators**: Data validation utilities

### 📋 Schemas Layer (`hana_x_vector.schemas`)
- **GraphQL Schemas**: Type definitions and resolvers
- **REST Models**: Pydantic models for validation
- **gRPC Schemas**: Protocol buffer definitions

## Installation

### Prerequisites
- Python 3.12+
- Redis server (for caching)
- Qdrant vector database
- External AI model servers (optional)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file or set environment variables:

```bash
# Qdrant Configuration
HANA_X_QDRANT_HOST=192.168.10.30
HANA_X_QDRANT_PORT=6333
HANA_X_QDRANT_GRPC_PORT=6334

# Cache Configuration
HANA_X_CACHE_HOST=192.168.10.35
HANA_X_CACHE_PORT=6379

# External Models Configuration
HANA_X_MODELS_SERVER_1=192.168.10.32
HANA_X_MODELS_SERVER_2=192.168.10.33
HANA_X_MODELS_PORT=11400

# API Gateway Configuration
HANA_X_API_HOST=0.0.0.0
HANA_X_API_PORT=8000
HANA_X_API_WORKERS=4

# Monitoring Configuration
HANA_X_LOG_LEVEL=INFO
HANA_X_METRICS_PORT=9090
```

## Quick Start

### Basic Usage
```python
from hana_x_vector import VectorOperationsManager, ConfigManager

# Initialize configuration
config = ConfigManager()

# Create vector operations manager
vector_ops = VectorOperationsManager(config.get_all_config())

# Insert vectors
await vector_ops.insert_vector(
    collection="documents",
    vector_id="doc_001",
    vector=[0.1, 0.2, 0.3, 0.4],
    payload={"title": "Example Document"}
)

# Search vectors
results = await vector_ops.search_vectors(
    collection="documents",
    query_vector=[0.1, 0.2, 0.3, 0.4],
    limit=10
)
```

### API Gateway Usage
```python
from hana_x_vector.gateway import UnifiedAPIGateway

# Initialize API gateway
gateway = UnifiedAPIGateway(config.get_all_config())

# Start all protocols
await gateway.startup()

# Gateway now serves:
# - REST API on http://localhost:8000
# - GraphQL on http://localhost:8000/graphql
# - gRPC on localhost:50051
```

### External Model Integration
```python
from hana_x_vector.external_models import IntegrationPatternManager

# Initialize integration manager
integration_manager = IntegrationPatternManager(config.get_all_config())

# Real-time embedding generation
embeddings = await integration_manager.real_time_integration(
    texts=["Hello world", "Vector database"],
    model_name="mixtral"
)
```

## API Endpoints

### REST API
- `POST /vectors/{collection}` - Insert vector
- `GET /vectors/{collection}/search` - Search vectors
- `PUT /vectors/{collection}/{id}` - Update vector
- `DELETE /vectors/{collection}/{id}` - Delete vector
- `POST /vectors/{collection}/batch` - Batch operations
- `GET /collections` - List collections
- `POST /collections` - Create collection
- `GET /health` - Health status

### GraphQL API
Access GraphQL playground at `http://localhost:8000/graphql`

Example query:
```graphql
query {
  search(collection: "documents", query: {
    vector: [0.1, 0.2, 0.3, 0.4]
    limit: 10
  }) {
    results {
      id
      score
      payload
    }
    totalCount
    queryTime
  }
}
```

### gRPC API
Protocol buffer definitions available in `schemas/grpc_schemas.py`

## Configuration

### Collection Configuration
```python
collection_config = {
    "vector_size": 384,
    "distance": "cosine",
    "shard_number": 1,
    "replication_factor": 1,
    "hnsw_config": {
        "m": 16,
        "ef_construct": 100,
        "full_scan_threshold": 10000
    }
}
```

### Performance Tuning
```python
performance_config = {
    "max_batch_size": 10000,
    "max_concurrent_requests": 100,
    "search_timeout": 10.0,
    "cache_warming_enabled": True,
    "connection_pool_size": 50
}
```

## Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
```

### Metrics
Prometheus metrics available at `http://localhost:9090/metrics`

Key metrics:
- `vector_operations_total` - Total vector operations
- `search_duration_seconds` - Search latency
- `cache_hit_ratio` - Cache effectiveness
- `external_model_requests_total` - External model usage

### Logging
Structured JSON logging with request correlation:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Vector operation completed",
  "operation": "search",
  "collection": "documents",
  "duration": 0.005,
  "request_id": "req_123"
}
```

## External Model Support

Supported models across two LLM servers:
- **Server 1 (192.168.10.32)**: mixtral, hermes, llama, qwen, codellama
- **Server 2 (192.168.10.33)**: phi, claude, gemma, mistral

Integration patterns:
- **Real-time**: Immediate embedding generation
- **Hybrid**: Cached + real-time fallback
- **Bulk**: Batch processing for large datasets
- **Streaming**: Continuous processing pipeline

## Security

### Authentication
- API key authentication
- IP allowlist support
- Request validation middleware

### R&D Environment Configuration
```python
security_config = {
    "auth_enabled": True,
    "api_keys": ["dev-key-001", "test-key-002"],
    "ip_allowlist": ["192.168.10.0/24", "127.0.0.1"],
    "rate_limit_requests": 1000,
    "rate_limit_window": 60
}
```

## Development

### Testing
```bash
pytest tests/ -v --cov=hana_x_vector
```

### Code Quality
```bash
black hana_x_vector/
flake8 hana_x_vector/
mypy hana_x_vector/
```

### Documentation
```bash
sphinx-build -b html docs/ docs/_build/
```

## Performance Benchmarks

Expected performance characteristics:
- **Vector Search**: <10ms average latency
- **API Gateway**: <5ms overhead
- **Throughput**: >10,000 operations/second
- **Cache Hit Ratio**: >80% for repeated queries

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify Qdrant server is running on 192.168.10.30:6333
   - Check Redis server availability on 192.168.10.35:6379

2. **Performance Issues**
   - Adjust batch sizes based on vector dimensions
   - Enable cache warming for frequently accessed collections
   - Optimize HNSW parameters for your use case

3. **External Model Errors**
   - Verify model servers are accessible
   - Check connection pool configuration
   - Monitor timeout settings

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow the coding standards in `HXP-Gov-Coding-Standards.md`
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all health checks pass

## License

This software is part of the HANA-X Vector Database Server project and is subject to the project's licensing terms.

## Support

For technical support and documentation, refer to the project documentation in:
- `/home/agent0/Citadel-Alpha-Infrastructure/0.0-Project-Management/`
- `/home/agent0/Citadel-Alpha-Infrastructure/0.1-Project-Execution/0.1.1-HXP-Detailed-Tasks/`
