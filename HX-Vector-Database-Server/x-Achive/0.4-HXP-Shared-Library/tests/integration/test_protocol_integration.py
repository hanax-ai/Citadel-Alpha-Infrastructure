"""
Protocol Integration Tests

Comprehensive integration tests for protocol abstraction layer.
Tests REST, GraphQL, and gRPC protocols with unified API Gateway.

Author: Citadel AI Team
License: MIT
"""

import pytest
import asyncio
from typing import Dict, Any, List
import json
import aiohttp
from unittest.mock import Mock, AsyncMock, patch

from hana_x_vector.protocols import (
    ProtocolAbstractionLayer,
    ProtocolType,
    RESTProtocolHandler,
    GraphQLProtocolHandler,
    GRPCProtocolHandler
)
from hana_x_vector.gateway.api_gateway import APIGateway
from hana_x_vector.models.vector_models import Vector, VectorSearchRequest
from hana_x_vector.models.external_models import ExternalModel, ModelType, ModelCapability


class TestProtocolIntegration:
    """Integration tests for protocol abstraction layer."""
    
    @pytest.fixture
    async def mock_vector_db(self):
        """Mock vector database."""
        mock_db = Mock()
        mock_db.vector_operations = AsyncMock()
        mock_db.embedding_service = AsyncMock()
        mock_db.health_check = AsyncMock(return_value={"status": "healthy"})
        return mock_db
    
    @pytest.fixture
    async def mock_model_registry(self):
        """Mock model registry."""
        mock_registry = Mock()
        mock_registry.list_models = AsyncMock(return_value=[])
        mock_registry.get_model = AsyncMock(return_value=None)
        mock_registry.call_model = AsyncMock(return_value={})
        return mock_registry
    
    @pytest.fixture
    async def mock_api_gateway(self, mock_vector_db, mock_model_registry):
        """Mock API Gateway."""
        mock_gateway = Mock()
        mock_gateway.app = Mock()
        mock_gateway.health_check = AsyncMock(return_value={"status": "healthy"})
        return mock_gateway
    
    @pytest.fixture
    async def protocol_layer(self, mock_vector_db, mock_model_registry, mock_api_gateway):
        """Protocol abstraction layer fixture."""
        with patch('hana_x_vector.protocols.protocol_abstraction.get_config') as mock_config:
            # Mock configuration
            mock_config.return_value.api_gateway.enable_rest = True
            mock_config.return_value.api_gateway.enable_graphql = True
            mock_config.return_value.api_gateway.enable_grpc = True
            mock_config.return_value.api_gateway.host = "localhost"
            mock_config.return_value.api_gateway.rest_port = 8000
            mock_config.return_value.api_gateway.graphql_port = 8001
            mock_config.return_value.api_gateway.grpc_port = 50051
            
            layer = ProtocolAbstractionLayer(
                mock_vector_db, mock_model_registry, mock_api_gateway
            )
            return layer
    
    @pytest.mark.asyncio
    async def test_protocol_layer_initialization(self, protocol_layer):
        """Test protocol layer initialization."""
        # Check that all handlers are initialized
        assert ProtocolType.REST in protocol_layer.handlers
        assert ProtocolType.GRAPHQL in protocol_layer.handlers
        assert ProtocolType.GRPC in protocol_layer.handlers
        
        # Check handler types
        assert isinstance(protocol_layer.handlers[ProtocolType.REST], RESTProtocolHandler)
        assert isinstance(protocol_layer.handlers[ProtocolType.GRAPHQL], GraphQLProtocolHandler)
        assert isinstance(protocol_layer.handlers[ProtocolType.GRPC], GRPCProtocolHandler)
    
    @pytest.mark.asyncio
    async def test_protocol_health_checks(self, protocol_layer):
        """Test protocol health checks."""
        # Test individual protocol health checks
        rest_health = await protocol_layer.health_check_protocol(ProtocolType.REST)
        assert rest_health["protocol"] == "REST"
        assert rest_health["status"] == "healthy"
        
        graphql_health = await protocol_layer.health_check_protocol(ProtocolType.GRAPHQL)
        assert graphql_health["protocol"] == "GraphQL"
        assert graphql_health["status"] == "healthy"
        
        grpc_health = await protocol_layer.health_check_protocol(ProtocolType.GRPC)
        assert grpc_health["protocol"] == "gRPC"
        assert grpc_health["status"] == "healthy"
        
        # Test overall health check
        overall_health = await protocol_layer.health_check_all()
        assert overall_health["overall_status"] == "healthy"
        assert "protocols" in overall_health
        assert len(overall_health["protocols"]) == 3
    
    @pytest.mark.asyncio
    async def test_protocol_stats(self, protocol_layer):
        """Test protocol statistics."""
        stats = await protocol_layer.get_protocol_stats()
        
        assert stats["active_protocols"] == 3
        assert "rest" in stats["protocol_types"]
        assert "graphql" in stats["protocol_types"]
        assert "grpc" in stats["protocol_types"]
        assert "timestamp" in stats
    
    @pytest.mark.asyncio
    async def test_get_active_protocols(self, protocol_layer):
        """Test getting active protocols."""
        active_protocols = protocol_layer.get_active_protocols()
        
        assert len(active_protocols) == 3
        assert ProtocolType.REST in active_protocols
        assert ProtocolType.GRAPHQL in active_protocols
        assert ProtocolType.GRPC in active_protocols
    
    @pytest.mark.asyncio
    async def test_get_protocol_handler(self, protocol_layer):
        """Test getting specific protocol handlers."""
        rest_handler = protocol_layer.get_protocol_handler(ProtocolType.REST)
        assert isinstance(rest_handler, RESTProtocolHandler)
        
        graphql_handler = protocol_layer.get_protocol_handler(ProtocolType.GRAPHQL)
        assert isinstance(graphql_handler, GraphQLProtocolHandler)
        
        grpc_handler = protocol_layer.get_protocol_handler(ProtocolType.GRPC)
        assert isinstance(grpc_handler, GRPCProtocolHandler)
        
        # Test non-existent protocol
        invalid_handler = protocol_layer.get_protocol_handler("invalid")
        assert invalid_handler is None


