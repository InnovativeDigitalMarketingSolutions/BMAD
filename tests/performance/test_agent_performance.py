#!/usr/bin/env python3
"""
Performance Testing Framework for BMAD Agents
Tests response times, throughput, and resource utilization
"""

import time
import statistics
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent
from bmad.agents.Agent.StrategiePartner.strategiepartner import StrategiePartnerAgent
from bmad.agents.Agent.WorkflowAutomator.workflowautomator import WorkflowAutomatorAgent
from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent


class PerformanceTestSuite:
    """Comprehensive performance testing suite for BMAD agents."""
    
    def __init__(self):
        self.results = {}
        self.performance_thresholds = {
            "response_time_ms": 2000,  # 2 seconds max
            "throughput_ops_per_sec": 10,  # 10 operations per second
            "memory_usage_mb": 512,  # 512MB max
            "cpu_usage_percent": 80,  # 80% max
            "error_rate_percent": 5  # 5% max error rate
        }
    
    def test_agent_response_time(self, agent_class, method_name: str, 
                                test_data: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """Test agent response time for a specific method."""
        print(f"🧪 Testing {agent_class.__name__}.{method_name} response time...")
        
        response_times = []
        errors = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                # Create agent instance
                agent = agent_class()
                
                # Call the method
                if method_name == "show_help":
                    result = agent.show_help()
                elif method_name == "test_resource_completeness":
                    result = agent.test_resource_completeness()
                elif method_name == "collaborate_example":
                    result = agent.collaborate_example()
                elif method_name == "create_workflow":
                    result = agent.create_workflow(**test_data)
                elif method_name == "validate_idea":
                    result = agent.validate_idea(**test_data)
                elif method_name == "analyze_code_quality":
                    result = agent.analyze_code_quality(**test_data)
                else:
                    raise ValueError(f"Unknown method: {method_name}")
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
                
                if i % 5 == 0:
                    print(f"  Iteration {i+1}: {response_time_ms:.2f}ms")
                    
            except Exception as e:
                errors += 1
                print(f"  Error in iteration {i+1}: {e}")
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            std_deviation = statistics.stdev(response_times) if len(response_times) > 1 else 0
            error_rate = (errors / iterations) * 100
            
            result = {
                "agent": agent_class.__name__,
                "method": method_name,
                "iterations": iterations,
                "avg_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "std_deviation_ms": round(std_deviation, 2),
                "error_rate_percent": round(error_rate, 2),
                "throughput_ops_per_sec": round(1000 / avg_response_time, 2),
                "performance_score": self._calculate_performance_score(avg_response_time, error_rate)
            }
            
            print(f"✅ {agent_class.__name__}.{method_name}: {avg_response_time:.2f}ms avg, {error_rate:.1f}% errors")
            return result
        else:
            print(f"❌ {agent_class.__name__}.{method_name}: All iterations failed")
            return {
                "agent": agent_class.__name__,
                "method": method_name,
                "error": "All iterations failed"
            }
    
    def test_concurrent_load(self, agent_class, method_name: str, 
                           test_data: Dict[str, Any], concurrent_users: int = 10, 
                           requests_per_user: int = 5) -> Dict[str, Any]:
        """Test agent performance under concurrent load."""
        print(f"🧪 Testing {agent_class.__name__}.{method_name} under {concurrent_users} concurrent users...")
        
        def single_user_test():
            response_times = []
            errors = 0
            
            for _ in range(requests_per_user):
                try:
                    start_time = time.time()
                    agent = agent_class()
                    
                    if method_name == "show_help":
                        result = agent.show_help()
                    elif method_name == "test_resource_completeness":
                        result = agent.test_resource_completeness()
                    elif method_name == "collaborate_example":
                        result = agent.collaborate_example()
                    elif method_name == "create_workflow":
                        result = agent.create_workflow(**test_data)
                    elif method_name == "validate_idea":
                        result = agent.validate_idea(**test_data)
                    elif method_name == "analyze_code_quality":
                        result = agent.analyze_code_quality(**test_data)
                    
                    end_time = time.time()
                    response_times.append((end_time - start_time) * 1000)
                    
                except Exception as e:
                    errors += 1
            
            return response_times, errors
        
        # Run concurrent tests
        all_response_times = []
        total_errors = 0
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(single_user_test) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                response_times, errors = future.result()
                all_response_times.extend(response_times)
                total_errors += errors
        
        end_time = time.time()
        total_time = end_time - start_time
        total_requests = concurrent_users * requests_per_user
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            throughput = total_requests / total_time
            error_rate = (total_errors / total_requests) * 100
            
            result = {
                "agent": agent_class.__name__,
                "method": method_name,
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests,
                "total_time_seconds": round(total_time, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "throughput_ops_per_sec": round(throughput, 2),
                "error_rate_percent": round(error_rate, 2),
                "performance_score": self._calculate_performance_score(avg_response_time, error_rate)
            }
            
            print(f"✅ {agent_class.__name__}.{method_name}: {throughput:.2f} ops/sec, {error_rate:.1f}% errors")
            return result
        else:
            print(f"❌ {agent_class.__name__}.{method_name}: All concurrent requests failed")
            return {
                "agent": agent_class.__name__,
                "method": method_name,
                "error": "All concurrent requests failed"
            }
    
    def test_memory_usage(self, agent_class, method_name: str, 
                         test_data: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """Test agent memory usage."""
        print(f"🧪 Testing {agent_class.__name__}.{method_name} memory usage...")
        
        try:
            import psutil
            import gc
            
            memory_usage = []
            
            for i in range(iterations):
                # Force garbage collection
                gc.collect()
                
                # Get initial memory
                process = psutil.Process()
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                # Create agent and call method
                agent = agent_class()
                
                if method_name == "show_help":
                    result = agent.show_help()
                elif method_name == "test_resource_completeness":
                    result = agent.test_resource_completeness()
                elif method_name == "collaborate_example":
                    result = agent.collaborate_example()
                elif method_name == "create_workflow":
                    result = agent.create_workflow(**test_data)
                elif method_name == "validate_idea":
                    result = agent.validate_idea(**test_data)
                elif method_name == "analyze_code_quality":
                    result = agent.analyze_code_quality(**test_data)
                
                # Get final memory
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = final_memory - initial_memory
                memory_usage.append(memory_delta)
                
                if i % 5 == 0:
                    print(f"  Iteration {i+1}: {memory_delta:.2f}MB")
                
                # Clean up
                del agent
                gc.collect()
            
            avg_memory_usage = statistics.mean(memory_usage)
            max_memory_usage = max(memory_usage)
            
            result = {
                "agent": agent_class.__name__,
                "method": method_name,
                "avg_memory_usage_mb": round(avg_memory_usage, 2),
                "max_memory_usage_mb": round(max_memory_usage, 2),
                "memory_efficiency": "good" if avg_memory_usage < 50 else "needs_optimization"
            }
            
            print(f"✅ {agent_class.__name__}.{method_name}: {avg_memory_usage:.2f}MB avg memory usage")
            return result
            
        except ImportError:
            print("⚠️  psutil not available, skipping memory usage test")
            return {
                "agent": agent_class.__name__,
                "method": method_name,
                "error": "psutil not available"
            }
    
    def _calculate_performance_score(self, avg_response_time_ms: float, error_rate_percent: float) -> str:
        """Calculate performance score based on response time and error rate."""
        if error_rate_percent > self.performance_thresholds["error_rate_percent"]:
            return "poor"
        elif avg_response_time_ms > self.performance_thresholds["response_time_ms"]:
            return "needs_optimization"
        elif avg_response_time_ms > self.performance_thresholds["response_time_ms"] * 0.5:
            return "good"
        else:
            return "excellent"
    
    def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive performance tests for all agents."""
        print("🚀 Starting Comprehensive Performance Test Suite...\n")
        
        test_configs = [
            # QualityGuardian tests
            (QualityGuardianAgent, "show_help", {}),
            (QualityGuardianAgent, "test_resource_completeness", {}),
            (QualityGuardianAgent, "collaborate_example", {}),
            (QualityGuardianAgent, "analyze_code_quality", {"path": "./tests"}),
            
            # StrategiePartner tests
            (StrategiePartnerAgent, "show_help", {}),
            (StrategiePartnerAgent, "test_resource_completeness", {}),
            (StrategiePartnerAgent, "collaborate_example", {}),
            (StrategiePartnerAgent, "validate_idea", {"idea_description": "Test idea for performance testing"}),
            
            # WorkflowAutomator tests
            (WorkflowAutomatorAgent, "show_help", {}),
            (WorkflowAutomatorAgent, "test_resource_completeness", {}),
            (WorkflowAutomatorAgent, "collaborate_example", {}),
            (WorkflowAutomatorAgent, "create_workflow", {
                "name": "Performance Test Workflow",
                "description": "Test workflow for performance testing",
                "agents": ["ProductOwner"],
                "commands": ["create-story"],
                "priority": "normal"
            }),
            
            # Orchestrator tests
            (OrchestratorAgent, "show_help", {}),
            (OrchestratorAgent, "test_resource_completeness", {}),
            (OrchestratorAgent, "collaborate_example", {})
        ]
        
        results = {
            "response_time_tests": [],
            "concurrent_load_tests": [],
            "memory_usage_tests": [],
            "summary": {}
        }
        
        # Run response time tests
        print("📊 Response Time Tests:")
        print("=" * 50)
        for agent_class, method_name, test_data in test_configs:
            result = self.test_agent_response_time(agent_class, method_name, test_data)
            results["response_time_tests"].append(result)
        
        # Run concurrent load tests (for key methods)
        print("\n📊 Concurrent Load Tests:")
        print("=" * 50)
        key_methods = [
            (QualityGuardianAgent, "analyze_code_quality", {"path": "./tests"}),
            (StrategiePartnerAgent, "validate_idea", {"idea_description": "Test idea"}),
            (WorkflowAutomatorAgent, "create_workflow", {
                "name": "Test Workflow",
                "description": "Test workflow",
                "agents": ["ProductOwner"],
                "commands": ["create-story"],
                "priority": "normal"
            })
        ]
        
        for agent_class, method_name, test_data in key_methods:
            result = self.test_concurrent_load(agent_class, method_name, test_data)
            results["concurrent_load_tests"].append(result)
        
        # Run memory usage tests
        print("\n📊 Memory Usage Tests:")
        print("=" * 50)
        for agent_class, method_name, test_data in test_configs[:5]:  # Test first 5 methods
            result = self.test_memory_usage(agent_class, method_name, test_data)
            results["memory_usage_tests"].append(result)
        
        # Generate summary
        results["summary"] = self._generate_performance_summary(results)
        
        return results
    
    def _generate_performance_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary and recommendations."""
        response_times = [r.get("avg_response_time_ms", 0) for r in results["response_time_tests"] if "avg_response_time_ms" in r]
        error_rates = [r.get("error_rate_percent", 0) for r in results["response_time_tests"] if "error_rate_percent" in r]
        throughputs = [r.get("throughput_ops_per_sec", 0) for r in results["concurrent_load_tests"] if "throughput_ops_per_sec" in r]
        
        summary = {
            "total_tests": len(results["response_time_tests"]),
            "avg_response_time_ms": round(statistics.mean(response_times), 2) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "avg_error_rate_percent": round(statistics.mean(error_rates), 2) if error_rates else 0,
            "avg_throughput_ops_per_sec": round(statistics.mean(throughputs), 2) if throughputs else 0,
            "performance_grade": self._calculate_overall_grade(response_times, error_rates),
            "recommendations": self._generate_recommendations(results)
        }
        
        return summary
    
    def _calculate_overall_grade(self, response_times: List[float], error_rates: List[float]) -> str:
        """Calculate overall performance grade."""
        if not response_times:
            return "incomplete"
        
        avg_response_time = statistics.mean(response_times)
        avg_error_rate = statistics.mean(error_rates) if error_rates else 0
        
        if avg_error_rate > 5 or avg_response_time > 2000:
            return "D"
        elif avg_response_time > 1000:
            return "C"
        elif avg_response_time > 500:
            return "B"
        else:
            return "A"
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Analyze response times
        slow_methods = [r for r in results["response_time_tests"] 
                       if r.get("avg_response_time_ms", 0) > 1000]
        if slow_methods:
            recommendations.append(f"Optimize {len(slow_methods)} slow methods (>1s response time)")
        
        # Analyze error rates
        high_error_methods = [r for r in results["response_time_tests"] 
                             if r.get("error_rate_percent", 0) > 5]
        if high_error_methods:
            recommendations.append(f"Fix {len(high_error_methods)} methods with high error rates (>5%)")
        
        # Analyze throughput
        low_throughput_methods = [r for r in results["concurrent_load_tests"] 
                                 if r.get("throughput_ops_per_sec", 0) < 5]
        if low_throughput_methods:
            recommendations.append(f"Improve throughput for {len(low_throughput_methods)} methods (<5 ops/sec)")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable limits")
        
        return recommendations


def main():
    """Run performance test suite."""
    test_suite = PerformanceTestSuite()
    results = test_suite.run_comprehensive_performance_test()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    summary = results["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Average Response Time: {summary['avg_response_time_ms']}ms")
    print(f"Maximum Response Time: {summary['max_response_time_ms']}ms")
    print(f"Average Error Rate: {summary['avg_error_rate_percent']}%")
    print(f"Average Throughput: {summary['avg_throughput_ops_per_sec']} ops/sec")
    print(f"Performance Grade: {summary['performance_grade']}")
    
    print("\n📋 Recommendations:")
    for rec in summary["recommendations"]:
        print(f"  • {rec}")
    
    # Save results
    import json
    with open("performance_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: performance_test_results.json")
    
    # Return exit code based on performance grade
    if summary["performance_grade"] in ["A", "B"]:
        print("✅ Performance tests PASSED")
        return 0
    else:
        print("❌ Performance tests FAILED - optimization needed")
        return 1


if __name__ == "__main__":
    exit(main()) 