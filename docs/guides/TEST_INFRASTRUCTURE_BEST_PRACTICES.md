# Test Infrastructure Best Practices Guide

**Datum**: 27 januari 2025  
**Status**: ✅ **ACTIVE** - Best practices geïmplementeerd  
**Focus**: Test infrastructure maintenance en preventie van common issues  

## 🎯 Overview

Dit document bevat best practices voor het onderhouden van een gezonde test infrastructure, gebaseerd op lessons learned van de test infrastructure cleanup. Het richt zich op preventie van common issues en het behouden van een betrouwbare test suite.

## 🧹 **Script Management Best Practices**

### Temporary Script Guidelines
**Probleem**: Recovery en repair scripts blijven achter in de codebase.

**Best Practices**:
1. **Temporary Directory**: Plaats tijdelijke scripts in `temp/` of `/tmp/`
2. **Naming Convention**: Gebruik timestamp in bestandsnaam
3. **Documentation**: Documenteer doel en gebruik van tijdelijke scripts
4. **Cleanup**: Verwijder scripts direct na gebruik
5. **Version Control**: Track script wijzigingen in git

**Example Structure**:
```
temp/
├── fix_shared_context_20250127_1430.py
├── recover_events_20250127_1600.py
└── cleanup_scripts.sh
```

**Good Example**:
```bash
# Temporary script with timestamp
temp/fix_shared_context_20250127_1430.py

# Cleanup script
temp/cleanup_scripts.sh
```

**Bad Example**:
```bash
# Permanent script in scripts directory
scripts/fix_shared_context.py
```

### Script Documentation Template
```python
#!/usr/bin/env python3
"""
Temporary Script: Fix Shared Context JSON
Date: 2025-01-27
Purpose: Repair corrupted shared_context.json file
Usage: python temp/fix_shared_context_20250127_1430.py
Cleanup: Remove after issue resolution
"""
```

## 🔧 **Import Error Prevention**

### Import Strategy Guidelines
**Probleem**: Relative imports veroorzaken collection issues in pytest.

**Best Practices**:
1. **Absolute Imports**: Gebruik absolute imports waar mogelijk
2. **Package Structure**: Zorg voor correcte package structuur
3. **Init Files**: Plaats `__init__.py` in alle test directories
4. **Import Testing**: Test imports tijdens development
5. **CI Validation**: Valideer imports in CI/CD pipeline

**Good Examples**:
```python
# Absolute import
from tests.integration.workflows.test_helpers import run_orchestrator_command

# Relative import with proper structure
from .test_helpers import run_orchestrator_command
```

**Bad Examples**:
```python
# Relative import without proper structure
from test_helpers import run_orchestrator_command

# Missing __init__.py in directory
from workflows.test_helpers import run_orchestrator_command
```

### Package Structure Requirements
```
tests/
├── __init__.py                    # Required
├── integration/
│   ├── __init__.py               # Required
│   └── workflows/
│       ├── __init__.py           # Required
│       └── test_helpers.py
└── unit/
    ├── __init__.py               # Required
    └── core/
        └── __init__.py           # Required
```

## ⚙️ **Pytest Configuration Management**

### Configuration Best Practices
**Probleem**: Te brede ignore regels en duplicaat configuratie.

**Best Practices**:
1. **Specific Ignores**: Gebruik specifieke ignore patterns
2. **Documentation**: Documenteer reden voor elke ignore regel
3. **No Duplicates**: Vermijd duplicaat configuratie opties
4. **Test Changes**: Test configuratie wijzigingen in isolatie
5. **Markers**: Gebruik markers voor test categorisatie

**Good Configuration**:
```ini
[tool:pytest]
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
    --ignore=bmad/agents/Agent/TestEngineer/testengineer.py  # Has __init__ constructor

markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**Bad Configuration**:
```ini
[tool:pytest]
addopts = 
    -v
    --tb=short
    --ignore=bmad/agents/Agent/  # Too broad
    --run-integration            # Duplicate option

addopts =                       # Duplicate section
    -v
    --tb=short
