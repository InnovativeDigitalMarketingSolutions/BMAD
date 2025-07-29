#!/usr/bin/env python3
"""
Uitgebreide tests voor Redis cache module om coverage te verhogen.
"""

import pytest
import redis
from unittest.mock import patch, MagicMock
from bmad.agents.core.data.redis_cache import RedisCache, cached, cache


class TestRedisCacheCoverage:
    """Test RedisCache voor volledige coverage."""
    
    def test_redis_cache_initialization(self):
        """Test RedisCache initialisatie."""
        with patch('redis.from_url') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError("Connection failed")
            redis_cache = RedisCache()
            assert redis_cache.enabled is False  # Disabled when connection fails
            assert redis_cache.client is None
    
    def test_redis_cache_initialization_with_redis(self):
        """Test RedisCache initialisatie met Redis beschikbaar."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            assert redis_cache.enabled is True
            assert redis_cache.client is not None
    
    def test_redis_cache_initialization_connection_error(self):
        """Test RedisCache initialisatie met connection error."""
        with patch('redis.from_url', side_effect=redis.ConnectionError("Connection failed")):
            redis_cache = RedisCache()
            assert redis_cache.enabled is False
            assert redis_cache.client is None
    
    def test_set_with_redis_enabled(self):
        """Test set met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.set("test_key", "test_value", ttl=60)
            assert result is True
            mock_redis.setex.assert_called_once()
    
    def test_set_with_redis_disabled(self):
        """Test set met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        result = redis_cache.set("test_key", "test_value", ttl=60)
        assert result is False
    
    def test_set_with_redis_error(self):
        """Test set met Redis error."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.setex.side_effect = redis.RedisError("Redis error")
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.set("test_key", "test_value", ttl=60)
            assert result is False
    
    def test_get_with_redis_enabled(self):
        """Test get met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = '{"test": "value"}'  # decode_responses=True
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.get("test_key")
            assert result == {"test": "value"}
            mock_redis.get.assert_called_once_with("test_key")
    
    def test_get_with_redis_disabled(self):
        """Test get met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        result = redis_cache.get("test_key")
        assert result is None
    
    def test_get_with_redis_error(self):
        """Test get met Redis error."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.side_effect = redis.RedisError("Redis error")
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.get("test_key")
            assert result is None
    
    def test_get_with_invalid_json(self):
        """Test get met invalid JSON."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = 'invalid json'
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.get("test_key")
            assert result == 'invalid json'  # Returns raw value if JSON decode fails
    
    def test_get_with_none_value(self):
        """Test get met None value."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.get("test_key")
            assert result is None
    
    def test_delete_with_redis_enabled(self):
        """Test delete met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.delete.return_value = 1
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.delete("test_key")
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")
    
    def test_delete_with_redis_disabled(self):
        """Test delete met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        result = redis_cache.delete("test_key")
        assert result is False
    
    def test_delete_with_redis_error(self):
        """Test delete met Redis error."""
        mock_redis = MagicMock()
        mock_redis.delete.side_effect = Exception("Redis error")
        
        with patch('redis.Redis', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.delete("test_key")
            assert result is False
    
    def test_exists_with_redis_enabled(self):
        """Test exists met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 1
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.exists("test_key")
            assert result is True
            mock_redis.exists.assert_called_once_with("test_key")
    
    def test_exists_with_redis_disabled(self):
        """Test exists met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        result = redis_cache.exists("test_key")
        assert result is False
    
    def test_exists_with_redis_error(self):
        """Test exists met Redis error."""
        mock_redis = MagicMock()
        mock_redis.exists.side_effect = Exception("Redis error")
        
        with patch('redis.Redis', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.exists("test_key")
            assert result is False
    
    def test_clear_pattern_with_redis_enabled(self):
        """Test clear_pattern met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.keys.return_value = ["key1", "key2"]
        mock_redis.delete.return_value = 2
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.clear_pattern("test:*")
            assert result == 2
            mock_redis.keys.assert_called_once_with("test:*")
            mock_redis.delete.assert_called_once_with("key1", "key2")
    
    def test_clear_pattern_with_redis_disabled(self):
        """Test clear_pattern met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        result = redis_cache.clear_pattern("test:*")
        assert result == 0
    
    def test_clear_pattern_with_redis_error(self):
        """Test clear_pattern met Redis error."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.keys.side_effect = redis.RedisError("Redis error")
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            result = redis_cache.clear_pattern("test:*")
            assert result == 0
    
    def test_get_stats_with_redis_enabled(self):
        """Test get_stats met Redis enabled."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.info.return_value = {
            "connected_clients": 5,
            "used_memory_human": "1.2M",
            "keyspace_hits": 100,
            "keyspace_misses": 20,
            "total_commands_processed": 500
        }
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            stats = redis_cache.get_stats()
            
            assert stats["enabled"] is True
            assert stats["connected_clients"] == 5
            assert stats["used_memory_human"] == "1.2M"
            assert stats["keyspace_hits"] == 100
            assert stats["keyspace_misses"] == 20
            assert stats["total_commands_processed"] == 500
    
    def test_get_stats_with_redis_disabled(self):
        """Test get_stats met Redis disabled."""
        redis_cache = RedisCache()
        redis_cache.enabled = False
        
        stats = redis_cache.get_stats()
        
        assert stats["enabled"] is False
    
    def test_get_stats_with_redis_error(self):
        """Test get_stats met Redis error."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.info.side_effect = redis.RedisError("Redis error")
        
        with patch('redis.from_url', return_value=mock_redis):
            redis_cache = RedisCache()
            
            stats = redis_cache.get_stats()
            
            assert stats["enabled"] is False
            assert "error" in stats


