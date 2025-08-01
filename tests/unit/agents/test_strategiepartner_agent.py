import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
from datetime import datetime, timedelta

from bmad.agents.Agent.StrategiePartner.strategiepartner import (
    StrategiePartnerAgent,
    StrategyError,
    StrategyValidationError
)


class TestStrategiePartnerAgent:
    """Test suite for StrategiePartnerAgent with comprehensive coverage."""

    @pytest.fixture
    def agent(self):
        """Create a StrategiePartnerAgent instance for testing."""
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_performance_monitor'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_sprite_library'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.BMADTracer'):
            return StrategiePartnerAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_name == "StrategiePartner"
        assert isinstance(agent.strategy_history, list)
        assert isinstance(agent.market_data, list)
        assert isinstance(agent.competitive_data, list)
        assert isinstance(agent.risk_register, list)
        assert isinstance(agent.performance_metrics, dict)

    def test_validate_input_success(self, agent):
        """Test input validation with valid input."""
        agent._validate_input("test", str, "test_param")
        agent._validate_input(123, int, "test_param")
        agent._validate_input([], list, "test_param")

    def test_validate_input_failure(self, agent):
        """Test input validation with invalid input."""
        with pytest.raises(StrategyValidationError):
            agent._validate_input(123, str, "test_param")
        with pytest.raises(StrategyValidationError):
            agent._validate_input("test", int, "test_param")

    def test_validate_strategy_data_success(self, agent):
        """Test strategy data validation with valid data."""
        valid_data = {"strategy_name": "Test Strategy", "objectives": [], "timeline": "12 months", "stakeholders": []}
        agent._validate_strategy_data(valid_data)

    def test_validate_strategy_data_missing_field(self, agent):
        """Test strategy data validation with missing required field."""
        invalid_data = {"strategy_name": "Test Strategy", "objectives": []}  # Missing timeline and stakeholders
        with pytest.raises(StrategyValidationError):
            agent._validate_strategy_data(invalid_data)

    def test_validate_market_data_success(self, agent):
        """Test market data validation with valid data."""
        valid_data = {"market_size": "$500B", "growth_rate": "8.5%", "key_players": [], "trends": []}
        agent._validate_market_data(valid_data)

    def test_validate_market_data_missing_field(self, agent):
        """Test market data validation with missing required field."""
        invalid_data = {"market_size": "$500B", "growth_rate": "8.5%"}  # Missing key_players and trends
        with pytest.raises(StrategyValidationError):
            agent._validate_market_data(invalid_data)

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_strategy_history_success(self, mock_exists, mock_open, agent):
        """Test successful strategy history loading."""
        # Clear existing history first
        agent.strategy_history = []
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "# Strategy History\n\n- Strategy 1 completed\n- Strategy 2 in progress"
        
        agent._load_strategy_history()
        assert len(agent.strategy_history) == 2

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_strategy_history_file_not_found(self, mock_exists, mock_open, agent):
        """Test strategy history loading when file doesn't exist."""
        # Clear existing history first
        agent.strategy_history = []
        mock_exists.return_value = False
        
        agent._load_strategy_history()
        assert len(agent.strategy_history) == 0

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_strategy_history_permission_error(self, mock_exists, mock_open, agent):
        """Test strategy history loading with permission error."""
        mock_exists.return_value = True
        mock_open.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(StrategyError):
            agent._load_strategy_history()

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_save_strategy_history_success(self, mock_mkdir, mock_open, agent):
        """Test successful strategy history saving."""
        agent.strategy_history = ["Strategy 1 completed", "Strategy 2 in progress"]
        
        agent._save_strategy_history()
        mock_open.assert_called()

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_save_strategy_history_permission_error(self, mock_mkdir, mock_open, agent):
        """Test strategy history saving with permission error."""
        mock_open.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(StrategyError):
            agent._save_strategy_history()

    def test_show_help(self, agent, capsys):
        """Test help display."""
        agent.show_help()
        captured = capsys.readouterr()
        assert "StrategiePartner Agent Commands:" in captured.out

    def test_show_resource_success(self, agent, capsys):
        """Test resource display with valid resource type."""
        with patch('builtins.open', create=True) as mock_open, \
             patch('pathlib.Path.exists', return_value=True):
            mock_open.return_value.__enter__.return_value.read.return_value = "Strategy planning content"
            agent.show_resource("strategy-planning")
            captured = capsys.readouterr()
            assert "Strategy planning content" in captured.out

    def test_show_resource_invalid_type(self, agent, capsys):
        """Test resource display with invalid resource type."""
        agent.show_resource("invalid-type")
        captured = capsys.readouterr()
        assert "Unknown resource type" in captured.out

    def test_show_resource_empty_type(self, agent, capsys):
        """Test resource display with empty resource type."""
        agent.show_resource("")
        captured = capsys.readouterr()
        assert "Permission denied accessing resource" in captured.out or "Error reading resource" in captured.out

    def test_show_strategy_history_empty(self, agent, capsys):
        """Test strategy history display when empty."""
        agent.strategy_history = []
        agent.show_strategy_history()
        captured = capsys.readouterr()
        assert "No strategy history available" in captured.out

    def test_show_strategy_history_with_data(self, agent, capsys):
        """Test strategy history display with data."""
        agent.strategy_history = ["Strategy 1 completed", "Strategy 2 in progress"]
        agent.show_strategy_history()
        captured = capsys.readouterr()
        assert "Strategy History:" in captured.out
        assert "Strategy 1 completed" in captured.out

    def test_show_market_data_empty(self, agent, capsys):
        """Test market data display when empty."""
        agent.market_data = []
        agent.show_market_data()
        captured = capsys.readouterr()
        assert "No market data available" in captured.out

    def test_show_market_data_with_data(self, agent, capsys):
        """Test market data display with data."""
        agent.market_data = ["Market size: $500B", "Growth rate: 8.5%"]
        agent.show_market_data()
        captured = capsys.readouterr()
        assert "Market Data:" in captured.out
        assert "Market size: $500B" in captured.out

    def test_show_competitive_data_empty(self, agent, capsys):
        """Test competitive data display when empty."""
        agent.competitive_data = []
        agent.show_competitive_data()
        captured = capsys.readouterr()
        assert "No competitive data available" in captured.out

    def test_show_competitive_data_with_data(self, agent, capsys):
        """Test competitive data display with data."""
        agent.competitive_data = ["Competitor A: 25% market share", "Competitor B: 15% market share"]
        agent.show_competitive_data()
        captured = capsys.readouterr()
        assert "Competitive Data:" in captured.out
        assert "Competitor A: 25% market share" in captured.out

    def test_show_risk_register_empty(self, agent, capsys):
        """Test risk register display when empty."""
        agent.risk_register = []
        agent.show_risk_register()
        captured = capsys.readouterr()
        assert "No risk register available" in captured.out

    def test_show_risk_register_with_data(self, agent, capsys):
        """Test risk register display with data."""
        agent.risk_register = ["High risk: Technology failure", "Medium risk: Budget overruns"]
        agent.show_risk_register()
        captured = capsys.readouterr()
        assert "Risk Register:" in captured.out
        assert "High risk: Technology failure" in captured.out

    @patch('time.sleep')
    def test_develop_strategy_success(self, mock_sleep, agent):
        """Test successful strategy development."""
        initial_count = len(agent.strategy_history)
        result = agent.develop_strategy("Digital Transformation Strategy")
        
        assert result["strategy_name"] == "Digital Transformation Strategy"
        assert result["status"] == "developed"
        assert "objectives" in result
        assert "timeline" in result
        assert len(agent.strategy_history) == initial_count + 1

    def test_develop_strategy_empty_name(self, agent):
        """Test strategy development with empty strategy name."""
        with pytest.raises(StrategyValidationError):
            agent.develop_strategy("")  # Empty strategy name

    @patch('time.sleep')
    def test_analyze_market_success(self, mock_sleep, agent):
        """Test successful market analysis."""
        initial_count = len(agent.market_data)
        result = agent.analyze_market("Technology")
        
        assert result["sector"] == "Technology"
        assert "market_size" in result
        assert "growth_rate" in result
        assert "key_players" in result
        assert len(agent.market_data) == initial_count + 1

    def test_analyze_market_empty_sector(self, agent):
        """Test market analysis with empty sector."""
        with pytest.raises(StrategyValidationError):
            agent.analyze_market("")  # Empty sector

    @patch('time.sleep')
    def test_competitive_analysis_success(self, mock_sleep, agent):
        """Test successful competitive analysis."""
        initial_count = len(agent.competitive_data)
        result = agent.competitive_analysis("Main Competitor")
        
        assert result["competitor"] == "Main Competitor"
        assert "market_share" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert len(agent.competitive_data) == initial_count + 1

    def test_competitive_analysis_empty_competitor(self, agent):
        """Test competitive analysis with empty competitor name."""
        with pytest.raises(StrategyValidationError):
            agent.competitive_analysis("")  # Empty competitor name

    @patch('time.sleep')
    def test_assess_risks_success(self, mock_sleep, agent):
        """Test successful risk assessment."""
        initial_count = len(agent.risk_register)
        result = agent.assess_risks("Digital Transformation")
        
        assert result["strategy"] == "Digital Transformation"
        assert "high_risks" in result
        assert "medium_risks" in result
        assert "low_risks" in result
        assert "risk_score" in result
        assert len(agent.risk_register) == initial_count + 1

    def test_assess_risks_empty_strategy(self, agent):
        """Test risk assessment with empty strategy name."""
        with pytest.raises(StrategyValidationError):
            agent.assess_risks("")  # Empty strategy name

    @patch('time.sleep')
    def test_stakeholder_analysis_success(self, mock_sleep, agent):
        """Test successful stakeholder analysis."""
        initial_count = len(agent.strategy_history)
        result = agent.stakeholder_analysis("Digital Transformation Project")
        
        assert result["project"] == "Digital Transformation Project"
        assert "stakeholders" in result
        assert "influence_levels" in result
        assert "engagement_strategies" in result
        assert len(agent.strategy_history) == initial_count + 1

    def test_stakeholder_analysis_empty_project(self, agent):
        """Test stakeholder analysis with empty project name."""
        with pytest.raises(StrategyValidationError):
            agent.stakeholder_analysis("")  # Empty project name

    @patch('time.sleep')
    def test_create_roadmap_success(self, mock_sleep, agent):
        """Test successful roadmap creation."""
        initial_count = len(agent.strategy_history)
        result = agent.create_roadmap("Digital Transformation Strategy")
        
        assert result["strategy"] == "Digital Transformation Strategy"
        assert "phases" in result
        assert "total_duration" in result
        assert "key_milestones" in result
        assert len(agent.strategy_history) == initial_count + 1

    def test_create_roadmap_empty_strategy(self, agent):
        """Test roadmap creation with empty strategy name."""
        with pytest.raises(StrategyValidationError):
            agent.create_roadmap("")  # Empty strategy name

    @patch('time.sleep')
    def test_calculate_roi_success(self, mock_sleep, agent):
        """Test successful ROI calculation."""
        initial_count = len(agent.strategy_history)
        result = agent.calculate_roi("Digital Transformation Strategy")
        
        assert result["strategy"] == "Digital Transformation Strategy"
        assert "investment" in result
        assert "expected_returns" in result
        assert "roi_percentage" in result
        assert "payback_period" in result
        assert len(agent.strategy_history) == initial_count + 1

    def test_calculate_roi_empty_strategy(self, agent):
        """Test ROI calculation with empty strategy name."""
        with pytest.raises(StrategyValidationError):
            agent.calculate_roi("")  # Empty strategy name

    @patch('time.sleep')
    def test_business_model_canvas_success(self, mock_sleep, agent):
        """Test successful business model canvas generation."""
        initial_count = len(agent.strategy_history)
        result = agent.business_model_canvas()
        
        assert "key_partners" in result
        assert "key_activities" in result
        assert "value_propositions" in result
        assert "customer_segments" in result
        assert "revenue_streams" in result
        assert len(agent.strategy_history) == initial_count + 1

    def test_test_resource_completeness_all_available(self, agent):
        """Test resource completeness when all resources are available."""
        with patch('pathlib.Path.exists', return_value=True):
            result = agent.test_resource_completeness()
            assert result is True

    def test_test_resource_completeness_missing_resources(self, agent):
        """Test resource completeness when resources are missing."""
        with patch('pathlib.Path.exists', return_value=False):
            result = agent.test_resource_completeness()
            assert result is False

    @patch('bmad.agents.Agent.StrategiePartner.strategiepartner.publish')
    def test_collaborate_example_success(self, mock_publish, agent):
        """Test successful collaboration example."""
        with patch.object(agent, 'develop_strategy') as mock_develop, \
             patch.object(agent, 'analyze_market') as mock_analyze, \
             patch.object(agent, 'competitive_analysis') as mock_competitive, \
             patch.object(agent, 'assess_risks') as mock_risks, \
             patch.object(agent, 'stakeholder_analysis') as mock_stakeholder, \
             patch.object(agent, 'create_roadmap') as mock_roadmap, \
             patch.object(agent, 'calculate_roi') as mock_roi, \
             patch.object(agent, 'business_model_canvas') as mock_canvas:
            agent.collaborate_example()
            
            mock_publish.assert_called()
            mock_develop.assert_called()
            mock_analyze.assert_called()
            mock_competitive.assert_called()
            mock_risks.assert_called()
            mock_stakeholder.assert_called()
            mock_roadmap.assert_called()
            mock_roi.assert_called()
            mock_canvas.assert_called()

    def test_handle_alignment_check_completed_success(self, agent):
        """Test successful alignment check completion handling."""
        event = {"strategy": "Test Strategy", "status": "aligned"}
        
        with patch.object(agent.monitor, 'log_metric') as mock_log, \
             patch.object(agent.policy_engine, 'evaluate_policy') as mock_policy:
            agent.handle_alignment_check_completed(event)
            
            mock_log.assert_called_with("alignment_check", event)
            mock_policy.assert_called()

    def test_handle_strategy_development_requested_success(self, agent):
        """Test successful strategy development request handling."""
        event = {"strategy_name": "Test Strategy"}
        
        with patch.object(agent, 'develop_strategy') as mock_develop:
            agent.handle_strategy_development_requested(event)
            mock_develop.assert_called_with("Test Strategy")


