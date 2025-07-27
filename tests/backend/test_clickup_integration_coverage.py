"""
Tests for bmad.agents.core.clickup_integration module.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from bmad.agents.core.clickup_integration import ClickUpIntegration


class TestClickUpIntegration:
    """Test ClickUpIntegration class."""
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key', 'CLICKUP_SPACE_ID': 'space123'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                integration = ClickUpIntegration()
                
                assert integration.api_key == "test-key"
                assert integration.enabled is True
                assert integration.space_id == "space123"
                assert integration.folder_id == "folder123"
                assert integration.list_id == "list123"
                assert "Authorization" in integration.headers
                assert "Content-Type" in integration.headers
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                
                assert integration.api_key is None
                assert integration.enabled is False
    
    def test_initialization_with_project_id(self):
        """Test initialization with specific project ID."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                integration = ClickUpIntegration(project_id="custom_project")
                
                assert integration.project_id == "custom_project"
                mock_pm.get_clickup_config.assert_called_with("custom_project")
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    @patch('bmad.agents.core.clickup_integration.save_context')
    @patch('bmad.agents.core.clickup_integration.publish')
    def test_create_project_success(self, mock_publish, mock_save_context, mock_post):
        """Test successful project creation."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "task123"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.create_project("Test Project", "web_app", "Test description")
                
                assert result == "task123"
                mock_post.assert_called_once()
                mock_save_context.assert_called_once()
                mock_publish.assert_called_once()
    
    def test_create_project_disabled(self):
        """Test project creation when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.create_project("Test Project", "web_app")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    def test_create_project_api_error(self, mock_post):
        """Test project creation with API error."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                # Mock API error
                mock_post.side_effect = Exception("API Error")
                
                integration = ClickUpIntegration()
                result = integration.create_project("Test Project", "web_app")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    @patch('bmad.agents.core.clickup_integration.save_context')
    @patch('bmad.agents.core.clickup_integration.publish')
    def test_create_task_success(self, mock_publish, mock_save_context, mock_post):
        """Test successful task creation."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "task456"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.create_task(
                    "Test Project", 
                    "Test Task", 
                    "Task description", 
                    "high", 
                    "user123"
                )
                
                assert result == "task456"
                mock_post.assert_called_once()
                mock_save_context.assert_called_once()
                mock_publish.assert_called_once()
    
    def test_create_task_disabled(self):
        """Test task creation when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.create_task("Test Project", "Test Task", "Description")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.put')
    def test_update_task_status_success(self, mock_put):
        """Test successful task status update."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_put.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.update_task_status("task123", "in progress")
                
                assert result is True
                mock_put.assert_called_once()
    
    def test_update_task_status_disabled(self):
        """Test task status update when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.update_task_status("task123", "in progress")
                
                assert result is False
    
    @patch('bmad.agents.core.clickup_integration.requests.put')
    def test_update_task_status_api_error(self, mock_put):
        """Test task status update with API error."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                # Mock API error
                mock_put.side_effect = Exception("API Error")
                
                integration = ClickUpIntegration()
                result = integration.update_task_status("task123", "in progress")
                
                assert result is False
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    @patch('bmad.agents.core.clickup_integration.save_context')
    def test_sync_project_requirements_success(self, mock_save_context, mock_post):
        """Test successful project requirements sync."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "task789"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                requirements = [
                    {"name": "Requirement 1", "description": "First requirement"},
                    {"name": "Requirement 2", "description": "Second requirement"}
                ]
                
                integration = ClickUpIntegration()
                result = integration.sync_project_requirements("Test Project", requirements)
                
                assert result is True
                assert mock_post.call_count == 2  # One call per requirement
                assert mock_save_context.call_count == 2
    
    def test_sync_project_requirements_disabled(self):
        """Test project requirements sync when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                requirements = [{"name": "Requirement 1", "description": "First requirement"}]
                
                integration = ClickUpIntegration()
                result = integration.sync_project_requirements("Test Project", requirements)
                
                assert result is False
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    @patch('bmad.agents.core.clickup_integration.save_context')
    def test_sync_user_stories_success(self, mock_save_context, mock_post):
        """Test successful user stories sync."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "story123"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                user_stories = [
                    {"title": "Story 1", "description": "First story", "priority": "high"},
                    {"title": "Story 2", "description": "Second story", "priority": "medium"}
                ]
                
                integration = ClickUpIntegration()
                result = integration.sync_user_stories("Test Project", user_stories)
                
                assert result is True
                assert mock_post.call_count == 2  # One call per story
                assert mock_save_context.call_count == 2
    
    def test_sync_user_stories_disabled(self):
        """Test user stories sync when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                user_stories = [{"title": "Story 1", "description": "First story"}]
                
                integration = ClickUpIntegration()
                result = integration.sync_user_stories("Test Project", user_stories)
                
                assert result is False
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_tasks_success(self, mock_get_context, mock_get):
        """Test successful project tasks retrieval."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock project mapping
                mock_get_context.return_value = {
                    "clickup_task_id": "project_task_123"
                }
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tasks": [
                        {"id": "task1", "name": "Task 1", "status": "to do"},
                        {"id": "task2", "name": "Task 2", "status": "in progress"}
                    ]
                }
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.get_project_tasks("Test Project")
                
                assert len(result) == 2
                assert result[0]["id"] == "task1"
                assert result[1]["id"] == "task2"
                mock_get.assert_called_once()
    
    def test_get_project_tasks_disabled(self):
        """Test project tasks retrieval when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.get_project_tasks("Test Project")
                
                assert result == []
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    @patch('bmad.agents.core.clickup_integration.save_context')
    @patch('bmad.agents.core.clickup_integration.publish')
    def test_create_agent_task_success(self, mock_publish, mock_save_context, mock_post):
        """Test successful agent task creation."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "agent_task_123"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.create_agent_task(
                    "Test Project", 
                    "TestEngineer", 
                    "Run automated tests", 
                    4
                )
                
                assert result == "agent_task_123"
                mock_post.assert_called_once()
                mock_save_context.assert_called_once()
                mock_publish.assert_called_once()
    
    def test_create_agent_task_disabled(self):
        """Test agent task creation when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.create_agent_task("Test Project", "TestEngineer", "Run tests")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.put')
    def test_mark_task_completed_success(self, mock_put):
        """Test successful task completion marking."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_put.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.mark_task_completed("task123", "Task completed successfully")
                
                assert result is True
                mock_put.assert_called_once()
    
    def test_mark_task_completed_disabled(self):
        """Test task completion marking when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.mark_task_completed("task123", "Task completed")
                
                assert result is False
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_metrics_success(self, mock_get_context, mock_get):
        """Test successful project metrics retrieval."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock project mapping
                mock_get_context.return_value = {
                    "clickup_task_id": "project_task_123"
                }
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "tasks": [
                        {"id": "task1", "status": "completed", "time_estimate": 3600000},
                        {"id": "task2", "status": "in progress", "time_estimate": 1800000},
                        {"id": "task3", "status": "to do", "time_estimate": 7200000}
                    ]
                }
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.get_project_metrics("Test Project")
                
                assert "total_tasks" in result
                assert "completed_tasks" in result
                assert "in_progress_tasks" in result
                assert "pending_tasks" in result
                assert "total_estimated_hours" in result
                assert result["total_tasks"] == 3
                assert result["completed_tasks"] == 1
                assert result["in_progress_tasks"] == 1
                assert result["pending_tasks"] == 1
                mock_get.assert_called_once()
    
    def test_get_project_metrics_disabled(self):
        """Test project metrics retrieval when integration is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                result = integration.get_project_metrics("Test Project")
                
                assert result == {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "pending_tasks": 0,
                    "total_estimated_hours": 0
                }


