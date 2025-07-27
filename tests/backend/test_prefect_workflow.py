"""
Tests for bmad.agents.core.prefect_workflow module.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from bmad.agents.core.prefect_workflow import (
    PrefectWorkflowOrchestrator,
    PrefectWorkflowConfig,
    AgentTaskConfig,
    WorkflowType,
    DeploymentEnvironment,
    create_prefect_orchestrator,
    create_development_workflow_config,
    create_deployment_workflow_config,
    create_testing_workflow_config,
    get_development_tasks,
    get_deployment_tasks
)


class TestPrefectWorkflowConfig:
    """Test PrefectWorkflowConfig dataclass."""
    
    def test_workflow_config_creation(self):
        """Test creating a PrefectWorkflowConfig."""
        config = PrefectWorkflowConfig(
            name="test_workflow",
            description="Test workflow",
            workflow_type=WorkflowType.DEVELOPMENT,
            environment=DeploymentEnvironment.DEVELOPMENT
        )
        
        assert config.name == "test_workflow"
        assert config.description == "Test workflow"
        assert config.workflow_type == WorkflowType.DEVELOPMENT
        assert config.environment == DeploymentEnvironment.DEVELOPMENT
        assert config.timeout_minutes == 60
        assert config.retries == 3
        assert config.retry_delay_seconds == 300
        assert config.tags == []
        assert config.parameters == {}
    
    def test_workflow_config_with_custom_settings(self):
        """Test creating a PrefectWorkflowConfig with custom settings."""
        config = PrefectWorkflowConfig(
            name="custom_workflow",
            description="Custom workflow",
            workflow_type=WorkflowType.DEPLOYMENT,
            environment=DeploymentEnvironment.PRODUCTION,
            schedule="0 */6 * * *",
            timeout_minutes=180,
            retries=5,
            retry_delay_seconds=600,
            tags=["production", "critical"],
            parameters={"environment": "prod"}
        )
        
        assert config.name == "custom_workflow"
        assert config.workflow_type == WorkflowType.DEPLOYMENT
        assert config.environment == DeploymentEnvironment.PRODUCTION
        assert config.schedule == "0 */6 * * *"
        assert config.timeout_minutes == 180
        assert config.retries == 5
        assert config.retry_delay_seconds == 600
        assert config.tags == ["production", "critical"]
        assert config.parameters == {"environment": "prod"}


class TestAgentTaskConfig:
    """Test AgentTaskConfig dataclass."""
    
    def test_agent_task_config_creation(self):
        """Test creating an AgentTaskConfig."""
        task_config = AgentTaskConfig(
            agent_name="ProductOwner",
            task_name="create_user_story",
            command="create_user_story"
        )
        
        assert task_config.agent_name == "ProductOwner"
        assert task_config.task_name == "create_user_story"
        assert task_config.command == "create_user_story"
        assert task_config.timeout_seconds == 300
        assert task_config.retries == 2
        assert task_config.retry_delay_seconds == 60
        assert task_config.dependencies == []
        assert task_config.parameters == {}
    
    def test_agent_task_config_with_dependencies(self):
        """Test creating an AgentTaskConfig with dependencies."""
        task_config = AgentTaskConfig(
            agent_name="Architect",
            task_name="design_system",
            command="design_system",
            dependencies=["create_user_story"],
            parameters={"architecture_type": "microservices"}
        )
        
        assert task_config.agent_name == "Architect"
        assert task_config.task_name == "design_system"
        assert task_config.command == "design_system"
        assert task_config.dependencies == ["create_user_story"]
        assert task_config.parameters == {"architecture_type": "microservices"}


class TestPrefectWorkflowOrchestrator:
    """Test PrefectWorkflowOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        assert isinstance(orchestrator.workflow_configs, dict)
        assert isinstance(orchestrator.agent_executors, dict)
        assert isinstance(orchestrator.deployments, dict)
        
        # Check that default executors are registered
        assert "ProductOwner" in orchestrator.agent_executors
        assert "Architect" in orchestrator.agent_executors
        assert "FullstackDeveloper" in orchestrator.agent_executors
        assert "TestEngineer" in orchestrator.agent_executors
        assert "DevOpsInfra" in orchestrator.agent_executors
        assert "SecurityDeveloper" in orchestrator.agent_executors
    
    def test_register_workflow_config(self):
        """Test registering a workflow config."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        config = PrefectWorkflowConfig(
            name="test_workflow",
            description="Test workflow",
            workflow_type=WorkflowType.DEVELOPMENT,
            environment=DeploymentEnvironment.DEVELOPMENT
        )
        
        orchestrator.register_workflow_config(config)
        
        assert "test_workflow" in orchestrator.workflow_configs
        assert orchestrator.workflow_configs["test_workflow"] == config
    
    def test_register_agent_executor(self):
        """Test registering an agent executor."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        def test_executor(task_name, command, parameters, context):
            return {"output": "test result"}
        
        orchestrator.register_agent_executor("TestAgent", test_executor)
        
        assert "TestAgent" in orchestrator.agent_executors
        assert orchestrator.agent_executors["TestAgent"] == test_executor
    
    def test_create_deployment_missing_config(self):
        """Test creating deployment with missing config."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        tasks = [
            AgentTaskConfig(
                agent_name="ProductOwner",
                task_name="test_task",
                command="test_command"
            )
        ]
        
        with pytest.raises(ValueError, match="Workflow config 'nonexistent' niet gevonden"):
            orchestrator.create_deployment("nonexistent", tasks)


class TestPrefectWorkflowOrchestratorExecutors:
    """Test agent executors in PrefectWorkflowOrchestrator."""
    
    def test_execute_product_owner_task(self):
        """Test ProductOwner task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="ProductOwner",
            task_name="create_user_story",
            command="create_user_story",
            parameters={"priority": "high"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "ProductOwner"
        assert result["task_name"] == "create_user_story"
        assert result["command"] == "create_user_story"
        assert result["parameters"] == {"priority": "high"}
        assert result["status"] == "success"
        assert "ProductOwner completed: create_user_story" in result["output"]
    
    def test_execute_architect_task(self):
        """Test Architect task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="Architect",
            task_name="design_system",
            command="design_system",
            parameters={"architecture_type": "microservices"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "Architect"
        assert result["task_name"] == "design_system"
        assert result["command"] == "design_system"
        assert result["parameters"] == {"architecture_type": "microservices"}
        assert result["status"] == "success"
        assert "Architect completed: design_system" in result["output"]
    
    def test_execute_fullstack_task(self):
        """Test FullstackDeveloper task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="FullstackDeveloper",
            task_name="implement_feature",
            command="implement_feature",
            parameters={"framework": "react-fastapi"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "FullstackDeveloper"
        assert result["task_name"] == "implement_feature"
        assert result["command"] == "implement_feature"
        assert result["parameters"] == {"framework": "react-fastapi"}
        assert result["status"] == "success"
        assert "FullstackDeveloper completed: implement_feature" in result["output"]
    
    def test_execute_test_task(self):
        """Test TestEngineer task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="TestEngineer",
            task_name="run_tests",
            command="run_tests",
            parameters={"test_type": "unit,integration,e2e"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "TestEngineer"
        assert result["task_name"] == "run_tests"
        assert result["command"] == "run_tests"
        assert result["parameters"] == {"test_type": "unit,integration,e2e"}
        assert result["status"] == "success"
        assert "TestEngineer completed: run_tests" in result["output"]
    
    def test_execute_devops_task(self):
        """Test DevOpsInfra task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="DevOpsInfra",
            task_name="build_application",
            command="build_application",
            parameters={"build_type": "docker"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "DevOpsInfra"
        assert result["task_name"] == "build_application"
        assert result["command"] == "build_application"
        assert result["parameters"] == {"build_type": "docker"}
        assert result["status"] == "success"
        assert "DevOpsInfra completed: build_application" in result["output"]
    
    def test_execute_security_task(self):
        """Test SecurityDeveloper task execution."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        task_config = AgentTaskConfig(
            agent_name="SecurityDeveloper",
            task_name="security_scan",
            command="security_scan",
            parameters={"scan_type": "vulnerability,secrets"}
        )
        
        context = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "environment": "development"
        }
        
        result = orchestrator._execute_agent_task(task_config, context)
        
        assert isinstance(result, dict)
        assert result["agent"] == "SecurityDeveloper"
        assert result["task_name"] == "security_scan"
        assert result["command"] == "security_scan"
        assert result["parameters"] == {"scan_type": "vulnerability,secrets"}
        assert result["status"] == "success"
        assert "SecurityDeveloper completed: security_scan" in result["output"]


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_prefect_orchestrator(self):
        """Test create_prefect_orchestrator function."""
        orchestrator = create_prefect_orchestrator()
        
        assert isinstance(orchestrator, PrefectWorkflowOrchestrator)
        assert "ProductOwner" in orchestrator.agent_executors
    
    def test_create_development_workflow_config(self):
        """Test create_development_workflow_config function."""
        config = create_development_workflow_config()
        
        assert isinstance(config, PrefectWorkflowConfig)
        assert config.name == "bmad-development-pipeline"
        assert config.workflow_type == WorkflowType.DEVELOPMENT
        assert config.environment == DeploymentEnvironment.DEVELOPMENT
        assert config.timeout_minutes == 120
        assert config.retries == 2
        assert "development" in config.tags
        assert "bmad" in config.tags
        assert "pipeline" in config.tags
    
    def test_create_deployment_workflow_config(self):
        """Test create_deployment_workflow_config function."""
        config = create_deployment_workflow_config()
        
        assert isinstance(config, PrefectWorkflowConfig)
        assert config.name == "bmad-deployment-pipeline"
        assert config.workflow_type == WorkflowType.DEPLOYMENT
        assert config.environment == DeploymentEnvironment.STAGING
        assert config.timeout_minutes == 180
        assert config.retries == 3
        assert "deployment" in config.tags
        assert "bmad" in config.tags
        assert "pipeline" in config.tags
    
    def test_create_testing_workflow_config(self):
        """Test create_testing_workflow_config function."""
        config = create_testing_workflow_config()
        
        assert isinstance(config, PrefectWorkflowConfig)
        assert config.name == "bmad-testing-pipeline"
        assert config.workflow_type == WorkflowType.TESTING
        assert config.environment == DeploymentEnvironment.DEVELOPMENT
        assert config.schedule == "0 */6 * * *"
        assert config.timeout_minutes == 90
        assert config.retries == 2
        assert "testing" in config.tags
        assert "bmad" in config.tags
        assert "pipeline" in config.tags


class TestPredefinedTaskConfigurations:
    """Test predefined task configurations."""
    
    def test_get_development_tasks(self):
        """Test get_development_tasks function."""
        tasks = get_development_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) == 4
        
        # Check ProductOwner task
        product_owner_task = tasks[0]
        assert product_owner_task.agent_name == "ProductOwner"
        assert product_owner_task.task_name == "create_user_story"
        assert product_owner_task.command == "create_user_story"
        assert product_owner_task.parameters == {"priority": "high"}
        
        # Check Architect task
        architect_task = tasks[1]
        assert architect_task.agent_name == "Architect"
        assert architect_task.task_name == "design_system"
        assert architect_task.command == "design_system"
        assert architect_task.dependencies == ["create_user_story"]
        assert architect_task.parameters == {"architecture_type": "microservices"}
        
        # Check FullstackDeveloper task
        developer_task = tasks[2]
        assert developer_task.agent_name == "FullstackDeveloper"
        assert developer_task.task_name == "implement_feature"
        assert developer_task.command == "implement_feature"
        assert developer_task.dependencies == ["design_system"]
        assert developer_task.parameters == {"framework": "react-fastapi"}
        
        # Check TestEngineer task
        test_task = tasks[3]
        assert test_task.agent_name == "TestEngineer"
        assert test_task.task_name == "run_tests"
        assert test_task.command == "run_tests"
        assert test_task.dependencies == ["implement_feature"]
        assert test_task.parameters == {"test_type": "unit,integration,e2e"}
    
    def test_get_deployment_tasks(self):
        """Test get_deployment_tasks function."""
        tasks = get_deployment_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) == 4
        
        # Check DevOpsInfra build task
        build_task = tasks[0]
        assert build_task.agent_name == "DevOpsInfra"
        assert build_task.task_name == "build_application"
        assert build_task.command == "build_application"
        assert build_task.parameters == {"build_type": "docker"}
        
        # Check SecurityDeveloper scan task
        scan_task = tasks[1]
        assert scan_task.agent_name == "SecurityDeveloper"
        assert scan_task.task_name == "security_scan"
        assert scan_task.command == "security_scan"
        assert scan_task.dependencies == ["build_application"]
        assert scan_task.parameters == {"scan_type": "vulnerability,secrets"}
        
        # Check DevOpsInfra deploy task
        deploy_task = tasks[2]
        assert deploy_task.agent_name == "DevOpsInfra"
        assert deploy_task.task_name == "deploy_application"
        assert deploy_task.command == "deploy_application"
        assert deploy_task.dependencies == ["security_scan"]
        assert deploy_task.parameters == {"environment": "staging"}
        
        # Check TestEngineer smoke test task
        smoke_task = tasks[3]
        assert smoke_task.agent_name == "TestEngineer"
        assert smoke_task.task_name == "smoke_tests"
        assert smoke_task.command == "smoke_tests"
        assert smoke_task.dependencies == ["deploy_application"]
        assert smoke_task.parameters == {"test_scope": "critical_paths"}


class TestWorkflowTypes:
    """Test WorkflowType enum."""
    
    def test_workflow_types(self):
        """Test all workflow types."""
        assert WorkflowType.DEVELOPMENT.value == "development"
        assert WorkflowType.TESTING.value == "testing"
        assert WorkflowType.DEPLOYMENT.value == "deployment"
        assert WorkflowType.MONITORING.value == "monitoring"
        assert WorkflowType.MAINTENANCE.value == "maintenance"


class TestDeploymentEnvironments:
    """Test DeploymentEnvironment enum."""
    
    def test_deployment_environments(self):
        """Test all deployment environments."""
        assert DeploymentEnvironment.DEVELOPMENT.value == "development"
        assert DeploymentEnvironment.STAGING.value == "staging"
        assert DeploymentEnvironment.PRODUCTION.value == "production"


class TestEventHandling:
    """Test event handling in PrefectWorkflowOrchestrator."""
    
    def test_handle_workflow_completion_success(self):
        """Test workflow completion handler for success."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        event = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "success_count": 4,
            "total_count": 4
        }
        
        # Mock publish function
        with patch('bmad.agents.core.prefect_workflow.publish') as mock_publish:
            orchestrator._handle_workflow_completion(event)
            
            # Should publish workflow_success event
            mock_publish.assert_called_with("workflow_success", event)
    
    def test_handle_workflow_completion_partial(self):
        """Test workflow completion handler for partial success."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        event = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "success_count": 2,
            "total_count": 4
        }
        
        # Mock publish function
        with patch('bmad.agents.core.prefect_workflow.publish') as mock_publish:
            orchestrator._handle_workflow_completion(event)
            
            # Should publish workflow_partial_success event
            mock_publish.assert_called_with("workflow_partial_success", event)
    
    def test_handle_workflow_completion_failure(self):
        """Test workflow completion handler for failure."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        event = {
            "workflow_name": "test_workflow",
            "run_id": "test-run-123",
            "success_count": 0,
            "total_count": 4
        }
        
        # Mock publish function
        with patch('bmad.agents.core.prefect_workflow.publish') as mock_publish:
            orchestrator._handle_workflow_completion(event)
            
            # Should publish workflow_failure event
            mock_publish.assert_called_with("workflow_failure", event)
    
    def test_handle_deployment_request(self):
        """Test deployment request handler."""
        orchestrator = PrefectWorkflowOrchestrator()
        
        event = {
            "workflow_name": "test_workflow",
            "environment": "staging"
        }
        
        # Mock publish function
        with patch('bmad.agents.core.prefect_workflow.publish') as mock_publish:
            orchestrator._handle_deployment_request(event)
            
            # Should publish deployment_triggered event
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0]
            assert call_args[0] == "deployment_triggered"
            assert call_args[1]["workflow_name"] == "test_workflow"
            assert call_args[1]["environment"] == "staging" 