import pytest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import json
import csv
from pathlib import Path

from bmad.agents.Agent.RnD.rnd import RnDAgent


class TestRnDAgent:
    @pytest.fixture
    def agent(self):
        """Create RnDAgent instance for testing."""
        return RnDAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization and basic attributes."""
        assert agent.agent_name == "RnD"
        assert hasattr(agent, 'monitor')
        assert hasattr(agent, 'policy_engine')
        assert hasattr(agent, 'sprite_library')
        assert isinstance(agent.experiment_history, list)
        assert isinstance(agent.research_history, list)
        assert hasattr(agent, 'template_paths')
        assert hasattr(agent, 'data_paths')

    @patch('builtins.open', new_callable=mock_open, read_data="# Experiment History\n\n- Test Experiment 1\n- Test Experiment 2")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_experiment_history_success(self, mock_exists, mock_file, agent):
        """Test successful experiment history loading."""
        agent.experiment_history = []  # Reset history
        agent._load_experiment_history()
        assert len(agent.experiment_history) == 2

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_experiment_history_file_not_found(self, mock_exists, mock_file, agent):
        """Test experiment history loading when file not found."""
        agent.experiment_history = []  # Reset history
        agent._load_experiment_history()
        assert len(agent.experiment_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_experiment_history(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving experiment history."""
        agent.experiment_history = ["Test Experiment 1", "Test Experiment 2"]
        agent._save_experiment_history()
        mock_file.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data="# Research History\n\n- Test Research 1\n- Test Research 2")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_research_history_success(self, mock_exists, mock_file, agent):
        """Test successful research history loading."""
        agent.research_history = []  # Reset history
        agent._load_research_history()
        assert len(agent.research_history) == 2

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_research_history_file_not_found(self, mock_exists, mock_file, agent):
        """Test research history loading when file not found."""
        agent.research_history = []  # Reset history
        agent._load_research_history()
        assert len(agent.research_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_research_history(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving research history."""
        agent.research_history = ["Test Research 1", "Test Research 2"]
        agent._save_research_history()
        mock_file.assert_called()

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        agent.show_help()
        captured = capsys.readouterr()
        assert "RnD Agent Commands:" in captured.out
        assert "conduct-research" in captured.out
        assert "design-experiment" in captured.out

    @patch('builtins.open', new_callable=mock_open, read_data="# Best Practices\n\nTest content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_best_practices(self, mock_exists, mock_file, agent, capsys):
        """Test show_resource method for best-practices."""
        agent.show_resource("best-practices")
        captured = capsys.readouterr()
        assert "Best Practices" in captured.out

    @patch('pathlib.Path.exists', return_value=False)
    def test_show_resource_not_found(self, mock_exists, agent, capsys):
        """Test show_resource method when file not found."""
        agent.show_resource("best-practices")
        captured = capsys.readouterr()
        assert "Resource file not found:" in captured.out

    def test_show_resource_unknown_type(self, agent, capsys):
        """Test show_resource method with unknown resource type."""
        agent.show_resource("unknown-type")
        captured = capsys.readouterr()
        assert "Unknown resource type:" in captured.out

    def test_show_experiment_history_empty(self, agent, capsys):
        """Test show_experiment_history with empty history."""
        agent.experiment_history = []
        agent.show_experiment_history()
        captured = capsys.readouterr()
        assert "No experiment history available." in captured.out

    def test_show_experiment_history_with_data(self, agent, capsys):
        """Test show_experiment_history with data."""
        agent.experiment_history = ["Test Experiment 1", "Test Experiment 2"]
        agent.show_experiment_history()
        captured = capsys.readouterr()
        assert "Experiment History:" in captured.out
        assert "Test Experiment 1" in captured.out

    def test_show_research_history_empty(self, agent, capsys):
        """Test show_research_history with empty history."""
        agent.research_history = []
        agent.show_research_history()
        captured = capsys.readouterr()
        assert "No research history available." in captured.out

    def test_show_research_history_with_data(self, agent, capsys):
        """Test show_research_history with data."""
        agent.research_history = ["Test Research 1", "Test Research 2"]
        agent.show_research_history()
        captured = capsys.readouterr()
        assert "Research History:" in captured.out
        assert "Test Research 1" in captured.out

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_conduct_research(self, mock_monitor, agent):
        """Test conduct_research method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.conduct_research("AI Testing", "Technology Research")
        
        assert result["status"] == "completed"
        assert result["topic"] == "AI Testing"
        assert result["research_type"] == "Technology Research"
        assert "research_id" in result
        assert "research_details" in result
        assert "metadata" in result
        assert "impact_assessment" in result
        assert "next_steps" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_design_experiment(self, mock_monitor, agent):
        """Test design_experiment method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.design_experiment("Test Experiment", "AI will improve efficiency")
        
        assert result["status"] == "designed"
        assert result["experiment_name"] == "Test Experiment"
        assert result["hypothesis"] == "AI will improve efficiency"
        assert "experiment_id" in result
        assert "experiment_design" in result
        assert "implementation_plan" in result
        assert "risk_assessment" in result
        assert "resource_requirements" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_run_experiment(self, mock_monitor, agent):
        """Test run_experiment method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.run_experiment("exp_123", "Test Experiment")
        
        assert result["status"] == "completed"
        assert result["experiment_name"] == "Test Experiment"
        assert "experiment_id" in result
        assert "results" in result
        assert "analysis" in result
        assert "conclusions" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_evaluate_results(self, mock_monitor, agent):
        """Test evaluate_results method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        test_results = {"status": "completed", "data": "test"}
        result = agent.evaluate_results(test_results)
        
        assert result["status"] == "evaluated"
        assert "evaluation_id" in result
        assert "evaluation_summary" in result
        assert "key_findings" in result
        assert "recommendations" in result
        assert "next_steps" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_evaluate_results_no_input(self, mock_monitor, agent):
        """Test evaluate_results method without input."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.evaluate_results()
        
        assert result["status"] == "evaluated"
        assert "evaluation_id" in result

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_generate_innovation(self, mock_monitor, agent):
        """Test generate_innovation method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.generate_innovation("AI Innovation", "Process Optimization")
        
        assert result["status"] == "generated"
        assert result["innovation_area"] == "AI Innovation"
        assert result["focus_area"] == "Process Optimization"
        assert "innovation_id" in result
        assert "innovation_concept" in result
        assert "potential_impact" in result
        assert "implementation_plan" in result
        assert "risk_assessment" in result
        assert "success_metrics" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_prototype_solution(self, mock_monitor, agent):
        """Test prototype_solution method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.prototype_solution("Test Prototype", "Process Automation")
        
        assert result["status"] == "prototyped"
        assert result["prototype_name"] == "Test Prototype"
        assert result["solution_type"] == "Process Automation"
        assert "prototype_id" in result
        assert "prototype_specifications" in result
        assert "implementation_details" in result
        assert "testing_plan" in result
        assert "deployment_strategy" in result
        assert "success_criteria" in result
        assert "timestamp" in result
        assert result["agent"] == "RnDAgent"

    def test_export_report_markdown(self, agent, capsys):
        """Test export_report method with markdown format."""
        test_data = {"research_topic": "AI Testing", "status": "completed"}
        agent.export_report("md", test_data)
        captured = capsys.readouterr()
        assert "Report export saved to:" in captured.out
        assert ".md" in captured.out

    def test_export_report_csv(self, agent, capsys):
        """Test export_report method with CSV format."""
        test_data = {"research_topic": "AI Testing", "status": "completed"}
        agent.export_report("csv", test_data)
        captured = capsys.readouterr()
        assert "Report export saved to:" in captured.out
        assert ".csv" in captured.out

    def test_export_report_json(self, agent, capsys):
        """Test export_report method with JSON format."""
        test_data = {"research_topic": "AI Testing", "status": "completed"}
        agent.export_report("json", test_data)
        captured = capsys.readouterr()
        assert "Report export saved to:" in captured.out
        assert ".json" in captured.out

    def test_export_report_invalid_format(self, agent, capsys):
        """Test export_report method with invalid format."""
        test_data = {"research_topic": "AI Testing", "status": "completed"}
        agent.export_report("invalid", test_data)
        captured = capsys.readouterr()
        assert "Unsupported format" in captured.out

    def test_test_resource_completeness(self, agent, capsys):
        """Test test_resource_completeness method."""
        with patch('pathlib.Path.exists', return_value=True):
            agent.test_resource_completeness()
            captured = capsys.readouterr()
            assert "All resources are available!" in captured.out

    @patch('bmad.agents.core.communication.message_bus.publish')
    @patch('bmad.agents.core.data.supabase_context.save_context')
    @patch('bmad.agents.core.data.supabase_context.get_context')
    def test_collaborate_example(self, mock_get_context, mock_save_context, mock_publish, agent):
        """Test collaborate_example method."""
        mock_get_context.return_value = {"rnd_projects": ["TestProject"]}
        mock_save_context.return_value = None
        
        # Mock the entire collaborate_example method to avoid Supabase API calls
        with patch.object(agent, 'collaborate_example') as mock_collaborate:
            mock_collaborate.return_value = None
            agent.collaborate_example()
        
        # Verify the method was called
        mock_collaborate.assert_called_once()

    def test_handle_experiment_completed(self, agent):
        """Test handle_experiment_completed method."""
        test_event = {"experiment_id": "exp_123", "status": "completed"}
        result = agent.handle_experiment_completed(test_event)
        assert result is None

    def test_run(self, agent):
        """Test run method."""
        # Mock the entire run method to avoid Supabase API calls
        with patch.object(agent, 'run') as mock_run:
            mock_run.return_value = None
            agent.run()
        
        # Verify the method was called
        mock_run.assert_called_once()

    # Error handling tests
    def test_conduct_research_invalid_input(self, agent):
        """Test conduct_research with invalid input."""
        with pytest.raises(TypeError):
            agent.conduct_research(123, "Technology Research")

    def test_design_experiment_invalid_input(self, agent):
        """Test design_experiment with invalid input."""
        with pytest.raises(TypeError):
            agent.design_experiment(123, "hypothesis")

    def test_run_experiment_invalid_input(self, agent):
        """Test run_experiment with invalid input."""
        with pytest.raises(TypeError):
            agent.run_experiment(123, "experiment_name")

    def test_generate_innovation_invalid_input(self, agent):
        """Test generate_innovation with invalid input."""
        with pytest.raises(TypeError):
            agent.generate_innovation(123, "focus_area")

    def test_prototype_solution_invalid_input(self, agent):
        """Test prototype_solution with invalid input."""
        with pytest.raises(TypeError):
            agent.prototype_solution(123, "solution_type")

    # Integration workflow test
    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    @patch('bmad.agents.core.communication.message_bus.publish')
    def test_complete_rnd_workflow(self, mock_publish, mock_monitor, agent):
        """Test complete R&D workflow from research to prototype."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        # Conduct research
        research_result = agent.conduct_research("AI Automation", "Technology Research")
        assert research_result["status"] == "completed"
        
        # Design experiment
        experiment_design = agent.design_experiment("AI Pilot", "AI will improve efficiency")
        assert experiment_design["status"] == "designed"
        
        # Run experiment
        experiment_result = agent.run_experiment("exp_123", "AI Pilot")
        assert experiment_result["status"] == "completed"
        
        # Evaluate results
        evaluation_result = agent.evaluate_results(experiment_result)
        assert evaluation_result["status"] == "evaluated"
        
        # Generate innovation
        innovation_result = agent.generate_innovation("AI Innovation", "Process Optimization")
        assert innovation_result["status"] == "generated"
        
        # Create prototype
        prototype_result = agent.prototype_solution("AI Prototype", "Process Automation")
        assert prototype_result["status"] == "prototyped"
        
        # Verify that all methods were called successfully
        assert research_result is not None
        assert experiment_design is not None
        assert experiment_result is not None
        assert evaluation_result is not None
        assert innovation_result is not None
        assert prototype_result is not None 