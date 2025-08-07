#!/usr/bin/env python3
"""
Framework Templates Utility voor BMAD Agents
Maakt development en testing framework templates beschikbaar voor alle agents.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FrameworkTemplatesManager:
    """Manager voor framework templates die agents kunnen gebruiken."""
    
    def __init__(self):
        # Set up resource paths
        self.resource_base = Path(__file__).parent.parent.parent.parent / "resources"
        self.frameworks_path = self.resource_base / "templates" / "frameworks"
        
        # Framework template paths
        self.framework_templates = {
            "development_strategy": self.frameworks_path / "development_strategy_template.md",
            "development_workflow": self.frameworks_path / "development_workflow_template.md",
            "testing_strategy": self.frameworks_path / "testing_strategy_template.md",
            "testing_workflow": self.frameworks_path / "testing_workflow_template.md",
            "frameworks_overview": self.frameworks_path / "frameworks_overview_template.md",
            "backend_development": self.frameworks_path / "backend_development_template.md",
            "frontend_development": self.frameworks_path / "frontend_development_template.md",
            "fullstack_development": self.frameworks_path / "fullstack_development_template.md",
            "testing_engineer": self.frameworks_path / "testing_engineer_template.md",
            "quality_guardian": self.frameworks_path / "quality_guardian_template.md",
            "data_engineer": self.frameworks_path / "data_engineer_template.md",
            "rnd": self.frameworks_path / "rnd_template.md",
            "product_owner": self.frameworks_path / "product_owner_template.md",
            "scrummaster": self.frameworks_path / "scrummaster_template.md",
            "release_manager": self.frameworks_path / "release_manager_template.md",
            "architecture": self.frameworks_path / "architecture_template.md",
            "devops": self.frameworks_path / "devops_template.md",
            "feedback_agent": self.frameworks_path / "feedback_agent_template.md",
            "security": self.frameworks_path / "security_template.md"
        }
        
        # Validate template paths
        self._validate_template_paths()
    
    def _validate_template_paths(self) -> None:
        """Validate that all framework template files exist."""
        missing_templates = []
        for template_name, template_path in self.framework_templates.items():
            if not template_path.exists():
                missing_templates.append(f"{template_name}: {template_path}")
        
        if missing_templates:
            logger.warning(f"Missing framework templates: {missing_templates}")
    
    def get_framework_template(self, template_name: str) -> Optional[str]:
        """Get framework template content by name."""
        if template_name not in self.framework_templates:
            logger.error(f"Unknown framework template: {template_name}")
            return None
        
        template_path = self.framework_templates[template_name]
        if not template_path.exists():
            logger.error(f"Framework template not found: {template_path}")
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading framework template {template_name}: {e}")
            return None
    
    def get_all_framework_templates(self) -> Dict[str, str]:
        """Get all available framework templates."""
        templates = {}
        for template_name in self.framework_templates.keys():
            content = self.get_framework_template(template_name)
            if content:
                templates[template_name] = content
        return templates
    
    def list_available_templates(self) -> List[str]:
        """List all available framework template names."""
        return list(self.framework_templates.keys())
    
    def get_framework_guidelines(self, agent_type: str) -> Dict[str, Any]:
        """Get framework guidelines specific to agent type."""
        guidelines = {
            "ai_agents": {
                "development": [
                    "Implementeer comprehensive error handling voor LLM calls",
                    "Gebruik structured logging voor alle AI operaties",
                    "Implementeer fallback mechanismen voor API failures",
                    "Valideer alle AI outputs voor safety en quality"
                ],
                "testing": [
                    "Mock LLM API calls in unit tests",
                    "Test AI output validation en safety checks",
                    "Implementeer integration tests met echte LLM APIs",
                    "Test fallback mechanismen voor API failures"
                ]
            },
            "backend_agents": {
                "development": [
                    "Volg microservices architecture patterns",
                    "Implementeer proper database schema design",
                    "Gebruik FastAPI voor REST API development",
                    "Implementeer comprehensive error handling",
                    "Volg security best practices (JWT, RBAC, input validation)",
                    "Gebruik connection pooling en caching strategies",
                    "Implementeer proper logging en monitoring"
                ],
                "testing": [
                    "Test database operations met proper fixtures",
                    "Mock external service dependencies",
                    "Test API endpoints met comprehensive scenarios",
                    "Implementeer integration tests voor service communication",
                    "Test security measures en authentication flows"
                ]
            },
            "frontend_agents": {
                "development": [
                    "Gebruik component-based architecture",
                    "Implementeer proper state management (React Query + Zustand)",
                    "Volg TypeScript best practices voor type safety",
                    "Gebruik Tailwind CSS voor consistent styling",
                    "Implementeer proper form validation met React Hook Form",
                    "Gebruik proper error boundaries en loading states",
                    "Implementeer responsive design patterns"
                ],
                "testing": [
                    "Test component rendering en user interactions",
                    "Mock API calls in component tests",
                    "Test form validation en error handling",
                    "Implementeer accessibility testing",
                    "Test responsive design op verschillende screen sizes"
                ]
            },
            "fullstack_agents": {
                "development": [
                    "Coördineer frontend en backend development",
                    "Gebruik shared type definitions tussen frontend en backend",
                    "Implementeer end-to-end workflows",
                    "Volg consistent API design patterns",
                    "Gebruik proper authentication flows",
                    "Implementeer real-time features met WebSockets",
                    "Test complete user journeys"
                ],
                "testing": [
                    "Implementeer end-to-end tests voor complete workflows",
                    "Test API integration tussen frontend en backend",
                    "Test real-time features en WebSocket communication",
                    "Test complete user registration en authentication flows",
                    "Implementeer performance testing voor fullstack applications"
                ]
            },
            "testing_agents": {
                "development": [
                    "Implementeer comprehensive test strategies",
                    "Volg test pyramid approach (70% unit, 20% integration, 10% E2E)",
                    "Gebruik test data factories en fixtures",
                    "Implementeer proper test isolation en cleanup",
                    "Gebruik mocking strategies voor external dependencies",
                    "Implementeer test automation en CI/CD integration",
                    "Volg test-driven development (TDD) principles"
                ],
                "testing": [
                    "Test test frameworks en test utilities",
                    "Valideer test coverage en quality metrics",
                    "Test test data management en seeding",
                    "Implementeer test performance monitoring",
                    "Test test reporting en analytics"
                ]
            },
            "quality_agents": {
                "development": [
                    "Implementeer quality gates en enforcement",
                    "Gebruik code quality analysis tools",
                    "Implementeer security scanning en vulnerability detection",
                    "Monitor performance metrics en benchmarks",
                    "Implementeer compliance checking en validation",
                    "Gebruik quality metrics dashboards en reporting",
                    "Implementeer quality trend analysis en prediction"
                ],
                "testing": [
                    "Test quality gate implementations",
                    "Valideer code quality analysis accuracy",
                    "Test security scanning effectiveness",
                    "Implementeer quality metrics validation",
                    "Test compliance checking accuracy"
                ]
            },
            "ai_agents": {
                "development": [
                    "Implementeer data pipeline architecture en ETL/ELT processes",
                    "Gebruik data quality management en validation frameworks",
                    "Implementeer technology research en evaluation methodologies",
                    "Gebruik proof-of-concept development en validation",
                    "Implementeer innovation pipeline management",
                    "Gebruik knowledge management en collaboration tools",
                    "Implementeer performance monitoring en optimization"
                ],
                "testing": [
                    "Test data pipeline functionality en performance",
                    "Valideer data quality metrics en validation accuracy",
                    "Test technology evaluation frameworks en decision processes",
                    "Implementeer POC testing en validation workflows",
                    "Test innovation tracking en metrics accuracy"
                ]
            },
            "management_agents": {
                "development": [
                    "Implementeer product management en backlog management frameworks",
                    "Gebruik scrum process facilitation en team coaching methodologies",
                    "Implementeer release planning en deployment management",
                    "Gebruik stakeholder management en communication strategies",
                    "Implementeer sprint planning en retrospective facilitation",
                    "Gebruik quality gates en release coordination",
                    "Implementeer changelog management en documentation"
                ],
                "testing": [
                    "Test product management workflows en backlog health",
                    "Valideer scrum process effectiveness en team performance",
                    "Test release planning accuracy en deployment success",
                    "Implementeer stakeholder satisfaction metrics",
                    "Test sprint planning en retrospective effectiveness"
                ]
            },
            "development_agents": {
                "development": [
                    "Volg de development pyramid strategie",
                    "Implementeer unit tests voor alle nieuwe functionaliteit",
                    "Gebruik type hints en comprehensive docstrings",
                    "Valideer code quality met linting tools",
                    "Gebruik framework templates voor consistente development",
                    "Implementeer proper error handling en logging",
                    "Volg security best practices voor input validation"
                ],
                "testing": [
                    "Volg de test pyramid strategie",
                    "Implementeer comprehensive unit tests",
                    "Gebruik pragmatic mocking voor externe dependencies",
                    "Valideer code quality met test coverage"
                ]
            },
            "testing_agents": {
                "development": [
                    "Implementeer pragmatic mocking voor externe dependencies",
                    "Volg de test pyramid strategie",
                    "Zorg voor comprehensive test coverage",
                    "Valideer test quality en performance"
                ],
                "testing": [
                    "Implementeer test frameworks en utilities",
                    "Zorg voor comprehensive test coverage",
                    "Valideer test quality en performance",
                    "Implementeer test monitoring en reporting"
                ]
            }
        }
        
        return guidelines.get(agent_type, {})
    
    def get_quality_gates(self) -> Dict[str, Any]:
        """Get quality gates for development and testing."""
        return {
            "development": {
                "linting": "No flake8 errors",
                "coverage": ">90% line coverage",
                "tests": "All tests passing",
                "documentation": "Complete docstrings"
            },
            "testing": {
                "unit_coverage": ">90% line coverage",
                "integration_success": ">95% success rate",
                "e2e_success": ">90% success rate",
                "execution_time": "<5 minutes for unit tests"
            }
        }
    
    def get_pyramid_strategies(self) -> Dict[str, Any]:
        """Get development and testing pyramid strategies."""
        return {
            "development": {
                "unit": "70% van alle development (snel, geïsoleerd)",
                "integration": "20% van alle development (service integratie)",
                "production": "10% van alle development (volledige validatie)"
            },
            "testing": {
                "unit": "70% van alle tests (snel, gemockt)",
                "integration": "20% van alle tests (echte dependencies)",
                "e2e": "10% van alle tests (volledige workflows)"
            }
        }
    
    def get_mocking_strategy(self) -> str:
        """Get pragmatic mocking strategy code."""
        return '''# Pragmatisch mocken van zware externe dependencies
import sys
from unittest.mock import MagicMock

# Mock externe modules
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['psutil'] = MagicMock()'''
    
    def get_workflow_commands(self) -> Dict[str, List[str]]:
        """Get development and testing workflow commands."""
        return {
            "development": [
                "# Dagelijks: Alleen unit development",
                "pytest tests/unit/ -v",
                "flake8 bmad/ --count",
                "",
                "# Voor commits: Unit + snelle integration development",
                "pytest tests/unit/ tests/integration/ -m \"not slow\" -v",
                "flake8 bmad/ --count",
                "",
                "# Voor releases: Alle development",
                "pytest tests/ -v --run-integration",
                "flake8 bmad/ --count"
            ],
            "testing": [
                "# Development: Alleen unit tests",
                "pytest tests/unit/ -v",
                "",
                "# Staging: Unit + integration tests",
                "pytest tests/ -v --run-integration",
                "",
                "# Production: Alle tests",
                "pytest tests/ -v --run-integration --run-e2e"
            ]
        }
    
    def get_linting_config(self) -> str:
        """Get flake8 linting configuration."""
        return '''# .flake8
[flake8]
max-line-length = 120
ignore = E501,W503,E402,F401,F541,F821,F811,F841,E265,E303,E226,W291,W293,W292,E128,E129,E305,E302,E306,E261,E504,F824,W504,E122,E116
exclude = .git,__pycache__,.venv,venv,path/to/venv,htmlcov,.pytest_cache,allure-results,test_data
per-file-ignores = 
    bmad/resources/templates/**/*.py:F821
    bmad/agents/Agent/**/*.py:E402
    bmad/agents/core/**/*.py:F401'''

# Global instance
framework_templates_manager = FrameworkTemplatesManager()

def get_framework_templates_manager() -> FrameworkTemplatesManager:
    """Get the global framework templates manager instance."""
    return framework_templates_manager

def get_framework_template(template_name: str) -> Optional[str]:
    """Get framework template content by name."""
    return framework_templates_manager.get_framework_template(template_name)

def get_all_framework_templates() -> Dict[str, str]:
    """Get all available framework templates."""
    return framework_templates_manager.get_all_framework_templates()

def get_framework_guidelines(agent_type: str) -> Dict[str, Any]:
    """Get framework guidelines specific to agent type."""
    return framework_templates_manager.get_framework_guidelines(agent_type)

def get_quality_gates() -> Dict[str, Any]:
    """Get quality gates for development and testing."""
    return framework_templates_manager.get_quality_gates()

def get_pyramid_strategies() -> Dict[str, Any]:
    """Get development and testing pyramid strategies."""
    return framework_templates_manager.get_pyramid_strategies()

def get_mocking_strategy() -> str:
    """Get pragmatic mocking strategy code."""
    return framework_templates_manager.get_mocking_strategy()

def get_workflow_commands() -> Dict[str, List[str]]:
    """Get development and testing workflow commands."""
    return framework_templates_manager.get_workflow_commands()

def get_linting_config() -> str:
    """Get flake8 linting configuration."""
    return framework_templates_manager.get_linting_config() 