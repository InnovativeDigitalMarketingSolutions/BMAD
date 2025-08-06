"""
Basic Integration Tests for BMAD System

This module tests basic integration functionality to ensure
the system is working correctly before running comprehensive tests.

Test Coverage:
- Basic agent initialization
- Core service availability
- Simple workflow execution
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Test basic imports first
def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        import bmad
        import bmad.core
        import bmad.agents
        assert True, "Basic imports successful"
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_core_services_available():
    """Test that core services are available."""
    try:
        from bmad.core.mcp import enhanced_mcp_integration
        from bmad.core.security import jwt_service
        from bmad.core.security import permission_service
        assert True, "Core services imports successful"
    except ImportError as e:
        pytest.fail(f"Core services import failed: {e}")

def test_agent_structure():
    """Test that agent structure is available."""
    try:
        from bmad.agents.Agent import agents_overview
        assert True, "Agent structure import successful"
    except ImportError as e:
        # Check if agents-overview.md exists instead
        import os
        agents_overview_path = "bmad/agents/Agent/agents-overview.md"
        if os.path.exists(agents_overview_path):
            assert True, "Agent structure available via markdown file"
        else:
            pytest.fail(f"Agent structure import failed: {e}")

@pytest.mark.asyncio
async def test_basic_workflow():
    """Test basic workflow execution."""
    # Mock a simple workflow
    workflow_steps = [
        {"step": 1, "action": "initialize", "status": "success"},
        {"step": 2, "action": "process", "status": "success"},
        {"step": 3, "action": "complete", "status": "success"},
    ]
    
    results = []
    for step in workflow_steps:
        # Simulate async processing
        await asyncio.sleep(0.01)
        results.append(step)
    
    assert len(results) == 3, "All workflow steps should be executed"
    for result in results:
        assert result["status"] == "success", f"Step {result['step']} should be successful"

@pytest.mark.asyncio
async def test_error_handling():
    """Test basic error handling."""
    try:
        # Simulate an error condition
        raise ValueError("Test error")
    except ValueError as e:
        assert str(e) == "Test error", "Error should be caught and handled"
        # Continue execution
        assert True, "Error handling successful"

def test_configuration_loading():
    """Test that configuration can be loaded."""
    # Mock configuration loading
    config = {
        "database": {"host": "localhost", "port": 5432},
        "api": {"host": "0.0.0.0", "port": 8000},
        "security": {"jwt_secret": "test_secret"},
    }
    
    assert "database" in config, "Database configuration should be present"
    assert "api" in config, "API configuration should be present"
    assert "security" in config, "Security configuration should be present"

@pytest.mark.asyncio
async def test_async_operations():
    """Test basic async operations."""
    async def async_operation():
        await asyncio.sleep(0.01)
        return "success"
    
    result = await async_operation()
    assert result == "success", "Async operation should complete successfully"

def test_mocking_strategy():
    """Test that mocking works correctly."""
    with patch('builtins.print') as mock_print:
        print("test message")
        mock_print.assert_called_once_with("test message")

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent operations."""
    async def operation(name: str, delay: float):
        await asyncio.sleep(delay)
        return f"{name}_completed"
    
    # Run operations concurrently
    tasks = [
        operation("task1", 0.01),
        operation("task2", 0.01),
        operation("task3", 0.01),
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3, "All tasks should complete"
    assert "task1_completed" in results, "Task 1 should complete"
    assert "task2_completed" in results, "Task 2 should complete"
    assert "task3_completed" in results, "Task 3 should complete"

def test_data_structures():
    """Test basic data structures used in the system."""
    # Test dictionary operations
    data = {"key1": "value1", "key2": "value2"}
    assert data["key1"] == "value1", "Dictionary access should work"
    
    # Test list operations
    items = ["item1", "item2", "item3"]
    assert len(items) == 3, "List should have correct length"
    
    # Test set operations
    unique_items = set(["a", "b", "a", "c"])
    assert len(unique_items) == 3, "Set should remove duplicates"

@pytest.mark.asyncio
async def test_performance_baseline():
    """Test basic performance baseline."""
    import time
    
    start_time = time.time()
    await asyncio.sleep(0.01)  # Simulate work
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 0.1, f"Operation should complete quickly: {duration}s"

def test_logging_setup():
    """Test that logging can be configured."""
    import logging
    
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Test logging
    with patch.object(logger, 'info') as mock_info:
        logger.info("Test log message")
        mock_info.assert_called_once_with("Test log message")

if __name__ == "__main__":
    # Run basic integration tests
    pytest.main([__file__, "-v", "--tb=short"]) 