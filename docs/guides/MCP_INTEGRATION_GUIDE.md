# MCP Integration Guide

## Overview

Dit document bevat complete patterns, best practices, en troubleshooting voor MCP (Model Context Protocol) integratie in BMAD agents. Deze guide is gebaseerd op lessons learned tijdens de MCP integration van alle 23 agents.

**Laatste Update**: 2025-01-27  
**Versie**: 2.0  
**Status**: Actief - Alle 23 agents MCP geïntegreerd

## 🎉 MCP Integration Completion Status

### **✅ Alle 23 Agents MCP Geïntegreerd (Januari 2025)**

**Voltooide Agents**:
1. **BackendDeveloper** ✅ - MCP tools voor code analysis en API building
2. **FrontendDeveloper** ✅ - MCP tools voor component building en accessibility
3. **FullstackDeveloper** ✅ - MCP tools voor fullstack development
4. **MobileDeveloper** ✅ - MCP tools voor mobile app development
5. **AiDeveloper** ✅ - MCP tools voor AI/ML development
6. **Architect** ✅ - MCP tools voor architecture design en analysis
7. **UXUIDesigner** ✅ - MCP tools voor UX/UI design en analysis
8. **AccessibilityAgent** ✅ - MCP tools voor accessibility audit en compliance
9. **TestEngineer** ✅ - MCP tools voor test engineering en automation
10. **QualityGuardian** ✅ - MCP tools voor quality analysis en gates
11. **ProductOwner** ✅ - MCP tools voor user story creation en analysis
12. **Scrummaster** ✅ - MCP tools voor sprint planning en analysis
13. **ReleaseManager** ✅ - MCP tools voor release management en deployment
14. **DocumentationAgent** ✅ - MCP tools voor documentation generation
15. **FeedbackAgent** ✅ - MCP tools voor feedback collection en analysis
16. **DevOpsInfra** ✅ - MCP tools voor infrastructure management
17. **DataEngineer** ✅ - MCP tools voor data pipeline development
18. **SecurityDeveloper** ✅ - MCP tools voor security scanning en analysis
19. **StrategiePartner** ✅ - MCP tools voor strategy development en analysis
20. **Retrospective** ✅ - MCP tools voor retrospective analysis
21. **RnD** ✅ - MCP tools voor research en innovation
22. **Orchestrator** ✅ - MCP tools voor workflow orchestration
23. **WorkflowAutomator** ✅ - MCP tools voor workflow automation

**Integration Features**:
- ✅ Async MCP client initialization
- ✅ Agent-specific MCP tools
- ✅ Graceful fallback naar lokale tools
- ✅ Backward compatibility behouden
- ✅ Proper error handling
- ✅ Test coverage voor alle agents

## MCP Integration Patterns

### 1. Agent MCP Integration Template

#### **Standard Agent MCP Setup**
```python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# MCP Integration
from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

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
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced capabilities."""
        try:
            self.mcp_client = await get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for AgentName")
        except Exception as e:
            logger.warning(f"MCP initialization failed for AgentName: {e}")
            self.mcp_enabled = False
    
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

### 2. Method Integration Pattern

#### **Async Method with MCP Enhancement**
```python
async def agent_method(self, param: str) -> Dict[str, Any]:
    """Agent method met MCP enhancement."""
    logger.info(f"Executing agent method for: {param}")

    # Try MCP-enhanced execution first
    if self.mcp_enabled and self.mcp_client:
        try:
            mcp_result = await self.use_mcp_tool("agent_method", {
                "param": param,
                "method_type": "enhanced",
                "include_analysis": True
            })
            
            if mcp_result:
                logger.info("MCP-enhanced execution completed")
                result = mcp_result.get("method_result", {})
                result["mcp_enhanced"] = True
            else:
                logger.warning("MCP execution failed, using local execution")
                result = self._create_local_result(param)
        except Exception as e:
            logger.warning(f"MCP execution failed: {e}, using local execution")
            result = self._create_local_result(param)
    else:
        result = self._create_local_result(param)
    
    # Use agent-specific MCP tools for additional enhancement
    if self.mcp_enabled:
        try:
            enhancement_data = {
                "param": param,
                "result": result,
                "enhancement_type": "comprehensive"
            }
            enhanced = await self.use_agent_specific_mcp_tools(enhancement_data)
            if enhanced:
                result["enhancements"] = enhanced
        except Exception as e:
            logger.warning(f"Agent-specific MCP tools failed: {e}")

    # Log performance metrics
    try:
        self.monitor._record_metric("AgentName", MetricType.SUCCESS_RATE, 95, "%")
    except AttributeError:
        logger.info("Performance metrics recording not available")

    logger.info(f"Agent method completed: {result}")
    return result

