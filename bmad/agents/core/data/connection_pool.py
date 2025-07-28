"""
BMAD Connection Pooling

Dit module biedt connection pooling voor database en externe service verbindingen.
Implementeert connection pooling met health checks en automatic reconnection.
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import aiohttp
import asyncpg
from redis import ConnectionPool as RedisConnectionPool
from redis import Redis

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    """
    Beheert connection pools voor verschillende services.
    """

    def __init__(self):
        self.pools: Dict[str, Any] = {}
        self.health_checks: Dict[str, bool] = {}
        self.last_health_check: Dict[str, float] = {}
        self.health_check_interval = 300  # 5 minuten

        # Pool configuraties
        self.pool_configs = {
            "redis": {
                "max_connections": 20,
                "retry_on_timeout": True,
                "socket_keepalive": True,
                "socket_keepalive_options": {},
            },
            "postgres": {
                "min_size": 5,
                "max_size": 20,
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "bmad_agents"
                }
            },
            "http": {
                "limit": 100,
                "limit_per_host": 30,
                "timeout": aiohttp.ClientTimeout(total=30),
            }
        }

    async def initialize_pools(self):
        """Initialiseer alle connection pools."""
        await self._init_redis_pool()
        await self._init_postgres_pool()
        await self._init_http_pool()

        logger.info("✅ Connection pools geïnitialiseerd")

    async def _init_redis_pool(self):
        """Initialiseer Redis connection pool."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            pool = RedisConnectionPool.from_url(
                redis_url,
                **self.pool_configs["redis"]
            )

            # Test connection
            redis_client = Redis(connection_pool=pool)
            redis_client.ping()

            self.pools["redis"] = pool
            self.health_checks["redis"] = True
            logger.info("✅ Redis connection pool geïnitialiseerd")

        except Exception as e:
            logger.warning(f"⚠️ Redis pool initialisatie gefaald: {e}")
            self.health_checks["redis"] = False

    async def _init_postgres_pool(self):
        """Initialiseer PostgreSQL connection pool."""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                logger.warning("⚠️ DATABASE_URL niet gezet - PostgreSQL pool uitgeschakeld")
                self.health_checks["postgres"] = False
                return

            pool = await asyncpg.create_pool(
                database_url,
                **self.pool_configs["postgres"]
            )

            # Test connection
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")

            self.pools["postgres"] = pool
            self.health_checks["postgres"] = True
            logger.info("✅ PostgreSQL connection pool geïnitialiseerd")

        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL pool initialisatie gefaald: {e}")
            self.health_checks["postgres"] = False

    async def _init_http_pool(self):
        """Initialiseer HTTP connection pool."""
        try:
            connector = aiohttp.TCPConnector(
                limit=self.pool_configs["http"]["limit"],
                limit_per_host=self.pool_configs["http"]["limit_per_host"],
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )

            session = aiohttp.ClientSession(
                timeout=self.pool_configs["http"]["timeout"],
                connector=connector
            )

            self.pools["http"] = session
            self.health_checks["http"] = True
            logger.info("✅ HTTP connection pool geïnitialiseerd")

        except Exception as e:
            logger.warning(f"⚠️ HTTP pool initialisatie gefaald: {e}")
            self.health_checks["http"] = False

    @asynccontextmanager
    async def get_redis_connection(self):
        """Context manager voor Redis connection."""
        if "redis" not in self.pools or not self.health_checks["redis"]:
            raise ConnectionError("Redis pool niet beschikbaar")

        try:
            redis_client = Redis(connection_pool=self.pools["redis"])
            yield redis_client
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise

    @asynccontextmanager
    async def get_postgres_connection(self):
        """Context manager voor PostgreSQL connection."""
        if "postgres" not in self.pools or not self.health_checks["postgres"]:
            raise ConnectionError("PostgreSQL pool niet beschikbaar")

        try:
            async with self.pools["postgres"].acquire() as conn:
                yield conn
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise

    @asynccontextmanager
    async def get_http_session(self):
        """Context manager voor HTTP session."""
        if "http" not in self.pools or not self.health_checks["http"]:
            raise ConnectionError("HTTP pool niet beschikbaar")

        try:
            yield self.pools["http"]
        except Exception as e:
            logger.error(f"HTTP session error: {e}")
            raise

    async def health_check(self, pool_name: str) -> bool:
        """
        Voer health check uit voor een specifieke pool.
        
        :param pool_name: Naam van de pool
        :return: True als pool gezond is
        """
        current_time = time.time()
        last_check = self.last_health_check.get(pool_name, 0)

        # Skip check als te recent
        if current_time - last_check < self.health_check_interval:
            return self.health_checks.get(pool_name, False)

        self.last_health_check[pool_name] = current_time

        try:
            if pool_name == "redis":
                async with self.get_redis_connection() as redis:
                    redis.ping()
                self.health_checks[pool_name] = True

            elif pool_name == "postgres":
                async with self.get_postgres_connection() as conn:
                    await conn.execute("SELECT 1")
                self.health_checks[pool_name] = True

            elif pool_name == "http":
                # HTTP session health check
                self.health_checks[pool_name] = True

            logger.debug(f"Health check {pool_name}: ✅")
            return True

        except Exception as e:
            logger.warning(f"Health check {pool_name} gefaald: {e}")
            self.health_checks[pool_name] = False
            return False

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Voer health check uit voor alle pools.
        
        :return: Dict met health status per pool
        """
        results = {}
        for pool_name in self.pools.keys():
            results[pool_name] = await self.health_check(pool_name)
        return results

    def get_pool_stats(self) -> Dict[str, Any]:
        """
        Haal statistieken op van alle pools.
        
        :return: Pool statistieken
        """
        stats = {}

        for pool_name, pool in self.pools.items():
            try:
                if pool_name == "redis":
                    redis_client = Redis(connection_pool=pool)
                    info = redis_client.info()
                    stats[pool_name] = {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory_human": info.get("used_memory_human", "0B"),
                        "total_commands_processed": info.get("total_commands_processed", 0),
                    }

                elif pool_name == "postgres":
                    stats[pool_name] = {
                        "min_size": pool.get_min_size(),
                        "max_size": pool.get_max_size(),
                        "size": pool.get_size(),
                        "free_size": pool.get_free_size(),
                    }

                elif pool_name == "http":
                    stats[pool_name] = {
                        "limit": pool.connector.limit,
                        "limit_per_host": pool.connector.limit_per_host,
                    }

            except Exception as e:
                logger.warning(f"Stats error voor {pool_name}: {e}")
                stats[pool_name] = {"error": str(e)}

        return stats

    async def close_all(self):
        """Sluit alle connection pools."""
        for pool_name, pool in self.pools.items():
            try:
                if pool_name == "http" or pool_name == "postgres":
                    await pool.close()
                elif pool_name == "redis":
                    pool.disconnect()

                logger.info(f"Pool {pool_name} gesloten")

            except Exception as e:
                logger.error(f"Error sluiten pool {pool_name}: {e}")

        self.pools.clear()
        self.health_checks.clear()

# Global connection pool manager
pool_manager = ConnectionPoolManager()

# Convenience functions
async def get_redis():
    """Convenience functie voor Redis connection."""
    async with pool_manager.get_redis_connection() as redis:
        return redis

async def get_postgres():
    """Convenience functie voor PostgreSQL connection."""
    async with pool_manager.get_postgres_connection() as conn:
        return conn

async def get_http_session():
    """Convenience functie voor HTTP session."""
    async with pool_manager.get_http_session() as session:
        return session
