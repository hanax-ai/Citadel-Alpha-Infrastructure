# HANA-X Shared Library

## Overview

The HANA-X Shared Library provides common utilities, modules, and base components that can be reused across all HANA-X infrastructure projects. This promotes code consistency, reduces duplication, and improves maintainability across the ecosystem.

## Directory Structure

```
0.11-HANA-X-Shared-Library/
├── src/                           # Shared source code
│   ├── common/                    # Common utilities (file system, system info, GPU checks)
│   ├── config/                    # Configuration management (Pydantic-based config utilities)
│   ├── logging/                   # Logging utilities (structured logging, server-specific formatters)
│   ├── monitoring/                # Monitoring utilities (performance monitoring, alerting)
│   ├── testing/                   # Testing utilities (base test cases, mocking utilities)
│   └── validation/                # Validation utilities
├── tests/                         # Test cases for shared code
├── examples/                      # Usage examples
├── docs/                          # Documentation
└── README.md                      # This file
```

## Available Modules

### Common Utilities
- **Purpose**: Essential utilities for file system, system info, and GPU checks
- **Location**: `src/common/`
- **Features**: Directory creation, system information, port validation, GPU availability checks
- **Usage**: `from hana_x_shared.common import ensure_directory, get_system_info, check_gpu_availability`

### Configuration Management
- **Purpose**: Standardized configuration handling across all servers
- **Location**: `src/config/`
- **Features**: Pydantic-based config classes, environment variable overrides, validation
- **Usage**: `from hana_x_shared.config import BaseConfigManager, create_server_config`

### Logging Framework
- **Purpose**: Centralized logging with consistent format and rotation
- **Location**: `src/logging/`
- **Features**: Structured logging, server-specific formatters, JSON support, contextual logging
- **Usage**: `from hana_x_shared.logging import create_hana_logger`

### Monitoring Utilities
- **Purpose**: Performance monitoring and metrics collection
- **Location**: `src/monitoring/`
- **Features**: Request tracking, latency monitoring, alerting, percentile calculations
- **Usage**: `from hana_x_shared.monitoring import PerformanceMonitor`

### Testing Utilities
- **Purpose**: Base test cases and mocking utilities
- **Location**: `src/testing/`
- **Features**: Abstract base test classes, mock generators, server-specific test patterns
- **Usage**: `from hana_x_shared.testing import BaseHanaXTestCase`

### Validation Tools
- **Purpose**: Input validation and system checks
- **Location**: `src/validation/`
- **Usage**: Hardware validation, configuration verification

## Getting Started

### Using Shared Modules

1. **Import from your project**:
```python
from hana_x_shared.common import ensure_directory, get_system_info, check_gpu_availability
from hana_x_shared.config import create_server_config, BaseConfigManager
from hana_x_shared.logging import create_hana_logger
from hana_x_shared.monitoring import PerformanceMonitor
from hana_x_shared.testing import BaseHanaXTestCase
```

2. **Configure logging**:
```python
logger = create_hana_logger(
    server_id="enterprise-server-01",
    server_type="enterprise",
    log_level="INFO",
    json_format=True
)
api_logger = logger.get_logger("api")
api_logger.info("Using shared logging framework")
```

3. **Use configuration management**:
```python
server_config = create_server_config(
    name="hx-llm-server-01",
    ip="192.168.10.29",
    port=8000,
    server_id="enterprise-server-01"
)
```

4. **Monitor performance**:
```python
monitor = PerformanceMonitor(server_id="enterprise-server-01")
monitor.record_request(latency_ms=1200.5, success=True)
metrics = monitor.get_metrics()
```

### Contributing New Modules

1. **Create module in appropriate directory**
2. **Add comprehensive tests**
3. **Update documentation**
4. **Add usage examples**

## Module Guidelines

### Code Standards
- Follow PEP 8 style guidelines
- Include type hints
- Add comprehensive docstrings
- Maintain backward compatibility

### Testing Requirements
- Unit tests for all functions
- Integration tests for complex modules
- Test coverage > 80%
- Performance benchmarks where applicable

### Documentation Requirements
- Clear API documentation
- Usage examples
- Performance characteristics
- Dependencies and requirements

## Current Modules Status

| Module | Status | Coverage | Last Updated |
|--------|--------|----------|--------------|
| Common Utils | ✅ Complete | 85% | 2025-01-10 |
| Config Management | ✅ Complete | 90% | 2025-01-10 |
| Logging Framework | ✅ Complete | 88% | 2025-01-10 |
| Monitoring Utils | ✅ Complete | 92% | 2025-01-10 |
| Testing Utils | ✅ Complete | 95% | 2025-01-10 |
| Validation Tools | 🔄 Development | 0% | 2025-01-10 |

## Roadmap

### Phase 1: Foundation (Completed)
- [x] Basic configuration management
- [x] Logging framework
- [x] Common validation utilities
- [x] Initial testing framework
- [x] Performance monitoring utilities
- [x] Base test case abstractions

