# Citadel LLM Test Suite

This directory contains comprehensive tests for the Citadel LLM system.

## Test Structure

### `/integration/` - Integration Tests

Tests that verify interaction between multiple system components:

- **`test_sql_integration.py`** - PostgreSQL async connection pooling and database operations
- **`test_end_to_end/`** - Complete workflow testing
- **`test_external_services/`** - External service integration tests

### `/performance/` - Performance Tests  

Tests that measure and validate system performance:

- **`test_cache.py`** - Redis cache performance validation (325x speedup testing)
- **`load_tests/`** - Load testing scenarios
- **`stress_tests/`** - Stress testing and resource limits

### `/unit/` - Unit Tests

Tests for individual components and functions:

- Component-specific test files
- Isolated functionality testing
- Mock-based testing

## Running Tests

### Individual Tests

```bash
# From /opt/citadel-02 directory

# Run cache performance test
cd tests/performance && python test_cache.py

# Run SQL integration test  
cd tests/integration && python test_sql_integration.py
```

### Test Requirements

- **Cache Test**: Requires gateway running on port 8000
- **SQL Test**: Requires PostgreSQL database configured (192.168.10.35)
- **Redis**: Required for cache tests (localhost:6379)
- **Virtual Environment**: Use venv

### Expected Results

- **Cache Test**: Should show 5x+ speedup on cache hits
- **SQL Test**: Should complete all async operations successfully
- **Integration**: All services should pass health checks

## Test Configuration

- Tests use Server-02 configuration (192.168.10.28)
- Gateway port: 8000
- Business models: yi-34b, deepcoder, qwen, jarvis, deepseek
- Database connections use async connection pooling
- Cache tests validate Redis performance
- All tests include comprehensive error handling and cleanup

## Adding New Tests

1. Place in appropriate category directory
2. Follow existing naming convention (`test_*.py`)
3. Include proper imports and path resolution
4. Add documentation to this README
5. Ensure cleanup in test teardown
