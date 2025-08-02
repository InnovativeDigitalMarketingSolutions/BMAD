#!/usr/bin/env python3
"""
Test script voor framework templates integratie
"""

import sys
import os
from pathlib import Path

# Add BMAD to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_framework_templates():
    """Test framework templates functionality."""
    print("🧪 Testing Framework Templates Integration")
    print("=" * 50)
    
    try:
        # Test framework templates manager
        from bmad.agents.core.utils.framework_templates import (
            get_framework_templates_manager,
            get_framework_guidelines,
            get_quality_gates,
            get_pyramid_strategies,
            get_mocking_strategy,
            get_workflow_commands,
            get_linting_config
        )
        
        print("✅ Framework templates module imported successfully")
        
        # Test manager
        manager = get_framework_templates_manager()
        print("✅ Framework templates manager created successfully")
        
        # Test available templates
        available_templates = manager.list_available_templates()
        print(f"✅ Available templates: {available_templates}")
        
        # Test template content
        for template_name in available_templates:
            content = manager.get_framework_template(template_name)
            if content:
                print(f"✅ Template '{template_name}' loaded successfully ({len(content)} characters)")
            else:
                print(f"❌ Template '{template_name}' failed to load")
        
        # Test guidelines
        ai_guidelines = get_framework_guidelines("ai_agents")
        print(f"✅ AI agent guidelines loaded: {len(ai_guidelines)} categories")
        
        # Test quality gates
        quality_gates = get_quality_gates()
        print(f"✅ Quality gates loaded: {len(quality_gates)} categories")
        
        # Test pyramid strategies
        pyramid_strategies = get_pyramid_strategies()
        print(f"✅ Pyramid strategies loaded: {len(pyramid_strategies)} categories")
        
        # Test mocking strategy
        mocking_strategy = get_mocking_strategy()
        print(f"✅ Mocking strategy loaded ({len(mocking_strategy)} characters)")
        
        # Test workflow commands
        workflow_commands = get_workflow_commands()
        print(f"✅ Workflow commands loaded: {len(workflow_commands)} categories")
        
        # Test linting config
        linting_config = get_linting_config()
        print(f"✅ Linting config loaded ({len(linting_config)} characters)")
        
        print("\n🎉 All framework templates tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_ai_developer_integration():
    """Test AI Developer agent integration with framework templates."""
    print("\n🤖 Testing AI Developer Agent Integration")
    print("=" * 50)
    
    try:
        from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent
        
        print("✅ AiDeveloperAgent imported successfully")
        
        # Create agent instance
        agent = AiDeveloperAgent()
        print("✅ AiDeveloperAgent instance created successfully")
        
        # Test framework manager
        if hasattr(agent, 'framework_manager'):
            print("✅ Framework manager available in agent")
        else:
            print("❌ Framework manager not available in agent")
            return False
        
        # Test framework guidelines
        if hasattr(agent, 'framework_guidelines'):
            print("✅ Framework guidelines available in agent")
        else:
            print("❌ Framework guidelines not available in agent")
            return False
        
        # Test quality gates
        if hasattr(agent, 'quality_gates'):
            print("✅ Quality gates available in agent")
        else:
            print("❌ Quality gates not available in agent")
            return False
        
        # Test pyramid strategies
        if hasattr(agent, 'pyramid_strategies'):
            print("✅ Pyramid strategies available in agent")
        else:
            print("❌ Pyramid strategies not available in agent")
            return False
        
        # Test mocking strategy
        if hasattr(agent, 'mocking_strategy'):
            print("✅ Mocking strategy available in agent")
        else:
            print("❌ Mocking strategy not available in agent")
            return False
        
        # Test workflow commands
        if hasattr(agent, 'workflow_commands'):
            print("✅ Workflow commands available in agent")
        else:
            print("❌ Workflow commands not available in agent")
            return False
        
        # Test linting config
        if hasattr(agent, 'linting_config'):
            print("✅ Linting config available in agent")
        else:
            print("❌ Linting config not available in agent")
            return False
        
        print("\n🎉 All AI Developer agent integration tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_framework_template_commands():
    """Test framework template commands."""
    print("\n⚡ Testing Framework Template Commands")
    print("=" * 50)
    
    try:
        from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent
        
        agent = AiDeveloperAgent()
        
        # Test framework overview
        print("Testing show_framework_overview...")
        agent.show_framework_overview()
        print("✅ Framework overview displayed")
        
        # Test framework guidelines
        print("\nTesting show_framework_guidelines...")
        agent.show_framework_guidelines()
        print("✅ Framework guidelines displayed")
        
        # Test quality gates
        print("\nTesting show_quality_gates...")
        agent.show_quality_gates()
        print("✅ Quality gates displayed")
        
        # Test pyramid strategies
        print("\nTesting show_pyramid_strategies...")
        agent.show_pyramid_strategies()
        print("✅ Pyramid strategies displayed")
        
        # Test mocking strategy
        print("\nTesting show_mocking_strategy...")
        agent.show_mocking_strategy()
        print("✅ Mocking strategy displayed")
        
        # Test workflow commands
        print("\nTesting show_workflow_commands...")
        agent.show_workflow_commands()
        print("✅ Workflow commands displayed")
        
        # Test linting config
        print("\nTesting show_linting_config...")
        agent.show_linting_config()
        print("✅ Linting config displayed")
        
        # Test specific template
        print("\nTesting show_framework_template...")
        agent.show_framework_template("development_strategy")
        print("✅ Development strategy template displayed")
        
        print("\n🎉 All framework template commands tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 Framework Templates Integration Test")
    print("=" * 60)
    
    # Test framework templates
    if not test_framework_templates():
        print("\n❌ Framework templates test failed")
        return False
    
    # Test AI developer integration
    if not test_ai_developer_integration():
        print("\n❌ AI Developer integration test failed")
        return False
    
    # Test framework template commands
    if not test_framework_template_commands():
        print("\n❌ Framework template commands test failed")
        return False
    
    print("\n🎉 All tests passed! Framework templates are ready for use.")
    print("\n📋 Usage Examples:")
    print("  python bmad/agents/Agent/AiDeveloper/aidev.py show-framework-overview")
    print("  python bmad/agents/Agent/AiDeveloper/aidev.py show-framework-guidelines")
    print("  python bmad/agents/Agent/AiDeveloper/aidev.py show-framework-template --template development_strategy")
    print("  python bmad/agents/Agent/AiDeveloper/aidev.py show-mocking-strategy")
    print("  python bmad/agents/Agent/AiDeveloper/aidev.py show-workflow-commands")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 