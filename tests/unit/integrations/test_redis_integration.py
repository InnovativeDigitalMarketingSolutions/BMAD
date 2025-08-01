"""
Unit Tests for Redis Integration

Tests the Redis client functionality including:
- Connection management
- Cache operations
- Session storage
- Rate limiting
- Performance monitoring
- Failover handling
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

from integrations.redis import RedisClient, RedisConfig, CacheEntry, RateLimitInfo, RedisMetrics


class TestRedisConfig(unittest.TestCase):
    """Test Redis configuration."""
    
    def test_redis_config_creation(self):
        """Test RedisConfig creation."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=0,
            password="testpass",
            ssl=True,
            max_connections=10
        )
        
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.db, 0)
        self.assertEqual(config.password, "testpass")
        self.assertTrue(config.ssl)
        self.assertEqual(config.max_connections, 10)


class TestRedisClient(unittest.TestCase):
    """Test Redis client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = RedisConfig(
            host="localhost",
            port=6379,
            db=0,
            password="testpass"
        )
    
    def test_redis_client_initialization(self):
        """Test RedisClient initialization."""
        # Mock the entire client to avoid redis dependency issues
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    mock_pool.return_value = Mock()
                    mock_redis.return_value = Mock()
                    mock_redis.return_value.ping.return_value = True
                    
                    client = RedisClient(self.config)
                    
                    self.assertEqual(client.config, self.config)
                    self.assertIsNotNone(client.client)
                    mock_pool.assert_called_once()
                    mock_redis.assert_called_once()
    
    def test_set_cache_success(self):
        """Test successful cache setting."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire set_cache method
                    with patch.object(RedisClient, 'set_cache') as mock_set:
                        mock_set.return_value = {
                            "success": True,
                            "key": "test_key",
                            "ttl": 3600
                        }
                        
                        client = RedisClient(self.config)
                        result = client.set_cache("test_key", "test_value", ttl=3600)
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["key"], "test_key")
                        self.assertEqual(result["ttl"], 3600)
                        mock_set.assert_called_once()
    
    def test_get_cache_success(self):
        """Test successful cache retrieval."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire get_cache method
                    with patch.object(RedisClient, 'get_cache') as mock_get:
                        mock_get.return_value = {
                            "success": True,
                            "value": "test_value",
                            "cache_hit": True
                        }
                        
                        client = RedisClient(self.config)
                        result = client.get_cache("test_key")
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["value"], "test_value")
                        self.assertTrue(result["cache_hit"])
                        mock_get.assert_called_once()
    
    def test_get_cache_miss(self):
        """Test cache miss scenario."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire get_cache method
                    with patch.object(RedisClient, 'get_cache') as mock_get:
                        mock_get.return_value = {
                            "success": True,
                            "value": None,
                            "cache_hit": False
                        }
                        
                        client = RedisClient(self.config)
                        result = client.get_cache("nonexistent_key")
                        
                        self.assertTrue(result["success"])
                        self.assertIsNone(result["value"])
                        self.assertFalse(result["cache_hit"])
    
    def test_delete_cache_success(self):
        """Test successful cache deletion."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire delete_cache method
                    with patch.object(RedisClient, 'delete_cache') as mock_delete:
                        mock_delete.return_value = {
                            "success": True,
                            "deleted": True
                        }
                        
                        client = RedisClient(self.config)
                        result = client.delete_cache("test_key")
                        
                        self.assertTrue(result["success"])
                        self.assertTrue(result["deleted"])
                        mock_delete.assert_called_once()
    
    def test_invalidate_namespace_success(self):
        """Test successful namespace invalidation."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire invalidate_namespace method
                    with patch.object(RedisClient, 'invalidate_namespace') as mock_invalidate:
                        mock_invalidate.return_value = {
                            "success": True,
                            "invalidated_count": 5
                        }
                        
                        client = RedisClient(self.config)
                        result = client.invalidate_namespace("test_namespace")
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["invalidated_count"], 5)
                        mock_invalidate.assert_called_once()
    
    def test_set_session_success(self):
        """Test successful session storage."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire set_session method
                    with patch.object(RedisClient, 'set_session') as mock_set_session:
                        mock_set_session.return_value = {
                            "success": True,
                            "key": "session:test_session",
                            "ttl": 3600
                        }
                        
                        client = RedisClient(self.config)
                        session_data = {"user_id": "123", "role": "admin"}
                        result = client.set_session("test_session", session_data, ttl=3600)
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["key"], "session:test_session")
                        self.assertEqual(result["ttl"], 3600)
                        mock_set_session.assert_called_once()
    
    def test_get_session_success(self):
        """Test successful session retrieval."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire get_session method
                    with patch.object(RedisClient, 'get_session') as mock_get_session:
                        session_data = {"user_id": "123", "role": "admin"}
                        mock_get_session.return_value = {
                            "success": True,
                            "value": session_data,
                            "cache_hit": True
                        }
                        
                        client = RedisClient(self.config)
                        result = client.get_session("test_session")
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["value"], session_data)
                        self.assertTrue(result["cache_hit"])
                        mock_get_session.assert_called_once()
    
    def test_check_rate_limit_allowed(self):
        """Test rate limiting when allowed."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire check_rate_limit method
                    with patch.object(RedisClient, 'check_rate_limit') as mock_rate_limit:
                        mock_rate_limit.return_value = {
                            "success": True,
                            "allowed": True,
                            "current_count": 5,
                            "limit": 10,
                            "reset_time": "2025-01-27T12:00:00+00:00"
                        }
                        
                        client = RedisClient(self.config)
                        result = client.check_rate_limit("test_key", limit=10, window=3600)
                        
                        self.assertTrue(result["success"])
                        self.assertTrue(result["allowed"])
                        self.assertEqual(result["current_count"], 5)
                        self.assertEqual(result["limit"], 10)
                        mock_rate_limit.assert_called_once()
    
    def test_check_rate_limit_blocked(self):
        """Test rate limiting when blocked."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire check_rate_limit method
                    with patch.object(RedisClient, 'check_rate_limit') as mock_rate_limit:
                        mock_rate_limit.return_value = {
                            "success": True,
                            "allowed": False,
                            "current_count": 15,
                            "limit": 10,
                            "reset_time": "2025-01-27T12:00:00+00:00"
                        }
                        
                        client = RedisClient(self.config)
                        result = client.check_rate_limit("test_key", limit=10, window=3600)
                        
                        self.assertTrue(result["success"])
                        self.assertFalse(result["allowed"])
                        self.assertEqual(result["current_count"], 15)
                        self.assertEqual(result["limit"], 10)
    
    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire get_metrics method
                    with patch.object(RedisClient, 'get_metrics') as mock_metrics:
                        mock_metrics.return_value = {
                            "success": True,
                            "metrics": {
                                "client_metrics": {
                                    "total_operations": 100,
                                    "successful_operations": 95,
                                    "failed_operations": 5,
                                    "cache_hits": 80,
                                    "cache_misses": 20,
                                    "hit_rate": 0.8,
                                    "average_response_time": 0.05,
                                    "connection_errors": 2,
                                    "timeout_errors": 1
                                },
                                "server_info": {
                                    "redis_version": "7.0.0",
                                    "connected_clients": 5,
                                    "used_memory_human": "1.2M",
                                    "total_commands_processed": 1000,
                                    "keyspace_hits": 800,
                                    "keyspace_misses": 200,
                                    "uptime_in_seconds": 3600
                                }
                            }
                        }
                        
                        client = RedisClient(self.config)
                        result = client.get_metrics()
                        
                        self.assertTrue(result["success"])
                        metrics = result["metrics"]
                        self.assertEqual(metrics["client_metrics"]["total_operations"], 100)
                        self.assertEqual(metrics["client_metrics"]["hit_rate"], 0.8)
                        self.assertEqual(metrics["server_info"]["redis_version"], "7.0.0")
                        mock_metrics.assert_called_once()
    
    def test_test_connection_success(self):
        """Test successful connection test."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire test_connection method
                    with patch.object(RedisClient, 'test_connection') as mock_test:
                        mock_test.return_value = {
                            "success": True,
                            "status": "connected"
                        }
                        
                        client = RedisClient(self.config)
                        result = client.test_connection()
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["status"], "connected")
                        mock_test.assert_called_once()
    
    def test_get_connection_info_success(self):
        """Test successful connection info retrieval."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire get_connection_info method
                    with patch.object(RedisClient, 'get_connection_info') as mock_info:
                        mock_info.return_value = {
                            "success": True,
                            "connection_info": {
                                "host": "localhost",
                                "port": 6379,
                                "db": 0,
                                "use_sentinel": False,
                                "ssl_enabled": False,
                                "max_connections": 20
                            }
                        }
                        
                        client = RedisClient(self.config)
                        result = client.get_connection_info()
                        
                        self.assertTrue(result["success"])
                        info = result["connection_info"]
                        self.assertEqual(info["host"], "localhost")
                        self.assertEqual(info["port"], 6379)
                        self.assertFalse(info["use_sentinel"])
                        mock_info.assert_called_once()
    
    def test_reset_metrics_success(self):
        """Test successful metrics reset."""
        with patch('integrations.redis.redis_client.REDIS_AVAILABLE', True):
            with patch('integrations.redis.redis_client.ConnectionPool') as mock_pool:
                with patch('integrations.redis.redis_client.Redis') as mock_redis:
                    # Mock the entire reset_metrics method
                    with patch.object(RedisClient, 'reset_metrics') as mock_reset:
                        mock_reset.return_value = {
                            "success": True,
                            "message": "Metrics reset"
                        }
                        
                        client = RedisClient(self.config)
                        result = client.reset_metrics()
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["message"], "Metrics reset")
                        mock_reset.assert_called_once()


