#!/usr/bin/env python3
"""
Eenvoudige backend tests die wel werken.
"""

import pytest
import time
import sys
import os

# Voeg BMAD modules toe aan path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

class TestSimpleBackend:
    """Eenvoudige backend tests."""
    
    def test_redis_cache_basic(self):
        """Test basic Redis cache functionaliteit."""
        from bmad.agents.core.redis_cache import cache
        
        # Test data
        test_data = {"test": "data", "timestamp": time.time()}
        cache_key = "simple_test_key"
        
        # Set cache
        success = cache.set(cache_key, test_data, cache_type="test")
        assert success is True
        
        # Get cache
        cached_data = cache.get(cache_key)
        assert cached_data == test_data
        
        # Cleanup
        cache.delete(cache_key)
        
        print("✅ Redis cache basic test passed")
    
    def test_cache_decorator_simple(self):
        """Test cache decorator zonder async."""
        from bmad.agents.core.redis_cache import cached
        
        call_count = 0
        
        @cached(ttl=60, cache_type="test", key_prefix="simple_func")
        def simple_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = simple_function(5, 3)
        assert result1 == 8
        assert call_count == 1
        
        # Second call (should be cached)
        result2 = simple_function(5, 3)
        assert result2 == 8
        assert call_count == 1  # Should not increment
        
        print("✅ Cache decorator test passed")
    
    def test_monitoring_basic(self):
        """Test basic monitoring zonder async."""
        from bmad.agents.core.monitoring import record_metric, increment_counter
        
        # Test metric recording
        record_metric("test_metric", 42.0, labels={"test": "value"})
        increment_counter("test_counter", labels={"test": "value"})
        
        # Should not raise exceptions
        assert True
        print("✅ Basic monitoring test passed")
    
    def test_metrics_collector(self):
        """Test metrics collector."""
        from bmad.agents.core.monitoring import metrics_collector
        
        # Record some metrics
        metrics_collector.record_metric("test_prometheus", 123.0)
        
        # Get Prometheus format
        prometheus_metrics = metrics_collector.get_prometheus_format()
        assert isinstance(prometheus_metrics, str)
        
        print("✅ Metrics collector test passed")
    
    def test_health_checker(self):
        """Test health checker initialization."""
        from bmad.agents.core.monitoring import health_checker
        
        # Check default checks are registered
        assert "redis" in health_checker.check_functions
        assert "database" in health_checker.check_functions
        assert "llm_api" in health_checker.check_functions
        assert "agents" in health_checker.check_functions
        
        print("✅ Health checker test passed")
    
    def test_structured_logging(self):
        """Test structured logging."""
        from bmad.agents.core.monitoring import structured_logger
        
        # Test logging
        structured_logger.log_event("test_event", "Test event message", test_data="value")
        structured_logger.log_agent_action("TestAgent", "test_action", result="success")
        
        # Should not raise exceptions
        assert True
        print("✅ Structured logging test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 