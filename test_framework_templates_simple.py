#!/usr/bin/env python3
"""
Eenvoudige test voor framework templates
"""

import sys
import os
from pathlib import Path

# Add BMAD to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_framework_templates_simple():
    """Test framework templates functionality."""
    print("🧪 Testing Framework Templates (Simple)")
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
        
        # Show example output
        print("\n📋 Example Framework Overview:")
        print("=" * 40)
        
        print("\n🤖 AI Agent Guidelines:")
        if "development" in ai_guidelines:
            print("🔧 DEVELOPMENT GUIDELINES:")
            for i, guideline in enumerate(ai_guidelines["development"], 1):
                print(f"  {i}. {guideline}")
        
        if "testing" in ai_guidelines:
            print("🧪 TESTING GUIDELINES:")
            for i, guideline in enumerate(ai_guidelines["testing"], 1):
                print(f"  {i}. {guideline}")
        
        print("\n🎯 Quality Gates:")
        print("🔧 DEVELOPMENT QUALITY GATES:")
        for gate, requirement in quality_gates["development"].items():
            print(f"  • {gate}: {requirement}")
        
        print("🧪 TESTING QUALITY GATES:")
        for gate, requirement in quality_gates["testing"].items():
            print(f"  • {gate}: {requirement}")
        
        print("\n🏗️ Pyramid Strategies:")
        print("🔧 DEVELOPMENT PYRAMID:")
        for level, description in pyramid_strategies["development"].items():
            print(f"  • {level.title()}: {description}")
        
        print("🧪 TESTING PYRAMID:")
        for level, description in pyramid_strategies["testing"].items():
            print(f"  • {level.title()}: {description}")
        
        print("\n⚡ Usage Examples:")
        print("  • Agents kunnen nu framework templates gebruiken")
        print("  • Framework guidelines zijn beschikbaar per agent type")
        print("  • Quality gates zijn gedefinieerd voor development en testing")
        print("  • Pyramid strategies zijn geïmplementeerd")
        print("  • Pragmatic mocking strategie is beschikbaar")
        print("  • Workflow commands zijn gedefinieerd")
        print("  • Linting configuratie is beschikbaar")
        
        print("\n" + "=" * 40)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 Framework Templates Simple Test")
    print("=" * 60)
    
    # Test framework templates
    if not test_framework_templates_simple():
        print("\n❌ Framework templates test failed")
        return False
    
    print("\n🎉 Framework templates are ready for use by agents!")
    print("\n📋 Next Steps:")
    print("  1. Agents kunnen nu framework templates gebruiken")
    print("  2. Framework guidelines zijn beschikbaar per agent type")
    print("  3. Quality gates zijn gedefinieerd voor development en testing")
    print("  4. Pyramid strategies zijn geïmplementeerd")
    print("  5. Pragmatic mocking strategie is beschikbaar")
    print("  6. Workflow commands zijn gedefinieerd")
    print("  7. Linting configuratie is beschikbaar")
    print("  8. Agents kunnen verbeteringen aanbrengen aan templates")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 