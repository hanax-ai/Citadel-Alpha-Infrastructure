"""
Migration Integration Tests

Comprehensive integration tests for migration system.
Tests database schema evolution and version control.

Author: Citadel AI Team
License: MIT
"""

import pytest
import asyncio
from typing import Dict, Any, List
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from hana_x_vector.migration import (
    MigrationManager,
    CollectionMigration,
    IndexMigration,
    MigrationStatus,
    MigrationDirection,
    BaseMigration
)


class TestMigrationIntegration:
    """Integration tests for migration system."""
    
    @pytest.fixture
    async def temp_storage(self):
        """Temporary storage for migration tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def mock_vector_db(self):
        """Mock vector database."""
        mock_db = Mock()
        mock_db.health_check = AsyncMock(return_value={"status": "healthy"})
        return mock_db
    
    @pytest.fixture
    async def migration_manager(self, mock_vector_db, temp_storage):
        """Migration manager fixture."""
        return MigrationManager(mock_vector_db, temp_storage)
    
    @pytest.mark.asyncio
    async def test_migration_manager_initialization(self, migration_manager, temp_storage):
        """Test migration manager initialization."""
        assert migration_manager.vector_db is not None
        assert migration_manager.migration_storage_path == temp_storage
        assert len(migration_manager.migrations) == 0
        assert len(migration_manager.migration_records) == 0
        
        # Check storage directory exists
        assert Path(temp_storage).exists()
    
    @pytest.mark.asyncio
    async def test_migration_registration(self, migration_manager):
        """Test migration registration."""
        # Create test migration
        migration = CollectionMigration(
            version="20250715_001",
            description="Create test collection",
            collection_name="test_collection",
            dimension=384
        )
        
        # Register migration
        migration_manager.register_migration(migration)
        
        # Verify registration
        assert "20250715_001" in migration_manager.migrations
        assert migration_manager.migrations["20250715_001"] == migration
    
    @pytest.mark.asyncio
    async def test_migration_unregistration(self, migration_manager):
        """Test migration unregistration."""
        # Register migration first
        migration = CollectionMigration(
            version="20250715_002",
            description="Create another test collection",
            collection_name="another_collection",
            dimension=768
        )
        migration_manager.register_migration(migration)
        
        # Verify registration
        assert "20250715_002" in migration_manager.migrations
        
        # Unregister migration
        migration_manager.unregister_migration("20250715_002")
        
        # Verify unregistration
        assert "20250715_002" not in migration_manager.migrations
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self, migration_manager):
        """Test migration dependency resolution."""
        # Create migrations with dependencies
        migration1 = CollectionMigration(
            version="20250715_010",
            description="Base migration",
            collection_name="base_collection",
            dimension=384
        )
        
        migration2 = IndexMigration(
            version="20250715_020",
            description="Index migration",
            collection_name="base_collection",
            index_config={},
            dependencies=["20250715_010"]
        )
        
        migration3 = CollectionMigration(
            version="20250715_030",
            description="Dependent migration",
            collection_name="dependent_collection",
            dimension=768,
            dependencies=["20250715_020"]
        )
        
        # Register migrations
        migration_manager.register_migration(migration1)
        migration_manager.register_migration(migration2)
        migration_manager.register_migration(migration3)
        
        # Resolve dependencies
        execution_order = migration_manager._resolve_dependencies("20250715_030")
        
        # Verify correct order
        assert execution_order == ["20250715_010", "20250715_020", "20250715_030"]
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, migration_manager):
        """Test circular dependency detection."""
        # Create migrations with circular dependencies
        migration1 = CollectionMigration(
            version="20250715_100",
            description="Migration 1",
            collection_name="collection1",
            dimension=384,
            dependencies=["20250715_200"]
        )
        
        migration2 = CollectionMigration(
            version="20250715_200",
            description="Migration 2",
            collection_name="collection2",
            dimension=768,
            dependencies=["20250715_100"]
        )
        
        # Register migrations
        migration_manager.register_migration(migration1)
        migration_manager.register_migration(migration2)
        
        # Attempt to resolve dependencies should raise error
        with pytest.raises(ValueError, match="Circular dependency detected"):
            migration_manager._resolve_dependencies("20250715_100")
    
    @pytest.mark.asyncio
    async def test_forward_migration_execution(self, migration_manager):
        """Test forward migration execution."""
        # Create test migration
        migration = CollectionMigration(
            version="20250715_300",
            description="Forward migration test",
            collection_name="forward_collection",
            dimension=384
        )
        
        # Register migration
        migration_manager.register_migration(migration)
        
        # Execute forward migration
        result = await migration_manager.migrate_up("20250715_300")
        
        # Verify result
        assert result["status"] == "success"
        assert "20250715_300" in result["executed_migrations"]
        
        # Verify migration record
        assert "20250715_300" in migration_manager.migration_records
        record = migration_manager.migration_records["20250715_300"]
        assert record.status == MigrationStatus.COMPLETED
        assert record.version == "20250715_300"
    
    @pytest.mark.asyncio
    async def test_rollback_migration_execution(self, migration_manager):
        """Test rollback migration execution."""
        # Create and execute forward migration first
        migration = CollectionMigration(
            version="20250715_400",
            description="Rollback migration test",
            collection_name="rollback_collection",
            dimension=384
        )
        
        migration_manager.register_migration(migration)
        await migration_manager.migrate_up("20250715_400")
        
        # Verify forward migration completed
        assert migration_manager.migration_records["20250715_400"].status == MigrationStatus.COMPLETED
        
        # Execute rollback
        result = await migration_manager.migrate_down("20250715_400")
        
        # Verify rollback result
        assert result["status"] == "success"
        
        # Verify migration record updated
        record = migration_manager.migration_records["20250715_400"]
        assert record.status == MigrationStatus.ROLLED_BACK
    
    @pytest.mark.asyncio
    async def test_migration_validation(self, migration_manager):
        """Test migration validation."""
        # Create test migration
        migration = CollectionMigration(
            version="20250715_500",
            description="Validation test",
            collection_name="validation_collection",
            dimension=384
        )
        
        migration_manager.register_migration(migration)
        
        # Validate migrations
        result = await migration_manager.validate_migrations()
        
        # Verify validation result
        assert result["all_valid"] == True
        assert "20250715_500" in result["validations"]
        assert result["validations"]["20250715_500"]["valid"] == True
    
    @pytest.mark.asyncio
    async def test_migration_status_tracking(self, migration_manager):
        """Test migration status tracking."""
        # Create multiple migrations
        migrations = [
            CollectionMigration(
                version=f"20250715_{i:03d}",
                description=f"Migration {i}",
                collection_name=f"collection_{i}",
                dimension=384
            )
            for i in range(600, 605)
        ]
        
        # Register migrations
        for migration in migrations:
            migration_manager.register_migration(migration)
        
        # Execute some migrations
        await migration_manager.migrate_up("20250715_602")
        
        # Get migration status
        status = await migration_manager.get_migration_status()
        
        # Verify status
        assert status["total_migrations"] == 5
        assert status["status_counts"]["completed"] == 3  # 600, 601, 602
        assert status["status_counts"]["pending"] == 0
        assert len(status["pending_migrations"]) == 2  # 603, 604
    
    @pytest.mark.asyncio
    async def test_migration_history(self, migration_manager):
        """Test migration history tracking."""
        # Create and execute migration
        migration = CollectionMigration(
            version="20250715_700",
            description="History test",
            collection_name="history_collection",
            dimension=384
        )
        
        migration_manager.register_migration(migration)
        await migration_manager.migrate_up("20250715_700")
        
        # Get migration history
        history = await migration_manager.get_migration_history()
        
        # Verify history
        assert len(history) == 1
        assert history[0]["version"] == "20250715_700"
        assert history[0]["status"] == "completed"
        assert history[0]["description"] == "History test"
    
    @pytest.mark.asyncio
    async def test_migration_persistence(self, migration_manager, temp_storage):
        """Test migration record persistence."""
        # Create and execute migration
        migration = CollectionMigration(
            version="20250715_800",
            description="Persistence test",
            collection_name="persistence_collection",
            dimension=384
        )
        
        migration_manager.register_migration(migration)
        await migration_manager.migrate_up("20250715_800")
        
        # Verify records file exists
        records_file = Path(temp_storage) / "migration_records.json"
        assert records_file.exists()
        
        # Verify records content
        with open(records_file, 'r') as f:
            records_data = json.load(f)
        
        assert "20250715_800" in records_data
        assert records_data["20250715_800"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_migration_reset(self, migration_manager):
        """Test migration reset functionality."""
        # Create and execute migration
        migration = CollectionMigration(
            version="20250715_900",
            description="Reset test",
            collection_name="reset_collection",
            dimension=384
        )
        
        migration_manager.register_migration(migration)
        await migration_manager.migrate_up("20250715_900")
        
        # Verify migration exists
        assert len(migration_manager.migration_records) == 1
        
        # Reset migrations
        result = await migration_manager.reset_migrations()
        
        # Verify reset
        assert result["status"] == "success"
        assert len(migration_manager.migration_records) == 0


class TestCollectionMigration:
    """Tests for collection migration implementation."""
    
    @pytest.fixture
    async def mock_context(self):
        """Mock migration context."""
        mock_vector_db = Mock()
        return {"vector_db": mock_vector_db}
    
    @pytest.mark.asyncio
    async def test_collection_migration_up(self, mock_context):
        """Test collection creation migration."""
        migration = CollectionMigration(
            version="20250715_001",
            description="Create test collection",
            collection_name="test_collection",
            dimension=384
        )
        
        # Execute up migration
        await migration.up(mock_context)
        
        # Verify migration properties
        assert migration.version == "20250715_001"
        assert migration.collection_name == "test_collection"
        assert migration.dimension == 384
    
    @pytest.mark.asyncio
    async def test_collection_migration_down(self, mock_context):
        """Test collection deletion migration."""
        migration = CollectionMigration(
            version="20250715_002",
            description="Drop test collection",
            collection_name="test_collection",
            dimension=384
        )
        
        # Execute down migration
        await migration.down(mock_context)
        
        # Verify migration completed without error
        assert migration.collection_name == "test_collection"
    
    @pytest.mark.asyncio
    async def test_collection_migration_validation(self, mock_context):
        """Test collection migration validation."""
        migration = CollectionMigration(
            version="20250715_003",
            description="Validate test collection",
            collection_name="test_collection",
            dimension=384
        )
        
        # Validate migration
        is_valid = await migration.validate(mock_context)
        
        # Should be valid with mock context
        assert is_valid == True


class TestIndexMigration:
    """Tests for index migration implementation."""
    
    @pytest.fixture
    async def mock_context(self):
        """Mock migration context."""
        mock_vector_db = Mock()
        return {"vector_db": mock_vector_db}
    
    @pytest.mark.asyncio
    async def test_index_migration_up(self, mock_context):
        """Test index creation migration."""
        migration = IndexMigration(
            version="20250715_101",
            description="Create test index",
            collection_name="test_collection",
            index_config={"type": "hnsw", "m": 16}
        )
        
        # Execute up migration
        await migration.up(mock_context)
        
        # Verify migration properties
        assert migration.version == "20250715_101"
        assert migration.collection_name == "test_collection"
        assert migration.index_config["type"] == "hnsw"
    
    @pytest.mark.asyncio
    async def test_index_migration_down(self, mock_context):
        """Test index deletion migration."""
        migration = IndexMigration(
            version="20250715_102",
            description="Drop test index",
            collection_name="test_collection",
            index_config={"type": "hnsw"}
        )
        
        # Execute down migration
        await migration.down(mock_context)
        
        # Verify migration completed without error
        assert migration.collection_name == "test_collection"


class TestMigrationPerformance:
    """Performance tests for migration system."""
    
    @pytest.fixture
    async def performance_setup(self):
        """Setup for performance testing."""
        temp_dir = tempfile.mkdtemp()
        mock_vector_db = Mock()
        mock_vector_db.health_check = AsyncMock(return_value={"status": "healthy"})
        
        manager = MigrationManager(mock_vector_db, temp_dir)
        
        yield manager, temp_dir
        
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_bulk_migration_performance(self, performance_setup):
        """Test performance with many migrations."""
        manager, temp_dir = performance_setup
        
        # Create many migrations
        migrations = []
        for i in range(100):
            migration = CollectionMigration(
                version=f"20250715_{i:04d}",
                description=f"Performance test migration {i}",
                collection_name=f"perf_collection_{i}",
                dimension=384
            )
            migrations.append(migration)
            manager.register_migration(migration)
        
        # Measure execution time
        import time
        start_time = time.time()
        
        # Execute all migrations
        result = await manager.migrate_up()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all migrations completed
        assert result["status"] == "success"
        assert len(result["executed_migrations"]) == 100
        
        # Performance assertion (should complete within reasonable time)
        assert execution_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_migration_operations(self, performance_setup):
        """Test concurrent migration operations."""
        manager, temp_dir = performance_setup
        
        # Create test migration
        migration = CollectionMigration(
            version="20250715_concurrent",
            description="Concurrent test",
            collection_name="concurrent_collection",
            dimension=384
        )
        manager.register_migration(migration)
        
        # Execute concurrent operations
        tasks = [
            manager.get_migration_status(),
            manager.validate_migrations(),
            manager.get_migration_history(),
            manager.migrate_up("20250715_concurrent")
        ]
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify no exceptions occurred
        for result in results:
            assert not isinstance(result, Exception)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
