# Best Practices Guide

## Overview

Dit document bevat alle best practices voor BMAD development, geconsolideerd uit lessons learned en development ervaring. Deze guide dient als referentie voor alle development activiteiten.

**Laatste Update**: 2025-01-27  
**Versie**: 2.1  
**Status**: Actief - MCP Integration voltooid, Test Quality Verbeterd

## Development Best Practices

### 1. Agent Development

#### **Agent Initialization Pattern**
**Best Practice**: Consistente agent initialization met MCP integration.

```python
class AgentName:
    """
    Agent Name voor BMAD.
    Gespecialiseerd in [agent specialization].
    """
    
    def __init__(self):
        # Core agent setup
        self.agent_name = "AgentName"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
```

**Voordelen**:
- ✅ Uniforme agent setup
- ✅ MCP integration ready
- ✅ Proper logging
- ✅ Type hints voor IDE support

#### **Async Development Pattern**
**Best Practice**: Consistente async patterns met backward compatibility.

```python
class AsyncAgent:
    def __init__(self):
        # 1. Initialize async attributes
        self.mcp_client = None
        self.mcp_enabled = False
    
    async def initialize_mcp(self):
        # 2. Proper async initialization
        try:
            self.mcp_client = await get_mcp_client()
            self.mcp_enabled = True
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False
    
    async def execute_task(self, task_name: str, **kwargs):
        # 3. Async task execution met fallback
        if self.mcp_enabled:
            try:
                return await self.mcp_client.execute_tool(task_name, **kwargs)
            except Exception:
                logger.warning("MCP failed, using local execution")
        
        # 4. Fallback naar lokale execution
        return await self._local_execution(task_name, **kwargs)
    
    # 5. Sync wrapper methods voor backward compatibility
    def sync_execute_task(self, task_name: str, **kwargs):
        return asyncio.run(self.execute_task(task_name, **kwargs))
```

**Voordelen**:
- ✅ Consistente async patterns
- ✅ Proper error handling
- ✅ Backward compatibility
- ✅ Graceful degradation

### 3. Test Quality Best Practices

#### **Async Test Patterns**
**Best Practice**: Proper async test patterns met pytest-asyncio.

```python
import pytest
from unittest.mock import patch, MagicMock

class TestAsyncAgent:
    @pytest.fixture
    def agent(self):
        return AsyncAgent()
    
    @pytest.mark.asyncio
    async def test_async_method(self, agent):
        """Test async methodes met proper decorators."""
        result = await agent.execute_task("test_task")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_cli_async_command(self, agent):
        """Test CLI commands die async methodes aanroepen."""
        with patch('sys.argv', ['agent.py', 'async-command']):
            with patch.object(agent, 'execute_task') as mock_task:
                async def async_mock():
                    return {"result": "success"}
                mock_task.side_effect = async_mock
                
                # Test CLI main function
                main()
                mock_task.assert_called_once()
```

**Voordelen**:
- ✅ Proper async test execution
- ✅ Event loop management
- ✅ Mock strategy voor async methodes
- ✅ CLI testing patterns

#### **Test Fix Automation**
**Best Practice**: Systematische aanpak voor het fixen van syntax errors.

```python
# Script voor het fixen van syntax errors in test files
def fix_test_syntax_errors(file_path):
    """Fix common syntax errors in test files."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Remove duplicate decorators
    content = re.sub(r'@pytest\.mark\.asyncio\s*\n\s*async\s+@pytest\.mark\.asyncio', 
                    '@pytest.mark.asyncio', content)
    
    # Fix 2: Remove backslashes from regex replacements
    content = content.replace('\\', '')
    
    # Fix 3: Fix async method calls
    content = re.sub(r'await agent\\.show_help\\(\\)', 'agent.show_help()', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
```

**Voordelen**:
- ✅ Systematische error fixing
- ✅ Consistentie in test files
- ✅ Automatisering van repetitieve fixes
- ✅ Kwaliteitsverbetering

### 2. MCP Integration

#### **MCP Tool Usage Pattern**
**Best Practice**: MCP tools met graceful fallback.

```python
async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Use MCP tool voor enhanced functionality."""
    if not self.mcp_enabled or not self.mcp_client:
        logger.warning("MCP not available, using local tools")
        return None
    
    try:
        result = await self.mcp_client.execute_tool(tool_name, parameters)
        logger.info(f"MCP tool {tool_name} executed successfully")
        return result
    except Exception as e:
        logger.error(f"MCP tool {tool_name} execution failed: {e}")
        return None
```

