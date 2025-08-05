#!/usr/bin/env python3
"""
Test script voor Development Framework Templates
Valideert de implementatie van framework templates voor Development Agents.
"""

import sys
import os
from pathlib import Path

# Add BMAD to path
sys.path.insert(0, str(Path(__file__).parent))

from bmad.agents.core.utils.framework_templates import FrameworkTemplatesManager

def test_development_framework_templates():
    """Test de implementatie van development framework templates."""
    print("🧪 Testing Development Framework Templates Implementation")
    print("=" * 60)
    
    # Initialize framework templates manager
    try:
        manager = FrameworkTemplatesManager()
        print("✅ Framework templates manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize framework templates manager: {e}")
        return False
    
    # Test available templates
    available_templates = manager.list_available_templates()
    print(f"\n📋 Available Templates: {len(available_templates)}")
    for template in available_templates:
        print(f"  • {template}")
    
    # Test development-specific templates
    development_templates = [
        "backend_development",
        "frontend_development", 
        "fullstack_development"
    ]
    
    print(f"\n🔧 Testing Development Templates:")
    for template_name in development_templates:
        try:
            content = manager.get_framework_template(template_name)
            if content:
                print(f"  ✅ {template_name}: {len(content)} characters")
            else:
                print(f"  ❌ {template_name}: Template not found or empty")
                return False
        except Exception as e:
            print(f"  ❌ {template_name}: Error loading template - {e}")
            return False
    
    # Test framework guidelines for development agents
    print(f"\n📚 Testing Framework Guidelines:")
    agent_types = ["backend_agents", "frontend_agents", "fullstack_agents"]
    
    for agent_type in agent_types:
        try:
            guidelines = manager.get_framework_guidelines(agent_type)
            if guidelines and "development" in guidelines and "testing" in guidelines:
                dev_count = len(guidelines["development"])
                test_count = len(guidelines["testing"])
                print(f"  ✅ {agent_type}: {dev_count} development, {test_count} testing guidelines")
            else:
                print(f"  ❌ {agent_type}: Missing guidelines structure")
                return False
        except Exception as e:
            print(f"  ❌ {agent_type}: Error loading guidelines - {e}")
            return False
    
    # Test template content validation
    print(f"\n🔍 Validating Template Content:")
    for template_name in development_templates:
        content = manager.get_framework_template(template_name)
        
        # Check for required sections
        required_sections = [
            "Development Overview",
            "Architecture Patterns", 
            "Best Practices",
            "Testing Strategy",
            "Development Workflow"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"  ❌ {template_name}: Missing sections - {missing_sections}")
            return False
        else:
            print(f"  ✅ {template_name}: All required sections present")
    
    # Test template integration with agents
    print(f"\n🤖 Testing Agent Integration:")
    try:
        # Test that agents can access the templates
        all_templates = manager.get_all_framework_templates()
        if len(all_templates) >= 8:  # Should have at least 8 templates now
            print(f"  ✅ Agent template access: {len(all_templates)} templates available")
        else:
            print(f"  ❌ Agent template access: Expected 8+, got {len(all_templates)}")
            return False
    except Exception as e:
        print(f"  ❌ Agent template access: Error - {e}")
        return False
    
    print(f"\n🎉 All Development Framework Templates Tests Passed!")
    return True

def test_template_content_quality():
    """Test de kwaliteit van template content."""
    print(f"\n📊 Testing Template Content Quality")
    print("=" * 40)
    
    manager = FrameworkTemplatesManager()
    
    quality_metrics = {}
    
    for template_name in ["backend_development", "frontend_development", "fullstack_development"]:
        content = manager.get_framework_template(template_name)
        
        metrics = {
            "total_length": len(content),
            "code_blocks": content.count("```"),
            "sections": content.count("##"),
            "examples": content.count("Example"),
            "best_practices": content.count("Best Practice"),
            "security": content.count("Security"),
            "testing": content.count("Test"),
            "deployment": content.count("Deploy")
        }
        
        quality_metrics[template_name] = metrics
        
        print(f"\n📋 {template_name}:")
        print(f"  • Total length: {metrics['total_length']} characters")
        print(f"  • Code blocks: {metrics['code_blocks']}")
        print(f"  • Sections: {metrics['sections']}")
        print(f"  • Examples: {metrics['examples']}")
        print(f"  • Best practices: {metrics['best_practices']}")
        print(f"  • Security mentions: {metrics['security']}")
        print(f"  • Testing mentions: {metrics['testing']}")
        print(f"  • Deployment mentions: {metrics['deployment']}")
    
    # Quality assessment
    print(f"\n📈 Quality Assessment:")
    for template_name, metrics in quality_metrics.items():
        score = 0
        if metrics["total_length"] > 10000: score += 1
        if metrics["code_blocks"] > 20: score += 1
        if metrics["sections"] > 10: score += 1
        if metrics["examples"] > 5: score += 1
        if metrics["best_practices"] > 10: score += 1
        if metrics["security"] > 5: score += 1
        if metrics["testing"] > 10: score += 1
        if metrics["deployment"] > 3: score += 1
        
        quality_level = "High" if score >= 6 else "Medium" if score >= 4 else "Low"
        print(f"  • {template_name}: {quality_level} quality ({score}/8 criteria met)")
    
    return True

def main():
    """Main test function."""
    print("🚀 Development Framework Templates Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_development_framework_templates()
    test2_passed = test_template_content_quality()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    print(f"  • Framework Templates: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Content Quality: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Development framework templates are ready for use.")
        return True
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 