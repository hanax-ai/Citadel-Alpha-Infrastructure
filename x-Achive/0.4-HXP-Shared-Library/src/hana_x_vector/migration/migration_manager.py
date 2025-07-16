"""
Migration Manager

Database schema evolution and version control system.
Implements Single Responsibility Principle for migration management.

Author: Citadel AI Team
License: MIT
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import json
import hashlib
import os
from pathlib import Path

from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.metrics import MetricsCollector, monitor_performance
from hana_x_vector.utils.config import get_config

logger = get_logger(__name__)


class MigrationStatus(Enum):
    """Migration status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationDirection(Enum):
    """Migration direction enumeration."""
    UP = "up"
    DOWN = "down"


class IMigration(ABC):
    """Interface for migration implementations."""
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get migration version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get migration description."""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Get migration dependencies."""
        pass
    
    @abstractmethod
    async def up(self, context: Dict[str, Any]) -> None:
        """Execute forward migration."""
        pass
    
    @abstractmethod
    async def down(self, context: Dict[str, Any]) -> None:
        """Execute rollback migration."""
        pass
    
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Validate migration can be executed."""
        pass


class MigrationRecord:
    """Migration execution record."""
    
    def __init__(self, version: str, description: str, status: MigrationStatus,
                 executed_at: Optional[datetime] = None, 
                 execution_time_ms: Optional[float] = None,
                 error_message: Optional[str] = None,
                 checksum: Optional[str] = None):
        """Initialize migration record."""
        self.version = version
        self.description = description
        self.status = status
        self.executed_at = executed_at or datetime.now()
        self.execution_time_ms = execution_time_ms
        self.error_message = error_message
        self.checksum = checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "executed_at": self.executed_at.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "checksum": self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationRecord":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            description=data["description"],
            status=MigrationStatus(data["status"]),
            executed_at=datetime.fromisoformat(data["executed_at"]),
            execution_time_ms=data.get("execution_time_ms"),
            error_message=data.get("error_message"),
            checksum=data.get("checksum")
        )


class BaseMigration(IMigration):
    """Base migration implementation."""
    
    def __init__(self, version: str, description: str, dependencies: List[str] = None):
        """Initialize base migration."""
        self._version = version
        self._description = description
        self._dependencies = dependencies or []
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    def version(self) -> str:
        """Get migration version."""
        return self._version
    
    @property
    def description(self) -> str:
        """Get migration description."""
        return self._description
    
    @property
    def dependencies(self) -> List[str]:
        """Get migration dependencies."""
        return self._dependencies
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Default validation - always returns True."""
        return True
    
    def _calculate_checksum(self) -> str:
        """Calculate migration checksum."""
        content = f"{self.version}:{self.description}:{':'.join(self.dependencies)}"
        return hashlib.sha256(content.encode()).hexdigest()


