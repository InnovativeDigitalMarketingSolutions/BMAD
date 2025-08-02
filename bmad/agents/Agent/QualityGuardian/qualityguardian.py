import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_slack_message
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager


# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class QualityError(Exception):
    """Custom exception for quality-related errors."""
    pass

class QualityValidationError(QualityError):
    """Exception for quality validation failures."""
    pass

class QualityGuardianAgent:
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        self.quality_guardian_template = self.framework_manager.get_template('quality_guardian')
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "QualityGuardian"
        
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/qualityguardian/best-practices.md",
            "quality-analysis": self.resource_base / "templates/qualityguardian/quality-analysis.md",
            "security-scan": self.resource_base / "templates/qualityguardian/security-scan.md",
            "performance-analysis": self.resource_base / "templates/qualityguardian/performance-analysis.md",
            "quality-gate": self.resource_base / "templates/qualityguardian/quality-gate.md",
            "quality-report": self.resource_base / "templates/qualityguardian/quality-report.md",
            "improvement-suggestions": self.resource_base / "templates/qualityguardian/improvement-suggestions.md",
            "standards-enforcement": self.resource_base / "templates/qualityguardian/standards-enforcement.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/qualityguardian/changelog.md",
            "quality-history": self.resource_base / "data/qualityguardian/quality-history.md",
            "security-history": self.resource_base / "data/qualityguardian/security-history.md",
            "performance-history": self.resource_base / "data/qualityguardian/performance-history.md",
            "quality-metrics": self.resource_base / "data/qualityguardian/quality-metrics.md"
        }

        # Initialize histories
        self.quality_history = []
        self.security_history = []
        self.performance_history = []
        self.quality_metrics = []
        self._load_quality_history()
        self._load_security_history()
        self._load_performance_history()
        self._load_quality_metrics()

        # Quality thresholds
        self.quality_thresholds = {
            "code_coverage": 80,
            "complexity": 10,
            "duplication": 5,
            "security_score": 90,
            "performance_score": 85
        }

        # Performance metrics
        self.performance_metrics = {
            "quality_analyses_completed": 0,
            "security_scans_completed": 0,
            "performance_analyses_completed": 0,
            "quality_gates_passed": 0,
            "quality_gates_failed": 0,
            "quality_score": 0.0
        }

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise QualityValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _load_quality_history(self):
        """Load quality history from data file"""
        try:
            if self.data_paths["quality-history"].exists():
                with open(self.data_paths["quality-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.quality_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load quality history: {e}")

    def _save_quality_history(self):
        """Save quality history to data file"""
        try:
            self.data_paths["quality-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["quality-history"], "w") as f:
                f.write("# Quality History\n\n")
                for quality in self.quality_history[-50:]:  # Keep last 50 entries
                    f.write(f"- {quality}\n")
        except Exception as e:
            logger.error(f"Could not save quality history: {e}")

    def _load_security_history(self):
        """Load security history from data file"""
        try:
            if self.data_paths["security-history"].exists():
                with open(self.data_paths["security-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.security_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load security history: {e}")

    def _save_security_history(self):
        """Save security history to data file"""
        try:
            self.data_paths["security-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["security-history"], "w") as f:
                f.write("# Security History\n\n")
                for security in self.security_history[-50:]:  # Keep last 50 entries
                    f.write(f"- {security}\n")
        except Exception as e:
            logger.error(f"Could not save security history: {e}")

    def _load_performance_history(self):
        """Load performance history from data file"""
        try:
            if self.data_paths["performance-history"].exists():
                with open(self.data_paths["performance-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.performance_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        """Save performance history to data file"""
        try:
            self.data_paths["performance-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["performance-history"], "w") as f:
                f.write("# Performance History\n\n")
                for performance in self.performance_history[-50:]:  # Keep last 50 entries
                    f.write(f"- {performance}\n")
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def _load_quality_metrics(self):
        """Load quality metrics from data file"""
        try:
            if self.data_paths["quality-metrics"].exists():
                with open(self.data_paths["quality-metrics"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.quality_metrics.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load quality metrics: {e}")

    def _save_quality_metrics(self):
        """Save quality metrics to data file"""
        try:
            self.data_paths["quality-metrics"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["quality-metrics"], "w") as f:
                f.write("# Quality Metrics\n\n")
                for metric in self.quality_metrics[-50:]:  # Keep last 50 entries
                    f.write(f"- {metric}\n")
        except Exception as e:
            logger.error(f"Could not save quality metrics: {e}")

    def _record_quality_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record quality-specific metrics."""
        try:
            self.monitor._record_metric(self.agent_name, MetricType.SUCCESS_RATE, value, unit)
        except Exception as e:
            logger.warning(f"Could not record metric {metric_name}: {e}")

    def show_help(self):
        """Show available QualityGuardian Agent commands."""
        help_text = """
QualityGuardian Agent Commands:
  help                    - Show this help message
  analyze-code-quality    - Analyze code quality and complexity
  monitor-test-coverage   - Monitor test coverage trends
  security-scan          - Perform security vulnerability scan
  performance-analysis   - Analyze code performance
  enforce-standards      - Enforce coding standards
  quality-gate-check     - Check quality gates for deployment
  generate-quality-report - Generate comprehensive quality report
  suggest-improvements   - AI-powered improvement suggestions
  show-quality-metrics   - Show quality metrics and trends
  show-quality-history   - Show quality analysis history
  show-security-history  - Show security scan history
  show-performance-history - Show performance analysis history
  test                   - Test resource completeness
  collaborate            - Demonstrate collaboration with other agents
  run                    - Start the agent in event listening mode
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show a specific resource file."""
        try:
            self._validate_input(resource_type, str, "resource_type")
            
            if resource_type in self.template_paths:
                if self.template_paths[resource_type].exists():
                    with open(self.template_paths[resource_type]) as f:
                        print(f"=== {resource_type.upper()} ===\n")
                        print(f.read())
                else:
                    print(f"Resource file not found: {self.template_paths[resource_type]}")
            else:
                print(f"Unknown resource type: {resource_type}")
                print("Available resources:", list(self.template_paths.keys()))
                
        except QualityValidationError as e:
            logger.error(f"Validation error showing resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error showing resource: {e}")
            raise QualityError(f"Failed to show resource: {e}")

    def analyze_code_quality(self, path: str = "./") -> Dict[str, Any]:
        """Analyze code quality with comprehensive validation and error handling."""
        try:
            self._validate_input(path, str, "path")
            
            if not path.strip():
                raise QualityValidationError("Path cannot be empty")
            
            logger.info(f"Analyzing code quality for path: {path}")

            # Simulate code quality analysis process
            time.sleep(1)
            
            result = {
                "path": path,
                "code_quality_score": 85,
                "complexity_score": 7.2,
                "maintainability_index": 78,
                "duplication_percentage": 3.5,
                "code_smells": ["Long method", "Complex condition"],
                "technical_debt": "Low",
                "recommendations": [
                    "Refactor long methods",
                    "Simplify complex conditions",
                    "Add more unit tests"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Add to history
            quality_entry = f"{result['timestamp']}: Code quality analysis for {path} - Score: {result['code_quality_score']}, Complexity: {result['complexity_score']}"
            self.quality_history.append(quality_entry)
            self._save_quality_history()

            # Update metrics
            self.performance_metrics["quality_analyses_completed"] += 1
            self.performance_metrics["quality_score"] = result["code_quality_score"]
            self._record_quality_metric("code_quality_analysis_success", 95, "%")

            logger.info(f"Code quality analysis result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error analyzing code quality: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            self._record_quality_metric("code_quality_analysis_error", 5, "%")
            raise QualityError(f"Failed to analyze code quality: {e}")

    def monitor_test_coverage(self, threshold: int = 80) -> Dict[str, Any]:
        """Monitor test coverage with comprehensive validation and error handling."""
        try:
            self._validate_input(threshold, int, "threshold")
            
            if threshold < 0 or threshold > 100:
                raise QualityValidationError("Threshold must be between 0 and 100")
            
            logger.info(f"Monitoring test coverage with threshold: {threshold}%")

            # Simulate test coverage monitoring process
            time.sleep(1)
            
            result = {
                "threshold": threshold,
                "current_coverage": 82.5,
                "coverage_status": "PASS" if 82.5 >= threshold else "FAIL",
                "missing_coverage": 17.5,
                "uncovered_files": ["utils/helper.py", "models/user.py"],
                "coverage_trend": "Improving",
                "recommendations": [
                    "Add tests for utils/helper.py",
                    "Increase coverage for models/user.py",
                    "Focus on critical path testing"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Add to metrics
            metric_entry = f"{result['timestamp']}: Test coverage monitoring - Current: {result['current_coverage']}%, Threshold: {threshold}%, Status: {result['coverage_status']}"
            self.quality_metrics.append(metric_entry)
            self._save_quality_metrics()

            # Update metrics
            self._record_quality_metric("test_coverage_monitoring_success", 92, "%")

            logger.info(f"Test coverage monitoring result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error monitoring test coverage: {e}")
            raise
        except Exception as e:
            logger.error(f"Error monitoring test coverage: {e}")
            self._record_quality_metric("test_coverage_monitoring_error", 8, "%")
            raise QualityError(f"Failed to monitor test coverage: {e}")

    def security_scan(self, files: str = "*.py") -> Dict[str, Any]:
        """Perform security scan with comprehensive validation and error handling."""
        try:
            self._validate_input(files, str, "files")
            
            if not files.strip():
                raise QualityValidationError("Files pattern cannot be empty")
            
            logger.info(f"Performing security scan for files: {files}")

            # Simulate security scan process
            time.sleep(1)
            
            result = {
                "files_pattern": files,
                "security_score": 92,
                "vulnerabilities_found": 2,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 1,
                "medium_vulnerabilities": 1,
                "low_vulnerabilities": 0,
                "vulnerability_details": [
                    {
                        "severity": "High",
                        "type": "SQL Injection",
                        "file": "database/query.py",
                        "line": 45,
                        "description": "Potential SQL injection vulnerability"
                    }
                ],
                "dependencies_checked": 15,
                "outdated_dependencies": 2,
                "security_recommendations": [
                    "Update outdated dependencies",
                    "Fix SQL injection vulnerability",
                    "Implement input validation"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Add to history
            security_entry = f"{result['timestamp']}: Security scan for {files} - Score: {result['security_score']}, Vulnerabilities: {result['vulnerabilities_found']}"
            self.security_history.append(security_entry)
            self._save_security_history()

            # Update metrics
            self.performance_metrics["security_scans_completed"] += 1
            self._record_quality_metric("security_scan_success", 88, "%")

            logger.info(f"Security scan result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error performing security scan: {e}")
            raise
        except Exception as e:
            logger.error(f"Error performing security scan: {e}")
            self._record_quality_metric("security_scan_error", 12, "%")
            raise QualityError(f"Failed to perform security scan: {e}")

    def performance_analysis(self, component: str = "main") -> Dict[str, Any]:
        """Analyze performance with comprehensive validation and error handling."""
        try:
            self._validate_input(component, str, "component")
            
            if not component.strip():
                raise QualityValidationError("Component cannot be empty")
            
            logger.info(f"Analyzing performance for component: {component}")

            # Simulate performance analysis process
            time.sleep(1)
            
            result = {
                "component": component,
                "performance_score": 87,
                "response_time": 245,  # milliseconds
                "memory_usage": 45.2,  # MB
                "cpu_usage": 12.5,     # percentage
                "bottlenecks": ["Database queries", "File I/O"],
                "optimization_opportunities": [
                    "Implement caching",
                    "Optimize database queries",
                    "Use async operations"
                ],
                "performance_trend": "Stable",
                "recommendations": [
                    "Add database connection pooling",
                    "Implement request caching",
                    "Optimize file operations"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Add to history
            performance_entry = f"{result['timestamp']}: Performance analysis for {component} - Score: {result['performance_score']}, Response Time: {result['response_time']}ms"
            self.performance_history.append(performance_entry)
            self._save_performance_history()

            # Update metrics
            self.performance_metrics["performance_analyses_completed"] += 1
            self._record_quality_metric("performance_analysis_success", 90, "%")

            logger.info(f"Performance analysis result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error analyzing performance: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            self._record_quality_metric("performance_analysis_error", 10, "%")
            raise QualityError(f"Failed to analyze performance: {e}")

    def quality_gate_check(self, deployment: bool = False) -> Dict[str, Any]:
        """Check quality gates with comprehensive validation and error handling."""
        try:
            self._validate_input(deployment, bool, "deployment")
            
            logger.info(f"Checking quality gates (deployment: {deployment})")

            # Simulate quality gate check process
            time.sleep(1)
            
            # Simulate quality metrics
            code_quality_score = 85
            test_coverage = 82.5
            security_score = 92
            performance_score = 87
            
            # Check against thresholds
            quality_gates = {
                "code_quality": code_quality_score >= self.quality_thresholds["code_coverage"],
                "test_coverage": test_coverage >= self.quality_thresholds["code_coverage"],
                "security": security_score >= self.quality_thresholds["security_score"],
                "performance": performance_score >= self.quality_thresholds["performance_score"]
            }
            
            all_gates_passed = all(quality_gates.values())
            
            result = {
                "deployment": deployment,
                "all_gates_passed": all_gates_passed,
                "quality_gates": quality_gates,
                "metrics": {
                    "code_quality_score": code_quality_score,
                    "test_coverage": test_coverage,
                    "security_score": security_score,
                    "performance_score": performance_score
                },
                "thresholds": self.quality_thresholds,
                "recommendations": [
                    "Improve test coverage to meet threshold",
                    "Optimize performance for better scores"
                ] if not all_gates_passed else ["All quality gates passed"],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Update metrics
            if all_gates_passed:
                self.performance_metrics["quality_gates_passed"] += 1
            else:
                self.performance_metrics["quality_gates_failed"] += 1

            self._record_quality_metric("quality_gate_check_success", 95, "%")

            logger.info(f"Quality gate check result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error checking quality gates: {e}")
            raise
        except Exception as e:
            logger.error(f"Error checking quality gates: {e}")
            self._record_quality_metric("quality_gate_check_error", 5, "%")
            raise QualityError(f"Failed to check quality gates: {e}")

    def generate_quality_report(self, format_type: str = "md") -> Dict[str, Any]:
        """Generate comprehensive quality report with comprehensive validation and error handling."""
        try:
            self._validate_input(format_type, str, "format_type")
            
            if format_type not in ["md", "json", "csv"]:
                raise QualityValidationError("Format type must be md, json, or csv")
            
            logger.info(f"Generating quality report in {format_type} format")

            # Simulate quality report generation process
            time.sleep(1)
            
            result = {
                "format": format_type,
                "report_data": {
                    "overall_quality_score": 86.5,
                    "code_quality": {
                        "score": 85,
                        "complexity": 7.2,
                        "maintainability": 78,
                        "duplication": 3.5
                    },
                    "test_coverage": {
                        "current": 82.5,
                        "threshold": 80,
                        "status": "PASS"
                    },
                    "security": {
                        "score": 92,
                        "vulnerabilities": 2,
                        "critical": 0,
                        "high": 1
                    },
                    "performance": {
                        "score": 87,
                        "response_time": 245,
                        "memory_usage": 45.2
                    },
                    "quality_gates": {
                        "passed": 3,
                        "failed": 1,
                        "total": 4
                    }
                },
                "recommendations": [
                    "Increase test coverage to 85%",
                    "Fix high severity security vulnerability",
                    "Optimize database queries for better performance"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            # Export report based on format
            self.export_report(format_type, result["report_data"])

            self._record_quality_metric("quality_report_generation_success", 93, "%")

            logger.info(f"Quality report generation result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error generating quality report: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            self._record_quality_metric("quality_report_generation_error", 7, "%")
            raise QualityError(f"Failed to generate quality report: {e}")

    def suggest_improvements(self, focus_area: str = "general") -> Dict[str, Any]:
        """Generate AI-powered improvement suggestions with comprehensive validation and error handling."""
        try:
            self._validate_input(focus_area, str, "focus_area")
            
            if not focus_area.strip():
                raise QualityValidationError("Focus area cannot be empty")
            
            logger.info(f"Generating improvement suggestions for focus area: {focus_area}")

            # Simulate AI-powered improvement suggestions process
            time.sleep(1)
            
            result = {
                "focus_area": focus_area,
                "suggestions": [
                    {
                        "category": "Code Quality",
                        "priority": "High",
                        "suggestion": "Refactor complex methods to reduce cyclomatic complexity",
                        "impact": "Improve maintainability and reduce bugs",
                        "effort": "Medium"
                    },
                    {
                        "category": "Test Coverage",
                        "priority": "Medium",
                        "suggestion": "Add unit tests for untested business logic",
                        "impact": "Increase confidence in code changes",
                        "effort": "Low"
                    },
                    {
                        "category": "Security",
                        "priority": "High",
                        "suggestion": "Implement input validation for user inputs",
                        "impact": "Prevent security vulnerabilities",
                        "effort": "Medium"
                    },
                    {
                        "category": "Performance",
                        "priority": "Medium",
                        "suggestion": "Implement caching for frequently accessed data",
                        "impact": "Improve response times",
                        "effort": "High"
                    }
                ],
                "ai_confidence": 87.5,
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            self._record_quality_metric("improvement_suggestions_success", 91, "%")

            logger.info(f"Improvement suggestions result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error generating improvement suggestions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {e}")
            self._record_quality_metric("improvement_suggestions_error", 9, "%")
            raise QualityError(f"Failed to generate improvement suggestions: {e}")

    def enforce_standards(self, path: str = "./") -> Dict[str, Any]:
        """Enforce coding standards with comprehensive validation and error handling."""
        try:
            self._validate_input(path, str, "path")
            
            if not path.strip():
                raise QualityValidationError("Path cannot be empty")
            
            logger.info(f"Enforcing coding standards for path: {path}")

            # Simulate standards enforcement process
            time.sleep(1)
            
            result = {
                "path": path,
                "standards_enforced": [
                    "PEP 8 Python style guide",
                    "Type hints compliance",
                    "Docstring standards",
                    "Naming conventions",
                    "Import organization"
                ],
                "violations_found": 3,
                "violations_details": [
                    {
                        "file": "utils/helper.py",
                        "line": 45,
                        "violation": "Missing type hints",
                        "severity": "Medium"
                    },
                    {
                        "file": "models/user.py",
                        "line": 23,
                        "violation": "Inconsistent naming",
                        "severity": "Low"
                    },
                    {
                        "file": "api/endpoints.py",
                        "line": 67,
                        "violation": "Missing docstring",
                        "severity": "Medium"
                    }
                ],
                "compliance_score": 92.5,
                "recommendations": [
                    "Add type hints to all function parameters",
                    "Follow consistent naming conventions",
                    "Add docstrings to all public functions"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "QualityGuardianAgent"
            }

            self._record_quality_metric("standards_enforcement_success", 89, "%")

            logger.info(f"Standards enforcement result: {result}")
            return result
            
        except QualityValidationError as e:
            logger.error(f"Validation error enforcing standards: {e}")
            raise
        except Exception as e:
            logger.error(f"Error enforcing standards: {e}")
            self._record_quality_metric("standards_enforcement_error", 11, "%")
            raise QualityError(f"Failed to enforce standards: {e}")

    def show_quality_history(self):
        """Show quality analysis history."""
        print("=== Quality Analysis History ===\n")
        for entry in self.quality_history[-10:]:  # Show last 10 entries
            print(f"- {entry}")
        print(f"\nTotal entries: {len(self.quality_history)}")

    def show_security_history(self):
        """Show security scan history."""
        print("=== Security Scan History ===\n")
        for entry in self.security_history[-10:]:  # Show last 10 entries
            print(f"- {entry}")
        print(f"\nTotal entries: {len(self.security_history)}")

    def show_performance_history(self):
        """Show performance analysis history."""
        print("=== Performance Analysis History ===\n")
        for entry in self.performance_history[-10:]:  # Show last 10 entries
            print(f"- {entry}")
        print(f"\nTotal entries: {len(self.performance_history)}")

    def show_quality_metrics(self):
        """Show quality metrics and trends."""
        print("=== Quality Metrics ===\n")
        for entry in self.quality_metrics[-10:]:  # Show last 10 entries
            print(f"- {entry}")
        print(f"\nTotal entries: {len(self.quality_metrics)}")
        
        print(f"\nPerformance Metrics:")
        print(f"- Quality analyses completed: {self.performance_metrics['quality_analyses_completed']}")
        print(f"- Security scans completed: {self.performance_metrics['security_scans_completed']}")
        print(f"- Performance analyses completed: {self.performance_metrics['performance_analyses_completed']}")
        print(f"- Quality gates passed: {self.performance_metrics['quality_gates_passed']}")
        print(f"- Quality gates failed: {self.performance_metrics['quality_gates_failed']}")
        print(f"- Overall quality score: {self.performance_metrics['quality_score']}")

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export quality report in specified format."""
        if report_data is None:
            report_data = {
                "overall_quality_score": 86.5,
                "code_quality": {"score": 85},
                "test_coverage": {"current": 82.5},
                "security": {"score": 92},
                "performance": {"score": 87}
            }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "md":
            self._export_markdown(report_data, timestamp)
        elif format_type == "json":
            self._export_json(report_data, timestamp)
        elif format_type == "csv":
            self._export_csv(report_data, timestamp)

    def _export_markdown(self, report_data: Dict, timestamp: str):
        """Export report in Markdown format."""
        filename = f"quality_report_{timestamp}.md"
        try:
            with open(filename, "w") as f:
                f.write("# Quality Report\n\n")
                f.write(f"**Generated**: {datetime.now().isoformat()}\n")
                f.write(f"**Agent**: QualityGuardian\n\n")
                
                f.write(f"## Overall Quality Score: {report_data['overall_quality_score']}%\n\n")
                
                f.write("## Detailed Metrics\n\n")
                f.write(f"- **Code Quality**: {report_data['code_quality']['score']}%\n")
                f.write(f"- **Test Coverage**: {report_data['test_coverage']['current']}%\n")
                f.write(f"- **Security Score**: {report_data['security']['score']}%\n")
                f.write(f"- **Performance Score**: {report_data['performance']['score']}%\n")
                
            print(f"Quality report exported to: {filename}")
        except Exception as e:
            logger.error(f"Error exporting markdown report: {e}")

    def _export_json(self, report_data: Dict, timestamp: str):
        """Export report in JSON format."""
        filename = f"quality_report_{timestamp}.json"
        try:
            with open(filename, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"Quality report exported to: {filename}")
        except Exception as e:
            logger.error(f"Error exporting JSON report: {e}")

    def _export_csv(self, report_data: Dict, timestamp: str):
        """Export report in CSV format."""
        filename = f"quality_report_{timestamp}.csv"
        try:
            with open(filename, "w") as f:
                f.write("Metric,Value\n")
                f.write(f"Overall Quality Score,{report_data['overall_quality_score']}\n")
                f.write(f"Code Quality,{report_data['code_quality']['score']}\n")
                f.write(f"Test Coverage,{report_data['test_coverage']['current']}\n")
                f.write(f"Security Score,{report_data['security']['score']}\n")
                f.write(f"Performance Score,{report_data['performance']['score']}\n")
            print(f"Quality report exported to: {filename}")
        except Exception as e:
            logger.error(f"Error exporting CSV report: {e}")

    def test_resource_completeness(self):
        """Test resource completeness."""
        print("=== Testing Resource Completeness ===\n")
        
        missing_resources = []
        
        # Check template files
        for template_name, template_path in self.template_paths.items():
            if not template_path.exists():
                missing_resources.append(f"Template: {template_name}")
                print(f"❌ Missing template: {template_name}")
            else:
                print(f"✅ Template found: {template_name}")
        
        # Check data files
        for data_name, data_path in self.data_paths.items():
            if not data_path.exists():
                missing_resources.append(f"Data: {data_name}")
                print(f"❌ Missing data file: {data_name}")
            else:
                print(f"✅ Data file found: {data_name}")
        
        if missing_resources:
            print(f"\n❌ Missing resources: {len(missing_resources)}")
            print("Please create the missing resource files.")
        else:
            print(f"\n✅ All resources are complete!")

    async def collaborate_example(self):
        """Demonstrate collaboration with other agents with async optimization."""
        print("=== QualityGuardian Agent Collaboration Example ===\n")
        
        # Use asyncio.gather for parallel execution
        tasks = [
            self._async_monitor_test_coverage(85),
            self._async_security_scan("*.py"),
            self._async_quality_gate_check(deployment=True)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        test_result, security_result, gate_result = results
        
        if isinstance(test_result, Exception):
            print(f"❌ TestEngineer collaboration failed: {test_result}")
        else:
            print("🤝 Collaborating with TestEngineer Agent...")
            print(f"📊 Test coverage result: {test_result['current_coverage']}%")
        
        if isinstance(security_result, Exception):
            print(f"❌ SecurityDeveloper collaboration failed: {security_result}")
        else:
            print("🔒 Collaborating with SecurityDeveloper Agent...")
            print(f"🛡️ Security scan result: {security_result['security_score']}%")
        
        if isinstance(gate_result, Exception):
            print(f"❌ ReleaseManager collaboration failed: {gate_result}")
        else:
            print("🚀 Collaborating with ReleaseManager Agent...")
            print(f"✅ Quality gates result: {'PASS' if gate_result['all_gates_passed'] else 'FAIL'}")
        
        print("\n✅ Async collaboration example completed successfully!")
    
    # Async wrapper methods for parallel execution
    async def _async_monitor_test_coverage(self, threshold: int):
        """Async wrapper for monitor_test_coverage."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.monitor_test_coverage, threshold)
    
    async def _async_security_scan(self, files: str):
        """Async wrapper for security_scan."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.security_scan, files)
    
    async def _async_quality_gate_check(self, deployment: bool):
        """Async wrapper for quality_gate_check."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.quality_gate_check, deployment)

    def on_test_completed(self, event):
        """Handle test completion events."""
        logger.info(f"Received test completion event: {event}")
        # Process test results and update quality metrics
        self.monitor_test_coverage()

    def on_security_scan_completed(self, event):
        """Handle security scan completion events."""
        logger.info(f"Received security scan completion event: {event}")
        # Process security results and update metrics
        self.security_scan()

    def on_deployment_requested(self, event):
        """Handle deployment request events."""
        logger.info(f"Received deployment request event: {event}")
        # Check quality gates before deployment
        gate_result = self.quality_gate_check(deployment=True)
        if not gate_result['all_gates_passed']:
            logger.warning("Quality gates failed - deployment blocked")
            # Notify ReleaseManager about failed gates
            publish("quality_gates_failed", {"reason": "Quality thresholds not met"})
        else:
            logger.info("Quality gates passed - deployment approved")
            publish("quality_gates_passed", {"result": gate_result})

    def run(self):
        """Run the agent and listen for events."""
        print("🚀 Starting QualityGuardian Agent...")
        
        def sync_handler(event):
            """Handle events synchronously."""
            try:
                if event.get("type") == "test_completed":
                    self.on_test_completed(event)
                elif event.get("type") == "security_scan_completed":
                    self.on_security_scan_completed(event)
                elif event.get("type") == "deployment_requested":
                    self.on_deployment_requested(event)
            except Exception as e:
                logger.error(f"Error handling event: {e}")

        # Subscribe to relevant events
        subscribe("test_completed", sync_handler)
        subscribe("security_scan_completed", sync_handler)
        subscribe("deployment_requested", sync_handler)
        
        print("✅ QualityGuardian Agent is running and listening for events...")
        print("Press Ctrl+C to stop the agent")

def main():
    """Main CLI function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description="QualityGuardian Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "analyze-code-quality", "monitor-test-coverage", 
                               "security-scan", "performance-analysis", "enforce-standards",
                               "quality-gate-check", "generate-quality-report", "suggest-improvements",
                               "show-quality-history", "show-security-history", 
                               "show-performance-history", "show-quality-metrics",
                               "test", "collaborate", "run"])
    parser.add_argument("--path", default="./", help="Path to analyze")
    parser.add_argument("--threshold", type=int, default=80, help="Coverage threshold")
    parser.add_argument("--files", default="*.py", help="Files pattern for security scan")
    parser.add_argument("--component", default="main", help="Component for performance analysis")
    parser.add_argument("--deployment", action="store_true", help="Check quality gates for deployment")
    parser.add_argument("--format", default="md", choices=["md", "json", "csv"], help="Report format")

    args = parser.parse_args()

    try:
        agent = QualityGuardianAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "analyze-code-quality":
            result = agent.analyze_code_quality(args.path)
            print(f"✅ Code quality analysis completed: {result['code_quality_score']}%")
        elif args.command == "monitor-test-coverage":
            result = agent.monitor_test_coverage(args.threshold)
            print(f"✅ Test coverage monitoring completed: {result['current_coverage']}%")
        elif args.command == "security-scan":
            result = agent.security_scan(args.files)
            print(f"✅ Security scan completed: {result['security_score']}%")
        elif args.command == "performance-analysis":
            result = agent.performance_analysis(args.component)
            print(f"✅ Performance analysis completed: {result['performance_score']}%")
        elif args.command == "enforce-standards":
            result = agent.enforce_standards(args.path)
            print(f"✅ Standards enforcement completed: {result['compliance_score']}%")
        elif args.command == "quality-gate-check":
            result = agent.quality_gate_check(args.deployment)
            print(f"✅ Quality gate check completed: {'PASS' if result['all_gates_passed'] else 'FAIL'}")
        elif args.command == "generate-quality-report":
            result = agent.generate_quality_report(args.format)
            print(f"✅ Quality report generated in {args.format} format")
        elif args.command == "suggest-improvements":
            result = agent.suggest_improvements()
            print(f"✅ Improvement suggestions generated: {len(result['suggestions'])} suggestions")
        elif args.command == "show-quality-history":
            agent.show_quality_history()
        elif args.command == "show-security-history":
            agent.show_security_history()
        elif args.command == "show-performance-history":
            agent.show_performance_history()
        elif args.command == "show-quality-metrics":
            agent.show_quality_metrics()
        elif args.command == "test":
            agent.test_resource_completeness()
        elif args.command == "collaborate":
            agent.collaborate_example()
        elif args.command == "run":
            agent.run()
            
    except QualityValidationError as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)
    except QualityError as e:
        print(f"❌ Quality error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 