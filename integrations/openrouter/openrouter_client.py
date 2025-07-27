"""
BMAD OpenRouter Client

Dit module biedt multi-LLM routing en provider integratie via OpenRouter.
Ondersteunt GPT, Claude, Gemini en andere LLM providers met automatische fallback en load balancing.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import openai
from openai import AsyncOpenAI
from bmad.agents.core.confidence_scoring import confidence_scoring

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    META = "meta"

class ModelTier(Enum):
    FAST = "fast"      # Quick responses, lower cost
    BALANCED = "balanced"  # Good balance of speed/cost/quality
    QUALITY = "quality"    # Highest quality, higher cost

@dataclass
class LLMConfig:
    """Configuration for LLM provider and model."""
    provider: LLMProvider
    model: str
    tier: ModelTier = ModelTier.BALANCED
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retries: int = 3

@dataclass
class RoutingStrategy:
    """Strategy for LLM routing and fallback."""
    primary_config: LLMConfig
    fallback_configs: List[LLMConfig] = field(default_factory=list)
    load_balancing: bool = True
    cost_optimization: bool = True
    quality_threshold: float = 0.8
    max_retries: int = 3

@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    latency: float
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class OpenRouterClient:
    """
    Multi-LLM client met routing, fallback en load balancing via OpenRouter.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.http_session = None
        
        # Provider configurations
        self.provider_configs = self._initialize_provider_configs()
        
        # Load balancing state
        self.provider_stats = {}
        self.response_history = []
        
        # Routing strategies
        self.routing_strategies = self._initialize_routing_strategies()
        
        logger.info("OpenRouter client geïnitialiseerd")
    
    def _initialize_provider_configs(self) -> Dict[LLMProvider, List[LLMConfig]]:
        """Initialize default provider configurations."""
        configs = {
            LLMProvider.OPENAI: [
                LLMConfig(LLMProvider.OPENAI, "gpt-4o", ModelTier.QUALITY),
                LLMConfig(LLMProvider.OPENAI, "gpt-4o-mini", ModelTier.BALANCED),
                LLMConfig(LLMProvider.OPENAI, "gpt-3.5-turbo", ModelTier.FAST),
            ],
            LLMProvider.ANTHROPIC: [
                LLMConfig(LLMProvider.ANTHROPIC, "claude-3-5-sonnet-20241022", ModelTier.QUALITY),
                LLMConfig(LLMProvider.ANTHROPIC, "claude-3-5-haiku-20241022", ModelTier.BALANCED),
                LLMConfig(LLMProvider.ANTHROPIC, "claude-3-haiku-20240307", ModelTier.FAST),
            ],
            LLMProvider.GOOGLE: [
                LLMConfig(LLMProvider.GOOGLE, "gemini-1.5-pro", ModelTier.QUALITY),
                LLMConfig(LLMProvider.GOOGLE, "gemini-1.5-flash", ModelTier.BALANCED),
                LLMConfig(LLMProvider.GOOGLE, "gemini-1.0-pro", ModelTier.FAST),
            ],
            LLMProvider.MISTRAL: [
                LLMConfig(LLMProvider.MISTRAL, "mistral-large", ModelTier.QUALITY),
                LLMConfig(LLMProvider.MISTRAL, "mistral-medium", ModelTier.BALANCED),
                LLMConfig(LLMProvider.MISTRAL, "mistral-small", ModelTier.FAST),
            ],
        }
        return configs
    
    def _initialize_routing_strategies(self) -> Dict[str, RoutingStrategy]:
        """Initialize default routing strategies."""
        strategies = {
            "development": RoutingStrategy(
                primary_config=LLMConfig(LLMProvider.OPENAI, "gpt-4o-mini", ModelTier.BALANCED),
                fallback_configs=[
                    LLMConfig(LLMProvider.ANTHROPIC, "claude-3-5-haiku-20241022", ModelTier.BALANCED),
                    LLMConfig(LLMProvider.GOOGLE, "gemini-1.5-flash", ModelTier.BALANCED),
                ],
                load_balancing=True,
                cost_optimization=True,
            ),
            "production": RoutingStrategy(
                primary_config=LLMConfig(LLMProvider.OPENAI, "gpt-4o", ModelTier.QUALITY),
                fallback_configs=[
                    LLMConfig(LLMProvider.ANTHROPIC, "claude-3-5-sonnet-20241022", ModelTier.QUALITY),
                    LLMConfig(LLMProvider.GOOGLE, "gemini-1.5-pro", ModelTier.QUALITY),
                ],
                load_balancing=True,
                cost_optimization=False,
            ),
            "testing": RoutingStrategy(
                primary_config=LLMConfig(LLMProvider.OPENAI, "gpt-3.5-turbo", ModelTier.FAST),
                fallback_configs=[
                    LLMConfig(LLMProvider.ANTHROPIC, "claude-3-haiku-20240307", ModelTier.FAST),
                    LLMConfig(LLMProvider.GOOGLE, "gemini-1.0-pro", ModelTier.FAST),
                ],
                load_balancing=True,
                cost_optimization=True,
            ),
        }
        return strategies
    
    async def generate_response(
        self,
        prompt: str,
        strategy_name: str = "development",
        custom_config: Optional[LLMConfig] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Generate response using the specified routing strategy.
        
        Args:
            prompt: The input prompt
            strategy_name: Name of the routing strategy to use
            custom_config: Optional custom LLM configuration
            context: Additional context for the request
            
        Returns:
            LLMResponse with content and metadata
        """
        start_time = time.time()
        
        if strategy_name not in self.routing_strategies:
            raise ValueError(f"Unknown routing strategy: {strategy_name}")
        
        strategy = self.routing_strategies[strategy_name]
        
        # Use custom config if provided, otherwise use strategy config
        config = custom_config or strategy.primary_config
        
        # Try primary config first
        try:
            response = await self._call_llm(config, prompt, context)
            response.confidence_score = await self._calculate_confidence(response, prompt)
            
            # Update provider stats
            self._update_provider_stats(config.provider, response)
            
            return response
            
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}")
            
            # Try fallback configs
            for fallback_config in strategy.fallback_configs:
                try:
                    response = await self._call_llm(fallback_config, prompt, context)
                    response.confidence_score = await self._calculate_confidence(response, prompt)
                    
                    # Update provider stats
                    self._update_provider_stats(fallback_config.provider, response)
                    
                    logger.info(f"Used fallback LLM: {fallback_config.provider.value}/{fallback_config.model}")
                    return response
                    
                except Exception as fallback_error:
                    logger.warning(f"Fallback LLM failed: {fallback_error}")
                    continue
            
            # All configs failed
            raise Exception(f"All LLM providers failed for strategy: {strategy_name}")
    
    async def _call_llm(
        self,
        config: LLMConfig,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Make a call to the LLM provider."""
        start_time = time.time()
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Add context if provided
        if context:
            context_message = f"\n\nContext: {json.dumps(context, indent=2)}"
            messages[0]["content"] += context_message
        
        try:
            # Make the API call using OpenAI client
            response = await self.client.chat.completions.create(
                model=config.model,
                messages=messages,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                timeout=config.timeout,
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = self._calculate_cost(config.provider, config.model, tokens_used)
            
            return LLMResponse(
                content=content,
                model=config.model,
                provider=config.provider.value,
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                confidence_score=0.0,  # Will be calculated later
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model_id": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _calculate_cost(self, provider: LLMProvider, model: str, tokens: int) -> float:
        """Calculate the cost of the API call."""
        # Simplified cost calculation - in production, use actual pricing
        base_costs = {
            LLMProvider.OPENAI: {
                "gpt-4o": 0.005,
                "gpt-4o-mini": 0.00015,
                "gpt-3.5-turbo": 0.0005,
            },
            LLMProvider.ANTHROPIC: {
                "claude-3-5-sonnet-20241022": 0.003,
                "claude-3-5-haiku-20241022": 0.00025,
                "claude-3-haiku-20240307": 0.00025,
            },
            LLMProvider.GOOGLE: {
                "gemini-1.5-pro": 0.0025,
                "gemini-1.5-flash": 0.000075,
                "gemini-1.0-pro": 0.0005,
            },
            LLMProvider.MISTRAL: {
                "mistral-large": 0.0024,
                "mistral-medium": 0.0007,
                "mistral-small": 0.0002,
            },
        }
        
        cost_per_1k = base_costs.get(provider, {}).get(model, 0.001)
        return (tokens / 1000) * cost_per_1k
    
    async def _calculate_confidence(self, response: LLMResponse, original_prompt: str) -> float:
        """Calculate confidence score for the response."""
        try:
            # Use the confidence scoring system
            confidence = await confidence_scoring(
                prompt=original_prompt,
                response=response.content,
                model=response.model,
                provider=response.provider,
                metadata=response.metadata
            )
            return confidence
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5  # Default confidence
    
    def _update_provider_stats(self, provider: LLMProvider, response: LLMResponse):
        """Update provider statistics for load balancing."""
        if provider.value not in self.provider_stats:
            self.provider_stats[provider.value] = {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "success_rate": 1.0,
                "last_used": time.time(),
            }
        
        stats = self.provider_stats[provider.value]
        stats["total_calls"] += 1
        stats["total_tokens"] += response.tokens_used
        stats["total_cost"] += response.cost
        stats["avg_latency"] = (stats["avg_latency"] * (stats["total_calls"] - 1) + response.latency) / stats["total_calls"]
        stats["last_used"] = time.time()
        
        # Store response in history
        self.response_history.append({
            "provider": provider.value,
            "model": response.model,
            "tokens": response.tokens_used,
            "cost": response.cost,
            "latency": response.latency,
            "confidence": response.confidence_score,
            "timestamp": time.time(),
        })
        
        # Keep only last 1000 responses
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-1000:]
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get current provider statistics."""
        return self.provider_stats
    
    def get_cost_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get cost analysis for the specified period."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        recent_responses = [r for r in self.response_history if r["timestamp"] > cutoff_time]
        
        total_cost = sum(r["cost"] for r in recent_responses)
        total_tokens = sum(r["tokens"] for r in recent_responses)
        
        provider_costs = {}
        for response in recent_responses:
            provider = response["provider"]
            if provider not in provider_costs:
                provider_costs[provider] = {"cost": 0.0, "tokens": 0, "calls": 0}
            provider_costs[provider]["cost"] += response["cost"]
            provider_costs[provider]["tokens"] += response["tokens"]
            provider_costs[provider]["calls"] += 1
        
        return {
            "period_days": days,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "provider_breakdown": provider_costs,
            "avg_cost_per_call": total_cost / len(recent_responses) if recent_responses else 0,
        }
    
    def add_routing_strategy(self, name: str, strategy: RoutingStrategy):
        """Add a custom routing strategy."""
        self.routing_strategies[name] = strategy
        logger.info(f"Routing strategy '{name}' toegevoegd")
    
    def get_available_models(self) -> Dict[LLMProvider, List[str]]:
        """Get list of available models per provider."""
        models = {}
        for provider, configs in self.provider_configs.items():
            models[provider] = [config.model for config in configs]
        return models

# Factory function
def create_openrouter_client(api_key: str, base_url: str = "https://openrouter.ai/api/v1") -> OpenRouterClient:
    """Create a new OpenRouter client instance."""
    return OpenRouterClient(api_key, base_url) 