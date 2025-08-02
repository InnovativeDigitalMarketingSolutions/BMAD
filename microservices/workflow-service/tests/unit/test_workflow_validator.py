"""
Unit tests for WorkflowValidator
"""

import pytest
from src.core.workflow_validator import WorkflowValidator, ValidationResult


class TestWorkflowValidator:
    """Test cases for WorkflowValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a WorkflowValidator instance for testing."""
        return WorkflowValidator()
        
    @pytest.fixture
    def valid_workflow_data(self):
        """Valid workflow data for testing."""
        return {
            "name": "Test Workflow",
            "workflow_type": "sequential",
            "description": "A test workflow",
            "steps": [
                {
                    "name": "Step 1",
                    "step_type": "agent_execution",
                    "agent_id": "agent_001",
                    "config": {"timeout": 30},
                    "dependencies": [],
                    "timeout_seconds": 300,
                    "retry_count": 3
                }
            ],
            "config": {"max_retries": 3},
            "metadata": {"created_by": "test_user"},
            "tags": ["test", "workflow"]
        }
        
    def test_validate_workflow_data_valid(self, validator, valid_workflow_data):
        """Test validation of valid workflow data."""
        result = validator.validate_workflow_data(valid_workflow_data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_workflow_data_missing_required_fields(self, validator):
        """Test validation with missing required fields."""
        invalid_data = {
            "description": "Missing name and type"
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert len(result.errors) >= 2
        assert any("Missing required field: name" in error for error in result.errors)
        assert any("Missing required field: workflow_type" in error for error in result.errors)
        
    def test_validate_workflow_data_invalid_name(self, validator):
        """Test validation with invalid name."""
        invalid_data = {
            "name": "",  # Empty name
            "workflow_type": "sequential"
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert any("Name cannot be empty" in error for error in result.errors)
        
    def test_validate_workflow_data_invalid_workflow_type(self, validator):
        """Test validation with invalid workflow type."""
        invalid_data = {
            "name": "Test Workflow",
            "workflow_type": "invalid_type"
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert any("Invalid workflow type" in error for error in result.errors)
        
    def test_validate_workflow_data_invalid_status(self, validator):
        """Test validation with invalid status."""
        invalid_data = {
            "name": "Test Workflow",
            "workflow_type": "sequential",
            "status": "invalid_status"
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert any("Invalid status" in error for error in result.errors)
        
    def test_validate_workflow_data_invalid_metadata(self, validator):
        """Test validation with invalid metadata."""
        invalid_data = {
            "name": "Test Workflow",
            "workflow_type": "sequential",
            "metadata": "not_a_dict"  # Should be dict
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert any("Metadata must be a dictionary" in error for error in result.errors)
        
    def test_validate_workflow_data_invalid_tags(self, validator):
        """Test validation with invalid tags."""
        invalid_data = {
            "name": "Test Workflow",
            "workflow_type": "sequential",
            "tags": "not_a_list"  # Should be list
        }
        
        result = validator.validate_workflow_data(invalid_data)
        
        assert result.is_valid is False
        assert any("Tags must be a list" in error for error in result.errors)
        
    def test_validate_step_data_valid(self, validator):
        """Test validation of valid step data."""
        valid_step_data = {
            "name": "Test Step",
            "step_type": "agent_execution",
            "agent_id": "agent_001",
            "config": {"timeout": 30},
            "dependencies": [],
            "timeout_seconds": 300,
            "retry_count": 3
        }
        
        result = validator.validate_step_data(valid_step_data, 0)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_step_data_missing_required_fields(self, validator):
        """Test validation with missing required step fields."""
        invalid_step_data = {
            "agent_id": "agent_001"  # Missing name and step_type
        }
        
        result = validator.validate_step_data(invalid_step_data, 0)
        
        assert result.is_valid is False
        assert len(result.errors) >= 2
        assert any("Missing required field: name" in error for error in result.errors)
        assert any("Missing required field: step_type" in error for error in result.errors)
        
    def test_validate_step_data_invalid_timeout(self, validator):
        """Test validation with invalid timeout."""
        invalid_step_data = {
            "name": "Test Step",
            "step_type": "agent_execution",
            "timeout_seconds": -1  # Negative timeout
        }
        
        result = validator.validate_step_data(invalid_step_data, 0)
        
        assert result.is_valid is False
        assert any("Timeout must be positive" in error for error in result.errors)
        
    def test_validate_step_data_invalid_retry_count(self, validator):
        """Test validation with invalid retry count."""
        invalid_step_data = {
            "name": "Test Step",
            "step_type": "agent_execution",
            "retry_count": -1  # Negative retry count
        }
        
        result = validator.validate_step_data(invalid_step_data, 0)
        
        assert result.is_valid is False
        assert any("Retry count cannot be negative" in error for error in result.errors)
        
    def test_validate_step_dependencies_valid(self, validator):
        """Test validation of valid step dependencies."""
        valid_steps = [
            {
                "id": "step1",
                "name": "Step 1",
                "step_type": "test",
                "dependencies": []
            },
            {
                "id": "step2",
                "name": "Step 2",
                "step_type": "test",
                "dependencies": ["step1"]
            }
        ]
        
        result = validator.validate_step_dependencies(valid_steps)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_step_dependencies_invalid_dependency(self, validator):
        """Test validation with invalid dependency."""
        invalid_steps = [
            {
                "id": "step1",
                "name": "Step 1",
                "step_type": "test",
                "dependencies": ["non_existent_step"]
            }
        ]
        
        result = validator.validate_step_dependencies(invalid_steps)
        
        assert result.is_valid is False
        assert any("depends on non-existent step" in error for error in result.errors)
        
    def test_validate_step_dependencies_self_dependency(self, validator):
        """Test validation with self-dependency."""
        invalid_steps = [
            {
                "id": "step1",
                "name": "Step 1",
                "step_type": "test",
                "dependencies": ["step1"]  # Self-dependency
            }
        ]
        
        result = validator.validate_step_dependencies(invalid_steps)
        
        assert result.is_valid is False
        assert any("cannot depend on itself" in error for error in result.errors)
        
    def test_validate_step_dependencies_circular_dependency(self, validator):
        """Test validation with circular dependency."""
        invalid_steps = [
            {
                "id": "step1",
                "name": "Step 1",
                "step_type": "test",
                "dependencies": ["step2"]
            },
            {
                "id": "step2",
                "name": "Step 2",
                "step_type": "test",
                "dependencies": ["step1"]  # Circular dependency
            }
        ]
        
        result = validator.validate_step_dependencies(invalid_steps)
        
        assert result.is_valid is False
        assert any("Circular dependency detected" in error for error in result.errors)
        
    def test_validate_execution_data_valid(self, validator):
        """Test validation of valid execution data."""
        valid_execution_data = {
            "workflow_id": "workflow_001",
            "input_data": {"test_input": "value"}
        }
        
        result = validator.validate_execution_data(valid_execution_data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_execution_data_missing_workflow_id(self, validator):
        """Test validation with missing workflow ID."""
        invalid_execution_data = {
            "input_data": {"test_input": "value"}
        }
        
        result = validator.validate_execution_data(invalid_execution_data)
        
        assert result.is_valid is False
        assert any("Missing required field: workflow_id" in error for error in result.errors)
        
    def test_validate_execution_data_invalid_input_data(self, validator):
        """Test validation with invalid input data."""
        invalid_execution_data = {
            "workflow_id": "workflow_001",
            "input_data": "not_a_dict"  # Should be dict
        }
        
        result = validator.validate_execution_data(invalid_execution_data)
        
        assert result.is_valid is False
        assert any("Input data must be a dictionary" in error for error in result.errors)
        
    def test_validate_workflow_id_valid(self, validator):
        """Test validation of valid workflow ID."""
        result = validator.validate_workflow_id("workflow_001")
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_workflow_id_empty(self, validator):
        """Test validation with empty workflow ID."""
        result = validator.validate_workflow_id("")
        
        assert result.is_valid is False
        assert any("Workflow ID cannot be empty" in error for error in result.errors)
        
    def test_validate_workflow_id_invalid_characters(self, validator):
        """Test validation with invalid characters in workflow ID."""
        result = validator.validate_workflow_id("workflow@001")  # Invalid character @
        
        assert result.is_valid is False
        assert any("contains invalid characters" in error for error in result.errors)
        
    def test_validate_execution_id_valid(self, validator):
        """Test validation of valid execution ID."""
        result = validator.validate_execution_id("execution_001")
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_execution_id_empty(self, validator):
        """Test validation with empty execution ID."""
        result = validator.validate_execution_id("")
        
        assert result.is_valid is False
        assert any("Execution ID cannot be empty" in error for error in result.errors)
        
    def test_validate_search_query_valid(self, validator):
        """Test validation of valid search query."""
        result = validator.validate_search_query("test query")
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_search_query_empty(self, validator):
        """Test validation with empty search query."""
        result = validator.validate_search_query("")
        
        assert result.is_valid is False
        assert any("Search query cannot be empty" in error for error in result.errors)
        
    def test_validate_search_query_too_long(self, validator):
        """Test validation with search query too long."""
        long_query = "a" * 501  # 501 characters, over 500 limit
        result = validator.validate_search_query(long_query)
        
        assert result.is_valid is False
        assert any("Search query too long" in error for error in result.errors)
        
    def test_validate_pagination_params_valid(self, validator):
        """Test validation of valid pagination parameters."""
        result = validator.validate_pagination_params(limit=10, offset=0)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_pagination_params_invalid_limit(self, validator):
        """Test validation with invalid limit."""
        result = validator.validate_pagination_params(limit=0, offset=0)  # Limit must be positive
        
        assert result.is_valid is False
        assert any("Limit must be positive" in error for error in result.errors)
        
    def test_validate_pagination_params_invalid_offset(self, validator):
        """Test validation with invalid offset."""
        result = validator.validate_pagination_params(limit=10, offset=-1)  # Offset cannot be negative
        
        assert result.is_valid is False
        assert any("Offset cannot be negative" in error for error in result.errors)
        
    def test_sanitize_workflow_data(self, validator):
        """Test workflow data sanitization."""
        raw_data = {
            "name": "  Test Workflow  ",  # Extra whitespace
            "workflow_type": "  sequential  ",  # Extra whitespace
            "description": "  Test description  ",  # Extra whitespace
            "tags": ["  tag1  ", "tag2", "  tag3  "],  # Extra whitespace
            "invalid_field": "should_be_removed"  # Invalid field
        }
        
        sanitized = validator.sanitize_workflow_data(raw_data)
        
        assert sanitized["name"] == "Test Workflow"
        assert sanitized["workflow_type"] == "sequential"
        assert sanitized["description"] == "Test description"
        assert sanitized["tags"] == ["tag1", "tag2", "tag3"]
        assert "invalid_field" not in sanitized
        
    def test_sanitize_execution_data(self, validator):
        """Test execution data sanitization."""
        raw_data = {
            "workflow_id": "  workflow_001  ",  # Extra whitespace
            "input_data": {"test": "value"},
            "invalid_field": "should_be_removed"  # Invalid field
        }
        
        sanitized = validator.sanitize_execution_data(raw_data)
        
        assert sanitized["workflow_id"] == "workflow_001"
        assert sanitized["input_data"] == {"test": "value"}
        assert "invalid_field" not in sanitized 