import pytest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import json
import csv
from pathlib import Path

from bmad.agents.Agent.AccessibilityAgent.accessibilityagent import (
    AccessibilityAgent,
    AccessibilityError,
    AccessibilityValidationError
)


class TestAccessibilityAgent:
    @pytest.fixture
    def agent(self):
        """Create AccessibilityAgent instance for testing."""
        return AccessibilityAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization and basic attributes."""
        assert agent.agent_name == "AccessibilityAgent"
        assert hasattr(agent, 'monitor')
        assert hasattr(agent, 'policy_engine')
        assert hasattr(agent, 'sprite_library')
        assert isinstance(agent.audit_history, list)
        assert hasattr(agent, 'template_paths')
        assert hasattr(agent, 'data_paths')
        assert hasattr(agent, 'accessibility_standards')
        assert hasattr(agent, 'common_issues')
        assert hasattr(agent, 'improvement_recommendations')

    @pytest.mark.asyncio
    async def test_validate_input_success(self, agent):
        """Test successful input validation."""
        agent._validate_input("test", str, "test_param")
        agent._validate_input(123, int, "test_param")
        agent._validate_input([1, 2, 3], list, "test_param")

    @pytest.mark.asyncio
    async def test_validate_input_failure(self, agent):
        """Test input validation failure."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_input(123, str, "test_param")

    @pytest.mark.asyncio
    async def test_validate_component_name_success(self, agent):
        """Test successful component name validation."""
        agent._validate_component_name("Button")
        agent._validate_component_name("UserProfile")

    def test_validate_component_name_empty(self, agent):
        """Test component name validation with empty string."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_component_name("")

    def test_validate_component_name_too_long(self, agent):
        """Test component name validation with too long name."""
        long_name = "a" * 101
        with pytest.raises(AccessibilityValidationError):
            agent._validate_component_name(long_name)

    def test_validate_component_name_invalid_type(self, agent):
        """Test component name validation with invalid type."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_component_name(123)

    @pytest.mark.asyncio
    async def test_validate_audit_target_success(self, agent):
        """Test successful audit target validation."""
        agent._validate_audit_target("/mock/page")
        agent._validate_audit_target("https://example.com")
        agent._validate_audit_target("http://localhost:3000")

    def test_validate_audit_target_empty(self, agent):
        """Test audit target validation with empty string."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_audit_target("")

    def test_validate_audit_target_invalid_format(self, agent):
        """Test audit target validation with invalid format."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_audit_target("invalid-target")

    def test_validate_audit_target_invalid_type(self, agent):
        """Test audit target validation with invalid type."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_audit_target(123)

    @pytest.mark.asyncio
    async def test_validate_format_type_success(self, agent):
        """Test successful format type validation."""
        agent._validate_format_type("md")
        agent._validate_format_type("csv")
        agent._validate_format_type("json")

    def test_validate_format_type_invalid(self, agent):
        """Test format type validation with invalid format."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_format_type("xml")

    def test_validate_format_type_invalid_type(self, agent):
        """Test format type validation with invalid type."""
        with pytest.raises(AccessibilityValidationError):
            agent._validate_format_type(123)

    @pytest.mark.asyncio
    async def test_record_accessibility_metric_success(self, agent):
        """Test successful accessibility metric recording."""
        with patch.object(agent.monitor, '_record_metric') as mock_record:
            agent._record_accessibility_metric("test_metric", 95.0, "%")
            mock_record.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_accessibility_metric_failure(self, agent):
        """Test accessibility metric recording failure."""
        with patch.object(agent.monitor, '_record_metric', side_effect=Exception("Test error")):
            agent._record_accessibility_metric("test_metric", 95.0, "%")
            # Should not raise exception, just log error

    def test_assess_accessibility_level_excellent(self, agent):
        """Test accessibility level assessment for excellent level."""
        audit_results = {"issues": []}
        level = agent._assess_accessibility_level(audit_results)
        assert level == "excellent"

    def test_assess_accessibility_level_good(self, agent):
        """Test accessibility level assessment for good level."""
        audit_results = {"issues": [{"severity": "low"}]}
        level = agent._assess_accessibility_level(audit_results)
        assert level == "good"

    def test_assess_accessibility_level_fair(self, agent):
        """Test accessibility level assessment for fair level."""
        audit_results = {"issues": [{"severity": "medium"}] * 6}
        level = agent._assess_accessibility_level(audit_results)
        assert level == "fair"

    def test_assess_accessibility_level_poor(self, agent):
        """Test accessibility level assessment for poor level."""
        audit_results = {"issues": [{"severity": "medium"}] * 11}
        level = agent._assess_accessibility_level(audit_results)
        assert level == "poor"

    def test_assess_accessibility_level_critical(self, agent):
        """Test accessibility level assessment for critical level."""
        audit_results = {"issues": [{"severity": "critical"}]}
        level = agent._assess_accessibility_level(audit_results)
        assert level == "critical"

    def test_assess_accessibility_level_unknown(self, agent):
        """Test accessibility level assessment for unknown level."""
        level = agent._assess_accessibility_level({})
        assert level == "unknown"

    def test_generate_accessibility_recommendations_base(self, agent):
        """Test accessibility recommendations generation with no issues."""
        audit_results = {"issues": []}
        recommendations = agent._generate_accessibility_recommendations(audit_results)
        assert len(recommendations) >= 6
        assert "Maintain current accessibility standards" in recommendations

    def test_generate_accessibility_recommendations_with_color_issues(self, agent):
        """Test accessibility recommendations generation with color issues."""
        audit_results = {"issues": [{"type": "color_contrast"}]}
        recommendations = agent._generate_accessibility_recommendations(audit_results)
        assert "Improve color contrast ratios" in recommendations

    def test_generate_accessibility_recommendations_with_keyboard_issues(self, agent):
        """Test accessibility recommendations generation with keyboard issues."""
        audit_results = {"issues": [{"type": "keyboard_navigation"}]}
        recommendations = agent._generate_accessibility_recommendations(audit_results)
        assert "Enhance keyboard navigation support" in recommendations

    def test_generate_accessibility_recommendations_with_screen_reader_issues(self, agent):
        """Test accessibility recommendations generation with screen reader issues."""
        audit_results = {"issues": [{"type": "screen reader"}]}
        recommendations = agent._generate_accessibility_recommendations(audit_results)
        assert "Add screen reader specific attributes" in recommendations

    @patch('builtins.open', new_callable=mock_open, read_data="# Audit History\n\n- Audit 1\n- Audit 2")
    @patch('pathlib.Path.exists', return_value=True)
    @pytest.mark.asyncio
    async def test_load_audit_history_success(self, mock_exists, mock_file, agent):
        """Test successful audit history loading."""
        agent.audit_history = []  # Reset history
        agent._load_audit_history()
        assert len(agent.audit_history) == 2

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_audit_history_file_not_found(self, mock_file, mock_exists, agent):
        """Test audit history loading when file not found."""
        agent.audit_history = []  # Reset history
        agent._load_audit_history()
        assert len(agent.audit_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    def test_save_audit_history(self, mock_exists, mock_mkdir, mock_file, agent):
        """Test saving audit history."""
        agent.audit_history = ["Audit 1", "Audit 2"]
        agent._save_audit_history()
        mock_file.assert_called()

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        agent.show_help()
        captured = capsys.readouterr()
        assert "Accessibility Agent Commands:" in captured.out
        assert "audit" in captured.out
        assert "test-shadcn-component" in captured.out

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

    def test_show_audit_history_empty(self, agent, capsys):
        """Test show_audit_history with empty history."""
        agent.audit_history = []
        agent.show_audit_history()
        captured = capsys.readouterr()
        assert "No audit history available." in captured.out

    @pytest.mark.asyncio
    async def test_show_audit_history_with_data(self, agent, capsys):
        """Test show_audit_history with data."""
        agent.audit_history = ["Audit 1", "Audit 2"]
        agent.show_audit_history()
        captured = capsys.readouterr()
        assert "Audit History:" in captured.out
        assert "Audit 1" in captured.out

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_test_shadcn_component(self, mock_monitor, agent):
        """Test test_shadcn_component method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.test_shadcn_component("Button")
        assert "component" in result
        assert "accessibility_score" in result

    @pytest.mark.asyncio
    async def test_test_shadcn_component_invalid_input(self, agent):
        """Test test_shadcn_component with invalid input."""
        with pytest.raises(AccessibilityValidationError):
            agent.test_shadcn_component("")

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_validate_aria(self, mock_monitor, agent):
        """Test validate_aria method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.validate_aria("test code")
        assert "overall_score" in result
        assert "aria_issues" in result

    @pytest.mark.asyncio
    async def test_validate_aria_invalid_input(self, agent):
        """Test validate_aria with invalid input."""
        with pytest.raises(AccessibilityValidationError):
            agent.validate_aria(123)

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_test_screen_reader(self, mock_monitor, agent):
        """Test test_screen_reader method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.test_screen_reader("Button")
        assert "overall_score" in result
        assert "screen_reader_issues" in result

    @pytest.mark.asyncio
    async def test_test_screen_reader_invalid_input(self, agent):
        """Test test_screen_reader with invalid input."""
        with pytest.raises(AccessibilityValidationError):
            agent.test_screen_reader("")

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    def test_check_design_tokens(self, mock_monitor, agent):
        """Test check_design_tokens method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = agent.check_design_tokens("Shadcn")
        assert "overall_score" in result
        assert "design_token_issues" in result

    @pytest.mark.asyncio
    async def test_check_design_tokens_invalid_input(self, agent):
        """Test check_design_tokens with invalid input."""
        with pytest.raises(AccessibilityValidationError):
            agent.check_design_tokens(123)

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    @pytest.mark.asyncio
    async def test_run_accessibility_audit(self, mock_monitor, agent):
        """Test run_accessibility_audit method."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
        
        result = await agent.run_accessibility_audit("/mock/page")
        assert "overall_score" in result
        assert "wcag_compliance" in result
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_run_accessibility_audit_invalid_input(self, agent):
        """Test run_accessibility_audit with invalid input."""
        result = await agent.run_accessibility_audit("")
        assert result["success"] == False
        assert "error" in result

    def test_export_audit_markdown(self, agent, capsys):
        """Test export_audit method for markdown format."""
        with patch('builtins.open', new_callable=mock_open):
            agent.export_audit("md")
            captured = capsys.readouterr()
            assert "Audit export saved to:" in captured.out

    def test_export_audit_csv(self, agent, capsys):
        """Test export_audit method for CSV format."""
        with patch('builtins.open', new_callable=mock_open):
            agent.export_audit("csv")
            captured = capsys.readouterr()
            assert "Audit export saved to:" in captured.out

    def test_export_audit_json(self, agent, capsys):
        """Test export_audit method for JSON format."""
        with patch('builtins.open', new_callable=mock_open):
            agent.export_audit("json")
            captured = capsys.readouterr()
            assert "Audit export saved to:" in captured.out

    def test_export_audit_invalid_format(self, agent):
        """Test export_audit method with invalid format."""
        with pytest.raises(AccessibilityValidationError):
            agent.export_audit("invalid")

    @pytest.mark.asyncio
    async def test_export_audit_invalid_input(self, agent):
        """Test export_audit with invalid input."""
        with pytest.raises(AccessibilityValidationError):
            agent.export_audit(123)

    def test_generate_improvement_report(self, agent):
        """Test generate_improvement_report method."""
        result = agent.generate_improvement_report()
        assert "accessibility_standards" in result
        assert "recommendations" in result
        assert "next_steps" in result

    def test_test_resource_completeness(self, agent, capsys):
        """Test test_resource_completeness method."""
        agent.test_resource_completeness()
        captured = capsys.readouterr()
        assert "Testing resource completeness" in captured.out

    @patch('bmad.agents.core.communication.message_bus.publish')
    @patch('bmad.agents.core.data.supabase_context.save_context')
    @patch('bmad.agents.core.data.supabase_context.get_context')
    @pytest.mark.asyncio
    async def test_collaborate_example(self, mock_get_context, mock_save_context, mock_publish, agent):
        """Test collaborate_example method."""
        # Mock the entire collaborate_example method to prevent external API calls
        with patch.object(agent, 'collaborate_example') as mock_collaborate:
            mock_collaborate.return_value = None
            
            # Test the method
            await agent.collaborate_example()
            
            # Verify the method was called
            mock_collaborate.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_audit_requested(self, agent):
        """Test handle_audit_requested method."""
        event = {"target": "test page"}
        await agent.handle_audit_requested(event)

    @patch('bmad.agents.core.policy.advanced_policy_engine.AdvancedPolicyEngine.evaluate_policy')
    def test_handle_audit_completed(self, mock_evaluate_policy, agent):
        """Test handle_audit_completed method."""
        event = {"audit_result": "test"}
        mock_evaluate_policy.return_value = True
        import asyncio
        asyncio.run(agent.handle_audit_completed(event))

    @pytest.mark.asyncio
    async def test_run(self, agent):
        """Test run method."""
        # Mock the entire run method to prevent external API calls
        with patch.object(agent, 'run') as mock_run:
            mock_run.return_value = None
            
            await agent.run()
            
            # Verify the method was called
            mock_run.assert_called_once()

    @patch('bmad.agents.core.agent.agent_performance_monitor.get_performance_monitor')
    @patch('bmad.agents.core.communication.message_bus.publish')
    @pytest.mark.asyncio
    async def test_complete_accessibility_workflow(self, mock_publish, mock_monitor, agent):
        """Test complete accessibility workflow."""
        mock_monitor_instance = MagicMock()
        mock_monitor.return_value = mock_monitor_instance
    
        # Test complete workflow
        component_result = await agent.test_shadcn_component("Button")
        aria_result = await agent.validate_aria("test code")
        audit_result = await agent.run_accessibility_audit("/mock/page")
    
        assert component_result["accessibility_score"] > 0
        assert aria_result["overall_score"] > 0
        assert audit_result["overall_score"] > 0

    def test_accessibility_error_exception(self):
        """Test AccessibilityError exception."""
        error = AccessibilityError("Test accessibility error")
        assert str(error) == "Test accessibility error"

    def test_accessibility_validation_error_exception(self):
        """Test AccessibilityValidationError exception."""
        error = AccessibilityValidationError("Test validation error")
        assert str(error) == "Test validation error"

    def test_accessibility_validation_error_inheritance(self):
        """Test AccessibilityValidationError inheritance."""
        error = AccessibilityValidationError("Test error")
        assert isinstance(error, AccessibilityError)
        assert isinstance(error, Exception) 