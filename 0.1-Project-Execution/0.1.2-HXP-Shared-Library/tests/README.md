# HANA-X Vector Database Shared Library - Test Suite

This directory contains the comprehensive test suite for the HANA-X Vector Database Shared Library, ensuring reliability, performance, and integration across all components.

## Test Structure

```
tests/
├── README.md                           # This file
├── conftest.py                         # Pytest configuration and fixtures
├── requirements-test.txt               # Test-specific dependencies
├── run_all_tests.sh                   # Master test runner script
├── unit/                              # Unit tests for individual components
│   ├── test_validators.py             # Validation utilities tests
│   ├── test_config.py                 # Configuration management tests
│   ├── test_exceptions.py             # Exception handling tests
│   ├── gateway/                       # API Gateway component tests
│   │   ├── test_api_gateway.py        # Unified API Gateway tests
│   │   ├── test_rest_handler.py       # REST API handler tests
│   │   ├── test_graphql_handler.py    # GraphQL handler tests
│   │   ├── test_grpc_handler.py       # gRPC handler tests
│   │   └── test_middleware.py         # Middleware tests
│   ├── vector_ops/                    # Vector operations tests
│   │   ├── test_operations.py         # Core vector operations
│   │   ├── test_search.py             # Vector search functionality
│   │   ├── test_batch.py              # Batch operations
│   │   └── test_cache.py              # Caching layer tests
│   ├── qdrant/                        # Qdrant integration tests
│   │   ├── test_client.py             # Qdrant client tests
│   │   ├── test_collections.py        # Collection management
│   │   ├── test_indexing.py           # Indexing operations
│   │   └── test_config.py             # Qdrant configuration
│   ├── external_models/               # External model integration tests
│   │   ├── test_client.py             # External model client
│   │   ├── test_embeddings.py         # Embedding generation
│   │   └── test_inference.py          # Model inference
│   ├── monitoring/                    # Monitoring and metrics tests
│   │   ├── test_metrics.py            # Metrics collection
│   │   ├── test_health.py             # Health checks
│   │   └── test_logging.py            # Structured logging
│   └── schemas/                       # Schema validation tests
│       ├── test_rest_models.py        # REST API models
│       ├── test_graphql_schemas.py    # GraphQL schema tests
│       └── test_grpc_schemas.py       # gRPC schema tests
├── integration/                       # Integration tests
│   ├── test_api_gateway_integration.py    # End-to-end API Gateway
│   ├── test_qdrant_integration.py         # Qdrant database integration
│   ├── test_external_models_integration.py # External model integration
│   ├── test_cross_server_communication.py # Cross-server communication
│   └── test_full_pipeline.py              # Complete pipeline tests
├── performance/                       # Performance and load tests
│   ├── test_vector_search_performance.py  # Vector search benchmarks
│   ├── test_api_gateway_performance.py    # API Gateway performance
│   ├── test_batch_operations_performance.py # Batch operation benchmarks
│   └── test_concurrent_operations.py      # Concurrency tests
├── security/                          # Security and validation tests
│   ├── test_authentication.py             # Authentication tests
│   ├── test_authorization.py              # Authorization tests
│   ├── test_input_validation.py           # Input validation tests
│   └── test_api_security.py               # API security tests
├── fixtures/                          # Test data and fixtures
│   ├── sample_vectors.json                # Sample vector data
│   ├── test_collections.json              # Test collection definitions
│   ├── mock_responses.json                # Mock API responses
│   └── performance_datasets/              # Performance test datasets
└── scripts/                           # Test utility scripts
    ├── cross-server-communication-test.sh # Cross-server communication test
    ├── setup_test_environment.sh          # Test environment setup
    ├── cleanup_test_data.sh               # Test data cleanup
    └── generate_test_data.py              # Test data generation
```

## Test Categories

### 1. Unit Tests (`unit/`)
- **Purpose:** Test individual components in isolation
- **Coverage:** All modules, classes, and functions
- **Framework:** pytest with mocking
- **Target:** >95% code coverage