class TestRESTProtocolHandler:
    """Tests for REST protocol handler."""
    
    @pytest.fixture
    async def mock_api_gateway(self):
        """Mock API Gateway for REST tests."""
        mock_gateway = Mock()
        mock_gateway.app = Mock()
        return mock_gateway
    
    @pytest.fixture
    async def rest_handler(self, mock_api_gateway):
        """REST protocol handler fixture."""
        return RESTProtocolHandler(mock_api_gateway, host="localhost", port=8000)
    
    @pytest.mark.asyncio
    async def test_rest_handler_initialization(self, rest_handler):
        """Test REST handler initialization."""
        assert rest_handler.host == "localhost"
        assert rest_handler.port == 8000
        assert rest_handler.get_protocol_type() == ProtocolType.REST
    
    @pytest.mark.asyncio
    async def test_rest_health_check(self, rest_handler):
        """Test REST health check."""
        health = await rest_handler.health_check()
        
        assert health["protocol"] == "REST"
        assert health["status"] == "healthy"
        assert health["host"] == "localhost"
        assert health["port"] == 8000
        assert "timestamp" in health


class TestGraphQLProtocolHandler:
    """Tests for GraphQL protocol handler."""
    
    @pytest.fixture
    async def mock_dependencies(self):
        """Mock dependencies for GraphQL tests."""
        mock_vector_db = Mock()
        mock_model_registry = Mock()
        mock_api_gateway = Mock()
        return mock_vector_db, mock_model_registry, mock_api_gateway
    
    @pytest.fixture
    async def graphql_handler(self, mock_dependencies):
        """GraphQL protocol handler fixture."""
        vector_db, model_registry, api_gateway = mock_dependencies
        return GraphQLProtocolHandler(
            vector_db, model_registry, api_gateway, 
            host="localhost", port=8001
        )
    
    @pytest.mark.asyncio
    async def test_graphql_handler_initialization(self, graphql_handler):
        """Test GraphQL handler initialization."""
        assert graphql_handler.host == "localhost"
        assert graphql_handler.port == 8001
        assert graphql_handler.get_protocol_type() == ProtocolType.GRAPHQL
    
    @pytest.mark.asyncio
    async def test_graphql_health_check(self, graphql_handler):
        """Test GraphQL health check."""
        health = await graphql_handler.health_check()
        
        assert health["protocol"] == "GraphQL"
        assert health["status"] == "healthy"
        assert health["host"] == "localhost"
        assert health["port"] == 8001
        assert "graphiql_url" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_graphql_app_creation(self, graphql_handler):
        """Test GraphQL FastAPI app creation."""
        app = graphql_handler._create_app()
        
        assert app is not None
        assert app.title == "HXP Vector Database GraphQL API"
        assert app.version == "1.0.0"