class CollectionMigration(BaseMigration):
    """Migration for collection operations."""
    
    def __init__(self, version: str, description: str, 
                 collection_name: str, dimension: int,
                 dependencies: List[str] = None):
        """Initialize collection migration."""
        super().__init__(version, description, dependencies)
        self.collection_name = collection_name
        self.dimension = dimension
    
    async def up(self, context: Dict[str, Any]) -> None:
        """Create collection."""
        try:
            vector_db = context.get("vector_db")
            if not vector_db:
                raise ValueError("Vector database not available in context")
            
            # Create collection (this would call actual collection manager)
            self.logger.info(f"Creating collection: {self.collection_name}")
            
            # Mock implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            
            self.logger.info(f"Collection {self.collection_name} created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create collection {self.collection_name}: {e}")
            raise
    
    async def down(self, context: Dict[str, Any]) -> None:
        """Drop collection."""
        try:
            vector_db = context.get("vector_db")
            if not vector_db:
                raise ValueError("Vector database not available in context")
            
            # Drop collection (this would call actual collection manager)
            self.logger.info(f"Dropping collection: {self.collection_name}")
            
            # Mock implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            
            self.logger.info(f"Collection {self.collection_name} dropped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to drop collection {self.collection_name}: {e}")
            raise
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Validate collection migration."""
        try:
            vector_db = context.get("vector_db")
            if not vector_db:
                return False
            
            # Check if collection already exists
            # This would call actual collection manager
            return True
            
        except Exception as e:
            self.logger.error(f"Collection migration validation failed: {e}")
            return False


class IndexMigration(BaseMigration):
    """Migration for index operations."""
    
    def __init__(self, version: str, description: str,
                 collection_name: str, index_config: Dict[str, Any],
                 dependencies: List[str] = None):
        """Initialize index migration."""
        super().__init__(version, description, dependencies)
        self.collection_name = collection_name
        self.index_config = index_config
    
    async def up(self, context: Dict[str, Any]) -> None:
        """Create index."""
        try:
            vector_db = context.get("vector_db")
            if not vector_db:
                raise ValueError("Vector database not available in context")
            
            # Create index (this would call actual index manager)
            self.logger.info(f"Creating index for collection: {self.collection_name}")
            
            # Mock implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            
            self.logger.info(f"Index created for collection {self.collection_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create index for {self.collection_name}: {e}")
            raise
    
    async def down(self, context: Dict[str, Any]) -> None:
        """Drop index."""
        try:
            vector_db = context.get("vector_db")
            if not vector_db:
                raise ValueError("Vector database not available in context")
            
            # Drop index (this would call actual index manager)
            self.logger.info(f"Dropping index for collection: {self.collection_name}")
            
            # Mock implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            
            self.logger.info(f"Index dropped for collection {self.collection_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to drop index for {self.collection_name}: {e}")
            raise


class MigrationManager:
    """
    Migration Manager
    
    Manages database schema evolution and version control.
    Implements Single Responsibility Principle for migration operations.
    """
    
    def __init__(self, vector_db, migration_storage_path: str = None):
        """Initialize migration manager."""
        self.vector_db = vector_db
        self.migration_storage_path = migration_storage_path or "migrations"
        self.migrations: Dict[str, IMigration] = {}
        self.migration_records: Dict[str, MigrationRecord] = {}
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
        self.config = get_config()
        
        # Ensure migration storage directory exists
        Path(self.migration_storage_path).mkdir(parents=True, exist_ok=True)
        
        # Load migration records
        asyncio.create_task(self._load_migration_records())
    
    def register_migration(self, migration: IMigration) -> None:
        """Register a migration."""
        try:
            if migration.version in self.migrations:
                raise ValueError(f"Migration {migration.version} already registered")
            
            self.migrations[migration.version] = migration
            self.logger.info(f"Registered migration: {migration.version} - {migration.description}")
            
        except Exception as e:
            self.logger.error(f"Failed to register migration {migration.version}: {e}")
            raise
    
    def unregister_migration(self, version: str) -> None:
        """Unregister a migration."""
        try:
            if version in self.migrations:
                del self.migrations[version]
                self.logger.info(f"Unregistered migration: {version}")
            else:
                self.logger.warning(f"Migration {version} not found for unregistration")
                
        except Exception as e:
            self.logger.error(f"Failed to unregister migration {version}: {e}")
            raise
    
    async def _load_migration_records(self) -> None:
        """Load migration records from storage."""
        try:
            records_file = Path(self.migration_storage_path) / "migration_records.json"
            
            if records_file.exists():
                with open(records_file, 'r') as f:
                    records_data = json.load(f)
                
                for version, record_data in records_data.items():
                    self.migration_records[version] = MigrationRecord.from_dict(record_data)
                
                self.logger.info(f"Loaded {len(self.migration_records)} migration records")
            else:
                self.logger.info("No existing migration records found")
                
        except Exception as e:
            self.logger.error(f"Failed to load migration records: {e}")
            # Continue without records - they will be created as migrations run
    
    async def _save_migration_records(self) -> None:
        """Save migration records to storage."""
        try:
            records_file = Path(self.migration_storage_path) / "migration_records.json"
            
            records_data = {
                version: record.to_dict() 
                for version, record in self.migration_records.items()
            }
            
            with open(records_file, 'w') as f:
                json.dump(records_data, f, indent=2)
            
            self.logger.debug("Migration records saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save migration records: {e}")
            raise
    
    def _resolve_dependencies(self, target_version: str = None) -> List[str]:
        """Resolve migration dependencies and return execution order."""
        try:
            # If no target version specified, include all migrations
            if target_version is None:
                target_migrations = set(self.migrations.keys())
            else:
                target_migrations = {target_version}
                
                # Add dependencies recursively
                def add_dependencies(version: str):
                    if version in self.migrations:
                        for dep in self.migrations[version].dependencies:
                            if dep not in target_migrations:
                                target_migrations.add(dep)
                                add_dependencies(dep)
                
                add_dependencies(target_version)
            
            # Topological sort to resolve execution order
            visited = set()
            temp_visited = set()
            execution_order = []
            
            def visit(version: str):
                if version in temp_visited:
                    raise ValueError(f"Circular dependency detected involving {version}")
                if version in visited:
                    return
                
                temp_visited.add(version)
                
                if version in self.migrations:
                    for dep in self.migrations[version].dependencies:
                        if dep in target_migrations:
                            visit(dep)
                
                temp_visited.remove(version)
                visited.add(version)
                execution_order.append(version)
            
            for version in target_migrations:
                if version not in visited:
                    visit(version)
            
            return execution_order
            
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies: {e}")
            raise
    
    @monitor_performance
    async def migrate_up(self, target_version: str = None) -> Dict[str, Any]:
        """Execute forward migrations."""
        try:
            self.logger.info(f"Starting forward migration to version: {target_version or 'latest'}")
            
            # Resolve execution order
            execution_order = self._resolve_dependencies(target_version)
            
            # Filter out already completed migrations
            pending_migrations = [
                version for version in execution_order
                if version not in self.migration_records or 
                self.migration_records[version].status != MigrationStatus.COMPLETED
            ]
            
            if not pending_migrations:
                self.logger.info("No pending migrations to execute")
                return {
                    "status": "success",
                    "message": "No pending migrations",
                    "executed_migrations": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute migrations
            executed_migrations = []
            context = {"vector_db": self.vector_db}
            
            for version in pending_migrations:
                if version not in self.migrations:
                    raise ValueError(f"Migration {version} not found")
                
                migration = self.migrations[version]
                
                # Update status to running
                record = MigrationRecord(
                    version=version,
                    description=migration.description,
                    status=MigrationStatus.RUNNING,
                    checksum=migration._calculate_checksum() if hasattr(migration, '_calculate_checksum') else None
                )
                self.migration_records[version] = record
                await self._save_migration_records()
                
                try:
                    # Validate migration
                    if not await migration.validate(context):
                        raise ValueError(f"Migration {version} validation failed")
                    
                    # Execute migration
                    start_time = datetime.now()
                    await migration.up(context)
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Update status to completed
                    record.status = MigrationStatus.COMPLETED
                    record.execution_time_ms = execution_time
                    record.executed_at = datetime.now()
                    
                    executed_migrations.append(version)
                    self.logger.info(f"Migration {version} completed successfully")
                    
                except Exception as e:
                    # Update status to failed
                    record.status = MigrationStatus.FAILED
                    record.error_message = str(e)
                    
                    self.logger.error(f"Migration {version} failed: {e}")
                    raise
                
                finally:
                    await self._save_migration_records()
            
            result = {
                "status": "success",
                "message": f"Successfully executed {len(executed_migrations)} migrations",
                "executed_migrations": executed_migrations,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Forward migration completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Forward migration failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "executed_migrations": executed_migrations if 'executed_migrations' in locals() else [],
                "timestamp": datetime.now().isoformat()
            }
    
    @monitor_performance
    async def migrate_down(self, target_version: str) -> Dict[str, Any]:
        """Execute rollback migrations."""
        try:
            self.logger.info(f"Starting rollback migration to version: {target_version}")
            
            # Get completed migrations in reverse order
            completed_migrations = [
                version for version, record in self.migration_records.items()
                if record.status == MigrationStatus.COMPLETED
            ]
            
            # Sort by execution time (most recent first)
            completed_migrations.sort(
                key=lambda v: self.migration_records[v].executed_at,
                reverse=True
            )
            
            # Find migrations to rollback
            rollback_migrations = []
            for version in completed_migrations:
                if version == target_version:
                    break
                rollback_migrations.append(version)
            
            if not rollback_migrations:
                self.logger.info("No migrations to rollback")
                return {
                    "status": "success",
                    "message": "No migrations to rollback",
                    "rolled_back_migrations": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute rollbacks
            rolled_back_migrations = []
            context = {"vector_db": self.vector_db}
            
            for version in rollback_migrations:
                if version not in self.migrations:
                    self.logger.warning(f"Migration {version} not found for rollback")
                    continue
                
                migration = self.migrations[version]
                record = self.migration_records[version]
                
                # Update status to running
                record.status = MigrationStatus.RUNNING
                await self._save_migration_records()
                
                try:
                    # Execute rollback
                    start_time = datetime.now()
                    await migration.down(context)
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Update status to rolled back
                    record.status = MigrationStatus.ROLLED_BACK
                    record.execution_time_ms = execution_time
                    record.executed_at = datetime.now()
                    
                    rolled_back_migrations.append(version)
                    self.logger.info(f"Migration {version} rolled back successfully")
                    
                except Exception as e:
                    # Update status to failed
                    record.status = MigrationStatus.FAILED
                    record.error_message = str(e)
                    
                    self.logger.error(f"Migration {version} rollback failed: {e}")
                    raise
                
                finally:
                    await self._save_migration_records()
            
            result = {
                "status": "success",
                "message": f"Successfully rolled back {len(rolled_back_migrations)} migrations",
                "rolled_back_migrations": rolled_back_migrations,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Rollback migration completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Rollback migration failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "rolled_back_migrations": rolled_back_migrations if 'rolled_back_migrations' in locals() else [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status."""
        try:
            # Count migrations by status
            status_counts = {}
            for status in MigrationStatus:
                status_counts[status.value] = 0
            
            for record in self.migration_records.values():
                status_counts[record.status.value] += 1
            
            # Get pending migrations
            pending_migrations = [
                version for version in self.migrations.keys()
                if version not in self.migration_records or 
                self.migration_records[version].status != MigrationStatus.COMPLETED
            ]
            
            return {
                "total_migrations": len(self.migrations),
                "status_counts": status_counts,
                "pending_migrations": pending_migrations,
                "latest_migration": max(
                    self.migration_records.keys(),
                    key=lambda v: self.migration_records[v].executed_at
                ) if self.migration_records else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        try:
            history = []
            
            for version, record in self.migration_records.items():
                migration = self.migrations.get(version)
                history.append({
                    "version": version,
                    "description": migration.description if migration else "Unknown",
                    "status": record.status.value,
                    "executed_at": record.executed_at.isoformat(),
                    "execution_time_ms": record.execution_time_ms,
                    "error_message": record.error_message,
                    "checksum": record.checksum
                })
            
            # Sort by execution time
            history.sort(key=lambda x: x["executed_at"], reverse=True)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get migration history: {e}")
            return []
    
    async def validate_migrations(self) -> Dict[str, Any]:
        """Validate all registered migrations."""
        try:
            validation_results = {}
            context = {"vector_db": self.vector_db}
            
            for version, migration in self.migrations.items():
                try:
                    is_valid = await migration.validate(context)
                    validation_results[version] = {
                        "valid": is_valid,
                        "description": migration.description,
                        "dependencies": migration.dependencies
                    }
                except Exception as e:
                    validation_results[version] = {
                        "valid": False,
                        "error": str(e),
                        "description": migration.description,
                        "dependencies": migration.dependencies
                    }
            
            all_valid = all(result["valid"] for result in validation_results.values())
            
            return {
                "all_valid": all_valid,
                "validations": validation_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Migration validation failed: {e}")
            return {
                "all_valid": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def reset_migrations(self) -> Dict[str, Any]:
        """Reset all migration records (use with caution)."""
        try:
            self.logger.warning("Resetting all migration records")
            
            # Clear records
            self.migration_records.clear()
            
            # Save empty records
            await self._save_migration_records()
            
            return {
                "status": "success",
                "message": "All migration records reset",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to reset migrations: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
