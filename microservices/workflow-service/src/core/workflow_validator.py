"""
Workflow Validator

This module provides validation functionality for workflow data and operations.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import json
from pydantic import BaseModel, ValidationError

from .workflow_manager import WorkflowType, WorkflowStatus

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Result of validation operation."""
    is_valid: bool = False
    errors: List[str] = []
    warnings: List[str] = []

class WorkflowValidator:
    """Validates workflow data and operations."""
    
    def __init__(self):
        self.max_workflow_steps = 100  # Maximum number of steps per workflow
        self.max_step_name_length = 255  # Maximum step name length
        self.max_workflow_name_length = 255  # Maximum workflow name length
        self.max_description_length = 1000  # Maximum description length
        self.max_config_size = 1024 * 1024  # Maximum config size in bytes
        self.max_metadata_size = 1024 * 1024  # Maximum metadata size in bytes
        self.max_tag_count = 20  # Maximum number of tags
        
    def validate_workflow_data(self, workflow_data: Dict[str, Any]) -> ValidationResult:
        """Validate workflow creation/update data."""
        result = ValidationResult()
        
        try:
            # Required fields
            required_fields = ['name', 'workflow_type']
            for field in required_fields:
                if field not in workflow_data:
                    result.errors.append(f"Missing required field: {field}")
                    
            # Name validation
            if 'name' in workflow_data:
                name = workflow_data['name']
                if not isinstance(name, str):
                    result.errors.append("Name must be a string")
                elif len(name.strip()) == 0:
                    result.errors.append("Name cannot be empty")
                elif len(name) > self.max_workflow_name_length:
                    result.errors.append(f"Name too long (max {self.max_workflow_name_length} characters)")
                    
            # Workflow type validation
            if 'workflow_type' in workflow_data:
                workflow_type = workflow_data['workflow_type']
                if not isinstance(workflow_type, str):
                    result.errors.append("Workflow type must be a string")
                elif workflow_type not in [t.value for t in WorkflowType]:
                    valid_types = [t.value for t in WorkflowType]
                    result.errors.append(f"Invalid workflow type. Must be one of: {valid_types}")
                    
            # Description validation
            if 'description' in workflow_data:
                description = workflow_data['description']
                if description is not None and not isinstance(description, str):
                    result.errors.append("Description must be a string or null")
                elif description and len(description) > self.max_description_length:
                    result.errors.append(f"Description too long (max {self.max_description_length} characters)")
                    
            # Status validation
            if 'status' in workflow_data:
                status = workflow_data['status']
                if not isinstance(status, str):
                    result.errors.append("Status must be a string")
                elif status not in [s.value for s in WorkflowStatus]:
                    valid_statuses = [s.value for s in WorkflowStatus]
                    result.errors.append(f"Invalid status. Must be one of: {valid_statuses}")
                    
            # Config validation
            if 'config' in workflow_data:
                config = workflow_data['config']
                if not isinstance(config, dict):
                    result.errors.append("Config must be a dictionary")
                else:
                    config_size = len(json.dumps(config))
                    if config_size > self.max_config_size:
                        result.errors.append(f"Config too large (max {self.max_config_size} bytes)")
                        
            # Metadata validation
            if 'metadata' in workflow_data:
                metadata = workflow_data['metadata']
                if not isinstance(metadata, dict):
                    result.errors.append("Metadata must be a dictionary")
                else:
                    metadata_size = len(json.dumps(metadata))
                    if metadata_size > self.max_metadata_size:
                        result.errors.append(f"Metadata too large (max {self.max_metadata_size} bytes)")
                        
            # Tags validation
            if 'tags' in workflow_data:
                tags = workflow_data['tags']
                if not isinstance(tags, list):
                    result.errors.append("Tags must be a list")
                else:
                    if len(tags) > self.max_tag_count:
                        result.errors.append(f"Too many tags (max {self.max_tag_count})")
                        
                    for tag in tags:
                        if not isinstance(tag, str):
                            result.errors.append("All tags must be strings")
                            break
                        if len(tag.strip()) == 0:
                            result.errors.append("Tags cannot be empty")
                            break
                        if len(tag) > 50:
                            result.errors.append(f"Tag too long: {tag}")
                            break
                            
            # Steps validation
            if 'steps' in workflow_data:
                steps = workflow_data['steps']
                if not isinstance(steps, list):
                    result.errors.append("Steps must be a list")
                else:
                    if len(steps) > self.max_workflow_steps:
                        result.errors.append(f"Too many steps (max {self.max_workflow_steps})")
                        
                    # Validate each step
                    step_ids = set()
                    for i, step in enumerate(steps):
                        step_result = self.validate_step_data(step, i)
                        result.errors.extend(step_result.errors)
                        result.warnings.extend(step_result.warnings)
                        
                        # Check for duplicate step IDs
                        if 'id' in step:
                            step_id = step['id']
                            if step_id in step_ids:
                                result.errors.append(f"Duplicate step ID: {step_id}")
                            else:
                                step_ids.add(step_id)
                                
                    # Validate step dependencies
                    if not result.errors:
                        dependency_result = self.validate_step_dependencies(steps)
                        result.errors.extend(dependency_result.errors)
                        result.warnings.extend(dependency_result.warnings)
                        
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_step_data(self, step_data: Dict[str, Any], step_index: int) -> ValidationResult:
        """Validate workflow step data."""
        result = ValidationResult()
        
        try:
            # Required fields
            required_fields = ['name', 'step_type']
            for field in required_fields:
                if field not in step_data:
                    result.errors.append(f"Step {step_index}: Missing required field: {field}")
                    
            # Name validation
            if 'name' in step_data:
                name = step_data['name']
                if not isinstance(name, str):
                    result.errors.append(f"Step {step_index}: Name must be a string")
                elif len(name.strip()) == 0:
                    result.errors.append(f"Step {step_index}: Name cannot be empty")
                elif len(name) > self.max_step_name_length:
                    result.errors.append(f"Step {step_index}: Name too long (max {self.max_step_name_length} characters)")
                    
            # Step type validation
            if 'step_type' in step_data:
                step_type = step_data['step_type']
                if not isinstance(step_type, str):
                    result.errors.append(f"Step {step_index}: Step type must be a string")
                elif len(step_type.strip()) == 0:
                    result.errors.append(f"Step {step_index}: Step type cannot be empty")
                elif len(step_type) > 100:
                    result.errors.append(f"Step {step_index}: Step type too long (max 100 characters)")
                    
            # Agent ID validation
            if 'agent_id' in step_data:
                agent_id = step_data['agent_id']
                if agent_id is not None and not isinstance(agent_id, str):
                    result.errors.append(f"Step {step_index}: Agent ID must be a string or null")
                elif agent_id and len(agent_id.strip()) == 0:
                    result.errors.append(f"Step {step_index}: Agent ID cannot be empty")
                    
            # Config validation
            if 'config' in step_data:
                config = step_data['config']
                if not isinstance(config, dict):
                    result.errors.append(f"Step {step_index}: Config must be a dictionary")
                else:
                    config_size = len(json.dumps(config))
                    if config_size > 1024 * 1024:  # 1MB limit for step config
                        result.errors.append(f"Step {step_index}: Config too large (max 1MB)")
                        
            # Dependencies validation
            if 'dependencies' in step_data:
                dependencies = step_data['dependencies']
                if not isinstance(dependencies, list):
                    result.errors.append(f"Step {step_index}: Dependencies must be a list")
                else:
                    for dep in dependencies:
                        if not isinstance(dep, str):
                            result.errors.append(f"Step {step_index}: All dependencies must be strings")
                            break
                        if len(dep.strip()) == 0:
                            result.errors.append(f"Step {step_index}: Dependencies cannot be empty")
                            break
                            
            # Timeout validation
            if 'timeout_seconds' in step_data:
                timeout = step_data['timeout_seconds']
                if not isinstance(timeout, int):
                    result.errors.append(f"Step {step_index}: Timeout must be an integer")
                elif timeout < 1:
                    result.errors.append(f"Step {step_index}: Timeout must be positive")
                elif timeout > 3600:  # 1 hour max
                    result.errors.append(f"Step {step_index}: Timeout too high (max 3600 seconds)")
                    
            # Retry count validation
            if 'retry_count' in step_data:
                retry_count = step_data['retry_count']
                if not isinstance(retry_count, int):
                    result.errors.append(f"Step {step_index}: Retry count must be an integer")
                elif retry_count < 0:
                    result.errors.append(f"Step {step_index}: Retry count cannot be negative")
                elif retry_count > 10:  # Max 10 retries
                    result.errors.append(f"Step {step_index}: Retry count too high (max 10)")
                    
        except Exception as e:
            result.errors.append(f"Step {step_index}: Validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_step_dependencies(self, steps: List[Dict[str, Any]]) -> ValidationResult:
        """Validate step dependencies and detect cycles."""
        result = ValidationResult()
        
        try:
            # Build dependency graph
            dependency_graph = {}
            step_ids = set()
            
            for step in steps:
                step_id = step.get('id', '')
                if step_id:
                    step_ids.add(step_id)
                    dependencies = step.get('dependencies', [])
                    dependency_graph[step_id] = dependencies
                    
            # Check for invalid dependencies
            for step_id, dependencies in dependency_graph.items():
                for dep in dependencies:
                    if dep not in step_ids:
                        result.errors.append(f"Step {step_id} depends on non-existent step: {dep}")
                        
            # Check for self-dependencies
            for step_id, dependencies in dependency_graph.items():
                if step_id in dependencies:
                    result.errors.append(f"Step {step_id} cannot depend on itself")
                    
            # Check for cycles using DFS
            if not result.errors:
                visited = set()
                rec_stack = set()
                
                def has_cycle(node):
                    visited.add(node)
                    rec_stack.add(node)
                    
                    for neighbor in dependency_graph.get(node, []):
                        if neighbor not in visited:
                            if has_cycle(neighbor):
                                return True
                        elif neighbor in rec_stack:
                            return True
                            
                    rec_stack.remove(node)
                    return False
                    
                for step_id in step_ids:
                    if step_id not in visited:
                        if has_cycle(step_id):
                            result.errors.append(f"Circular dependency detected involving step: {step_id}")
                            break
                            
        except Exception as e:
            result.errors.append(f"Dependency validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_execution_data(self, execution_data: Dict[str, Any]) -> ValidationResult:
        """Validate workflow execution data."""
        result = ValidationResult()
        
        try:
            # Required fields
            required_fields = ['workflow_id']
            for field in required_fields:
                if field not in execution_data:
                    result.errors.append(f"Missing required field: {field}")
                    
            # Workflow ID validation
            if 'workflow_id' in execution_data:
                workflow_id = execution_data['workflow_id']
                if not isinstance(workflow_id, str):
                    result.errors.append("Workflow ID must be a string")
                elif len(workflow_id.strip()) == 0:
                    result.errors.append("Workflow ID cannot be empty")
                    
            # Input data validation
            if 'input_data' in execution_data:
                input_data = execution_data['input_data']
                if not isinstance(input_data, dict):
                    result.errors.append("Input data must be a dictionary")
                else:
                    input_size = len(json.dumps(input_data))
                    if input_size > 10 * 1024 * 1024:  # 10MB limit
                        result.errors.append("Input data too large (max 10MB)")
                        
        except Exception as e:
            result.errors.append(f"Execution validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_workflow_id(self, workflow_id: str) -> ValidationResult:
        """Validate workflow ID format."""
        result = ValidationResult()
        
        if not isinstance(workflow_id, str):
            result.errors.append("Workflow ID must be a string")
        elif len(workflow_id.strip()) == 0:
            result.errors.append("Workflow ID cannot be empty")
        elif len(workflow_id) > 255:
            result.errors.append("Workflow ID too long (max 255 characters)")
        elif not workflow_id.replace('-', '').replace('_', '').isalnum():
            result.errors.append("Workflow ID contains invalid characters")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_execution_id(self, execution_id: str) -> ValidationResult:
        """Validate execution ID format."""
        result = ValidationResult()
        
        if not isinstance(execution_id, str):
            result.errors.append("Execution ID must be a string")
        elif len(execution_id.strip()) == 0:
            result.errors.append("Execution ID cannot be empty")
        elif len(execution_id) > 255:
            result.errors.append("Execution ID too long (max 255 characters)")
        elif not execution_id.replace('-', '').replace('_', '').isalnum():
            result.errors.append("Execution ID contains invalid characters")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_search_query(self, query: str) -> ValidationResult:
        """Validate search query."""
        result = ValidationResult()
        
        if not isinstance(query, str):
            result.errors.append("Search query must be a string")
        elif len(query.strip()) == 0:
            result.errors.append("Search query cannot be empty")
        elif len(query) > 500:
            result.errors.append("Search query too long (max 500 characters)")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_pagination_params(self, limit: int, offset: int) -> ValidationResult:
        """Validate pagination parameters."""
        result = ValidationResult()
        
        if not isinstance(limit, int):
            result.errors.append("Limit must be an integer")
        elif limit < 1:
            result.errors.append("Limit must be positive")
        elif limit > 1000:
            result.errors.append("Limit too high (max 1000)")
            
        if not isinstance(offset, int):
            result.errors.append("Offset must be an integer")
        elif offset < 0:
            result.errors.append("Offset cannot be negative")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def sanitize_workflow_data(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize workflow data by removing invalid fields and normalizing values."""
        sanitized = {}
        
        # Copy valid fields
        valid_fields = ['name', 'description', 'workflow_type', 'status', 'config', 'metadata', 'tags', 'steps']
        for field in valid_fields:
            if field in workflow_data:
                sanitized[field] = workflow_data[field]
                
        # Normalize string fields
        if 'name' in sanitized:
            sanitized['name'] = sanitized['name'].strip()
            
        if 'description' in sanitized and sanitized['description']:
            sanitized['description'] = sanitized['description'].strip()
            
        if 'workflow_type' in sanitized:
            sanitized['workflow_type'] = sanitized['workflow_type'].strip()
            
        if 'status' in sanitized:
            sanitized['status'] = sanitized['status'].lower()
            
        # Normalize tags
        if 'tags' in sanitized:
            tags = sanitized['tags']
            if isinstance(tags, list):
                sanitized['tags'] = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
                
        # Sanitize steps
        if 'steps' in sanitized:
            steps = sanitized['steps']
            if isinstance(steps, list):
                sanitized_steps = []
                for step in steps:
                    if isinstance(step, dict):
                        sanitized_step = {}
                        step_fields = ['id', 'name', 'step_type', 'agent_id', 'config', 'dependencies', 'timeout_seconds', 'retry_count']
                        for field in step_fields:
                            if field in step:
                                sanitized_step[field] = step[field]
                                
                        # Normalize step name
                        if 'name' in sanitized_step:
                            sanitized_step['name'] = sanitized_step['name'].strip()
                            
                        # Normalize step type
                        if 'step_type' in sanitized_step:
                            sanitized_step['step_type'] = sanitized_step['step_type'].strip()
                            
                        sanitized_steps.append(sanitized_step)
                sanitized['steps'] = sanitized_steps
                
        return sanitized
        
    def sanitize_execution_data(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize execution data."""
        sanitized = {}
        
        # Copy valid fields
        valid_fields = ['workflow_id', 'input_data']
        for field in valid_fields:
            if field in execution_data:
                sanitized[field] = execution_data[field]
                
        # Normalize workflow ID
        if 'workflow_id' in sanitized:
            sanitized['workflow_id'] = sanitized['workflow_id'].strip()
            
        return sanitized 