class TestClickUpIntegrationErrorHandling:
    """Test error handling in ClickUpIntegration."""
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    def test_create_project_api_error_handling(self, mock_post):
        """Test API error handling in project creation."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                # Mock API error
                mock_post.side_effect = Exception("Network error")
                
                integration = ClickUpIntegration()
                result = integration.create_project("Test Project", "web_app")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    def test_create_task_api_error_handling(self, mock_post):
        """Test API error handling in task creation."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                # Mock API error
                mock_post.side_effect = Exception("Network error")
                
                integration = ClickUpIntegration()
                result = integration.create_task("Test Project", "Test Task", "Description")
                
                assert result is None
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_tasks_api_error_handling(self, mock_get_context, mock_get):
        """Test API error handling in project tasks retrieval."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                # Mock project mapping
                mock_get_context.return_value = {
                    "clickup_task_id": "project_task_123"
                }
                
                # Mock API error
                mock_get.side_effect = Exception("Network error")
                
                integration = ClickUpIntegration()
                result = integration.get_project_tasks("Test Project")
                
                assert result == []
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_metrics_api_error_handling(self, mock_get_context, mock_get):
        """Test API error handling in project metrics retrieval."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                
                # Mock project mapping
                mock_get_context.return_value = {
                    "clickup_task_id": "project_task_123"
                }
                
                # Mock API error
                mock_get.side_effect = Exception("Network error")
                
                integration = ClickUpIntegration()
                result = integration.get_project_metrics("Test Project")
                
                assert result == {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "pending_tasks": 0,
                    "total_estimated_hours": 0
                }


