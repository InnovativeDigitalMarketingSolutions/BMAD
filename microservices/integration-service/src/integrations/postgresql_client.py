"""
PostgreSQL Integration Client

This module provides the PostgreSQL client for the Integration Service,
handling database connections, queries, and transaction management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import asyncpg
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class QueryResult(BaseModel):
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    success: bool
    error: Optional[str] = None

class ConnectionPool(BaseModel):
    pool_size: int
    active_connections: int
    idle_connections: int
    total_connections: int

class PostgreSQLClient:
    """PostgreSQL client for database operations."""
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_params = self._parse_connection_string(connection_string)
        
    def _parse_connection_string(self, connection_string: str) -> Dict[str, str]:
        """Parse PostgreSQL connection string."""
        # Simple parsing - in production use proper URL parsing
        if connection_string.startswith("postgresql://"):
            parts = connection_string.replace("postgresql://", "").split("@")
            if len(parts) == 2:
                user_pass = parts[0].split(":")
                host_port_db = parts[1].split("/")
                if len(user_pass) >= 2 and len(host_port_db) >= 2:
                    user = user_pass[0]
                    password = user_pass[1]
                    host_port = host_port_db[0].split(":")
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else "5432"
                    database = host_port_db[1]
                    
                    return {
                        "user": user,
                        "password": password,
                        "host": host,
                        "port": port,
                        "database": database
                    }
        return {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        
    async def connect(self):
        """Create connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=self.pool_size,
                command_timeout=60
            )
            logger.info(f"PostgreSQL connection pool created with size {self.pool_size}")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
            
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
            
    async def execute_query(self, query: str, *args) -> QueryResult:
        """Execute a query and return results."""
        start_time = datetime.now()
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *args)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                rows = [dict(row) for row in result]
                return QueryResult(
                    rows=rows,
                    row_count=len(rows),
                    execution_time=execution_time,
                    success=True
                )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                rows=[],
                row_count=0,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            
    async def execute_command(self, command: str, *args) -> QueryResult:
        """Execute a command (INSERT, UPDATE, DELETE) and return results."""
        start_time = datetime.now()
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(command, *args)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return QueryResult(
                    rows=[],
                    row_count=0,
                    execution_time=execution_time,
                    success=True
                )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Command execution failed: {e}")
            return QueryResult(
                rows=[],
                row_count=0,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            
    async def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> QueryResult:
        """Execute multiple queries in a transaction."""
        start_time = datetime.now()
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    results = []
                    for query, args in queries:
                        result = await connection.fetch(query, *args)
                        results.extend([dict(row) for row in result])
                        
                    execution_time = (datetime.now() - start_time).total_seconds()
                    return QueryResult(
                        rows=results,
                        row_count=len(results),
                        execution_time=execution_time,
                        success=True
                    )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Transaction execution failed: {e}")
            return QueryResult(
                rows=[],
                row_count=0,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            
    async def get_table_info(self, table_name: str) -> QueryResult:
        """Get table schema information."""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        return await self.execute_query(query, table_name)
        
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            # Get database size
            size_query = "SELECT pg_size_pretty(pg_database_size(current_database())) as size"
            size_result = await self.execute_query(size_query)
            
            # Get table count
            table_query = """
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            table_result = await self.execute_query(table_query)
            
            # Get connection info
            connection_query = """
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity
            """
            connection_result = await self.execute_query(connection_query)
            
            return {
                "database_size": size_result.rows[0]["size"] if size_result.success else "unknown",
                "table_count": table_result.rows[0]["table_count"] if table_result.success else 0,
                "total_connections": connection_result.rows[0]["total_connections"] if connection_result.success else 0,
                "active_connections": connection_result.rows[0]["active_connections"] if connection_result.success else 0,
                "idle_connections": connection_result.rows[0]["idle_connections"] if connection_result.success else 0
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "error": str(e)
            }
            
    async def health_check(self) -> Dict[str, Any]:
        """Check PostgreSQL service health."""
        try:
            if not self.pool:
                return {
                    "status": "unhealthy",
                    "error": "Connection pool not initialized",
                    "connection_string": self.connection_string
                }
                
            # Test connection with simple query
            result = await self.execute_query("SELECT 1 as test")
            
            if result.success:
                stats = await self.get_database_stats()
                return {
                    "status": "healthy",
                    "connection_string": self.connection_string,
                    "pool_size": self.pool_size,
                    "database_stats": stats
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": result.error,
                    "connection_string": self.connection_string
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_string": self.connection_string
            } 