```

### Ignore Rule Documentation Template
```ini
# Ignore specific files with reasons
--ignore=bmad/agents/Agent/TestEngineer/testengineer.py  # Has __init__ constructor, not a test class
--ignore=bmad/agents/Agent/Orchestrator/orchestrator.py  # CLI script, not a test module
```

## 📁 **Test Structure Organization**

### Directory Structure Guidelines
**Probleem**: Losse test bestanden in root directory.

**Best Practices**:
1. **Test Pyramid**: Volg unit → integration → e2e structuur
2. **Descriptive Names**: Gebruik beschrijvende directory namen
3. **Grouping**: Groepeer gerelateerde tests samen
4. **Separation**: Scheid test types per directory
5. **Consistency**: Behoud consistente naming conventions

**Recommended Structure**:
```
tests/
├── unit/                    # Unit tests (70%)
│   ├── agents/             # Agent unit tests
│   ├── core/               # Core functionality tests
│   ├── utils/              # Utility function tests
│   └── enterprise/         # Enterprise feature tests
├── integration/            # Integration tests (20%)
│   ├── agents/             # Agent integration tests
│   ├── workflows/          # Workflow integration tests
│   ├── external/           # External service integration
│   └── microservices/      # Microservice integration tests
├── e2e/                   # End-to-end tests (10%)
│   ├── scenarios/          # Business scenario tests
│   └── workflows/          # Complete workflow tests
├── performance/           # Performance tests
├── regression/            # Regression tests
└── fixtures/              # Test fixtures and data
```

### File Naming Conventions
```
# Good naming
test_agent_integration.py
test_workflow_orchestrator.py
test_database_connection.py

