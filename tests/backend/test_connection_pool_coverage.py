import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import bmad.agents.core.connection_pool as cp

@pytest.fixture(autouse=True)
def reset_pool_manager():
    # Reset global pool_manager before each test
    cp.pool_manager = cp.ConnectionPoolManager()
    yield
    cp.pool_manager = cp.ConnectionPoolManager()

class TestConnectionPoolManagerUnit:
    """Unit tests voor ConnectionPoolManager met mocks."""

    @patch('bmad.agents.core.connection_pool.RedisConnectionPool.from_url')
    @patch('bmad.agents.core.connection_pool.Redis')
    def test_init_redis_pool_success(self, mock_redis, mock_pool):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_pool.return_value = MagicMock()
        
        manager = cp.ConnectionPoolManager()
        asyncio.run(manager._init_redis_pool())
        assert 'redis' in manager.pools
        assert manager.health_checks['redis'] is True

    @patch('bmad.agents.core.connection_pool.RedisConnectionPool.from_url', side_effect=Exception("fail"))
    def test_init_redis_pool_fail(self, mock_pool):
        manager = cp.ConnectionPoolManager()
        asyncio.run(manager._init_redis_pool())
        assert manager.health_checks['redis'] is False

    @patch('bmad.agents.core.connection_pool.asyncpg.create_pool', new_callable=AsyncMock)
    def test_init_postgres_pool_success(self, mock_create_pool):
        # Mock the pool and connection
        pool = MagicMock()
        conn_mock = MagicMock()
        conn_mock.execute = AsyncMock(return_value=1)
        
        # Mock the pool.acquire method to return a context manager
        context_manager = MagicMock()
        context_manager.__aenter__ = AsyncMock(return_value=conn_mock)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        pool.acquire = MagicMock(return_value=context_manager)
        mock_create_pool.return_value = pool
        
        with patch.dict('os.environ', {'DATABASE_URL': 'postgres://user:pass@localhost/db'}):
            manager = cp.ConnectionPoolManager()
            asyncio.run(manager._init_postgres_pool())
            assert 'postgres' in manager.pools
            assert manager.health_checks['postgres'] is True

    @patch('bmad.agents.core.connection_pool.asyncpg.create_pool', side_effect=Exception("fail"))
    def test_init_postgres_pool_fail(self, mock_create_pool):
        with patch.dict('os.environ', {'DATABASE_URL': 'postgres://user:pass@localhost/db'}):
            manager = cp.ConnectionPoolManager()
            asyncio.run(manager._init_postgres_pool())
            assert manager.health_checks['postgres'] is False

    def test_init_postgres_pool_no_url(self):
        with patch.dict('os.environ', {}, clear=True):
            manager = cp.ConnectionPoolManager()
            asyncio.run(manager._init_postgres_pool())
            assert manager.health_checks['postgres'] is False

    @patch('bmad.agents.core.connection_pool.aiohttp.ClientSession')
    @patch('bmad.agents.core.connection_pool.aiohttp.TCPConnector')
    def test_init_http_pool_success(self, mock_connector, mock_session):
        mock_session.return_value = MagicMock()
        mock_connector.return_value = MagicMock()
        manager = cp.ConnectionPoolManager()
        asyncio.run(manager._init_http_pool())
        assert 'http' in manager.pools
        assert manager.health_checks['http'] is True

    @patch('bmad.agents.core.connection_pool.aiohttp.ClientSession', side_effect=Exception("fail"))
    @patch('bmad.agents.core.connection_pool.aiohttp.TCPConnector')
    def test_init_http_pool_fail(self, mock_connector, mock_session):
        manager = cp.ConnectionPoolManager()
        asyncio.run(manager._init_http_pool())
        assert manager.health_checks['http'] is False

    @patch('bmad.agents.core.connection_pool.Redis')
    def test_get_redis_connection_success(self, mock_redis):
        manager = cp.ConnectionPoolManager()
        manager.pools['redis'] = MagicMock()
        manager.health_checks['redis'] = True
        mock_redis.return_value = MagicMock()
        async def test():
            async with manager.get_redis_connection() as conn:
                assert conn is not None
        asyncio.run(test())

    def test_get_redis_connection_unavailable(self):
        manager = cp.ConnectionPoolManager()
        with pytest.raises(ConnectionError):
            async def test():
                async with manager.get_redis_connection():
                    pass
            asyncio.run(test())

    def test_get_postgres_connection_success(self):
        manager = cp.ConnectionPoolManager()
        pool = MagicMock()
        conn_mock = MagicMock()
        
        # Mock the pool.acquire method to return a context manager
        context_manager = MagicMock()
        context_manager.__aenter__ = AsyncMock(return_value=conn_mock)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        pool.acquire = MagicMock(return_value=context_manager)
        manager.pools['postgres'] = pool
        manager.health_checks['postgres'] = True
        async def test():
            async with manager.get_postgres_connection() as conn:
                assert conn is not None
        asyncio.run(test())

    def test_get_postgres_connection_unavailable(self):
        manager = cp.ConnectionPoolManager()
        with pytest.raises(ConnectionError):
            async def test():
                async with manager.get_postgres_connection():
                    pass
            asyncio.run(test())

    def test_get_http_session_success(self):
        manager = cp.ConnectionPoolManager()
        session = MagicMock()
        manager.pools['http'] = session
        manager.health_checks['http'] = True
        async def test():
            async with manager.get_http_session() as sess:
                assert sess is session
        asyncio.run(test())

    def test_get_http_session_unavailable(self):
        manager = cp.ConnectionPoolManager()
        with pytest.raises(ConnectionError):
            async def test():
                async with manager.get_http_session():
                    pass
            asyncio.run(test())

    @patch('bmad.agents.core.connection_pool.Redis')
    def test_get_pool_stats_redis(self, mock_redis):
        manager = cp.ConnectionPoolManager()
        pool = MagicMock()
        manager.pools['redis'] = pool
        mock_redis.return_value.info.return_value = {
            'connected_clients': 2,
            'used_memory_human': '1MB',
            'total_commands_processed': 100
        }
        stats = manager.get_pool_stats()
        assert stats['redis']['connected_clients'] == 2

    def test_get_pool_stats_postgres(self):
        manager = cp.ConnectionPoolManager()
        pool = MagicMock()
        pool.get_min_size.return_value = 1
        pool.get_max_size.return_value = 10
        pool.get_size.return_value = 5
        pool.get_free_size.return_value = 3
        manager.pools['postgres'] = pool
        stats = manager.get_pool_stats()
        assert stats['postgres']['min_size'] == 1

    def test_get_pool_stats_http(self):
        manager = cp.ConnectionPoolManager()
        connector = MagicMock()
        connector.limit = 10
        connector.limit_per_host = 5
        session = MagicMock()
        session.connector = connector
        manager.pools['http'] = session
        stats = manager.get_pool_stats()
        assert stats['http']['limit'] == 10

    def test_get_pool_stats_error(self):
        manager = cp.ConnectionPoolManager()
        pool = MagicMock()
        pool.get_min_size.side_effect = Exception("fail")
        manager.pools['postgres'] = pool
        stats = manager.get_pool_stats()
        assert 'error' in stats['postgres']

    def test_close_all(self):
        manager = cp.ConnectionPoolManager()
        http_pool = AsyncMock()
        postgres_pool = AsyncMock()
        redis_pool = MagicMock()
        manager.pools = {'http': http_pool, 'postgres': postgres_pool, 'redis': redis_pool}
        manager.health_checks = {'http': True, 'postgres': True, 'redis': True}
        asyncio.run(manager.close_all())
        assert manager.pools == {}
        assert manager.health_checks == {}

    def test_convenience_functions(self):
        manager = cp.ConnectionPoolManager()
        # Redis
        manager.pools['redis'] = MagicMock()
        manager.health_checks['redis'] = True
        # Postgres
        pool = MagicMock()
        conn_mock = MagicMock()
        
        # Mock the pool.acquire method to return a context manager
        context_manager = MagicMock()
        context_manager.__aenter__ = AsyncMock(return_value=conn_mock)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        pool.acquire = MagicMock(return_value=context_manager)
        manager.pools['postgres'] = pool
        manager.health_checks['postgres'] = True
        # HTTP
        session = MagicMock()
        manager.pools['http'] = session
        manager.health_checks['http'] = True
        async def test():
            with patch.object(cp, 'pool_manager', manager):
                redis = await cp.get_redis()
                assert redis is not None
                pg = await cp.get_postgres()
                assert pg is not None
                http = await cp.get_http_session()
                assert http is not None
        asyncio.run(test())

