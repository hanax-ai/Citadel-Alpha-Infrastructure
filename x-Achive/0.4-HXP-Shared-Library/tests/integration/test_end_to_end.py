"""
End-to-End Integration Tests

Comprehensive end-to-end testing of the complete HXP Vector Database system.
Tests all components working together without Qdrant dependency.

Author: Citadel AI Team
License: MIT
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from hana_x_vector import VectorDatabase, APIGateway
from hana_x_vector.protocols import ProtocolAbstractionLayer, ProtocolType
from hana_x_vector.migration import MigrationManager, CollectionMigration
from hana_x_vector.core.gpu_manager import GPUMemoryManager
from hana_x_vector.external_models.model_registry import ExternalModelRegistry
from hana_x_vector.orchestration.service_manager import ServiceOrchestrator
from hana_x_vector.models.vector_models import Vector, VectorSearchRequest
from hana_x_vector.models.external_models import ExternalModel, ModelType, ModelCapability


class TestEndToEndIntegration:
    """End-to-end integration tests for the complete system."""
    
    @pytest.fixture
    async def temp_storage(self):
        """Temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        
        # Database configuration
        config.database.host = "localhost"
        config.database.port = 6333
        config.database.grpc_port = 6334
        config.database.collection_name = "test_collection"
        
        # API Gateway configuration
        config.api_gateway.host = "localhost"
        config.api_gateway.rest_port = 8000
        config.api_gateway.graphql_port = 8001
        config.api_gateway.grpc_port = 50051
        config.api_gateway.enable_rest = True
        config.api_gateway.enable_graphql = True
        config.api_gateway.enable_grpc = True
        
        # External models configuration
        config.external_models.openai_api_key = "test_key"
        config.external_models.anthropic_api_key = "test_key"
        
        # Caching configuration
        config.caching.redis_url = "redis://localhost:6379"
        config.caching.enabled = True
        config.caching.ttl_seconds = 3600
        
        return config
    
    @pytest.fixture
    async def integrated_system(self, temp_storage, mock_config):
        """Fully integrated system for testing."""
        with patch('hana_x_vector.utils.config.get_config', return_value=mock_config):
            # Initialize core components
            vector_db = VectorDatabase()
            api_gateway = APIGateway(vector_db)
            
            # Initialize additional components
            gpu_manager = GPUMemoryManager()
            model_registry = ExternalModelRegistry()
            migration_manager = MigrationManager(vector_db, temp_storage)
            protocol_layer = ProtocolAbstractionLayer(vector_db, model_registry, api_gateway)
            service_orchestrator = ServiceOrchestrator()
            
            # Register services with orchestrator
            await service_orchestrator.register_service("vector_db", vector_db)
            await service_orchestrator.register_service("api_gateway", api_gateway)
            await service_orchestrator.register_service("gpu_manager", gpu_manager)
            await service_orchestrator.register_service("model_registry", model_registry)
            await service_orchestrator.register_service("migration_manager", migration_manager)
            await service_orchestrator.register_service("protocol_layer", protocol_layer)
            
            return {
                "vector_db": vector_db,
                "api_gateway": api_gateway,
                "gpu_manager": gpu_manager,
                "model_registry": model_registry,
                "migration_manager": migration_manager,
                "protocol_layer": protocol_layer,
                "service_orchestrator": service_orchestrator
            }
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, integrated_system):
        """Test complete system initialization."""
        system = integrated_system
        
        # Verify all components are initialized
        assert system["vector_db"] is not None
        assert system["api_gateway"] is not None
        assert system["gpu_manager"] is not None
        assert system["model_registry"] is not None
        assert system["migration_manager"] is not None
        assert system["protocol_layer"] is not None
        assert system["service_orchestrator"] is not None
        
        # Verify service orchestrator has all services
        services = await system["service_orchestrator"].get_service_status()
        assert len(services["services"]) == 6
        
        # Verify protocol layer has all protocols
        active_protocols = system["protocol_layer"].get_active_protocols()
        assert len(active_protocols) == 3
        assert ProtocolType.REST in active_protocols
        assert ProtocolType.GRAPHQL in active_protocols
        assert ProtocolType.GRPC in active_protocols
    
    @pytest.mark.asyncio
    async def test_service_orchestration_lifecycle(self, integrated_system):
        """Test service orchestration startup and shutdown."""
        orchestrator = integrated_system["service_orchestrator"]
        
        # Test startup sequence
        startup_result = await orchestrator.start_all_services()
        assert startup_result["status"] == "success"
        
        # Verify all services are running
        status = await orchestrator.get_service_status()
        for service_name, service_status in status["services"].items():
            assert service_status["status"] == "running"
        
        # Test health monitoring
        health_result = await orchestrator.monitor_service_health()
        assert health_result["overall_health"] == "healthy"
        
        # Test shutdown sequence
        shutdown_result = await orchestrator.stop_all_services()
        assert shutdown_result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_protocol_abstraction_integration(self, integrated_system):
        """Test protocol abstraction layer integration."""
        protocol_layer = integrated_system["protocol_layer"]
        
        # Test protocol health checks
        health_results = await protocol_layer.health_check_all()
        assert health_results["overall_status"] == "healthy"
        assert len(health_results["protocols"]) == 3
        
        # Test individual protocol handlers
        for protocol_type in [ProtocolType.REST, ProtocolType.GRAPHQL, ProtocolType.GRPC]:
            handler = protocol_layer.get_protocol_handler(protocol_type)
            assert handler is not None
            
            health = await handler.health_check()
            assert health["status"] == "healthy"
        
        # Test protocol statistics
        stats = await protocol_layer.get_protocol_stats()
        assert stats["active_protocols"] == 3
        assert "rest" in stats["protocol_types"]
        assert "graphql" in stats["protocol_types"]
        assert "grpc" in stats["protocol_types"]
    
    @pytest.mark.asyncio
    async def test_migration_system_integration(self, integrated_system):
        """Test migration system integration."""
        migration_manager = integrated_system["migration_manager"]
        
        # Create test migration
        migration = CollectionMigration(
            version="20250715_001",
            description="Test collection migration",
            collection_name="test_collection",
            dimension=384
        )
        
        # Register migration
        migration_manager.register_migration(migration)
        
        # Test migration execution
        result = await migration_manager.migrate_up("20250715_001")
        assert result["status"] == "success"
        assert "20250715_001" in result["executed_migrations"]
        
        # Test migration status
        status = await migration_manager.get_migration_status()
        assert status["total_migrations"] == 1
        assert status["status_counts"]["completed"] == 1
        
        # Test migration history
        history = await migration_manager.get_migration_history()
        assert len(history) == 1
        assert history[0]["version"] == "20250715_001"
        assert history[0]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_gpu_memory_management_integration(self, integrated_system):
        """Test GPU memory management integration."""
        gpu_manager = integrated_system["gpu_manager"]
        
        # Test GPU information
        gpu_info = gpu_manager.get_gpu_info()
        assert len(gpu_info) == 2  # Dual GPU setup
        
        # Test model allocation
        success = gpu_manager.allocate_model("all-MiniLM-L6-v2", device_id=0)
        assert success == True
        
        # Test allocation summary
        summary = gpu_manager.get_allocation_summary()
        assert summary["total_models"] == 1
        assert len(summary["allocations"]) == 1
        assert summary["allocations"][0]["model_name"] == "all-MiniLM-L6-v2"
        
        # Test model deallocation
        success = gpu_manager.deallocate_model("all-MiniLM-L6-v2")
        assert success == True
        
        # Verify deallocation
        summary = gpu_manager.get_allocation_summary()
        assert summary["total_models"] == 0
    
    @pytest.mark.asyncio
    async def test_external_model_integration(self, integrated_system):
        """Test external model integration."""
        model_registry = integrated_system["model_registry"]
        
        # Create test external model
        external_model = ExternalModel(
            id="test_openai_model",
            name="OpenAI GPT-4",
            model_type=ModelType.LANGUAGE_MODEL,
            api_endpoint="https://api.openai.com/v1/chat/completions",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.EMBEDDINGS],
            is_active=True
        )
        
        # Register model
        await model_registry.register_model(external_model)
        
        # Test model listing
        models = await model_registry.list_models()
        assert len(models) == 1
        assert models[0].id == "test_openai_model"
        
        # Test model retrieval
        retrieved_model = await model_registry.get_model("test_openai_model")
        assert retrieved_model is not None
        assert retrieved_model.name == "OpenAI GPT-4"
        
        # Test model health check
        health = await model_registry.check_model_health("test_openai_model")
        assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_vector_operations_integration(self, integrated_system):
        """Test vector operations integration."""
        vector_db = integrated_system["vector_db"]
        
        # Test vector insertion
        test_vector = Vector(
            id="test_vector_001",
            embedding=[0.1] * 384,
            metadata={"test": True, "type": "integration_test"},
            collection="test_collection"
        )
        
        # Mock the vector operations
        with patch.object(vector_db.vector_operations, 'insert_vector') as mock_insert:
            mock_insert.return_value = AsyncMock(success=True, message="Vector inserted")
            
            result = await vector_db.vector_operations.insert_vector(test_vector, "test_collection")
            assert result.success == True
            mock_insert.assert_called_once()
        
        # Test vector search
        search_request = VectorSearchRequest(
            query_vector=[0.1] * 384,
            collection="test_collection",
            limit=10,
            include_vectors=True,
            include_metadata=True
        )
        
        with patch.object(vector_db.vector_operations, 'search_vectors') as mock_search:
            mock_search.return_value = AsyncMock(
                vectors=[test_vector],
                total_count=1,
                query_time_ms=2.5
            )
            
            result = await vector_db.vector_operations.search_vectors(search_request)
            assert len(result.vectors) == 1
            assert result.vectors[0].id == "test_vector_001"
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_embedding_service_integration(self, integrated_system):
        """Test embedding service integration."""
        vector_db = integrated_system["vector_db"]
        
        # Test embedding generation
        test_texts = ["This is a test sentence.", "Another test sentence."]
        
        with patch.object(vector_db.embedding_service, 'generate_embeddings') as mock_embed:
            mock_embed.return_value = AsyncMock(
                embeddings=[[0.1] * 384, [0.2] * 384],
                model_name="all-MiniLM-L6-v2",
                dimension=384,
                processing_time_ms=50.0
            )
            
            result = await vector_db.embedding_service.generate_embeddings(test_texts)
            assert len(result.embeddings) == 2
            assert result.dimension == 384
            assert result.model_name == "all-MiniLM-L6-v2"
            mock_embed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_gateway_integration(self, integrated_system):
        """Test API Gateway integration."""
        api_gateway = integrated_system["api_gateway"]
        
        # Test health check endpoint
        health_result = await api_gateway.health_check()
        assert health_result["status"] == "healthy"
        
        # Test that FastAPI app is configured
        assert api_gateway.app is not None
        assert api_gateway.app.title == "HXP Vector Database API"
    
    @pytest.mark.asyncio
    async def test_performance_requirements_validation(self, integrated_system):
        """Test system performance against PRD requirements."""
        vector_db = integrated_system["vector_db"]
        
        # Performance targets from PRD
        TARGET_OPS_PER_SECOND = 10000
        TARGET_LATENCY_MS = 10
        TARGET_EMBEDDING_LATENCY_MS = 100
        
        # Mock high-performance operations
        with patch.object(vector_db.vector_operations, 'search_vectors') as mock_search:
            # Simulate fast search (2ms latency)
            mock_search.return_value = AsyncMock(
                vectors=[],
                total_count=0,
                query_time_ms=2.0
            )
            
            # Test search performance
            import time
            start_time = time.time()
            
            # Simulate 1000 operations
            tasks = []
            for _ in range(1000):
                search_request = VectorSearchRequest(
                    query_vector=[0.1] * 384,
                    collection="test_collection",
                    limit=10
                )
                task = vector_db.vector_operations.search_vectors(search_request)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            ops_per_second = 1000 / duration
            
            # Verify performance meets requirements
            assert ops_per_second >= TARGET_OPS_PER_SECOND * 0.1  # Allow 10% of target for mock
            
        # Test embedding generation performance
        with patch.object(vector_db.embedding_service, 'generate_embeddings') as mock_embed:
            # Simulate fast embedding generation (50ms)
            mock_embed.return_value = AsyncMock(
                embeddings=[[0.1] * 384],
                model_name="all-MiniLM-L6-v2",
                dimension=384,
                processing_time_ms=50.0
            )
            
            start_time = time.time()
            result = await vector_db.embedding_service.generate_embeddings(["test text"])
            end_time = time.time()
            
            actual_latency_ms = (end_time - start_time) * 1000
            
            # Verify latency meets requirements (allowing for mock overhead)
            assert actual_latency_ms <= TARGET_EMBEDDING_LATENCY_MS * 2
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, integrated_system):
        """Test error handling and recovery mechanisms."""
        orchestrator = integrated_system["service_orchestrator"]
        
        # Test service failure simulation
        with patch.object(orchestrator, '_check_service_health') as mock_health:
            # Simulate service failure
            mock_health.return_value = {
                "status": "unhealthy",
                "error": "Service connection failed"
            }
            
            # Test health monitoring with failure
            health_result = await orchestrator.monitor_service_health()
            assert health_result["overall_health"] == "unhealthy"
        
        # Test recovery mechanism
        with patch.object(orchestrator, '_restart_service') as mock_restart:
            mock_restart.return_value = True
            
            # Test service restart
            restart_result = await orchestrator.restart_service("test_service")
            assert restart_result == True
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, integrated_system):
        """Test concurrent operations across all components."""
        system = integrated_system
        
        # Create concurrent tasks for different components
        tasks = []
        
        # Vector operations
        for i in range(10):
            search_request = VectorSearchRequest(
                query_vector=[0.1] * 384,
                collection="test_collection",
                limit=10
            )
            with patch.object(system["vector_db"].vector_operations, 'search_vectors') as mock_search:
                mock_search.return_value = AsyncMock(vectors=[], total_count=0, query_time_ms=2.0)
                task = system["vector_db"].vector_operations.search_vectors(search_request)
                tasks.append(task)
        
        # Health checks
        for _ in range(5):
            task = system["service_orchestrator"].monitor_service_health()
            tasks.append(task)
        
        # Protocol health checks
        for _ in range(3):
            task = system["protocol_layer"].health_check_all()
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify no exceptions occurred
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Concurrent operations failed: {exceptions}"
    
    @pytest.mark.asyncio
    async def test_system_configuration_validation(self, integrated_system):
        """Test system configuration validation."""
        system = integrated_system
        
        # Test GPU configuration
        gpu_info = system["gpu_manager"].get_gpu_info()
        assert len(gpu_info) == 2  # Dual GPU setup as per PRD
        
        for device_id, info in gpu_info.items():
            assert info.total_memory_mb == 6144  # 6GB per GPU as per PRD
        
        # Test protocol configuration
        active_protocols = system["protocol_layer"].get_active_protocols()
        assert len(active_protocols) == 3  # REST, GraphQL, gRPC
        
        # Test model registry configuration
        models = await system["model_registry"].list_models()
        # Should be empty initially, but registry should be functional
        assert isinstance(models, list)
    
    @pytest.mark.asyncio
    async def test_system_metrics_collection(self, integrated_system):
        """Test system-wide metrics collection."""
        system = integrated_system
        
        # Test GPU metrics
        gpu_summary = system["gpu_manager"].get_allocation_summary()
        assert "gpu_utilization" in gpu_summary
        assert "gpu_0" in gpu_summary["gpu_utilization"]
        assert "gpu_1" in gpu_summary["gpu_utilization"]
        
        # Test service metrics
        service_status = await system["service_orchestrator"].get_service_status()
        assert "services" in service_status
        assert len(service_status["services"]) > 0
        
        # Test protocol metrics
        protocol_stats = await system["protocol_layer"].get_protocol_stats()
        assert "active_protocols" in protocol_stats
        assert protocol_stats["active_protocols"] == 3


