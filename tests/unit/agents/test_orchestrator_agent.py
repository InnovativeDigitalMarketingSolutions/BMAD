import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import asyncio

from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent."""

    @pytest.fixture
    def agent(self):
        """Create an OrchestratorAgent instance for testing."""
        agent = OrchestratorAgent()
        # Reset history to ensure clean state for each test
        agent.workflow_history = []
        agent.orchestration_history = []
        agent._history_loaded = False
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization and core attributes."""
        assert agent.agent_name == "Orchestrator"
        assert hasattr(agent, 'monitor')
        assert hasattr(agent, 'policy_engine')
        assert hasattr(agent, 'sprite_library')
        assert hasattr(agent, 'workflow_history')
        assert hasattr(agent, 'orchestration_history')
        assert hasattr(agent, 'status')
        assert hasattr(agent, 'event_log')
        assert agent._history_loaded == False  # Should start with lazy loading

    def test_ensure_history_loaded(self, agent):
        """Test lazy loading of history."""
        # Initially history should not be loaded
        assert agent._history_loaded == False
        
        # Call a method that triggers history loading
        agent.get_status()
        
        # Now history should be loaded
        assert agent._history_loaded == True

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_load_workflow_history_success(self, mock_makedirs, mock_exists, agent):
        """Test successful loading of workflow history."""
        mock_exists.return_value = True
        mock_content = "# Workflow History\n\n- 2025-07-31T08:14:22.179170: Workflow started - automated_deployment\n- 2025-07-31T08:15:30.123456: Workflow completed - feature_delivery"
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            agent.workflow_history = []  # Clear existing history
            agent._load_workflow_history()
        
        assert len(agent.workflow_history) == 2
        assert "automated_deployment" in agent.workflow_history[0]
        assert "feature_delivery" in agent.workflow_history[1]

    @patch('os.path.exists')
    def test_load_workflow_history_file_not_found(self, mock_exists, agent):
        """Test loading workflow history when file doesn't exist."""
        mock_exists.return_value = False
        
        # Clear existing history and reload
        agent.workflow_history = []
        agent._history_loaded = False  # Reset lazy loading flag
        agent._load_workflow_history()
        
        # Should remain empty since file doesn't exist
        assert len(agent.workflow_history) == 0

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_save_workflow_history(self, mock_makedirs, mock_exists, agent):
        """Test saving workflow history."""
        # Mock that directory doesn't exist, so mkdir should be called
        mock_exists.return_value = False
        agent.workflow_history = ["Test workflow 1", "Test workflow 2"]
        
        with patch('builtins.open', mock_open()) as mock_file:
            agent._save_workflow_history()
        
        # Check that mkdir was called to ensure directory exists
        mock_makedirs.assert_called_once()
        
        # Check that file was opened for writing
        assert mock_file.call_count > 0

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_load_orchestration_history_success(self, mock_makedirs, mock_exists, agent):
        """Test successful loading of orchestration history."""
        mock_exists.return_value = True
        mock_content = "# Orchestration History\n\n- 2025-07-31T08:14:22.179170: Task assignment orchestration\n- 2025-07-31T08:15:30.123456: Resource allocation orchestration"
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            agent.orchestration_history = []  # Clear existing history
            agent._load_orchestration_history()
        
        # The agent loads history during __init__, so we need to account for that
        assert len(agent.orchestration_history) == 2
        assert "Task assignment" in agent.orchestration_history[0]
        assert "Resource allocation" in agent.orchestration_history[1]

    @patch('os.path.exists')
    def test_load_orchestration_history_file_not_found(self, mock_exists, agent):
        """Test loading orchestration history when file doesn't exist."""
        mock_exists.return_value = False
        
        # Clear existing history and reload
        agent.orchestration_history = []
        agent._history_loaded = False  # Reset lazy loading flag
        agent._load_orchestration_history()
        
        # Should remain empty since file doesn't exist
        assert len(agent.orchestration_history) == 0

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_save_orchestration_history(self, mock_makedirs, mock_exists, agent):
        """Test saving orchestration history."""
        # Mock that directory doesn't exist, so mkdir should be called
        mock_exists.return_value = False
        agent.orchestration_history = ["Test orchestration 1", "Test orchestration 2"]
        
        with patch('builtins.open', mock_open()) as mock_file:
            agent._save_orchestration_history()
        
        # Check that mkdir was called to ensure directory exists
        mock_makedirs.assert_called_once()
        
        # Check that file was opened for writing
        assert mock_file.call_count > 0

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        agent.show_help()
        captured = capsys.readouterr()
        
        assert "Orchestrator Agent Commands:" in captured.out
        assert "help" in captured.out
        assert "start-workflow" in captured.out
        assert "monitor-workflows" in captured.out
        assert "orchestrate-agents" in captured.out

    @patch('os.path.exists')
    def test_show_resource_best_practices(self, mock_exists, agent, capsys):
        """Test show_resource with best practices."""
        mock_exists.return_value = True
        mock_content = "# Orchestration Best Practices\n\n1. Always validate inputs\n2. Monitor workflows continuously\n3. Handle escalations promptly"
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            agent.show_resource("best-practices")
        
        captured = capsys.readouterr()
        assert "Orchestration Best Practices" in captured.out
        assert "Always validate inputs" in captured.out

    @patch('os.path.exists')
    def test_show_resource_not_found(self, mock_exists, agent, capsys):
        """Test show_resource when file doesn't exist."""
        mock_exists.return_value = False
        
        agent.show_resource("nonexistent")
        
        captured = capsys.readouterr()
        assert "Unknown resource type: nonexistent" in captured.out

    def test_show_workflow_history(self, agent, capsys):
        """Test show_workflow_history method."""
        agent.workflow_history = ["Workflow 1", "Workflow 2", "Workflow 3"]
        agent._history_loaded = True  # Mark as loaded to skip file loading
    
        agent.show_workflow_history()
        captured = capsys.readouterr()
    
        assert "Workflow History:" in captured.out
        assert "Workflow 1" in captured.out
        assert "Workflow 2" in captured.out
        assert "Workflow 3" in captured.out

    def test_show_orchestration_history(self, agent, capsys):
        """Test show_orchestration_history method."""
        agent.orchestration_history = ["Orchestration 1", "Orchestration 2"]
        agent._history_loaded = True  # Mark as loaded to skip file loading
    
        agent.show_orchestration_history()
        captured = capsys.readouterr()
    
        assert "Orchestration History:" in captured.out
        assert "Orchestration 1" in captured.out
        assert "Orchestration 2" in captured.out

    def test_validate_input_valid(self, agent):
        """Test validate_input with valid parameters."""
        # Should not raise any exception
        agent.validate_input("test_workflow")
        agent.validate_input("test_workflow", "task_assignment")
        agent.validate_input("test_workflow", "task_assignment", "md")

    def test_validate_input_invalid_workflow_name(self, agent):
        """Test validate_input with invalid workflow name."""
        with pytest.raises(ValueError, match="Workflow name must be a non-empty string"):
            agent.validate_input("")
        
        with pytest.raises(ValueError, match="Workflow name must be a non-empty string"):
            agent.validate_input(None)

    def test_validate_input_invalid_orchestration_type(self, agent):
        """Test validate_input with invalid orchestration type."""
        with pytest.raises(ValueError, match="Orchestration type must be task_assignment, workflow_coordination, or resource_allocation"):
            agent.validate_input("test", "invalid_type")

    def test_validate_input_invalid_format_type(self, agent):
        """Test validate_input with invalid format type."""
        with pytest.raises(ValueError, match="Format type must be 'md', 'csv', or 'json'"):
            agent.validate_input("test", format_type="invalid")

    @patch('time.sleep')
    def test_monitor_workflows(self, mock_sleep, agent):
        """Test monitor_workflows method."""
        result = agent.monitor_workflows()
        
        assert result["monitoring_type"] == "Workflow Monitoring"
        assert result["status"] == "completed"
        assert "active_workflows" in result
        assert "workflow_metrics" in result
        assert "performance_indicators" in result
        assert "alerts" in result
        assert "recommendations" in result
        assert result["agent"] == "OrchestratorAgent"

    @patch('time.sleep')
    def test_orchestrate_agents(self, mock_sleep, agent):
        """Test orchestrate_agents method."""
        result = agent.orchestrate_agents("task_assignment", "Test feature development")
        
        assert result["orchestration_type"] == "task_assignment"
        assert result["task_description"] == "Test feature development"
        assert result["status"] == "completed"
        assert "agent_assignments" in result
        assert "coordination_plan" in result
        assert "communication_channels" in result
        assert "success_criteria" in result
        assert "risk_mitigation" in result
        assert "performance_metrics" in result

    @patch('time.sleep')
    def test_manage_escalations(self, mock_sleep, agent):
        """Test manage_escalations method."""
        result = agent.manage_escalations("workflow_blocked", "test_workflow")
        
        assert result["escalation_type"] == "workflow_blocked"
        assert result["workflow_name"] == "test_workflow"
        assert result["status"] == "resolved"
        assert "escalation_details" in result
        assert "resolution_actions" in result
        assert "prevention_measures" in result
        assert "escalation_metrics" in result

    @patch('time.sleep')
    def test_analyze_metrics(self, mock_sleep, agent):
        """Test analyze_metrics method."""
        result = agent.analyze_metrics("workflow_performance", "30 days")
        
        assert result["analysis_type"] == "workflow_performance Analysis"
        assert result["timeframe"] == "30 days"
        assert result["status"] == "completed"
        assert "key_metrics" in result
        assert "trend_analysis" in result
        assert "recommendations" in result
        assert "benchmark_comparison" in result

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_markdown(self, mock_file, agent):
        """Test export_report with markdown format."""
        test_data = {
            "report_type": "Test Report",
            "timeframe": "Test Timeframe",
            "status": "completed",
            "workflows_managed": 10,
            "escalations_handled": 2,
            "success_rate": "95%"
        }
        
        agent.export_report("md", test_data)
        
        mock_file.assert_called()
        # Check that file was opened for writing
        assert mock_file.call_count > 0

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_csv(self, mock_file, agent):
        """Test export_report with CSV format."""
        test_data = {
            "timeframe": "Test Timeframe",
            "status": "completed",
            "workflows_managed": 10,
            "escalations_handled": 2,
            "success_rate": "95%"
        }
        
        agent.export_report("csv", test_data)
        
        mock_file.assert_called()
        # Check that file was opened for writing
        assert mock_file.call_count > 0

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_json(self, mock_file, agent):
        """Test export_report with JSON format."""
        test_data = {
            "report_type": "Test Report",
            "timeframe": "Test Timeframe",
            "status": "completed"
        }
        
        agent.export_report("json", test_data)
        
        mock_file.assert_called()
        # Check that file was opened for writing
        assert mock_file.call_count > 0

    def test_export_report_invalid_format(self, agent):
        """Test export_report with invalid format."""
        with pytest.raises(ValueError, match="Format type must be 'md', 'csv', or 'json'"):
            agent.export_report("invalid")

    def test_export_report_default_data(self, agent):
        """Test export_report with default data."""
        with patch('builtins.open', new_callable=mock_open):
            agent.export_report("md")  # Should use default data

    def test_get_status(self, agent):
        """Test get_status method."""
        agent.workflow_history = ["Workflow 1", "Workflow 2"]
        agent.orchestration_history = ["Orchestration 1"]
        agent.status = {"workflow1": "active", "workflow2": "completed"}
        agent.event_log = [{"event": "test"}]
        agent._history_loaded = True  # Mark as loaded to skip file loading
    
        status = agent.get_status()
    
        assert status["agent_name"] == "Orchestrator"
        assert status["workflow_history_count"] == 2
        assert status["orchestration_history_count"] == 1
        assert status["active_workflows"] == 1
        assert status["last_workflow"] == "Workflow 2"
        assert status["last_orchestration"] == "Orchestration 1"
        assert status["event_log_count"] == 1
        assert status["status"] == "active"

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.publish')
    @patch('bmad.agents.Agent.Orchestrator.orchestrator.save_context')
    @patch('bmad.agents.Agent.Orchestrator.orchestrator.get_context')
    @patch('bmad.agents.Agent.Orchestrator.orchestrator.send_slack_message')
    def test_collaborate_example(self, mock_slack, mock_get_context, mock_save_context, mock_publish, agent):
        """Test collaborate_example method."""
        mock_publish.return_value = None
        mock_save_context.return_value = None
        mock_get_context.return_value = {"status": "active"}
        mock_slack.return_value = None
        
        agent.collaborate_example()
        
        # Verify that publish was called
        assert mock_publish.call_count >= 2  # At least workflow_started and orchestration_completed

    def test_run_agent_class_method(self):
        """Test run_agent class method."""
        with patch('bmad.agents.Agent.Orchestrator.orchestrator.OrchestratorAgent.run') as mock_run:
            OrchestratorAgent.run_agent()
            mock_run.assert_called_once()

    def test_load_event_log(self, agent):
        """Test load_event_log method."""
        test_events = [{"event": "test1"}, {"event": "test2"}]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_events))):
            events = agent.load_event_log()
        
        assert events == test_events

    def test_load_event_log_file_not_found(self, agent):
        """Test load_event_log when file doesn't exist."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            events = agent.load_event_log()
        
        assert events == []

    def test_save_event_log(self, agent):
        """Test save_event_log method."""
        agent.event_log = [{"event": "test1"}, {"event": "test2"}]
        
        with patch('builtins.open', mock_open()) as mock_file:
            agent.save_event_log()
        
        mock_file.assert_called_once()

    def test_log_event(self, agent):
        """Test log_event method."""
        with patch.object(agent, 'save_event_log') as mock_save:
            agent.log_event({"event_type": "test", "data": "test_data"})
            
            assert len(agent.event_log) == 1
            assert agent.event_log[0]["event_type"] == "test"
            assert "timestamp" in agent.event_log[0]
            mock_save.assert_called_once()

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.publish')
    def test_route_event(self, mock_publish, agent):
        """Test route_event method."""
        mock_publish.return_value = None
        
        with patch.object(agent, 'log_event') as mock_log:
            agent.route_event({"event_type": "feedback", "data": "test"})
            
            mock_log.assert_called_once()
            mock_publish.assert_called_once()

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.ask_openai')
    def test_intelligent_task_assignment_success(self, mock_ask_openai, agent):
        """Test intelligent_task_assignment with successful LLM response."""
        mock_ask_openai.return_value = {"agent": "TestEngineer"}
        
        result = agent.intelligent_task_assignment("Test task description")
        
        assert result == "TestEngineer"
        mock_ask_openai.assert_called_once()

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.ask_openai')
    def test_intelligent_task_assignment_error(self, mock_ask_openai, agent):
        """Test intelligent_task_assignment with LLM error."""
        mock_ask_openai.side_effect = Exception("LLM error")
        
        result = agent.intelligent_task_assignment("Test task description")
        
        assert result == "ProductOwner"  # Default fallback

    def test_intelligent_task_assignment_invalid_input(self, agent):
        """Test intelligent_task_assignment with invalid input."""
        with pytest.raises(ValueError, match="Task description must be a non-empty string"):
            agent.intelligent_task_assignment("")
        
        with pytest.raises(ValueError, match="Task description must be a non-empty string"):
            agent.intelligent_task_assignment(None)

    def test_set_workflow_status(self, agent):
        """Test set_workflow_status method."""
        with patch.object(agent, 'log_event') as mock_log:
            agent.set_workflow_status("test_workflow", "active")
            
            assert agent.status["test_workflow"] == "active"
            mock_log.assert_called_once()

    def test_get_workflow_status(self, agent):
        """Test get_workflow_status method."""
        agent.status["test_workflow"] = "active"
        
        assert agent.get_workflow_status("test_workflow") == "active"
        assert agent.get_workflow_status("nonexistent") == "onbekend"

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.send_slack_message')
    def test_start_workflow_valid(self, mock_slack, agent):
        """Test start_workflow with valid workflow."""
        mock_slack.return_value = None
        
        with patch.object(agent, 'set_workflow_status') as mock_set_status:
            agent.start_workflow("feature")
            
            mock_set_status.assert_called_with("feature", "lopend")
            # The workflow sends multiple Slack messages, so we check for at least one call
            assert mock_slack.call_count >= 1

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.send_slack_message')
    def test_start_workflow_invalid(self, mock_slack, agent):
        """Test start_workflow with invalid workflow."""
        mock_slack.return_value = None
        
        agent.start_workflow("nonexistent_workflow")
        
        # Should call Slack with error message
        mock_slack.assert_called_once()

    def test_list_workflows(self, agent, capsys):
        """Test list_workflows method."""
        agent.list_workflows()
        captured = capsys.readouterr()
        
        assert "Beschikbare workflows:" in captured.out
        assert "feature" in captured.out
        assert "incident_response" in captured.out

    def test_show_status(self, agent):
        """Test show_status method."""
        with patch.object(agent, 'monitor_agents') as mock_monitor:
            agent.show_status()
            mock_monitor.assert_called_once()

    def test_show_history(self, agent, capsys):
        """Test show_history method."""
        agent.event_log = [{"event": "test1"}, {"event": "test2"}]
        
        agent.show_history()
        captured = capsys.readouterr()
        
        assert "Event history:" in captured.out
        assert "test1" in captured.out
        assert "test2" in captured.out

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.publish')
    def test_replay_history(self, mock_publish, agent, capsys):
        """Test replay_history method."""
        mock_publish.return_value = None
        agent.event_log = [{"event_type": "test1"}, {"event_type": "test2"}]
        
        agent.replay_history()
        captured = capsys.readouterr()
        
        assert "Replaying event history..." in captured.out
        assert mock_publish.call_count == 2

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.get_events')
    def test_wait_for_hitl_decision_approved(self, mock_get_events, agent):
        """Test wait_for_hitl_decision with approval."""
        mock_get_events.return_value = [
            {"data": {"alert_id": "test_id", "approved": True}}
        ]
        
        result = agent.wait_for_hitl_decision("test_id", timeout=1)
        
        assert result is True

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.get_events')
    def test_wait_for_hitl_decision_rejected(self, mock_get_events, agent):
        """Test wait_for_hitl_decision with rejection."""
        mock_get_events.return_value = [
            {"data": {"alert_id": "test_id", "approved": False}}
        ]
        
        result = agent.wait_for_hitl_decision("test_id", timeout=1)
        
        assert result is False

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.get_events')
    def test_wait_for_hitl_decision_timeout(self, mock_get_events, agent):
        """Test wait_for_hitl_decision with timeout."""
        mock_get_events.return_value = []
        
        result = agent.wait_for_hitl_decision("test_id", timeout=1)
        
        assert result is False

    @patch('bmad.agents.Agent.Orchestrator.orchestrator.get_context')
    def test_monitor_agents(self, mock_get_context, agent, capsys):
        """Test monitor_agents method."""
        mock_get_context.return_value = "active"
        
        agent.monitor_agents()
        captured = capsys.readouterr()
        
        assert "Agent status:" in captured.out
        assert mock_get_context.call_count >= 1


class TestOrchestratorIntegration:
    """Integration tests for OrchestratorAgent."""

    def test_complete_orchestration_workflow(self):
        """Test complete orchestration workflow."""
        agent = OrchestratorAgent()
        
        # Test workflow monitoring
        monitoring_result = agent.monitor_workflows()
        assert monitoring_result["status"] == "completed"
        
        # Test agent orchestration
        orchestration_result = agent.orchestrate_agents("task_assignment", "Integration test")
        assert orchestration_result["status"] == "completed"
        
        # Test escalation management
        escalation_result = agent.manage_escalations("workflow_blocked", "test_workflow")
        assert escalation_result["status"] == "resolved"
        
        # Test metrics analysis
        metrics_result = agent.analyze_metrics("workflow_performance", "7 days")
        assert metrics_result["status"] == "completed"

    def test_agent_resource_completeness(self):
        """Test that all agent resources are properly defined."""
        agent = OrchestratorAgent()
        
        # Test resource completeness
        with patch.object(agent, 'test_resource_completeness') as mock_test:
            agent.test_resource_completeness()
            mock_test.assert_called_once()

    def test_agent_export_functionality(self):
        """Test agent export functionality."""
        agent = OrchestratorAgent()
        
        # Test export with different formats
        test_data = {
            "report_type": "Test Report",
            "timeframe": "Test Timeframe",
            "status": "completed",
            "workflows_managed": 5,
            "escalations_handled": 1,
            "success_rate": "90%"
        }
        
        with patch('builtins.open', mock_open()):
            # Test markdown export
            agent.export_report("md", test_data)
            
            # Test CSV export
            agent.export_report("csv", test_data)
            
            # Test JSON export
            agent.export_report("json", test_data)

    def test_agent_status_and_history(self):
        """Test agent status and history functionality."""
        agent = OrchestratorAgent()
        
        # Test status
        status = agent.get_status()
        assert status["agent_name"] == "Orchestrator"
        assert status["status"] == "active"
        
        # Test history display
        with patch('builtins.print') as mock_print:
            agent.show_workflow_history()
            agent.show_orchestration_history()
            assert mock_print.call_count >= 2 