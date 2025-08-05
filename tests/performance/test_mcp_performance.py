#!/usr/bin/env python3
"""
MCP Performance Test
Focused test for measuring MCP operations performance
"""

import time
import statistics
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.core.mcp.tool_registry import MCPToolRegistry
from bmad.core.mcp.mcp_client import MCPClient
from bmad.core.mcp.dependency_manager import DependencyManager


class MCPPerformanceTest:
    """Focused performance test for MCP operations."""
    
    def __init__(self):
        self.results = {}
        self.performance_thresholds = {
            "tool_registration_ms": 50,  # 50ms max for tool registration
            "client_operation_ms": 100,  # 100ms max for client operations
            "dependency_check_ms": 30,  # 30ms max for dependency checks
            "error_rate_percent": 5  # 5% max error rate
        }
    
    def test_tool_registry_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Test MCP tool registry performance."""
        print("🧪 Testing MCP Tool Registry Performance...")
        
        try:
            registry = MCPToolRegistry()
            
            # Test tool registration performance
            register_times = []
            for i in range(iterations):
                tool_name = f"test_tool_{i}"
                tool_config = {
                    "name": tool_name,
                    "description": f"Test tool {i}",
                    "parameters": {"param1": "string"},
                    "handler": lambda x: x
                }
                
                start_time = time.time()
                registry.register_tool(tool_name, tool_config)
                end_time = time.time()
                
                register_time_ms = (end_time - start_time) * 1000
                register_times.append(register_time_ms)
            
            # Test tool lookup performance
            lookup_times = []
            for i in range(iterations):
                tool_name = f"test_tool_{i}"
                
                start_time = time.time()
                tool = registry.get_tool(tool_name)
                end_time = time.time()
                
                lookup_time_ms = (end_time - start_time) * 1000
                lookup_times.append(lookup_time_ms)
            
            # Test tool listing performance
            list_times = []
            for i in range(iterations):
                start_time = time.time()
                tools = registry.list_tools()
                end_time = time.time()
                
                list_time_ms = (end_time - start_time) * 1000
                list_times.append(list_time_ms)
            
            # Calculate statistics
            avg_register_time = statistics.mean(register_times)
            avg_lookup_time = statistics.mean(lookup_times)
            avg_list_time = statistics.mean(list_times)
            
            result = {
                "test_type": "tool_registry",
                "iterations": iterations,
                "avg_register_time_ms": round(avg_register_time, 2),
                "avg_lookup_time_ms": round(avg_lookup_time, 2),
                "avg_list_time_ms": round(avg_list_time, 2),
                "register_performance": self._evaluate_performance(avg_register_time, "tool_registration"),
                "lookup_performance": self._evaluate_performance(avg_lookup_time, "tool_registration"),
                "list_performance": self._evaluate_performance(avg_list_time, "tool_registration")
            }
            
            print(f"  ✅ Tool Registration: {avg_register_time:.2f}ms avg")
            print(f"  ✅ Tool Lookup: {avg_lookup_time:.2f}ms avg")
            print(f"  ✅ Tool Listing: {avg_list_time:.2f}ms avg")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Tool Registry Test Failed: {e}")
            return None
    
    def test_mcp_client_performance(self, iterations: int = 5) -> Dict[str, Any]:
        """Test MCP client performance."""
        print("🧪 Testing MCP Client Performance...")
        
        try:
            client = MCPClient()
            
            # Test client initialization performance
            init_times = []
            for i in range(iterations):
                start_time = time.time()
                client.initialize()
                end_time = time.time()
                
                init_time_ms = (end_time - start_time) * 1000
                init_times.append(init_time_ms)
            
            # Test client connection performance
            connect_times = []
            for i in range(iterations):
                start_time = time.time()
                client.connect()
                end_time = time.time()
                
                connect_time_ms = (end_time - start_time) * 1000
                connect_times.append(connect_time_ms)
            
            # Calculate statistics
            avg_init_time = statistics.mean(init_times)
            avg_connect_time = statistics.mean(connect_times)
            
            result = {
                "test_type": "mcp_client",
                "iterations": iterations,
                "avg_init_time_ms": round(avg_init_time, 2),
                "avg_connect_time_ms": round(avg_connect_time, 2),
                "init_performance": self._evaluate_performance(avg_init_time, "client_operation"),
                "connect_performance": self._evaluate_performance(avg_connect_time, "client_operation")
            }
            
            print(f"  ✅ Client Initialization: {avg_init_time:.2f}ms avg")
            print(f"  ✅ Client Connection: {avg_connect_time:.2f}ms avg")
            
            return result
            
        except Exception as e:
            print(f"  ❌ MCP Client Test Failed: {e}")
            return None
    
    def test_dependency_manager_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Test dependency manager performance."""
        print("🧪 Testing Dependency Manager Performance...")
        
        try:
            manager = DependencyManager()
            
            # Test dependency check performance
            check_times = []
            for i in range(iterations):
                dependency_name = f"test_dependency_{i}"
                
                start_time = time.time()
                is_available = manager.check_dependency(dependency_name)
                end_time = time.time()
                
                check_time_ms = (end_time - start_time) * 1000
                check_times.append(check_time_ms)
            
            # Test dependency registration performance
            register_times = []
            for i in range(iterations):
                dependency_name = f"test_dependency_{i}"
                dependency_config = {
                    "name": dependency_name,
                    "version": "1.0.0",
                    "required": True
                }
                
                start_time = time.time()
                manager.register_dependency(dependency_name, dependency_config)
                end_time = time.time()
                
                register_time_ms = (end_time - start_time) * 1000
                register_times.append(register_time_ms)
            
            # Calculate statistics
            avg_check_time = statistics.mean(check_times)
            avg_register_time = statistics.mean(register_times)
            
            result = {
                "test_type": "dependency_manager",
                "iterations": iterations,
                "avg_check_time_ms": round(avg_check_time, 2),
                "avg_register_time_ms": round(avg_register_time, 2),
                "check_performance": self._evaluate_performance(avg_check_time, "dependency_check"),
                "register_performance": self._evaluate_performance(avg_register_time, "dependency_check")
            }
            
            print(f"  ✅ Dependency Check: {avg_check_time:.2f}ms avg")
            print(f"  ✅ Dependency Registration: {avg_register_time:.2f}ms avg")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Dependency Manager Test Failed: {e}")
            return None
    
    def _evaluate_performance(self, avg_time_ms: float, operation_type: str) -> str:
        """Evaluate performance based on operation type."""
        if operation_type == "tool_registration":
            threshold = self.performance_thresholds["tool_registration_ms"]
        elif operation_type == "client_operation":
            threshold = self.performance_thresholds["client_operation_ms"]
        elif operation_type == "dependency_check":
            threshold = self.performance_thresholds["dependency_check_ms"]
        else:
            threshold = 100  # Default threshold
        
        if avg_time_ms > threshold * 2:
            return "SLOW"
        elif avg_time_ms > threshold:
            return "ACCEPTABLE"
        elif avg_time_ms < threshold * 0.5:
            return "EXCELLENT"
        else:
            return "GOOD"
    
    def run_mcp_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive MCP performance tests."""
        print("🚀 Starting MCP Performance Test")
        print("=" * 60)
        
        results = {}
        
        # Test tool registry
        tool_result = self.test_tool_registry_performance()
        if tool_result:
            results["tool_registry"] = tool_result
        
        # Test MCP client
        client_result = self.test_mcp_client_performance()
        if client_result:
            results["mcp_client"] = client_result
        
        # Test dependency manager
        dep_result = self.test_dependency_manager_performance()
        if dep_result:
            results["dependency_manager"] = dep_result
        
        # Generate summary
        summary = self._generate_summary(results)
        
        print("\n" + "=" * 60)
        print("📊 MCP PERFORMANCE SUMMARY")
        print("=" * 60)
        
        for test_type, result in results.items():
            print(f"📊 {test_type.upper()}:")
            for key, value in result.items():
                if "performance" in key and isinstance(value, str):
                    status = "✅" if value in ["EXCELLENT", "GOOD"] else "⚠️" if value == "ACCEPTABLE" else "❌"
                    print(f"  {status} {key}: {value}")
                elif "time_ms" in key:
                    print(f"  ⏱️  {key}: {value}ms")
        
        print(f"\nOverall MCP Performance: {summary['overall_grade']}")
        print(f"Average Operation Time: {summary['avg_operation_time']:.2f}ms")
        print(f"Total Tests: {summary['total_tests']}")
        
        return results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        if not results:
            return {"overall_grade": "FAIL", "avg_operation_time": 0, "total_tests": 0}
        
        all_times = []
        performance_scores = []
        
        for result in results.values():
            for key, value in result.items():
                if "time_ms" in key and isinstance(value, (int, float)):
                    all_times.append(value)
                elif "performance" in key and isinstance(value, str):
                    performance_scores.append(value)
        
        if not all_times:
            return {"overall_grade": "FAIL", "avg_operation_time": 0, "total_tests": 0}
        
        avg_operation_time = statistics.mean(all_times)
        
        # Calculate overall grade
        excellent_count = performance_scores.count("EXCELLENT")
        good_count = performance_scores.count("GOOD")
        acceptable_count = performance_scores.count("ACCEPTABLE")
        slow_count = performance_scores.count("SLOW")
        
        total_scores = len(performance_scores)
        
        if slow_count > 0:
            overall_grade = "SLOW"
        elif excellent_count >= total_scores * 0.7:
            overall_grade = "EXCELLENT"
        elif (excellent_count + good_count) >= total_scores * 0.8:
            overall_grade = "GOOD"
        else:
            overall_grade = "ACCEPTABLE"
        
        return {
            "overall_grade": overall_grade,
            "avg_operation_time": avg_operation_time,
            "total_tests": len(results),
            "excellent_count": excellent_count,
            "good_count": good_count,
            "acceptable_count": acceptable_count,
            "slow_count": slow_count
        }


def main():
    """Run the MCP performance test."""
    test_suite = MCPPerformanceTest()
    results = test_suite.run_mcp_performance_test()
    return results


if __name__ == "__main__":
    main() 