**Voordelen**:
- ✅ Betrouwbare MCP usage
- ✅ Proper error handling
- ✅ Informative logging
- ✅ Graceful fallback

#### **Agent-Specific MCP Tools**
**Best Practice**: Agent-specifieke MCP tools voor enhanced functionality.

```python
async def use_agent_specific_mcp_tools(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Use agent-specific MCP tools voor enhanced functionality."""
    if not self.mcp_enabled:
        return {}
    
    enhanced_data = {}
    
    try:
        # Agent-specific tools
        tool_result = await self.use_mcp_tool("agent_specific_tool", data)
        if tool_result:
            enhanced_data["tool_result"] = tool_result
        
        logger.info(f"Agent-specific MCP tools executed: {list(enhanced_data.keys())}")
        
    except Exception as e:
        logger.error(f"Error in agent-specific MCP tools: {e}")
    
    return enhanced_data
```

**Voordelen**:
- ✅ Agent-specifieke enhancement
- ✅ Modular tool usage
- ✅ Proper error isolation
- ✅ Comprehensive logging

### 3. Error Handling

#### **Graceful Error Handling**
**Best Practice**: Graceful error handling voor alle external calls.

```python
# Performance metrics recording
try:
    self.monitor._record_metric("AgentName", MetricType.SUCCESS_RATE, 95, "%")
except AttributeError:
    logger.info("Performance metrics recording not available")

# MCP initialization
try:
    self.mcp_client = await get_mcp_client()
    self.mcp_enabled = True
except Exception as e:
    logger.warning(f"MCP initialization failed: {e}")
    self.mcp_enabled = False
```

**Voordelen**:
- ✅ Geen crashes bij external failures
- ✅ Informative error messages
- ✅ Graceful degradation
- ✅ Proper logging

#### **Import Path Setup**
**Best Practice**: Proper sys.path setup voor agent files.

```python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
```

**Voordelen**:
- ✅ Correcte module imports
- ✅ Consistent across agents
- ✅ IDE support
- ✅ No import errors

### 4. Code Quality

#### **Method Refactoring Pattern**
**Best Practice**: Backward compatibility bij method refactoring.

```python
# Oude sync methode
def old_method(self, param):
    return self._process(param)

# Nieuwe async methode met sync wrapper
async def new_method(self, param):
    # Async implementation
    return await self._async_process(param)

def old_method(self, param):
    """Sync wrapper voor backward compatibility."""
    return asyncio.run(self.new_method(param))
```

**Voordelen**:
- ✅ Geen breaking changes
- ✅ Smooth migration
- ✅ Backward compatibility
- ✅ Clear documentation

#### **Code Duplication Prevention**
**Best Practice**: Helper methods voor code reuse.

```python
def _create_local_result(self, **kwargs):
    """Create local result when MCP is not available."""
    return {
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "agent": self.agent_name,
        **kwargs
    }
```

**Voordelen**:
- ✅ Vermindert code duplication
- ✅ Verbetert maintainability
- ✅ Consistent result structure
- ✅ Easy to modify

## Testing Best Practices

### 1. Test Organization

#### **Test File Structure**
**Best Practice**: Volg de test pyramid structuur.

```
tests/
├── unit/
│   ├── core/
│   ├── agents/
│   └── integrations/
├── integration/
│   ├── workflows/
│   └── agents/
└── e2e/
    └── scenarios/
```

**Voordelen**:
- ✅ Duidelijke test structuur
- ✅ Makkelijk te navigeren
- ✅ Consistent across project
- ✅ Proper test isolation

#### **Test Naming Convention**
**Best Practice**: Beschrijvende test namen.

```python
# ✅ Goed
async def test_agent_mcp_integration():
    """Test MCP integration in agent."""

async def test_async_method_with_fallback():
    """Test async method with MCP fallback."""

# ❌ Slecht
async def test_method():
    """Test method."""
```

**Voordelen**:
- ✅ Duidelijke test purpose
- ✅ Makkelijk te debuggen
- ✅ Self-documenting
- ✅ Better test reports

### 2. Async Testing

#### **Async Test Pattern**
**Best Practice**: Proper async test setup.

```python
async def test_async_agent():
    agent = AsyncAgent()
    
    # Test initialization
    await agent.initialize_mcp()
    assert agent.mcp_enabled in [True, False]  # Both are valid
    
    # Test async execution
    result = await agent.execute_task("test_task")
    assert result is not None
    
    # Test sync wrapper
    result = agent.sync_execute_task("test_task")
    assert result is not None
```

