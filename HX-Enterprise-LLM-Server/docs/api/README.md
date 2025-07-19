# API Reference - HXP-Enterprise LLM Server

[![API Coverage](https://img.shields.io/badge/API%20Coverage-100%25-brightgreen.svg)](https://github.com/manus-ai/hxp-enterprise-llm)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/manus-ai/hxp-enterprise-llm)

Complete API reference documentation for the HXP-Enterprise LLM Server modular architecture library. This documentation provides comprehensive API references for all service modules, configuration management, testing frameworks, orchestration logic, and integration services.

## 📚 API Documentation Overview

### **API Categories**

| Category | Description | Coverage | Status |
|----------|-------------|----------|--------|
| **[Service APIs](services/README.md)** | AI model services and infrastructure services | 100% | ✅ Complete |
| **[Configuration APIs](configuration/README.md)** | Configuration management and validation | 100% | ✅ Complete |
| **[Testing APIs](testing/README.md)** | Testing frameworks and utilities | 100% | ✅ Complete |
| **[Orchestration APIs](orchestration/README.md)** | Deployment and operational logic | 100% | ✅ Complete |
| **[Integration APIs](integration/README.md)** | External service integrations | 100% | ✅ Complete |

## 🚀 Quick Start

### **API Authentication**
All APIs use standard authentication mechanisms:

```python
# API Key Authentication
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

# Basic Authentication
headers = {
    "Authorization": "Basic base64(username:password)",
    "Content-Type": "application/json"
}
```

### **API Base URLs**
```python
# Development Environment
BASE_URL = "http://localhost:8000"

# Production Environment
BASE_URL = "https://api.hxp-enterprise-llm.com"

# Service-Specific Endpoints
MIXTRAL_URL = "http://localhost:11400"
HERMES_URL = "http://localhost:11401"
OPENCHAT_URL = "http://localhost:11402"
PHI3_URL = "http://localhost:11403"
```

### **Common Response Format**
```python
# Success Response
{
    "status": "success",
    "data": {
        "result": "API response data",
        "metadata": {
            "timestamp": "2025-01-18T10:30:00Z",
            "request_id": "req_123456789"
        }
    }
}

# Error Response
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": "Additional error details"
    },
    "metadata": {
        "timestamp": "2025-01-18T10:30:00Z",
        "request_id": "req_123456789"
    }
}
```

## 📋 API Reference Index

### **1. Service APIs**
- **[AI Model Services](services/ai-models/README.md)**
  - [Mixtral-8x7B Service](services/ai-models/mixtral.md)
  - [Hermes-2 Service](services/ai-models/hermes.md)
  - [OpenChat-3.5 Service](services/ai-models/openchat.md)
  - [Phi-3-Mini Service](services/ai-models/phi3.md)

- **[Infrastructure Services](services/infrastructure/README.md)**
  - [API Gateway](services/infrastructure/api-gateway.md)
  - [Monitoring Service](services/infrastructure/monitoring.md)
  - [Configuration Service](services/infrastructure/configuration.md)
  - [Storage Service](services/infrastructure/storage.md)

### **2. Configuration APIs**
- **[Configuration Management](configuration/README.md)**
  - [Configuration Manager](configuration/manager.md)
  - [Configuration Validator](configuration/validator.md)
  - [Configuration Loader](configuration/loader.md)
  - [Environment Management](configuration/environment.md)
  - [Secret Management](configuration/secrets.md)

### **3. Testing APIs**
- **[Testing Frameworks](testing/README.md)**
  - [Component Testing](testing/component/README.md)
  - [Integration Testing](testing/integration/README.md)
  - [Performance Testing](testing/performance/README.md)
  - [Security Testing](testing/security/README.md)

### **4. Orchestration APIs**
- **[Deployment Orchestration](orchestration/README.md)**
  - [Service Deployment](orchestration/deployment/service.md)
  - [Model Deployment](orchestration/deployment/model.md)
  - [Monitoring Deployment](orchestration/deployment/monitoring.md)

- **[Operational Orchestration](orchestration/operational/README.md)**
  - [Health Checks](orchestration/operational/health-checks.md)
  - [Metrics Exporters](orchestration/operational/metrics.md)
  - [Lifecycle Management](orchestration/operational/lifecycle.md)

### **5. Integration APIs**
- **[Database Integration](integration/database/README.md)**
  - [PostgreSQL Connector](integration/database/postgresql.md)
  - [Connection Pooling](integration/database/connection-pool.md)
  - [Query Builder](integration/database/query-builder.md)

- **[Vector Database Integration](integration/vector-database/README.md)**
  - [Qdrant Connector](integration/vector-database/qdrant.md)
  - [Vector Operations](integration/vector-database/operations.md)
  - [Similarity Search](integration/vector-database/search.md)

- **[Cache Integration](integration/cache/README.md)**
  - [Redis Connector](integration/cache/redis.md)
  - [Cache Management](integration/cache/management.md)
  - [Session Management](integration/cache/session.md)

- **[Metrics Integration](integration/metrics/README.md)**
  - [Prometheus Connector](integration/metrics/prometheus.md)
  - [Grafana Connector](integration/metrics/grafana.md)
  - [Alert Manager](integration/metrics/alertmanager.md)

## 🔧 API Usage Examples

### **Basic Service Usage**
```python
from hxp_enterprise_llm.services.ai_models.mixtral import MixtralService
from hxp_enterprise_llm.schemas.requests import CompletionRequest

# Initialize service
service = MixtralService()

# Create request
request = CompletionRequest(
    prompt="Hello, how are you?",
    max_tokens=100,
    temperature=0.7
)

# Get completion
response = await service.complete(request)
print(response.completion)
```

### **Configuration Management**
```python
from hxp_enterprise_llm.services.infrastructure.configuration import ConfigurationManager

# Initialize configuration manager
config_manager = ConfigurationManager()

# Load configuration
config = await config_manager.load_config("production")

# Get service configuration
service_config = config.get_service_config("mixtral")
print(service_config.port)  # 11400
```

### **Testing Framework Usage**
```python
from hxp_enterprise_llm.testing.component.ai_model_tests import MixtralTestSuite

# Initialize test suite
test_suite = MixtralTestSuite()

# Run performance tests
results = await test_suite.run_performance_tests()
print(f"Average latency: {results.avg_latency}ms")
```

## 📊 API Performance Metrics

### **Response Time Targets**
| Service | Average Latency | 95th Percentile | 99th Percentile |
|---------|----------------|-----------------|-----------------|
| Mixtral-8x7B | 2000ms | 3000ms | 5000ms |
| Hermes-2 | 1500ms | 2500ms | 4000ms |
| OpenChat-3.5 | 1000ms | 2000ms | 3000ms |
| Phi-3-Mini | 800ms | 1500ms | 2500ms |
| API Gateway | 100ms | 200ms | 500ms |

### **Throughput Targets**
| Service | Requests/Second | Concurrent Users | Batch Size |
|---------|----------------|-----------------|------------|
| Mixtral-8x7B | 10 | 50 | 8K tokens |
| Hermes-2 | 15 | 75 | 4K tokens |
| OpenChat-3.5 | 25 | 100 | 2K tokens |
| Phi-3-Mini | 30 | 150 | 1K tokens |
| API Gateway | 1000 | 1000 | N/A |

## 🛡️ API Security

### **Authentication Methods**
- **API Key Authentication**: Primary authentication method
- **OAuth 2.0**: For third-party integrations
- **JWT Tokens**: For session-based authentication
- **Basic Authentication**: For internal services

### **Authorization Levels**
- **Public**: Read-only access to public APIs
- **User**: Standard user access with rate limiting
- **Admin**: Administrative access with full permissions
- **System**: Internal system access for service-to-service communication

### **Rate Limiting**
```python
# Rate Limiting Configuration
RATE_LIMITS = {
    "public": {"requests_per_minute": 60},
    "user": {"requests_per_minute": 300},
    "admin": {"requests_per_minute": 1000},
    "system": {"requests_per_minute": 10000}
}
```

## 🔍 API Error Handling

### **Error Codes**
| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `AUTHENTICATION_FAILED` | Invalid authentication credentials | 401 |
| `AUTHORIZATION_FAILED` | Insufficient permissions | 403 |
| `RESOURCE_NOT_FOUND` | Requested resource not found | 404 |
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |
| `INTERNAL_ERROR` | Internal server error | 500 |

### **Error Response Format**
```python
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": {
            "field": "prompt",
            "issue": "Field is required"
        }
    },
    "metadata": {
        "timestamp": "2025-01-18T10:30:00Z",
        "request_id": "req_123456789",
        "correlation_id": "corr_987654321"
    }
}
```

## 📈 API Versioning

### **Version Strategy**
- **Major Version**: Breaking changes (v1.0.0 → v2.0.0)
- **Minor Version**: New features (v1.0.0 → v1.1.0)
- **Patch Version**: Bug fixes (v1.0.0 → v1.0.1)

### **Version Compatibility**
| API Version | Status | Deprecation Date | End of Life |
|-------------|--------|------------------|-------------|
| v3.0.0 | ✅ Current | - | - |
| v2.0.0 | ⚠️ Deprecated | 2025-06-30 | 2025-12-31 |
| v1.0.0 | ❌ End of Life | 2024-12-31 | 2024-12-31 |

### **Version Migration**
```python
# Version-specific API calls
# v3.0.0
response = await service.complete_v3(request)

# v2.0.0 (deprecated)
response = await service.complete_v2(request)

# v1.0.0 (end of life)
response = await service.complete_v1(request)
```

## 🔧 API Development Tools

### **OpenAPI/Swagger Documentation**
- **Interactive Documentation**: [API Explorer](https://api.hxp-enterprise-llm.com/docs)
- **OpenAPI Specification**: [openapi.json](https://api.hxp-enterprise-llm.com/openapi.json)
- **Postman Collection**: [Download Collection](https://api.hxp-enterprise-llm.com/postman.json)

### **SDK and Client Libraries**
```python
# Python SDK
pip install hxp-enterprise-llm-sdk

# JavaScript SDK
npm install @hxp-enterprise-llm/sdk

# Go SDK
go get github.com/hxp-enterprise-llm/sdk-go
```

### **Testing Tools**
```python
# API Testing Framework
from hxp_enterprise_llm.testing.api import APITestSuite

# Load Testing
from hxp_enterprise_llm.testing.load import LoadTestSuite

# Security Testing
from hxp_enterprise_llm.testing.security import SecurityTestSuite
```

## 📞 API Support

### **Support Channels**
- **Documentation**: [API Documentation](https://docs.hxp-enterprise-llm.com)
- **GitHub Issues**: [Report Issues](https://github.com/manus-ai/hxp-enterprise-llm/issues)
- **Discussions**: [Community Q&A](https://github.com/manus-ai/hxp-enterprise-llm/discussions)
- **Email Support**: [support@hxp-enterprise-llm.com](mailto:support@hxp-enterprise-llm.com)

### **API Status**
- **Status Page**: [API Status](https://status.hxp-enterprise-llm.com)
- **Uptime**: 99.9% uptime guarantee
- **Response Time**: Real-time performance monitoring
- **Incidents**: Live incident updates and notifications

---

**Last Updated:** 2025-01-18  
**API Version:** 3.0.0  
**Documentation Status:** Complete  
**API Coverage:** 100% 