class TestClickUpIntegrationEdgeCases:
    """Test edge cases in ClickUpIntegration."""
    
    def test_initialization_with_missing_config(self):
        """Test initialization with missing ClickUp config."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {}
                
                integration = ClickUpIntegration()
                
                assert integration.space_id is None
                assert integration.folder_id is None
                assert integration.list_id is None
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    def test_create_project_with_empty_description(self, mock_post):
        """Test project creation with empty description."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "task123"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.create_project("Test Project", "web_app", "")
                
                assert result == "task123"
                mock_post.assert_called_once()
    
    @patch('bmad.agents.core.clickup_integration.requests.post')
    def test_create_task_without_assignee(self, mock_post):
        """Test task creation without assignee."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock successful API response
                mock_response = MagicMock()
                mock_response.json.return_value = {"id": "task456"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                integration = ClickUpIntegration()
                result = integration.create_task("Test Project", "Test Task", "Description")
                
                assert result == "task456"
                mock_post.assert_called_once()
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_tasks_without_mapping(self, mock_get_context, mock_get):
        """Test project tasks retrieval without project mapping."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock missing project mapping
                mock_get_context.return_value = None
                
                integration = ClickUpIntegration()
                result = integration.get_project_tasks("Test Project")
                
                assert result == []
                mock_get.assert_not_called()
    
    @patch('bmad.agents.core.clickup_integration.requests.get')
    @patch('bmad.agents.core.clickup_integration.get_context')
    def test_get_project_metrics_without_mapping(self, mock_get_context, mock_get):
        """Test project metrics retrieval without project mapping."""
        with patch.dict(os.environ, {'CLICKUP_API_KEY': 'test-key'}):
            with patch('bmad.agents.core.clickup_integration.project_manager') as mock_pm:
                mock_pm.active_project = "test_project"
                mock_pm.get_clickup_config.return_value = {
                    "space_id": "space123",
                    "folder_id": "folder123",
                    "list_id": "list123"
                }
                mock_pm.get_project_scope.return_value = "test_scope"
                
                # Mock missing project mapping
                mock_get_context.return_value = None
                
                integration = ClickUpIntegration()
                result = integration.get_project_metrics("Test Project")
                
                assert result == {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "pending_tasks": 0,
                    "total_estimated_hours": 0
                }
                mock_get.assert_not_called() 