### Phase 2: Enhancement (Current)
- [x] Monitoring and metrics collection
- [x] Performance optimization utilities
- [x] Error handling framework
- [ ] Documentation automation
- [ ] Advanced validation utilities
- [ ] Model management utilities

### Phase 3: Advanced Features (Planned)
- [ ] Service discovery utilities
- [ ] Load balancing helpers
- [ ] Security utilities
- [ ] API client libraries
- [ ] Deployment automation
- [ ] Health check frameworks

## Usage Examples

### Example 1: System Validation and GPU Checks
```python
from hana_x_shared.common import check_gpu_availability, get_system_info

# Check GPU availability
gpu_info = check_gpu_availability()
if gpu_info['available']:
    print(f"Found {gpu_info['count']} GPUs")
    print(f"Driver version: {gpu_info['driver_version']}")

# Get system information
system_info = get_system_info()
print(f"System: {system_info['system']} {system_info['release']}")
```

### Example 2: Configuration Management
```python
from hana_x_shared.config import create_server_config, create_model_config

# Create server configuration
server_config = create_server_config(
    name="hx-llm-server-01",
    ip="192.168.10.29",
    port=8000,
    server_id="enterprise-server-01",
    description="Enterprise LLM Server"
)

# Create model configuration
model_config = create_model_config(
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
    model_type="mixtral",
    tensor_parallel_size=2,
    max_model_len=32768,
    specialization="enterprise"
)
```

### Example 3: Structured Logging
```python
from hana_x_shared.logging import create_hana_logger

# Create server-specific logger
logger = create_hana_logger(
    server_id="enterprise-server-01",
    server_type="enterprise",
    log_level="INFO",
    json_format=True
)

# Get component logger
api_logger = logger.get_logger("api")
api_logger.info("Server starting...")

# Log API requests
logger.log_api_request(
    method="POST",
    path="/v1/completions",
    status_code=200,
    latency_ms=1250.5
)
```

### Example 4: Performance Monitoring
```python
from hana_x_shared.monitoring import PerformanceMonitor

# Create performance monitor
monitor = PerformanceMonitor(
    server_id="enterprise-server-01",
    history_size=1000
)

# Record request metrics
monitor.record_request(
    latency_ms=1200.5,
    success=True,
    endpoint="/v1/completions"
)

# Set thresholds and get metrics
monitor.set_threshold("average_latency_ms", 2000.0)
metrics = monitor.get_metrics()
print(f"Average latency: {metrics['average_latency_ms']:.2f}ms")
print(f"Success rate: {metrics['success_rate']:.1f}%")
```

### Example 5: Testing Utilities
```python
from hana_x_shared.testing import BaseHanaXTestCase, create_mock_model_response

class EnterpriseServerTestCase(BaseHanaXTestCase):
    def get_server_type(self):
        return "enterprise"
    
    def get_server_config(self):
        return {
            'name': 'hx-llm-server-01',
            'ip': '192.168.10.29',
            'port': 8000,
            'server_id': 'enterprise-server-01'
        }
    
    def get_performance_targets(self):
        return {
            'max_latency_ms': 1500,
            'min_throughput_rps': 15,
            'availability_target': 99.9
        }
    
    def test_model_response(self):
        response = create_mock_model_response(
            model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
            response_text="This is a test response.",
            server_id="enterprise-server-01"
        )
        self.assertEqual(response['model'], "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.assert_model_response_quality(response['choices'][0]['text'])
```

## Integration with Projects

### Enterprise Server (0.1)
- **Configuration Management**: Pydantic-based server and model configurations
- **Logging**: Structured logging with enterprise-specific formatters
- **Monitoring**: Performance tracking with business-critical alerting
- **Testing**: Enterprise-specific test base classes and mocking utilities
- **Common Utils**: GPU validation, system info, and file system utilities

### LoB Server (0.2)
- **Configuration Management**: Development-focused configuration templates
- **Logging**: Debug-friendly logging with code-specific context
- **Monitoring**: Development metrics and performance profiling
- **Testing**: Development-specific test patterns and code quality checks
- **Common Utils**: Shared system validation and development tooling

### Shared Benefits
- **Consistency**: Common patterns and utilities across all servers
- **Maintainability**: Centralized updates and bug fixes
- **Reusability**: Reduce code duplication by 60-80%
- **Testability**: Comprehensive mocking and testing infrastructure
- **Observability**: Unified monitoring and logging across the ecosystem

## Best Practices

1. **Keep modules focused and single-purpose**
2. **Maintain clean interfaces with minimal dependencies**
3. **Provide comprehensive error handling**
4. **Include performance considerations**
5. **Document all public APIs thoroughly**

## Support and Contributions

For questions or contributions:
1. Review existing modules for patterns
2. Follow established coding standards
3. Add comprehensive tests
4. Update documentation
5. Submit for review

---

*This shared library supports the systematic deployment and operation of the HANA-X infrastructure ecosystem.*
