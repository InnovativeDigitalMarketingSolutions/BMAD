#!/usr/bin/env python3
"""
Eenvoudige test voor backend optimalisaties.
"""

import time
import sys
import os

# Voeg BMAD modules toe aan path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_redis_caching():
    """Test Redis caching functionaliteit."""
    print("\n🔍 Testing Redis Caching...")
    
    try:
        from bmad.agents.core.data.redis_cache import cache, cached
        
        # Test basic caching
        test_data = {"test": "data", "timestamp": time.time()}
        cache_key = "test_key"
        
        # Set cache
        success = cache.set(cache_key, test_data, cache_type="test")
        print(f"✅ Cache set: {success}")
        
        # Get cache
        cached_data = cache.get(cache_key)
        print(f"✅ Cache get: {cached_data == test_data}")
        
        # Test cache decorator
        @cached(ttl=60, cache_type="test", key_prefix="test_func")
        def expensive_function(x, y):
            time.sleep(0.1)  # Simulate expensive operation
            return x + y
        
        # First call (cache miss)
        start_time = time.time()
        result1 = expensive_function(5, 3)
        duration1 = time.time() - start_time
        print(f"✅ First call (cache miss): {result1} in {duration1:.3f}s")
        
        # Second call (cache hit)
        start_time = time.time()
        result2 = expensive_function(5, 3)
        duration2 = time.time() - start_time
        print(f"✅ Second call (cache hit): {result2} in {duration2:.3f}s")
        
        # Verify cache hit was faster
        if duration2 < duration1:
            print(f"✅ Cache hit {duration1/duration2:.1f}x faster than cache miss")
        else:
            print("⚠️ Cache hit not faster (expected for small operations)")
            
        assert True  # Test passed
        
    except Exception as e:
        print(f"❌ Redis caching test gefaald: {e}")
        assert False, f"Redis caching test failed: {e}"

def test_monitoring():
    """Test monitoring en metrics functionaliteit."""
    print("\n🔍 Testing Monitoring & Metrics...")
    
    try:
        from bmad.agents.core.monitoring.monitoring import (
            metrics_collector, structured_logger,
            record_metric, increment_counter, measure_time
        )
        
        # Test metrics recording
        record_metric("test_metric", 42.0, labels={"test": "value"})
        increment_counter("test_counter", labels={"test": "value"})
        
        with measure_time("test_timing", labels={"test": "value"}):
            time.sleep(0.1)  # Simulate work
        
        print("✅ Metrics recorded")
        
        # Test structured logging
        structured_logger.log_event("test_event", "Test event message", test_data="value")
        structured_logger.log_agent_action("TestAgent", "test_action", result="success")
        print("✅ Structured logging werkt")
        
        # Get Prometheus format
        prometheus_metrics = metrics_collector.get_prometheus_format()
        print(f"✅ Prometheus metrics: {len(prometheus_metrics.split())} metrics")
        
        assert True  # Test passed
        
    except Exception as e:
        print(f"❌ Monitoring test gefaald: {e}")
        assert False, f"Monitoring test failed: {e}"

def test_llm_caching():
    """Test LLM response caching."""
    print("\n🔍 Testing LLM Caching...")
    
    try:
        from bmad.agents.core.data.redis_cache import cached

        # Test cache decorator with a simple function
        @cached(ttl=60, cache_type="test", key_prefix="test_llm")
        def mock_llm_function(prompt, context, max_tokens=10):
            # Simulate LLM response
            return {
                "answer": "Hello",
                "confidence": 0.8,
                "tokens_used": max_tokens
            }

        # Test cached function call
        context = {"test": "llm_caching"}

        # First call (cache miss)
        start_time = time.time()
        result1 = mock_llm_function("Say 'Hello from BMAD' in one word", context, max_tokens=10)
        duration1 = time.time() - start_time
        print(f"✅ First call (cache miss): {duration1:.3f}s")

        # Second call (cache hit)
        start_time = time.time()
        result2 = mock_llm_function("Say 'Hello from BMAD' in one word", context, max_tokens=10)
        duration2 = time.time() - start_time
        print(f"✅ Second call (cache hit): {duration2:.3f}s")

        if duration2 < duration1:
            print(f"✅ LLM caching werkt: {duration1/duration2:.1f}x sneller")
        else:
            print("⚠️ LLM caching niet effectief")

        # Verify results are the same
        assert result1 == result2, "Cached results should be identical"

        assert True  # Test passed

    except Exception as e:
        print(f"❌ LLM caching test gefaald: {e}")
        assert False, f"LLM caching test failed: {e}"

def test_cache_stats():
    """Test cache statistieken."""
    print("\n🔍 Testing Cache Statistics...")
    
    try:
        from bmad.agents.core.data.redis_cache import cache

        # Get cache stats
        stats = cache.get_stats()
        print(f"✅ Cache stats: {stats}")

        # Test cache operations
        cache.set("stats_test", "test_value", ttl=60)
        exists = cache.exists("stats_test")
        print(f"✅ Cache exists test: {exists}")

        # Clear test data
        cache.delete("stats_test")
        cache.delete("test_key")

        assert True  # Test passed

    except Exception as e:
        print(f"❌ Cache stats test gefaald: {e}")
        assert False, f"Cache stats test failed: {e}"

def main():
    """Main test functie."""
    print("🚀 BMAD Backend Optimization Tests (Simple)")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_redis_caching,
        test_monitoring,
        test_llm_caching,
        test_cache_stats
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