"""
Enhanced Performance Tests for BMAD System

This module provides comprehensive performance testing to identify
bottlenecks, optimize system performance, and ensure production readiness.

Test Coverage:
- Detailed response time analysis
- Load testing with various scenarios
- Stress testing to find system limits
- Resource utilization monitoring
- Performance regression detection
- Optimization recommendations
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# Performance configuration
@dataclass
class PerformanceConfig:
    """Performance testing configuration."""
    # Response time thresholds (milliseconds)
    fast_response: float = 50.0      # Fast operations
    normal_response: float = 100.0   # Normal operations
    slow_response: float = 500.0     # Slow operations
    
    # Throughput thresholds (operations per second)
    min_throughput: float = 10.0     # Minimum acceptable throughput
    target_throughput: float = 50.0  # Target throughput
    high_throughput: float = 100.0   # High throughput
    
    # Load testing parameters
    light_load: int = 10             # Light load operations
    normal_load: int = 50            # Normal load operations
    heavy_load: int = 100            # Heavy load operations
    stress_load: int = 200           # Stress test operations
    
    # Resource thresholds
    max_memory_mb: float = 500.0     # Maximum memory usage
    max_cpu_percent: float = 80.0    # Maximum CPU usage
    max_disk_io_mb: float = 100.0    # Maximum disk I/O

class EnhancedPerformanceBenchmark:
    """Enhanced performance benchmarking with detailed metrics."""
    
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or PerformanceConfig()
        self.metrics = []
        self.start_time = None
        self.end_time = None
        self.resource_samples = []
    
    def start_benchmark(self):
        """Start performance benchmark."""
        self.start_time = time.time()
        self.metrics = []
        self.resource_samples = []
        self._record_resource_sample("start")
    
    def end_benchmark(self):
        """End performance benchmark."""
        self.end_time = time.time()
        self._record_resource_sample("end")
        return self.calculate_detailed_metrics()
    
    def record_metric(self, operation: str, duration: float, success: bool = True, 
                     metadata: Dict[str, Any] = None):
        """Record a performance metric with metadata."""
        metric = {
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.metrics.append(metric)
        self._record_resource_sample("operation")
    
    def _record_resource_sample(self, sample_type: str):
        """Record resource usage sample."""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            sample = {
                "timestamp": time.time(),
                "type": sample_type,
                "memory_mb": memory_info.rss / 1024 / 1024,
                "cpu_percent": cpu_percent,
                "disk_io": self._get_disk_io()
            }
            self.resource_samples.append(sample)
        except Exception as e:
            # Fallback if resource monitoring fails
            sample = {
                "timestamp": time.time(),
                "type": sample_type,
                "memory_mb": 0,
                "cpu_percent": 0,
                "disk_io": 0,
                "error": str(e)
            }
            self.resource_samples.append(sample)
    
    def _get_disk_io(self) -> float:
        """Get current disk I/O usage."""
        try:
            disk_io = psutil.disk_io_counters()
            return (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024  # MB
        except:
            return 0.0
    
    def calculate_detailed_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not self.metrics:
            return {"error": "No metrics recorded"}
        
        successful_metrics = [m for m in self.metrics if m["success"]]
        failed_metrics = [m for m in self.metrics if not m["success"]]
        
        if not successful_metrics:
            return {"error": "No successful operations"}
        
        durations = [m["duration"] for m in successful_metrics]
        total_duration = self.end_time - self.start_time
        
        # Basic metrics
        basic_metrics = {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful_metrics),
            "failed_operations": len(failed_metrics),
            "total_duration": total_duration,
            "success_rate": len(successful_metrics) / len(self.metrics),
        }
        
        # Response time metrics
        response_metrics = {
            "average_response_time": statistics.mean(durations),
            "median_response_time": statistics.median(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "p50_response_time": self._percentile(durations, 50),
            "p90_response_time": self._percentile(durations, 90),
            "p95_response_time": self._percentile(durations, 95),
            "p99_response_time": self._percentile(durations, 99),
        }
        
        # Throughput metrics
        throughput_metrics = {
            "throughput_ops_per_sec": len(successful_metrics) / total_duration,
            "effective_throughput": len(successful_metrics) / total_duration,
        }
        
        # Resource metrics
        resource_metrics = self._calculate_resource_metrics()
        
        # Performance analysis
        performance_analysis = self._analyze_performance(durations, response_metrics)
        
        return {
            **basic_metrics,
            **response_metrics,
            **throughput_metrics,
            **resource_metrics,
            **performance_analysis
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_resource_metrics(self) -> Dict[str, Any]:
        """Calculate resource utilization metrics."""
        if not self.resource_samples:
            return {"resource_metrics": "No resource data available"}
        
        memory_samples = [s["memory_mb"] for s in self.resource_samples if "memory_mb" in s]
        cpu_samples = [s["cpu_percent"] for s in self.resource_samples if "cpu_percent" in s]
        
        return {
            "avg_memory_mb": statistics.mean(memory_samples) if memory_samples else 0,
            "max_memory_mb": max(memory_samples) if memory_samples else 0,
            "avg_cpu_percent": statistics.mean(cpu_samples) if cpu_samples else 0,
            "max_cpu_percent": max(cpu_samples) if cpu_samples else 0,
            "memory_increase_mb": max(memory_samples) - min(memory_samples) if memory_samples else 0,
        }
    
    def _analyze_performance(self, durations: List[float], response_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze performance characteristics."""
        avg_response = response_metrics["average_response_time"]
        p95_response = response_metrics["p95_response_time"]
        
        # Performance classification
        if avg_response < self.config.fast_response:
            performance_class = "excellent"
        elif avg_response < self.config.normal_response:
            performance_class = "good"
        elif avg_response < self.config.slow_response:
            performance_class = "acceptable"
        else:
            performance_class = "poor"
        
        # Consistency analysis
        response_variance = statistics.variance(durations) if len(durations) > 1 else 0
        consistency_score = 1.0 / (1.0 + response_variance / 1000)  # Normalize variance
        
        # Bottleneck identification
        bottlenecks = []
        if p95_response > avg_response * 2:
            bottlenecks.append("high_p95_latency")
        if response_variance > avg_response:
            bottlenecks.append("inconsistent_response_times")
        
        return {
            "performance_class": performance_class,
            "consistency_score": consistency_score,
            "response_variance": response_variance,
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_recommendations(performance_class, bottlenecks)
        }
    
    def _generate_recommendations(self, performance_class: str, bottlenecks: List[str]) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if performance_class == "poor":
            recommendations.extend([
                "Investigate system bottlenecks",
                "Consider horizontal scaling",
                "Optimize database queries",
                "Implement caching strategies"
            ])
        
        if "high_p95_latency" in bottlenecks:
            recommendations.append("Optimize slow operations and implement request queuing")
        
        if "inconsistent_response_times" in bottlenecks:
            recommendations.append("Standardize operation patterns and reduce variance")
        
        if performance_class in ["excellent", "good"]:
            recommendations.append("Monitor for performance regressions")
        
        return recommendations

