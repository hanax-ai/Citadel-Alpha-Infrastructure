# HANA-X Vector Database Shared Library

**Unified API Gateway & External Model Integration Library**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

The HXP Vector Database Shared Library provides a comprehensive Python SDK for interacting with the Citadel AI Infrastructure Program's Vector Database Server. This library enables seamless integration with Qdrant vector database operations and external AI model connectivity. Note: Embedded AI models are deployed on the Orchestration Server, not the Vector Database Server.

### Key Features

- **Unified API Gateway**: Single entry point for REST, GraphQL, and gRPC protocols
- **Orchestration Server Integration**: Integration with embedded AI models deployed on the Orchestration Server
- **GPU-Accelerated Vector Operations**: High-performance vector operations with dual GPU accelerations and metadata management
- **Performance Optimization**: Caching, load balancing, and batch processing
- **Service Orchestration**: Coordinated service management and health monitoring
- **CLI Tools**: Comprehensive command-line interface for management operations
- **Migration System**: Database schema evolution and version control

## Quick Start

### Installation

```bash
pip install hana-x-vector-shared
```

### Basic Usage

```python
from hana_x_vector import VectorDatabase, APIGateway
from hana_x_vector.external_models import ExternalModelRegistry

# Initialize components
db = VectorDatabase(config_path="config.yaml")
gateway = APIGateway(db)
models = ExternalModelRegistry()

# Start services
await gateway.start()
await models.initialize_all()
```

### External Model Integration

```python
from hana_x_vector.external_models import ExternalModelRegistry

# Initialize external model registry
model_registry = ExternalModelRegistry()

# Call external AI model
response = await model_registry.call_model(
    model_id="mixtral-8x7b",
    request_data={
        "text": "Generate embeddings for this text",
        "task": "embedding"
    }
)

print(f"Model response: {response}")
```

### CLI Usage

```bash
# Initialize database
hana-x-db init --config config.yaml

# Run migrations
hana-x-migrate up

# Check system health
hana-x-health check --all

# Manage models
hana-x-models list --type external
```

## Architecture

This library implements the comprehensive architecture defined in Project 2, providing:

- **Core Vector Operations**: CRUD operations, embedding generation, collection management
- **Unified API Gateway**: Multi-protocol support with intelligent routing
- **External Model Integration**: Real-time, hybrid, and bulk processing patterns
- **Service Orchestration**: Dependency management and health monitoring
- **Performance Optimization**: Caching, load balancing, and batch processing

## Documentation

- [Full Documentation](docs/HXP-Vector-Database-Shared-Library.md)
- [API Reference](docs/api-reference.md)
- [CLI Guide](docs/cli-guide.md)
- [Migration Guide](docs/migration-guide.md)

## Development

### Setup Development Environment

```bash
git clone https://github.com/citadel-ai/hana-x-vector-shared.git
cd hana-x-vector-shared
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact the Citadel AI Team at dev@citadel-ai.com or create an issue in the repository.