#### **MCP Integration Test Pattern**
**Best Practice**: Comprehensive MCP integration testing.

```python
@pytest.mark.asyncio
async def test_mcp_integration_workflow(self, agent):
    """Test complete MCP integration workflow."""
    # Test MCP initialization
    await agent.initialize_mcp()
    
    # Test MCP tool usage
    result = await agent.develop_strategy("Test Strategy")
    assert result["status"] == "developed"
    
    # Test MCP enhanced data
    if "mcp_enhanced_data" in result:
        assert isinstance(result["mcp_enhanced_data"], dict)
    
    # Test fallback behavior
    agent.mcp_enabled = False
    fallback_result = await agent.develop_strategy("Test Strategy")
    assert fallback_result["status"] == "developed"
```

**Voordelen**:
- ✅ Test MCP initialization
- ✅ Test MCP tool execution
- ✅ Test fallback behavior
- ✅ Test enhanced data structure

#### **CLI Async Test Pattern**
**Best Practice**: Proper CLI async method testing.

```python
def test_cli_async_command(self, capsys):
    """Test CLI command with async method."""
    with patch('module.AgentClass') as mock_agent_class:
        mock_agent = Mock()
        from unittest.mock import AsyncMock
        
        # Setup async mock
        mock_async_method = AsyncMock()
        mock_async_method.return_value = {"status": "success"}
        mock_agent.async_method = mock_async_method
        mock_agent_class.return_value = mock_agent
        
        # Execute CLI
        main()
        
        # Verify output
        captured = capsys.readouterr()
        assert "success" in captured.out
```

**Voordelen**:
- ✅ Proper async mocking
- ✅ CLI integration testing
- ✅ Output verification
- ✅ Error handling testing

#### **Integration Test Logger Setup**
**Best Practice**: Proper logger setup voor integration tests.

```python
# ✅ Test File Header
import pytest
from unittest.mock import Mock, patch
import logging

from bmad.agents.Agent.AgentName.agentname import AgentClass

# Configure logging for tests
logger = logging.getLogger(__name__)

class TestAgentIntegration:
    @pytest.fixture
    def agent(self):
        return AgentClass()
    
    @pytest.mark.asyncio
    async def test_integration_workflow(self, agent):
        """Test complete integration workflow."""
        # ... test logic ...
        logger.info("Integration test completed successfully")
```

**Voordelen**:
- ✅ Voorkomt logger import errors
- ✅ Consistent logging across tests
- ✅ Better test debugging
- ✅ Professional test output

#### **Test Isolation**
**Best Practice**: Independent tests zonder shared state.

```python
async def test_agent_method():
    # Fresh agent instance
    agent = AgentName()
    
    # Test method
    result = await agent.agent_method("test_param")
    assert result is not None
    
    # Clean up
    del agent
```

**Voordelen**:
- ✅ Independent tests
- ✅ No test interference
- ✅ Reproducible results
- ✅ Parallel execution safe

### 3. Test Quality

#### **Test Data Management**
**Best Practice**: Geïsoleerde test data.

```python
@pytest.fixture
def test_agent():
    """Provide fresh agent instance for each test."""
    agent = AgentName()
    yield agent
    # Cleanup if needed
    del agent

async def test_agent_with_fixture(test_agent):
    result = await test_agent.agent_method("test")
    assert result is not None
```

**Voordelen**:
- ✅ Consistent test data
- ✅ Proper cleanup
- ✅ Reusable fixtures
- ✅ Clean test environment

#### **Mock External Dependencies**
**Best Practice**: Mock external calls voor reliable tests.

```python
@patch('bmad.core.mcp.get_mcp_client')
async def test_mcp_integration(mock_get_client):
    mock_get_client.return_value = MockMCPClient()
    
    agent = AgentName()
    await agent.initialize_mcp()
    
    assert agent.mcp_enabled is True
```

**Voordelen**:
- ✅ Reliable tests
- ✅ No external dependencies
- ✅ Fast execution
- ✅ Predictable results

## Quality Assurance Best Practices

### 1. Code Review Process

#### **Quality-First Review**
**Best Practice**: Review voor kwaliteit, niet alleen functionaliteit.

**Review Checklist**:
- [ ] **Code Quality**: Volgt best practices
- [ ] **Error Handling**: Proper error handling
- [ ] **Documentation**: Code is documented
- [ ] **Testing**: Tests zijn geschreven
- [ ] **Performance**: Geen performance issues
- [ ] **Security**: Geen security vulnerabilities