class TestStrategiePartnerAgentCLI:
    """Test suite for StrategiePartnerAgent CLI functionality."""

    @pytest.fixture
    def agent(self):
        """Create a StrategiePartnerAgent instance for CLI testing."""
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_performance_monitor'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_sprite_library'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.BMADTracer'):
            return StrategiePartnerAgent()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'help'])
    def test_cli_help_command(self, capsys):
        """Test CLI help command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        main()
        captured = capsys.readouterr()
        assert "StrategiePartner Agent Commands:" in captured.out

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'develop-strategy', '--strategy-name', 'Test Strategy'])
    def test_cli_develop_strategy_command(self, capsys):
        """Test CLI develop-strategy command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.develop_strategy.return_value = {"strategy_name": "Test Strategy", "status": "developed"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.develop_strategy.assert_called_with("Test Strategy")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'analyze-market', '--sector', 'Healthcare'])
    def test_cli_analyze_market_command(self, capsys):
        """Test CLI analyze-market command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.analyze_market.return_value = {"sector": "Healthcare", "market_size": "$1T"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.analyze_market.assert_called_with("Healthcare")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'competitive-analysis', '--competitor', 'Competitor A'])
    def test_cli_competitive_analysis_command(self, capsys):
        """Test CLI competitive-analysis command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.competitive_analysis.return_value = {"competitor": "Competitor A", "market_share": "30%"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.competitive_analysis.assert_called_with("Competitor A")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'assess-risks', '--strategy-name', 'Test Strategy'])
    def test_cli_assess_risks_command(self, capsys):
        """Test CLI assess-risks command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.assess_risks.return_value = {"strategy": "Test Strategy", "risk_score": "Medium"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.assess_risks.assert_called_with("Test Strategy")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'stakeholder-analysis', '--project', 'Test Project'])
    def test_cli_stakeholder_analysis_command(self, capsys):
        """Test CLI stakeholder-analysis command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.stakeholder_analysis.return_value = {"project": "Test Project", "stakeholders": {}}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.stakeholder_analysis.assert_called_with("Test Project")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'create-roadmap', '--strategy-name', 'Test Strategy'])
    def test_cli_create_roadmap_command(self, capsys):
        """Test CLI create-roadmap command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.create_roadmap.return_value = {"strategy": "Test Strategy", "total_duration": "12 months"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.create_roadmap.assert_called_with("Test Strategy")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'calculate-roi', '--strategy-name', 'Test Strategy'])
    def test_cli_calculate_roi_command(self, capsys):
        """Test CLI calculate-roi command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.calculate_roi.return_value = {"strategy": "Test Strategy", "roi_percentage": "75%"}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.calculate_roi.assert_called_with("Test Strategy")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'business-model-canvas'])
    def test_cli_business_model_canvas_command(self, capsys):
        """Test CLI business-model-canvas command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.business_model_canvas.return_value = {"key_partners": [], "customer_segments": []}
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.business_model_canvas.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'show-strategy-history'])
    def test_cli_show_strategy_history_command(self, capsys):
        """Test CLI show-strategy-history command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.show_strategy_history.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'show-market-data'])
    def test_cli_show_market_data_command(self, capsys):
        """Test CLI show-market-data command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.show_market_data.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'show-competitive-data'])
    def test_cli_show_competitive_data_command(self, capsys):
        """Test CLI show-competitive-data command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.show_competitive_data.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'show-risk-register'])
    def test_cli_show_risk_register_command(self, capsys):
        """Test CLI show-risk-register command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.show_risk_register.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'show-strategy-guide'])
    def test_cli_show_strategy_guide_command(self, capsys):
        """Test CLI show-strategy-guide command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.show_resource.assert_called_with("strategy-guide")

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'test'])
    def test_cli_test_command(self, capsys):
        """Test CLI test command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.test_resource_completeness.return_value = True
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.test_resource_completeness.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'collaborate'])
    def test_cli_collaborate_command(self, capsys):
        """Test CLI collaborate command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.collaborate_example.assert_called()

    @patch('sys.argv', ['test_strategiepartner_agent.py', 'run'])
    def test_cli_run_command(self, capsys):
        """Test CLI run command."""
        from bmad.agents.Agent.StrategiePartner.strategiepartner import main
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.StrategiePartnerAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            main()
            mock_agent.run.assert_called()


