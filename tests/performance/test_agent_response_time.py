#!/usr/bin/env python3
"""
Agent Response Time Performance Test
Focused test for measuring agent method response times
"""

import time
import statistics
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent
from bmad.agents.Agent.StrategiePartner.strategiepartner import StrategiePartnerAgent
from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent


class AgentResponseTimeTest:
    """Focused performance test for agent response times."""
    
    def __init__(self):
        self.results = {}
        self.performance_thresholds = {
            "response_time_ms": 2000,  # 2 seconds max
            "error_rate_percent": 5  # 5% max error rate
        }
    
    def test_single_agent_method(self, agent_class, method_name: str, 
                                test_data: Dict[str, Any] = None, iterations: int = 5) -> Dict[str, Any]:
        """Test response time for a single agent method."""
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
                elif method_name == "create_workflow" and test_data:
                    result = agent.create_workflow(**test_data)
                elif method_name == "validate_idea" and test_data:
                    result = agent.validate_idea(**test_data)
                elif method_name == "analyze_code_quality" and test_data:
                    result = agent.analyze_code_quality(**test_data)
                else:
                    raise ValueError(f"Unknown method: {method_name}")
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
                
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
            
            print(f"  ✅ {agent_class.__name__}.{method_name}: {avg_response_time:.2f}ms avg")
            return result
        else:
            print(f"  ❌ {agent_class.__name__}.{method_name}: All iterations failed")
            return None
    
    def _calculate_performance_score(self, avg_response_time_ms: float, error_rate_percent: float) -> str:
        """Calculate performance score based on response time and error rate."""
        if error_rate_percent > self.performance_thresholds["error_rate_percent"]:
            return "FAIL"
        elif avg_response_time_ms > self.performance_thresholds["response_time_ms"]:
            return "SLOW"
        elif avg_response_time_ms < 500:
            return "EXCELLENT"
        elif avg_response_time_ms < 1000:
            return "GOOD"
        else:
            return "ACCEPTABLE"
    
    def run_quick_response_time_test(self) -> Dict[str, Any]:
        """Run quick response time tests for all agents."""
        print("🚀 Starting Agent Response Time Performance Test")
        print("=" * 60)
        
        test_cases = [
            (QualityGuardianAgent, "show_help"),
            (QualityGuardianAgent, "test_resource_completeness"),
            (StrategiePartnerAgent, "show_help"),
            (StrategiePartnerAgent, "collaborate_example"),
            (OrchestratorAgent, "show_help"),
        ]
        
        results = {}
        
        for agent_class, method_name in test_cases:
            result = self.test_single_agent_method(agent_class, method_name)
            if result:
                results[f"{agent_class.__name__}.{method_name}"] = result
        
        # Generate summary
        summary = self._generate_summary(results)
        
        print("\n" + "=" * 60)
        print("📊 RESPONSE TIME PERFORMANCE SUMMARY")
        print("=" * 60)
        
        for key, result in results.items():
            status = "✅" if result["performance_score"] in ["EXCELLENT", "GOOD"] else "⚠️" if result["performance_score"] == "ACCEPTABLE" else "❌"
            print(f"{status} {key}: {result['avg_response_time_ms']}ms ({result['performance_score']})")
        
        print(f"\nOverall Performance: {summary['overall_grade']}")
        print(f"Average Response Time: {summary['avg_response_time']:.2f}ms")
        print(f"Total Tests: {summary['total_tests']}")
        
        return results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        if not results:
            return {"overall_grade": "FAIL", "avg_response_time": 0, "total_tests": 0}
        
        response_times = [r["avg_response_time_ms"] for r in results.values()]
        avg_response_time = statistics.mean(response_times)
        
        # Calculate overall grade
        excellent_count = sum(1 for r in results.values() if r["performance_score"] == "EXCELLENT")
        good_count = sum(1 for r in results.values() if r["performance_score"] == "GOOD")
        acceptable_count = sum(1 for r in results.values() if r["performance_score"] == "ACCEPTABLE")
        fail_count = sum(1 for r in results.values() if r["performance_score"] in ["SLOW", "FAIL"])
        
        total_tests = len(results)
        
        if fail_count > 0:
            overall_grade = "FAIL"
        elif excellent_count >= total_tests * 0.7:
            overall_grade = "EXCELLENT"
        elif (excellent_count + good_count) >= total_tests * 0.8:
            overall_grade = "GOOD"
        else:
            overall_grade = "ACCEPTABLE"
        
        return {
            "overall_grade": overall_grade,
            "avg_response_time": avg_response_time,
            "total_tests": total_tests,
            "excellent_count": excellent_count,
            "good_count": good_count,
            "acceptable_count": acceptable_count,
            "fail_count": fail_count
        }


def main():
    """Run the response time performance test."""
    test_suite = AgentResponseTimeTest()
    results = test_suite.run_quick_response_time_test()
    return results


if __name__ == "__main__":
    main() 