class TestCachedDecoratorCoverage:
    """Test cached decorator voor volledige coverage."""
    
    def test_cached_decorator_basic(self):
        """Test cached decorator basic functionaliteit."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.client = mock_redis
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y):
                return x + y
            
            result = test_function(5, 3)
            assert result == 8
            
            # Check that cache was used
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()
    
    def test_cached_decorator_cache_hit(self):
        """Test cached decorator met cache hit."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.client = mock_redis
            mock_cache.get.return_value = 8  # Cache hit
            mock_cache.set.return_value = True
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y):
                return x + y
            
            result = test_function(5, 3)
            assert result == 8
            
            # Check that cache was used but not set again
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_not_called()
    
    def test_cached_decorator_with_redis_disabled(self):
        """Test cached decorator met Redis disabled."""
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = False
            mock_cache.get.return_value = None
            mock_cache.set.return_value = False
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y):
                return x + y
            
            result = test_function(5, 3)
            assert result == 8
    
    def test_cached_decorator_with_redis_error(self):
        """Test cached decorator met Redis error."""
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.get.side_effect = redis.RedisError("Redis error")
            mock_cache.set.return_value = False
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y):
                return x + y
            
            # The decorator should propagate the Redis error
            with pytest.raises(redis.RedisError):
                test_function(5, 3)
    
    def test_cached_decorator_with_complex_arguments(self):
        """Test cached decorator met complexe argumenten."""
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(data, options=None):
                return {"data": data, "options": options}
            
            result = test_function({"key": "value"}, {"option": "test"})
            assert result == {"data": {"key": "value"}, "options": {"option": "test"}}
    
    def test_cached_decorator_with_kwargs(self):
        """Test cached decorator met kwargs."""
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y, z=10):
                return x + y + z
            
            result = test_function(5, 3, z=20)
            assert result == 28
    
    def test_cached_decorator_key_generation(self):
        """Test cached decorator key generatie."""
        with patch('bmad.agents.core.redis_cache.cache') as mock_cache:
            mock_cache.enabled = True
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_cache._generate_key.return_value = "test_key"
            
            @cached(ttl=60, cache_type="test", key_prefix="test_func")
            def test_function(x, y):
                return x + y
            
            test_function(5, 3)
            
            # Check that the key generation was called
            mock_cache._generate_key.assert_called_once()
            call_args = mock_cache._generate_key.call_args[0]
            assert "test_func" in call_args
            assert "test_function" in call_args


class TestGlobalCacheInstance:
    """Test globale cache instance."""
    
    def test_global_cache_instance_exists(self):
        """Test dat globale cache instance bestaat."""
        assert cache is not None
        assert isinstance(cache, RedisCache)
    
    def test_global_cache_operations(self):
        """Test globale cache operations."""
        # Test basic operations - these should work even with Redis disabled
        result_set = cache.set("test_key", "test_value", ttl=60)
        result_get = cache.get("test_key")
        result_exists = cache.exists("test_key")
        result_delete = cache.delete("test_key")
        
        # These should return appropriate values even if Redis is disabled
        assert isinstance(result_set, bool)
        assert isinstance(result_exists, bool)
        assert isinstance(result_delete, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 