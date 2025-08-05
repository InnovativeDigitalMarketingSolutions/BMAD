#!/usr/bin/env python3
"""
Test script voor AI Framework Templates
Valideert de implementatie van framework templates voor AI Agents.
"""

import os
from pathlib import Path

def test_ai_framework_templates():
    """Test de implementatie van AI framework templates."""
    print("🤖 Testing AI Framework Templates Implementation")
    print("=" * 60)
    
    # Define template paths
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    if not frameworks_path.exists():
        print(f"❌ Frameworks path not found: {frameworks_path}")
        return False
    
    print(f"✅ Frameworks path found: {frameworks_path}")
    
    # Test AI-specific templates
    ai_templates = [
        "data_engineer_template.md",
        "rnd_template.md"
    ]
    
    print(f"\n🔧 Testing AI Templates:")
    for template_file in ai_templates:
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
    for template_file in ai_templates:
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
    
    print(f"\n🎉 All AI Framework Templates Tests Passed!")
    return True

def test_template_content_quality():
    """Test de kwaliteit van template content."""
    print(f"\n📊 Testing Template Content Quality")
    print("=" * 40)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    quality_metrics = {}
    
    for template_file in ["data_engineer_template.md", "rnd_template.md"]:
        template_path = frameworks_path / template_file
        content = template_path.read_text(encoding='utf-8')
        
        metrics = {
            "total_length": len(content),
            "code_blocks": content.count("```"),
            "sections": content.count("##"),
            "examples": content.count("Example"),
            "best_practices": content.count("Best Practice"),
            "data": content.count("Data"),
            "technology": content.count("Technology"),
            "innovation": content.count("Innovation"),
            "research": content.count("Research")
        }
        
        quality_metrics[template_file] = metrics
        
        print(f"\n📋 {template_file}:")
        print(f"  • Total length: {metrics['total_length']} characters")
        print(f"  • Code blocks: {metrics['code_blocks']}")
        print(f"  • Sections: {metrics['sections']}")
        print(f"  • Examples: {metrics['examples']}")
        print(f"  • Best practices: {metrics['best_practices']}")
        print(f"  • Data mentions: {metrics['data']}")
        print(f"  • Technology mentions: {metrics['technology']}")
        print(f"  • Innovation mentions: {metrics['innovation']}")
        print(f"  • Research mentions: {metrics['research']}")
    
    # Quality assessment
    print(f"\n📈 Quality Assessment:")
    for template_file, metrics in quality_metrics.items():
        score = 0
        if metrics["total_length"] > 15000: score += 1  # Higher threshold for AI templates
        if metrics["code_blocks"] > 25: score += 1
        if metrics["sections"] > 15: score += 1
        if metrics["examples"] > 5: score += 1
        if metrics["best_practices"] > 8: score += 1
        if metrics["data"] > 10: score += 1
        if metrics["technology"] > 15: score += 1
        if metrics["innovation"] > 5: score += 1
        if metrics["research"] > 5: score += 1
        
        quality_level = "High" if score >= 7 else "Medium" if score >= 5 else "Low"
        print(f"  • {template_file}: {quality_level} quality ({score}/9 criteria met)")
    
    return True

def test_ai_specific_content():
    """Test AI-specifieke content validatie."""
    print(f"\n🔬 Testing AI-Specific Content Validation")
    print("=" * 50)
    
    frameworks_path = Path("bmad/resources/templates/frameworks")
    
    # Test Data Engineer template
    data_engineer_path = frameworks_path / "data_engineer_template.md"
    if data_engineer_path.exists():
        content = data_engineer_path.read_text(encoding='utf-8')
        
        data_engineering_keywords = [
            "Data Pipeline",
            "ETL/ELT",
            "Data Quality",
            "Data Validation",
            "Data Processing",
            "Data Storage",
            "Data Monitoring",
            "Data Analytics",
            "Data Governance",
            "Data Lineage"
        ]
        
        found_keywords = []
        for keyword in data_engineering_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 Data Engineer Template Keywords Found: {len(found_keywords)}/{len(data_engineering_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ Data Engineer template has comprehensive data engineering content")
        else:
            print(f"  ❌ Data Engineer template missing key data engineering concepts")
            return False
    
    # Test RnD template
    rnd_path = frameworks_path / "rnd_template.md"
    if rnd_path.exists():
        content = rnd_path.read_text(encoding='utf-8')
        
        rnd_keywords = [
            "Technology Research",
            "Proof of Concept",
            "Innovation",
            "Technology Evaluation",
            "Research Workflow",
            "Technology Assessment",
            "Innovation Pipeline",
            "Knowledge Management",
            "Technology Trends",
            "Innovation Analytics"
        ]
        
        found_keywords = []
        for keyword in rnd_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"📋 RnD Template Keywords Found: {len(found_keywords)}/{len(rnd_keywords)}")
        for keyword in found_keywords:
            print(f"  ✅ {keyword}")
        
        if len(found_keywords) >= 8:  # At least 80% of keywords
            print(f"  ✅ RnD template has comprehensive research and development content")
        else:
            print(f"  ❌ RnD template missing key research and development concepts")
            return False
    
    return True

def main():
    """Main test function."""
    print("🚀 AI Framework Templates Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_ai_framework_templates()
    test2_passed = test_template_content_quality()
    test3_passed = test_ai_specific_content()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    print(f"  • Framework Templates: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Content Quality: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  • AI-Specific Content: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print(f"\n🎉 All tests passed! AI framework templates are ready for use.")
        return True
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 