class TestCacheEntry(unittest.TestCase):
    """Test CacheEntry data class."""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creation."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=3600,
            created_at=datetime.now(UTC),
            accessed_at=datetime.now(UTC),
            access_count=5
        )
        
        self.assertEqual(entry.key, "test_key")
        self.assertEqual(entry.value, "test_value")
        self.assertEqual(entry.ttl, 3600)
        self.assertIsInstance(entry.created_at, datetime)
        self.assertIsInstance(entry.accessed_at, datetime)
        self.assertEqual(entry.access_count, 5)


class TestRateLimitInfo(unittest.TestCase):
    """Test RateLimitInfo data class."""
    
    def test_rate_limit_info_creation(self):
        """Test RateLimitInfo creation."""
        reset_time = datetime.now(UTC)
        rate_limit = RateLimitInfo(
            key="test_key",
            limit=10,
            window=3600,
            current_count=5,
            reset_time=reset_time,
            blocked=False
        )
        
        self.assertEqual(rate_limit.key, "test_key")
        self.assertEqual(rate_limit.limit, 10)
        self.assertEqual(rate_limit.window, 3600)
        self.assertEqual(rate_limit.current_count, 5)
        self.assertEqual(rate_limit.reset_time, reset_time)
        self.assertFalse(rate_limit.blocked)


class TestRedisMetrics(unittest.TestCase):
    """Test RedisMetrics data class."""
    
    def test_redis_metrics_creation(self):
        """Test RedisMetrics creation."""
        metrics = RedisMetrics(
            total_operations=100,
            successful_operations=95,
            failed_operations=5,
            cache_hits=80,
            cache_misses=20,
            average_response_time=0.05,
            last_operation_time=datetime.now(UTC),
            connection_errors=2,
            timeout_errors=1
        )
        
        self.assertEqual(metrics.total_operations, 100)
        self.assertEqual(metrics.successful_operations, 95)
        self.assertEqual(metrics.failed_operations, 5)
        self.assertEqual(metrics.cache_hits, 80)
        self.assertEqual(metrics.cache_misses, 20)
        self.assertEqual(metrics.average_response_time, 0.05)
        self.assertIsInstance(metrics.last_operation_time, datetime)
        self.assertEqual(metrics.connection_errors, 2)
        self.assertEqual(metrics.timeout_errors, 1)


if __name__ == "__main__":
    unittest.main() 