# Bad naming
test.py
integration_test.py
workflow_test.py
```

## 🎭 **Mocking Strategy for External Dependencies**

### Mocking Guidelines
**Probleem**: Tests falen door externe service issues.

**Best Practices**:
1. **Service Boundaries**: Mock op service boundary niveau
2. **Dependency Injection**: Gebruik dependency injection voor testability
3. **Realistic Responses**: Geef realistische mock responses
4. **Success/Failure**: Test zowel success als failure scenarios
5. **Isolation**: Zorg voor test isolation

**Good Mocking Example**:
```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_workflow_event_publishing(self, agent):
    """Test workflow event publishing with mocked message bus wrapper."""
    with patch.object(agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish_event:
        await agent.publish_agent_event(EventTypes.WORKFLOW_STARTED, {"workflow_id": "test_workflow"})
        mock_publish_event.assert_awaited_with(EventTypes.WORKFLOW_STARTED, {"workflow_id": "test_workflow"})
```

**Bad Mocking Example**:
```python
@pytest.mark.asyncio
async def test_workflow_event_publishing(self, agent):
    """Avoid calling wrapper without mocking or assertions."""
    # Dit is fragiel en raakt de echte bus
    await agent.publish_agent_event(EventTypes.WORKFLOW_STARTED, {"workflow_id": "test_workflow"})
    assert True  # Geen verificatie
```

### Mock Configuration Best Practices
```python
# conftest.py
import pytest
from unittest.mock import patch, AsyncMock

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services for all tests."""
    with patch('bmad.core.message_bus.publish_event', new_callable=AsyncMock) as mock_publish_event:
        with patch('integrations.supabase.client') as mock_supabase:
            with patch('integrations.openrouter.client') as mock_openrouter:
                yield {
                    'message_bus': mock_publish,
                    'supabase': mock_supabase,
                    'openrouter': mock_openrouter
                }
```

## 🔄 **Async Test Handling**

### Async Test Guidelines
**Probleem**: Async tests vereisen speciale setup en teardown.

**Best Practices**:
1. **Pytest Asyncio**: Gebruik `pytest-asyncio` voor async tests
2. **Async Markers**: Markeer async tests met `@pytest.mark.asyncio`
3. **Context Managers**: Handle async context managers correct
4. **Resource Cleanup**: Clean up async resources in teardown
5. **Sync/Async**: Test zowel sync als async interfaces

**Good Async Test Example**:
```python
@pytest.mark.asyncio
async def test_async_operation(self):
    """Test async operation with proper setup."""
    async with AsyncContextManager() as manager:
        result = await manager.operation()
        assert result is not None
        assert result.status == "completed"
```

**Bad Async Test Example**:
```python
async def test_async_operation(self):  # Missing @pytest.mark.asyncio
    """Test async operation without proper setup."""
    result = await operation()  # May fail without proper async support
    assert result is not None
```

### Async Test Configuration
```python
# pytest.ini
[tool:pytest]
asyncio_mode = auto

# conftest.py
import pytest

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

## 📊 **Test Status Monitoring**

### Monitoring Guidelines
**Probleem**: Test issues worden laat gedetecteerd.

**Best Practices**:
1. **Regular Execution**: Draai tests regelmatig (dagelijks of bij elke commit)
2. **Execution Time**: Monitor test execution time
3. **Failure Patterns**: Track test failure patterns
4. **Alerts**: Stel alerts in voor test failures
5. **Coverage Reports**: Onderhoud test coverage reports

### Metrics to Track
```python
# Test metrics to monitor
TEST_METRICS = {
    "pass_rate": "Percentage of passing tests",
    "execution_time": "Total test execution time",
    "coverage": "Code coverage percentage",
    "flaky_tests": "Number of flaky tests",
    "fix_time": "Time to fix test failures"
}
```

### Monitoring Script Example
```python
#!/usr/bin/env python3
"""
Test Status Monitor
Monitors test execution and reports issues.
"""

import subprocess
import json
from datetime import datetime

def run_test_monitor():
    """Run test suite and collect metrics."""
    start_time = datetime.now()
    
    # Run tests
    result = subprocess.run([
        "python", "-m", "pytest", "tests/", 
        "--json-report", "--json-report-file=test_report.json"
    ], capture_output=True, text=True)
    
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    # Parse results
    with open("test_report.json", "r") as f:
        report = json.load(f)
    
    # Calculate metrics
    total_tests = report["summary"]["total"]
    passed_tests = report["summary"]["passed"]
    failed_tests = report["summary"]["failed"]
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Report metrics
    print(f"Test Execution Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Execution Time: {execution_time:.1f} seconds")
    
    # Alert on issues
    if pass_rate < 90:
        print("⚠️  WARNING: Pass rate below 90%")
    if execution_time > 300:
        print("⚠️  WARNING: Test execution time exceeds 5 minutes")

if __name__ == "__main__":
    run_test_monitor()
```

## 🛠️ **Troubleshooting Common Issues**

### Import Error Resolution
```python
# Common import error solutions
IMPORT_ERROR_SOLUTIONS = {
    "ModuleNotFoundError": [
        "Check file structure and __init__.py files",
        "Verify import paths are correct",
        "Use absolute imports when possible",
        "Test imports in isolation"
    ],
    "AttributeError": [
        "Check if module is properly imported",
        "Verify class/method exists",
        "Check for typos in import statements"
    ]
}
```

### Test Failure Resolution
```python
# Common test failure solutions
TEST_FAILURE_SOLUTIONS = {
    "AssertionError": [
        "Check test data consistency",
        "Verify mock setup",
        "Review test logic",
        "Check for race conditions"
    ],
    "TimeoutError": [
        "Increase timeout values",
        "Check for infinite loops",
        "Verify async operations complete",
        "Review resource cleanup"
    ]
}
```

## 📋 **Checklist for Test Infrastructure Maintenance**

### Daily Maintenance
- [ ] Run unit tests
- [ ] Check test execution time
- [ ] Review test failures
- [ ] Update test documentation

### Weekly Maintenance
- [ ] Run full test suite
- [ ] Generate coverage reports
- [ ] Review test metrics
- [ ] Clean up temporary files
- [ ] Update test dependencies

### Monthly Maintenance
- [ ] Review test structure
- [ ] Optimize slow tests
- [ ] Update test configuration
- [ ] Review mocking strategy
- [ ] Plan test improvements

## 🎯 **Conclusion**

Het onderhouden van een gezonde test infrastructure vereist consistentie en aandacht voor detail. Door deze best practices te volgen, kunnen we:

- **Voorkomen** van common issues
- **Detecteren** van problemen vroeg
- **Oplossen** van issues snel
- **Behouden** van test betrouwbaarheid
- **Verbeteren** van developer experience

**Key Success Factors**:
1. **Consistency**: Volg best practices consistent
2. **Documentation**: Documenteer alle configuratie en setup
3. **Monitoring**: Monitor test status regelmatig
4. **Cleanup**: Ruim tijdelijke artifacts op
5. **Review**: Review en update best practices regelmatig

**Status**: ✅ **ACTIVE** - Best practices geïmplementeerd en in gebruik 