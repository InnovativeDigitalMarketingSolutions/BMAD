# Test Workflow Guide

## Overview

Dit document beschrijft de verplichte test workflow voor alle nieuwe functionaliteit en uitbreidingen in het BMAD systeem. Het doel is om ervoor te zorgen dat alle code kwalitatief is geïmplementeerd en goed getest wordt.

## Test Workflow Checklist

### Voor het implementeren van nieuwe functionaliteit:

- [ ] **Analyse**: Root cause analysis uitvoeren voor bugs
- [ ] **Planning**: Test strategie bepalen (unit, integration, e2e)
- [ ] **Review**: Bestaande guide files raadplegen voor best practices

### Tijdens implementatie:

- [ ] **Unit Tests**: Schrijven voor alle core modules
- [ ] **Integration Tests**: Schrijven voor API endpoints
- [ ] **Mocking**: Gebruik AsyncMock voor async functies
- [ ] **Validation**: Test edge cases en error scenarios

### Na implementatie:

- [ ] **Test Execution**: Alle tests uitvoeren
- [ ] **Coverage Check**: Test coverage controleren
- [ ] **Documentation**: Tests documenteren
- [ ] **Review**: Code review inclusief tests

## Test Structure

### Voor Microservices:

```
microservices/{service-name}/
├── tests/
│   ├── __init__.py
│   ├── unit/                    # Unit tests voor core modules
│   │   ├── __init__.py
│   │   ├── test_{module_name}.py
│   │   └── ...
│   ├── integration/             # Integration tests voor API
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   └── ...
│   └── performance/             # Performance tests
│       ├── __init__.py
│       ├── test_load.py
│       └── ...
└── test_{service_name}.py       # Main test file
```

### Voor Agents:

```
tests/unit/agents/
├── test_{agent_name}_agent.py   # Agent unit tests
└── ...
```

### Voor CLI:

```
tests/unit/cli/
├── test_{cli_name}_cli.py       # CLI unit tests
└── ...
```

## Test Best Practices

### 1. Unit Tests

```python
"""
Unit tests voor {ModuleName}
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.{module_path} import {ClassName}


class Test{ClassName}:
    """Test cases voor {ClassName}."""
    
    @pytest.fixture
    def {instance_name}(self):
        """Create a {ClassName} instance for testing."""
        return {ClassName}()
        
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            "field1": "value1",
            "field2": "value2"
        }
        
    @pytest.mark.asyncio
    async def test_method_name(self, {instance_name}, sample_data):
        """Test method functionality."""
        # Arrange
        # Act
        result = await {instance_name}.method_name(sample_data)
        
        # Assert
        assert result is not None
        assert result.field1 == sample_data["field1"]
```

### 2. Integration Tests

```python
"""
Integration tests voor {ServiceName} API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api.main import app

client = TestClient(app)

class Test{ServiceName}API:
    """Test cases voor {ServiceName} API endpoints."""
    
    def test_endpoint_name(self):
        """Test endpoint functionality."""
        response = client.get("/endpoint")
        assert response.status_code == 200
        
        data = response.json()
        assert "expected_field" in data
```

### 3. Mocking Best Practices

```python
# Voor async functies
@pytest.mark.asyncio
async def test_async_method(self):
    with patch('module.AsyncClass') as mock_class:
        mock_instance = AsyncMock()
        mock_class.return_value = mock_instance
        mock_instance.method.return_value = {"result": "success"}
        
        result = await test_method()
        assert result["result"] == "success"

# Voor sync functies
def test_sync_method(self):
    with patch('module.SyncClass') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_instance.method.return_value = "success"
        
        result = test_method()
        assert result == "success"
```

## Test Categories

### 1. Unit Tests (70% van alle tests)
- **Doel**: Test individuele functies en methoden
- **Scope**: Geïsoleerde componenten
- **Tools**: pytest, unittest.mock
- **Coverage**: 90%+ line coverage

### 2. Integration Tests (20% van alle tests)
- **Doel**: Test componenten samenwerking
- **Scope**: API endpoints, service integratie
- **Tools**: pytest, TestClient, httpx
- **Coverage**: Alle endpoints en workflows

