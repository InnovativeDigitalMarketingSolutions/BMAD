#!/usr/bin/env python3
"""
Async LLM Client for Performance Optimization
Provides async/await support for LLM calls with caching and connection pooling
"""

import asyncio
import aiohttp
import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import redis
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """LLM request configuration."""
    prompt: str
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30

@dataclass
class LLMResponse:
    """LLM response data."""
    content: str
    model: str
    usage: Dict[str, int]
    response_time: float
    cached: bool = False
    error: Optional[str] = None

class AsyncLLMClient:
    """Async LLM client with caching and connection pooling."""
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 3600):
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.session: Optional[aiohttp.ClientSession] = None
        self.redis_client: Optional[redis.Redis] = None
        self.connection_pool = []
        self.max_connections = 10
        self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis connection for caching."""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}")
            self.redis_client = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling."""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self.session
    
    def _generate_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key for request."""
        request_data = {
            'prompt': request.prompt,
            'model': request.model,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature
        }
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response if available."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return LLMResponse(
                    content=data['content'],
                    model=data['model'],
                    usage=data['usage'],
                    response_time=0.0,
                    cached=True
                )
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache response for future use."""
        if not self.redis_client:
            return
        
        try:
            cache_data = {
                'content': response.content,
                'model': response.model,
                'usage': response.usage,
                'timestamp': datetime.now().isoformat()
            }
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def ask_async(self, request: LLMRequest) -> LLMResponse:
        """Send async LLM request with caching."""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            logger.info(f"Cache hit for request: {cache_key[:8]}...")
            return cached_response
        
        # Make actual request
        try:
            session = await self._get_session()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': request.model,
                'messages': [{'role': 'user', 'content': request.prompt}],
                'max_tokens': request.max_tokens,
                'temperature': request.temperature
            }
            
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    usage = data['usage']
                    
                    llm_response = LLMResponse(
                        content=content,
                        model=request.model,
                        usage=usage,
                        response_time=time.time() - start_time
                    )
                    
                    # Cache the response
                    await self._cache_response(cache_key, llm_response)
                    
                    logger.info(f"LLM request completed in {llm_response.response_time:.2f}s")
                    return llm_response
                else:
                    error_text = await response.text()
                    logger.error(f"LLM API error: {response.status} - {error_text}")
                    return LLMResponse(
                        content="",
                        model=request.model,
                        usage={},
                        response_time=time.time() - start_time,
                        error=f"API error: {response.status}"
                    )
        
        except asyncio.TimeoutError:
            logger.error("LLM request timeout")
            return LLMResponse(
                content="",
                model=request.model,
                usage={},
                response_time=time.time() - start_time,
                error="Request timeout"
            )
        except Exception as e:
            logger.error(f"LLM request error: {e}")
            return LLMResponse(
                content="",
                model=request.model,
                usage={},
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def ask_batch(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """Send multiple LLM requests concurrently."""
        tasks = [self.ask_async(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close(self):
        """Close HTTP session and connections."""
        if self.session and not self.session.closed:
            await self.session.close()
        
        if self.redis_client:
            self.redis_client.close()

def async_llm_call(func):
    """Decorator to convert sync LLM calls to async."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Convert sync function to async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper

# Global async LLM client instance
_async_llm_client: Optional[AsyncLLMClient] = None

def get_async_llm_client() -> AsyncLLMClient:
    """Get global async LLM client instance."""
    global _async_llm_client
    if _async_llm_client is None:
        _async_llm_client = AsyncLLMClient()
    return _async_llm_client

async def ask_openai_async(prompt: str, **kwargs) -> str:
    """Async wrapper for OpenAI API calls."""
    client = get_async_llm_client()
    request = LLMRequest(prompt=prompt, **kwargs)
    response = await client.ask_async(request)
    
    if response.error:
        raise Exception(f"LLM request failed: {response.error}")
    
    return response.content

# Performance monitoring
class LLMPerformanceMonitor:
    """Monitor LLM performance metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.cache_hits = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.start_time = time.time()
    
    def record_request(self, response_time: float, cached: bool = False, error: bool = False):
        """Record request metrics."""
        self.request_count += 1
        self.total_response_time += response_time
        
        if cached:
            self.cache_hits += 1
        
        if error:
            self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        uptime = time.time() - self.start_time
        avg_response_time = self.total_response_time / max(self.request_count, 1)
        cache_hit_rate = self.cache_hits / max(self.request_count, 1) * 100
        error_rate = self.error_count / max(self.request_count, 1) * 100
        
        return {
            'total_requests': self.request_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': cache_hit_rate,
            'avg_response_time': avg_response_time,
            'error_count': self.error_count,
            'error_rate': error_rate,
            'uptime': uptime,
            'requests_per_second': self.request_count / max(uptime, 1)
        }

# Global performance monitor
_llm_performance_monitor = LLMPerformanceMonitor()

def get_llm_performance_stats() -> Dict[str, Any]:
    """Get LLM performance statistics."""
    return _llm_performance_monitor.get_stats() 