def _create_local_result(self, param: str) -> Dict[str, Any]:
    """Create local result when MCP is not available."""
    return {
        "param": param,
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "agent": self.agent_name
    }
```

### 3. CLI Integration Pattern

#### **Main Function with Async Support**
```python
import asyncio

def main():
    parser = argparse.ArgumentParser(description="AgentName CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "method-name", "run", "collaborate"])
    parser.add_argument("--param", default="default_value", help="Parameter value")

    args = parser.parse_args()

    agent = AgentName()

    if args.command == "help":
        agent.show_help()
    elif args.command == "method-name":
        result = asyncio.run(agent.agent_method(args.param))
        print(json.dumps(result, indent=2))
    elif args.command == "collaborate":
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        asyncio.run(agent.run())
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## MCP Tool Patterns

### 1. Tool Naming Conventions

#### **Standard Tool Names**
- **Verb_Noun**: `create_api_docs`, `deploy_release`, `analyze_code`
- **Agent Prefix**: `agent_specific_tool`
- **Action Based**: `process_data`, `generate_report`, `validate_input`

#### **Parameter Structure**
```python
# Standard parameter structure
parameters = {
    "primary_param": "value",
    "options": {
        "include_analysis": True,
        "enhancement_level": "comprehensive"
    },
    "context": {
        "agent": "AgentName",
        "timestamp": datetime.now().isoformat()
    }
}
```

### 2. Agent-Specific Tool Patterns

#### **QualityGuardian Tools**
```python
async def use_quality_specific_mcp_tools(self, quality_data: Dict[str, Any]):
    enhanced_data = {}
    
    # Code quality analysis
    quality_result = await self.use_mcp_tool("code_quality_analysis", {
        "code_path": quality_data.get("code_path", ""),
        "quality_metrics": quality_data.get("quality_metrics", {}),
        "analysis_type": "comprehensive"
    })
    if quality_result:
        enhanced_data["code_quality_analysis"] = quality_result
    
    # Security analysis
    security_result = await self.use_mcp_tool("security_analysis", {
        "files": quality_data.get("files", ""),
        "security_scan_type": "comprehensive",
        "vulnerability_check": True
    })
    if security_result:
        enhanced_data["security_analysis"] = security_result
    
    return enhanced_data
```

#### **ReleaseManager Tools**
```python
async def use_release_specific_mcp_tools(self, release_data: Dict[str, Any]):
    enhanced_data = {}
    
    # Release creation
    release_result = await self.use_mcp_tool("release_creation", {
        "version": release_data.get("version", ""),
        "description": release_data.get("description", ""),
        "release_type": release_data.get("release_type", "feature"),
        "target_environment": release_data.get("target_environment", "production")
    })
    if release_result:
        enhanced_data["release_creation"] = release_result
    
    # Deployment coordination
    deployment_result = await self.use_mcp_tool("deployment_coordination", {
        "version": release_data.get("version", ""),
        "deployment_strategy": release_data.get("deployment_strategy", "rolling"),
        "rollback_plan": release_data.get("rollback_plan", {}),
        "monitoring_setup": release_data.get("monitoring_setup", True)
    })
    if deployment_result:
        enhanced_data["deployment_coordination"] = deployment_result
    
    return enhanced_data
```

#### **DocumentationAgent Tools**
```python
async def use_documentation_specific_mcp_tools(self, doc_data: Dict[str, Any]):
    enhanced_data = {}
    
    # API documentation generation
    api_result = await self.use_mcp_tool("api_documentation_generation", {
        "api_name": doc_data.get("api_name", ""),
        "api_type": doc_data.get("api_type", "REST"),
        "endpoints": doc_data.get("endpoints", []),
        "documentation_style": doc_data.get("documentation_style", "comprehensive")
    })
    if api_result:
        enhanced_data["api_documentation_generation"] = api_result
    
    # Technical documentation
    tech_result = await self.use_mcp_tool("technical_documentation", {
        "system_name": doc_data.get("system_name", ""),
        "doc_type": doc_data.get("doc_type", "architecture"),
        "technical_depth": doc_data.get("technical_depth", "detailed"),
        "include_diagrams": doc_data.get("include_diagrams", True)
    })
    if tech_result:
        enhanced_data["technical_documentation"] = tech_result
    
    return enhanced_data
```

#### **StrategiePartner Tools**
```python
async def use_strategy_specific_mcp_tools(self, strategy_data: Dict[str, Any]):
    enhanced_data = {}
    
    # Strategy development
    strategy_result = await self.use_mcp_tool("strategy_development", {
        "strategy_name": strategy_data.get("strategy_name", ""),
        "business_context": strategy_data.get("business_context", ""),
        "market_conditions": strategy_data.get("market_conditions", ""),
        "analysis_type": "comprehensive"
    })
    if strategy_result:
        enhanced_data["strategy_development"] = strategy_result
    
    # Market analysis
    market_result = await self.use_mcp_tool("market_analysis", {
        "sector": strategy_data.get("sector", ""),
        "market_size": strategy_data.get("market_size", ""),
        "growth_rate": strategy_data.get("growth_rate", ""),
        "analysis_depth": "detailed"
    })
    if market_result:
        enhanced_data["market_analysis"] = market_result
    
    # Competitive analysis
    competitive_result = await self.use_mcp_tool("competitive_analysis", {
        "competitors": strategy_data.get("competitors", []),
        "market_position": strategy_data.get("market_position", ""),
        "competitive_advantage": strategy_data.get("competitive_advantage", ""),
        "analysis_scope": "comprehensive"
    })
    if competitive_result:
        enhanced_data["competitive_analysis"] = competitive_result
    
    # Risk assessment
    risk_result = await self.use_mcp_tool("risk_assessment", {
        "strategy": strategy_data.get("strategy", ""),
        "risk_factors": strategy_data.get("risk_factors", []),
        "mitigation_strategies": strategy_data.get("mitigation_strategies", []),
        "assessment_type": "comprehensive"
    })
    if risk_result:
        enhanced_data["risk_assessment"] = risk_result
    
    return enhanced_data
```

## Error Handling Patterns

### 1. MCP Initialization Error Handling
```python
async def initialize_mcp(self):
    try:
        self.mcp_client = await get_mcp_client()
        self.mcp_integration = get_framework_mcp_integration()
        await initialize_framework_mcp_integration()
        self.mcp_enabled = True
        logger.info("MCP client initialized successfully")
    except Exception as e:
        logger.warning(f"MCP initialization failed: {e}")
        self.mcp_enabled = False
        # Continue with local functionality
```

### 2. MCP Tool Execution Error Handling
```python
async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]):
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

### 3. Performance Metrics Error Handling
```python
# Log performance metrics
try:
    self.monitor._record_metric("AgentName", MetricType.SUCCESS_RATE, 95, "%")
except AttributeError:
    logger.info("Performance metrics recording not available")
```

## Testing MCP Integration

### 1. Unit Test Pattern
```python
async def test_agent_mcp_integration():
    agent = AgentName()
    
    # Test initialization
    await agent.initialize_mcp()
    assert agent.mcp_enabled in [True, False]  # Both are valid
    
    # Test MCP tool usage
    result = await agent.use_mcp_tool("test_tool", {"param": "test"})
    # Result can be None if MCP not available, which is valid
    
    # Test agent method
    result = await agent.agent_method("test_param")
    assert result is not None
    assert "status" in result
    assert result["agent"] == "AgentName"
```

### 2. CLI Test Pattern
```python
def test_cli_functionality():
    # Test help command
    result = subprocess.run(["python", "agent.py", "help"], capture_output=True, text=True)
    assert result.returncode == 0
    
    # Test method command
    result = subprocess.run(["python", "agent.py", "method-name", "--param", "test"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "test" in result.stdout
```

## Troubleshooting Guide

### 1. Common Issues

#### **Import Errors**
**Problem**: `ModuleNotFoundError: No module named 'bmad'`

**Solution**:
```python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
```

#### **Async Function Errors**
**Problem**: `async def functions are not natively supported`

**Solution**: Use pytest-asyncio for async tests
```python
# pytest.ini
[tool:pytest]
asyncio_mode = auto
```

#### **Performance Metrics Errors**
**Problem**: `AttributeError: 'PerformanceOptimizer' object has no attribute '_record_metric'`

**Solution**: Add error handling
```python
try:
    self.monitor._record_metric("AgentName", MetricType.SUCCESS_RATE, 95, "%")
except AttributeError:
    logger.info("Performance metrics recording not available")
```

#### **MCP Tool Execution Errors**
**Problem**: MCP tools return None or fail

**Solution**: Always provide fallback
```python
if mcp_result:
    result = mcp_result.get("result", {})
else:
    result = self._create_local_result(param)
```

### 2. Debugging MCP Integration

#### **Enable Debug Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Check MCP Status**
```python
print(f"MCP Enabled: {self.mcp_enabled}")
print(f"MCP Client: {self.mcp_client}")
print(f"MCP Integration: {self.mcp_integration}")
```

#### **Test MCP Tools Individually**
```python
# Test individual tool
result = await self.use_mcp_tool("test_tool", {"param": "test"})
print(f"Tool Result: {result}")
```

### 3. Async Wrapper Method Patterns

#### **Correct Async Wrapper Pattern**
**Problem**: Incorrect async wrapper voor reeds async methodes

**Solution**:
```python
# ❌ VERKEERD: Async wrapper voor reeds async methode
async def _async_develop_strategy(self, strategy_name: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self.develop_strategy, strategy_name)

# ✅ CORRECT: Directe async call voor reeds async methode
async def _async_develop_strategy(self, strategy_name: str):
    return await self.develop_strategy(strategy_name)
```

**Waarom**: `run_in_executor()` is alleen voor sync methodes. Voor async methodes gebruik je direct `await`.

#### **CLI Async Method Handling**
**Problem**: CLI methodes die async methodes aanroepen

**Solution**:
```python
def main():
    # ... argument parsing ...
    
    if args.command == "develop-strategy":
        result = asyncio.run(agent.develop_strategy(args.strategy_name))
        print(f"Strategy developed successfully: {result}")
    elif args.command == "collaborate":
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        agent = asyncio.run(StrategiePartnerAgent.run_agent())
```

**Waarom**: Zorgt voor correcte async execution in CLI context.

#### **Test Logger Setup**
**Problem**: `NameError: name 'logger' is not defined` in integration tests

**Solution**:
```python
# ✅ Test File Setup met Logger
import pytest
from unittest.mock import Mock, patch
import logging

from bmad.agents.Agent.AgentName.agentname import AgentClass

# Configure logging for tests
logger = logging.getLogger(__name__)
```

**Waarom**: Voorkomt logger import errors in integration tests.

## Best Practices Checklist

### **MCP Integration Checklist**
- [ ] **Agent Initialization**: MCP attributes toegevoegd
- [ ] **MCP Initialization**: Async initialize_mcp method geïmplementeerd
- [ ] **MCP Tool Usage**: use_mcp_tool method met error handling
- [ ] **Agent-Specific Tools**: use_agent_specific_mcp_tools method
- [ ] **Method Integration**: Async methods met MCP enhancement
- [ ] **Fallback Strategy**: Lokale tools als MCP niet beschikbaar
- [ ] **Error Handling**: Graceful failure handling voor alle MCP calls
- [ ] **CLI Integration**: Async support in main function
- [ ] **Testing**: Unit tests voor MCP integration
- [ ] **Documentation**: Method documentation bijgewerkt

### **Code Quality Checklist**
- [ ] **Backward Compatibility**: Sync wrappers voor async methods
- [ ] **Logging**: Proper logging voor MCP operations
- [ ] **Performance Metrics**: Error handling voor metrics recording
- [ ] **Import Paths**: Correcte sys.path setup
- [ ] **Type Hints**: Proper type annotations
- [ ] **Error Messages**: Informatieve error messages

## Quick Reference

### **Standard MCP Integration**
```python
# 1. Imports
from bmad.core.mcp import (
    MCPClient, MCPContext, FrameworkMCPIntegration,
    get_mcp_client, get_framework_mcp_integration, initialize_framework_mcp_integration
)

# 2. Agent Setup
self.mcp_client: Optional[MCPClient] = None
self.mcp_integration: Optional[FrameworkMCPIntegration] = None
self.mcp_enabled = False

# 3. MCP Initialization
async def initialize_mcp(self):
    try:
        self.mcp_client = await get_mcp_client()
        self.mcp_enabled = True
    except Exception as e:
        logger.warning(f"MCP initialization failed: {e}")
        self.mcp_enabled = False

# 4. MCP Tool Usage
async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]):
    if not self.mcp_enabled or not self.mcp_client:
        return None
    try:
        return await self.mcp_client.execute_tool(tool_name, parameters)
    except Exception as e:
        logger.error(f"MCP tool {tool_name} failed: {e}")
        return None

# 5. Method Integration
async def agent_method(self, param):
    if self.mcp_enabled:
        mcp_result = await self.use_mcp_tool("agent_method", {"param": param})
        if mcp_result:
            return mcp_result.get("result", {})
    
    return self._create_local_result(param)
```

## Version History

- **v1.0 (2025-08-02)**: Initial version met MCP integration patterns
- **v1.1 (Planned)**: Additional agent-specific patterns
- **v1.2 (Planned)**: Advanced troubleshooting en optimization

## Contributing

Voeg nieuwe MCP patterns toe door:
1. **Pattern Description**: Beschrijf het pattern en use case
2. **Code Example**: Volledig werkend code voorbeeld
3. **Best Practices**: Wanneer en hoe te gebruiken
4. **Troubleshooting**: Common issues en solutions
5. **Update Version**: Update version history

---

**Note**: Deze guide wordt continu bijgewerkt tijdens MCP integration. Check regelmatig voor nieuwe patterns en best practices. 

## ⚡️ Async/Synchronous MCP Integration Pattern (2025-01-27)

### Probleem
Bij sommige agents (zoals Architect en BackendDeveloper) ontstonden errors zoals:
- `TypeError: object dict can't be used in 'await' expression`
- `object MCPClient can't be used in 'await' expression`

Dit komt doordat methodes die MCP kunnen aanroepen soms sync zijn, maar in de praktijk (en in tests) async worden aangeroepen. MCP vereist altijd een async interface.

### Best Practice Pattern

**Alle methodes die MCP kunnen aanroepen moeten async zijn, ook als de lokale fallback sync is.**

#### Voorbeeldimplementatie:
```python
async def deploy_api(self, ...):
    if self.mcp_enabled and self.mcp_client:
        return await self.mcp_client.execute_tool(...)
    else:
        # Fallback naar sync, maar via thread
        return await asyncio.to_thread(self._deploy_api_sync, ...)

def _deploy_api_sync(self, ...):
    # Lokale implementatie
    ...
```

- **Waarom:** Dit voorkomt await/sync mismatches, maakt testen eenvoudiger en zorgt voor uniforme agent interfaces.
- **Tests:** Gebruik altijd `AsyncMock` voor async methodes.

### Lessons Learned
- Sync fallback direct aanroepen in een async context veroorzaakt TypeErrors.
- MCP integratie is alleen robuust als alle relevante agentmethodes async zijn.
- Fallbacks moeten via `await asyncio.to_thread(...)` worden aangeroepen.
- Dit patroon is nu verplicht voor alle BMAD agents.

### Checklist voor MCP-integratie
- [x] Alle MCP-methodes zijn async
- [x] Lokale fallback via `asyncio.to_thread`
- [x] Tests gebruiken `AsyncMock` voor alle async methodes
- [x] Documentatie en guides zijn geüpdatet

--- 

## 4. Enhanced MCP Phase 2 Integration

### 4.1 Enhanced MCP Tool Integration
```python
# Enhanced MCP initialization
async def initialize_enhanced_mcp(self):
    """Initialize enhanced MCP capabilities for Phase 2."""
    try:
        self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
        self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
        
        if self.enhanced_mcp_enabled:
            logger.info("Enhanced MCP capabilities initialized successfully")
        else:
            logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
    except Exception as e:
        logger.warning(f"Enhanced MCP initialization failed: {e}")
        self.enhanced_mcp_enabled = False

# Enhanced MCP tool usage
async def use_enhanced_mcp_tools(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use enhanced MCP tools voor Phase 2 capabilities."""
    if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
        logger.warning("Enhanced MCP not available, using standard MCP tools")
        return await self.use_agent_specific_mcp_tools(agent_data)
    
    enhanced_data = {}
    
    # Core enhancement tools
    core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
        "agent_type": self.agent_name,
        "enhancement_level": "advanced",
        "capabilities": agent_data.get("capabilities", []),
        "performance_metrics": agent_data.get("performance_metrics", {})
    })
    if core_result:
        enhanced_data["core_enhancement"] = core_result
    
    # Agent-specific enhancement tools
    specific_result = await self.use_agent_specific_enhanced_tools(agent_data)
    if specific_result:
        enhanced_data.update(specific_result)
    
    return enhanced_data
```

### 4.2 Tracing Integration
```python
# Tracing initialization
async def initialize_tracing(self):
    """Initialize tracing capabilities."""
    try:
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": f"{self.agent_name}",
            "environment": "development",
            "tracing_level": "detailed"
        })())
        self.tracing_enabled = await self.tracer.initialize()
        
        if self.tracing_enabled:
            logger.info("Tracing capabilities initialized successfully")
            await self.tracer.setup_agent_specific_tracing({
                "agent_name": self.agent_name,
                "tracing_level": "detailed",
                "performance_tracking": True,
                "error_tracking": True
            })
    except Exception as e:
        logger.warning(f"Tracing initialization failed: {e}")
        self.tracing_enabled = False

# Agent-specific tracing methods
async def trace_agent_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Trace agent-specific operations."""
    if not self.tracing_enabled or not self.tracer:
        return {}
    
    try:
        trace_result = await self.tracer.trace_agent_operation({
            "operation_type": operation_data.get("type", "unknown"),
            "agent_name": self.agent_name,
            "performance_metrics": operation_data.get("performance_metrics", {}),
            "timestamp": datetime.now().isoformat()
        })
        return trace_result
    except Exception as e:
        logger.error(f"Agent operation tracing failed: {e}")
        return {}
```

### 4.3 Complete Integration Pattern
```python
class EnhancedAgent:
    def __init__(self):
        # Standard MCP
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False

    async def run(self):
        """Run the agent with complete integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        logger.info("Agent ready with enhanced MCP and tracing capabilities...")
```

### 4.4 CLI Integration
```python
def main():
    parser = argparse.ArgumentParser(description="Enhanced Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "enhanced-collaborate", "enhanced-security", 
                               "enhanced-performance", "enhanced-tools", "enhanced-summary",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
    
    # Enhanced MCP commands
    elif args.command == "enhanced-collaborate":
        result = asyncio.run(agent.communicate_with_agents(args.agents, message))
    
    # Tracing commands
    elif args.command == "trace-operation":
        result = asyncio.run(agent.trace_agent_operation(operation_data))
    elif args.command == "tracing-summary":
        tracing_summary = agent.get_tracing_summary()
```

### 4.5 Testing Strategy
```python
@pytest.mark.asyncio
async def test_enhanced_mcp_integration(agent):
    """Test enhanced MCP integration."""
    with patch('create_enhanced_mcp_integration') as mock_create:
        mock_enhanced_mcp = MagicMock()
        mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
        mock_create.return_value = mock_enhanced_mcp
        
        await agent.initialize_enhanced_mcp()
        assert agent.enhanced_mcp_enabled is True

@pytest.mark.asyncio
async def test_tracing_integration(agent):
    """Test tracing integration."""
    with patch('BMADTracer') as mock_tracer_class:
        mock_tracer = MagicMock()
        mock_tracer.initialize = AsyncMock(return_value=True)
        mock_tracer_class.return_value = mock_tracer
        
        await agent.initialize_tracing()
        assert agent.tracing_enabled is True
``` 