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
        assert hasattr(agent, 'template_paths')
        assert hasattr(agent, 'data_paths')
        assert isinstance(agent.component_history, list)
        assert isinstance(agent.performance_history, list)
        assert isinstance(agent.template_paths, dict)
        assert isinstance(agent.data_paths, dict)

    @patch('builtins.open', new_callable=mock_open, read_data="# Component History\n\n- Component 1\n- Component 2")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_component_history_success(self, mock_exists, mock_file):
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
    def test_load_performance_history_success(self, mock_exists, mock_file):
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

    def test_show_component_history_with_data(self, capsys):
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

    def test_show_performance_with_data(self, capsys):
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
    def test_build_shadcn_component(self, mock_sleep):
        """Test build_shadcn_component method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        result = agent.build_shadcn_component("TestButton")
        
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
    def test_build_component(self, mock_sleep):
        """Test build_component method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        result = agent.build_component("TestButton")
        
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
        """Test test_resource_completeness when all resources are available."""
        agent = FrontendDeveloperAgent()
        agent.test_resource_completeness()
        
        captured = capsys.readouterr()
        assert "All resources are available!" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_test_resource_completeness_missing_resources(self, mock_exists, capsys):
        """Test test_resource_completeness when resources are missing."""
        agent = FrontendDeveloperAgent()
        agent.test_resource_completeness()
        
        captured = capsys.readouterr()
        assert "Missing resources:" in captured.out

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
        assert "Collaboration example completed successfully." in captured.out

    def test_handle_component_build_requested(self):
        """Test handle_component_build_requested method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        event = {"component_name": "TestButton"}
        agent.handle_component_build_requested(event)
        
        # Should call build_component
        assert len(agent.component_history) > 0

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    def test_code_review_success(self, mock_llm):
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
    def test_bug_root_cause_success(self, mock_llm):
        """Test bug_root_cause with success."""
        mock_llm.return_value = "Bug analysis result"
        
        agent = FrontendDeveloperAgent()
        result = agent.bug_root_cause("Error: Cannot read property of undefined")
        
        assert result == "Bug analysis result"
        assert mock_llm.called

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.ask_openai')
    def test_bug_root_cause_error(self, mock_llm):
        """Test bug_root_cause with error."""
        mock_llm.side_effect = Exception("LLM error")
        
        agent = FrontendDeveloperAgent()
        result = agent.bug_root_cause("Error: Cannot read property of undefined")
        
        assert "Error analyzing bug root cause" in result

    def test_bug_root_cause_invalid_input(self):
        """Test bug_root_cause with invalid input."""
        agent = FrontendDeveloperAgent()
        with pytest.raises(ValueError, match="Error log must be a non-empty string"):
            agent.bug_root_cause("")
        with pytest.raises(ValueError, match="Error log must be a non-empty string"):
            agent.bug_root_cause(None)

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.FigmaClient')
    def test_parse_figma_components_success(self, mock_figma_client):
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
    def test_generate_nextjs_component_success(self, mock_llm):
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
    def test_generate_components_from_figma_success(self, mock_llm, mock_figma_client):
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

    def test_run_method(self):
        """Test run method."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        agent.run()
        
        # Just check that it doesn't raise an error
        assert True

    def test_run_agent_class_method(self):
        """Test run_agent class method."""
        with patch.object(FrontendDeveloperAgent, 'run') as mock_run:
            FrontendDeveloperAgent.run_agent()
            
            assert mock_run.called


class TestFrontendDeveloperIntegration:
    """Integration tests for FrontendDeveloperAgent."""

    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_performance_monitor')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_advanced_policy_engine')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_sprite_library')
    @patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.time.sleep')
    def test_complete_component_build_workflow(self, mock_sleep, mock_sprite, mock_policy, mock_monitor):
        """Test complete component build workflow."""
        agent = FrontendDeveloperAgent()
        # Initialize services to avoid monitor error
        agent._ensure_services_initialized()
        
        # Test input validation
        with pytest.raises(ValueError):
            agent.build_component("")
        
        # Test valid component build
        result = agent.build_component("TestComponent")
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