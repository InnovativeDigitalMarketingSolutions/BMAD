#!/usr/bin/env python3
"""
Database Performance Test
Focused test for measuring database operations and caching performance
"""

import time
import statistics
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.agents.core.data.redis_cache import RedisCache
from bmad.agents.core.data.supabase_context import save_context, get_context


class DatabasePerformanceTest:
    """Focused performance test for database operations."""
    
    def __init__(self):
        self.results = {}
        self.performance_thresholds = {
            "query_time_ms": 100,  # 100ms max for queries
            "cache_hit_time_ms": 10,  # 10ms max for cache hits
            "error_rate_percent": 5  # 5% max error rate
        }
    
    def test_redis_cache_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Test Redis cache performance."""
        print("🧪 Testing Redis Cache Performance...")
        
        try:
            cache = RedisCache()
            
            # Test cache set performance
            set_times = []
            for i in range(iterations):
                key = f"test_key_{i}"
                value = f"test_value_{i}"
                
                start_time = time.time()
                cache.set(key, value, ttl=60)
                end_time = time.time()
                
                set_time_ms = (end_time - start_time) * 1000
                set_times.append(set_time_ms)
            
            # Test cache get performance (cache hits)
            get_times = []
            for i in range(iterations):
                key = f"test_key_{i}"
                
                start_time = time.time()
                result = cache.get(key)
                end_time = time.time()
                
                get_time_ms = (end_time - start_time) * 1000
                get_times.append(get_time_ms)
            
            # Test cache miss performance
            miss_times = []
            for i in range(iterations):
                key = f"miss_key_{i}"
                
                start_time = time.time()
                result = cache.get(key)
                end_time = time.time()
                
                miss_time_ms = (end_time - start_time) * 1000
                miss_times.append(miss_time_ms)
            
            # Calculate statistics
            avg_set_time = statistics.mean(set_times)
            avg_get_time = statistics.mean(get_times)
            avg_miss_time = statistics.mean(miss_times)
            
            result = {
                "test_type": "redis_cache",
                "iterations": iterations,
                "avg_set_time_ms": round(avg_set_time, 2),
                "avg_get_time_ms": round(avg_get_time, 2),
                "avg_miss_time_ms": round(avg_miss_time, 2),
                "set_performance": self._evaluate_performance(avg_set_time, "set"),
                "get_performance": self._evaluate_performance(avg_get_time, "get"),
                "miss_performance": self._evaluate_performance(avg_miss_time, "miss")
            }
            
            print(f"  ✅ Redis Cache SET: {avg_set_time:.2f}ms avg")
            print(f"  ✅ Redis Cache GET (hit): {avg_get_time:.2f}ms avg")
            print(f"  ✅ Redis Cache GET (miss): {avg_miss_time:.2f}ms avg")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Redis Cache Test Failed: {e}")
            return None
    
    def test_supabase_context_performance(self, iterations: int = 5) -> Dict[str, Any]:
        """Test Supabase context operations performance."""
        print("🧪 Testing Supabase Context Performance...")
        
        try:
            # Test context save performance
            save_times = []
            for i in range(iterations):
                context_data = {
                    "test_key": f"test_value_{i}",
                    "timestamp": time.time(),
                    "iteration": i
                }
                
                start_time = time.time()
                save_context("test_agent", f"test_context_{i}", context_data)
                end_time = time.time()
                
                save_time_ms = (end_time - start_time) * 1000
                save_times.append(save_time_ms)
            
            # Test context load performance
            load_times = []
            for i in range(iterations):
                start_time = time.time()
                context_data = get_context("test_agent", f"test_context_{i}")
                end_time = time.time()
                
                load_time_ms = (end_time - start_time) * 1000
                load_times.append(load_time_ms)
            
            # Calculate statistics
            avg_save_time = statistics.mean(save_times)
            avg_load_time = statistics.mean(load_times)
            
            result = {
                "test_type": "supabase_context",
                "iterations": iterations,
                "avg_save_time_ms": round(avg_save_time, 2),
                "avg_load_time_ms": round(avg_load_time, 2),
                "save_performance": self._evaluate_performance(avg_save_time, "save"),
                "load_performance": self._evaluate_performance(avg_load_time, "load")
            }
            
            print(f"  ✅ Supabase Context SAVE: {avg_save_time:.2f}ms avg")
            print(f"  ✅ Supabase Context LOAD: {avg_load_time:.2f}ms avg")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Supabase Context Test Failed: {e}")
            return None
    
    def _evaluate_performance(self, avg_time_ms: float, operation_type: str) -> str:
        """Evaluate performance based on operation type."""
        if operation_type == "get":
            threshold = self.performance_thresholds["cache_hit_time_ms"]
        else:
            threshold = self.performance_thresholds["query_time_ms"]
        
        if avg_time_ms > threshold * 2:
            return "SLOW"
        elif avg_time_ms > threshold:
            return "ACCEPTABLE"
        elif avg_time_ms < threshold * 0.5:
            return "EXCELLENT"
        else:
            return "GOOD"
    
    def run_database_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive database performance tests."""
        print("🚀 Starting Database Performance Test")
        print("=" * 60)
        
        results = {}
        
        # Test Redis cache
        redis_result = self.test_redis_cache_performance()
        if redis_result:
            results["redis_cache"] = redis_result
        
        # Test Supabase context
        supabase_result = self.test_supabase_context_performance()
        if supabase_result:
            results["supabase_context"] = supabase_result
        
        # Generate summary
        summary = self._generate_summary(results)
        
        print("\n" + "=" * 60)
        print("📊 DATABASE PERFORMANCE SUMMARY")
        print("=" * 60)
        
        for test_type, result in results.items():
            print(f"📊 {test_type.upper()}:")
            for key, value in result.items():
                if "performance" in key and isinstance(value, str):
                    status = "✅" if value in ["EXCELLENT", "GOOD"] else "⚠️" if value == "ACCEPTABLE" else "❌"
                    print(f"  {status} {key}: {value}")
                elif "time_ms" in key:
                    print(f"  ⏱️  {key}: {value}ms")
        
        print(f"\nOverall Database Performance: {summary['overall_grade']}")
        print(f"Average Query Time: {summary['avg_query_time']:.2f}ms")
        print(f"Total Tests: {summary['total_tests']}")
        
        return results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        if not results:
            return {"overall_grade": "FAIL", "avg_query_time": 0, "total_tests": 0}
        
        all_times = []
        performance_scores = []
        
        for result in results.values():
            for key, value in result.items():
                if "time_ms" in key and isinstance(value, (int, float)):
                    all_times.append(value)
                elif "performance" in key and isinstance(value, str):
                    performance_scores.append(value)
        
        if not all_times:
            return {"overall_grade": "FAIL", "avg_query_time": 0, "total_tests": 0}
        
        avg_query_time = statistics.mean(all_times)
        
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
            "avg_query_time": avg_query_time,
            "total_tests": len(results),
            "excellent_count": excellent_count,
            "good_count": good_count,
            "acceptable_count": acceptable_count,
            "slow_count": slow_count
        }


def main():
    """Run the database performance test."""
    test_suite = DatabasePerformanceTest()
    results = test_suite.run_database_performance_test()
    return results


if __name__ == "__main__":
    main() 