class TestGRPCProtocolHandler:
    """Tests for gRPC protocol handler."""
    
    @pytest.fixture
    async def mock_dependencies(self):
        """Mock dependencies for gRPC tests."""
        mock_vector_db = Mock()
        mock_model_registry = Mock()
        mock_api_gateway = Mock()
        return mock_vector_db, mock_model_registry, mock_api_gateway
    
    @pytest.fixture
    async def grpc_handler(self, mock_dependencies):
        """gRPC protocol handler fixture."""
        vector_db, model_registry, api_gateway = mock_dependencies
        return GRPCProtocolHandler(
            vector_db, model_registry, api_gateway, port=50051
        )
    
    @pytest.mark.asyncio
    async def test_grpc_handler_initialization(self, grpc_handler):
        """Test gRPC handler initialization."""
        assert grpc_handler.port == 50051
        assert grpc_handler.get_protocol_type() == ProtocolType.GRPC
    
    @pytest.mark.asyncio
    async def test_grpc_health_check(self, grpc_handler):
        """Test gRPC health check."""
        health = await grpc_handler.health_check()
        
        assert health["protocol"] == "gRPC"
        assert health["status"] == "healthy"
        assert health["port"] == 50051
        assert "timestamp" in health


class TestProtocolUnification:
    """Tests for protocol unification and interoperability."""
    
    @pytest.fixture
    async def unified_system(self):
        """Unified system with all protocols."""
        # Mock all dependencies
        mock_vector_db = Mock()
        mock_vector_db.vector_operations = AsyncMock()
        mock_vector_db.embedding_service = AsyncMock()
        mock_vector_db.health_check = AsyncMock(return_value={"status": "healthy"})
        
        mock_model_registry = Mock()
        mock_model_registry.list_models = AsyncMock(return_value=[])
        mock_model_registry.call_model = AsyncMock(return_value={})
        
        mock_api_gateway = Mock()
        mock_api_gateway.app = Mock()
        mock_api_gateway.health_check = AsyncMock(return_value={"status": "healthy"})
        
        with patch('hana_x_vector.protocols.protocol_abstraction.get_config') as mock_config:
            mock_config.return_value.api_gateway.enable_rest = True
            mock_config.return_value.api_gateway.enable_graphql = True
            mock_config.return_value.api_gateway.enable_grpc = True
            mock_config.return_value.api_gateway.host = "localhost"
            mock_config.return_value.api_gateway.rest_port = 8000
            mock_config.return_value.api_gateway.graphql_port = 8001
            mock_config.return_value.api_gateway.grpc_port = 50051
            
            protocol_layer = ProtocolAbstractionLayer(
                mock_vector_db, mock_model_registry, mock_api_gateway
            )
            
            return {
                "protocol_layer": protocol_layer,
                "vector_db": mock_vector_db,
                "model_registry": mock_model_registry,
                "api_gateway": mock_api_gateway
            }
    
    @pytest.mark.asyncio
    async def test_unified_health_monitoring(self, unified_system):
        """Test unified health monitoring across all protocols."""
        protocol_layer = unified_system["protocol_layer"]
        
        # Test health check for all protocols
        health_results = await protocol_layer.health_check_all()
        
        assert health_results["overall_status"] == "healthy"
        assert len(health_results["protocols"]) == 3
        
        # Verify each protocol reports healthy
        for protocol_name, health in health_results["protocols"].items():
            assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_protocol_failover_simulation(self, unified_system):
        """Test protocol failover behavior."""
        protocol_layer = unified_system["protocol_layer"]
        
        # Simulate REST protocol failure
        rest_handler = protocol_layer.get_protocol_handler(ProtocolType.REST)
        
        # Mock health check failure
        async def failing_health_check():
            return {
                "protocol": "REST",
                "status": "unhealthy",
                "error": "Connection failed",
                "timestamp": "2025-07-15T16:30:00"
            }
        
        rest_handler.health_check = failing_health_check
        
        # Check overall health with one protocol failing
        health_results = await protocol_layer.health_check_all()
        
        assert health_results["overall_status"] == "unhealthy"
        assert health_results["protocols"]["rest"]["status"] == "unhealthy"
        assert health_results["protocols"]["graphql"]["status"] == "healthy"
        assert health_results["protocols"]["grpc"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_concurrent_protocol_operations(self, unified_system):
        """Test concurrent operations across multiple protocols."""
        protocol_layer = unified_system["protocol_layer"]
        
        # Simulate concurrent health checks
        tasks = []
        for protocol_type in [ProtocolType.REST, ProtocolType.GRAPHQL, ProtocolType.GRPC]:
            task = protocol_layer.health_check_protocol(protocol_type)
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all protocols responded
        assert len(results) == 3
        for result in results:
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_protocol_configuration_reload(self, unified_system):
        """Test protocol configuration reload."""
        protocol_layer = unified_system["protocol_layer"]
        
        # Get initial protocol count
        initial_protocols = len(protocol_layer.get_active_protocols())
        assert initial_protocols == 3
        
        # Mock configuration change (disable GraphQL)
        with patch('hana_x_vector.protocols.protocol_abstraction.get_config') as mock_config:
            mock_config.return_value.api_gateway.enable_rest = True
            mock_config.return_value.api_gateway.enable_graphql = False
            mock_config.return_value.api_gateway.enable_grpc = True
            mock_config.return_value.api_gateway.host = "localhost"
            mock_config.return_value.api_gateway.rest_port = 8000
            mock_config.return_value.api_gateway.grpc_port = 50051
            
            # Reload configuration
            await protocol_layer.reload_configuration()
            
            # Verify protocol count changed
            updated_protocols = len(protocol_layer.get_active_protocols())
            assert updated_protocols == 2
            assert ProtocolType.GRAPHQL not in protocol_layer.get_active_protocols()


class TestProtocolPerformance:
    """Performance tests for protocol abstraction layer."""
    
    @pytest.fixture
    async def performance_system(self):
        """System setup for performance testing."""
        mock_vector_db = Mock()
        mock_vector_db.health_check = AsyncMock(return_value={"status": "healthy"})
        
        mock_model_registry = Mock()
        mock_api_gateway = Mock()
        mock_api_gateway.health_check = AsyncMock(return_value={"status": "healthy"})
        
        with patch('hana_x_vector.protocols.protocol_abstraction.get_config') as mock_config:
            mock_config.return_value.api_gateway.enable_rest = True
            mock_config.return_value.api_gateway.enable_graphql = True
            mock_config.return_value.api_gateway.enable_grpc = True
            mock_config.return_value.api_gateway.host = "localhost"
            mock_config.return_value.api_gateway.rest_port = 8000
            mock_config.return_value.api_gateway.graphql_port = 8001
            mock_config.return_value.api_gateway.grpc_port = 50051
            
            protocol_layer = ProtocolAbstractionLayer(
                mock_vector_db, mock_model_registry, mock_api_gateway
            )
            
            return protocol_layer
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks_performance(self, performance_system):
        """Test performance of concurrent health checks."""
        protocol_layer = performance_system
        
        # Run multiple concurrent health checks
        tasks = []
        for _ in range(100):  # 100 concurrent requests
            task = protocol_layer.health_check_all()
            tasks.append(task)
        
        # Measure execution time
        import time
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests completed successfully
        assert len(results) == 100
        for result in results:
            assert result["overall_status"] == "healthy"
        
        # Performance assertion (should complete within reasonable time)
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_protocol_stats_performance(self, performance_system):
        """Test performance of protocol statistics collection."""
        protocol_layer = performance_system
        
        # Run multiple stats collection requests
        tasks = []
        for _ in range(50):
            task = protocol_layer.get_protocol_stats()
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all requests completed
        assert len(results) == 50
        for result in results:
            assert result["active_protocols"] == 3
            assert "timestamp" in result


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
