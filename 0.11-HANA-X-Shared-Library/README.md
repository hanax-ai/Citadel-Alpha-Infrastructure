# HANA-X Shared Library

## Overview

The HANA-X Shared Library provides common utilities, modules, and base components that can be reused across all HANA-X infrastructure projects. This promotes code consistency, reduces duplication, and improves maintainability across the ecosystem.

## Directory Structure

```
0.11-HANA-X-Shared-Library/
├── src/                           # Shared source code
│   ├── common/                    # Common utilities
│   ├── config/                    # Configuration management
│   ├── logging/                   # Logging utilities
│   ├── monitoring/                # Monitoring utilities
│   └── validation/                # Validation utilities
├── tests/                         # Test cases for shared code
├── examples/                      # Usage examples
├── docs/                          # Documentation
└── README.md                      # This file
```

## Available Modules

### Configuration Management
- **Purpose**: Standardized configuration handling across all servers
- **Location**: `src/config/`
- **Usage**: Pydantic-based configuration classes with validation

### Logging Framework
- **Purpose**: Centralized logging with consistent format and rotation
- **Location**: `src/logging/`
- **Usage**: Pre-configured loggers for different components

### Monitoring Utilities
- **Purpose**: Common monitoring and metrics collection
- **Location**: `src/monitoring/`
- **Usage**: GPU monitoring, system metrics, performance tracking

### Validation Tools
- **Purpose**: Input validation and system checks
- **Location**: `src/validation/`
- **Usage**: Hardware validation, configuration verification

## Getting Started

### Using Shared Modules

1. **Import from your project**:
```python
from src.common.utils import SystemValidator
from src.config.base import BaseConfig
from src.logging.logger import get_logger
```

2. **Configure logging**:
```python
logger = get_logger("my-component")
logger.info("Using shared logging framework")
```

3. **Use configuration management**:
```python
config = BaseConfig()
config.validate()
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
| Common Utils | 🔄 Development | 0% | 2025-01-10 |
| Config Management | 🔄 Development | 0% | 2025-01-10 |
| Logging Framework | 🔄 Development | 0% | 2025-01-10 |
| Monitoring Utils | 🔄 Development | 0% | 2025-01-10 |
| Validation Tools | 🔄 Development | 0% | 2025-01-10 |

## Roadmap

### Phase 1: Foundation (Current)
- [ ] Basic configuration management
- [ ] Logging framework
- [ ] Common validation utilities
- [ ] Initial testing framework

### Phase 2: Enhancement
- [ ] Monitoring and metrics collection
- [ ] Performance optimization utilities
- [ ] Error handling framework
- [ ] Documentation automation

### Phase 3: Advanced Features
- [ ] Service discovery utilities
- [ ] Load balancing helpers
- [ ] Security utilities
- [ ] API client libraries

## Usage Examples

### Example 1: System Validation
```python
from src.validation.hardware import GPUValidator, MemoryValidator

# Validate GPU requirements
gpu_validator = GPUValidator(min_gpus=2, min_vram_gb=30)
if gpu_validator.validate():
    print("GPU requirements met")

# Validate memory requirements  
memory_validator = MemoryValidator(min_memory_gb=125)
if memory_validator.validate():
    print("Memory requirements met")
```

### Example 2: Configuration Management
```python
from src.config.vllm import VLLMConfig

# Load enterprise model configuration
config = VLLMConfig()
config.load_enterprise_models()
args = config.get_vllm_args()
```

### Example 3: Logging
```python
from src.logging.logger import setup_logging, get_logger

# Setup centralized logging
setup_logging(log_level="INFO", log_dir="/opt/citadel/logs")

# Get component-specific logger
logger = get_logger("vllm-server")
logger.info("Server starting...")
```

## Integration with Projects

### Enterprise Server (0.1)
- Configuration management for enterprise models
- Logging for business-critical operations  
- GPU validation for enterprise workloads

### LoB Server (0.2)
- Shared configuration templates
- Common monitoring utilities
- Validation frameworks

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
