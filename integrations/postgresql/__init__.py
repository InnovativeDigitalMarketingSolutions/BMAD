"""
PostgreSQL Integration Module

Provides production database capabilities with connection pooling, migrations, and backup strategies.
"""

from .postgresql_client import (
    PostgreSQLClient,
    PostgreSQLConfig,
    DatabaseMigration,
    DatabaseBackup
)

__all__ = [
    "PostgreSQLClient",
    "PostgreSQLConfig",
    "DatabaseMigration", 
    "DatabaseBackup"
] 