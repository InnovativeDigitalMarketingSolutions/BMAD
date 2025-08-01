import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.Agent.QualityGuardian.qualityguardian import (
    QualityGuardianAgent,
    QualityError,
    QualityValidationError
)
from bmad.agents.core.agent.agent_performance_monitor import MetricType


class TestQualityGuardianAgent:
    """Test suite for QualityGuardianAgent."""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test."""
        agent = QualityGuardianAgent()
        # Reset state for each test
        agent.quality_history = []
        agent.security_history = []
        agent.performance_history = []
        agent.quality_metrics = []
        agent.performance_metrics = {
            "quality_analyses_completed": 0,
            "security_scans_completed": 0,
            "performance_analyses_completed": 0,
            "quality_gates_passed": 0,
            "quality_gates_failed": 0,
            "quality_score": 0.0
        }
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_name == "QualityGuardian"
        assert agent.quality_thresholds["code_coverage"] == 80
        assert agent.quality_thresholds["complexity"] == 10
        assert agent.quality_thresholds["duplication"] == 5
        assert agent.quality_thresholds["security_score"] == 90
        assert agent.quality_thresholds["performance_score"] == 85

    def test_validate_input_success(self, agent):
        """Test successful input validation."""
        agent._validate_input("test", str, "test_param")
        agent._validate_input(42, int, "test_param")
        agent._validate_input(True, bool, "test_param")

    def test_validate_input_failure(self, agent):
        """Test input validation failure."""
        with pytest.raises(QualityValidationError, match="Invalid type for test_param"):
            agent._validate_input(42, str, "test_param")

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        agent.show_help()
        captured = capsys.readouterr()
        assert "QualityGuardian Agent Commands:" in captured.out
        assert "analyze-code-quality" in captured.out
        assert "monitor-test-coverage" in captured.out
        assert "security-scan" in captured.out
        assert "performance-analysis" in captured.out
        assert "enforce-standards" in captured.out
        assert "quality-gate-check" in captured.out

    def test_analyze_code_quality_success(self, agent):
        """Test successful code quality analysis."""
        result = agent.analyze_code_quality("./test_path")
        
        assert result["path"] == "./test_path"
        assert "code_quality_score" in result
        assert "complexity_score" in result
        assert "maintainability_index" in result
        assert "duplication_percentage" in result
        assert "code_smells" in result
        assert "technical_debt" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["code_quality_score"], int)
        assert isinstance(result["complexity_score"], float)

    def test_analyze_code_quality_empty_path(self, agent):
        """Test code quality analysis with empty path."""
        with pytest.raises(QualityValidationError, match="Path cannot be empty"):
            agent.analyze_code_quality("")

    def test_analyze_code_quality_invalid_path_type(self, agent):
        """Test code quality analysis with invalid path type."""
        with pytest.raises(QualityValidationError, match="Invalid type for path"):
            agent.analyze_code_quality(123)

    def test_monitor_test_coverage_success(self, agent):
        """Test successful test coverage monitoring."""
        result = agent.monitor_test_coverage(85)
        
        assert result["threshold"] == 85
        assert "current_coverage" in result
        assert "coverage_status" in result
        assert "missing_coverage" in result
        assert "uncovered_files" in result
        assert "coverage_trend" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["current_coverage"], float)

    def test_monitor_test_coverage_invalid_threshold(self, agent):
        """Test test coverage monitoring with invalid threshold."""
        with pytest.raises(QualityValidationError, match="Threshold must be between 0 and 100"):
            agent.monitor_test_coverage(150)

    def test_monitor_test_coverage_negative_threshold(self, agent):
        """Test test coverage monitoring with negative threshold."""
        with pytest.raises(QualityValidationError, match="Threshold must be between 0 and 100"):
            agent.monitor_test_coverage(-10)

    def test_security_scan_success(self, agent):
        """Test successful security scan."""
        result = agent.security_scan("*.py")
        
        assert result["files_pattern"] == "*.py"
        assert "security_score" in result
        assert "vulnerabilities_found" in result
        assert "critical_vulnerabilities" in result
        assert "high_vulnerabilities" in result
        assert "medium_vulnerabilities" in result
        assert "low_vulnerabilities" in result
        assert "vulnerability_details" in result
        assert "dependencies_checked" in result
        assert "outdated_dependencies" in result
        assert "security_recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["security_score"], int)

    def test_security_scan_empty_files(self, agent):
        """Test security scan with empty files pattern."""
        with pytest.raises(QualityValidationError, match="Files pattern cannot be empty"):
            agent.security_scan("")

    def test_security_scan_invalid_files_type(self, agent):
        """Test security scan with invalid files type."""
        with pytest.raises(QualityValidationError, match="Invalid type for files"):
            agent.security_scan(123)

    def test_performance_analysis_success(self, agent):
        """Test successful performance analysis."""
        result = agent.performance_analysis("test_component")
        
        assert result["component"] == "test_component"
        assert "performance_score" in result
        assert "response_time" in result
        assert "memory_usage" in result
        assert "cpu_usage" in result
        assert "bottlenecks" in result
        assert "optimization_opportunities" in result
        assert "performance_trend" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["performance_score"], int)

    def test_performance_analysis_empty_component(self, agent):
        """Test performance analysis with empty component."""
        with pytest.raises(QualityValidationError, match="Component cannot be empty"):
            agent.performance_analysis("")

    def test_performance_analysis_invalid_component_type(self, agent):
        """Test performance analysis with invalid component type."""
        with pytest.raises(QualityValidationError, match="Invalid type for component"):
            agent.performance_analysis(123)

    def test_enforce_standards_success(self, agent):
        """Test successful standards enforcement."""
        result = agent.enforce_standards("./test_path")
        
        assert result["path"] == "./test_path"
        assert "standards_enforced" in result
        assert "violations_found" in result
        assert "violations_details" in result
        assert "compliance_score" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["compliance_score"], float)
        assert isinstance(result["violations_found"], int)

    def test_enforce_standards_empty_path(self, agent):
        """Test standards enforcement with empty path."""
        with pytest.raises(QualityValidationError, match="Path cannot be empty"):
            agent.enforce_standards("")

    def test_enforce_standards_invalid_path_type(self, agent):
        """Test standards enforcement with invalid path type."""
        with pytest.raises(QualityValidationError, match="Invalid type for path"):
            agent.enforce_standards(123)

    def test_quality_gate_check_success(self, agent):
        """Test successful quality gate check."""
        result = agent.quality_gate_check(deployment=True)
        
        assert result["deployment"] is True
        assert "all_gates_passed" in result
        assert "quality_gates" in result
        assert "metrics" in result
        assert "thresholds" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["all_gates_passed"], bool)

    def test_quality_gate_check_invalid_deployment_type(self, agent):
        """Test quality gate check with invalid deployment type."""
        with pytest.raises(QualityValidationError, match="Invalid type for deployment"):
            agent.quality_gate_check("invalid")

    def test_generate_quality_report_success(self, agent):
        """Test successful quality report generation."""
        result = agent.generate_quality_report("md")
        
        assert result["format"] == "md"
        assert "report_data" in result
        assert "recommendations" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert "overall_quality_score" in result["report_data"]

    def test_generate_quality_report_invalid_format(self, agent):
        """Test quality report generation with invalid format."""
        with pytest.raises(QualityValidationError, match="Format type must be md, json, or csv"):
            agent.generate_quality_report("invalid")

    def test_generate_quality_report_invalid_format_type(self, agent):
        """Test quality report generation with invalid format type."""
        with pytest.raises(QualityValidationError, match="Invalid type for format_type"):
            agent.generate_quality_report(123)

    def test_suggest_improvements_success(self, agent):
        """Test successful improvement suggestions."""
        result = agent.suggest_improvements("code_quality")
        
        assert result["focus_area"] == "code_quality"
        assert "suggestions" in result
        assert "ai_confidence" in result
        assert "timestamp" in result
        assert result["agent"] == "QualityGuardianAgent"
        assert isinstance(result["ai_confidence"], float)
        assert len(result["suggestions"]) > 0

    def test_suggest_improvements_empty_focus_area(self, agent):
        """Test improvement suggestions with empty focus area."""
        with pytest.raises(QualityValidationError, match="Focus area cannot be empty"):
            agent.suggest_improvements("")

    def test_suggest_improvements_invalid_focus_area_type(self, agent):
        """Test improvement suggestions with invalid focus area type."""
        with pytest.raises(QualityValidationError, match="Invalid type for focus_area"):
            agent.suggest_improvements(123)

    def test_show_quality_history(self, agent, capsys):
        """Test show_quality_history method."""
        agent.quality_history = [
            "2025-01-31T09:16:59.595749: Code quality analysis for ./src - Score: 85, Complexity: 7.2",
            "2025-01-31T09:15:30.123456: Code quality analysis for ./tests - Score: 88, Complexity: 6.8"
        ]
        agent.show_quality_history()
        captured = capsys.readouterr()
        assert "Quality Analysis History" in captured.out
        assert "Score: 85" in captured.out
        assert "Score: 88" in captured.out
        assert "Total entries: 2" in captured.out

    def test_show_security_history(self, agent, capsys):
        """Test show_security_history method."""
        agent.security_history = [
            "2025-01-31T09:16:59.595749: Security scan for *.py - Score: 92, Vulnerabilities: 2",
            "2025-01-31T09:15:30.123456: Security scan for *.js - Score: 88, Vulnerabilities: 1"
        ]
        agent.show_security_history()
        captured = capsys.readouterr()
        assert "Security Scan History" in captured.out
        assert "Score: 92" in captured.out
        assert "Score: 88" in captured.out
        assert "Total entries: 2" in captured.out

    def test_show_performance_history(self, agent, capsys):
        """Test show_performance_history method."""
        agent.performance_history = [
            "2025-01-31T09:16:59.595749: Performance analysis for main - Score: 87, Response Time: 245ms",
            "2025-01-31T09:15:30.123456: Performance analysis for api - Score: 85, Response Time: 320ms"
        ]
        agent.show_performance_history()
        captured = capsys.readouterr()
        assert "Performance Analysis History" in captured.out
        assert "Score: 87" in captured.out
        assert "Score: 85" in captured.out
        assert "Total entries: 2" in captured.out

    def test_show_quality_metrics(self, agent, capsys):
        """Test show_quality_metrics method."""
        agent.quality_metrics = [
            "2025-01-31T09:16:59.595749: Test coverage monitoring - Current: 82.5%, Threshold: 80%, Status: PASS",
            "2025-01-31T09:15:30.123456: Quality gate check - Status: PASS, Score: 86.5%"
        ]
        agent.performance_metrics = {
            "quality_analyses_completed": 5,
            "security_scans_completed": 3,
            "performance_analyses_completed": 2,
            "quality_gates_passed": 8,
            "quality_gates_failed": 1,
            "quality_score": 87.5
        }
        agent.show_quality_metrics()
        captured = capsys.readouterr()
        assert "Quality Metrics" in captured.out
        assert "Current: 82.5%" in captured.out
        assert "Status: PASS" in captured.out
        assert "Quality analyses completed: 5" in captured.out
        assert "Security scans completed: 3" in captured.out
        assert "Overall quality score: 87.5" in captured.out

    def test_export_report_markdown(self, agent):
        """Test export report in markdown format."""
        report_data = {
            "overall_quality_score": 86.5,
            "code_quality": {"score": 85},
            "test_coverage": {"current": 82.5},
            "security": {"score": 92},
            "performance": {"score": 87}
        }
        
        with patch('builtins.open', create=True) as mock_open:
            agent.export_report("md", report_data)
            mock_open.assert_called_once()
            call_args = mock_open.call_args[0]
            assert call_args[0].endswith(".md")

    def test_export_report_json(self, agent):
        """Test export report in JSON format."""
        report_data = {
            "overall_quality_score": 86.5,
            "code_quality": {"score": 85},
            "test_coverage": {"current": 82.5},
            "security": {"score": 92},
            "performance": {"score": 87}
        }
        
        with patch('builtins.open', create=True) as mock_open:
            agent.export_report("json", report_data)
            mock_open.assert_called_once()
            call_args = mock_open.call_args[0]
            assert call_args[0].endswith(".json")

    def test_export_report_csv(self, agent):
        """Test export report in CSV format."""
        report_data = {
            "overall_quality_score": 86.5,
            "code_quality": {"score": 85},
            "test_coverage": {"current": 82.5},
            "security": {"score": 92},
            "performance": {"score": 87}
        }
        
        with patch('builtins.open', create=True) as mock_open:
            agent.export_report("csv", report_data)
            mock_open.assert_called_once()
            call_args = mock_open.call_args[0]
            assert call_args[0].endswith(".csv")

    def test_test_resource_completeness(self, agent, capsys):
        """Test test_resource_completeness method."""
        with patch('pathlib.Path.exists', return_value=True):
            agent.test_resource_completeness()
            captured = capsys.readouterr()
            assert "Testing Resource Completeness" in captured.out
            assert "Template found:" in captured.out
            assert "Data file found:" in captured.out

    def test_collaborate_example(self, agent, capsys):
        """Test collaborate_example method."""
        import asyncio
        asyncio.run(agent.collaborate_example())
        captured = capsys.readouterr()
        assert "QualityGuardian Agent Collaboration Example" in captured.out
        assert "Collaborating with TestEngineer Agent" in captured.out
        assert "Collaborating with SecurityDeveloper Agent" in captured.out
        assert "Collaborating with ReleaseManager Agent" in captured.out
        assert "Async collaboration example completed successfully" in captured.out

    def test_on_test_completed(self, agent):
        """Test on_test_completed event handler."""
        event = {"type": "test_completed", "data": "test_data"}
        with patch.object(agent, 'monitor_test_coverage') as mock_monitor:
            agent.on_test_completed(event)
            mock_monitor.assert_called_once()

    def test_on_security_scan_completed(self, agent):
        """Test on_security_scan_completed event handler."""
        event = {"type": "security_scan_completed", "data": "test_data"}
        with patch.object(agent, 'security_scan') as mock_scan:
            agent.on_security_scan_completed(event)
            mock_scan.assert_called_once()

    def test_on_deployment_requested_success(self, agent):
        """Test on_deployment_requested event handler with successful gates."""
        event = {"type": "deployment_requested", "data": "test_data"}
        with patch.object(agent, 'quality_gate_check', return_value={"all_gates_passed": True}):
            with patch('bmad.agents.Agent.QualityGuardian.qualityguardian.publish') as mock_publish:
                agent.on_deployment_requested(event)
                mock_publish.assert_called_once_with("quality_gates_passed", {"result": {"all_gates_passed": True}})

    def test_on_deployment_requested_failure(self, agent):
        """Test on_deployment_requested event handler with failed gates."""
        event = {"type": "deployment_requested", "data": "test_data"}
        with patch.object(agent, 'quality_gate_check', return_value={"all_gates_passed": False}):
            with patch('bmad.agents.Agent.QualityGuardian.qualityguardian.publish') as mock_publish:
                agent.on_deployment_requested(event)
                mock_publish.assert_called_once_with("quality_gates_failed", {"reason": "Quality thresholds not met"})

    def test_run_method(self, agent, capsys):
        """Test run method."""
        with patch('bmad.agents.Agent.QualityGuardian.qualityguardian.subscribe') as mock_subscribe:
            agent.run()
            captured = capsys.readouterr()
            assert "Starting QualityGuardian Agent" in captured.out
            assert "QualityGuardian Agent is running and listening for events" in captured.out
            assert mock_subscribe.call_count == 3  # Three event subscriptions

    def test_record_quality_metric(self, agent):
        """Test _record_quality_metric method."""
        with patch.object(agent.monitor, '_record_metric') as mock_record:
            agent._record_quality_metric("test_metric", 95.5, "%")
            mock_record.assert_called_once_with("QualityGuardian", MetricType.SUCCESS_RATE, 95.5, "%")

    def test_record_quality_metric_exception(self, agent):
        """Test _record_quality_metric method with exception."""
        with patch.object(agent.monitor, '_record_metric', side_effect=Exception("Test error")):
            # Should not raise exception, just log warning
            agent._record_quality_metric("test_metric", 95.5, "%")

    def test_load_quality_history_file_not_exists(self, agent):
        """Test _load_quality_history when file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            agent._load_quality_history()
            assert len(agent.quality_history) == 0

    def test_load_quality_history_file_exists(self, agent):
        """Test _load_quality_history when file exists."""
        test_content = "# Quality History\n\n- Test entry 1\n- Test entry 2"
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=test_content)):
                agent._load_quality_history()
                assert len(agent.quality_history) == 2
                assert "Test entry 1" in agent.quality_history[0]
                assert "Test entry 2" in agent.quality_history[1]

    def test_save_quality_history(self, agent):
        """Test _save_quality_history method."""
        agent.quality_history = ["Test entry 1", "Test entry 2"]
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                agent._save_quality_history()
                mock_mkdir.assert_called_once()
                mock_open.assert_called_once()

    def test_save_quality_history_exception(self, agent):
        """Test _save_quality_history method with exception."""
        agent.quality_history = ["Test entry 1"]
        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', side_effect=Exception("Test error")):
                # Should not raise exception, just log error
                agent._save_quality_history()

    def test_show_resource_existing(self, agent, capsys):
        """Test show_resource with existing resource."""
        test_content = "# Test Resource\n\nThis is test content."
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=test_content)):
                agent.show_resource("best-practices")
                captured = capsys.readouterr()
                assert "BEST-PRACTICES" in captured.out
                assert "This is test content." in captured.out

    def test_show_resource_not_exists(self, agent, capsys):
        """Test show_resource with non-existing resource."""
        with patch('pathlib.Path.exists', return_value=False):
            agent.show_resource("best-practices")
            captured = capsys.readouterr()
            assert "Resource file not found:" in captured.out

    def test_show_resource_unknown_type(self, agent, capsys):
        """Test show_resource with unknown resource type."""
        agent.show_resource("unknown_resource")
        captured = capsys.readouterr()
        assert "Unknown resource type: unknown_resource" in captured.out
        assert "Available resources:" in captured.out

    def test_show_resource_invalid_type(self, agent):
        """Test show_resource with invalid resource type."""
        with pytest.raises(QualityValidationError, match="Invalid type for resource_type"):
            agent.show_resource(123)


# Mock for builtins.open
class mock_open:
    def __init__(self, read_data="", side_effect=None):
        self.read_data = read_data
        self.side_effect = side_effect

    def __call__(self, *args, **kwargs):
        if self.side_effect:
            raise self.side_effect
        return MagicMock(read=lambda: self.read_data, __enter__=lambda self: self, __exit__=lambda self, *args: None) 