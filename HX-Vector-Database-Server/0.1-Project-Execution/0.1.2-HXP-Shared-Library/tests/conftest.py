"""
Pytest Configuration and Fixtures
=================================

Global pytest configuration and shared fixtures for the HANA-X Vector Database Shared Library test suite.
"""

import pytest
import asyncio
import os
import tempfile
import json
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock
import numpy as np

# Set test environment
os.environ["HANA_X_TEST_MODE"] = "true"
os.environ["TESTING"] = "true"

# Test configuration
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_vector_data():
    """Sample vector data for testing."""
    return {
        "id": "test-vector-1",
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "payload": {
            "category": "test",
            "source": "unit_test",
            "timestamp": "2025-07-17T03:59:00Z"
        },
        "collection": "test_collection"
    }


@pytest.fixture
def sample_vectors_batch():
    """Sample batch of vectors for testing."""
    return [
        {
            "id": f"test-vector-{i}",
            "vector": [float(i * 0.1 + j * 0.01) for j in range(5)],
            "payload": {"category": "test", "index": i},
            "collection": "test_collection"
        }
        for i in range(10)
    ]


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return {
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "collection": "test_collection",
        "limit": 10,
        "filter": {"category": "test"},
        "with_payload": True,
        "with_vectors": False
    }


@pytest.fixture
def sample_collection_config():
    """Sample collection configuration for testing."""
    return {
        "name": "test_collection",
        "vectors": {
            "size": 5,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    client = Mock()
    client.get_collections = AsyncMock(return_value={"collections": []})
    client.create_collection = AsyncMock(return_value={"status": "ok"})
    client.upsert = AsyncMock(return_value={"status": "ok"})
    client.search = AsyncMock(return_value=[])
    client.delete = AsyncMock(return_value={"status": "ok"})
    client.get_collection = AsyncMock(return_value={"status": "ok"})
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = Mock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=False)
    client.expire = AsyncMock(return_value=True)
    client.flushdb = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_external_model_client():
    """Mock external model client for testing."""
    client = Mock()
    client.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
    client.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3, 0.4, 0.5]])
    client.health_check = AsyncMock(return_value={"status": "healthy"})
    return client


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector for testing."""
    collector = Mock()
    collector.increment_counter = Mock()
    collector.record_histogram = Mock()
    collector.record_gauge = Mock()
    collector.record_timer = Mock()
    return collector


@pytest.fixture
def test_config():
    """Test configuration dictionary."""
    return {
        "qdrant": {
            "host": "localhost",
            "port": 6333,
            "grpc_port": 6334,
            "api_key": None,
            "timeout": 30.0
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None
        },
        "api_gateway": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": ["http://localhost:3000"],
            "api_keys": ["test-api-key-123"]
        },
        "external_models": {
            "primary_llm_server": "http://192.168.10.29:8000",
            "secondary_llm_server": "http://192.168.10.28:8000",
            "timeout": 30.0
        },
        "monitoring": {
            "metrics_enabled": True,
            "health_check_interval": 30,
            "log_level": "INFO"
        }
    }


@pytest.fixture
def temp_directory():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_api_request():
    """Sample API request for testing."""
    return {
        "method": "POST",
        "path": "/vectors/search",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-api-key-123"
        },
        "body": {
            "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
            "collection": "test_collection",
            "limit": 10
        }
    }


@pytest.fixture
def sample_graphql_query():
    """Sample GraphQL query for testing."""
    return """
    query SearchVectors($vector: [Float!]!, $collection: String!, $limit: Int!) {
        searchVectors(vector: $vector, collection: $collection, limit: $limit) {
            id
            score
            payload
        }
    }
    """


@pytest.fixture
def sample_grpc_request():
    """Sample gRPC request for testing."""
    return {
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "collection": "test_collection",
        "limit": 10,
        "filter": {}
    }


@pytest.fixture
def performance_test_vectors():
    """Large set of vectors for performance testing."""
    return [
        [float(np.random.random()) for _ in range(384)]
        for _ in range(1000)
    ]


@pytest.fixture
def mock_health_checker():
    """Mock health checker for testing."""
    checker = Mock()
    checker.check_qdrant_health = AsyncMock(return_value={"status": "healthy"})
    checker.check_redis_health = AsyncMock(return_value={"status": "healthy"})
    checker.check_external_models_health = AsyncMock(return_value={"status": "healthy"})
    checker.get_overall_health = AsyncMock(return_value={"status": "healthy"})
    return checker


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.slow = pytest.mark.slow


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance/" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security/" in str(item.fspath):
            item.add_marker(pytest.mark.security)


# Async test utilities
@pytest.fixture
async def async_test_client():
    """Async test client for API testing."""
    from httpx import AsyncClient
    async with AsyncClient() as client:
        yield client


# Database test utilities
@pytest.fixture
def test_database_url():
    """Test database URL."""
    return "postgresql://test:test@localhost:5432/test_db"


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test."""
    yield
    # Cleanup logic here if needed
    pass
