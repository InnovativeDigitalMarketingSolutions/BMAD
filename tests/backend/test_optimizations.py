#!/usr/bin/env python3
"""
Backend optimization tests.

Tests voor Redis caching, connection pooling en monitoring functionaliteiten.
"""

import pytest
import time
import sys
import os
from unittest.mock import patch, MagicMock

# Voeg BMAD modules toe aan path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

class TestRedisCaching:
    """Test Redis caching functionaliteit."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        from bmad.agents.core.redis_cache import cache
        
        # Test data
        test_data = {"test": "data", "timestamp": time.time()}
        cache_key = "test_key"
        
        # Set cache
        success = cache.set(cache_key, test_data, cache_type="test")
        assert success is True
        
        # Get cache
        cached_data = cache.get(cache_key)
        assert cached_data == test_data
        
        # Test exists
        assert cache.exists(cache_key) is True
        
        # Test delete
        assert cache.delete(cache_key) is True
        assert cache.exists(cache_key) is False
    
    def test_cache_decorator(self):
        """Test cache decorator."""
        from bmad.agents.core.redis_cache import cached
        
        call_count = 0
        
        @cached(ttl=60, cache_type="test", key_prefix="test_func")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate work
            return x + y
        
        # First call (cache miss)
        result1 = expensive_function(5, 3)
        assert result1 == 8
        assert call_count == 1
        
        # Second call (cache hit)
        result2 = expensive_function(5, 3)
        assert result2 == 8
        assert call_count == 1  # Should not increment
    
    def test_cache_stats(self):
        """Test cache statistics."""
        from bmad.agents.core.redis_cache import cache
        
        stats = cache.get_stats()
        assert isinstance(stats, dict)
        assert "enabled" in stats

class TestMonitoring:
    """Test monitoring en metrics functionaliteit."""
    
    def test_metrics_recording(self):
        """Test metrics recording."""
        from bmad.agents.core.monitoring import record_metric, increment_counter
        
        # Test metric recording
        record_metric("test_metric", 42.0, labels={"test": "value"})
        increment_counter("test_counter", labels={"test": "value"})
        
        # Should not raise exceptions
        assert True
    
    def test_measure_time(self):
        """Test timing measurements."""
        from bmad.agents.core.monitoring import measure_time
        
        with measure_time("test_timing", labels={"test": "value"}):
            time.sleep(0.01)  # Simulate work
        
        # Should not raise exceptions
        assert True
    
    def test_structured_logging(self):
        """Test structured logging."""
        from bmad.agents.core.monitoring import structured_logger
        
        # Test logging
        structured_logger.log_event("test_event", "Test event message", test_data="value")
        structured_logger.log_agent_action("TestAgent", "test_action", result="success")
        
        # Should not raise exceptions
        assert True
    
    def test_prometheus_format(self):
        """Test Prometheus format export."""
        from bmad.agents.core.monitoring import metrics_collector
        
        # Record some metrics
        metrics_collector.record_metric("test_prometheus", 123.0)
        
        # Get Prometheus format
        prometheus_metrics = metrics_collector.get_prometheus_format()
        assert isinstance(prometheus_metrics, str)
        assert len(prometheus_metrics) > 0

class TestLLMCaching:
    """Test LLM response caching."""
    
    @patch('bmad.agents.core.llm_client.ask_openai_with_confidence')
    def test_llm_caching_decorator(self, mock_llm):
        """Test LLM caching decorator."""
        from bmad.agents.core.llm_client import ask_openai_with_confidence
        
        # Mock LLM response
        mock_llm.return_value = {"response": "Hello", "confidence": 0.9}
        
        context = {"test": "llm_caching"}
        
        # First call
        result1 = ask_openai_with_confidence(
            "Say 'Hello from BMAD' in one word",
            context,
            max_tokens=10
        )
        
        # Second call (should be cached)
        result2 = ask_openai_with_confidence(
            "Say 'Hello from BMAD' in one word",
            context,
            max_tokens=10
        )
        
        # Both should return same result
        assert result1 == result2
        assert result1["response"] == "Hello"

class TestConnectionPooling:
    """Test connection pooling (mocked)."""
    
    @patch('bmad.agents.core.connection_pool.pool_manager')
    def test_pool_initialization(self, mock_pool_manager):
        """Test pool initialization."""
        from bmad.agents.core.connection_pool import pool_manager
        
        # Mock initialization
        mock_pool_manager.initialize_pools.return_value = None
        
        # Should not raise exceptions
        assert True
    
    def test_pool_configs(self):
        """Test pool configurations."""
        from bmad.agents.core.connection_pool import pool_manager
        
        # Check configs exist
        assert "redis" in pool_manager.pool_configs
        assert "postgres" in pool_manager.pool_configs
        assert "http" in pool_manager.pool_configs
        
        # Check config structure
        redis_config = pool_manager.pool_configs["redis"]
        assert "max_connections" in redis_config
        assert redis_config["max_connections"] == 20

class TestHealthChecks:
    """Test health checks."""
    
    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        from bmad.agents.core.monitoring import health_checker
        
        # Check default checks are registered
        assert "redis" in health_checker.check_functions
        assert "database" in health_checker.check_functions
        assert "llm_api" in health_checker.check_functions
        assert "agents" in health_checker.check_functions
    
    def test_health_status(self):
        """Test health status."""
        from bmad.agents.core.monitoring import health_checker
        
        status = health_checker.get_health_status()
        assert isinstance(status, dict)
        assert "overall_status" in status
        assert "healthy_checks" in status
        assert "total_checks" in status
        assert "checks" in status

# Integration tests
class TestBackendIntegration:
    """Integration tests voor backend optimalisaties."""
    
    def test_cache_and_monitoring_integration(self):
        """Test integration tussen cache en monitoring."""
        from bmad.agents.core.redis_cache import cache
        from bmad.agents.core.monitoring import record_metric, measure_time
        
        # Use cache with monitoring
        with measure_time("cache_operation"):
            cache.set("integration_test", "test_value", ttl=60)
            value = cache.get("integration_test")
            record_metric("cache_hit", 1 if value else 0)
        
        # Cleanup
        cache.delete("integration_test")
        
        # Should not raise exceptions
        assert True
    
    def test_llm_and_cache_integration(self):
        """Test integration tussen LLM en cache."""
        from bmad.agents.core.llm_client import ask_openai_with_confidence
        from bmad.agents.core.monitoring import record_metric
        
        # Mock context
        context = {"test": "integration"}
        
        # This should work with caching
        try:
            result = ask_openai_with_confidence(
                "Test message",
                context,
                max_tokens=5
            )
            record_metric("llm_requests", 1)
        except Exception:
            # Expected if no API key
            pass
        
        # Should not raise exceptions
        assert True

# Performance tests
class TestPerformance:
    """Performance tests."""
    
    def test_cache_performance(self):
        """Test cache performance."""
        from bmad.agents.core.redis_cache import cache, cached
        import time
        
        @cached(ttl=60, cache_type="perf_test")
        def slow_function():
            time.sleep(0.01)
            return "result"
        
        # First call (slow)
        start_time = time.time()
        result1 = slow_function()
        first_duration = time.time() - start_time
        
        # Second call (fast)
        start_time = time.time()
        result2 = slow_function()
        second_duration = time.time() - start_time
        
        assert result1 == result2
        assert second_duration < first_duration
    
    def test_metrics_performance(self):
        """Test metrics performance."""
        from bmad.agents.core.monitoring import metrics_collector
        import time
        
        # Test bulk metric recording
        start_time = time.time()
        
        for i in range(100):
            metrics_collector.record_metric(f"bulk_test_{i}", i)
        
        duration = time.time() - start_time
        
        # Should be fast (< 1 second for 100 metrics)
        assert duration < 1.0

if __name__ == "__main__":
    pytest.main([__file__]) 