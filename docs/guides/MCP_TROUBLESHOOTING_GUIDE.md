# MCP Integration Troubleshooting Guide

## Overview

Dit document bevat alle troubleshooting informatie voor MCP (Model Context Protocol) integratie in BMAD agents. Het is gebaseerd op echte problemen die we hebben opgelost tijdens de MCP integratie van alle agents.

**Laatste Update**: 2025-08-02  
**Versie**: 1.0  
**Status**: Actief

## Quick Reference

### Common Issues & Solutions
| Issue | Solution | Guide Section |
|-------|----------|---------------|
| `TypeError: 'coroutine' object is not subscriptable` | Add `@pytest.mark.asyncio` and `await` | [Async Test Issues](#async-test-issues) |
| `NameError: name 'logger' is not defined` | Add logger import in test files | [Test Setup Issues](#test-setup-issues) |
| `ValueError: a coroutine was expected, got <MagicMock>` | Use AsyncMock for async methods | [CLI Test Issues](#cli-test-issues) |
| `SyntaxError: 'await' outside async function` | Make method async | [Async Method Issues](#async-method-issues) |
| `SystemExit: 1` in CLI tests | Fix async mocking in CLI | [CLI Test Issues](#cli-test-issues) |

## Async Test Issues

### Problem: `TypeError: 'coroutine' object is not subscriptable`

**Root Cause**: Test method calls async function without `await`

**Solution**:
```python
# ❌ VERKEERD
def test_develop_strategy_success(self, agent):
    result = agent.develop_strategy("Strategy")  # Returns coroutine
    assert result["status"] == "developed"  # TypeError!

# ✅ CORRECT
@pytest.mark.asyncio
async def test_develop_strategy_success(self, agent):
    result = await agent.develop_strategy("Strategy")  # Await the coroutine
    assert result["status"] == "developed"  # Works!
```

### Problem: `RuntimeWarning: coroutine was never awaited`

**Root Cause**: Async function called without await in test

**Solution**:
```python
# ❌ VERKEERD
def test_async_method(self, agent):
    agent.develop_strategy("Strategy")  # Warning!

# ✅ CORRECT
@pytest.mark.asyncio
async def test_async_method(self, agent):
    await agent.develop_strategy("Strategy")  # No warning!
```

## Test Setup Issues

### Problem: `NameError: name 'logger' is not defined`

**Root Cause**: Missing logger import in test files

**Solution**:
```python
# ✅ Test File Header
import pytest
from unittest.mock import Mock, patch
import logging

from bmad.agents.Agent.AgentName.agentname import AgentClass

# Configure logging for tests
logger = logging.getLogger(__name__)

class TestAgentIntegration:
    @pytest.mark.asyncio
    async def test_integration_workflow(self, agent):
        # ... test logic ...
        logger.info("Integration test completed successfully")
```

## CLI Test Issues

### Problem: `ValueError: a coroutine was expected, got <MagicMock>`

**Root Cause**: Using MagicMock for async methods in CLI tests

**Solution**:
```python
# ❌ VERKEERD
def test_cli_command(self, capsys):
    with patch('module.AgentClass') as mock_agent_class:
        mock_agent = Mock()
        mock_agent.develop_strategy.return_value = {"status": "success"}
        mock_agent_class.return_value = mock_agent
        main()  # ValueError!

# ✅ CORRECT
def test_cli_command(self, capsys):
    with patch('module.AgentClass') as mock_agent_class:
        mock_agent = Mock()
        from unittest.mock import AsyncMock
        mock_develop_strategy = AsyncMock()
        mock_develop_strategy.return_value = {"status": "success"}
        mock_agent.develop_strategy = mock_develop_strategy
        mock_agent_class.return_value = mock_agent
        main()  # Works!
```

### Problem: `SystemExit: 1` in CLI tests

**Root Cause**: CLI main function fails due to async method issues

**Solution**:
```python
# ✅ CLI Main Function Fix
def main():
    # ... argument parsing ...
    
    if args.command == "develop-strategy":
        result = asyncio.run(agent.develop_strategy(args.strategy_name))
        print(f"Strategy developed successfully: {result}")
    elif args.command == "collaborate":
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        agent = asyncio.run(AgentClass.run_agent())
```

## Async Method Issues

### Problem: `SyntaxError: 'await' outside async function`

**Root Cause**: Using `await` in non-async method

**Solution**:
```python
# ❌ VERKEERD
def develop_strategy(self, strategy_name: str):
    enhanced_data = await self.use_mcp_tools(strategy_data)  # SyntaxError!

# ✅ CORRECT
async def develop_strategy(self, strategy_name: str):
    enhanced_data = await self.use_mcp_tools(strategy_data)  # Works!
```

### Problem: Incorrect async wrapper methods

**Root Cause**: Using `run_in_executor` for already async methods

**Solution**:
```python
# ❌ VERKEERD
async def _async_develop_strategy(self, strategy_name: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self.develop_strategy, strategy_name)

# ✅ CORRECT
async def _async_develop_strategy(self, strategy_name: str):
    return await self.develop_strategy(strategy_name)
```

## MCP Integration Issues

### Problem: MCP tools return None

**Root Cause**: MCP client not initialized or tools not available

**Solution**:
```python
# ✅ MCP Integration with Fallback
async def develop_strategy(self, strategy_name: str):
    # Try MCP first
    enhanced_data = await self.use_strategy_specific_mcp_tools(strategy_data)
    
    # Create result with or without MCP data
    result = {
        "strategy_name": strategy_name,
        "status": "developed",
        "timestamp": datetime.now().isoformat(),
        "agent": self.agent_name
    }
    
    # Add MCP enhanced data if available
    if enhanced_data:
        result["mcp_enhanced_data"] = enhanced_data
    
    return result
```

### Problem: MCP initialization fails

**Root Cause**: MCP client setup issues

**Solution**:
```python
# ✅ Robust MCP Initialization
async def initialize_mcp(self):
    """Initialize MCP client and integration."""
    try:
        self.mcp_client = await get_mcp_client()
        self.mcp_integration = get_framework_mcp_integration()
        await initialize_framework_mcp_integration()
        self.mcp_enabled = True
        logger.info("MCP client initialized successfully")
    except Exception as e:
        logger.warning(f"MCP initialization failed: {e}")
        self.mcp_enabled = False
```

## Performance Issues

### Problem: Tests run slowly

**Root Cause**: Unnecessary async operations or poor mocking

**Solution**:
```python
# ✅ Fast Async Tests
@pytest.mark.asyncio
async def test_fast_async_method(self, agent):
    # Mock time.sleep to speed up tests
    with patch('time.sleep'):
        result = await agent.develop_strategy("Test Strategy")
        assert result["status"] == "developed"
```

## Debugging Techniques

### 1. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Check MCP Status
```python
print(f"MCP Enabled: {self.mcp_enabled}")
print(f"MCP Client: {self.mcp_client}")
print(f"MCP Integration: {self.mcp_integration}")
```

### 3. Test Individual Components
```python
# Test MCP initialization
await agent.initialize_mcp()
assert agent.mcp_enabled in [True, False]

# Test MCP tool
result = await agent.use_mcp_tool("test_tool", {"param": "test"})
print(f"Tool Result: {result}")
```

### 4. Verify Async Method Calls
```python
# Check if method is async
import inspect
print(f"Is async: {inspect.iscoroutinefunction(agent.develop_strategy)}")
```

## Prevention Checklist

### Before Starting MCP Integration
- [ ] **Review Existing Patterns**: Check other agents for MCP patterns
- [ ] **Plan Async Changes**: Identify which methods need to be async
- [ ] **Prepare Test Updates**: Plan test modifications for async methods
- [ ] **Check Dependencies**: Ensure all MCP imports are available

### During MCP Integration
- [ ] **Incremental Changes**: Make one method async at a time
- [ ] **Test Each Change**: Run tests after each modification
- [ ] **Use Fallbacks**: Always provide fallback for MCP failures
- [ ] **Maintain Compatibility**: Keep existing functionality working

### After MCP Integration
- [ ] **Complete Test Suite**: Ensure all tests pass
- [ ] **Documentation Update**: Update guides with new patterns
- [ ] **Code Review**: Review for consistency and quality
- [ ] **Performance Check**: Verify no performance regressions

## Common Patterns

### Agent MCP Integration Pattern
```python
class AgentName:
    def __init__(self):
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False

    async def initialize_mcp(self):
        """Initialize MCP client and integration."""
        try:
            self.mcp_client = await get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False

    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]):
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

    async def agent_method(self, param: str):
        """Agent method with MCP enhancement."""
        # Use MCP tools
        enhanced_data = await self.use_agent_specific_mcp_tools(data)
        
        # Create result
        result = {
            "param": param,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name
        }
        
        # Add MCP data if available
        if enhanced_data:
            result["mcp_enhanced_data"] = enhanced_data
        
        return result

    async def run(self):
        """Start the agent with MCP initialization."""
        await self.initialize_mcp()
        # ... rest of run logic ...

    @classmethod
    async def run_agent(cls):
        """Class method to run the agent with proper async setup."""
        agent = cls()
        await agent.run()
        return agent
```

### Test Pattern for MCP Integration
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
import logging

from bmad.agents.Agent.AgentName.agentname import AgentName

# Configure logging for tests
logger = logging.getLogger(__name__)

class TestAgentName:
    @pytest.fixture
    def agent(self):
        return AgentName()

    @pytest.mark.asyncio
    async def test_agent_method_success(self, agent):
        """Test successful agent method execution."""
        with patch('time.sleep'):
            result = await agent.agent_method("test_param")
            assert result["status"] == "completed"
            assert result["param"] == "test_param"

    @pytest.mark.asyncio
    async def test_agent_method_empty_param(self, agent):
        """Test agent method with empty parameter."""
        with pytest.raises(ValidationError):
            await agent.agent_method("")

class TestAgentNameCLI:
    @patch('sys.argv', ['test_agent.py', 'method-name', '--param', 'test'])
    def test_cli_method_command(self, capsys):
        """Test CLI method command."""
        with patch('module.AgentName') as mock_agent_class:
            mock_agent = Mock()
            mock_method = AsyncMock()
            mock_method.return_value = {"status": "success"}
            mock_agent.agent_method = mock_method
            mock_agent_class.return_value = mock_agent

            main()

class TestAgentNameIntegration:
    @pytest.fixture
    def agent(self):
        return AgentName()

    @pytest.mark.asyncio
    async def test_complete_workflow(self, agent):
        """Test complete agent workflow."""
        result = await agent.agent_method("test_param")
        assert result["status"] == "completed"
        logger.info("Integration test completed successfully")
```

## Resources

### Related Guides
- **MCP Integration Guide**: `MCP_INTEGRATION_GUIDE.md`
- **Best Practices Guide**: `BEST_PRACTICES_GUIDE.md`
- **Lessons Learned Guide**: `LESSONS_LEARNED_GUIDE.md`
- **Development Workflow Guide**: `DEVELOPMENT_WORKFLOW_GUIDE.md`
- **Test Workflow Guide**: `TEST_WORKFLOW_GUIDE.md`

### External Resources
- **Pytest-asyncio Documentation**: https://pytest-asyncio.readthedocs.io/
- **Python Async/Await Guide**: https://docs.python.org/3/library/asyncio.html
- **Unittest.mock Documentation**: https://docs.python.org/3/library/unittest.mock.html

---

**Note**: Deze guide wordt regelmatig bijgewerkt met nieuwe troubleshooting informatie uit echte MCP integratie ervaringen. 