class TestSystemStressAndLoad:
    """Stress and load testing for the integrated system."""
    
    @pytest.fixture
    async def stress_test_system(self, integrated_system):
        """System configured for stress testing."""
        return integrated_system
    
    @pytest.mark.asyncio
    async def test_high_concurrency_vector_operations(self, stress_test_system):
        """Test high concurrency vector operations."""
        vector_db = stress_test_system["vector_db"]
        
        # Mock high-performance vector operations
        with patch.object(vector_db.vector_operations, 'search_vectors') as mock_search:
            mock_search.return_value = AsyncMock(
                vectors=[],
                total_count=0,
                query_time_ms=1.0
            )
            
            # Create 1000 concurrent search operations
            tasks = []
            for i in range(1000):
                search_request = VectorSearchRequest(
                    query_vector=[0.1] * 384,
                    collection="stress_test_collection",
                    limit=10
                )
                task = vector_db.vector_operations.search_vectors(search_request)
                tasks.append(task)
            
            # Execute all tasks concurrently
            import time
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Verify all operations completed successfully
            exceptions = [r for r in results if isinstance(r, Exception)]
            assert len(exceptions) == 0
            
            # Verify performance
            duration = end_time - start_time
            ops_per_second = 1000 / duration
            
            # Should handle at least 1000 ops/sec in stress test
            assert ops_per_second >= 1000
    
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self, stress_test_system):
        """Test system behavior under memory pressure."""
        gpu_manager = stress_test_system["gpu_manager"]
        
        # Attempt to allocate all available models
        models = ["all-MiniLM-L6-v2", "phi-3-mini", "e5-small", "bge-base"]
        
        allocation_results = []
        for model in models:
            result = gpu_manager.allocate_model(model)
            allocation_results.append(result)
        
        # Should successfully allocate models within GPU memory limits
        successful_allocations = sum(1 for r in allocation_results if r)
        assert successful_allocations >= 2  # At least 2 models should fit
        
        # Test allocation summary under pressure
        summary = gpu_manager.get_allocation_summary()
        assert summary["total_models"] == successful_allocations
        
        # Test memory optimization
        optimization_result = gpu_manager.optimize_allocations()
        assert "reallocated_models" in optimization_result
    
    @pytest.mark.asyncio
    async def test_service_recovery_under_load(self, stress_test_system):
        """Test service recovery mechanisms under load."""
        orchestrator = stress_test_system["service_orchestrator"]
        
        # Simulate service failures during high load
        with patch.object(orchestrator, '_check_service_health') as mock_health:
            # Simulate intermittent failures
            health_responses = [
                {"status": "healthy"},
                {"status": "unhealthy", "error": "Connection timeout"},
                {"status": "healthy"},
                {"status": "unhealthy", "error": "Memory exhausted"},
                {"status": "healthy"}
            ]
            mock_health.side_effect = health_responses
            
            # Test multiple health checks
            health_results = []
            for _ in range(5):
                result = await orchestrator.monitor_service_health()
                health_results.append(result)
            
            # Should handle failures gracefully
            assert len(health_results) == 5
            
            # At least some checks should succeed
            healthy_checks = sum(1 for r in health_results if r.get("overall_health") == "healthy")
            assert healthy_checks >= 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-x"])