### 3. Performance Tests (10% van alle tests)
- **Doel**: Test performance en schaalbaarheid
- **Scope**: Load testing, stress testing
- **Tools**: pytest-benchmark, locust
- **Coverage**: Kritieke paden

## Test Execution Workflow

### 1. Voor elke nieuwe feature:

```bash
# 1. Schrijf unit tests
pytest tests/unit/test_new_feature.py -v

# 2. Schrijf integration tests
pytest tests/integration/test_new_feature_integration.py -v

# 3. Run alle tests
pytest tests/ -v

# 4. Check coverage
pytest --cov=src tests/ --cov-report=html
```

### 2. Voor microservices:

```bash
# 1. Unit tests voor core modules
cd microservices/{service-name}
pytest tests/unit/ -v

# 2. Integration tests voor API
pytest tests/integration/ -v

# 3. Performance tests
pytest tests/performance/ -v

# 4. Full test suite
pytest tests/ -v --cov=src
```

## Quality Gates

### 1. Test Coverage Requirements
- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 100% endpoint coverage
- **Performance Tests**: Alle kritieke paden

### 2. Test Quality Requirements
- **Naming**: Beschrijvende test namen
- **Documentation**: Docstrings voor alle tests
- **Mocking**: Proper mocking van dependencies
- **Assertions**: Specifieke assertions

### 3. Code Quality Requirements
- **No Code Removal**: Alleen uitbreiden, niet verwijderen
- **Root Cause Analysis**: Voor bugs, niet symptomen
- **Guide Updates**: Update guide files na oplossingen

## Test Maintenance

### 1. Regular Updates
- Update tests bij code wijzigingen
- Verwijder obsolete tests
- Voeg tests toe voor nieuwe edge cases

### 2. Test Review
- Code review inclusief tests
- Test coverage monitoring
- Performance test monitoring

### 3. Documentation
- Update test documentation
- Document test patterns
- Share best practices

## Troubleshooting

### Common Issues

1. **AsyncMock vs MagicMock**
   - Gebruik AsyncMock voor async functies
   - Gebruik MagicMock voor sync functies

2. **Import Errors**
   - Check sys.path voor test imports
   - Gebruik relative imports waar mogelijk

3. **Test Isolation**
   - Gebruik fixtures voor setup/teardown
   - Mock external dependencies
   - Clean up test data

### Debug Tips

```python
# Debug test execution
pytest tests/ -v -s --tb=short

# Debug specific test
pytest tests/test_file.py::TestClass::test_method -v -s

# Check test discovery
pytest --collect-only

# Run with coverage
pytest --cov=src --cov-report=term-missing tests/
```

## Examples

### Voor Context Service:

```python
# tests/unit/test_context_manager.py
@pytest.mark.asyncio
async def test_create_context(self, context_manager):
    context = await context_manager.create_context(
        name="Test Context",
        context_type="test"
    )
    assert context.name == "Test Context"
```

### Voor Integration Service:

```python
# tests/unit/test_client_manager.py
@pytest.mark.asyncio
async def test_get_client(self, client_manager):
    client_manager.clients["auth0"] = mock_auth0_client
    client = await client_manager.get_client("auth0")
    assert client == mock_auth0_client
```

### Voor Workflow Service:

```python
# tests/unit/test_workflow_manager.py
@pytest.mark.asyncio
async def test_create_workflow(self, workflow_manager):
    workflow = await workflow_manager.create_workflow(
        name="Test Workflow",
        workflow_type="sequential"
    )
    assert workflow.name == "Test Workflow"
```

## Conclusion

Deze test workflow zorgt ervoor dat:
- Alle nieuwe functionaliteit goed getest wordt
- Code kwaliteit hoog blijft
- Bugs vroeg gedetecteerd worden
- Documentatie up-to-date blijft
- Best practices consistent worden toegepast

**Belangrijk**: Tests zijn geen optie, maar een verplicht onderdeel van elke implementatie! 