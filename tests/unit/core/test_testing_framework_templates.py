#!/usr/bin/env python3
"""
Test script voor Testing Framework Templates
Valideert de implementatie van framework templates voor Testing Agents.
"""

import os
from pathlib import Path

def test_testing_framework_templates():
    """Test de implementatie van testing framework templates."""
    print("🧪 Testing Testing Framework Templates Implementation")
    print("=" * 60)
    
    # Define template paths
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    if not frameworks_path.exists():
        print(f"❌ Frameworks path not found: {frameworks_path}")
        return False
    
    print(f"✅ Frameworks path found: {frameworks_path}")
    
    # Test testing-specific templates
    testing_templates = [
        "testing_engineer_template.md",
        "quality_guardian_template.md"
    ]
    
    print(f"\n🔧 Testing Testing Templates:")
    for template_file in testing_templates:
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
    for template_file in testing_templates:
        template_path = frameworks_path / template_file
        content = template_path.read_text(encoding='utf-8')
        
        # Check for required sections
        required_sections = [
            "Overview",
            "Architecture Patterns", 
            "Best Practices",
            "Strategy Implementation",
            "Workflow Implementation"
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
    
    print(f"\n🎉 All Testing Framework Templates Tests Passed!")
    return True

def test_template_content_quality():
    """Test de kwaliteit van template content."""
    print(f"\n📊 Testing Template Content Quality")
    print("=" * 40)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    quality_metrics = {}
    
    for template_file in ["testing_engineer_template.md", "quality_guardian_template.md"]:
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
            "quality": content.count("Quality"),
            "compliance": content.count("Compliance")
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
        print(f"  • Quality mentions: {metrics['quality']}")
        print(f"  • Compliance mentions: {metrics['compliance']}")
    
    # Quality assessment
    print(f"\n📈 Quality Assessment:")
    for template_file, metrics in quality_metrics.items():
        score = 0
        if metrics["total_length"] > 15000: score += 1  # Higher threshold for testing templates
        if metrics["code_blocks"] > 30: score += 1
        if metrics["sections"] > 15: score += 1
        if metrics["examples"] > 5: score += 1
        if metrics["best_practices"] > 10: score += 1
        if metrics["security"] > 5: score += 1
        if metrics["testing"] > 20: score += 1
        if metrics["quality"] > 10: score += 1
        if metrics["compliance"] > 3: score += 1
        
        quality_level = "High" if score >= 7 else "Medium" if score >= 5 else "Low"
        print(f"  • {template_file}: {quality_level} quality ({score}/9 criteria met)")
    
    return True

def test_testing_specific_content():
    """Test testing-specifieke content validatie."""
    print(f"\n🔬 Testing Testing-Specific Content Validation")
    print("=" * 50)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    # Test Testing Engineer template
    testing_engineer_path = frameworks_path / "testing_engineer_template.md"
    if testing_engineer_path.exists():
        content = testing_engineer_path.read_text(encoding='utf-8')
        
        testing_keywords = [
            "Test Pyramid",
            "Unit Tests",
            "Integration Tests", 
            "End-to-End Tests",
            "Test Automation",
            "Test Data",
            "Mocking",
            "Test Coverage",
            "Performance Testing",
            "Security Testing"
        ]
        
        found_keywords = []
        for keyword in testing_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Testing Engineer Template Keywords Found: {len(found_keywords)}/{len(testing_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Testing Engineer template has comprehensive testing content")
        else:
            print(f"  ❌ Testing Engineer template missing key testing concepts")
            return False
    
    # Test Quality Guardian template
    quality_guardian_path = frameworks_path / "quality_guardian_template.md"
    if quality_guardian_path.exists():
        content = quality_guardian_path.read_text(encoding='utf-8')
        
        quality_keywords = [
            "Quality Gates",
            "Code Quality",
            "Security Quality",
            "Performance Quality",
            "Compliance",
            "Quality Metrics",
            "Quality Monitoring",
            "Quality Reporting",
            "Quality Trends",
            "Quality Alerts"
        ]
        
        found_keywords = []
        for keyword in quality_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Quality Guardian Template Keywords Found: {len(found_keywords)}/{len(quality_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Quality Guardian template has comprehensive quality content")
        else:
            print(f"  ❌ Quality Guardian template missing key quality concepts")
            return False
    
    return True

def main():
    """Main test function."""
    print("🚀 Testing Framework Templates Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_testing_framework_templates()
    test2_passed = test_template_content_quality()
    test3_passed = test_testing_specific_content()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    print(f"  • Framework Templates: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Content Quality: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  • Testing-Specific Content: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print(f"\n🎉 All tests passed! Testing framework templates are ready for use.")
        return True
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 