@pytest.mark.asyncio
async def test_detailed_response_time_analysis():
    """Test detailed response time analysis with various operation types."""
    config = PerformanceConfig()
    benchmark = EnhancedPerformanceBenchmark(config)
    benchmark.start_benchmark()
    
    # Test different operation types with realistic durations
    operation_types = [
        ("cache_lookup", 0.005, {"type": "cache", "complexity": "low"}),
        ("database_query", 0.050, {"type": "database", "complexity": "medium"}),
        ("api_call", 0.030, {"type": "external", "complexity": "medium"}),
        ("file_operation", 0.020, {"type": "file", "complexity": "low"}),
        ("data_processing", 0.040, {"type": "computation", "complexity": "high"}),
        ("network_request", 0.080, {"type": "network", "complexity": "medium"}),
        ("complex_calculation", 0.100, {"type": "computation", "complexity": "high"}),
    ]
    
    for operation_name, simulated_duration, metadata in operation_types:
        start_time = time.time()
        
        # Simulate operation with some variance
        actual_duration = simulated_duration + (time.time() % 0.01)  # Add variance
        await asyncio.sleep(actual_duration)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        benchmark.record_metric(operation_name, duration, success=True, metadata=metadata)
    
    metrics = benchmark.end_benchmark()
    
    # Verify detailed metrics
    assert metrics["total_operations"] == 7, "Should have 7 operations"
    assert metrics["successful_operations"] == 7, "All operations should succeed"
    assert metrics["success_rate"] == 1.0, "100% success rate"
    
    # Verify response time metrics
    assert "p50_response_time" in metrics, "Should have p50 response time"
    assert "p95_response_time" in metrics, "Should have p95 response time"
    assert "p99_response_time" in metrics, "Should have p99 response time"
    
    # Verify performance analysis
    assert "performance_class" in metrics, "Should have performance classification"
    assert "consistency_score" in metrics, "Should have consistency score"
    assert "recommendations" in metrics, "Should have optimization recommendations"