**Voordelen**:
- ✅ Consistente code kwaliteit
- ✅ Fewer bugs
- ✅ Better maintainability
- ✅ Knowledge sharing

#### **Documentation Review**
**Best Practice**: Review documentatie gelijktijdig met code.

**Documentation Checklist**:
- [ ] **Code Comments**: Complex code is commented
- [ ] **Method Documentation**: Methods zijn documented
- [ ] **README Updates**: README is bijgewerkt
- [ ] **API Documentation**: API docs zijn bijgewerkt
- [ ] **Change Log**: Changes zijn gedocumenteerd

**Voordelen**:
- ✅ Up-to-date documentatie
- ✅ Better onboarding
- ✅ Easier maintenance
- ✅ Knowledge preservation

### 2. Performance Optimization

#### **Async Performance**
**Best Practice**: Gebruik async voor I/O operations.

```python
# ✅ Goed: Async voor I/O
async def fetch_data(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ❌ Slecht: Sync voor I/O
def fetch_data(self):
    response = requests.get(url)
    return response.json()
```

**Voordelen**:
- ✅ Betere performance
- ✅ Non-blocking operations
- ✅ Scalable code
- ✅ Resource efficient

#### **Memory Management**
**Best Practice**: Proper memory management voor grote datasets.

```python
# ✅ Goed: Generator voor grote datasets
def process_large_dataset(self, data):
    for item in data:
        yield self.process_item(item)

# ❌ Slecht: List comprehension voor grote datasets
def process_large_dataset(self, data):
    return [self.process_item(item) for item in data]
```

**Voordelen**:
- ✅ Memory efficient
- ✅ Scalable
- ✅ Better performance
- ✅ No memory leaks

## Project Management Best Practices

### 1. Task Tracking

#### **Kanban Board Management**
**Best Practice**: Houd alleen sprint tasks bij in Kanban board.

**Kanban Best Practices**:
- **Sprint Tasks Only**: Alleen huidige sprint tasks
- **Master Planning**: Uitgebreide backlog in separate file
- **Regular Updates**: Update status na elke completed task
- **Clear Status**: Duidelijke task status

**Voordelen**:
- ✅ Duidelijke project status
- ✅ Focus op huidige sprint
- ✅ Better planning
- ✅ Reduced complexity

#### **Documentation Workflow**
**Best Practice**: Documentatie updates als deel van development workflow.

**Documentation Workflow**:
1. **Feature Development**: Update docs tijdens development
2. **Code Review**: Review documentatie gelijktijdig
3. **Testing**: Update test documentation
4. **Deployment**: Update deployment docs

**Voordelen**:
- ✅ Up-to-date documentatie
- ✅ Consistent information
- ✅ Better knowledge sharing
- ✅ Easier maintenance

### 2. Version Control

#### **Commit Best Practices**
**Best Practice**: Meaningful commits met proper messages.

```bash
# ✅ Goed: Descriptive commit message
git commit -m "Add MCP integration to QualityGuardian agent with async support"

# ❌ Slecht: Vague commit message
git commit -m "Update code"
```

**Commit Guidelines**:
- **Verb + Object**: "Add", "Update", "Fix", "Remove"
- **Specific Description**: Wat is er veranderd
- **Scope**: Welke component/agent
- **Context**: Waarom de change

**Voordelen**:
- ✅ Clear change history
- ✅ Easy to review
- ✅ Better collaboration
- ✅ Easier debugging

#### **Branch Management**
**Best Practice**: Feature branches voor development.

