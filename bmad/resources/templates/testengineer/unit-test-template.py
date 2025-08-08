
"""
Unit Test Template voor BMAD TestEngineer Agent

Dit template bevat een uitgebreide unit test structuur voor het testen van componenten.
Gebruik dit template als basis voor het schrijven van unit tests.

Best Practices:
- Test één functionaliteit per test
- Gebruik beschrijvende test namen
- Test edge cases en error scenarios
- Gebruik fixtures voor setup en teardown
- Houd tests onafhankelijk en idempotent
"""

import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict, List

class TestComponent:
    """Test class voor het component dat we testen."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = {}
    
    def add_data(self, key: str, value: Any) -> bool:
        """Voeg data toe aan het component."""
        if not key or not isinstance(key, str):
            return False
        self.data[key] = value
        return True
    
    def get_data(self, key: str) -> Any:
        """Haal data op uit het component."""
        return self.data.get(key)

# Test Fixtures
@pytest.fixture
def test_component():
    """Fixture voor het test component."""
    return TestComponent("test_component")

@pytest.fixture
def sample_data():
    """Fixture voor test data."""
    return {
        "string_value": "test_string",
        "int_value": 42,
        "list_value": [1, 2, 3],
        "dict_value": {"key": "value"}
    }

# Unit Tests
class TestTestComponent:
    """Test suite voor TestComponent."""
    
    def test_component_initialization(self, test_component):
        """Test component initialisatie."""
        assert test_component.name == "test_component"
        assert test_component.data == {}
        assert isinstance(test_component.data, dict)
    
    def test_add_data_success(self, test_component):
        """Test succesvolle data toevoeging."""
        result = test_component.add_data("test_key", "test_value")
        assert result is True
        assert test_component.data["test_key"] == "test_value"
        assert len(test_component.data) == 1
    
    def test_add_data_invalid_key(self, test_component):
        """Test data toevoeging met ongeldige key."""
        # Test met lege string
        result = test_component.add_data("", "value")
        assert result is False
        assert len(test_component.data) == 0
        
        # Test met None
        result = test_component.add_data(None, "value")
        assert result is False
        assert len(test_component.data) == 0
    
    def test_get_data_existing(self, test_component):
        """Test ophalen van bestaande data."""
        test_component.add_data("existing_key", "existing_value")
        result = test_component.get_data("existing_key")
        assert result == "existing_value"
    
    def test_get_data_nonexistent(self, test_component):
        """Test ophalen van niet-bestaande data."""
        result = test_component.get_data("nonexistent_key")
        assert result is None
    
    def test_multiple_data_operations(self, test_component, sample_data):
        """Test meerdere data operaties."""
        # Voeg meerdere items toe
        for key, value in sample_data.items():
            result = test_component.add_data(key, value)
            assert result is True
        
        # Verifieer alle data
        assert len(test_component.data) == len(sample_data)
        for key, value in sample_data.items():
            assert test_component.get_data(key) == value
    
    @pytest.mark.parametrize("key,value,expected", [
        ("string", "hello", True),
        ("number", 42, True),
        ("list", [1, 2, 3], True),
        ("dict", {"a": 1}, True),
        ("", "value", False),
        (None, "value", False),
    ])
    def test_add_data_parametrized(self, test_component, key, value, expected):
        """Parametrized test voor verschillende data types."""
        result = test_component.add_data(key, value)
        assert result is expected
        
        if expected:
            assert test_component.get_data(key) == value

# Mock Tests
class TestTestComponentWithMocks:
    """Test suite met mock objecten."""
    
    @patch('builtins.print')
    def test_component_with_mock(self, mock_print, test_component):
        """Test component met mock print functie."""
        test_component.add_data("mock_key", "mock_value")
        
        # Simuleer print operatie
        print(f"Component {test_component.name} heeft data: {test_component.data}")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "mock_key" in call_args
        assert "mock_value" in call_args
    
    def test_component_with_mock_object(self):
        """Test met mock object."""
        mock_component = Mock(spec=TestComponent)
        mock_component.name = "mock_component"
        mock_component.data = {"mock_key": "mock_value"}
        mock_component.get_data.return_value = "mock_value"
        
        result = mock_component.get_data("mock_key")
        assert result == "mock_value"
        mock_component.get_data.assert_called_once_with("mock_key")

# Error Handling Tests
class TestTestComponentErrorHandling:
    """Test suite voor error handling."""
    
    def test_component_error_recovery(self, test_component):
        """Test error recovery scenario."""
        # Voeg geldige data toe
        test_component.add_data("valid_key", "valid_value")
        
        # Probeer ongeldige operatie
        result = test_component.add_data("", "invalid_value")
        assert result is False
        
        # Verifieer dat geldige data nog steeds bestaat
        assert test_component.get_data("valid_key") == "valid_value"
        assert len(test_component.data) == 1

# Performance Tests
class TestTestComponentPerformance:
    """Test suite voor performance tests."""
    
    def test_component_performance(self, test_component):
        """Test component performance met veel data."""
        import time
        
        start_time = time.time()
        
        # Voeg veel data toe
        for i in range(1000):
            test_component.add_data(f"key_{i}", f"value_{i}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verifieer dat alle data is toegevoegd
        assert len(test_component.data) == 1000
        assert test_component.get_data("key_999") == "value_999"
        
        # Performance assertion (moet binnen 1 seconde)
        assert execution_time < 1.0, f"Performance test failed: {execution_time:.3f}s"

# Async & Wrapper Mocking Example
import asyncio
from unittest.mock import AsyncMock

class TestAsyncExamples:
    @pytest.mark.asyncio
    async def test_async_wrapper_mock(self):
        class DummyAgent:
            async def publish_agent_event(self, event_type: str, data: Dict[str, Any]):
                return True
        agent = DummyAgent()
        agent.publish_agent_event = AsyncMock(return_value=True)
        result = await agent.publish_agent_event("workflow_started", {"status": "requested"})
        assert result is True
        agent.publish_agent_event.assert_awaited_with("workflow_started", {"status": "requested"})