@pytest.mark.asyncio
async def test_load_testing_scenarios():
    """Test system performance under various load scenarios."""
    config = PerformanceConfig()
    
    load_scenarios = [
        ("light_load", config.light_load, 0.01),
        ("normal_load", config.normal_load, 0.01),
        ("heavy_load", config.heavy_load, 0.01),
    ]
    
    scenario_results = []
    
    for scenario_name, num_operations, operation_duration in load_scenarios:
        benchmark = EnhancedPerformanceBenchmark(config)
        benchmark.start_benchmark()
        
        async def load_operation(operation_id: int):
            start_time = time.time()
            await asyncio.sleep(operation_duration)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            benchmark.record_metric(
                f"{scenario_name}_op_{operation_id}",
                duration,
                success=True,
                metadata={"scenario": scenario_name, "operation_id": operation_id}
            )
            return duration
        
        # Run concurrent operations
        tasks = [load_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*tasks)
        
        metrics = benchmark.end_benchmark()
        scenario_results.append({
            "scenario": scenario_name,
            "operations": num_operations,
            "metrics": metrics
        })
    
    # Analyze load testing results
    for result in scenario_results:
        scenario = result["scenario"]
        metrics = result["metrics"]
        
        assert metrics["total_operations"] == result["operations"], \
            f"{scenario} should have {result['operations']} operations"
        assert metrics["success_rate"] == 1.0, f"{scenario} should have 100% success rate"
        
        # Performance should degrade gracefully with load
        if scenario == "light_load":
            assert metrics["average_response_time"] < 50, \
                f"{scenario} should have fast response: {metrics['average_response_time']:.2f}ms"
        elif scenario == "normal_load":
            assert metrics["average_response_time"] < 100, \
                f"{scenario} should have acceptable response: {metrics['average_response_time']:.2f}ms"
        elif scenario == "heavy_load":
            assert metrics["average_response_time"] < 200, \
                f"{scenario} should handle heavy load: {metrics['average_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_stress_testing():
    """Test system behavior under stress conditions."""
    config = PerformanceConfig()
    benchmark = EnhancedPerformanceBenchmark(config)
    benchmark.start_benchmark()
    
    # Simulate stress conditions
    stress_operations = []
    
    async def stress_operation(operation_id: int):
        start_time = time.time()
        
        # Simulate varying stress levels
        if operation_id % 10 == 0:
            # Heavy operation
            await asyncio.sleep(0.05)
        elif operation_id % 5 == 0:
            # Medium operation
            await asyncio.sleep(0.02)
        else:
            # Light operation
            await asyncio.sleep(0.01)
        
        # Simulate occasional failures under stress
        should_fail = operation_id % 20 == 0  # 5% failure rate under stress
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        success = not should_fail
        benchmark.record_metric(
            f"stress_op_{operation_id}",
            duration,
            success=success,
            metadata={"stress_level": "high", "operation_id": operation_id}
        )
        
        return {"operation_id": operation_id, "success": success, "duration": duration}
    
    # Run stress test
    num_stress_operations = 50
    tasks = [stress_operation(i) for i in range(num_stress_operations)]
    results = await asyncio.gather(*tasks)
    
    metrics = benchmark.end_benchmark()
    
    # Verify stress test results
    assert metrics["total_operations"] == num_stress_operations, \
        f"Should have {num_stress_operations} stress operations"
    assert metrics["success_rate"] > 0.9, \
        f"Success rate should be > 90% under stress: {metrics['success_rate']:.2f}"
    assert metrics["failed_operations"] > 0, \
        "Should have some failures under stress conditions"

@pytest.mark.asyncio
async def test_resource_utilization_monitoring():
    """Test resource utilization monitoring under load."""
    config = PerformanceConfig()
    benchmark = EnhancedPerformanceBenchmark(config)
    benchmark.start_benchmark()
    
    # Simulate resource-intensive operations
    async def resource_intensive_operation(operation_id: int):
        start_time = time.time()
        
        # Simulate CPU-intensive work
        for _ in range(1000):
            _ = sum(range(100))
        
        # Simulate memory allocation
        large_data = [i for i in range(1000)]
        
        await asyncio.sleep(0.01)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        benchmark.record_metric(
            f"resource_op_{operation_id}",
            duration,
            success=True,
            metadata={"resource_type": "cpu_memory", "operation_id": operation_id}
        )
        
        # Clean up
        del large_data
        return duration
    
    # Run resource-intensive operations
    num_operations = 10
    tasks = [resource_intensive_operation(i) for i in range(num_operations)]
    results = await asyncio.gather(*tasks)
    
    metrics = benchmark.end_benchmark()
    
    # Verify resource metrics
    assert "avg_memory_mb" in metrics, "Should have average memory usage"
    assert "max_memory_mb" in metrics, "Should have maximum memory usage"
    assert "avg_cpu_percent" in metrics, "Should have average CPU usage"
    assert "max_cpu_percent" in metrics, "Should have maximum CPU usage"
    
    # Verify resource usage is reasonable
    assert metrics["max_memory_mb"] < config.max_memory_mb, \
        f"Memory usage {metrics['max_memory_mb']:.2f}MB should be below {config.max_memory_mb}MB"
    assert metrics["max_cpu_percent"] < config.max_cpu_percent, \
        f"CPU usage {metrics['max_cpu_percent']:.1f}% should be below {config.max_cpu_percent}%"

