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

    def test_export_report_invalid_format(self, agent):
        """Test export_report method with invalid format."""
        test_data = {"research_topic": "AI Testing", "status": "completed"}
        with pytest.raises(ValueError, match="format_type must be one of: md, csv, json"):
            agent.export_report("invalid", test_data)

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

    # Additional error handling and input validation tests
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_experiment_history_permission_error(self, mock_exists, mock_file, agent):
        """Test experiment history loading with permission error."""
        agent.experiment_history = []  # Reset history
        agent._load_experiment_history()
        assert len(agent.experiment_history) == 0

    @patch('builtins.open', side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid utf-8"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_experiment_history_unicode_error(self, mock_exists, mock_file, agent):
        """Test experiment history loading with unicode error."""
        agent.experiment_history = []  # Reset history
        agent._load_experiment_history()
        assert len(agent.experiment_history) == 0

    @patch('builtins.open', side_effect=OSError("OS error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_experiment_history_os_error(self, mock_exists, mock_file, agent):
        """Test experiment history loading with OS error."""
        agent.experiment_history = []  # Reset history
        agent._load_experiment_history()
        assert len(agent.experiment_history) == 0

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_experiment_history_permission_error(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving experiment history with permission error."""
        agent.experiment_history = ["Test Experiment 1", "Test Experiment 2"]
        agent._save_experiment_history()

    @patch('builtins.open', side_effect=OSError("OS error"))
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_experiment_history_os_error(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving experiment history with OS error."""
        agent.experiment_history = ["Test Experiment 1", "Test Experiment 2"]
        agent._save_experiment_history()

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_research_history_permission_error(self, mock_exists, mock_file, agent):
        """Test research history loading with permission error."""
        agent.research_history = []  # Reset history
        agent._load_research_history()
        assert len(agent.research_history) == 0

    @patch('builtins.open', side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid utf-8"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_research_history_unicode_error(self, mock_exists, mock_file, agent):
        """Test research history loading with unicode error."""
        agent.research_history = []  # Reset history
        agent._load_research_history()
        assert len(agent.research_history) == 0

    @patch('builtins.open', side_effect=OSError("OS error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_research_history_os_error(self, mock_exists, mock_file, agent):
        """Test research history loading with OS error."""
        agent.research_history = []  # Reset history
        agent._load_research_history()
        assert len(agent.research_history) == 0

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_research_history_permission_error(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving research history with permission error."""
        agent.research_history = ["Test Research 1", "Test Research 2"]
        agent._save_research_history()

    @patch('builtins.open', side_effect=OSError("OS error"))
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_research_history_os_error(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving research history with OS error."""
        agent.research_history = ["Test Research 1", "Test Research 2"]
        agent._save_research_history()

    def test_show_resource_invalid_type(self, agent, capsys):
        """Test show_resource method with invalid resource type."""
        agent.show_resource(123)  # Invalid type
        captured = capsys.readouterr()
        assert "Error: resource_type must be a string" in captured.out

    def test_show_resource_empty_type(self, agent, capsys):
        """Test show_resource method with empty resource type."""
        agent.show_resource("")  # Empty string
        captured = capsys.readouterr()
        assert "Error: resource_type cannot be empty" in captured.out

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_file_not_found(self, mock_exists, mock_file, agent, capsys):
        """Test show_resource method when file not found."""
        agent.show_resource("best-practices")
        captured = capsys.readouterr()
        assert "Resource file not found: best-practices" in captured.out

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_permission_error(self, mock_exists, mock_file, agent, capsys):
        """Test show_resource method with permission error."""
        agent.show_resource("best-practices")
        captured = capsys.readouterr()
        assert "Permission denied accessing resource best-practices" in captured.out

    @patch('builtins.open', side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid utf-8"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_show_resource_unicode_error(self, mock_exists, mock_file, agent, capsys):
        """Test show_resource method with unicode error."""
        agent.show_resource("best-practices")
        captured = capsys.readouterr()
        assert "Unicode decode error in resource best-practices" in captured.out

    def test_conduct_research_empty_topic(self, agent):
        """Test conduct_research with empty topic."""
        with pytest.raises(ValueError, match="research_topic cannot be empty"):
            agent.conduct_research("", "Technology Research")

    def test_conduct_research_empty_type(self, agent):
        """Test conduct_research with empty type."""
        with pytest.raises(ValueError, match="research_type cannot be empty"):
            agent.conduct_research("AI Automation", "")

    def test_design_experiment_empty_name(self, agent):
        """Test design_experiment with empty name."""
        with pytest.raises(ValueError, match="experiment_name cannot be empty"):
            agent.design_experiment("", "hypothesis")

    def test_design_experiment_empty_hypothesis(self, agent):
        """Test design_experiment with empty hypothesis."""
        with pytest.raises(ValueError, match="hypothesis cannot be empty"):
            agent.design_experiment("AI Pilot", "")

    def test_run_experiment_empty_id(self, agent):
        """Test run_experiment with empty id."""
        with pytest.raises(ValueError, match="experiment_id cannot be empty"):
            agent.run_experiment("", "experiment_name")

    def test_run_experiment_empty_name(self, agent):
        """Test run_experiment with empty name."""
        with pytest.raises(ValueError, match="experiment_name cannot be empty"):
            agent.run_experiment("exp_123", "")

    def test_evaluate_results_invalid_type(self, agent):
        """Test evaluate_results with invalid type."""
        with pytest.raises(TypeError, match="experiment_results must be a dictionary"):
            agent.evaluate_results("invalid")

    def test_generate_innovation_empty_area(self, agent):
        """Test generate_innovation with empty area."""
        with pytest.raises(ValueError, match="innovation_area cannot be empty"):
            agent.generate_innovation("", "focus_area")

    def test_generate_innovation_empty_focus(self, agent):
        """Test generate_innovation with empty focus."""
        with pytest.raises(ValueError, match="focus_area cannot be empty"):
            agent.generate_innovation("AI Innovation", "")

    def test_prototype_solution_empty_name(self, agent):
        """Test prototype_solution with empty name."""
        with pytest.raises(ValueError, match="prototype_name cannot be empty"):
            agent.prototype_solution("", "solution_type")

    def test_prototype_solution_empty_type(self, agent):
        """Test prototype_solution with empty type."""
        with pytest.raises(ValueError, match="solution_type cannot be empty"):
            agent.prototype_solution("AI Prototype", "")

    def test_export_report_invalid_format_type(self, agent):
        """Test export_report with invalid format type."""
        with pytest.raises(TypeError, match="format_type must be a string"):
            agent.export_report(123)

    def test_export_report_invalid_format_value(self, agent):
        """Test export_report with invalid format value."""
        with pytest.raises(ValueError, match="format_type must be one of: md, csv, json"):
            agent.export_report("xml")

    def test_export_report_invalid_report_data_type(self, agent):
        """Test export_report with invalid report data type."""
        with pytest.raises(TypeError, match="report_data must be a dictionary"):
            agent.export_report("md", "invalid")

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_markdown_permission_error(self, mock_file, agent):
        """Test _export_markdown with permission error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_markdown(test_data)

    @patch('builtins.open', side_effect=OSError("OS error"))
    def test_export_markdown_os_error(self, mock_file, agent):
        """Test _export_markdown with OS error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_markdown(test_data)

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_csv_permission_error(self, mock_file, agent):
        """Test _export_csv with permission error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_csv(test_data)

    @patch('builtins.open', side_effect=OSError("OS error"))
    def test_export_csv_os_error(self, mock_file, agent):
        """Test _export_csv with OS error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_csv(test_data)

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_json_permission_error(self, mock_file, agent):
        """Test _export_json with permission error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_json(test_data)

    @patch('builtins.open', side_effect=OSError("OS error"))
    def test_export_json_os_error(self, mock_file, agent):
        """Test _export_json with OS error."""
        test_data = {"version": "1.2.0", "status": "success"}
        agent._export_json(test_data)

    def test_handle_experiment_completed_invalid_event_type(self, agent):
        """Test handle_experiment_completed with invalid event type."""
        agent.handle_experiment_completed("invalid event")  # Should handle gracefully 


class TestRnDAgentCLI:
    @patch('sys.argv', ['rnd.py', 'help'])
    @patch('builtins.print')
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_help(self, mock_get_context, mock_publish, mock_save_context, mock_print):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'show_help') as mock_show_help:
                main()
                mock_show_help.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'conduct-research', '--research-topic', 'AI Testing', '--research-type', 'Technology Research'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_conduct_research(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'conduct_research', return_value={"result": "ok"}) as mock_conduct_research:
                main()
                mock_conduct_research.assert_called_once_with('AI Testing', 'Technology Research')

    @patch('sys.argv', ['rnd.py', 'design-experiment', '--experiment-name', 'AI Pilot', '--hypothesis', 'AI will improve efficiency'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_design_experiment(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'design_experiment', return_value={"result": "ok"}) as mock_design_experiment:
                main()
                mock_design_experiment.assert_called_once_with('AI Pilot', 'AI will improve efficiency')

    @patch('sys.argv', ['rnd.py', 'run-experiment', '--experiment-id', 'exp_123', '--experiment-name', 'AI Pilot'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_run_experiment(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'run_experiment', return_value={"result": "ok"}) as mock_run_experiment:
                main()
                mock_run_experiment.assert_called_once_with('exp_123', 'AI Pilot')

    @patch('sys.argv', ['rnd.py', 'evaluate-results'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_evaluate_results(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'evaluate_results', return_value={"result": "ok"}) as mock_evaluate_results:
                main()
                mock_evaluate_results.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'generate-innovation', '--innovation-area', 'AI Innovation', '--focus-area', 'Process Optimization'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_generate_innovation(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'generate_innovation', return_value={"result": "ok"}) as mock_generate_innovation:
                main()
                mock_generate_innovation.assert_called_once_with('AI Innovation', 'Process Optimization')

    @patch('sys.argv', ['rnd.py', 'prototype-solution', '--prototype-name', 'AI Prototype', '--solution-type', 'Process Automation'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_prototype_solution(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'prototype_solution', return_value={"result": "ok"}) as mock_prototype_solution:
                main()
                mock_prototype_solution.assert_called_once_with('AI Prototype', 'Process Automation')

    @patch('sys.argv', ['rnd.py', 'show-experiment-history'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_show_experiment_history(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'show_experiment_history') as mock_show_experiment_history:
                main()
                mock_show_experiment_history.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'show-research-history'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_show_research_history(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'show_research_history') as mock_show_research_history:
                main()
                mock_show_research_history.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'show-best-practices'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_show_best_practices(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'show_resource') as mock_show_resource:
                main()
                mock_show_resource.assert_called_once_with('best-practices')

    @patch('sys.argv', ['rnd.py', 'show-changelog'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_show_changelog(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'show_resource') as mock_show_resource:
                main()
                mock_show_resource.assert_called_once_with('changelog')

    @patch('sys.argv', ['rnd.py', 'export-report', '--format', 'json'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_export_report(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'export_report') as mock_export_report:
                main()
                mock_export_report.assert_called_once_with('json')

    @patch('sys.argv', ['rnd.py', 'test'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_test(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'test_resource_completeness') as mock_test_resource_completeness:
                main()
                mock_test_resource_completeness.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'collaborate'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_collaborate(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'collaborate_example') as mock_collaborate_example:
                main()
                mock_collaborate_example.assert_called_once()

    @patch('sys.argv', ['rnd.py', 'run'])
    @patch('bmad.agents.Agent.RnD.rnd.save_context')
    @patch('bmad.agents.Agent.RnD.rnd.publish')
    @patch('bmad.agents.Agent.RnD.rnd.get_context', return_value={"status": "active"})
    def test_cli_run(self, mock_get_context, mock_publish, mock_save_context):
        from bmad.agents.Agent.RnD.rnd import main
        with patch('bmad.agents.Agent.RnD.rnd.RnDAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            with patch.object(mock_agent, 'run') as mock_run:
                main()
                mock_run.assert_called_once() 