### 2. Integration Tests (`integration/`)
- **Purpose:** Test component interactions and workflows
- **Coverage:** API endpoints, database operations, external integrations
- **Framework:** pytest with real services
- **Target:** All critical user journeys

### 3. Performance Tests (`performance/`)
- **Purpose:** Validate performance requirements
- **Coverage:** Vector search latency, API throughput, concurrent operations
- **Framework:** pytest-benchmark, locust
- **Targets:** <10ms search latency, >10K ops/sec

### 4. Security Tests (`security/`)
- **Purpose:** Validate security controls and input validation
- **Coverage:** Authentication, authorization, input sanitization
- **Framework:** pytest with security-focused assertions
- **Target:** All security requirements validated

## Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
./run_all_tests.sh

# Run specific test category
pytest unit/                    # Unit tests only
pytest integration/             # Integration tests only
pytest performance/             # Performance tests only
pytest security/                # Security tests only
```

### Individual Test Execution
```bash
# Run specific test file
pytest unit/test_validators.py -v

# Run specific test function
pytest unit/test_validators.py::test_validate_vector_data -v

# Run with coverage
pytest --cov=hana_x_vector --cov-report=html

# Run performance tests
pytest performance/ --benchmark-only
```

## Test Configuration

### Environment Variables
```bash
# Test environment configuration
export HANA_X_TEST_MODE=true
export QDRANT_TEST_URL=http://localhost:6333
export REDIS_TEST_URL=redis://localhost:6379
export TEST_DATA_PATH=./fixtures
```

### Test Database Setup
```bash
# Setup test Qdrant instance
docker run -d --name qdrant-test -p 6333:6333 qdrant/qdrant

# Setup test Redis instance
docker run -d --name redis-test -p 6379:6379 redis:alpine
```

## Test Data Management

### Fixtures
- **Vector Data:** Sample vectors for testing search operations
- **Collections:** Test collection configurations
- **Mock Responses:** Predefined API responses for testing
- **Performance Datasets:** Large datasets for performance testing

### Data Generation
```bash
# Generate test vectors
python scripts/generate_test_data.py --vectors 10000 --dimensions 384

# Setup test collections
python scripts/setup_test_environment.py
```

## Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: ./run_all_tests.sh
```

### Quality Gates
- **Unit Tests:** Must pass with >95% coverage
- **Integration Tests:** Must pass all critical workflows
- **Performance Tests:** Must meet latency and throughput targets
- **Security Tests:** Must pass all security validations

## Test Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=hana_x_vector --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=hana_x_vector --cov-report=xml
```

### Performance Reports
```bash
# Generate performance benchmark report
pytest performance/ --benchmark-json=benchmark.json
```

## Contributing to Tests

### Test Writing Guidelines
1. **Follow AAA Pattern:** Arrange, Act, Assert
2. **Use Descriptive Names:** Test names should describe the scenario
3. **Mock External Dependencies:** Use mocks for external services
4. **Test Edge Cases:** Include boundary conditions and error scenarios
5. **Maintain Test Data:** Keep fixtures up-to-date and relevant

### Example Test Structure
```python
def test_validate_vector_data_with_valid_input():
    # Arrange
    valid_vector_data = {
        "id": "test-vector-1",
        "vector": [0.1, 0.2, 0.3],
        "payload": {"category": "test"}
    }
    
    # Act
    result = validate_vector_data(valid_vector_data)
    
    # Assert
    assert result is True
```

## Troubleshooting

### Common Issues
1. **Test Dependencies:** Ensure all test dependencies are installed
2. **Service Availability:** Verify test services (Qdrant, Redis) are running
3. **Environment Variables:** Check test environment configuration
4. **Test Data:** Ensure test fixtures are properly generated

### Debug Mode
```bash
# Run tests with debug output
pytest -v -s --tb=long

# Run specific test with debugging
pytest unit/test_validators.py::test_validate_vector_data -v -s --pdb
```

---

**Test Suite Version:** 1.0  
**Last Updated:** July 17, 2025  
**Maintained By:** X-AI Infrastructure Team  
**Framework:** pytest, pytest-benchmark, pytest-cov
