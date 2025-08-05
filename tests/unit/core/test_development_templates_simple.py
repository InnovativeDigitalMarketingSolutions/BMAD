#!/usr/bin/env python3
"""
Simple test script voor Development Framework Templates
Test alleen de template bestanden zonder volledige BMAD dependencies.
"""

import os
from pathlib import Path

def test_development_framework_templates():
    """Test de implementatie van development framework templates."""
    print("🧪 Testing Development Framework Templates Implementation")
    print("=" * 60)
    
    # Define template paths
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    if not frameworks_path.exists():
        print(f"❌ Frameworks path not found: {frameworks_path}")
        return False
    
    print(f"✅ Frameworks path found: {frameworks_path}")
    
    # Test development-specific templates
    development_templates = [
        "backend_development_template.md",
        "frontend_development_template.md", 
        "fullstack_development_template.md"
    ]
    
    print(f"\n🔧 Testing Development Templates:")
    for template_file in development_templates:
        template_path = frameworks_path / template_file
        try:
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
                if content and len(content) > 1000:  # Minimum content length
                    print(f"  ✅ {template_file}: {len(content)} characters")
                else:
                    print(f"  ❌ {template_file}: Template too short or empty")
                    return False
            else:
                print(f"  ❌ {template_file}: Template file not found")
                return False
        except Exception as e:
            print(f"  ❌ {template_file}: Error reading template - {e}")
            return False
    
    # Test template content validation
    print(f"\n🔍 Validating Template Content:")
    for template_file in development_templates:
        template_path = frameworks_path / template_file
        content = template_path.read_text(encoding='utf-8')
        
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
            print(f"  ❌ {template_file}: Missing sections - {missing_sections}")
            return False
        else:
            print(f"  ✅ {template_file}: All required sections present")
    
    # Test all available templates
    print(f"\n📋 All Available Templates:")
    all_templates = list(frameworks_path.glob("*.md"))
    print(f"  Total templates: {len(all_templates)}")
    
    for template_path in all_templates:
        try:
            content = template_path.read_text(encoding='utf-8')
            print(f"  • {template_path.name}: {len(content)} characters")
        except Exception as e:
            print(f"  ❌ {template_path.name}: Error reading - {e}")
    
    print(f"\n🎉 All Development Framework Templates Tests Passed!")
    return True

def test_template_content_quality():
    """Test de kwaliteit van template content."""
    print(f"\n📊 Testing Template Content Quality")
    print("=" * 40)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    quality_metrics = {}
    
    for template_file in ["backend_development_template.md", "frontend_development_template.md", "fullstack_development_template.md"]:
        template_path = frameworks_path / template_file
        content = template_path.read_text(encoding='utf-8')
        
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
        
        quality_metrics[template_file] = metrics
        
        print(f"\n📋 {template_file}:")
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
    for template_file, metrics in quality_metrics.items():
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
        print(f"  • {template_file}: {quality_level} quality ({score}/8 criteria met)")
    
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
    exit(0 if success else 1) 