# Optionele integratietests (draaien alleen als marker is gezet)
@pytest.mark.integration
class TestConnectionPoolIntegration:
    @pytest.mark.asyncio
    async def test_redis_integration(self):
        # Vereist draaiende Redis op REDIS_URL
        await cp.pool_manager._init_redis_pool()
        if not cp.pool_manager.health_checks.get('redis'):
            pytest.skip('Redis niet beschikbaar')
        async with cp.pool_manager.get_redis_connection() as redis:
            pong = redis.ping()
            assert pong is True or pong == b'PONG'

    @pytest.mark.asyncio
    async def test_postgres_integration(self):
        # Vereist draaiende Postgres op DATABASE_URL
        await cp.pool_manager._init_postgres_pool()
        if not cp.pool_manager.health_checks.get('postgres'):
            pytest.skip('Postgres niet beschikbaar')
        async with cp.pool_manager.get_postgres_connection() as conn:
            result = await conn.execute('SELECT 1')
            assert result is not None

    @pytest.mark.asyncio
    async def test_http_integration(self):
        await cp.pool_manager._init_http_pool()
        if not cp.pool_manager.health_checks.get('http'):
            pytest.skip('HTTP pool niet beschikbaar')
        async with cp.pool_manager.get_http_session() as session:
            assert session is not None 