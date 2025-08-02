#!/usr/bin/env python3
"""
Test script for MCP Phase 2: Agent Enhancement
Testing enhanced MCP implementation following official specification
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
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

async def test_mcp_core_components():
    """Test MCP core components following official specification."""
    print("🧪 Testing MCP Core Components...")
    
    try:
        # Test MCP Client
        client = get_mcp_client()
        print(f"✅ MCP Client created: {client.session_id}")
        
        # Test connection
        connected = await client.connect()
        print(f"✅ MCP Client connection: {connected}")
        
        # Test tool registration
        tools = client.get_tools()
        print(f"✅ Default tools registered: {len(tools)}")
        
        # Test context creation
        context = await client.create_context(
            user_id="test_user",
            agent_id="test_agent",
            project_id="test_project"
        )
        print(f"✅ Context created: {context.session_id}")
        
        # Test tool execution
        response = await client.call_tool("file_system", {
            "operation": "exists",
            "path": "test.txt"
        }, context)
        print(f"✅ Tool execution: {response.success}")
        
        # Test statistics
        stats = client.get_statistics()
        print(f"✅ Client statistics: {stats['tools_count']} tools, {stats['requests_count']} requests")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Core Components test failed: {e}")
        return False

async def test_tool_registry():
    """Test MCP Tool Registry following official specification."""
    print("\n🧪 Testing MCP Tool Registry...")
    
    try:
        # Test registry creation
        registry = get_mcp_tool_registry()
        print(f"✅ Tool Registry created")
        
        # Test tool registration
        test_tool = MCPTool(
            name="test_tool",
            description="Test tool for validation",
            input_schema={"type": "object", "properties": {"test": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
            category="testing"
        )
        
        success = registry.register_tool(test_tool)
        print(f"✅ Tool registration: {success}")
        
        # Test tool retrieval
        tool = registry.get_tool("test_tool")
        print(f"✅ Tool retrieval: {tool.name if tool else 'Failed'}")
        
        # Test tool search
        search_results = registry.search_tools("test")
        print(f"✅ Tool search: {len(search_results)} results")
        
        # Test statistics
        stats = registry.get_registry_statistics()
        print(f"✅ Registry statistics: {stats['total_tools']} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool Registry test failed: {e}")
        return False

async def test_framework_integration():
    """Test Framework MCP Integration following official specification."""
    print("\n🧪 Testing Framework MCP Integration...")
    
    try:
        # Test integration creation
        integration = get_framework_mcp_integration()
        print(f"✅ Framework Integration created")
        
        # Test initialization
        success = await integration.initialize()
        print(f"✅ Framework Integration initialization: {success}")
        
        # Test framework tools
        tools = integration.get_framework_tools()
        print(f"✅ Framework tools: {len(tools)} tools")
        
        # Test integration status
        status = integration.get_integration_status()
        print(f"✅ Integration status: {status['enabled']}")
        
        # Test framework tool execution
        if integration.integration_enabled:
            context = await integration.mcp_client.create_context(
                user_id="test_user",
                agent_id="framework_test",
                project_id="test_project"
            )
            
            response = await integration.call_framework_tool("code_analysis", {
                "code": "def test(): pass",
                "language": "python",
                "analysis_type": "quality"
            }, context)
            
            print(f"✅ Framework tool execution: {response.success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework Integration test failed: {e}")
        return False

async def test_agent_integration():
    """Test Agent MCP Integration."""
    print("\n🧪 Testing Agent MCP Integration...")
    
    try:
        # Test FrontendDeveloper agent MCP integration
        from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
        
        agent = FrontendDeveloperAgent()
        print(f"✅ FrontendDeveloper agent created")
        
        # Test MCP initialization
        mcp_success = await agent.initialize_mcp()
        print(f"✅ Agent MCP initialization: {mcp_success}")
        
        if mcp_success:
            # Test MCP tool usage
            result = await agent.use_mcp_tool("code_analysis", {
                "code": "const Button = () => <button>Click me</button>",
                "language": "typescript",
                "analysis_type": "quality"
            })
            print(f"✅ Agent MCP tool usage: {result is not None}")
            
            # Test enhanced component building
            component_result = await agent.build_shadcn_component("TestButton")
            print(f"✅ Enhanced component building: {'code_quality' in component_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Integration test failed: {e}")
        return False

async def test_mcp_workflow():
    """Test complete MCP workflow following official specification."""
    print("\n🧪 Testing Complete MCP Workflow...")
    
    try:
        # Initialize all components
        client = get_mcp_client()
        await client.connect()
        
        registry = get_mcp_tool_registry()
        
        integration = get_framework_mcp_integration()
        await integration.initialize(client)
        
        # Create context
        context = await client.create_context(
            user_id="workflow_test",
            agent_id="test_agent",
            project_id="workflow_project"
        )
        
        # Test complete workflow
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
        print(f"❌ MCP Workflow test failed: {e}")
        return False

async def test_mcp_specification_compliance():
    """Test MCP specification compliance."""
    print("\n🧪 Testing MCP Specification Compliance...")
    
    try:
        client = get_mcp_client()
        
        # Test version compliance
        print(f"✅ MCP Version: {client.version}")
        
        # Test server info
        await client.connect()
        if client.server_info:
            print(f"✅ Server Info: {client.server_info.name} v{client.server_info.version}")
            print(f"✅ Supported Versions: {client.server_info.supported_versions}")
            print(f"✅ Capabilities: {client.server_info.capabilities}")
        
        # Test message types
        from bmad.core.mcp import MCPMessageType
        print(f"✅ Message Types: {[msg.value for msg in MCPMessageType]}")
        
        # Test tool categories
        from bmad.core.mcp import ToolCategory
        print(f"✅ Tool Categories: {[cat.value for cat in ToolCategory]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Specification Compliance test failed: {e}")
        return False

async def main():
    """Run all MCP Phase 2 tests."""
    print("🚀 Starting MCP Phase 2: Agent Enhancement Tests")
    print("=" * 60)
    
    tests = [
        ("MCP Core Components", test_mcp_core_components),
        ("Tool Registry", test_tool_registry),
        ("Framework Integration", test_framework_integration),
        ("Agent Integration", test_agent_integration),
        ("MCP Workflow", test_mcp_workflow),
        ("Specification Compliance", test_mcp_specification_compliance)
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
    print("📊 MCP Phase 2 Test Results")
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
        print("🎉 All MCP Phase 2 tests passed! Implementation is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 