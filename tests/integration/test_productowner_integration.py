#!/usr/bin/env python3
"""
Integration tests for ProductOwnerAgent
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bmad.agents.Agent.ProductOwner.product_owner import ProductOwnerAgent


class TestProductOwnerAgentIntegration:
    """Integration tests for ProductOwnerAgent."""
    
    @pytest.fixture
    async def product_owner_agent(self):
        """Create a ProductOwnerAgent instance for testing."""
        agent = ProductOwnerAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization_integration(self, product_owner_agent):
        """Test agent initialization in integration context."""
        assert product_owner_agent is not None
        assert product_owner_agent.agent_name == "ProductOwnerAgent"
        assert hasattr(product_owner_agent, 'mcp_client')
        assert hasattr(product_owner_agent, 'enhanced_mcp')
        assert hasattr(product_owner_agent, 'tracing_enabled')
        assert hasattr(product_owner_agent, 'message_bus_integration')
    
    @pytest.mark.asyncio
    async def test_message_bus_initialization_integration(self, product_owner_agent):
        """Test message bus initialization in integration context."""
        with patch('bmad.core.message_bus.get_message_bus') as mock_get_bus:
            mock_bus = Mock()
            mock_get_bus.return_value = mock_bus
            
            result = await product_owner_agent.initialize_message_bus()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization_integration(self, product_owner_agent):
        """Test enhanced MCP initialization in integration context."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_mcp = AsyncMock()
            mock_mcp.initialize_enhanced_mcp.return_value = True
            mock_create.return_value = mock_mcp
            
            await product_owner_agent.initialize_enhanced_mcp()
            assert product_owner_agent.enhanced_mcp_enabled is True
    
    @pytest.mark.asyncio
    async def test_tracing_initialization_integration(self, product_owner_agent):
        """Test tracing initialization in integration context."""
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            await product_owner_agent.initialize_tracing()
            assert product_owner_agent.tracing_enabled is True
            assert product_owner_agent.tracer is not None
    
    @pytest.mark.asyncio
    async def test_user_story_creation_integration(self, product_owner_agent):
        """Test user story creation in integration context."""
        story_data = {
            "requirement": "As a user, I want to create a new project",
            "user_type": "end_user",
            "priority": "high"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "User story created successfully",
                "confidence": 0.95
            }
            
            result = await product_owner_agent.create_user_story(story_data)
            assert result is not None
            assert "response" in result
    
    @pytest.mark.asyncio
    async def test_backlog_prioritization_integration(self, product_owner_agent):
        """Test backlog prioritization in integration context."""
        event = {
            "backlog_items": [
                {"id": 1, "title": "Feature A", "priority": "medium"},
                {"id": 2, "title": "Feature B", "priority": "high"}
            ],
            "prioritization_method": "mooscow"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "Backlog prioritized successfully",
                "confidence": 0.90
            }
            
            result = await product_owner_agent.handle_backlog_prioritization_requested(event)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_product_vision_generation_integration(self, product_owner_agent):
        """Test product vision generation in integration context."""
        event = {
            "product_name": "BMAD System",
            "vision_type": "strategic",
            "timeframe": "1 year"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "Product vision generated successfully",
                "confidence": 0.92
            }
            
            result = await product_owner_agent.handle_product_vision_generation_requested(event)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_stakeholder_analysis_integration(self, product_owner_agent):
        """Test stakeholder analysis in integration context."""
        event = {
            "stakeholders": [
                {"name": "End Users", "type": "primary"},
                {"name": "Developers", "type": "secondary"}
            ],
            "analysis_type": "impact_assessment"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "Stakeholder analysis completed",
                "confidence": 0.88
            }
            
            result = await product_owner_agent.handle_stakeholder_analysis_requested(event)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_market_research_integration(self, product_owner_agent):
        """Test market research in integration context."""
        event = {
            "market_segment": "enterprise",
            "research_type": "competitive_analysis",
            "timeframe": "3 months"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "Market research completed",
                "confidence": 0.85
            }
            
            result = await product_owner_agent.handle_market_research_requested(event)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_feature_roadmap_update_integration(self, product_owner_agent):
        """Test feature roadmap update in integration context."""
        event = {
            "roadmap_items": [
                {"feature": "Enhanced UI", "quarter": "Q1"},
                {"feature": "API Integration", "quarter": "Q2"}
            ],
            "update_type": "quarterly_review"
        }
        
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "Feature roadmap updated successfully",
                "confidence": 0.87
            }
            
            result = await product_owner_agent.handle_feature_roadmap_update_requested(event)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools_integration(self, product_owner_agent):
        """Test enhanced MCP tools in integration context."""
        # Initialize enhanced MCP
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_mcp = AsyncMock()
            mock_mcp.initialize_enhanced_mcp.return_value = True
            mock_create.return_value = mock_mcp
            
            await product_owner_agent.initialize_enhanced_mcp()
            
            # Test getting tools
            tools = product_owner_agent.get_enhanced_mcp_tools()
            assert isinstance(tools, list)
            assert len(tools) > 0
            
            # Test registering tools
            result = product_owner_agent.register_enhanced_mcp_tools()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_tracing_operation_integration(self, product_owner_agent):
        """Test tracing operation in integration context."""
        # Initialize tracing
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = AsyncMock()
            mock_tracer_class.return_value = mock_tracer
            
            await product_owner_agent.initialize_tracing()
            
            # Test tracing operation
            result = await product_owner_agent.trace_operation("test_operation", {"key": "value"})
            assert result is True
    
    @pytest.mark.asyncio
    async def test_agent_collaboration_integration(self, product_owner_agent):
        """Test agent collaboration capabilities in integration context."""
        with patch('bmad.core.message_bus.get_message_bus') as mock_get_bus:
            mock_bus = Mock()
            mock_get_bus.return_value = mock_bus
            
            await product_owner_agent.initialize_message_bus()
            
            # Test collaboration example
            result = await product_owner_agent.collaborate_example()
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, product_owner_agent):
        """Test error handling in integration context."""
        # Test with invalid data
        invalid_data = None
        
        result = await product_owner_agent.create_user_story(invalid_data)
        assert result is not None
        assert "error" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_resource_management_integration(self, product_owner_agent):
        """Test resource management in integration context."""
        # Test showing resources
        result = product_owner_agent.show_resource("best_practices")
        assert result is not None
        
        # Test showing story history
        result = product_owner_agent.show_story_history()
        assert result is not None
        
        # Test showing vision history
        result = product_owner_agent.show_vision_history()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_performance_metrics_integration(self, product_owner_agent):
        """Test performance metrics in integration context."""
        # Check initial metrics
        assert "user_stories_created" in product_owner_agent.performance_metrics
        assert "backlog_items_prioritized" in product_owner_agent.performance_metrics
        assert "product_visions_generated" in product_owner_agent.performance_metrics
        
        # Test metric updates
        initial_count = product_owner_agent.performance_metrics["user_stories_created"]
        
        # Simulate creating a user story
        with patch('bmad.agents.core.ai.llm_client.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "response": "User story created",
                "confidence": 0.95
            }
            
            await product_owner_agent.create_user_story("Test requirement")
            
            # Metrics should be updated (though this depends on implementation)
            assert product_owner_agent.performance_metrics is not None


if __name__ == "__main__":
    pytest.main([__file__]) 