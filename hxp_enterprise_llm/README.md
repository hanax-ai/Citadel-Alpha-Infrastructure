cd ls
# HXP-Enterprise LLM Server Modular Architecture Library

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A comprehensive modular architecture library for enterprise-grade LLM server implementation, providing service-aligned modularity, isolated testing suites, and reusable orchestration logic.

## 🏗️ Architecture Overview

The HXP-Enterprise LLM Server Modular Architecture Library follows a **service-aligned modular design** that provides:

- **Service-Aligned Modularity**: Each module corresponds directly to architectural components
- **Isolated Testing Architecture**: Dedicated testing suites for each infrastructure component
- **Reusable Orchestration Logic**: Standardized deployment and operational patterns
- **Architectural Traceability**: Direct mapping between modules and architecture

## 📦 Package Structure

```
hxp_enterprise_llm/
├── services/                           # Service-Aligned Modules
│   ├── ai_models/                      # AI Model Services
│   │   ├── mixtral/                    # Mixtral-8x7B Service Module
│   │   ├── hermes/                     # Hermes-2 Service Module
│   │   ├── openchat/                   # OpenChat-3.5 Service Module
│   │   └── phi3/                       # Phi-3-Mini Service Module
│   ├── infrastructure/                 # Infrastructure Services
│   │   ├── api_gateway/                # API Gateway Service Module
│   │   ├── monitoring/                 # Monitoring Service Module
│   │   ├── configuration/              # Configuration Service Module
│   │   └── storage/                    # Storage Service Module
│   └── integration/                    # Integration Services
│       ├── database/                   # Database Integration Module
│       ├── vector_database/            # Vector Database Integration Module
│       ├── cache/                      # Cache Integration Module
│       └── metrics/                    # Metrics Integration Module
├── core/                               # Core Framework
│   ├── base_classes/                   # Base Service Classes
│   ├── exceptions/                     # Custom Exceptions
│   └── constants/                      # Constants and Enums
├── schemas/                            # Global Schemas
│   ├── common/                         # Common Schemas
│   ├── api/                            # API Schemas
│   └── configuration/                  # Configuration Schemas
├── utilities/                          # Utility Frameworks
│   ├── logging/                        # Logging Framework
│   ├── configuration/                  # Configuration Management
│   ├── validation/                     # Validation Utilities
│   └── testing/                        # Testing Utilities
└── orchestration/                      # Reusable Orchestration Logic
    ├── deployment/                     # Deployment Scaffolds
    ├── operational/                    # Operational Logic
    └── utilities/                      # Orchestration Utilities
```

## 🚀 Quick Start

### Installation

```bash
# Install the core package
pip install hxp-enterprise-llm

# Install with AI model dependencies
pip install hxp-enterprise-llm[ai]

# Install with monitoring dependencies
pip install hxp-enterprise-llm[monitoring]

# Install with development dependencies
pip install hxp-enterprise-llm[dev]
```

### Basic Usage

```python
from hxp_enterprise_llm.core.base_classes import BaseAIModelService
from hxp_enterprise_llm.schemas.common import ServiceConfig
from hxp_enterprise_llm.utilities.logging import get_logger

# Initialize a service
logger = get_logger(__name__)

class MyAIService(BaseAIModelService):
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        logger.info("AI Service initialized")

# Use the service
config = ServiceConfig(
    service_name="my-ai-service",
    port=8000,
    host="0.0.0.0"
)
service = MyAIService(config)
```

## 🔧 Configuration

### Environment Variables

```bash
# Service Configuration
HXP_SERVICE_NAME=my-service
HXP_SERVICE_PORT=8000
HXP_SERVICE_HOST=0.0.0.0

# Database Configuration
HXP_DATABASE_HOST=192.168.10.35
HXP_DATABASE_PORT=5433
HXP_DATABASE_NAME=citadel_ai

# Vector Database Configuration
HXP_VECTOR_DB_HOST=192.168.10.30
HXP_VECTOR_DB_PORT=6333

# Monitoring Configuration
HXP_METRICS_HOST=192.168.10.37
HXP_METRICS_PORT=9090
```

