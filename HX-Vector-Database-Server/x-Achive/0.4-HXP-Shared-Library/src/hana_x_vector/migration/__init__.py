"""
Migration Package

Database schema evolution and version control system.
Follows HXP Governance Coding Standards and SOLID principles.

Author: Citadel AI Team
License: MIT
"""

from .migration_manager import (
    MigrationManager,
    IMigration,
    BaseMigration,
    CollectionMigration,
    IndexMigration,
    MigrationRecord,
    MigrationStatus,
    MigrationDirection
)

__all__ = [
    "MigrationManager",
    "IMigration",
    "BaseMigration",
    "CollectionMigration",
    "IndexMigration",
    "MigrationRecord",
    "MigrationStatus",
    "MigrationDirection"
]