class TestStrategiePartnerAgentIntegration:
    """Integration tests for StrategiePartnerAgent."""

    @pytest.fixture
    def agent(self):
        """Create a StrategiePartnerAgent instance for integration testing."""
        with patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_performance_monitor'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.get_sprite_library'), \
             patch('bmad.agents.Agent.StrategiePartner.strategiepartner.BMADTracer'):
            return StrategiePartnerAgent()

    def test_complete_strategy_workflow(self, agent):
        """Test complete strategy workflow from development to ROI calculation."""
        # Develop strategy
        initial_strategy_count = len(agent.strategy_history)
        strategy_result = agent.develop_strategy("Digital Transformation Strategy")
        assert strategy_result["status"] == "developed"
        assert len(agent.strategy_history) == initial_strategy_count + 1

        # Analyze market
        initial_market_count = len(agent.market_data)
        market_result = agent.analyze_market("Technology")
        assert "market_size" in market_result
        assert len(agent.market_data) == initial_market_count + 1

        # Competitive analysis
        initial_competitive_count = len(agent.competitive_data)
        competitive_result = agent.competitive_analysis("Main Competitor")
        assert "market_share" in competitive_result
        assert len(agent.competitive_data) == initial_competitive_count + 1

        # Risk assessment
        initial_risk_count = len(agent.risk_register)
        risk_result = agent.assess_risks("Digital Transformation")
        assert "risk_score" in risk_result
        assert len(agent.risk_register) == initial_risk_count + 1

        # Stakeholder analysis
        stakeholder_result = agent.stakeholder_analysis("Digital Transformation Project")
        assert "stakeholders" in stakeholder_result

        # Create roadmap
        roadmap_result = agent.create_roadmap("Digital Transformation Strategy")
        assert "phases" in roadmap_result

        # Calculate ROI
        roi_result = agent.calculate_roi("Digital Transformation Strategy")
        assert "roi_percentage" in roi_result

        # Generate business model canvas
        canvas_result = agent.business_model_canvas()
        assert "customer_segments" in canvas_result

    def test_agent_resource_completeness(self, agent):
        """Test agent resource completeness."""
        with patch('pathlib.Path.exists', return_value=True):
            result = agent.test_resource_completeness()
            assert result is True

    def test_agent_error_handling_integration(self, agent, capsys):
        """Test agent error handling in integration scenarios."""
        # Test empty strategy name
        with pytest.raises(StrategyValidationError):
            agent.develop_strategy("")

        # Test empty sector
        with pytest.raises(StrategyValidationError):
            agent.analyze_market("")

        # Test empty competitor name
        with pytest.raises(StrategyValidationError):
            agent.competitive_analysis("")

        # Test empty project name
        with pytest.raises(StrategyValidationError):
            agent.stakeholder_analysis("")

    def test_agent_metrics_tracking(self, agent):
        """Test agent metrics tracking functionality."""
        with patch.object(agent, '_record_strategy_metric') as mock_record:
            agent.develop_strategy("Test Strategy")
            mock_record.assert_called()

            agent.analyze_market("Technology")
            mock_record.assert_called()

            agent.competitive_analysis("Competitor")
            mock_record.assert_called()

            agent.assess_risks("Test Strategy")
            mock_record.assert_called()

    def test_agent_event_handling_integration(self, agent):
        """Test agent event handling integration."""
        event = {"strategy_name": "Test Strategy", "status": "requested"}
        
        with patch.object(agent, 'develop_strategy') as mock_develop:
            agent.handle_strategy_development_requested(event)
            mock_develop.assert_called()

        with patch.object(agent.monitor, 'log_metric') as mock_log:
            agent.handle_alignment_check_completed(event)
            mock_log.assert_called() 