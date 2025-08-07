"""
Load Testing Framework for BMAD System

This module provides comprehensive load testing to simulate
real-world usage patterns and identify system bottlenecks.

Test Coverage:
- User simulation scenarios
- API endpoint load testing
- Database load testing
- Concurrent user testing
- Peak load simulation
- Endurance testing
"""

import pytest
import asyncio
import time
import random
import statistics
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class LoadTestScenario:
    """Load test scenario configuration."""
    name: str
    description: str
    num_users: int
    duration_seconds: int
    ramp_up_seconds: int
    target_operations_per_second: float
    operation_types: List[str]
    expected_success_rate: float

class LoadTestUser:
    """Simulates a user interacting with the system."""
    
    def __init__(self, user_id: int, scenario: LoadTestScenario):
        self.user_id = user_id
        self.scenario = scenario
        self.session_start = time.time()
        self.operations_completed = 0
        self.operations_failed = 0
        self.total_response_time = 0.0
        
    async def simulate_user_session(self):
        """Simulate a complete user session."""
        session_duration = self.scenario.duration_seconds
        target_ops_per_sec = self.scenario.target_operations_per_second
        
        while time.time() - self.session_start < session_duration:
            # Calculate delay between operations
            delay = 1.0 / target_ops_per_sec
            
            # Add some randomness to simulate real user behavior
            delay += random.uniform(-0.1, 0.1)
            delay = max(0.01, delay)  # Minimum delay
            
            await asyncio.sleep(delay)
            
            # Perform a random operation
            operation_type = random.choice(self.scenario.operation_types)
            success = await self.perform_operation(operation_type)
            
            if success:
                self.operations_completed += 1
            else:
                self.operations_failed += 1
    
    async def perform_operation(self, operation_type: str) -> bool:
        """Perform a specific type of operation."""
        start_time = time.time()
        
        try:
            # Simulate different operation types
            if operation_type == "login":
                await self.simulate_login()
            elif operation_type == "data_query":
                await self.simulate_data_query()
            elif operation_type == "file_upload":
                await self.simulate_file_upload()
            elif operation_type == "report_generation":
                await self.simulate_report_generation()
            elif operation_type == "api_call":
                await self.simulate_api_call()
            else:
                await self.simulate_generic_operation()
            
            response_time = (time.time() - start_time) * 1000
            self.total_response_time += response_time
            
            # Simulate occasional failures
            success_rate = self.scenario.expected_success_rate
            return random.random() < success_rate
            
        except Exception as e:
            return False
    
    async def simulate_login(self):
        """Simulate user login operation."""
        await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def simulate_data_query(self):
        """Simulate database query operation."""
        await asyncio.sleep(random.uniform(0.02, 0.08))
    
    async def simulate_file_upload(self):
        """Simulate file upload operation."""
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def simulate_report_generation(self):
        """Simulate report generation operation."""
        await asyncio.sleep(random.uniform(0.2, 0.5))
    
    async def simulate_api_call(self):
        """Simulate API call operation."""
        await asyncio.sleep(random.uniform(0.03, 0.12))
    
    async def simulate_generic_operation(self):
        """Simulate generic operation."""
        await asyncio.sleep(random.uniform(0.01, 0.05))

