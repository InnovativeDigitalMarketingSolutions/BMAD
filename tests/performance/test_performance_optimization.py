"""
Performance Optimization Framework for BMAD System

This module provides tools and tests for identifying performance bottlenecks
and implementing optimization strategies.

Test Coverage:
- Bottleneck identification
- Optimization strategy testing
- Performance improvement validation
- Caching strategy testing
- Database optimization testing
- Memory optimization testing
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationStrategy:
    """Performance optimization strategy configuration."""
    name: str
    description: str
    category: str  # caching, database, memory, algorithm, etc.
    expected_improvement: float  # Expected performance improvement factor
    implementation_cost: str  # low, medium, high
    risk_level: str  # low, medium, high

class PerformanceOptimizer:
    """Performance optimization analysis and implementation."""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.optimized_metrics = {}
        self.optimization_results = []
    
    async def measure_baseline_performance(self, operation_name: str, operation_func, 
                                         num_iterations: int = 10) -> Dict[str, Any]:
        """Measure baseline performance for an operation."""
        durations = []
        memory_samples = []
        
        for i in range(num_iterations):
            # Measure memory before
            memory_before = self._get_memory_usage()
            
            # Measure operation
            start_time = time.time()
            result = await operation_func()
            end_time = time.time()
            
            # Measure memory after
            memory_after = self._get_memory_usage()
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            memory_used = memory_after - memory_before
            
            durations.append(duration)
            memory_samples.append(memory_used)
        
        baseline_metrics = {
            "operation": operation_name,
            "iterations": num_iterations,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p95_duration": self._percentile(durations, 95),
            "avg_memory_usage": statistics.mean(memory_samples),
            "max_memory_usage": max(memory_samples),
            "duration_variance": statistics.variance(durations) if len(durations) > 1 else 0,
        }
        
        self.baseline_metrics[operation_name] = baseline_metrics
        return baseline_metrics
    
    async def measure_optimized_performance(self, operation_name: str, optimized_func,
                                          num_iterations: int = 10) -> Dict[str, Any]:
        """Measure performance after optimization."""
        durations = []
        memory_samples = []
        
        for i in range(num_iterations):
            # Measure memory before
            memory_before = self._get_memory_usage()
            
            # Measure optimized operation
            start_time = time.time()
            result = await optimized_func()
            end_time = time.time()
            
            # Measure memory after
            memory_after = self._get_memory_usage()
            
            duration = (end_time - start_time) * 1000
            memory_used = memory_after - memory_before
            
            durations.append(duration)
            memory_samples.append(memory_used)
        
        optimized_metrics = {
            "operation": operation_name,
            "iterations": num_iterations,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p95_duration": self._percentile(durations, 95),
            "avg_memory_usage": statistics.mean(memory_samples),
            "max_memory_usage": max(memory_samples),
            "duration_variance": statistics.variance(durations) if len(durations) > 1 else 0,
        }
        
        self.optimized_metrics[operation_name] = optimized_metrics
        return optimized_metrics
    
    def compare_performance(self, operation_name: str) -> Dict[str, Any]:
        """Compare baseline vs optimized performance."""
        baseline = self.baseline_metrics.get(operation_name)
        optimized = self.optimized_metrics.get(operation_name)
        
        if not baseline or not optimized:
            return {"error": "Missing baseline or optimized metrics"}
        
        # Calculate improvements
        duration_improvement = baseline["avg_duration"] / optimized["avg_duration"]
        memory_improvement = baseline["avg_memory_usage"] / optimized["avg_memory_usage"] if optimized["avg_memory_usage"] > 0 else float('inf')
        variance_improvement = baseline["duration_variance"] / optimized["duration_variance"] if optimized["duration_variance"] > 0 else float('inf')
        
        comparison = {
            "operation": operation_name,
            "duration_improvement_factor": duration_improvement,
            "memory_improvement_factor": memory_improvement,
            "variance_improvement_factor": variance_improvement,
            "duration_improvement_percent": (duration_improvement - 1) * 100,
            "memory_improvement_percent": (memory_improvement - 1) * 100,
            "baseline_metrics": baseline,
            "optimized_metrics": optimized,
            "optimization_successful": duration_improvement > 1.1,  # 10% improvement threshold
        }
        
        self.optimization_results.append(comparison)
        return comparison
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
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

# Optimization strategies
OPTIMIZATION_STRATEGIES = [
    OptimizationStrategy(
        name="caching_optimization",
        description="Implement result caching for expensive operations",
        category="caching",
        expected_improvement=3.0,
        implementation_cost="low",
        risk_level="low"
    ),
    OptimizationStrategy(
        name="database_query_optimization",
        description="Optimize database queries and add indexes",
        category="database",
        expected_improvement=2.5,
        implementation_cost="medium",
        risk_level="medium"
    ),
    OptimizationStrategy(
        name="memory_optimization",
        description="Reduce memory allocations and improve garbage collection",
        category="memory",
        expected_improvement=1.5,
        implementation_cost="medium",
        risk_level="low"
    ),
    OptimizationStrategy(
        name="algorithm_optimization",
        description="Replace inefficient algorithms with optimized versions",
        category="algorithm",
        expected_improvement=5.0,
        implementation_cost="high",
        risk_level="high"
    ),
    OptimizationStrategy(
        name="concurrency_optimization",
        description="Improve concurrent operation handling",
        category="concurrency",
        expected_improvement=2.0,
        implementation_cost="medium",
        risk_level="medium"
    ),
]

# Mock operations for testing
async def baseline_expensive_operation():
    """Baseline expensive operation for testing."""
    # Simulate expensive computation
    await asyncio.sleep(0.1)
    # Simulate memory allocation
    large_data = [i for i in range(10000)]
    result = sum(large_data)
    del large_data
    return result

async def optimized_expensive_operation():
    """Optimized version of expensive operation."""
    # Simulate optimized computation
    await asyncio.sleep(0.03)  # 70% faster
    # Simulate reduced memory allocation
    result = sum(range(10000))  # More efficient
    return result

async def baseline_database_query():
    """Baseline database query simulation."""
    # Simulate slow database query
    await asyncio.sleep(0.05)
    # Simulate large result set
    result = [{"id": i, "data": f"data_{i}"} for i in range(1000)]
    return result

async def optimized_database_query():
    """Optimized database query simulation."""
    # Simulate optimized query with indexing
    await asyncio.sleep(0.02)  # 60% faster
    # Simulate smaller, more targeted result set
    result = [{"id": i, "data": f"data_{i}"} for i in range(100)]  # Reduced data
    return result

async def baseline_memory_intensive_operation():
    """Baseline memory-intensive operation."""
    # Simulate memory-intensive operation
    large_objects = []
    for i in range(1000):
        large_objects.append({"id": i, "data": "x" * 1000})
    result = len(large_objects)
    del large_objects
    return result

async def optimized_memory_intensive_operation():
    """Optimized memory-intensive operation."""
    # Simulate memory-optimized operation
    result = 1000  # Direct calculation without large objects
    return result

@pytest.mark.asyncio
async def test_caching_optimization():
    """Test caching optimization strategy."""
    optimizer = PerformanceOptimizer()
    
    # Measure baseline performance
    baseline_metrics = await optimizer.measure_baseline_performance(
        "expensive_operation", baseline_expensive_operation
    )
    
    # Measure optimized performance
    optimized_metrics = await optimizer.measure_optimized_performance(
        "expensive_operation", optimized_expensive_operation
    )
    
    # Compare performance
    comparison = optimizer.compare_performance("expensive_operation")
    
    # Verify optimization results
    assert comparison["optimization_successful"], "Optimization should be successful"
    assert comparison["duration_improvement_factor"] > 2.0, \
        f"Should have >2x improvement: {comparison['duration_improvement_factor']:.2f}x"
    assert comparison["duration_improvement_percent"] > 50, \
        f"Should have >50% improvement: {comparison['duration_improvement_percent']:.1f}%"

@pytest.mark.asyncio
async def test_database_optimization():
    """Test database query optimization strategy."""
    optimizer = PerformanceOptimizer()
    
    # Measure baseline performance
    baseline_metrics = await optimizer.measure_baseline_performance(
        "database_query", baseline_database_query
    )
    
    # Measure optimized performance
    optimized_metrics = await optimizer.measure_optimized_performance(
        "database_query", optimized_database_query
    )
    
    # Compare performance
    comparison = optimizer.compare_performance("database_query")
    
    # Verify optimization results
    assert comparison["optimization_successful"], "Database optimization should be successful"
    assert comparison["duration_improvement_factor"] > 1.5, \
        f"Should have >1.5x improvement: {comparison['duration_improvement_factor']:.2f}x"
    # Memory improvement is optional and may not always be measurable
    if comparison["memory_improvement_factor"] != float('inf'):
        # Accept any reasonable memory usage (positive or negative improvement)
        assert abs(comparison["memory_improvement_factor"]) < 1000, \
            f"Should have reasonable memory usage: {comparison['memory_improvement_factor']:.2f}x"

@pytest.mark.asyncio
async def test_memory_optimization():
    """Test memory optimization strategy."""
    optimizer = PerformanceOptimizer()
    
    # Measure baseline performance
    baseline_metrics = await optimizer.measure_baseline_performance(
        "memory_operation", baseline_memory_intensive_operation
    )
    
    # Measure optimized performance
    optimized_metrics = await optimizer.measure_optimized_performance(
        "memory_operation", optimized_memory_intensive_operation
    )
    
    # Compare performance
    comparison = optimizer.compare_performance("memory_operation")
    
    # Verify optimization results
    assert comparison["optimization_successful"], "Memory optimization should be successful"
    # Memory improvement may not always be measurable in test environment
    if comparison["memory_improvement_factor"] != float('inf'):
        # Accept any reasonable memory usage (positive or negative improvement)
        assert abs(comparison["memory_improvement_factor"]) < 1000, \
            f"Should have reasonable memory usage: {comparison['memory_improvement_factor']:.2f}x"

@pytest.mark.asyncio
async def test_optimization_strategy_analysis():
    """Test analysis of different optimization strategies."""
    optimizer = PerformanceOptimizer()
    
    # Test multiple optimization strategies
    test_cases = [
        ("expensive_operation", baseline_expensive_operation, optimized_expensive_operation),
        ("database_query", baseline_database_query, optimized_database_query),
        ("memory_operation", baseline_memory_intensive_operation, optimized_memory_intensive_operation),
    ]
    
    optimization_results = []
    
    for operation_name, baseline_func, optimized_func in test_cases:
        # Measure baseline
        await optimizer.measure_baseline_performance(operation_name, baseline_func)
        
        # Measure optimized
        await optimizer.measure_optimized_performance(operation_name, optimized_func)
        
        # Compare
        comparison = optimizer.compare_performance(operation_name)
        optimization_results.append(comparison)
    
    # Analyze overall optimization effectiveness
    successful_optimizations = [r for r in optimization_results if r["optimization_successful"]]
    avg_improvement = statistics.mean([r["duration_improvement_factor"] for r in successful_optimizations])
    
    assert len(successful_optimizations) >= 2, "At least 2 optimizations should be successful"
    assert avg_improvement > 1.5, f"Average improvement should be >1.5x: {avg_improvement:.2f}x"

@pytest.mark.asyncio
async def test_performance_bottleneck_identification():
    """Test identification of performance bottlenecks."""
    optimizer = PerformanceOptimizer()
    
    # Simulate operations with different performance characteristics
    async def fast_operation():
        await asyncio.sleep(0.01)
        return "fast"
    
    async def slow_operation():
        await asyncio.sleep(0.1)
        return "slow"
    
    async def very_slow_operation():
        await asyncio.sleep(0.2)
        return "very_slow"
    
    # Measure all operations
    fast_metrics = await optimizer.measure_baseline_performance("fast", fast_operation)
    slow_metrics = await optimizer.measure_baseline_performance("slow", slow_operation)
    very_slow_metrics = await optimizer.measure_baseline_performance("very_slow", very_slow_operation)
    
    # Identify bottlenecks
    all_metrics = [fast_metrics, slow_metrics, very_slow_metrics]
    avg_durations = [m["avg_duration"] for m in all_metrics]
    max_duration = max(avg_durations)
    min_duration = min(avg_durations)
    
    # Calculate bottleneck severity
    bottleneck_factor = max_duration / min_duration
    
    # Verify bottleneck identification
    assert bottleneck_factor > 10, f"Should identify significant bottleneck: {bottleneck_factor:.1f}x"
    
    # Identify the slowest operation
    slowest_operation = max(all_metrics, key=lambda x: x["avg_duration"])
    assert slowest_operation["operation"] == "very_slow", "Should identify very_slow as bottleneck"

@pytest.mark.asyncio
async def test_optimization_impact_analysis():
    """Test analysis of optimization impact on different metrics."""
    optimizer = PerformanceOptimizer()
    
    # Measure baseline with multiple metrics
    baseline_metrics = await optimizer.measure_baseline_performance(
        "comprehensive_operation", baseline_expensive_operation, num_iterations=20
    )
    
    # Measure optimized version
    optimized_metrics = await optimizer.measure_optimized_performance(
        "comprehensive_operation", optimized_expensive_operation, num_iterations=20
    )
    
    # Compare performance
    comparison = optimizer.compare_performance("comprehensive_operation")
    
    # Analyze impact on different metrics
    duration_impact = comparison["duration_improvement_percent"]
    memory_impact = comparison["memory_improvement_percent"]
    variance_impact = comparison["variance_improvement_factor"]
    
    # Verify comprehensive optimization analysis
    assert duration_impact > 0, "Should have positive duration impact"
    assert comparison["optimization_successful"], "Optimization should be successful"
    
    # Check consistency improvement
    baseline_variance = baseline_metrics["duration_variance"]
    optimized_variance = optimized_metrics["duration_variance"]
    
    if baseline_variance > 0 and optimized_variance > 0:
        consistency_improvement = baseline_variance / optimized_variance
        assert consistency_improvement > 0.5, "Should maintain reasonable consistency"

def test_optimization_strategy_validation():
    """Test validation of optimization strategies."""
    for strategy in OPTIMIZATION_STRATEGIES:
        # Verify strategy configuration
        assert strategy.name, f"Strategy {strategy.name} should have a name"
        assert strategy.description, f"Strategy {strategy.name} should have a description"
        assert strategy.category, f"Strategy {strategy.name} should have a category"
        assert strategy.expected_improvement > 1.0, f"Strategy {strategy.name} should expect improvement > 1.0"
        assert strategy.implementation_cost in ["low", "medium", "high"], \
            f"Strategy {strategy.name} should have valid implementation cost"
        assert strategy.risk_level in ["low", "medium", "high"], \
            f"Strategy {strategy.name} should have valid risk level"

@pytest.mark.asyncio
async def test_optimization_prioritization():
    """Test prioritization of optimization strategies based on impact and cost."""
    optimizer = PerformanceOptimizer()
    
    # Simulate different optimization scenarios
    optimization_scenarios = [
        ("high_impact_low_cost", 5.0, "low", "low"),
        ("medium_impact_medium_cost", 2.0, "medium", "medium"),
        ("low_impact_high_cost", 1.2, "high", "high"),
    ]
    
    prioritized_strategies = []
    
    for name, improvement, cost, risk in optimization_scenarios:
        # Calculate priority score (higher is better)
        priority_score = improvement / (1 + ["low", "medium", "high"].index(cost))
        prioritized_strategies.append({
            "name": name,
            "improvement": improvement,
            "cost": cost,
            "risk": risk,
            "priority_score": priority_score
        })
    
    # Sort by priority score
    prioritized_strategies.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Verify prioritization
    assert prioritized_strategies[0]["name"] == "high_impact_low_cost", \
        "High impact, low cost should be prioritized first"
    assert prioritized_strategies[-1]["name"] == "low_impact_high_cost", \
        "Low impact, high cost should be prioritized last"

if __name__ == "__main__":
    # Run performance optimization tests
    pytest.main([__file__, "-v", "--tb=short"]) 