**Branch Strategy**:
- **main**: Production ready code
- **develop**: Integration branch
- **feature/**: Feature development
- **hotfix/**: Critical fixes

**Voordelen**:
- ✅ Isolated development
- ✅ Safe integration
- ✅ Easy rollback
- ✅ Better collaboration

## Security Best Practices

### 1. Input Validation

#### **Parameter Validation**
**Best Practice**: Valideer alle input parameters.

```python
def agent_method(self, param: str) -> Dict[str, Any]:
    # Input validation
    if not isinstance(param, str):
        raise TypeError("param must be a string")
    
    if not param.strip():
        raise ValueError("param cannot be empty")
    
    # Method implementation
    return self._process_param(param)
```

**Voordelen**:
- ✅ Prevents crashes
- ✅ Better error messages
- ✅ Security improvement
- ✅ Robust code

#### **Type Checking**
**Best Practice**: Gebruik type hints voor better code quality.

```python
from typing import Dict, Any, Optional

async def use_mcp_tool(
    self, 
    tool_name: str, 
    parameters: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Use MCP tool voor enhanced functionality."""
    pass
```

**Voordelen**:
- ✅ Better IDE support
- ✅ Catch type errors early
- ✅ Self-documenting code
- ✅ Better refactoring

### 2. Error Information

#### **Safe Error Messages**
**Best Practice**: Geen sensitive informatie in error messages.

```python
# ✅ Goed: Safe error message
try:
    result = await self.mcp_client.execute_tool(tool_name, parameters)
except Exception as e:
    logger.error(f"MCP tool {tool_name} execution failed")
    return None

# ❌ Slecht: Expose sensitive info
try:
    result = await self.mcp_client.execute_tool(tool_name, parameters)
except Exception as e:
    logger.error(f"MCP tool failed: {e}")  # May expose sensitive data
    return None
```

**Voordelen**:
- ✅ Security improvement
- ✅ No sensitive data exposure
- ✅ Professional error handling
- ✅ Better user experience

## Performance Best Practices

### 1. Async Optimization

#### **Concurrent Operations**
**Best Practice**: Gebruik concurrent operations waar mogelijk.

```python
async def process_multiple_items(self, items: List[str]):
    # ✅ Goed: Concurrent processing
    tasks = [self.process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results

# ❌ Slecht: Sequential processing
async def process_multiple_items(self, items: List[str]):
    results = []
    for item in items:
        result = await self.process_item(item)
        results.append(result)
    return results
```

**Voordelen**:
- ✅ Better performance
- ✅ Parallel execution
- ✅ Resource efficient
- ✅ Scalable

#### **Resource Management**
**Best Practice**: Proper resource cleanup.

```python
async def fetch_data_with_session(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
    # Session automatically closed
```

**Voordelen**:
- ✅ Automatic cleanup
- ✅ No resource leaks
- ✅ Better performance
- ✅ Reliable code

### 2. Caching Strategy

#### **Result Caching**
**Best Practice**: Cache expensive operations.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(self, param: str) -> Dict[str, Any]:
    # Expensive calculation
    return self._calculate(param)
```

**Voordelen**:
- ✅ Better performance
- ✅ Reduced computation
- ✅ Memory efficient
- ✅ Scalable

## Quick Reference

### **Development Checklist**
- [ ] **Agent Setup**: Proper initialization met MCP
- [ ] **Async Patterns**: Consistent async implementation
- [ ] **Error Handling**: Graceful error handling
- [ ] **Input Validation**: Parameter validation
- [ ] **Type Hints**: Proper type annotations
- [ ] **Documentation**: Code documentation
- [ ] **Testing**: Unit tests geschreven
- [ ] **Code Review**: Quality review uitgevoerd

### **Common Patterns**
```python
# Agent Initialization
class AgentName:
    def __init__(self):
        self.agent_name = "AgentName"
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_enabled = False

# Async Method Pattern
async def method_name(self, param: str) -> Dict[str, Any]:
    if self.mcp_enabled:
        try:
            return await self.mcp_client.execute_tool("tool_name", {"param": param})
        except Exception:
            logger.warning("MCP failed, using local execution")
    
    return self._local_method(param)

# Error Handling Pattern
try:
    result = await self.external_call()
except Exception as e:
    logger.warning(f"External call failed: {e}")
    result = self._fallback_method()

# Input Validation Pattern
def method_name(self, param: str) -> Dict[str, Any]:
    if not isinstance(param, str):
        raise TypeError("param must be a string")
    if not param.strip():
        raise ValueError("param cannot be empty")
    
    return self._process(param)
```

## Version History

- **v1.0 (2025-08-02)**: Initial version met geconsolideerde best practices
- **v1.1 (Planned)**: Additional patterns en optimizations
- **v1.2 (Planned)**: Advanced performance en security patterns

## Contributing

Voeg nieuwe best practices toe door:
1. **Pattern Description**: Beschrijf het pattern en use case
2. **Code Example**: Volledig werkend code voorbeeld
3. **Benefits**: Voordelen van het pattern
4. **Implementation**: Stap-voor-stap implementatie
5. **Update Version**: Update version history

---

**Note**: Deze guide wordt continu bijgewerkt tijdens development. Check regelmatig voor nieuwe best practices. 