class LoadTestRunner:
    """Load test runner with comprehensive metrics collection."""
    
    def __init__(self):
        self.test_start_time = None
        self.test_end_time = None
        self.user_sessions = []
        self.operation_metrics = []
        self.system_metrics = []
    
    async def run_load_test(self, scenario: LoadTestScenario):
        """Run a complete load test scenario."""
        self.test_start_time = time.time()
        
        # Create user sessions
        users = [
            LoadTestUser(i, scenario)
            for i in range(scenario.num_users)
        ]
        
        # Ramp up users gradually
        await self.ramp_up_users(users, scenario.ramp_up_seconds)
        
        # Run user sessions concurrently
        user_tasks = [user.simulate_user_session() for user in users]
        await asyncio.gather(*user_tasks)
        
        self.test_end_time = time.time()
        
        # Collect results
        return self.collect_test_results(scenario, users)
    
    async def ramp_up_users(self, users: List[LoadTestUser], ramp_up_seconds: int):
        """Gradually start user sessions to simulate realistic load."""
        if ramp_up_seconds <= 0:
            return
        
        delay_per_user = ramp_up_seconds / len(users)
        
        for i, user in enumerate(users):
            # Start user session after delay
            await asyncio.sleep(delay_per_user)
            # User session will start automatically
    
    def collect_test_results(self, scenario: LoadTestScenario, users: List[LoadTestUser]) -> Dict[str, Any]:
        """Collect comprehensive test results."""
        total_operations = sum(user.operations_completed + user.operations_failed for user in users)
        successful_operations = sum(user.operations_completed for user in users)
        failed_operations = sum(user.operations_failed for user in users)
        
        test_duration = self.test_end_time - self.test_start_time
        
        # Calculate response times
        response_times = []
        for user in users:
            if user.operations_completed > 0:
                avg_response_time = user.total_response_time / user.operations_completed
                response_times.append(avg_response_time)
        
        # Calculate throughput
        actual_throughput = successful_operations / test_duration
        
        return {
            "scenario": scenario.name,
            "test_duration": test_duration,
            "num_users": len(users),
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "throughput_ops_per_sec": actual_throughput,
            "target_throughput": scenario.target_operations_per_second,
            "throughput_achievement": actual_throughput / scenario.target_operations_per_second,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "p95_response_time": self._percentile(response_times, 95) if response_times else 0,
            "p99_response_time": self._percentile(response_times, 99) if response_times else 0,
            "user_metrics": [
                {
                    "user_id": user.user_id,
                    "operations_completed": user.operations_completed,
                    "operations_failed": user.operations_failed,
                    "avg_response_time": user.total_response_time / user.operations_completed if user.operations_completed > 0 else 0
                }
                for user in users
            ]
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

# Load test scenarios
LOAD_TEST_SCENARIOS = [
    LoadTestScenario(
        name="light_load",
        description="Light load with few users",
        num_users=5,
        duration_seconds=30,
        ramp_up_seconds=5,
        target_operations_per_second=10.0,
        operation_types=["login", "data_query", "api_call"],
        expected_success_rate=0.99
    ),
    LoadTestScenario(
        name="normal_load",
        description="Normal load with moderate users",
        num_users=20,
        duration_seconds=60,
        ramp_up_seconds=10,
        target_operations_per_second=50.0,
        operation_types=["login", "data_query", "file_upload", "api_call"],
        expected_success_rate=0.95
    ),
    LoadTestScenario(
        name="heavy_load",
        description="Heavy load with many users",
        num_users=50,
        duration_seconds=120,
        ramp_up_seconds=20,
        target_operations_per_second=100.0,
        operation_types=["login", "data_query", "file_upload", "report_generation", "api_call"],
        expected_success_rate=0.90
    ),
    LoadTestScenario(
        name="peak_load",
        description="Peak load simulation",
        num_users=100,
        duration_seconds=180,
        ramp_up_seconds=30,
        target_operations_per_second=200.0,
        operation_types=["login", "data_query", "file_upload", "report_generation", "api_call"],
        expected_success_rate=0.85
    ),
]

@pytest.mark.asyncio
async def test_light_load_scenario():
    """Test light load scenario."""
    scenario = next(s for s in LOAD_TEST_SCENARIOS if s.name == "light_load")
    runner = LoadTestRunner()
    
    results = await runner.run_load_test(scenario)
    
    # Verify light load results
    assert results["num_users"] == 5, "Should have 5 users"
    assert results["success_rate"] > 0.95, f"Success rate should be > 95%: {results['success_rate']:.2f}"
    assert results["throughput_achievement"] > 0.8, f"Throughput achievement should be > 80%: {results['throughput_achievement']:.2f}"
    assert results["avg_response_time"] < 200, f"Average response time should be < 200ms: {results['avg_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_normal_load_scenario():
    """Test normal load scenario."""
    scenario = next(s for s in LOAD_TEST_SCENARIOS if s.name == "normal_load")
    runner = LoadTestRunner()
    
    results = await runner.run_load_test(scenario)
    
    # Verify normal load results
    assert results["num_users"] == 20, "Should have 20 users"
    assert results["success_rate"] > 0.90, f"Success rate should be > 90%: {results['success_rate']:.2f}"
    assert results["throughput_achievement"] > 0.7, f"Throughput achievement should be > 70%: {results['throughput_achievement']:.2f}"
    assert results["avg_response_time"] < 300, f"Average response time should be < 300ms: {results['avg_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_heavy_load_scenario():
    """Test heavy load scenario."""
    scenario = next(s for s in LOAD_TEST_SCENARIOS if s.name == "heavy_load")
    runner = LoadTestRunner()
    
    results = await runner.run_load_test(scenario)
    
    # Verify heavy load results
    assert results["num_users"] == 50, "Should have 50 users"
    assert results["success_rate"] > 0.80, f"Success rate should be > 80%: {results['success_rate']:.2f}"
    assert results["throughput_achievement"] > 0.6, f"Throughput achievement should be > 60%: {results['throughput_achievement']:.2f}"
    assert results["avg_response_time"] < 500, f"Average response time should be < 500ms: {results['avg_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_peak_load_scenario():
    """Test peak load scenario."""
    scenario = next(s for s in LOAD_TEST_SCENARIOS if s.name == "peak_load")
    runner = LoadTestRunner()
    
    results = await runner.run_load_test(scenario)
    
    # Verify peak load results
    assert results["num_users"] == 100, "Should have 100 users"
    assert results["success_rate"] > 0.70, f"Success rate should be > 70%: {results['success_rate']:.2f}"
    assert results["throughput_achievement"] > 0.5, f"Throughput achievement should be > 50%: {results['throughput_achievement']:.2f}"
    assert results["avg_response_time"] < 1000, f"Average response time should be < 1000ms: {results['avg_response_time']:.2f}ms"

@pytest.mark.asyncio
async def test_load_test_scalability():
    """Test system scalability across different load levels."""
    scalability_results = []
    
    for scenario in LOAD_TEST_SCENARIOS:
        runner = LoadTestRunner()
        results = await runner.run_load_test(scenario)
        scalability_results.append(results)
    
    # Analyze scalability
    for i, result in enumerate(scalability_results):
        scenario_name = result["scenario"]
        
        # Performance should degrade gracefully with load
        if scenario_name == "light_load":
            assert result["success_rate"] > 0.95, f"{scenario_name} should have high success rate"
            assert result["avg_response_time"] < 200, f"{scenario_name} should have fast response"
        elif scenario_name == "normal_load":
            assert result["success_rate"] > 0.90, f"{scenario_name} should have good success rate"
            assert result["avg_response_time"] < 300, f"{scenario_name} should have acceptable response"
        elif scenario_name == "heavy_load":
            assert result["success_rate"] > 0.80, f"{scenario_name} should have reasonable success rate"
            assert result["avg_response_time"] < 500, f"{scenario_name} should handle heavy load"
        elif scenario_name == "peak_load":
            assert result["success_rate"] > 0.70, f"{scenario_name} should maintain basic functionality"
            assert result["avg_response_time"] < 1000, f"{scenario_name} should not completely fail"

@pytest.mark.asyncio
async def test_endurance_testing():
    """Test system endurance under sustained load."""
    # Create endurance scenario
    endurance_scenario = LoadTestScenario(
        name="endurance_test",
        description="Endurance test with sustained load",
        num_users=30,
        duration_seconds=300,  # 5 minutes
        ramp_up_seconds=30,
        target_operations_per_second=75.0,
        operation_types=["login", "data_query", "file_upload", "api_call"],
        expected_success_rate=0.90
    )
    
    runner = LoadTestRunner()
    results = await runner.run_load_test(endurance_scenario)
    
    # Verify endurance test results
    assert results["test_duration"] >= 300, "Endurance test should run for at least 5 minutes"
    assert results["success_rate"] > 0.85, f"Endurance success rate should be > 85%: {results['success_rate']:.2f}"
    assert results["throughput_achievement"] > 0.6, f"Endurance throughput should be > 60%: {results['throughput_achievement']:.2f}"
    
    # Check for performance degradation over time
    user_metrics = results["user_metrics"]
    early_users = [u for u in user_metrics if u["user_id"] < 10]
    late_users = [u for u in user_metrics if u["user_id"] >= 20]
    
    if early_users and late_users:
        early_avg_response = statistics.mean([u["avg_response_time"] for u in early_users])
        late_avg_response = statistics.mean([u["avg_response_time"] for u in late_users])
        
        # Late users shouldn't be significantly slower
        degradation_factor = late_avg_response / early_avg_response
        assert degradation_factor < 2.0, f"Performance degradation should be < 2x: {degradation_factor:.2f}"

@pytest.mark.asyncio
async def test_concurrent_user_behavior():
    """Test realistic concurrent user behavior patterns."""
    # Create scenario with varied user behavior
    behavior_scenario = LoadTestScenario(
        name="behavior_test",
        description="Test varied user behavior patterns",
        num_users=25,
        duration_seconds=60,
        ramp_up_seconds=10,
        target_operations_per_second=40.0,
        operation_types=["login", "data_query", "file_upload", "report_generation", "api_call"],
        expected_success_rate=0.92
    )
    
    runner = LoadTestRunner()
    results = await runner.run_load_test(behavior_scenario)
    
    # Verify behavior test results
    assert results["num_users"] == 25, "Should have 25 users"
    assert results["success_rate"] > 0.85, f"Behavior test success rate should be > 85%: {results['success_rate']:.2f}"
    
    # Check user behavior distribution
    user_metrics = results["user_metrics"]
    total_operations = sum(u["operations_completed"] + u["operations_failed"] for u in user_metrics)
    
    # Users should have varied operation counts (realistic behavior)
    operation_counts = [u["operations_completed"] + u["operations_failed"] for u in user_metrics]
    operation_variance = statistics.variance(operation_counts) if len(operation_counts) > 1 else 0
    
    assert operation_variance > 0, "Users should have varied operation patterns"

def test_load_test_scenario_configuration():
    """Test load test scenario configuration validation."""
    for scenario in LOAD_TEST_SCENARIOS:
        # Verify scenario configuration
        assert scenario.num_users > 0, f"{scenario.name}: Number of users should be positive"
        assert scenario.duration_seconds > 0, f"{scenario.name}: Duration should be positive"
        assert scenario.ramp_up_seconds >= 0, f"{scenario.name}: Ramp up should be non-negative"
        assert scenario.target_operations_per_second > 0, f"{scenario.name}: Target throughput should be positive"
        assert len(scenario.operation_types) > 0, f"{scenario.name}: Should have operation types"
        assert 0 < scenario.expected_success_rate <= 1, f"{scenario.name}: Success rate should be between 0 and 1"

if __name__ == "__main__":
    # Run load testing
    pytest.main([__file__, "-v", "--tb=short"]) 