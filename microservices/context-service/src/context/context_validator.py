"""
Context Validator

This module provides validation functionality for context data and operations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Result of validation operation."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class ContextValidator:
    """Validates context data and operations."""
    
    def __init__(self):
        self.max_context_size_mb = 100.0  # Maximum context size in MB
        self.max_layer_count = 50  # Maximum number of layers per context
        self.max_metadata_keys = 100  # Maximum number of metadata keys
        self.max_tag_count = 20  # Maximum number of tags
        
    def validate_context_data(self, context_data: Dict[str, Any]) -> ValidationResult:
        """Validate context creation/update data."""
        result = ValidationResult()
        
        try:
            # Required fields
            required_fields = ['name', 'type']
            for field in required_fields:
                if field not in context_data:
                    result.errors.append(f"Missing required field: {field}")
                    
            # Name validation
            if 'name' in context_data:
                name = context_data['name']
                if not isinstance(name, str):
                    result.errors.append("Name must be a string")
                elif len(name.strip()) == 0:
                    result.errors.append("Name cannot be empty")
                elif len(name) > 255:
                    result.errors.append("Name too long (max 255 characters)")
                    
            # Type validation
            if 'type' in context_data:
                context_type = context_data['type']
                if not isinstance(context_type, str):
                    result.errors.append("Type must be a string")
                elif len(context_type.strip()) == 0:
                    result.errors.append("Type cannot be empty")
                elif len(context_type) > 100:
                    result.errors.append("Type too long (max 100 characters)")
                    
            # Status validation
            if 'status' in context_data:
                status = context_data['status']
                valid_statuses = ['active', 'inactive', 'archived', 'deleted']
                if status not in valid_statuses:
                    result.errors.append(f"Invalid status. Must be one of: {valid_statuses}")
                    
            # Metadata validation
            if 'metadata' in context_data:
                metadata = context_data['metadata']
                if not isinstance(metadata, dict):
                    result.errors.append("Metadata must be a dictionary")
                else:
                    # Check metadata size
                    metadata_size = len(json.dumps(metadata))
                    if metadata_size > 1024 * 1024:  # 1MB limit
                        result.errors.append("Metadata too large (max 1MB)")
                        
                    # Check number of keys
                    if len(metadata) > self.max_metadata_keys:
                        result.errors.append(f"Too many metadata keys (max {self.max_metadata_keys})")
                        
                    # Validate metadata values
                    for key, value in metadata.items():
                        if not isinstance(key, str):
                            result.errors.append("Metadata keys must be strings")
                            break
                        if len(key) > 100:
                            result.errors.append(f"Metadata key too long: {key}")
                            break
                            
            # Tags validation
            if 'tags' in context_data:
                tags = context_data['tags']
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
                            
            # Size validation
            if 'size_mb' in context_data:
                size_mb = context_data['size_mb']
                if not isinstance(size_mb, (int, float)):
                    result.errors.append("Size must be a number")
                elif size_mb < 0:
                    result.errors.append("Size cannot be negative")
                elif size_mb > self.max_context_size_mb:
                    result.errors.append(f"Size too large (max {self.max_context_size_mb}MB)")
                    
            # Layer count validation
            if 'layer_count' in context_data:
                layer_count = context_data['layer_count']
                if not isinstance(layer_count, int):
                    result.errors.append("Layer count must be an integer")
                elif layer_count < 0:
                    result.errors.append("Layer count cannot be negative")
                elif layer_count > self.max_layer_count:
                    result.errors.append(f"Layer count too high (max {self.max_layer_count})")
                    
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_layer_data(self, layer_data: Dict[str, Any]) -> ValidationResult:
        """Validate context layer data."""
        result = ValidationResult()
        
        try:
            # Required fields
            required_fields = ['layer_type', 'data']
            for field in required_fields:
                if field not in layer_data:
                    result.errors.append(f"Missing required field: {field}")
                    
            # Layer type validation
            if 'layer_type' in layer_data:
                layer_type = layer_data['layer_type']
                if not isinstance(layer_type, str):
                    result.errors.append("Layer type must be a string")
                elif len(layer_type.strip()) == 0:
                    result.errors.append("Layer type cannot be empty")
                elif len(layer_type) > 100:
                    result.errors.append("Layer type too long (max 100 characters)")
                    
            # Data validation
            if 'data' in layer_data:
                data = layer_data['data']
                if not isinstance(data, dict):
                    result.errors.append("Layer data must be a dictionary")
                else:
                    # Check data size
                    data_size = len(json.dumps(data))
                    if data_size > 10 * 1024 * 1024:  # 10MB limit
                        result.errors.append("Layer data too large (max 10MB)")
                        
                    # Validate data structure
                    self._validate_data_structure(data, result)
                    
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def _validate_data_structure(self, data: Any, result: ValidationResult, depth: int = 0):
        """Recursively validate data structure."""
        if depth > 10:  # Prevent infinite recursion
            result.errors.append("Data structure too deep (max 10 levels)")
            return
            
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, str):
                    result.errors.append("Dictionary keys must be strings")
                    return
                if len(key) > 100:
                    result.errors.append(f"Dictionary key too long: {key}")
                    return
                self._validate_data_structure(value, result, depth + 1)
                
        elif isinstance(data, list):
            if len(data) > 1000:  # Limit list size
                result.errors.append("List too large (max 1000 items)")
                return
            for item in data:
                self._validate_data_structure(item, result, depth + 1)
                
        elif isinstance(data, (str, int, float, bool, type(None))):
            # Basic types are valid
            pass
        else:
            result.errors.append(f"Unsupported data type: {type(data)}")
            
    def validate_context_id(self, context_id: str) -> ValidationResult:
        """Validate context ID format."""
        result = ValidationResult()
        
        if not isinstance(context_id, str):
            result.errors.append("Context ID must be a string")
        elif len(context_id.strip()) == 0:
            result.errors.append("Context ID cannot be empty")
        elif len(context_id) > 255:
            result.errors.append("Context ID too long (max 255 characters)")
        elif not context_id.replace('-', '').replace('_', '').isalnum():
            result.errors.append("Context ID contains invalid characters")
            
        result.is_valid = len(result.errors) == 0
        return result
        
    def validate_layer_id(self, layer_id: str) -> ValidationResult:
        """Validate layer ID format."""
        result = ValidationResult()
        
        if not isinstance(layer_id, str):
            result.errors.append("Layer ID must be a string")
        elif len(layer_id.strip()) == 0:
            result.errors.append("Layer ID cannot be empty")
        elif len(layer_id) > 255:
            result.errors.append("Layer ID too long (max 255 characters)")
        elif not layer_id.replace('-', '').replace('_', '').isalnum():
            result.errors.append("Layer ID contains invalid characters")
            
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
        
    def sanitize_context_data(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context data by removing invalid fields and normalizing values."""
        sanitized = {}
        
        # Copy valid fields
        valid_fields = ['name', 'type', 'status', 'metadata', 'tags', 'size_mb', 'layer_count']
        for field in valid_fields:
            if field in context_data:
                sanitized[field] = context_data[field]
                
        # Normalize string fields
        if 'name' in sanitized:
            sanitized['name'] = sanitized['name'].strip()
            
        if 'type' in sanitized:
            sanitized['type'] = sanitized['type'].strip()
            
        if 'status' in sanitized:
            sanitized['status'] = sanitized['status'].lower()
            
        # Normalize tags
        if 'tags' in sanitized:
            tags = sanitized['tags']
            if isinstance(tags, list):
                sanitized['tags'] = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
                
        return sanitized
        
    def sanitize_layer_data(self, layer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize layer data."""
        sanitized = {}
        
        # Copy valid fields
        valid_fields = ['layer_type', 'data']
        for field in valid_fields:
            if field in layer_data:
                sanitized[field] = layer_data[field]
                
        # Normalize layer type
        if 'layer_type' in sanitized:
            sanitized['layer_type'] = sanitized['layer_type'].strip()
            
        return sanitized 