### Configuration Files

```yaml
# config.yaml
services:
  ai_models:
    mixtral:
      port: 11400
      memory_limit_gb: 90
      cpu_cores: 8
    hermes:
      port: 11401
      memory_limit_gb: 15
      cpu_cores: 4

infrastructure:
  api_gateway:
    port: 8000
    workers: 4
    timeout: 300

integration:
  database:
    host: "192.168.10.35"
    port: 5433
    connection_pool_size: 20
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m ai
pytest -m infrastructure

# Run with coverage
pytest --cov=hxp_enterprise_llm

# Run performance tests
pytest -m slow
```

### Test Structure

```
tests/
├── unit/                              # Unit Tests
│   ├── test_ai_models/
│   ├── test_infrastructure/
│   └── test_integration/
├── integration/                       # Integration Tests
│   ├── test_cross_service/
│   ├── test_external_apis/
│   └── test_database/
└── performance/                       # Performance Tests
    ├── test_load/
    ├── test_stress/
    └── test_scalability/
```

## 📊 Monitoring and Observability

### Health Checks

```python
from hxp_enterprise_llm.utilities.monitoring import HealthChecker

health_checker = HealthChecker()
status = health_checker.check_service_health()
```

### Metrics Collection

```python
from hxp_enterprise_llm.utilities.metrics import MetricsCollector

metrics = MetricsCollector()
metrics.record_request_latency("ai_inference", 150.0)
metrics.record_request_count("ai_inference", 1)
```

### Logging

```python
from hxp_enterprise_llm.utilities.logging import get_logger

logger = get_logger(__name__)
logger.info("Service started", extra={"service": "ai-model", "port": 8000})
```

## 🔒 Security

### Authentication

```python
from hxp_enterprise_llm.utilities.security import AuthManager

auth_manager = AuthManager()
token = auth_manager.create_access_token(user_id="user123")
```

### Input Validation

```python
from hxp_enterprise_llm.schemas.api import InferenceRequest
from pydantic import ValidationError

try:
    request = InferenceRequest(
        prompt="Hello, world!",
        max_tokens=100,
        temperature=0.7
    )
except ValidationError as e:
    logger.error(f"Invalid request: {e}")
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "hxp_enterprise_llm.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hxp-enterprise-llm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hxp-enterprise-llm
  template:
    metadata:
      labels:
        app: hxp-enterprise-llm
    spec:
      containers:
      - name: hxp-enterprise-llm
        image: hxp-enterprise-llm:latest
        ports:
        - containerPort: 8000
        env:
        - name: HXP_SERVICE_PORT
          value: "8000"
```

## 📚 Documentation

- [API Reference](https://hxp-enterprise-llm.readthedocs.io/api/)
- [Architecture Guide](https://hxp-enterprise-llm.readthedocs.io/architecture/)
- [Deployment Guide](https://hxp-enterprise-llm.readthedocs.io/deployment/)
- [Development Guide](https://hxp-enterprise-llm.readthedocs.io/development/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/manus-ai/hxp-enterprise-llm.git
cd hxp-enterprise-llm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://hxp-enterprise-llm.readthedocs.io/](https://hxp-enterprise-llm.readthedocs.io/)
- **Issues**: [https://github.com/manus-ai/hxp-enterprise-llm/issues](https://github.com/manus-ai/hxp-enterprise-llm/issues)
- **Discussions**: [https://github.com/manus-ai/hxp-enterprise-llm/discussions](https://github.com/manus-ai/hxp-enterprise-llm/discussions)

## 🏢 About

HXP-Enterprise LLM Server Modular Architecture Library is developed by [Manus AI](https://manus.ai) to provide enterprise-grade LLM server implementation with modular architecture, comprehensive testing, and operational excellence.

---

**Built with ❤️ by Manus AI** 