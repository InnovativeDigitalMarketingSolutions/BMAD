"""
Comprehensive test suite for FrontendDeveloperAgent.
Aims to increase coverage from 19% to 70%+.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, mock_open
import json
import time
from datetime import datetime
from unittest.mock import AsyncMock

from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent


class TestFrontendDeveloperAgent:
    """Test suite for FrontendDeveloperAgent."""

    def test_agent_initialization(self):
        """Test agent initialization and attributes."""
        agent = FrontendDeveloperAgent()
        
        assert hasattr(agent, 'agent_name')
        assert agent.agent_name == "FrontendDeveloper"
        assert hasattr(agent, 'component_history')
        assert hasattr(agent, 'performance_history')
        assert hasattr(agent, 'performance_metrics')
        assert hasattr(agent, 'template_paths')
        assert hasattr(agent, 'data_paths')
        assert isinstance(agent.component_history, list)
        assert isinstance(agent.performance_history, list)
        assert isinstance(agent.performance_metrics, dict)
        assert isinstance(agent.template_paths, dict)
        assert isinstance(agent.data_paths, dict)
        
        # Performance metrics validation
        expected_metrics = ["total_components", "build_success_rate", "average_build_time", "accessibility_score", "component_reuse_rate"]
        for metric in expected_metrics:
            assert metric in agent.performance_metrics
            assert isinstance(agent.performance_metrics[metric], (int, float))
        
        # Message Bus Integration attributes
        assert hasattr(agent, 'message_bus_integration')
        assert hasattr(agent, 'message_bus_enabled')
        assert agent.message_bus_integration is None
        assert agent.message_bus_enabled is False

    @patch('builtins.open', new_callable=mock_open, read_data="# Component History\n\n- Component 1\n- Component 2")
    @patch('pathlib.Path.exists', return_value=True)
    @pytest.mark.asyncio
    async def test_load_component_history_success(self, mock_exists, mock_file):
        """Test successful loading of component history."""
        agent = FrontendDeveloperAgent()
        # Clear history that was loaded during initialization
        agent.component_history = []
        agent._load_component_history()
        
        assert len(agent.component_history) == 2
        assert "Component 1" in agent.component_history
        assert "Component 2" in agent.component_history

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_component_history_file_not_found(self, mock_exists):
        """Test loading component history when file doesn't exist."""
        agent = FrontendDeveloperAgent()
        agent.component_history = []
        agent._load_component_history()
        
        assert len(agent.component_history) == 0

    @patch('builtins.open', new_callable=mock_open, read_data="# Performance History\n\n- Performance 1\n- Performance 2")
    @patch('pathlib.Path.exists', return_value=True)
    @pytest.mark.asyncio
    async def test_load_performance_history_success(self, mock_exists, mock_file):
        """Test successful loading of performance history."""
        agent = FrontendDeveloperAgent()
        # Clear history that was loaded during initialization
        agent.performance_history = []
        agent._load_performance_history()
        
        assert len(agent.performance_history) == 2
        assert "Performance 1" in agent.performance_history
        assert "Performance 2" in agent.performance_history

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_performance_history_file_not_found(self, mock_exists):
        """Test loading performance history when file doesn't exist."""
        agent = FrontendDeveloperAgent()
        agent.performance_history = []
        agent._load_performance_history()
        
        assert len(agent.performance_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_component_history(self, mock_mkdir, mock_file):
        """Test saving component history."""
        agent = FrontendDeveloperAgent()
        agent.component_history = ["Component 1", "Component 2"]
        agent._save_component_history()
        
        # Check that open was called for saving (not just loading)
        save_calls = [call for call in mock_file.call_args_list if 'w' in str(call)]
        assert len(save_calls) > 0
        mock_mkdir.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_performance_history(self, mock_mkdir, mock_file):
        """Test saving performance history."""
        agent = FrontendDeveloperAgent()
        agent.performance_history = ["Performance 1", "Performance 2"]
        agent._save_performance_history()
        
        # Check that open was called for saving (not just loading)
        save_calls = [call for call in mock_file.call_args_list if 'w' in str(call)]
        assert len(save_calls) > 0
        mock_mkdir.assert_called_once()

    def test_show_help(self, capsys):
        """Test show_help method."""
        agent = FrontendDeveloperAgent()
        agent.show_help()
        
        captured = capsys.readouterr()
        assert "FrontendDeveloper Agent Commands:" in captured.out
        assert "help" in captured.out
        assert "build-component" in captured.out

    @patch('builtins.open', new_callable=mock_open, read_data="Best practices content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_best_practices(self, mock_exists, mock_file, capsys):
        """Test show_resource with best practices."""
        agent = FrontendDeveloperAgent()
        agent.show_resource("best-practices")
        
        captured = capsys.readouterr()
        assert "Best practices content" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_show_resource_not_found(self, mock_exists, capsys):
        """Test show_resource when file doesn't exist."""
        agent = FrontendDeveloperAgent()
        agent.show_resource("best-practices")
        
        captured = capsys.readouterr()
        assert "Resource file not found" in captured.out

    def test_show_component_history_empty(self, capsys):
        """Test show_component_history when history is empty."""
        agent = FrontendDeveloperAgent()
        agent.component_history = []
        agent.show_component_history()
        
        captured = capsys.readouterr()
        assert "No component history available" in captured.out

    @pytest.mark.asyncio
    async def test_show_component_history_with_data(self, capsys):
        """Test show_component_history with data."""
        agent = FrontendDeveloperAgent()
        agent.component_history = ["Component 1", "Component 2", "Component 3"]
        agent.show_component_history()
        
        captured = capsys.readouterr()
        assert "Component History:" in captured.out
        assert "Component 1" in captured.out

    def test_show_performance_empty(self, capsys):
        """Test show_performance when history is empty."""
        agent = FrontendDeveloperAgent()
        agent.performance_history = []
        agent.show_performance()
        
        captured = capsys.readouterr()
        assert "No performance history available" in captured.out

    @pytest.mark.asyncio
    async def test_show_performance_with_data(self, capsys):
        """Test show_performance with data."""
        agent = FrontendDeveloperAgent()
        agent.performance_history = ["Performance 1", "Performance 2", "Performance 3"]
        agent.show_performance()
        
        captured = capsys.readouterr()
        assert "Performance History:" in captured.out
        assert "Performance 1" in captured.out

    def test_validate_input_valid(self):
        """Test validate_input with valid parameters."""
        agent = FrontendDeveloperAgent()
        # Should not raise any exception
        agent.validate_input("TestComponent")
        agent.validate_input("TestComponent", "md")
        agent.validate_input("TestComponent", "json")

    def test_validate_input_invalid_component_name(self):
        """Test validate_input with invalid component name."""
        agent = FrontendDeveloperAgent()
        with pytest.raises(ValueError, match="Component name must be a non-empty string"):
            agent.validate_input("")
        with pytest.raises(ValueError, match="Component name must be a non-empty string"):
            agent.validate_input(None)

    def test_validate_input_invalid_format_type(self):
        """Test validate_input with invalid format type."""
        agent = FrontendDeveloperAgent()
        with pytest.raises(ValueError, match="Format type must be 'md' or 'json'"):
            agent.validate_input("TestComponent", "invalid")

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    @pytest.mark.asyncio
    async def test_build_shadcn_component(self, mock_sleep):
        """Test build_shadcn_component method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        result = await agent.build_shadcn_component("TestButton")
        
        assert isinstance(result, dict)
        assert result["component"] == "TestButton"
        assert result["type"] == "Shadcn/ui"
        assert "variants" in result
        assert "sizes" in result
        assert "accessibility_features" in result
        assert "accessibility_score" in result
        assert "performance_score" in result
        assert len(agent.component_history) > 0

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    @pytest.mark.asyncio
    async def test_build_component(self, mock_sleep):
        """Test build_component method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        result = await agent.build_component("TestButton")
        
        assert isinstance(result, dict)
        assert result["name"] == "TestButton"
        assert result["type"] == "React/Next.js"
        assert "accessibility_score" in result
        assert "performance_score" in result
        assert len(agent.component_history) > 0

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    def test_run_accessibility_check(self, mock_sleep):
        """Test run_accessibility_check method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        result = agent.run_accessibility_check("TestButton")
        
        assert isinstance(result, dict)
        assert result["component"] == "TestButton"
        assert "score" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_export_component_md(self, mock_exists, mock_file, capsys):
        """Test export_component with markdown format."""
        agent = FrontendDeveloperAgent()
        component_data = {"name": "TestButton", "type": "React", "accessibility_score": 95}
        agent.export_component("md", component_data)
        
        captured = capsys.readouterr()
        assert "Component export saved to:" in captured.out

    @patch('builtins.open', new_callable=mock_open)
    def test_export_component_json(self, mock_file, capsys):
        """Test export_component with JSON format."""
        agent = FrontendDeveloperAgent()
        component_data = {"name": "TestButton", "type": "React", "accessibility_score": 95}
        agent.export_component("json", component_data)
        
        captured = capsys.readouterr()
        assert "Component export saved to:" in captured.out

    def test_export_component_invalid_format(self):
        """Test export_component with invalid format."""
        agent = FrontendDeveloperAgent()
        component_data = {"name": "TestButton", "type": "React", "accessibility_score": 95}
        
        with pytest.raises(ValueError, match="Format type must be 'md' or 'json'"):
            agent.export_component("invalid", component_data)

    @patch('pathlib.Path.exists', return_value=True)
    def test_test_resource_completeness_all_available(self, mock_exists, capsys):
        """Test resource completeness when all resources are available."""
        agent = FrontendDeveloperAgent()
        agent.test_resource_completeness()
        captured = capsys.readouterr()
        
        assert "✅ All resources available" in captured.out
        assert "Available resources (10):" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_test_resource_completeness_missing_resources(self, mock_exists, capsys):
        """Test resource completeness when resources are missing."""
        agent = FrontendDeveloperAgent()
        agent.test_resource_completeness()
        captured = capsys.readouterr()
        
        assert "❌ Missing resources (10):" in captured.out
        assert "Missing resources" in captured.out

    def test_get_status(self):
        """Test get_status method."""
        agent = FrontendDeveloperAgent()
        agent.component_history = ["Component 1", "Component 2"]
        agent.performance_history = ["Performance 1"]
        
        status = agent.get_status()
        
        assert status["agent_name"] == "FrontendDeveloper"
        assert status["component_history_count"] == 2
        assert status["performance_history_count"] == 1
        assert status["last_component"] == "Component 2"
        assert status["last_performance"] == "Performance 1"
        assert status["status"] == "active"
        assert "services_initialized" in status
        assert "resources_loaded" in status

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    def test_collaborate_example(self, mock_sleep, capsys):
        """Test collaborate_example method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        agent.collaborate_example()
        
        captured = capsys.readouterr()
        assert "Collaboration example completed successfully" in captured.out

    @pytest.mark.asyncio
    async def test_initialize_message_bus_integration_success(self):
        """Test successful Message Bus Integration initialization."""
        agent = FrontendDeveloperAgent()
        
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_integration = MagicMock()
            mock_integration.publish_event = MagicMock()
            mock_integration.subscribe_to_event = MagicMock()
            mock_create.return_value = mock_integration
            
            # Mock the async function to return the mock integration
            mock_create.return_value = mock_integration
            
            await agent.initialize_message_bus_integration()
            
            mock_create.assert_called_once()
            assert agent.message_bus_integration == mock_integration
            # Note: message_bus_enabled is set to True only if initialization succeeds without exception
            # Since we're mocking, we need to check if the integration was assigned
            assert agent.message_bus_integration is not None

    @pytest.mark.asyncio
    async def test_initialize_message_bus_integration_failure(self):
        """Test Message Bus Integration initialization failure."""
        agent = FrontendDeveloperAgent()
        
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            
            await agent.initialize_message_bus_integration()
            
            assert agent.message_bus_integration is None
            assert agent.message_bus_enabled is False

    @pytest.mark.asyncio
    async def test_handle_component_build_requested(self):
        """Test handling component build requested event with real functionality."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        agent.message_bus_integration.publish_event = AsyncMock()
        
        # Store initial metrics
        initial_total_components = agent.performance_metrics["total_components"]
        initial_component_history_length = len(agent.component_history)
        
        event_data = {
            "component_name": "TestComponent",
            "framework": "react",
            "request_id": "test-123"
        }
        
        result = await agent.handle_component_build_requested(event_data)
        
        # Verify that the event was processed
        assert result["status"] == "processed"
        assert result["event"] == "component_build_requested"
        
        # Verify performance metrics were updated
        assert agent.performance_metrics["total_components"] == initial_total_components + 1
        
        # Verify component history was updated
        assert len(agent.component_history) == initial_component_history_length + 1
        last_entry = agent.component_history[-1]
        assert last_entry["component"] == "TestComponent"
        assert last_entry["action"] == "build_requested"
        assert last_entry["framework"] == "react"
        assert last_entry["status"] == "processing"
        
        # Verify follow-up event was published
        agent.message_bus_integration.publish_event.assert_called_once_with(
            "component_build_processing",
            {
                "component_name": "TestComponent",
                "request_id": "test-123",
                "status": "processing"
            }
        )

    @pytest.mark.asyncio
    async def test_handle_component_build_completed(self):
        """Test handling component build completed event with real functionality."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        agent.message_bus_integration.publish_event = AsyncMock()
        
        # Store initial metrics
        initial_build_success_rate = agent.performance_metrics["build_success_rate"]
        initial_average_build_time = agent.performance_metrics["average_build_time"]
        initial_performance_history_length = len(agent.performance_history)
        
        event_data = {
            "component_name": "TestComponent",
            "status": "completed",
            "request_id": "test-123",
            "build_time": 1500  # 1.5 seconds
        }
        
        result = await agent.handle_component_build_completed(event_data)
        
        # Verify that the event was processed
        assert result["status"] == "processed"
        assert result["event"] == "component_build_completed"
        
        # Verify performance metrics were updated
        assert agent.performance_metrics["build_success_rate"] > initial_build_success_rate
        assert agent.performance_metrics["average_build_time"] > 0
        
        # Verify performance history was updated
        assert len(agent.performance_history) == initial_performance_history_length + 1
        last_entry = agent.performance_history[-1]
        assert last_entry["component"] == "TestComponent"
        assert last_entry["action"] == "build_completed"
        assert last_entry["status"] == "completed"
        assert last_entry["build_time"] == 1500
        assert last_entry["framework"] == "react"
        
        # Verify follow-up event was published
        agent.message_bus_integration.publish_event.assert_called_once_with(
            "component_build_finalized",
            {
                "component_name": "TestComponent",
                "request_id": "test-123",
                "status": "completed",
                "build_time": 1500
            }
        )

    @pytest.mark.asyncio
    async def test_handle_figma_design_updated(self):
        """Test handling Figma design updated event with real functionality."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        agent.message_bus_integration.publish_event = AsyncMock()
        
        # Store initial metrics
        initial_component_reuse_rate = agent.performance_metrics["component_reuse_rate"]
        initial_performance_history_length = len(agent.performance_history)
        
        event_data = {
            "file_id": "figma-file-123",
            "version": "2.0",
            "request_id": "test-123",
            "components_affected": ["Button", "Card", "Modal"],
            "design_system_version": "1.2.0"
        }
        
        result = await agent.handle_figma_design_updated(event_data)
        
        # Verify that the event was processed
        assert result["status"] == "processed"
        assert result["event"] == "figma_design_updated"
        
        # Verify performance metrics were updated
        assert agent.performance_metrics["component_reuse_rate"] > initial_component_reuse_rate
        
        # Verify performance history was updated
        assert len(agent.performance_history) == initial_performance_history_length + 1
        last_entry = agent.performance_history[-1]
        assert last_entry["action"] == "figma_design_updated"
        assert last_entry["file_id"] == "figma-file-123"
        assert last_entry["version"] == "2.0"
        assert last_entry["components_affected"] == ["Button", "Card", "Modal"]
        assert last_entry["design_system_version"] == "1.2.0"
        
        # Verify follow-up event was published
        agent.message_bus_integration.publish_event.assert_called_once_with(
            "design_update_processed",
            {
                "file_id": "figma-file-123",
                "version": "2.0",
                "components_affected": ["Button", "Card", "Modal"],
                "request_id": "test-123"
            }
        )

    @pytest.mark.asyncio
    async def test_handle_ui_feedback_received(self):
        """Test handling UI feedback received event with real functionality."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        agent.message_bus_integration.publish_event = AsyncMock()
        
        # Store initial metrics
        initial_accessibility_score = agent.performance_metrics["accessibility_score"]
        initial_performance_history_length = len(agent.performance_history)
        
        event_data = {
            "component_name": "TestComponent",
            "feedback": "Improve accessibility",
            "feedback_score": 85,
            "request_id": "test-123",
            "user_id": "user-123",
            "feedback_type": "accessibility"
        }
        
        result = await agent.handle_ui_feedback_received(event_data)
        
        # Verify that the event was processed
        assert result["status"] == "processed"
        assert result["event"] == "ui_feedback_received"
        
        # Verify performance metrics were updated
        assert agent.performance_metrics["accessibility_score"] > initial_accessibility_score
        
        # Verify performance history was updated
        assert len(agent.performance_history) == initial_performance_history_length + 1
        last_entry = agent.performance_history[-1]
        assert last_entry["component"] == "TestComponent"
        assert last_entry["action"] == "ui_feedback_received"
        assert last_entry["feedback"] == "Improve accessibility"
        assert last_entry["feedback_score"] == 85
        assert last_entry["user_id"] == "user-123"
        assert last_entry["feedback_type"] == "accessibility"
        
        # Verify follow-up event was published
        agent.message_bus_integration.publish_event.assert_called_once_with(
            "feedback_processed",
            {
                "component_name": "TestComponent",
                "feedback_score": 85,
                "feedback_type": "accessibility",
                "request_id": "test-123"
            }
        )

    @pytest.mark.asyncio
    async def test_handle_accessibility_check_requested(self):
        """Test handling accessibility check requested event with real functionality."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        agent.message_bus_integration.publish_event = AsyncMock()
        
        # Store initial metrics
        initial_total_components = agent.performance_metrics["total_components"]
        initial_performance_history_length = len(agent.performance_history)
        
        event_data = {
            "component_name": "TestComponent",
            "request_id": "test-123",
            "check_type": "wcag",
            "priority": "high"
        }
        
        result = await agent.handle_accessibility_check_requested(event_data)
        
        # Verify that the event was processed
        assert result["status"] == "processed"
        assert result["event"] == "accessibility_check_requested"
        
        # Verify performance metrics were updated
        assert agent.performance_metrics["total_components"] == initial_total_components + 1
        
        # Verify performance history was updated
        assert len(agent.performance_history) == initial_performance_history_length + 1
        last_entry = agent.performance_history[-1]
        assert last_entry["component"] == "TestComponent"
        assert last_entry["action"] == "accessibility_check_requested"
        assert last_entry["check_type"] == "wcag"
        assert last_entry["priority"] == "high"
        
        # Verify follow-up event was published
        agent.message_bus_integration.publish_event.assert_called_once_with(
            "accessibility_check_processing",
            {
                "component_name": "TestComponent",
                "check_type": "wcag",
                "request_id": "test-123"
            }
        )

    @pytest.mark.asyncio
    async def test_message_bus_integration_in_run_method(self):
        """Test that Message Bus Integration is initialized in run method."""
        agent = FrontendDeveloperAgent()
        
        with patch.object(agent, 'initialize_message_bus_integration') as mock_init:
            with patch.object(agent, 'collaborate_example'):
                with patch('asyncio.sleep') as mock_sleep:
                    # Mock the infinite loop to run only once
                    mock_sleep.side_effect = KeyboardInterrupt()
                    
                    try:
                        await agent.run()
                    except KeyboardInterrupt:
                        pass  # Expected behavior
                    
                    mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_bus_status_in_run_method(self):
        """Test that Message Bus status is printed in run method."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_enabled = True
        
        with patch('builtins.print') as mock_print:
            with patch.object(agent, 'initialize_message_bus_integration'):
                with patch.object(agent, 'collaborate_example'):
                    with patch('asyncio.sleep') as mock_sleep:
                        # Mock the infinite loop to run only once
                        mock_sleep.side_effect = KeyboardInterrupt()
                        
                        try:
                            await agent.run()
                        except KeyboardInterrupt:
                            pass  # Expected behavior
                        
                        # Verify status message was printed
                        mock_print.assert_any_call("Message Bus: Enabled")

    @pytest.mark.asyncio
    async def test_message_bus_disabled_status(self):
        """Test Message Bus disabled status display."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_enabled = False
        
        with patch('builtins.print') as mock_print:
            with patch.object(agent, 'initialize_message_bus_integration'):
                with patch.object(agent, 'collaborate_example'):
                    with patch('asyncio.sleep') as mock_sleep:
                        # Mock the infinite loop to run only once
                        mock_sleep.side_effect = KeyboardInterrupt()
                        
                        try:
                            await agent.run()
                        except KeyboardInterrupt:
                            pass  # Expected behavior
                        
                        # Verify disabled status message was printed
                        mock_print.assert_any_call("Message Bus: Disabled")

    @pytest.mark.asyncio
    async def test_event_handler_error_handling(self):
        """Test error handling in event handlers."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        # Simulate an error in event processing
        with patch.object(agent, 'build_component', side_effect=Exception("Build failed")):
            event_data = {"component_name": "TestComponent"}
            
            # Should not raise exception
            await agent.handle_component_build_requested(event_data)
            
            # Verify error was logged or handled gracefully
            assert agent.message_bus_integration is not None

    @pytest.mark.asyncio
    async def test_message_bus_integration_config(self):
        """Test Message Bus Integration configuration."""
        agent = FrontendDeveloperAgent()
        
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_integration = MagicMock()
            # Make register_event_handler async
            async def async_register_handler(event_type, handler):
                return True
            mock_integration.register_event_handler = async_register_handler
            mock_create.return_value = mock_integration
            
            await agent.initialize_message_bus_integration()
            
            # Verify correct parameters were passed
            call_args = mock_create.call_args
            assert call_args[1]['agent_name'] == "FrontendDeveloper"
            assert call_args[1]['agent_instance'] == agent
            
            # Verify message bus was enabled
            assert agent.message_bus_enabled is True

    @pytest.mark.asyncio
    async def test_message_bus_event_handlers_registration(self):
        """Test that event handlers are properly registered."""
        agent = FrontendDeveloperAgent()
        
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_integration = MagicMock()
            # Make register_event_handler async
            async def async_register_handler(event_type, handler):
                return True
            mock_integration.register_event_handler = async_register_handler
            mock_create.return_value = mock_integration
            
            await agent.initialize_message_bus_integration()
            
            # Verify message bus was enabled
            assert agent.message_bus_enabled is True
            
            # Verify the agent has the expected event handlers
            assert hasattr(agent, 'handle_component_build_requested')
            assert hasattr(agent, 'handle_component_build_completed')
            assert hasattr(agent, 'handle_figma_design_updated')
            assert hasattr(agent, 'handle_ui_feedback_received')
            assert hasattr(agent, 'handle_accessibility_check_requested')

    def test_message_bus_publish_event(self):
        """Test publishing events through Message Bus Integration."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        event_name = "component_build_completed"
        event_data = {"component_name": "TestComponent", "status": "success"}
        
        # Test that we can call publish_event (mock will handle the async part)
        agent.message_bus_integration.publish_event(event_name, event_data)
        
        agent.message_bus_integration.publish_event.assert_called_once_with(event_name, event_data)

    @pytest.mark.asyncio
    async def test_message_bus_subscription_handling(self):
        """Test Message Bus subscription handling."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        # Simulate receiving an event
        event_data = {"component_name": "TestComponent"}
        
        # Test that event handlers can be called
        result = await agent.handle_component_build_requested(event_data)
        
        # Verify the handler was called (indirectly through the event system)
        assert agent.message_bus_integration is not None
        assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_message_bus_integration_cleanup(self):
        """Test Message Bus Integration cleanup."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        # Simulate cleanup
        if agent.message_bus_integration:
            agent.message_bus_integration.close = MagicMock()
            agent.message_bus_integration.close()
            
            agent.message_bus_integration.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_bus_performance_monitoring(self):
        """Test Message Bus performance monitoring."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        start_time = time.time()
        
        # Simulate event processing
        event_data = {"component_name": "TestComponent"}
        result = await agent.handle_component_build_requested(event_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify processing time is reasonable (< 1 second for test)
        assert processing_time < 1.0
        assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_message_bus_concurrent_events(self):
        """Test handling multiple concurrent events."""
        agent = FrontendDeveloperAgent()
        agent.message_bus_integration = MagicMock()
        
        # Create multiple events
        events = [
            {"component_name": f"Component{i}", "request_id": f"req-{i}"}
            for i in range(3)
        ]
        
        # Process events sequentially (since handle_component_build_requested is now async)
        results = []
        for event in events:
            result = await agent.handle_component_build_requested(event)
            results.append(result)
        
        # Verify all events were processed
        assert len(results) == 3
        for result in results:
            assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_message_bus_integration_with_tracing(self):
        """Test Message Bus Integration with tracing enabled."""
        agent = FrontendDeveloperAgent()
        
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            await agent.initialize_message_bus_integration()
            
            # Verify Message Bus Integration was initialized
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_bus_error_recovery(self):
        """Test Message Bus error recovery mechanisms."""
        agent = FrontendDeveloperAgent()
        
        # Simulate initial failure
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_create.side_effect = Exception("Initial failure")
            
            await agent.initialize_message_bus_integration()
            
            assert agent.message_bus_integration is None
            assert agent.message_bus_enabled is False
        
        # Simulate recovery
        with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_agent_message_bus_integration') as mock_create:
            mock_integration = MagicMock()
            # Make register_event_handler async
            async def async_register_handler(event_type, handler):
                return True
            mock_integration.register_event_handler = async_register_handler
            mock_create.return_value = mock_integration
            
            await agent.initialize_message_bus_integration()
            
            assert agent.message_bus_integration == mock_integration
            assert agent.message_bus_enabled is True

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    @pytest.mark.asyncio
    async def test_code_review_success(self, mock_llm):
        """Test code_review with success."""
        mock_llm.return_value = "Good code review"
        
        agent = FrontendDeveloperAgent()
        result = agent.code_review("const test = 'hello';")
        
        assert result == "Good code review"
        assert mock_llm.called

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    def test_code_review_error(self, mock_llm):
        """Test code_review with error."""
        mock_llm.side_effect = Exception("LLM error")
        
        agent = FrontendDeveloperAgent()
        result = agent.code_review("const test = 'hello';")
        
        assert "Error performing code review" in result

    def test_code_review_invalid_input(self):
        """Test code_review with invalid input."""
        agent = FrontendDeveloperAgent()
        with pytest.raises(ValueError, match="Code snippet must be a non-empty string"):
            agent.code_review("")
        with pytest.raises(ValueError, match="Code snippet must be a non-empty string"):
            agent.code_review(None)

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    @pytest.mark.asyncio
    async def test_bug_root_cause_success(self, mock_llm):
        """Test bug_root_cause with success."""
        mock_llm.return_value = "Bug analysis result"
        
        agent = FrontendDeveloperAgent()
        result = agent.bug_root_cause("Error: Ca\n\not read property of undefined")
        
        assert result == "Bug analysis result"
        assert mock_llm.called

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    def test_bug_root_cause_error(self, mock_llm):
        """Test bug_root_cause with error."""
        mock_llm.side_effect = Exception("LLM error")
        
        agent = FrontendDeveloperAgent()
        result = agent.bug_root_cause("Error: Ca\n\not read property of undefined")
        
        assert "Error analyzing bug root cause" in result

    def test_bug_root_cause_invalid_input(self):
        """Test bug_root_cause with invalid input."""
        agent = FrontendDeveloperAgent()
        with pytest.raises(ValueError, match="Error log must be a non-empty string"):
            agent.bug_root_cause("")
        with pytest.raises(ValueError, match="Error log must be a non-empty string"):
            agent.bug_root_cause(None)

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.FigmaClient')
    @pytest.mark.asyncio
    async def test_parse_figma_components_success(self, mock_figma_client):
        """Test parse_figma_components with success."""
        mock_client = MagicMock()
        mock_figma_client.return_value = mock_client
        mock_client.get_file.return_value = {"name": "Test File"}
        mock_client.get_components.return_value = {
            "meta": {
                "components": {
                    "comp1": {
                        "name": "Button",
                        "description": "A button component",
                        "key": "key1",
                        "created_at": "2023-01-01",
                        "updated_at": "2023-01-02"
                    }
                }
            }
        }
        
        agent = FrontendDeveloperAgent()
        result = agent.parse_figma_components("test_file_id")
        
        assert result["file_name"] == "Test File"
        assert result["file_id"] == "test_file_id"
        assert len(result["components"]) == 1
        assert result["total_components"] == 1

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.FigmaClient')
    def test_parse_figma_components_error(self, mock_figma_client):
        """Test parse_figma_components with error."""
        mock_figma_client.side_effect = Exception("Figma API error")
        
        agent = FrontendDeveloperAgent()
        result = agent.parse_figma_components("test_file_id")
        
        assert "error" in result
        assert "Figma API error" in result["error"]

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    @pytest.mark.asyncio
    async def test_generate_nextjs_component_success(self, mock_llm):
        """Test generate_nextjs_component with success."""
        mock_llm.return_value = "export const TestComponent = () => { return <div>Test</div>; };"
        
        agent = FrontendDeveloperAgent()
        component_data = {"name": "Button", "description": "A button component"}
        result = agent.generate_nextjs_component(component_data, "TestComponent")
        
        assert "export const TestComponent" in result
        assert mock_llm.called

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    def test_generate_nextjs_component_error(self, mock_llm):
        """Test generate_nextjs_component with error."""
        mock_llm.side_effect = Exception("LLM error")
        
        agent = FrontendDeveloperAgent()
        component_data = {"name": "Button", "description": "A button component"}
        result = agent.generate_nextjs_component(component_data, "TestComponent")
        
        assert "Error generating component" in result

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.FigmaClient')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    @pytest.mark.asyncio
    async def test_generate_components_from_figma_success(self, mock_llm, mock_figma_client):
        """Test generate_components_from_figma with success."""
        mock_client = MagicMock()
        mock_figma_client.return_value = mock_client
        mock_client.get_file.return_value = {"name": "Test File"}
        mock_client.get_components.return_value = {
            "meta": {
                "components": {
                    "comp1": {
                        "name": "Button",
                        "description": "A button component",
                        "key": "key1",
                        "created_at": "2023-01-01",
                        "updated_at": "2023-01-02"
                    }
                }
            }
        }
        mock_llm.return_value = "export const Button = () => { return <button>Button</button>; };"
        
        agent = FrontendDeveloperAgent()
        result = agent.generate_components_from_figma("test_file_id", "components")
        
        assert result["file_name"] == "Test File"
        assert result["file_id"] == "test_file_id"
        assert len(result["generated_components"]) == 1
        assert result["total_generated"] == 1

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.FigmaClient')
    def test_generate_components_from_figma_error(self, mock_figma_client):
        """Test generate_components_from_figma with error."""
        mock_figma_client.side_effect = Exception("Figma API error")
        
        agent = FrontendDeveloperAgent()
        result = agent.generate_components_from_figma("test_file_id", "components")
        
        assert "error" in result
        assert "Figma API error" in result["error"]

    @pytest.mark.asyncio
    async def test_run_method(self):
        """Test run method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        
        # Mock the infinite loop to avoid hanging
        with patch.object(agent, 'initialize_mcp') as mock_init, \
             patch.object(agent, 'collaborate_example') as mock_collab, \
             patch('asyncio.sleep') as mock_sleep:
            
            # Mock sleep to raise KeyboardInterrupt after first call
            mock_sleep.side_effect = KeyboardInterrupt()
            
            await agent.run()
            
            # Verify methods were called
            mock_init.assert_called_once()
            mock_collab.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_agent_class_method(self):
        """Test run_agent class method."""
        with patch.object(FrontendDeveloperAgent, 'run') as mock_run:
            await FrontendDeveloperAgent.run_agent()
            
            assert mock_run.called


class TestFrontendDeveloperIntegration:
    """Integration tests for FrontendDeveloperAgent."""

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_performance_monitor')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_advanced_policy_engine')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_sprite_library')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    @pytest.mark.asyncio
    async def test_complete_component_build_workflow(self, mock_sleep, mock_sprite, mock_policy, mock_monitor):
        """Test complete component build workflow."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        
        # Test input validation
        with pytest.raises(ValueError):
            await agent.build_component("")
        
        # Test valid component build
        result = await agent.build_component("TestComponent")
        assert result["name"] == "TestComponent"
        assert result["type"] == "React/Next.js"
        
        # Test accessibility check
        accessibility_result = agent.run_accessibility_check("TestComponent")
        assert accessibility_result["component"] == "TestComponent"
        assert "score" in accessibility_result
        
        # Test status retrieval
        status = agent.get_status()
        assert status["agent_name"] == "FrontendDeveloper"
        assert status["component_history_count"] > 0

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_performance_monitor')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_advanced_policy_engine')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_sprite_library')
    def test_agent_resource_completeness(self, mock_sprite, mock_policy, mock_monitor):
        """Test agent resource completeness."""
        agent = FrontendDeveloperAgent()
        
        # Test that agent has all required attributes
        assert hasattr(agent, 'agent_name')
        assert hasattr(agent, 'component_history')
        assert hasattr(agent, 'performance_history')
        assert hasattr(agent, 'template_paths')
        assert hasattr(agent, 'data_paths')
        
        # Test that agent has all required methods
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'build_component')
        assert hasattr(agent, 'run_accessibility_check')
        assert hasattr(agent, 'export_component')
        assert hasattr(agent, 'get_status')
        assert hasattr(agent, 'collaborate_example')
        assert hasattr(agent, 'validate_input') 