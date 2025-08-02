#!/usr/bin/env python3
"""
Test script for MCP Quality Solutions - Testing the new architecture
Testing the quality solutions without removing existing functionality
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from bmad.core.mcp import (
    MCPClient,
    MCPTool,
    MCPContext,
    MCPToolRegistry,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_mcp_tool_registry,
    get_framework_mcp_integration
)
from bmad.core.mcp.agent_mixin import MCPAgentMixin, MCPAgentConfig, create_mcp_agent_config
from bmad.core.mcp.dependency_manager import DependencyManager, get_dependency_manager

class QualityTestAgent(MCPAgentMixin):
    """Test agent for quality solutions testing."""
    
    def __init__(self):
        # Initialize with test configuration
        mcp_config = create_mcp_agent_config(
            agent_name="QualityTestAgent",
            agent_type="Testing",
            tool_categories=["development", "testing", "quality"],
            custom_tools=["test_tool"],
            error_handling="graceful"
        )
        super().__init__(mcp_config)
        
        self.test_results = []
    
    async def test_enhanced_operation(self, operation_name: str, operation_data: dict) -> dict:
        """Test enhanced operation functionality."""
        result = await self.enhanced_operation(operation_name, operation_data)
        self.test_results.append({
            "test": "enhanced_operation",
            "operation": operation_name,
            "result": result
        })
        return result
    
    async def test_multiple_tools(self, tool_calls: list) -> dict:
        """Test multiple MCP tools execution."""
        result = await self.use_multiple_mcp_tools(tool_calls)
        self.test_results.append({
            "test": "multiple_tools",
            "tool_calls": tool_calls,
            "result": result
        })
        return result

async def test_agent_mixin_quality():
    """Test MCP Agent Mixin quality solutions."""
    print("🧪 Testing MCP Agent Mixin Quality Solutions...")
    
    try:
        # Create test agent
        agent = QualityTestAgent()
        print(f"✅ QualityTestAgent created with mixin")
        
        # Test MCP initialization
        mcp_success = await agent.initialize_mcp()
        print(f"✅ Agent MCP initialization: {mcp_success}")
        
        if mcp_success:
            # Test enhanced operation
            enhanced_result = await agent.test_enhanced_operation(
                "test_operation",
                {"code": "def test(): pass", "language": "python"}
            )
            print(f"✅ Enhanced operation: {enhanced_result.get('mcp_enhanced', False)}")
            
            # Test multiple tools
            tool_calls = [
                {"tool": "code_analysis", "parameters": {"code": "def test(): pass", "language": "python", "analysis_type": "quality"}},
                {"tool": "test_generation", "parameters": {"code": "def test(): pass", "language": "python", "framework": "pytest", "test_type": "unit"}}
            ]
            multiple_result = await agent.test_multiple_tools(tool_calls)
            print(f"✅ Multiple tools execution: {len(multiple_result)} tools executed")
            
            # Test status reporting
            status = agent.get_mcp_status()
            print(f"✅ MCP status reporting: {status['mcp_enabled']}")
            
            return True
        else:
            print("⚠️ MCP initialization failed")
            return False
        
    except Exception as e:
        print(f"❌ Agent Mixin Quality test failed: {e}")
        return False

async def test_dependency_manager_quality():
    """Test Dependency Manager quality solutions."""
    print("\n🧪 Testing Dependency Manager Quality Solutions...")
    
    try:
        # Create dependency manager
        manager = get_dependency_manager()
        print(f"✅ Dependency Manager created")
        
        # Test required dependencies
        required_modules = ["asyncio", "json", "logging", "pathlib"]
        for module in required_modules:
            available = manager.is_module_available(module)
            print(f"✅ Required module {module}: {available}")
        
        # Test optional dependencies
        optional_modules = ["psutil", "aiohttp", "fastapi"]
        for module in optional_modules:
            available = manager.is_module_available(module)
            print(f"✅ Optional module {module}: {available}")
        
        # Test health report
        health_report = manager.get_dependency_health_report()
        print(f"✅ Health report: {health_report['load_success_rate']:.1f}% success rate")
        
        # Test feature checker
        feature_checker = manager.create_feature_checker(["asyncio", "json"])
        feature_available = feature_checker()
        print(f"✅ Feature checker: {feature_available}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency Manager Quality test failed: {e}")
        return False

async def test_frontend_developer_quality():
    """Test FrontendDeveloper agent with quality solutions."""
    print("\n🧪 Testing FrontendDeveloper Agent Quality Solutions...")
    
    try:
        # Check if psutil is available before importing FrontendDeveloper
        import importlib.util
        psutil_available = importlib.util.find_spec('psutil') is not None
        
        if not psutil_available:
            print("⚠️ psutil not available, testing FrontendDeveloper with dependency isolation")
            
            # Test dependency manager functionality
            manager = get_dependency_manager()
            psutil_available_via_manager = manager.is_module_available('psutil')
            print(f"✅ Dependency manager psutil check: {psutil_available_via_manager}")
            
            # Test that the agent can be created without psutil
            try:
                from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
                agent = FrontendDeveloperAgent()
                print(f"✅ FrontendDeveloper agent created successfully without psutil")
                
                # Test MCP initialization
                mcp_success = await agent.initialize_mcp()
                print(f"✅ FrontendDeveloper MCP initialization: {mcp_success}")
                
                if mcp_success:
                    # Test enhanced component building
                    component_result = await agent.build_shadcn_component("TestButton")
                    print(f"✅ Enhanced component building: {'frontend_enhancements' in component_result}")
                    
                    # Test status reporting
                    status = agent.get_frontend_mcp_status()
                    print(f"✅ Frontend MCP status: {status['mcp_enabled']}")
                    
                    return True
                else:
                    print("⚠️ FrontendDeveloper MCP initialization failed")
                    return False
                    
            except ImportError as e:
                if 'psutil' in str(e):
                    print("❌ FrontendDeveloper still has psutil dependency issues")
                    return False
                else:
                    raise e
        else:
            # psutil is available, test normally
            from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
            
            # Create agent
            agent = FrontendDeveloperAgent()
            print(f"✅ FrontendDeveloper agent created")
            
            # Test MCP initialization
            mcp_success = await agent.initialize_mcp()
            print(f"✅ FrontendDeveloper MCP initialization: {mcp_success}")
            
            if mcp_success:
                # Test enhanced component building
                component_result = await agent.build_shadcn_component("TestButton")
                print(f"✅ Enhanced component building: {'frontend_enhancements' in component_result}")
                
                # Test frontend-specific MCP tools
                component_data = {
                    "code": "const Button = () => <button>Click me</button>",
                    "accessibility_score": 95,
                    "wcag_compliance": True
                }
                frontend_result = await agent.use_frontend_specific_mcp_tools(component_data)
                print(f"✅ Frontend-specific MCP tools: {len(frontend_result)} enhancements")
                
                # Test status reporting
                status = agent.get_frontend_mcp_status()
                print(f"✅ Frontend MCP status: {status['mcp_enabled']}")
                
                return True
            else:
                print("⚠️ FrontendDeveloper MCP initialization failed")
                return False
        
    except Exception as e:
        print(f"❌ FrontendDeveloper Quality test failed: {e}")
        return False

async def test_mcp_workflow_quality():
    """Test complete MCP workflow with quality solutions."""
    print("\n🧪 Testing Complete MCP Workflow Quality...")
    
    try:
        # Initialize all components
        client = get_mcp_client()
        await client.connect()
        
        registry = get_mcp_tool_registry()
        
        integration = get_framework_mcp_integration()
        await integration.initialize(client)
        
        # Create context
        context = await client.create_context(
            user_id="quality_test",
            agent_id="test_agent",
            project_id="quality_project"
        )
        
        # Test complete workflow with error handling
        workflow_steps = [
            ("code_analysis", {"code": "def hello(): print('world')", "language": "python", "analysis_type": "quality"}),
            ("test_generation", {"code": "def hello(): pass", "language": "python", "framework": "pytest", "test_type": "unit"}),
            ("quality_gate", {"metrics": {"coverage": 85, "quality_score": 90}, "thresholds": {"coverage": 80, "quality_score": 70}}),
            ("documentation_generator", {"source": "# Test Module", "output_format": "markdown"})
        ]
        
        successful_steps = 0
        for tool_name, parameters in workflow_steps:
            try:
                response = await integration.call_framework_tool(tool_name, parameters, context)
                if response.success:
                    successful_steps += 1
                    print(f"✅ {tool_name}: Success")
                else:
                    print(f"⚠️ {tool_name}: {response.error}")
            except Exception as e:
                print(f"❌ {tool_name}: {e}")
        
        print(f"✅ Workflow completion: {successful_steps}/{len(workflow_steps)} steps successful")
        
        return successful_steps == len(workflow_steps)
        
    except Exception as e:
        print(f"❌ MCP Workflow Quality test failed: {e}")
        return False

async def test_backward_compatibility():
    """Test backward compatibility with existing functionality."""
    print("\n🧪 Testing Backward Compatibility...")
    
    try:
        # Test that existing MCP core functionality still works
        client = get_mcp_client()
        await client.connect()
        
        # Test existing tool execution
        context = await client.create_context(
            user_id="compatibility_test",
            agent_id="test_agent",
            project_id="compatibility_project"
        )
        
        response = await client.call_tool("file_system", {
            "operation": "exists",
            "path": "test.txt"
        }, context)
        
        print(f"✅ Backward compatibility: {response.success}")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

async def main():
    """Run all quality solution tests."""
    print("🚀 Starting MCP Quality Solutions Tests")
    print("=" * 60)
    
    tests = [
        ("Agent Mixin Quality", test_agent_mixin_quality),
        ("Dependency Manager Quality", test_dependency_manager_quality),
        ("FrontendDeveloper Quality", test_frontend_developer_quality),
        ("MCP Workflow Quality", test_mcp_workflow_quality),
        ("Backward Compatibility", test_backward_compatibility)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MCP Quality Solutions Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MCP Quality Solutions tests passed! Implementation is robust and production-ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the quality solutions implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 