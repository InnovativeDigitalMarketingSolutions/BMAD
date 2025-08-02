import pytest
import asyncio
from unittest.mock import patch, MagicMock, mock_open
import json
import time
from datetime import datetime

from bmad.agents.Agent.TestEngineer.testengineer import TestEngineerAgent


class TestTestEngineerAgent:
    """Test suite for TestEngineerAgent."""

    def test_agent_initialization(self):
        """Test agent initialization and attributes."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            
            assert hasattr(agent, 'agent_name')
            assert agent.agent_name == "TestEngineerAgent"
            assert hasattr(agent, 'monitor')
            assert hasattr(agent, 'policy_engine')
            assert hasattr(agent, 'sprite_library')
            assert hasattr(agent, 'test_history')
            assert hasattr(agent, 'coverage_history')
            assert isinstance(agent.test_history, list)
            assert isinstance(agent.coverage_history, list)

    @patch('builtins.open', new_callable=mock_open, read_data="# Test History\n\n- Test 1\n- Test 2")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_test_history_success(self, mock_exists, mock_file):
        """Test successful loading of test history."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            # Clear history that was loaded during initialization
            agent.test_history = []
            agent._load_test_history()
            
            assert len(agent.test_history) == 2
            assert "Test 1" in agent.test_history
            assert "Test 2" in agent.test_history

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_test_history_file_not_found(self, mock_exists):
        """Test loading test history when file doesn't exist."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent._load_test_history()
            
            assert len(agent.test_history) == 0

    @patch('builtins.open', new_callable=mock_open, read_data="# Coverage History\n\n- Coverage 1\n- Coverage 2")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_coverage_history_success(self, mock_exists, mock_file):
        """Test successful loading of coverage history."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            # Clear history that was loaded during initialization
            agent.coverage_history = []
            agent._load_coverage_history()
            
            assert len(agent.coverage_history) == 2
            assert "Coverage 1" in agent.coverage_history
            assert "Coverage 2" in agent.coverage_history

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_coverage_history_file_not_found(self, mock_exists):
        """Test loading coverage history when file doesn't exist."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent._load_coverage_history()
            
            assert len(agent.coverage_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_test_history(self, mock_mkdir, mock_file):
        """Test saving test history."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_history = ["Test 1", "Test 2"]
            agent._save_test_history()
            
            # Check that open was called for saving (not just loading)
            save_calls = [call for call in mock_file.call_args_list if 'w' in str(call)]
            assert len(save_calls) > 0
            mock_mkdir.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_coverage_history(self, mock_mkdir, mock_file):
        """Test saving coverage history."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.coverage_history = ["Coverage 1", "Coverage 2"]
            agent._save_coverage_history()
            
            # Check that open was called for saving (not just loading)
            save_calls = [call for call in mock_file.call_args_list if 'w' in str(call)]
            assert len(save_calls) > 0
            mock_mkdir.assert_called_once()

    def test_show_help(self, capsys):
        """Test show_help method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.show_help()
            
            captured = capsys.readouterr()
            assert "TestEngineer Agent Commands:" in captured.out
            assert "help" in captured.out
            assert "run-tests" in captured.out

    @patch('builtins.open', new_callable=mock_open, read_data="Best practices content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_best_practices(self, mock_exists, mock_file, capsys):
        """Test show_resource with best practices."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.show_resource("best-practices")
            
            captured = capsys.readouterr()
            assert "Best practices content" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_show_resource_not_found(self, mock_exists, capsys):
        """Test show_resource when file doesn't exist."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.show_resource("best-practices")
            
            captured = capsys.readouterr()
            assert "Resource file not found" in captured.out

    def test_show_test_history_empty(self, capsys):
        """Test show_test_history when history is empty."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_history = []
            agent.show_test_history()
            
            captured = capsys.readouterr()
            assert "No test history available" in captured.out

    def test_show_test_history_with_data(self, capsys):
        """Test show_test_history with data."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_history = ["Test 1", "Test 2", "Test 3"]
            agent.show_test_history()
            
            captured = capsys.readouterr()
            assert "Test History:" in captured.out
            assert "Test 1" in captured.out

    def test_show_coverage_empty(self, capsys):
        """Test show_coverage when history is empty."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.coverage_history = []
            agent.show_coverage()
            
            captured = capsys.readouterr()
            assert "No coverage history available" in captured.out

    def test_show_coverage_with_data(self, capsys):
        """Test show_coverage with data."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.coverage_history = ["Coverage 1", "Coverage 2", "Coverage 3"]
            agent.show_coverage()
            
            captured = capsys.readouterr()
            assert "Coverage History:" in captured.out
            assert "Coverage 1" in captured.out

    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    @pytest.mark.asyncio
    async def test_run_tests(self, mock_sleep):
        """Test run_tests method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = await agent.run_tests()
            
            assert isinstance(result, dict)
            assert "redis_cache" in result
            assert "monitoring" in result
            assert "connection_pool" in result
            assert "llm_caching" in result
            assert len(agent.test_history) > 0

    def test_validate_input_valid(self):
        """Test validate_input with valid parameters."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            # Should not raise any exception
            agent.validate_input("TestComponent", "unit")

    def test_validate_input_invalid_component_name(self):
        """Test validate_input with invalid component name."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            with pytest.raises(ValueError, match="Component name must be a non-empty string"):
                agent.validate_input("", "unit")

    def test_validate_input_invalid_test_type(self):
        """Test validate_input with invalid test type."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            with pytest.raises(ValueError, match="Test type must be unit, integration, or e2e"):
                agent.validate_input("TestComponent", "invalid")

    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    @pytest.mark.asyncio
    async def test_generate_tests_unit(self, mock_sleep):
        """Test generate_tests for unit tests."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = await agent.generate_tests("TestComponent", "unit")
            
            assert result["success"] is True
            assert result["component_name"] == "TestComponent"
            assert result["test_type"] == "unit"
            assert "generation_time" in result
            assert "test_result" in result

    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    @pytest.mark.asyncio
    async def test_generate_tests_integration(self, mock_sleep):
        """Test generate_tests for integration tests."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = await agent.generate_tests("TestComponent", "integration")
            
            assert result["success"] is True
            assert result["component_name"] == "TestComponent"
            assert result["test_type"] == "integration"

    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    @pytest.mark.asyncio
    async def test_generate_tests_e2e(self, mock_sleep):
        """Test generate_tests for e2e tests."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = await agent.generate_tests("TestComponent", "e2e")
            
            assert result["success"] is True
            assert result["component_name"] == "TestComponent"
            assert result["test_type"] == "e2e"

    def test_generate_unit_test(self):
        """Test _generate_unit_test method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = agent._generate_unit_test("TestComponent")
            
            assert "import pytest" in result
            assert "TestComponent" in result
            assert "test_testcomponent_creation" in result

    def test_generate_integration_test(self):
        """Test _generate_integration_test method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = agent._generate_integration_test("TestComponent")
            
            assert "import pytest" in result
            assert "TestComponent" in result
            assert "test_testcomponent_integration" in result

    def test_generate_e2e_test(self):
        """Test _generate_e2e_test method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            result = agent._generate_e2e_test("TestComponent")
            
            assert "import pytest" in result
            assert "selenium" in result
            assert "TestComponent" in result
            assert "test_testcomponent_e2e" in result

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_export_report_md(self, mock_exists, mock_file, capsys):
        """Test export_report with markdown format."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            test_data = {"test1": "✅ Pass", "test2": "❌ Fail"}
            agent.export_report("md", test_data)
            
            captured = capsys.readouterr()
            assert "Test report exported to:" in captured.out

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_json(self, mock_file, capsys):
        """Test export_report with JSON format."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            test_data = {"test1": "✅ Pass", "test2": "❌ Fail"}
            agent.export_report("json", test_data)
            
            captured = capsys.readouterr()
            assert "Test report exported to:" in captured.out

    def test_export_report_invalid_format(self):
        """Test export_report with invalid format."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            test_data = {"test1": "✅ Pass"}
            
            with pytest.raises(ValueError, match="Format type must be 'md' or 'json'"):
                agent.export_report("invalid", test_data)

    @patch('pathlib.Path.exists', return_value=True)
    def test_test_resource_completeness_all_available(self, mock_exists, capsys):
        """Test test_resource_completeness when all resources are available."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_resource_completeness()
            
            captured = capsys.readouterr()
            assert "All resources are available!" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_test_resource_completeness_missing_resources(self, mock_exists, capsys):
        """Test test_resource_completeness when resources are missing."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_resource_completeness()
            
            captured = capsys.readouterr()
            assert "Missing resources:" in captured.out

    def test_get_status(self):
        """Test get_status method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.test_history = ["Test 1", "Test 2"]
            agent.coverage_history = ["Coverage 1"]
            
            status = agent.get_status()
            
            assert status["agent_name"] == "TestEngineerAgent"
            assert status["test_history_count"] == 2
            assert status["coverage_history_count"] == 1
            assert status["last_test"] == "Test 2"
            assert status["last_coverage"] == "Coverage 1"
            assert status["status"] == "active"

    @patch('bmad.agents.Agent.TestEngineer.testengineer.publish')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.send_slack_message')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    def test_collaborate_example(self, mock_sleep, mock_slack, mock_publish, capsys):
        """Test collaborate_example method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            agent.collaborate_example()
            
            captured = capsys.readouterr()
            assert "Collaboration example completed successfully." in captured.out
            assert mock_publish.call_count == 2
            assert mock_slack.called

    @patch('bmad.agents.Agent.TestEngineer.testengineer.publish')
    @pytest.mark.asyncio
    async def test_handle_tests_requested(self, mock_publish):
        """Test handle_tests_requested method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep'):

            agent = TestEngineerAgent()
            event = {"test_type": "unit"}
            await agent.handle_tests_requested(event)

            assert mock_publish.called

    @patch('bmad.agents.Agent.TestEngineer.testengineer.ask_openai')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.send_slack_message')
    def test_handle_test_generation_requested_success(self, mock_slack, mock_llm):
        """Test handle_test_generation_requested with success."""
        mock_llm.return_value = "Generated test code"
        
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            event = {
                "function_description": "def add(a, b): return a + b",
                "context": "Simple addition function"
            }
            
            result = asyncio.run(agent.handle_test_generation_requested(event))
            
            assert result == "Generated test code"
            assert mock_llm.called
            assert mock_slack.called

    @patch('bmad.agents.Agent.TestEngineer.testengineer.ask_openai')
    def test_handle_test_generation_requested_error(self, mock_llm):
        """Test handle_test_generation_requested with error."""
        mock_llm.side_effect = Exception("LLM error")
        
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'):
            
            agent = TestEngineerAgent()
            event = {
                "function_description": "def add(a, b): return a + b",
                "context": "Simple addition function"
            }
            
            result = asyncio.run(agent.handle_test_generation_requested(event))
            
            assert "Error generating tests" in result

    @patch('bmad.agents.Agent.TestEngineer.testengineer.subscribe')
    @pytest.mark.asyncio
    async def test_run_method(self, mock_subscribe):
        """Test run method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.asyncio.sleep') as mock_sleep:

            mock_sleep.side_effect = KeyboardInterrupt()

            agent = TestEngineerAgent()
            await agent.run()

            assert mock_subscribe.call_count == 2

    @pytest.mark.asyncio
    async def test_run_agent_class_method(self):
        """Test run_agent class method."""
        with patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library'), \
             patch.object(TestEngineerAgent, 'run') as mock_run:

            await TestEngineerAgent.run_agent()

            assert mock_run.called


class TestTestEngineerIntegration:
    """Integration tests for TestEngineerAgent."""

    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.time.sleep')
    @pytest.mark.asyncio
    async def test_complete_test_generation_workflow(self, mock_sleep, mock_sprite, mock_policy, mock_monitor):
        """Test complete test generation workflow."""
        agent = TestEngineerAgent()

        # Test input validation - the agent logs the error but doesn't re-raise it
        result = await agent.generate_tests("", "unit")
        assert result["success"] is False
        assert "Component name must be a non-empty string" in result["error"]
        
        # Test valid test generation
        result = await agent.generate_tests("TestComponent", "unit")
        assert result["success"] is True
        assert result["component_name"] == "TestComponent"
        
        # Test status retrieval
        status = agent.get_status()
        assert status["agent_name"] == "TestEngineerAgent"
        assert status["test_history_count"] > 0

    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_performance_monitor')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_advanced_policy_engine')
    @patch('bmad.agents.Agent.TestEngineer.testengineer.get_sprite_library')
    def test_agent_resource_completeness(self, mock_sprite, mock_policy, mock_monitor):
        """Test agent resource completeness."""
        agent = TestEngineerAgent()
        
        # Test that agent has all required attributes
        assert hasattr(agent, 'agent_name')
        assert hasattr(agent, 'monitor')
        assert hasattr(agent, 'policy_engine')
        assert hasattr(agent, 'sprite_library')
        assert hasattr(agent, 'test_history')
        assert hasattr(agent, 'coverage_history')
        
        # Test that agent has all required methods
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'run_tests')
        assert hasattr(agent, 'generate_tests')
        assert hasattr(agent, 'export_report')
        assert hasattr(agent, 'get_status')
        assert hasattr(agent, 'collaborate_example')
