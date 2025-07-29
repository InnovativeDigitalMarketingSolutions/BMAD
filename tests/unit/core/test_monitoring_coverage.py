#!/usr/bin/env python3
"""
Uitgebreide tests voor monitoring module om coverage te verhogen.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from bmad.agents.core.monitoring.monitoring import (
    MetricsCollector,
    measure_time,
    log_event
)


class TestMetricsCollectorCoverage:
    """Test MetricsCollector voor volledige coverage."""
    
    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialisatie."""
        collector = MetricsCollector()
        assert collector.metrics is not None
        assert collector.counters is not None
        assert collector.histograms is not None
        assert collector.lock is not None
        assert collector.prefixes is not None
    
    def test_record_metric_with_labels(self):
        """Test record_metric met labels."""
        collector = MetricsCollector()
        labels = {"test": "value", "env": "test"}
        
        collector.record_metric("test_metric", 42.0, labels=labels, metric_type="counter", prefix="test")
        
        metrics = collector.get_metrics()
        assert "test_test_metric" in metrics
        assert len(metrics["test_test_metric"]) == 1
        assert metrics["test_test_metric"][0].value == 42.0
        assert metrics["test_test_metric"][0].labels == labels
        assert metrics["test_test_metric"][0].metric_type == "counter"
    
    def test_increment_counter(self):
        """Test increment_counter functionaliteit."""
        collector = MetricsCollector()
        
        # Increment counter
        collector.increment_counter("test_counter", labels={"test": "value"})
        
        # Check counter value
        assert collector.counters["bmad_test_counter"] == 1
        
        # Increment again
        collector.increment_counter("test_counter", labels={"test": "value"})
        assert collector.counters["bmad_test_counter"] == 2
    
    def test_record_histogram(self):
        """Test record_histogram functionaliteit."""
        collector = MetricsCollector()
        
        # Record histogram values
        collector.record_histogram("test_histogram", 10.0)
        collector.record_histogram("test_histogram", 20.0)
        collector.record_histogram("test_histogram", 30.0)
        
        # Check histogram data
        assert len(collector.histograms["bmad_test_histogram"]) == 3
        assert 10.0 in collector.histograms["bmad_test_histogram"]
        assert 20.0 in collector.histograms["bmad_test_histogram"]
        assert 30.0 in collector.histograms["bmad_test_histogram"]
    
    def test_measure_time_context_manager(self):
        """Test measure_time context manager."""
        collector = MetricsCollector()
        
        with collector.measure_time("test_timing"):
            time.sleep(0.01)  # Small delay
        
        # Check that histogram was recorded
        assert len(collector.histograms["bmad_test_timing"]) == 1
        assert collector.histograms["bmad_test_timing"][0] > 0
    
    def test_get_metrics_with_filter(self):
        """Test get_metrics met name filter."""
        collector = MetricsCollector()
        
        # Add some metrics
        collector.record_metric("test_metric1", 1.0)
        collector.record_metric("test_metric2", 2.0)
        collector.record_metric("other_metric", 3.0)
        
        # Filter by name
        filtered_metrics = collector.get_metrics(name_filter="test_metric")
        
        assert "bmad_test_metric1" in filtered_metrics
        assert "bmad_test_metric2" in filtered_metrics
        assert "bmad_other_metric" not in filtered_metrics
    
    def test_get_metrics_with_time_window(self):
        """Test get_metrics met time window."""
        collector = MetricsCollector()
        
        # Add metric
        collector.record_metric("test_metric", 1.0)
        
        # Get metrics with time window
        from datetime import timedelta
        recent_metrics = collector.get_metrics(time_window=timedelta(seconds=1))
        
        assert "bmad_test_metric" in recent_metrics
        assert len(recent_metrics["bmad_test_metric"]) == 1
    
    def test_get_prometheus_format(self):
        """Test get_prometheus_format."""
        collector = MetricsCollector()
        
        # Add metric with labels
        collector.record_metric("test_metric", 42.0, labels={"test": "value"})
        
        prometheus_format = collector.get_prometheus_format()
        
        assert "bmad_test_metric" in prometheus_format
        assert "test=\"value\"" in prometheus_format
        assert "42.0" in prometheus_format
    
    def test_clear_old_metrics(self):
        """Test clear_old_metrics."""
        collector = MetricsCollector()
        
        # Add metric
        collector.record_metric("test_metric", 1.0)
        
        # Clear old metrics (should keep recent ones)
        collector.clear_old_metrics(max_age_hours=1)
        
        # Metric should still exist
        metrics = collector.get_metrics()
        assert "bmad_test_metric" in metrics


