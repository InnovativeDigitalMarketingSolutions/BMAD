#!/usr/bin/env python3
"""
Simplified Agent MCP Integration Test
Testing agent MCP integration without external dependencies
"""

import asyncio
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration
)

class SimpleAgent:
    """Simple agent for testing MCP integration without external dependencies."""
    
    def __init__(self):
        self.agent_name = "SimpleAgent"
        self.mcp_client = None
        self.mcp_integration = None
        self.mcp_enabled = False
    
    async def initialize_mcp(self) -> bool:
        """Initialize MCP integration for SimpleAgent."""
        try:
            # Initialize MCP client
            self.mcp_client = get_mcp_client()
            await self.mcp_client.connect()
            
            # Initialize framework integration
            self.mcp_integration = get_framework_mcp_integration()
            await self.mcp_integration.initialize(self.mcp_client)
            
            self.mcp_enabled = True
            print("✅ MCP integration initialized successfully for SimpleAgent")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP for SimpleAgent: {e}")
            self.mcp_enabled = False
            return False
    
    async def use_mcp_tool(self, tool_name: str, parameters: dict) -> dict:
        """Use MCP tool for enhanced functionality."""
        if not self.mcp_enabled or not self.mcp_integration:
            print("⚠️ MCP integration not available")
            return None
        
        try:
            context = await self.mcp_client.create_context(
                user_id="simple_agent",
                agent_id=self.agent_name,
                project_id="test_project"
            )
            
            response = await self.mcp_integration.call_framework_tool(tool_name, parameters, context)
            
            if response.success:
                print(f"✅ MCP tool {tool_name} executed successfully")
                return response.data
            else:
                print(f"❌ MCP tool {tool_name} failed: {response.error}")
                return None
                
        except Exception as e:
            print(f"❌ Error using MCP tool {tool_name}: {e}")
            return None
    
    async def enhanced_operation(self, operation_name: str) -> dict:
        """Perform enhanced operation using MCP tools."""
        result = {
            "operation": operation_name,
            "agent": self.agent_name,
            "timestamp": "2025-01-27T17:30:00Z"
        }
        
        # Use MCP tools for enhanced functionality if available
        if self.mcp_enabled:
            # Code analysis
            code_analysis_result = await self.use_mcp_tool("code_analysis", {
                "code": f"// {operation_name} operation code",
                "language": "python",
                "analysis_type": "quality"
            })
            
            if code_analysis_result:
                result["code_quality"] = {
                    "score": code_analysis_result.get("score", 0),
                    "issues": code_analysis_result.get("issues", []),
                    "recommendations": code_analysis_result.get("recommendations", [])
                }
            
            # Test generation
            test_result = await self.use_mcp_tool("test_generation", {
                "code": f"def {operation_name}(): pass",
                "language": "python",
                "framework": "pytest",
                "test_type": "unit"
            })
            
            if test_result:
                result["tests"] = test_result.get("tests", [])
                result["test_coverage"] = test_result.get("coverage", 0)
        
        return result

@pytest.mark.asyncio
async def test_simple_agent_integration():
    """Test SimpleAgent MCP Integration."""
    print("🧪 Testing SimpleAgent MCP Integration...")
    
    try:
        # Create simple agent
        agent = SimpleAgent()
        print(f"✅ SimpleAgent created")
        
        # Test MCP initialization
        mcp_success = await agent.initialize_mcp()
        print(f"✅ Agent MCP initialization: {mcp_success}")
        
        if mcp_success:
            # Test MCP tool usage
            result = await agent.use_mcp_tool("code_analysis", {
                "code": "def test_function(): return 'hello world'",
                "language": "python",
                "analysis_type": "quality"
            })
            print(f"✅ Agent MCP tool usage: {result is not None}")
            
            # Test enhanced operation
            operation_result = await agent.enhanced_operation("test_operation")
            print(f"✅ Enhanced operation: {'code_quality' in operation_result}")
            
            return True
        else:
            print("⚠️ MCP initialization failed")
            return False
        
    except Exception as e:
        print(f"❌ SimpleAgent Integration test failed: {e}")
        return False

async def main():
    """Run simplified agent test."""
    print("🚀 Starting Simplified Agent MCP Integration Test")
    print("=" * 50)
    
    success = await test_simple_agent_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Simplified Agent MCP Integration test passed!")
        return True
    else:
        print("⚠️ Simplified Agent MCP Integration test failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 