#!/usr/bin/env python3
"""
Eenvoudige backend tests die wel werken.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
import json

# Fix import paths for moved modules
from bmad.agents.core.data.redis_cache import cache, cached
from bmad.agents.core.monitoring.monitoring import MetricsCollector, StructuredLogger, HealthChecker

class TestSimpleBackend(unittest.TestCase):
    
    def test_redis_cache_basic(self):
        """Test basic Redis cache functionality."""
        # Test set and get
        cache.set("test_key", "test_value", ttl=60)
        result = cache.get("test_key")
        self.assertEqual(result, "test_value")
        
        # Test delete
        cache.delete("test_key")
        result = cache.get("test_key")
        self.assertIsNone(result)
    
    def test_cache_decorator_simple(self):
        """Test simple cache decorator functionality."""
        call_count = 0
        
        @cached(ttl=60)
        def simple_function(a, b):
            nonlocal call_count
            call_count += 1
            return a + b
        
        # First call should execute function
        result1 = simple_function(5, 3)
        self.assertEqual(result1, 8)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = simple_function(5, 3)
        self.assertEqual(result2, 8)
        self.assertEqual(call_count, 1)  # Should not increment
    
    def test_monitoring_basic(self):
        """Test basic monitoring functionality."""
        collector = MetricsCollector()
        collector.record_metric("test_metric", 42.0, labels={"test": "value"})
        
        # Verify metric was recorded
        metrics = collector.get_metrics("test_metric")
        self.assertGreater(len(metrics), 0)
    
    def test_metrics_collector(self):
        """Test metrics collector functionality."""
        collector = MetricsCollector()
        collector.record_metric("test_prometheus", 123.0)
        
        prometheus_data = collector.get_prometheus_format()
        self.assertIsInstance(prometheus_data, str)
        self.assertIn("test_prometheus", prometheus_data)
    
    def test_health_checker(self):
        """Test health checker functionality."""
        checker = HealthChecker()
        # Verify health checker was created
        self.assertIsInstance(checker, HealthChecker)
    
    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = StructuredLogger()
        logger.log_event("test_event", "Test event message", test_data="value")
        # No assertion needed - just verify no exception

if __name__ == '__main__':
    unittest.main() 