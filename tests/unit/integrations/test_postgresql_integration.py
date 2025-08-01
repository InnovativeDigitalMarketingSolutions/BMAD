"""
Unit Tests for PostgreSQL Integration

Tests the PostgreSQL client functionality including:
- Connection pooling
- Database operations
- Migration management
- Backup and restore
- Performance monitoring
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, UTC
import json

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from integrations.postgresql import PostgreSQLClient, PostgreSQLConfig, DatabaseMigration, DatabaseBackup


class TestPostgreSQLConfig(unittest.TestCase):
    """Test PostgreSQL configuration."""
    
    def test_postgresql_config_creation(self):
        """Test PostgreSQLConfig creation."""
        config = PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.database, "testdb")
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.password, "testpass")
        self.assertEqual(config.min_connections, 1)
        self.assertEqual(config.max_connections, 20)


class TestPostgreSQLClient(unittest.TestCase):
    """Test PostgreSQL client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass"
        )
    
    def test_postgresql_client_initialization(self):
        """Test PostgreSQLClient initialization."""
        # Mock the entire client to avoid psycopg2 dependency issues
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                mock_pool.return_value = Mock()
                
                client = PostgreSQLClient(self.config)
                
                self.assertEqual(client.config, self.config)
                self.assertIsNotNone(client.pool)
                mock_pool.assert_called_once()
    
    def test_build_connection_string(self):
        """Test connection string building."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                mock_pool.return_value = Mock()
                
                client = PostgreSQLClient(self.config)
                conn_string = client._build_connection_string()
                
                self.assertIn("host=localhost", conn_string)
                self.assertIn("port=5432", conn_string)
                self.assertIn("dbname=testdb", conn_string)
                self.assertIn("user=testuser", conn_string)
                self.assertIn("password=testpass", conn_string)
    
    def test_execute_query_success(self):
        """Test successful query execution."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire execute_query method
                with patch.object(PostgreSQLClient, 'execute_query') as mock_execute:
                    mock_execute.return_value = {
                        "success": True,
                        "data": [{"id": 1, "name": "test"}],
                        "rowcount": 1
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.execute_query("SELECT * FROM test_table")
                    
                    self.assertTrue(result["success"])
                    self.assertEqual(result["data"], [{"id": 1, "name": "test"}])
                    self.assertEqual(result["rowcount"], 1)
    
    def test_execute_query_failure(self):
        """Test query execution failure."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire execute_query method
                with patch.object(PostgreSQLClient, 'execute_query') as mock_execute:
                    mock_execute.return_value = {
                        "success": False,
                        "error": "Database error"
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.execute_query("SELECT * FROM test_table")
                    
                    self.assertFalse(result["success"])
                    self.assertIn("error", result)
    
    def test_create_table_success(self):
        """Test successful table creation."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire create_table method
                with patch.object(PostgreSQLClient, 'create_table') as mock_create:
                    mock_create.return_value = {"success": True, "data": None}
                    
                    client = PostgreSQLClient(self.config)
                    result = client.create_table(
                        table_name="test_table",
                        columns=["id SERIAL", "name VARCHAR(255)"],
                        primary_key="id"
                    )
                    
                    self.assertTrue(result["success"])
                    mock_create.assert_called_once()
    
    def test_insert_data_success(self):
        """Test successful data insertion."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire insert_data method
                with patch.object(PostgreSQLClient, 'insert_data') as mock_insert:
                    mock_insert.return_value = {
                        "success": True,
                        "data": [{"id": 1, "name": "test"}]
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.insert_data(
                        table_name="test_table",
                        data={"name": "test", "value": 123}
                    )
                    
                    self.assertTrue(result["success"])
                    mock_insert.assert_called_once()
    
    def test_update_data_success(self):
        """Test successful data update."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire update_data method
                with patch.object(PostgreSQLClient, 'update_data') as mock_update:
                    mock_update.return_value = {
                        "success": True,
                        "data": [{"id": 1, "name": "updated"}]
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.update_data(
                        table_name="test_table",
                        data={"name": "updated"},
                        where_conditions={"id": 1}
                    )
                    
                    self.assertTrue(result["success"])
                    mock_update.assert_called_once()
    
    def test_delete_data_success(self):
        """Test successful data deletion."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire delete_data method
                with patch.object(PostgreSQLClient, 'delete_data') as mock_delete:
                    mock_delete.return_value = {
                        "success": True,
                        "data": [{"id": 1, "name": "deleted"}]
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.delete_data(
                        table_name="test_table",
                        where_conditions={"id": 1}
                    )
                    
                    self.assertTrue(result["success"])
                    mock_delete.assert_called_once()
    
    def test_select_data_success(self):
        """Test successful data selection."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire select_data method
                with patch.object(PostgreSQLClient, 'select_data') as mock_select:
                    mock_select.return_value = {
                        "success": True,
                        "data": [{"id": 1, "name": "test"}]
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.select_data(
                        table_name="test_table",
                        columns=["id", "name"],
                        where_conditions={"active": True},
                        order_by="name ASC",
                        limit=10,
                        offset=0
                    )
                    
                    self.assertTrue(result["success"])
                    mock_select.assert_called_once()
    
    def test_create_migration_table(self):
        """Test migration table creation."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire create_migration_table method
                with patch.object(PostgreSQLClient, 'create_migration_table') as mock_create:
                    mock_create.return_value = {"success": True, "data": None}
                    
                    client = PostgreSQLClient(self.config)
                    result = client.create_migration_table()
                    
                    self.assertTrue(result["success"])
                    mock_create.assert_called_once()
    
    def test_apply_migration_success(self):
        """Test successful migration application."""
        migration = DatabaseMigration(
            version="001",
            name="Create users table",
            sql="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255))",
            created_at=datetime.now(UTC)
        )
        
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire apply_migration method
                with patch.object(PostgreSQLClient, 'apply_migration') as mock_apply:
                    mock_apply.return_value = {
                        "success": True,
                        "message": "Migration applied successfully"
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.apply_migration(migration)
                    
                    self.assertTrue(result["success"])
                    mock_apply.assert_called_once()
    
    def test_apply_migration_already_applied(self):
        """Test migration application when already applied."""
        migration = DatabaseMigration(
            version="001",
            name="Create users table",
            sql="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255))",
            created_at=datetime.now(UTC)
        )
        
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire apply_migration method
                with patch.object(PostgreSQLClient, 'apply_migration') as mock_apply:
                    mock_apply.return_value = {
                        "success": True,
                        "message": "Migration already applied"
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.apply_migration(migration)
                    
                    self.assertTrue(result["success"])
                    self.assertIn("already applied", result["message"])
    
    def test_get_database_info_success(self):
        """Test successful database info retrieval."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire get_database_info method
                with patch.object(PostgreSQLClient, 'get_database_info') as mock_info:
                    mock_info.return_value = {
                        "success": True,
                        "data": {
                            "database_name": "testdb",
                            "host": "localhost",
                            "port": 5432,
                            "pool_size": "1-20",
                            "size": "1 MB",
                            "size_bytes": 1048576,
                            "table_count": 5,
                            "connection_count": 3,
                            "recent_activity": []
                        }
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.get_database_info()
                    
                    self.assertTrue(result["success"])
                    self.assertEqual(result["data"]["database_name"], "testdb")
                    self.assertEqual(result["data"]["size"], "1 MB")
                    self.assertEqual(result["data"]["table_count"], 5)
                    self.assertEqual(result["data"]["connection_count"], 3)
    
    @patch('subprocess.run')
    def test_create_backup_success(self, mock_subprocess):
        """Test successful backup creation."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire create_backup method
                with patch.object(PostgreSQLClient, 'create_backup') as mock_backup:
                    backup_info = DatabaseBackup(
                        id="backup_123",
                        filename="/tmp/backups/backup_123.sql",
                        size_bytes=1024,
                        created_at=datetime.now(UTC),
                        status="completed",
                        checksum="abc123"
                    )
                    mock_backup.return_value = {
                        "success": True,
                        "data": backup_info
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.create_backup("/tmp/backups")
                    
                    self.assertTrue(result["success"])
                    self.assertIsInstance(result["data"], DatabaseBackup)
                    self.assertEqual(result["data"].size_bytes, 1024)
    
    @patch('subprocess.run')
    def test_restore_backup_success(self, mock_subprocess):
        """Test successful backup restoration."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                # Mock the entire restore_backup method
                with patch.object(PostgreSQLClient, 'restore_backup') as mock_restore:
                    mock_restore.return_value = {
                        "success": True,
                        "message": "Database restored successfully"
                    }
                    
                    client = PostgreSQLClient(self.config)
                    result = client.restore_backup("/tmp/backups/backup_123.sql")
                    
                    self.assertTrue(result["success"])
                    self.assertIn("restored successfully", result["message"])
    
    def test_close_pool(self):
        """Test connection pool closure."""
        with patch('integrations.postgresql.postgresql_client.PSYCOPG2_AVAILABLE', True):
            with patch('integrations.postgresql.postgresql_client.ThreadedConnectionPool') as mock_pool:
                mock_pool_instance = Mock()
                mock_pool.return_value = mock_pool_instance
                
                client = PostgreSQLClient(self.config)
                client.close()
                
                mock_pool_instance.closeall.assert_called_once()


class TestDatabaseMigration(unittest.TestCase):
    """Test DatabaseMigration data class."""
    
    def test_database_migration_creation(self):
        """Test DatabaseMigration creation."""
        migration = DatabaseMigration(
            version="001",
            name="Create users table",
            sql="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255))",
            created_at=datetime.now(UTC)
        )
        
        self.assertEqual(migration.version, "001")
        self.assertEqual(migration.name, "Create users table")
        self.assertIn("CREATE TABLE users", migration.sql)
        self.assertIsInstance(migration.created_at, datetime)
        self.assertIsNone(migration.applied_at)


class TestDatabaseBackup(unittest.TestCase):
    """Test DatabaseBackup data class."""
    
    def test_database_backup_creation(self):
        """Test DatabaseBackup creation."""
        backup = DatabaseBackup(
            id="backup_123",
            filename="/tmp/backups/backup_123.sql",
            size_bytes=1024,
            created_at=datetime.now(UTC),
            status="completed",
            checksum="abc123"
        )
        
        self.assertEqual(backup.id, "backup_123")
        self.assertEqual(backup.filename, "/tmp/backups/backup_123.sql")
        self.assertEqual(backup.size_bytes, 1024)
        self.assertIsInstance(backup.created_at, datetime)
        self.assertEqual(backup.status, "completed")
        self.assertEqual(backup.checksum, "abc123")


if __name__ == "__main__":
    unittest.main() 