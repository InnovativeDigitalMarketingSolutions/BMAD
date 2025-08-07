"""
Integration tests for TestEngineerAgent.

This module contains integration tests for the TestEngineerAgent to ensure
proper functionality with enhanced MCP integration, tracing, and message bus.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bmad.agents.Agent.TestEngineer.testengineer import TestEngineerAgent


class TestTestEngineerIntegration:
    """Integration tests for TestEngineerAgent."""
    
    @pytest.fixture
    def test_engineer_agent(self):
        """Create a TestEngineerAgent instance for testing."""
        agent = TestEngineerAgent()
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_engineer_agent):
        """Test that TestEngineerAgent initializes correctly."""
        assert test_engineer_agent is not None
        assert test_engineer_agent.agent_name == "TestEngineerAgent"
        assert hasattr(test_engineer_agent, 'framework_manager')
        assert hasattr(test_engineer_agent, 'monitor')
        assert hasattr(test_engineer_agent, 'policy_engine')
        assert hasattr(test_engineer_agent, 'sprite_library')
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization(self, test_engineer_agent):
        """Test enhanced MCP initialization."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.create_enhanced_mcp_integration') as mock_create:
            mock_mcp = Mock()
            mock_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
            mock_create.return_value = mock_mcp
            
            await test_engineer_agent.initialize_enhanced_mcp()
            
            assert test_engineer_agent.enhanced_mcp_enabled is True
            assert test_engineer_agent.enhanced_mcp is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools(self, test_engineer_agent):
        """Test enhanced MCP tools functionality."""
        # Mock enhanced MCP as enabled
        test_engineer_agent.enhanced_mcp_enabled = True
        
        tools = test_engineer_agent.get_enhanced_mcp_tools()
        
        expected_tools = [
            "test_strategy_development",
            "test_case_generation",
            "test_execution_monitoring",
            "coverage_analysis",
            "test_quality_assessment",
            "test_automation_framework"
        ]
        
        assert len(tools) == len(expected_tools)
        for tool in expected_tools:
            assert tool in tools
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_registration(self, test_engineer_agent):
        """Test enhanced MCP tool registration."""
        # Mock enhanced MCP
        mock_mcp = Mock()
        mock_mcp.register_tool = Mock()
        test_engineer_agent.enhanced_mcp = mock_mcp
        test_engineer_agent.enhanced_mcp_enabled = True
        
        result = test_engineer_agent.register_enhanced_mcp_tools()
        
        assert result is True
        assert mock_mcp.register_tool.call_count == 6  # 6 tools should be registered
    
    @pytest.mark.asyncio
    async def test_tracing_initialization(self, test_engineer_agent):
        """Test tracing initialization."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer.initialize = AsyncMock()
            mock_tracer.setup_test_tracing = AsyncMock()
            mock_tracer_class.return_value = mock_tracer
            
            test_engineer_agent.tracer = mock_tracer
            
            await test_engineer_agent.initialize_tracing()
            
            assert test_engineer_agent.tracing_enabled is True
            mock_tracer.initialize.assert_called_once()
            mock_tracer.setup_test_tracing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trace_operation(self, test_engineer_agent):
        """Test operation tracing."""
        # Mock tracer
        mock_tracer = Mock()
        mock_tracer.trace_operation = AsyncMock()
        test_engineer_agent.tracer = mock_tracer
        test_engineer_agent.tracing_enabled = True
        
        operation_data = {"test": "data"}
        await test_engineer_agent.trace_operation("test_operation", operation_data)
        
        mock_tracer.trace_operation.assert_called_once_with(
            operation_name="test_operation",
            agent_name="TestEngineerAgent",
            data=operation_data
        )
    
    @pytest.mark.asyncio
    async def test_message_bus_integration(self, test_engineer_agent):
        """Test message bus integration initialization."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.create_agent_message_bus_integration') as mock_create:
            mock_integration = Mock()
            mock_integration.register_event_handler = AsyncMock()
            mock_create.return_value = mock_integration
            
            result = await test_engineer_agent.initialize_message_bus_integration()
            
            assert result is True
            assert test_engineer_agent.message_bus_enabled is True
            assert test_engineer_agent.message_bus_integration is not None
            assert mock_integration.register_event_handler.call_count == 4  # 4 event handlers
    
    @pytest.mark.asyncio
    async def test_test_generation(self, test_engineer_agent):
        """Test test generation functionality."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.ask_openai') as mock_openai:
            mock_openai.return_value = "Generated test content"
            
            result = await test_engineer_agent.generate_tests("TestComponent", "unit")
            
            assert result is not None
            assert "component_name" in result
            assert "test_type" in result
            assert "test_content" in result
            assert result["component_name"] == "TestComponent"
            assert result["test_type"] == "unit"
    
    @pytest.mark.asyncio
    async def test_test_execution(self, test_engineer_agent):
        """Test test execution functionality."""
        with patch('pytest.main') as mock_pytest:
            mock_pytest.return_value = 0  # Success
            
            result = await test_engineer_agent.run_tests()
            
            assert result is not None
            assert "status" in result
            assert "tests_run" in result
            assert "tests_passed" in result
            assert "tests_failed" in result
    
    @pytest.mark.asyncio
    async def test_resource_completeness(self, test_engineer_agent):
        """Test resource completeness check."""
        result = test_engineer_agent.test_resource_completeness()
        
        assert result is not None
        assert "templates" in result
        assert "data_files" in result
        assert "completeness" in result
    
    @pytest.mark.asyncio
    async def test_export_report(self, test_engineer_agent):
        """Test report export functionality."""
        test_data = {
            "component_name": "TestComponent",
            "test_type": "unit",
            "test_content": "Test content",
            "timestamp": "2025-01-27"
        }
        
        # Test markdown export
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            test_engineer_agent.export_report("md", test_data)
            
            mock_file.write.assert_called()
        
        # Test JSON export
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            test_engineer_agent.export_report("json", test_data)
            
            mock_file.write.assert_called()
    
    @pytest.mark.asyncio
    async def test_event_handlers(self, test_engineer_agent):
        """Test event handler functionality."""
        # Test tests_requested handler
        event = {"component": "TestComponent", "test_type": "unit"}
        result = await test_engineer_agent.handle_tests_requested(event)
        
        assert result is not None
        assert "status" in result
        
        # Test test_generation_requested handler
        result = await test_engineer_agent.handle_test_generation_requested(event)
        
        assert result is not None
        assert "status" in result
        
        # Test test_completed handler
        event = {"component": "TestComponent", "results": {"passed": 5, "failed": 0}}
        result = await test_engineer_agent.handle_test_completed(event)
        
        assert result is not None
        assert "status" in result
        
        # Test coverage_report_requested handler
        event = {"component": "TestComponent"}
        result = await test_engineer_agent.handle_coverage_report_requested(event)
        
        assert result is not None
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_agent_status(self, test_engineer_agent):
        """Test agent status functionality."""
        status = test_engineer_agent.get_status()
        
        assert status is not None
        assert "agent_name" in status
        assert "mcp_enabled" in status
        assert "enhanced_mcp_enabled" in status
        assert "tracing_enabled" in status
        assert "message_bus_enabled" in status
        assert status["agent_name"] == "TestEngineerAgent"
    
    @pytest.mark.asyncio
    async def test_help_functionality(self, test_engineer_agent):
        """Test help functionality."""
        help_text = test_engineer_agent.show_help()
        
        assert help_text is not None
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "TestEngineer" in help_text
    
    @pytest.mark.asyncio
    async def test_resource_show_functionality(self, test_engineer_agent):
        """Test resource show functionality."""
        # Test showing best practices
        content = test_engineer_agent.show_resource("best-practices")
        
        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_test_history_functionality(self, test_engineer_agent):
        """Test test history functionality."""
        history = test_engineer_agent.show_test_history()
        
        assert history is not None
        assert isinstance(history, str)
    
    @pytest.mark.asyncio
    async def test_coverage_functionality(self, test_engineer_agent):
        """Test coverage functionality."""
        coverage = test_engineer_agent.show_coverage()
        
        assert coverage is not None
        assert isinstance(coverage, str)
    
    @pytest.mark.asyncio
    async def test_collaboration_example(self, test_engineer_agent):
        """Test collaboration example functionality."""
        result = await test_engineer_agent.collaborate_example()
        
        assert result is not None
        assert "message" in result
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_required_attributes_presence(self, test_engineer_agent):
        """Test that all required attributes are present."""
        required_attributes = [
            'mcp_client',
            'enhanced_mcp',
            'enhanced_mcp_enabled',
            'tracing_enabled',
            'agent_name',
            'message_bus_integration'
        ]
        
        for attr in required_attributes:
            assert hasattr(test_engineer_agent, attr)
    
    @pytest.mark.asyncio
    async def test_required_methods_presence(self, test_engineer_agent):
        """Test that all required methods are present."""
        required_methods = [
            'initialize_enhanced_mcp',
            'get_enhanced_mcp_tools',
            'register_enhanced_mcp_tools',
            'trace_operation'
        ]
        
        for method in required_methods:
            assert hasattr(test_engineer_agent, method)
            assert callable(getattr(test_engineer_agent, method))


if __name__ == "__main__":
    pytest.main([__file__]) 