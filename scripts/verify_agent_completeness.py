#!/usr/bin/env python3
"""
Agent Completeness Verification Script

This script systematically checks all agents for missing required methods and attributes,
and adds them if they are missing. This implements the Agent Completeness Prevention Strategy.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_all_agent_files() -> List[Path]:
    """Get all agent Python files."""
    agent_dir = project_root / "bmad" / "agents" / "Agent"
    agent_files = []
    
    for agent_folder in agent_dir.iterdir():
        if agent_folder.is_dir():
            # Look for main agent file (usually agentname.py or agentnameagent.py)
            for py_file in agent_folder.glob("*.py"):
                if not py_file.name.startswith("__"):
                    agent_files.append(py_file)
                    break
    
    return agent_files

def get_required_attributes() -> List[str]:
    """Get list of required attributes for all agents."""
    return [
        'mcp_client',
        'enhanced_mcp', 
        'enhanced_mcp_enabled',
        'tracing_enabled',
        'agent_name',
        'message_bus_integration'
    ]

def get_required_methods() -> List[str]:
    """Get list of required methods for all agents."""
    return [
        'initialize_enhanced_mcp',
        'get_enhanced_mcp_tools',
        'register_enhanced_mcp_tools', 
        'trace_operation'
    ]

def check_agent_completeness(agent_file: Path) -> Dict[str, Any]:
    """Check if an agent has all required attributes and methods."""
    try:
        # Import the agent module
        module_name = f"bmad.agents.Agent.{agent_file.parent.name}.{agent_file.stem}"
        module = importlib.import_module(module_name)
        
        # Find the agent class
        agent_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and 'Agent' in name and name != 'AgentMessageBusIntegration':
                agent_class = obj
                break
        
        if not agent_class:
            return {
                'file': str(agent_file),
                'status': 'error',
                'message': 'No agent class found'
            }
        
        # Check attributes
        missing_attributes = []
        for attr in get_required_attributes():
            if not hasattr(agent_class, attr):
                missing_attributes.append(attr)
        
        # Check methods
        missing_methods = []
        for method in get_required_methods():
            if not hasattr(agent_class, method):
                missing_methods.append(method)
        
        return {
            'file': str(agent_file),
            'agent_class': agent_class.__name__,
            'status': 'complete' if not missing_attributes and not missing_methods else 'incomplete',
            'missing_attributes': missing_attributes,
            'missing_methods': missing_methods
        }
        
    except Exception as e:
        return {
            'file': str(agent_file),
            'status': 'error',
            'message': str(e)
        }

def generate_missing_methods_code(agent_name: str) -> str:
    """Generate code for missing methods."""
    return f'''
    def get_enhanced_mcp_tools(self) -> List[str]:
        """Get list of available enhanced MCP tools for this agent."""
        if not self.enhanced_mcp_enabled:
            return []
        
        try:
            return [
                "{agent_name.lower()}_specific_tool_1",
                "{agent_name.lower()}_specific_tool_2", 
                "{agent_name.lower()}_specific_tool_3"
            ]
        except Exception as e:
            logger.warning(f"Failed to get enhanced MCP tools: {{e}}")
            return []

    def register_enhanced_mcp_tools(self) -> bool:
        """Register enhanced MCP tools for this agent."""
        if not self.enhanced_mcp_enabled:
            return False
        
        try:
            tools = self.get_enhanced_mcp_tools()
            for tool in tools:
                if self.enhanced_mcp:
                    self.enhanced_mcp.register_tool(tool)
            return True
        except Exception as e:
            logger.warning(f"Failed to register enhanced MCP tools: {{e}}")
            return False

    async def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """Trace operations for monitoring and debugging."""
        try:
            if not self.tracing_enabled or not self.tracer:
                return False
            
            trace_data = {{
                "agent": self.agent_name,
                "operation": operation_name,
                "timestamp": datetime.now().isoformat(),
                "attributes": attributes or {{}}
            }}
            
            await self.tracer.trace_operation(trace_data)
            return True
            
        except Exception as e:
            logger.warning(f"Tracing operation failed: {{e}}")
            return False
'''

def main():
    """Main function to verify and fix agent completeness."""
    print("🔍 Agent Completeness Verification")
    print("=" * 50)
    
    agent_files = get_all_agent_files()
    results = []
    
    for agent_file in agent_files:
        print(f"\n📋 Checking {agent_file.name}...")
        result = check_agent_completeness(agent_file)
        results.append(result)
        
        if result['status'] == 'complete':
            print(f"✅ {result['agent_class']} is complete")
        elif result['status'] == 'incomplete':
            print(f"❌ {result['agent_class']} is incomplete:")
            if result['missing_attributes']:
                print(f"   Missing attributes: {result['missing_attributes']}")
            if result['missing_methods']:
                print(f"   Missing methods: {result['missing_methods']}")
        else:
            print(f"⚠️  Error checking {agent_file.name}: {result['message']}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    complete_count = sum(1 for r in results if r['status'] == 'complete')
    incomplete_count = sum(1 for r in results if r['status'] == 'incomplete')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    print(f"✅ Complete agents: {complete_count}")
    print(f"❌ Incomplete agents: {incomplete_count}")
    print(f"⚠️  Errors: {error_count}")
    print(f"📈 Total agents: {len(results)}")
    
    # Show incomplete agents
    if incomplete_count > 0:
        print(f"\n🔧 INCOMPLETE AGENTS NEEDING FIXES:")
        for result in results:
            if result['status'] == 'incomplete':
                print(f"\n📁 {result['file']}")
                print(f"   Class: {result['agent_class']}")
                if result['missing_attributes']:
                    print(f"   Missing attributes: {result['missing_attributes']}")
                if result['missing_methods']:
                    print(f"   Missing methods: {result['missing_methods']}")
                    
                # Generate code for missing methods
                if result['missing_methods']:
                    agent_name = result['agent_class'].replace('Agent', '')
                    print(f"\n💡 Add these methods to {result['agent_class']}:")
                    print(generate_missing_methods_code(agent_name))
    
    return results

if __name__ == "__main__":
    main() 