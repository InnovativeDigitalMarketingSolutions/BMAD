#!/usr/bin/env python3
"""
Test script voor Management Framework Templates
Valideert de implementatie van framework templates voor Management Agents.
"""

import os
from pathlib import Path

def test_management_framework_templates():
    """Test de implementatie van management framework templates."""
    print("📋 Testing Management Framework Templates Implementation")
    print("=" * 60)
    
    # Define template paths
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    if not frameworks_path.exists():
        print(f"❌ Frameworks path not found: {frameworks_path}")
        return False
    
    print(f"✅ Frameworks path found: {frameworks_path}")
    
    # Test management-specific templates
    management_templates = [
        "product_owner_template.md",
        "scrummaster_template.md",
        "release_manager_template.md"
    ]
    
    print(f"\n🔧 Testing Management Templates:")
    for template_file in management_templates:
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
    for template_file in management_templates:
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
    
    print(f"\n🎉 All Management Framework Templates Tests Passed!")
    return True

def test_template_content_quality():
    """Test de kwaliteit van template content."""
    print(f"\n📊 Testing Template Content Quality")
    print("=" * 40)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    quality_metrics = {}
    
    for template_file in ["product_owner_template.md", "scrummaster_template.md", "release_manager_template.md"]:
        template_path = frameworks_path / template_file
        content = template_path.read_text(encoding='utf-8')
        
        metrics = {
            "total_length": len(content),
            "code_blocks": content.count("```"),
            "sections": content.count("##"),
            "examples": content.count("Example"),
            "best_practices": content.count("Best Practice"),
            "management": content.count("Management"),
            "process": content.count("Process"),
            "workflow": content.count("Workflow"),
            "coordination": content.count("Coordination")
        }
        
        quality_metrics[template_file] = metrics
        
        print(f"\n📋 {template_file}:")
        print(f"  • Total length: {metrics['total_length']} characters")
        print(f"  • Code blocks: {metrics['code_blocks']}")
        print(f"  • Sections: {metrics['sections']}")
        print(f"  • Examples: {metrics['examples']}")
        print(f"  • Best practices: {metrics['best_practices']}")
        print(f"  • Management mentions: {metrics['management']}")
        print(f"  • Process mentions: {metrics['process']}")
        print(f"  • Workflow mentions: {metrics['workflow']}")
        print(f"  • Coordination mentions: {metrics['coordination']}")
    
    # Quality assessment
    print(f"\n📈 Quality Assessment:")
    for template_file, metrics in quality_metrics.items():
        score = 0
        if metrics["total_length"] > 15000: score += 1  # Higher threshold for management templates
        if metrics["code_blocks"] > 20: score += 1
        if metrics["sections"] > 15: score += 1
        if metrics["examples"] > 5: score += 1
        if metrics["best_practices"] > 8: score += 1
        if metrics["management"] > 10: score += 1
        if metrics["process"] > 15: score += 1
        if metrics["workflow"] > 10: score += 1
        if metrics["coordination"] > 5: score += 1
        
        quality_level = "High" if score >= 7 else "Medium" if score >= 5 else "Low"
        print(f"  • {template_file}: {quality_level} quality ({score}/9 criteria met)")
    
    return True

def test_management_specific_content():
    """Test management-specifieke content validatie."""
    print(f"\n🔬 Testing Management-Specific Content Validation")
    print("=" * 50)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    # Test Product Owner template
    product_owner_path = frameworks_path / "product_owner_template.md"
    if product_owner_path.exists():
        content = product_owner_path.read_text(encoding='utf-8')
        
        product_management_keywords = [
            "Product Management",
            "Backlog Management",
            "User Story",
            "Sprint Planning",
            "Stakeholder Management",
            "Product Strategy",
            "Release Planning",
            "Acceptance Criteria",
            "Product Roadmap",
            "Value Proposition"
        ]
        
        found_keywords = []
        for keyword in product_management_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Product Owner Template Keywords Found: {len(found_keywords)}/{len(product_management_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Product Owner template has comprehensive product management content")
        else:
            print(f"  ❌ Product Owner template missing key product management concepts")
            return False
    
    # Test Scrum Master template
    scrummaster_path = frameworks_path / "scrummaster_template.md"
    if scrummaster_path.exists():
        content = scrummaster_path.read_text(encoding='utf-8')
        
        scrum_keywords = [
            "Scrum Process",
            "Sprint Management",
            "Team Facilitation",
            "Daily Scrum",
            "Sprint Retrospective",
            "Process Monitoring",
            "Team Coaching",
            "Conflict Resolution",
            "Quality Gates",
            "Stakeholder Management"
        ]
        
        found_keywords = []
        for keyword in scrum_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Scrum Master Template Keywords Found: {len(found_keywords)}/{len(scrum_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Scrum Master template has comprehensive scrum process content")
        else:
            print(f"  ❌ Scrum Master template missing key scrum process concepts")
            return False
    
    # Test Release Manager template
    release_manager_path = frameworks_path / "release_manager_template.md"
    if release_manager_path.exists():
        content = release_manager_path.read_text(encoding='utf-8')
        
        release_management_keywords = [
            "Release Planning",
            "Deployment Management",
            "Changelog Management",
            "Release Coordination",
            "Environment Management",
            "Rollback Procedures",
            "Release Documentation",
            "Quality Gates",
            "Release Analytics",
            "Post-Release Analysis"
        ]
        
        found_keywords = []
        for keyword in release_management_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Release Manager Template Keywords Found: {len(found_keywords)}/{len(release_management_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Release Manager template has comprehensive release management content")
        else:
            print(f"  ❌ Release Manager template missing key release management concepts")
            return False
    
    return True

def main():
    """Main test function."""
    print("🚀 Management Framework Templates Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_management_framework_templates()
    test2_passed = test_template_content_quality()
    test3_passed = test_management_specific_content()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    print(f"  • Framework Templates: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Content Quality: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  • Management-Specific Content: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print(f"\n🎉 All tests passed! Management framework templates are ready for use.")
        return True
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 