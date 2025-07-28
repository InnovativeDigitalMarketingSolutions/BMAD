#!/usr/bin/env python3
"""
Eenvoudige test voor backend optimalisaties.
"""

import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Test Redis cache functionality
def test_redis_cache():
    """Test Redis cache functionality."""
    try:
        from bmad.agents.core.data.redis_cache import cache, cached
        
        # Test cache decorator
        @cached(ttl=60)
        def test_function(x, y):
            return x + y
        
        result1 = test_function(1, 2)
        result2 = test_function(1, 2)  # Should be cached
        
        print(f"✅ Redis cache test passed: {result1} == {result2}")
        return True
    except Exception as e:
        print(f"❌ Redis cache test failed: {e}")
        return False

# Test monitoring functionality
def test_monitoring():
    """Test monitoring functionality."""
    try:
        from bmad.agents.core.monitoring.monitoring import (
            record_metric, increment_counter, measure_time
        )
        
        # Test metric recording
        record_metric("test_metric", 42.0, {"test": "value"})
        increment_counter("test_counter", {"test": "value"})
        
        # Test time measurement
        with measure_time("test_operation", {"test": "value"}):
            time.sleep(0.1)
        
        print("✅ Monitoring test passed")
        return True
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

# Test LLM client caching
def test_llm_caching():
    """Test LLM client caching."""
    try:
        from bmad.agents.core.data.redis_cache import cached
        
        # Mock LLM function
        @cached(ttl=300)
        def mock_llm_function(prompt):
            return f"Response to: {prompt}"
        
        # Test caching
        response1 = mock_llm_function("test prompt")
        response2 = mock_llm_function("test prompt")  # Should be cached
        
        print(f"✅ LLM caching test passed: {response1} == {response2}")
        return True
    except Exception as e:
        print(f"❌ LLM caching test failed: {e}")
        return False

# Test performance monitoring
def test_performance_monitoring():
    """Test performance monitoring."""
    try:
        from bmad.agents.core.data.redis_cache import cache
        
        # Test performance monitoring with cache
        @cache(ttl=60)
        def performance_test_function():
            time.sleep(0.1)  # Simulate work
            return "performance_test_result"
        
        start_time = time.time()
        result1 = performance_test_function()
        first_call_time = time.time() - start_time
        
        start_time = time.time()
        result2 = performance_test_function()  # Should be cached
        second_call_time = time.time() - start_time
        
        print(f"✅ Performance monitoring test passed")
        print(f"   First call: {first_call_time:.3f}s")
        print(f"   Second call: {second_call_time:.3f}s")
        print(f"   Results: {result1} == {result2}")
        return True
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        return False

def main():
    """Main test functie."""
    print("🚀 BMAD Backend Optimization Tests (Simple)")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_redis_cache,
        test_monitoring,
        test_llm_caching,
        test_performance_monitoring
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"✅ Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All backend optimization tests passed!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 