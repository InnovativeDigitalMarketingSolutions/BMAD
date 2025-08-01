"""
PostgreSQL Integration Client

Provides comprehensive PostgreSQL integration for production database including:
- Database connection pooling
- Migration scripts
- Data backup strategies
- Performance optimization
- Monitoring and alerting
- Disaster recovery
"""

import os
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, UTC
from contextlib import contextmanager
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values
    from psycopg2.pool import SimpleConnectionPool, ThreadedConnectionPool
    from psycopg2.extensions import connection, cursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    execute_values = None
    SimpleConnectionPool = None
    ThreadedConnectionPool = None
    connection = None
    cursor = None
    PSYCOPG2_AVAILABLE = False
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PostgreSQLConfig:
    """Configuration for PostgreSQL integration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    min_connections: int = 1
    max_connections: int = 20
    connection_timeout: int = 30
    pool_timeout: int = 30
    ssl_mode: str = "prefer"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None

@dataclass
class DatabaseMigration:
    """Database migration information."""
    version: str
    name: str
    sql: str
    created_at: datetime
    applied_at: Optional[datetime] = None

@dataclass
class DatabaseBackup:
    """Database backup information."""
    id: str
    filename: str
    size_bytes: int
    created_at: datetime
    status: str
    checksum: Optional[str] = None

class PostgreSQLClient:
    """
    Comprehensive PostgreSQL client for production database.
    """
    
    def __init__(self, config: PostgreSQLConfig):
        """Initialize PostgreSQL client with configuration."""
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL integration. Install with: pip install psycopg2-binary")
        
        self.config = config
        self.pool = None
        self._initialize_pool()
        
        logger.info(f"PostgreSQL client initialized for database: {config.database}")
    
    def _initialize_pool(self):
        """Initialize connection pool."""
        try:
            # Build connection string
            conn_string = self._build_connection_string()
            
            # Create connection pool
            self.pool = ThreadedConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                dsn=conn_string
            )
            
            logger.info(f"Connection pool initialized: {self.config.min_connections}-{self.config.max_connections} connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string."""
        conn_parts = [
            f"host={self.config.host}",
            f"port={self.config.port}",
            f"dbname={self.config.database}",
            f"user={self.config.username}",
            f"password={self.config.password}",
            f"connect_timeout={self.config.connection_timeout}",
            f"sslmode={self.config.ssl_mode}"
        ]
        
        # Add SSL certificates if provided
        if self.config.ssl_cert:
            conn_parts.append(f"sslcert={self.config.ssl_cert}")
        if self.config.ssl_key:
            conn_parts.append(f"sslkey={self.config.ssl_key}")
        if self.config.ssl_ca:
            conn_parts.append(f"sslrootcert={self.config.ssl_ca}")
        
        return " ".join(conn_parts)
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, connection: connection, cursor_factory=None):
        """Get database cursor."""
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=cursor_factory or RealDictCursor)
            yield cursor
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database cursor error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """Execute a query and return results."""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    cursor.execute(query, params)
                    
                    if cursor.description:
                        results = cursor.fetchall()
                        return {
                            "success": True,
                            "data": [dict(row) for row in results],
                            "rowcount": cursor.rowcount
                        }
                    else:
                        return {
                            "success": True,
                            "data": None,
                            "rowcount": cursor.rowcount
                        }
                        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_many(self, query: str, params_list: List[tuple]) -> Dict[str, Any]:
        """Execute a query with multiple parameter sets."""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    execute_values(cursor, query, params_list)
                    
                    return {
                        "success": True,
                        "data": None,
                        "rowcount": cursor.rowcount
                    }
                    
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_table(self, table_name: str, columns: List[str], 
                    primary_key: Optional[str] = None,
                    indexes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new table."""
        try:
            # Build CREATE TABLE statement
            columns_sql = ", ".join(columns)
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql}"
            
            if primary_key:
                sql += f", PRIMARY KEY ({primary_key})"
            
            sql += ")"
            
            result = self.execute_query(sql)
            
            # Create indexes if specified
            if result["success"] and indexes:
                for index in indexes:
                    index_result = self.execute_query(index)
                    if not index_result["success"]:
                        logger.warning(f"Failed to create index: {index}")
            
            return result
            
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def drop_table(self, table_name: str, cascade: bool = False) -> Dict[str, Any]:
        """Drop a table."""
        cascade_sql = " CASCADE" if cascade else ""
        sql = f"DROP TABLE IF EXISTS {table_name}{cascade_sql}"
        
        return self.execute_query(sql)
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table."""
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join(["%s"] * len(columns))
            
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
            
            return self.execute_query(sql, tuple(values))
            
        except Exception as e:
            logger.error(f"Data insertion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def update_data(self, table_name: str, data: Dict[str, Any], 
                   where_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Update data in a table."""
        try:
            # Build SET clause
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            set_values = list(data.values())
            
            # Build WHERE clause
            where_clause = " AND ".join([f"{k} = %s" for k in where_conditions.keys()])
            where_values = list(where_conditions.values())
            
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause} RETURNING *"
            
            return self.execute_query(sql, tuple(set_values + where_values))
            
        except Exception as e:
            logger.error(f"Data update failed: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_data(self, table_name: str, where_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Delete data from a table."""
        try:
            # Build WHERE clause
            where_clause = " AND ".join([f"{k} = %s" for k in where_conditions.keys()])
            where_values = list(where_conditions.values())
            
            sql = f"DELETE FROM {table_name} WHERE {where_clause} RETURNING *"
            
            return self.execute_query(sql, tuple(where_values))
            
        except Exception as e:
            logger.error(f"Data deletion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def select_data(self, table_name: str, columns: Optional[List[str]] = None,
                   where_conditions: Optional[Dict[str, Any]] = None,
                   order_by: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> Dict[str, Any]:
        """Select data from a table."""
        try:
            # Build SELECT clause
            columns_sql = ", ".join(columns) if columns else "*"
            
            # Build WHERE clause
            where_sql = ""
            where_values = []
            if where_conditions:
                where_clause = " AND ".join([f"{k} = %s" for k in where_conditions.keys()])
                where_values = list(where_conditions.values())
                where_sql = f"WHERE {where_clause}"
            
            # Build ORDER BY clause
            order_sql = f"ORDER BY {order_by}" if order_by else ""
            
            # Build LIMIT and OFFSET clauses
            limit_sql = f"LIMIT {limit}" if limit else ""
            offset_sql = f"OFFSET {offset}" if offset else ""
            
            sql = f"SELECT {columns_sql} FROM {table_name} {where_sql} {order_sql} {limit_sql} {offset_sql}".strip()
            
            return self.execute_query(sql, tuple(where_values) if where_values else None)
            
        except Exception as e:
            logger.error(f"Data selection failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_migration_table(self) -> Dict[str, Any]:
        """Create migrations table if it doesn't exist."""
        columns = [
            "version VARCHAR(50) NOT NULL",
            "name VARCHAR(255) NOT NULL",
            "sql TEXT NOT NULL",
            "created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
            "applied_at TIMESTAMP WITH TIME ZONE"
        ]
        
        return self.create_table("migrations", columns, primary_key="version")
    
    def apply_migration(self, migration: DatabaseMigration) -> Dict[str, Any]:
        """Apply a database migration."""
        try:
            # Check if migration already applied
            check_result = self.select_data(
                "migrations",
                where_conditions={"version": migration.version}
            )
            
            if check_result["success"] and check_result["data"]:
                return {"success": True, "message": "Migration already applied"}
            
            # Apply migration
            result = self.execute_query(migration.sql)
            
            if result["success"]:
                # Record migration
                migration_data = {
                    "version": migration.version,
                    "name": migration.name,
                    "sql": migration.sql,
                    "applied_at": datetime.now(UTC)
                }
                
                self.insert_data("migrations", migration_data)
                
                logger.info(f"Migration applied: {migration.name} (v{migration.version})")
                return {"success": True, "message": "Migration applied successfully"}
            else:
                return result
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_applied_migrations(self) -> Dict[str, Any]:
        """Get list of applied migrations."""
        return self.select_data(
            "migrations",
            order_by="applied_at ASC"
        )
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            # Get database size
            size_query = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       pg_database_size(current_database()) as size_bytes
            """
            size_result = self.execute_query(size_query)
            
            # Get table count
            table_query = """
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            table_result = self.execute_query(table_query)
            
            # Get connection count
            conn_query = """
                SELECT COUNT(*) as connection_count 
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """
            conn_result = self.execute_query(conn_query)
            
            # Get recent activity
            activity_query = """
                SELECT query, query_start, state 
                FROM pg_stat_activity 
                WHERE datname = current_database() 
                AND state = 'active'
                ORDER BY query_start DESC 
                LIMIT 10
            """
            activity_result = self.execute_query(activity_query)
            
            info = {
                "database_name": self.config.database,
                "host": self.config.host,
                "port": self.config.port,
                "pool_size": f"{self.config.min_connections}-{self.config.max_connections}",
                "size": size_result["data"][0]["size"] if size_result["success"] else "Unknown",
                "size_bytes": size_result["data"][0]["size_bytes"] if size_result["success"] else 0,
                "table_count": table_result["data"][0]["table_count"] if table_result["success"] else 0,
                "connection_count": conn_result["data"][0]["connection_count"] if conn_result["success"] else 0,
                "recent_activity": activity_result["data"] if activity_result["success"] else []
            }
            
            return {"success": True, "data": info}
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"success": False, "error": str(e)}
    
    def create_backup(self, backup_path: str) -> Dict[str, Any]:
        """Create database backup."""
        try:
            import subprocess
            
            backup_id = f"backup_{int(time.time())}"
            backup_file = f"{backup_path}/{backup_id}.sql"
            
            # Ensure backup directory exists
            Path(backup_path).mkdir(parents=True, exist_ok=True)
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_file,
                "--verbose"
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            # Execute backup
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get file size
                file_size = os.path.getsize(backup_file)
                
                # Calculate checksum
                import hashlib
                with open(backup_file, 'rb') as f:
                    checksum = hashlib.md5(f.read()).hexdigest()
                
                backup_info = DatabaseBackup(
                    id=backup_id,
                    filename=backup_file,
                    size_bytes=file_size,
                    created_at=datetime.now(UTC),
                    status="completed",
                    checksum=checksum
                )
                
                logger.info(f"Database backup created: {backup_file} ({file_size} bytes)")
                return {"success": True, "data": backup_info}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """Restore database from backup."""
        try:
            import subprocess
            
            # Build psql command
            cmd = [
                "psql",
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_file,
                "--verbose"
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            # Execute restore
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database restored from: {backup_file}")
                return {"success": True, "message": "Database restored successfully"}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL connection pool closed") 