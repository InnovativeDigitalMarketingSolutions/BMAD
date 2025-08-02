# Testing Workflow Template

## 🎯 **Agent Testing Workflow**

**⚠️ LEVENDE DOCUMENT - Agents mogen en moeten verbeteringen aanbrengen!**

### Overzicht
Dit template beschrijft de test workflow die alle agents moeten volgen voor consistente, hoogwaardige software testing.

## Test Workflow Checklist

### Voor het implementeren van nieuwe functionaliteit:

- [ ] **Analyse**: Root cause analysis uitvoeren voor bugs
- [ ] **Planning**: Test strategie bepalen (unit, integration, e2e)
- [ ] **Review**: Bestaande guide files raadplegen voor best practices
- [ ] **Strategy Review**: Bekijk testing strategy template voor test type keuze

### Tijdens implementatie:

- [ ] **Unit Tests**: Schrijven voor alle core modules
- [ ] **Integration Tests**: Schrijven voor API endpoints
- [ ] **Mocking**: Gebruik AsyncMock voor async functies
- [ ] **Validation**: Test edge cases en error scenarios
- [ ] **Pragmatic Mocking**: Volg mocking strategie uit testing strategy template

### Na implementatie:

- [ ] **Test Execution**: Alle tests uitvoeren
- [ ] **Coverage Check**: Test coverage controleren
- [ ] **Documentation**: Tests documenteren
- [ ] **Review**: Code review inclusief tests
- [ ] **Strategy Validation**: Controleer of test strategie correct is toegepast

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

#### Pragmatic Mocking (Voor Zware Externe Dependencies)
```python
# Mock zware externe dependencies zoals in CLI tests
import sys
from unittest.mock import MagicMock

# Mock externe modules
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Voorbeeld uit CLI tests
class TestIntegratedWorkflowCLI:
    def setup_method(self):
        """Set up test environment."""
        # Create mock orchestrator
        self.mock_orchestrator = MagicMock()
        
        # Patch the orchestrator before creating CLI
        with patch('cli.integrated_workflow_cli.IntegratedWorkflowOrchestrator', return_value=self.mock_orchestrator):
            self.cli = IntegratedWorkflowCLI()
```

#### Standard Mocking (Voor Interne Dependencies)
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

#### Mocking Guidelines
- **Pragmatic Mocking**: Voor zware externe dependencies (opentelemetry, supabase, etc.)
- **Standard Mocking**: Voor interne dependencies en business logic
- **AsyncMock**: Voor async functies en methoden
- **MagicMock**: Voor sync functies en objecten
- **patch.object**: Voor specifieke methoden van bestaande objecten

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
# 1. Schrijf unit tests (pragmatic mocking voor externe dependencies)
pytest tests/unit/test_new_feature.py -v

# 2. Schrijf integration tests (echte dependencies)
pytest tests/integration/test_new_feature_integration.py -v --run-integration

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
pytest tests/integration/ -v --run-integration

# 3. Performance tests
pytest tests/performance/ -v

# 4. Full test suite
pytest tests/ -v --cov=src
```

### 3. Integration Testing Workflow

```bash
# Development: Alleen unit tests (snel)
pytest tests/unit/ -v

# Staging: Unit + integration tests
pytest tests/ -v --run-integration

# Production: Alle tests
pytest tests/ -v --run-integration --run-e2e
```

### 4. Integration Test Setup

```python
# tests/integration/test_integrations.py
import pytest
import os

class TestIntegrations:
    @pytest.fixture(autouse=True)
    def setup_integration_tests(self):
        """Setup for integration tests with real dependencies."""
        # Skip if integration tests are disabled
        if not pytest.config.getoption("--run-integration"):
            pytest.skip("Integration tests disabled. Use --run-integration to enable.")

        # Check if required environment variables are set
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_KEY", 
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_supabase_integration(self):
        """Test real Supabase database integration."""
        # Echte database operaties
        result = await cli.create_tenant("test", "test.com", "basic")
        assert result is not None
```

### 5. Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests (default)
    integration: Integration tests with real dependencies
    e2e: End-to-end tests
    slow: Slow running tests

addopts = 
    -v
    --strict-markers
    --disable-warnings
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

## Agent-Specific Testing Guidelines

### Voor AI Agents
- Mock LLM API calls in unit tests
- Test AI output validation en safety checks
- Implementeer integration tests met echte LLM APIs
- Test fallback mechanismen voor API failures

### Voor Development Agents
- Volg de test pyramid strategie
- Implementeer comprehensive unit tests
- Gebruik pragmatic mocking voor externe dependencies
- Valideer code quality met test coverage

### Voor Testing Agents
- Implementeer test frameworks en utilities
- Zorg voor comprehensive test coverage
- Valideer test quality en performance
- Implementeer test monitoring en reporting

## Agent Verbeteringen

**⚠️ AGENTS: Dit is een levend document!**

### Verbeteringen die agents mogen/moeten aanbrengen:
1. **Nieuwe Test Patterns**: Voeg nieuwe test patterns toe
2. **Mocking Strategieën**: Verbeter mocking strategieën en technieken
3. **Integration Test Categories**: Voeg nieuwe integration test types toe
4. **Test Tools**: Voeg nieuwe test tools en frameworks toe
5. **Agent-Specific Guidelines**: Voeg guidelines toe voor specifieke agent types
6. **Troubleshooting**: Verbeter troubleshooting en debug tips
7. **Documentation**: Verbeter test documentatie en uitleg

### Hoe verbeteringen aanbrengen:
1. **Analyseer**: Identificeer gebieden voor verbetering
2. **Implementeer**: Test verbeteringen in praktijk
3. **Valideer**: Zorg dat verbeteringen test kwaliteit verhogen
4. **Documenteer**: Update dit template met verbeteringen
5. **Deel**: Deel verbeteringen met andere agents

---

**Status**: 🔄 **Levend Document** - Agents mogen en moeten verbeteringen aanbrengen  
**Laatste Update**: 2 augustus 2025  
**Volgende Review**: Continue door agents 