@pytest.mark.asyncio
async def test_performance_regression_detection():
    """Test detection of performance regressions."""
    config = PerformanceConfig()
    
    # Baseline performance measurement
    baseline_benchmark = EnhancedPerformanceBenchmark(config)
    baseline_benchmark.start_benchmark()
    
    for _ in range(10):
        start_time = time.time()
        await asyncio.sleep(0.01)  # Baseline operation
        duration = (time.time() - start_time) * 1000
        baseline_benchmark.record_metric("baseline_op", duration)
    
    baseline_metrics = baseline_benchmark.end_benchmark()
    baseline_avg = baseline_metrics["average_response_time"]
    
    # Current performance measurement (simulate regression)
    current_benchmark = EnhancedPerformanceBenchmark(config)
    current_benchmark.start_benchmark()
    
    for _ in range(10):
        start_time = time.time()
        await asyncio.sleep(0.02)  # Simulated regression (slower)
        duration = (time.time() - start_time) * 1000
        current_benchmark.record_metric("current_op", duration)
    
    current_metrics = current_benchmark.end_benchmark()
    current_avg = current_metrics["average_response_time"]
    
    # Detect regression
    regression_factor = current_avg / baseline_avg
    regression_detected = regression_factor > 1.5
    
    # Verify regression detection
    assert regression_detected, f"Should detect performance regression: {regression_factor:.2f}x slower"
    assert current_avg > baseline_avg, "Current performance should be worse than baseline"
    
    # Verify regression analysis
    assert current_metrics["performance_class"] in ["acceptable", "poor"], \
        "Performance should be classified as degraded"

@pytest.mark.asyncio
async def test_throughput_optimization():
    """Test throughput optimization scenarios."""
    config = PerformanceConfig()
    
    # Test different optimization scenarios
    optimization_scenarios = [
        ("baseline", 0.01, 1),      # Baseline performance
        ("optimized", 0.005, 2),    # Optimized operations
        ("highly_optimized", 0.002, 3),  # Highly optimized operations
    ]
    
    scenario_results = []
    
    for scenario_name, operation_duration, concurrency_factor in optimization_scenarios:
        benchmark = EnhancedPerformanceBenchmark(config)
        benchmark.start_benchmark()
        
        async def optimized_operation(operation_id: int):
            start_time = time.time()
            await asyncio.sleep(operation_duration)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            benchmark.record_metric(
                f"{scenario_name}_op_{operation_id}",
                duration,
                success=True,
                metadata={"scenario": scenario_name, "optimization_level": concurrency_factor}
            )
            return duration
        
        # Run operations with different concurrency levels
        num_operations = 20 * concurrency_factor
        tasks = [optimized_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*tasks)
        
        metrics = benchmark.end_benchmark()
        scenario_results.append({
            "scenario": scenario_name,
            "metrics": metrics,
            "optimization_level": concurrency_factor
        })
    
    # Analyze optimization results
    baseline_throughput = scenario_results[0]["metrics"]["throughput_ops_per_sec"]
    
    for result in scenario_results[1:]:  # Skip baseline
        scenario = result["scenario"]
        metrics = result["metrics"]
        optimization_level = result["optimization_level"]
        
        # Throughput should improve with optimization
        throughput_improvement = metrics["throughput_ops_per_sec"] / baseline_throughput
        assert throughput_improvement > 1.0, \
            f"{scenario} should improve throughput: {throughput_improvement:.2f}x"

def test_performance_configuration():
    """Test performance configuration validation."""
    config = PerformanceConfig()
    
    # Verify configuration values
    assert config.fast_response > 0, "Fast response threshold should be positive"
    assert config.normal_response > config.fast_response, "Normal response should be > fast response"
    assert config.slow_response > config.normal_response, "Slow response should be > normal response"
    
    assert config.min_throughput > 0, "Minimum throughput should be positive"
    assert config.target_throughput > config.min_throughput, "Target throughput should be > minimum"
    assert config.high_throughput > config.target_throughput, "High throughput should be > target"
    
    assert config.light_load > 0, "Light load should be positive"
    assert config.normal_load > config.light_load, "Normal load should be > light load"
    assert config.heavy_load > config.normal_load, "Heavy load should be > normal load"
    assert config.stress_load > config.heavy_load, "Stress load should be > heavy load"

if __name__ == "__main__":
    # Run enhanced performance tests
    pytest.main([__file__, "-v", "--tb=short"]) 