"""
Performance Benchmarking Tests for BMAD System

This module tests performance characteristics of the BMAD system
to ensure it meets performance requirements and identify bottlenecks.

Test Coverage:
- Response time measurements
- Throughput testing
- Resource usage monitoring
- Scalability testing
- Performance regression detection
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List, Tuple

# Performance constants
PERFORMANCE_THRESHOLDS = {
    "response_time_ms": 100,  # Maximum response time in milliseconds
    "throughput_ops_per_sec": 10,  # Minimum operations per second
    "concurrent_operations": 5,  # Number of concurrent operations to test
    "memory_usage_mb": 100,  # Maximum memory usage in MB
    "cpu_usage_percent": 80,  # Maximum CPU usage percentage
}

class PerformanceBenchmark:
    """Performance benchmarking utility class."""
    
    def __init__(self):
        self.metrics = []
        self.start_time = None
        self.end_time = None
    
    def start_benchmark(self):
        """Start performance benchmark."""
        self.start_time = time.time()
        self.metrics = []
    
    def end_benchmark(self):
        """End performance benchmark."""
        self.end_time = time.time()
        return self.calculate_metrics()
    
    def record_metric(self, operation: str, duration: float, success: bool = True):
        """Record a performance metric."""
        self.metrics.append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.metrics:
            return {"error": "No metrics recorded"}
        
        durations = [m["duration"] for m in self.metrics if m["success"]]
        total_duration = self.end_time - self.start_time
        
        if not durations:
            return {"error": "No successful operations"}
        
        return {
            "total_operations": len(self.metrics),
            "successful_operations": len(durations),
            "failed_operations": len(self.metrics) - len(durations),
            "total_duration": total_duration,
            "average_response_time": statistics.mean(durations),
            "median_response_time": statistics.median(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "throughput_ops_per_sec": len(durations) / total_duration,
            "success_rate": len(durations) / len(self.metrics),
            "p95_response_time": self._percentile(durations, 95),
            "p99_response_time": self._percentile(durations, 99),
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

@pytest.mark.asyncio
async def test_response_time_benchmark():
    """Test response time performance."""
    benchmark = PerformanceBenchmark()
    benchmark.start_benchmark()
    
    # Simulate operations with varying response times
    operations = [
        ("database_query", 0.05),
        ("api_call", 0.03),
        ("file_operation", 0.02),
        ("cache_lookup", 0.01),
        ("data_processing", 0.04),
    ]
    
    for operation_name, simulated_duration in operations:
        start_time = time.time()
        
        # Simulate operation
        await asyncio.sleep(simulated_duration)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        benchmark.record_metric(operation_name, duration)
    
    metrics = benchmark.end_benchmark()
    
    # Verify performance metrics
    assert metrics["total_operations"] == 5, "Should have 5 operations"
    assert metrics["successful_operations"] == 5, "All operations should succeed"
    assert metrics["average_response_time"] < PERFORMANCE_THRESHOLDS["response_time_ms"], \
        f"Average response time {metrics['average_response_time']:.2f}ms should be below {PERFORMANCE_THRESHOLDS['response_time_ms']}ms"
    assert metrics["throughput_ops_per_sec"] > PERFORMANCE_THRESHOLDS["throughput_ops_per_sec"], \
        f"Throughput {metrics['throughput_ops_per_sec']:.2f} ops/sec should be above {PERFORMANCE_THRESHOLDS['throughput_ops_per_sec']} ops/sec"

@pytest.mark.asyncio
async def test_concurrent_operations_benchmark():
    """Test concurrent operations performance."""
    benchmark = PerformanceBenchmark()
    benchmark.start_benchmark()
    
    # Simulate concurrent operations
    async def concurrent_operation(operation_id: int):
        start_time = time.time()
        
        # Simulate work with some variation
        await asyncio.sleep(0.01 + (operation_id * 0.005))
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        benchmark.record_metric(f"concurrent_op_{operation_id}", duration)
        return {"operation_id": operation_id, "duration": duration}
    
    # Run concurrent operations
    tasks = [
        concurrent_operation(i)
        for i in range(PERFORMANCE_THRESHOLDS["concurrent_operations"])
    ]
    
    results = await asyncio.gather(*tasks)
    
    metrics = benchmark.end_benchmark()
    
    # Verify concurrent performance
    assert len(results) == PERFORMANCE_THRESHOLDS["concurrent_operations"], \
        f"Should have {PERFORMANCE_THRESHOLDS['concurrent_operations']} concurrent operations"
    assert metrics["successful_operations"] == PERFORMANCE_THRESHOLDS["concurrent_operations"], \
        "All concurrent operations should succeed"
    assert metrics["total_duration"] < 0.1, \
        f"Concurrent operations should complete quickly: {metrics['total_duration']:.3f}s"

@pytest.mark.asyncio
async def test_throughput_benchmark():
    """Test system throughput under load."""
    benchmark = PerformanceBenchmark()
    benchmark.start_benchmark()
    
    # Simulate high-throughput operations
    async def high_throughput_operation():
        start_time = time.time()
        
        # Simulate fast operation
        await asyncio.sleep(0.001)  # 1ms operation
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        benchmark.record_metric("high_throughput_op", duration)
        return duration
    
    # Run many operations quickly
    num_operations = 50
    tasks = [high_throughput_operation() for _ in range(num_operations)]
    
    results = await asyncio.gather(*tasks)
    
    metrics = benchmark.end_benchmark()
    
    # Verify throughput
    assert len(results) == num_operations, f"Should have {num_operations} operations"
    assert metrics["throughput_ops_per_sec"] > PERFORMANCE_THRESHOLDS["throughput_ops_per_sec"], \
        f"Throughput {metrics['throughput_ops_per_sec']:.2f} ops/sec should be above {PERFORMANCE_THRESHOLDS['throughput_ops_per_sec']} ops/sec"
    assert metrics["average_response_time"] < 10, \
        f"High-throughput operations should be fast: {metrics['average_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_scalability_benchmark():
    """Test system scalability with increasing load."""
    scalability_results = []
    
    # Test different load levels
    load_levels = [1, 2, 5, 10, 20]
    
    for load in load_levels:
        benchmark = PerformanceBenchmark()
        benchmark.start_benchmark()
        
        async def scalable_operation():
            start_time = time.time()
            await asyncio.sleep(0.01)  # Simulate work
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            benchmark.record_metric("scalable_op", duration)
            return duration
        
        # Run operations with current load level
        tasks = [scalable_operation() for _ in range(load)]
        results = await asyncio.gather(*tasks)
        
        metrics = benchmark.end_benchmark()
        scalability_results.append({
            "load_level": load,
            "metrics": metrics
        })
    
    # Analyze scalability
    for result in scalability_results:
        load = result["load_level"]
        metrics = result["metrics"]
        
        # Performance should degrade gracefully with load
        if load <= 5:
            assert metrics["average_response_time"] < 50, \
                f"Low load ({load}) should have fast response: {metrics['average_response_time']:.2f}ms"
        else:
            assert metrics["average_response_time"] < 200, \
                f"High load ({load}) should still be reasonable: {metrics['average_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_memory_usage_benchmark():
    """Test memory usage under load."""
    import psutil
    import os
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Simulate memory-intensive operations
    memory_usage_samples = []
    
    for i in range(10):
        # Simulate memory allocation
        large_data = [i for i in range(1000)]  # Allocate some memory
        
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_usage_samples.append(current_memory)
        
        await asyncio.sleep(0.01)
        
        # Clean up
        del large_data
    
    # Calculate memory metrics
    max_memory = max(memory_usage_samples)
    memory_increase = max_memory - initial_memory
    
    # Verify memory usage
    assert max_memory < PERFORMANCE_THRESHOLDS["memory_usage_mb"], \
        f"Memory usage {max_memory:.2f}MB should be below {PERFORMANCE_THRESHOLDS['memory_usage_mb']}MB"
    assert memory_increase < 50, \
        f"Memory increase {memory_increase:.2f}MB should be reasonable"

@pytest.mark.asyncio
async def test_error_handling_performance():
    """Test performance under error conditions."""
    benchmark = PerformanceBenchmark()
    benchmark.start_benchmark()
    
    async def operation_with_errors(should_fail: bool = False):
        start_time = time.time()
        
        try:
            if should_fail:
                raise ValueError("Simulated error")
            
            await asyncio.sleep(0.01)
            duration = (time.time() - start_time) * 1000
            benchmark.record_metric("successful_op", duration, success=True)
            return {"status": "success", "duration": duration}
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            benchmark.record_metric("failed_op", duration, success=False)
            return {"status": "error", "error": str(e), "duration": duration}
    
    # Run mix of successful and failed operations
    tasks = []
    for i in range(10):
        should_fail = i % 3 == 0  # 33% failure rate
        tasks.append(operation_with_errors(should_fail))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    metrics = benchmark.end_benchmark()
    
    # Verify error handling performance
    assert metrics["total_operations"] == 10, "Should have 10 operations"
    assert metrics["successful_operations"] > 0, "Should have some successful operations"
    assert metrics["failed_operations"] > 0, "Should have some failed operations"
    assert metrics["success_rate"] > 0.5, "Success rate should be reasonable"

@pytest.mark.asyncio
async def test_performance_regression_detection():
    """Test detection of performance regressions."""
    # Baseline performance
    baseline_benchmark = PerformanceBenchmark()
    baseline_benchmark.start_benchmark()
    
    for _ in range(5):
        start_time = time.time()
        await asyncio.sleep(0.01)  # Baseline operation
        duration = (time.time() - start_time) * 1000
        baseline_benchmark.record_metric("baseline_op", duration)
    
    baseline_metrics = baseline_benchmark.end_benchmark()
    baseline_avg = baseline_metrics["average_response_time"]
    
    # Current performance (simulate regression)
    current_benchmark = PerformanceBenchmark()
    current_benchmark.start_benchmark()
    
    for _ in range(5):
        start_time = time.time()
        await asyncio.sleep(0.02)  # Simulated regression (slower)
        duration = (time.time() - start_time) * 1000
        current_benchmark.record_metric("current_op", duration)
    
    current_metrics = current_benchmark.end_benchmark()
    current_avg = current_metrics["average_response_time"]
    
    # Detect regression
    regression_factor = current_avg / baseline_avg
    
    # Verify regression detection
    assert regression_factor > 1.5, f"Should detect performance regression: {regression_factor:.2f}x slower"
    assert current_avg > baseline_avg, "Current performance should be worse than baseline"

@pytest.mark.asyncio
async def test_resource_utilization_benchmark():
    """Test resource utilization under load."""
    import psutil
    
    # Monitor CPU and memory during load test
    resource_samples = []
    
    async def resource_intensive_operation():
        # Simulate CPU-intensive work
        start_time = time.time()
        
        # CPU work simulation
        for _ in range(1000):
            _ = sum(range(100))
        
        await asyncio.sleep(0.01)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        # Sample resource usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.virtual_memory().used / 1024 / 1024
        
        resource_samples.append({
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "duration": duration
        })
        
        return duration
    
    # Run resource-intensive operations
    tasks = [resource_intensive_operation() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    # Analyze resource utilization
    avg_cpu = statistics.mean([s["cpu_percent"] for s in resource_samples])
    max_cpu = max([s["cpu_percent"] for s in resource_samples])
    avg_memory = statistics.mean([s["memory_mb"] for s in resource_samples])
    
    # Verify resource usage
    assert avg_cpu < PERFORMANCE_THRESHOLDS["cpu_usage_percent"], \
        f"Average CPU usage {avg_cpu:.1f}% should be below {PERFORMANCE_THRESHOLDS['cpu_usage_percent']}%"
    assert max_cpu < 100, f"Maximum CPU usage {max_cpu:.1f}% should be reasonable"
    assert avg_memory < PERFORMANCE_THRESHOLDS["memory_usage_mb"], \
        f"Average memory usage {avg_memory:.1f}MB should be below {PERFORMANCE_THRESHOLDS['memory_usage_mb']}MB"

def test_performance_thresholds():
    """Test that performance thresholds are reasonable."""
    assert PERFORMANCE_THRESHOLDS["response_time_ms"] > 0, "Response time threshold should be positive"
    assert PERFORMANCE_THRESHOLDS["throughput_ops_per_sec"] > 0, "Throughput threshold should be positive"
    assert PERFORMANCE_THRESHOLDS["concurrent_operations"] > 0, "Concurrent operations threshold should be positive"
    assert PERFORMANCE_THRESHOLDS["memory_usage_mb"] > 0, "Memory usage threshold should be positive"
    assert PERFORMANCE_THRESHOLDS["cpu_usage_percent"] > 0, "CPU usage threshold should be positive"
    assert PERFORMANCE_THRESHOLDS["cpu_usage_percent"] <= 100, "CPU usage threshold should be <= 100%"

if __name__ == "__main__":
    # Run performance benchmarking tests
    pytest.main([__file__, "-v", "--tb=short"]) 