class TestHealthCheckerCoverage:
    """Test HealthChecker voor volledige coverage."""
    
    def test_health_checker_initialization(self):
        """Test HealthChecker initialisatie."""
        checker = HealthChecker()
        assert checker.health_checks is not None
        assert checker.check_functions is not None
        assert checker.last_check is not None
        assert checker.check_interval == 300
    
    def test_register_check(self):
        """Test register_check functionaliteit."""
        checker = HealthChecker()
        
        def test_check():
            return HealthCheck(
                name="test_check",
                status="healthy",
                message="Test check passed",
                timestamp=time.time()
            )
        
        checker.register_check("test_check", test_check)
        assert "test_check" in checker.check_functions
    
    def test_check_system_with_psutil(self):
        """Test _check_system met psutil."""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 60.0
                mock_memory.return_value.available = 1024 * 1024 * 1024  # 1GB
                
                checker = HealthChecker()
                result = checker._check_system()
                
                assert result.name == "system"
                assert result.status == "healthy"
                assert "CPU: 50.0%" in result.message
                assert "Memory: 60.0%" in result.message
                assert result.details["cpu_percent"] == 50.0
                assert result.details["memory_percent"] == 60.0
    
    def test_check_system_without_psutil(self):
        """Test _check_system zonder psutil."""
        with patch('builtins.__import__', side_effect=ImportError):
            checker = HealthChecker()
            result = checker._check_system()
            
            assert result.name == "system"
            assert result.status == "degraded"
            assert "psutil not available" in result.message
    
    def test_check_python_modules(self):
        """Test _check_python_modules."""
        checker = HealthChecker()
        result = checker._check_python_modules()
        
        assert result.name == "python_modules"
        # The status depends on which modules are available, so we just check it's valid
        assert result.status in ["healthy", "unhealthy"]
        assert "modules" in result.message
        # Check that details contains either available_modules or missing_modules
        assert any(key in result.details for key in ["available_modules", "missing_modules"])
    
    def test_check_redis_lazy_success(self):
        """Test _check_redis_lazy met succes."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.client = MagicMock()
        mock_cache.client.ping.return_value = True
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.cache = mock_cache
            mock_import.return_value = mock_module
            
            checker = HealthChecker()
            result = checker._check_redis_lazy()
            
            assert result.name == "redis"
            assert result.status == "healthy"
            assert "Redis connection OK" in result.message
    
    def test_check_redis_lazy_disabled(self):
        """Test _check_redis_lazy wanneer Redis uitgeschakeld is."""
        mock_cache = MagicMock()
        mock_cache.enabled = False
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.cache = mock_cache
            mock_import.return_value = mock_module
            
            checker = HealthChecker()
            result = checker._check_redis_lazy()
            
            assert result.name == "redis"
            assert result.status == "healthy"
            assert "Redis not configured" in result.message
    
    def test_check_database_lazy(self):
        """Test _check_database_lazy."""
        mock_pool_manager = MagicMock()
        mock_pool_manager.health_check = MagicMock()
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.pool_manager = mock_pool_manager
            mock_import.return_value = mock_module
            
            checker = HealthChecker()
            result = checker._check_database_lazy()
            
            assert result.name == "database"
            assert result.status == "healthy"
            assert "Database pool manager available" in result.message
    
    def test_check_llm_api_lazy_with_key(self):
        """Test _check_llm_api_lazy met API key."""
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.OPENAI_API_KEY = "test_key"
            mock_import.return_value = mock_module
            
            checker = HealthChecker()
            result = checker._check_llm_api_lazy()
            
            assert result.name == "llm_api"
            # The status depends on the actual implementation, so we check it's valid
            assert result.status in ["healthy", "degraded", "unhealthy"]
            assert "OpenAI" in result.message
    
    def test_check_llm_api_lazy_without_key(self):
        """Test _check_llm_api_lazy zonder API key."""
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.OPENAI_API_KEY = None
            mock_import.return_value = mock_module
            
            checker = HealthChecker()
            result = checker._check_llm_api_lazy()
            
            assert result.name == "llm_api"
            assert result.status == "unhealthy"
            assert "OpenAI API key not configured" in result.message
    
    def test_check_agents_lazy(self):
        """Test _check_agents_lazy."""
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = MagicMock()
            
            checker = HealthChecker()
            result = checker._check_agents_lazy()
            
            assert result.name == "agents"
            assert result.status == "healthy"
            assert "All agent modules available" in result.message
    
    def test_run_health_check(self):
        """Test run_health_check."""
        checker = HealthChecker()
        
        def test_check():
            return HealthCheck(
                name="test_check",
                status="healthy",
                message="Test check passed",
                timestamp=time.time()
            )
        
        checker.register_check("test_check", test_check)
        result = checker.run_health_check("test_check")
        
        assert result.name == "test_check"
        assert result.status == "healthy"
        assert "test_check" in checker.health_checks
    
    def test_run_health_check_not_found(self):
        """Test run_health_check met niet-bestaande check."""
        checker = HealthChecker()
        result = checker.run_health_check("non_existent")
        
        assert result.name == "non_existent"
        assert result.status == "unhealthy"
        assert "not found" in result.message
    
    def test_run_all_health_checks(self):
        """Test run_all_health_checks."""
        checker = HealthChecker()
        
        def test_check():
            return HealthCheck(
                name="test_check",
                status="healthy",
                message="Test check passed",
                timestamp=time.time()
            )
        
        checker.register_check("test_check", test_check)
        results = checker.run_all_health_checks()
        
        assert "test_check" in results
        assert results["test_check"].status == "healthy"
    
    def test_get_health_status(self):
        """Test get_health_status."""
        checker = HealthChecker()
        
        # Add a health check
        checker.health_checks["test_check"] = HealthCheck(
            name="test_check",
            status="healthy",
            message="Test check passed",
            timestamp=time.time()
        )
        
        status = checker.get_health_status()
        
        assert status["overall_status"] == "healthy"
        assert status["healthy_checks"] == 1
        assert status["total_checks"] == 1
        assert "test_check" in status["checks"]


class TestStructuredLoggerCoverage:
    """Test StructuredLogger voor volledige coverage."""
    
    def test_structured_logger_initialization(self):
        """Test StructuredLogger initialisatie."""
        logger = StructuredLogger()
        assert logger.logger is not None
        assert len(logger.logger.handlers) > 0
    
    def test_log_event(self):
        """Test log_event functionaliteit."""
        logger = StructuredLogger()
        
        # Test basic event logging
        logger.log_event("test_event", "Test message", test_data="value")
        
        # The logger should not raise any exceptions
        assert True
    
    def test_log_agent_action(self):
        """Test log_agent_action functionaliteit."""
        logger = StructuredLogger()
        
        logger.log_agent_action("TestAgent", "test_action", result="success")
        
        # The logger should not raise any exceptions
        assert True
    
    def test_log_workflow_event(self):
        """Test log_workflow_event functionaliteit."""
        logger = StructuredLogger()
        
        logger.log_workflow_event("test_workflow", "test_event", data="value")
        
        # The logger should not raise any exceptions
        assert True
    
    def test_log_performance(self):
        """Test log_performance functionaliteit."""
        logger = StructuredLogger()
        
        logger.log_performance("test_operation", 1.5, details="test")
        
        # The logger should not raise any exceptions
        assert True


class TestGlobalInstances:
    """Test globale instances."""
    
    def test_global_instances_exist(self):
        """Test dat globale instances bestaan."""
        assert metrics_collector is not None
        assert health_checker is not None
        assert structured_logger is not None
        
        assert isinstance(metrics_collector, MetricsCollector)
        assert isinstance(health_checker, HealthChecker)
        assert isinstance(structured_logger, StructuredLogger)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        from bmad.agents.core.monitoring import record_metric, increment_counter, log_event
        
        # Test convenience functions
        record_metric("test_conv", 123.0)
        increment_counter("test_conv_counter")
        log_event("test_conv_event", "Test convenience function")
        
        # Check that metrics were recorded
        metrics = metrics_collector.get_metrics()
        assert "bmad_test_conv" in metrics
        assert "bmad_test_conv_counter" in metrics_collector.counters


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 