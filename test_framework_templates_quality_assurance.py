#!/usr/bin/env python3
"""
Test script for Framework Templates Quality Assurance Implementation
Tests the new quality assurance functionality in FeedbackAgent and QualityGuardian
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_feedback_agent_template_quality():
    """Test FeedbackAgent template quality assurance functionality"""
    print("🧪 Testing FeedbackAgent Template Quality Assurance...")
    
    try:
        from bmad.agents.Agent.FeedbackAgent.feedbackagent import FeedbackAgent
        
        agent = FeedbackAgent()
        
        # Test 1: Collect template feedback
        print("\n1. Testing template feedback collection...")
        result = agent.collect_template_feedback(
            "backend_development",
            "Excellent template with comprehensive guidelines and clear examples",
            "quality",
            5
        )
        assert result["success"] == True, f"Feedback collection failed: {result}"
        print(f"✅ Template feedback collected: {result['message']}")
        
        # Test 2: Analyze template trends
        print("\n2. Testing template trends analysis...")
        result = agent.analyze_template_trends("backend_development", "30 days")
        assert result["success"] == True, f"Trend analysis failed: {result}"
        print(f"✅ Template trends analyzed: {result['timeframe']}")
        
        # Test 3: Suggest template improvements
        print("\n3. Testing template improvement suggestions...")
        result = agent.suggest_template_improvements("backend_development")
        assert result["success"] == True, f"Improvement suggestions failed: {result}"
        print(f"✅ Template improvements suggested: {result['total_feedback']} feedback items")
        
        # Test 4: Get template quality report
        print("\n4. Testing template quality report...")
        result = agent.get_template_quality_report("backend_development")
        assert result["success"] == True, f"Quality report failed: {result}"
        print(f"✅ Template quality report generated: {result['quality_score']}/100")
        
        print("\n🎉 All FeedbackAgent template quality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FeedbackAgent test failed: {e}")
        return False

def test_quality_guardian_template_validation():
    """Test QualityGuardian template validation functionality"""
    print("\n🧪 Testing QualityGuardian Template Validation...")
    
    try:
        from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent
        
        agent = QualityGuardianAgent()
        
        # Test 1: Validate framework template
        print("\n1. Testing template validation...")
        result = agent.validate_framework_template("backend_development")
        assert result["success"] == True, f"Template validation failed: {result}"
        print(f"✅ Template validation completed: {result['validation']['overall_score']}/100")
        print(f"   Status: {result['validation']['status']}")
        
        # Test 2: Monitor template quality
        print("\n2. Testing template quality monitoring...")
        result = agent.monitor_template_quality(["backend_development", "frontend_development"])
        assert result["success"] == True, f"Template monitoring failed: {result}"
        avg_score = result["monitoring"]["overall_metrics"]["average_score"]
        print(f"✅ Template quality monitoring completed: {avg_score}/100")
        
        # Test 3: Enforce template standards
        print("\n3. Testing template standards enforcement...")
        result = agent.enforce_template_standards("backend_development")
        assert result["success"] == True, f"Standards enforcement failed: {result}"
        compliance = result["enforcement"]["compliance_score"]
        print(f"✅ Template standards enforcement completed: {compliance}/100")
        print(f"   Status: {result['enforcement']['status']}")
        
        # Test 4: Generate template quality report
        print("\n4. Testing template quality report generation...")
        result = agent.generate_template_quality_report("backend_development", "md")
        assert result["success"] == True, f"Quality report generation failed: {result}"
        print(f"✅ Template quality report generated in {result['format']} format")
        
        print("\n🎉 All QualityGuardian template validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ QualityGuardian test failed: {e}")
        return False

def test_integration():
    """Test integration between FeedbackAgent and QualityGuardian"""
    print("\n🧪 Testing Integration Between Agents...")
    
    try:
        from bmad.agents.Agent.FeedbackAgent.feedbackagent import FeedbackAgent
        from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent
        
        feedback_agent = FeedbackAgent()
        quality_agent = QualityGuardianAgent()
        
        # Test 1: Collect feedback and validate template
        print("\n1. Testing feedback collection and validation integration...")
        
        # Collect feedback
        feedback_result = feedback_agent.collect_template_feedback(
            "frontend_development",
            "Good template but could use more examples",
            "usability",
            4
        )
        assert feedback_result["success"] == True, "Feedback collection failed"
        
        # Validate template
        validation_result = quality_agent.validate_framework_template("frontend_development")
        assert validation_result["success"] == True, "Template validation failed"
        
        print(f"✅ Integration test passed: Feedback collected and template validated")
        print(f"   Feedback rating: {feedback_result['rating']}/5")
        print(f"   Template score: {validation_result['validation']['overall_score']}/100")
        
        # Test 2: Generate comprehensive quality report
        print("\n2. Testing comprehensive quality report generation...")
        
        quality_report = quality_agent.generate_template_quality_report(None, "md")
        feedback_report = feedback_agent.get_template_quality_report()
        
        assert quality_report["success"] == True, "Quality report generation failed"
        assert feedback_report["success"] == True, "Feedback report generation failed"
        
        print(f"✅ Comprehensive reports generated:")
        print(f"   Quality report: {quality_report['report']['templates_analyzed']} templates")
        print(f"   Feedback report: {feedback_report['total_templates']} templates")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI commands for both agents"""
    print("\n🧪 Testing CLI Commands...")
    
    try:
        import subprocess
        
        # Test FeedbackAgent CLI commands
        print("\n1. Testing FeedbackAgent CLI commands...")
        
        # Test help command
        result = subprocess.run([
            "python3", "bmad/agents/Agent/FeedbackAgent/feedbackagent.py", "help"
        ], capture_output=True, text=True)
        assert result.returncode == 0, "FeedbackAgent help command failed"
        print("✅ FeedbackAgent help command works")
        
        # Test template feedback collection command
        result = subprocess.run([
            "python3", "bmad/agents/Agent/FeedbackAgent/feedbackagent.py", 
            "collect-template-feedback",
            "--template-name", "backend_development",
            "--template-feedback", "Test feedback for CLI",
            "--feedback-type", "general",
            "--rating", "5"
        ], capture_output=True, text=True)
        assert result.returncode == 0, "FeedbackAgent template feedback command failed"
        print("✅ FeedbackAgent template feedback command works")
        
        # Test QualityGuardian CLI commands
        print("\n2. Testing QualityGuardian CLI commands...")
        
        # Test help command
        result = subprocess.run([
            "python3", "bmad/agents/Agent/QualityGuardian/qualityguardian.py", "help"
        ], capture_output=True, text=True)
        assert result.returncode == 0, "QualityGuardian help command failed"
        print("✅ QualityGuardian help command works")
        
        # Test template validation command
        result = subprocess.run([
            "python3", "bmad/agents/Agent/QualityGuardian/qualityguardian.py", 
            "validate-framework-template",
            "--template-name", "backend_development"
        ], capture_output=True, text=True)
        assert result.returncode == 0, "QualityGuardian template validation command failed"
        print("✅ QualityGuardian template validation command works")
        
        print("\n🎉 All CLI command tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI command test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Framework Templates Quality Assurance Test Suite")
    print("=" * 60)
    
    tests = [
        ("FeedbackAgent Template Quality", test_feedback_agent_template_quality),
        ("QualityGuardian Template Validation", test_quality_guardian_template_validation),
        ("Agent Integration", test_integration),
        ("CLI Commands", test_cli_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Framework Templates Quality Assurance is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 