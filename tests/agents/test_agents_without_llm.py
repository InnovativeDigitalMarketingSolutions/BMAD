#!/usr/bin/env python3
"""
Test Script voor Agents zonder LLM

Dit script test de agents voor template aanpassing zonder LLM functionaliteit.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_frontend_developer_agent():
    """Test FrontendDeveloper agent without LLM."""
    try:
        from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
        
        agent = FrontendDeveloperAgent()
        
        # Test basic functionality
        assert agent.agent_name == "FrontendDeveloper"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'build_component')
        
        print("✅ FrontendDeveloper agent test passed")
        return True
    except Exception as e:
        print(f"❌ FrontendDeveloper agent test failed: {e}")
        return False

def test_fullstack_developer_agent():
    """Test FullstackDeveloper agent without LLM."""
    try:
        from bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper import FullstackDeveloperAgent
        
        agent = FullstackDeveloperAgent()
        
        # Test basic functionality
        assert agent.agent_name == "FullstackDeveloper"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'build_component')
        
        print("✅ FullstackDeveloper agent test passed")
        return True
    except Exception as e:
        print(f"❌ FullstackDeveloper agent test failed: {e}")
        return False

def test_architect_agent():
    """Test Architect agent without LLM."""
    try:
        from bmad.agents.Agent.Architect.architect import ArchitectAgent
        
        agent = ArchitectAgent()
        
        # Test basic functionality
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'design_api')
        
        print("✅ Architect agent test passed")
        return True
    except Exception as e:
        print(f"❌ Architect agent test failed: {e}")
        return False

def test_ai_developer_agent():
    """Test AiDeveloper agent without LLM."""
    try:
        from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent
        
        agent = AiDeveloperAgent()
        
        # Test basic functionality
        assert agent.agent_name == "AiDeveloper"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'run_experiment')
        
        print("✅ AiDeveloper agent test passed")
        return True
    except Exception as e:
        print(f"❌ AiDeveloper agent test failed: {e}")
        return False

def test_uxui_designer_agent():
    """Test UXUIDesigner agent without LLM."""
    try:
        from bmad.agents.Agent.UXUIDesigner.uxuidesigner import UXUIDesignerAgent
        
        agent = UXUIDesignerAgent()
        
        # Test basic functionality
        assert agent.agent_name == "UXUIDesigner"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'create_design')
        
        print("✅ UXUIDesigner agent test passed")
        return True
    except Exception as e:
        print(f"❌ UXUIDesigner agent test failed: {e}")
        return False

def test_security_developer_agent():
    """Test SecurityDeveloper agent without LLM."""
    try:
        from bmad.agents.Agent.SecurityDeveloper.securitydeveloper import SecurityDeveloperAgent
        
        agent = SecurityDeveloperAgent()
        
        # Test basic functionality
        assert agent.agent_name == "SecurityDeveloper"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'security_scan')
        
        print("✅ SecurityDeveloper agent test passed")
        return True
    except Exception as e:
        print(f"❌ SecurityDeveloper agent test failed: {e}")
        return False

def test_accessibility_agent():
    """Test AccessibilityAgent without LLM."""
    try:
        from bmad.agents.Agent.AccessibilityAgent.accessibilityagent import AccessibilityAgent
        
        agent = AccessibilityAgent()
        
        # Test basic functionality
        assert agent.agent_name == "AccessibilityAgent"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'audit_accessibility')
        
        print("✅ AccessibilityAgent test passed")
        return True
    except Exception as e:
        print(f"❌ AccessibilityAgent test failed: {e}")
        return False

def test_data_engineer_agent():
    """Test DataEngineer agent without LLM."""
    try:
        from bmad.agents.Agent.DataEngineer.dataengineer import DataEngineerAgent
        
        agent = DataEngineerAgent()
        
        # Test basic functionality
        assert agent.agent_name == "DataEngineer"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'build_pipeline')
        
        print("✅ DataEngineer agent test passed")
        return True
    except Exception as e:
        print(f"❌ DataEngineer agent test failed: {e}")
        return False

def test_devops_infra_agent():
    """Test DevOpsInfra agent without LLM."""
    try:
        from bmad.agents.Agent.DevOpsInfra.devopsinfra import DevOpsInfraAgent
        
        agent = DevOpsInfraAgent()
        
        # Test basic functionality
        assert agent.agent_name == "DevOpsInfra"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'deploy_infrastructure')
        
        print("✅ DevOpsInfra agent test passed")
        return True
    except Exception as e:
        print(f"❌ DevOpsInfra agent test failed: {e}")
        return False

def test_release_manager_agent():
    """Test ReleaseManager agent without LLM."""
    try:
        from bmad.agents.Agent.ReleaseManager.releasemanager import ReleaseManagerAgent
        
        agent = ReleaseManagerAgent()
        
        # Test basic functionality
        assert agent.agent_name == "ReleaseManager"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'plan_release')
        
        print("✅ ReleaseManager agent test passed")
        return True
    except Exception as e:
        print(f"❌ ReleaseManager agent test failed: {e}")
        return False

def test_retrospective_agent():
    """Test Retrospective agent without LLM."""
    try:
        from bmad.agents.Agent.Retrospective.retrospective import RetrospectiveAgent
        
        agent = RetrospectiveAgent()
        
        # Test basic functionality
        assert agent.agent_name == "Retrospective"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'conduct_retrospective')
        
        print("✅ Retrospective agent test passed")
        return True
    except Exception as e:
        print(f"❌ Retrospective agent test failed: {e}")
        return False

def test_feedback_agent():
    """Test FeedbackAgent without LLM."""
    try:
        from bmad.agents.Agent.FeedbackAgent.feedbackagent import FeedbackAgent
        
        agent = FeedbackAgent()
        
        # Test basic functionality
        assert agent.agent_name == "FeedbackAgent"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'analyze_feedback')
        
        print("✅ FeedbackAgent test passed")
        return True
    except Exception as e:
        print(f"❌ FeedbackAgent test failed: {e}")
        return False

def test_rnd_agent():
    """Test RnD agent without LLM."""
    try:
        from bmad.agents.Agent.RnD.rnd import RnDAgent
        
        agent = RnDAgent()
        
        # Test basic functionality
        assert agent.agent_name == "RnD"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'conduct_research')
        
        print("✅ RnD agent test passed")
        return True
    except Exception as e:
        print(f"❌ RnD agent test failed: {e}")
        return False

def test_orchestrator_agent():
    """Test Orchestrator agent without LLM."""
    try:
        from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent()
        
        # Test basic functionality
        assert agent.agent_name == "Orchestrator"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'orchestrate_workflow')
        
        print("✅ Orchestrator agent test passed")
        return True
    except Exception as e:
        print(f"❌ Orchestrator agent test failed: {e}")
        return False

def test_mobile_developer_agent():
    """Test MobileDeveloper agent without LLM."""
    try:
        from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent
        
        agent = MobileDeveloperAgent()
        
        # Test basic functionality
        assert agent.agent_name == "MobileDeveloper"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'create_app')
        
        print("✅ MobileDeveloper agent test passed")
        return True
    except Exception as e:
        print(f"❌ MobileDeveloper agent test failed: {e}")
        return False

def test_documentation_agent():
    """Test DocumentationAgent without LLM."""
    try:
        from bmad.agents.Agent.DocumentationAgent.documentationagent import DocumentationAgent
        
        agent = DocumentationAgent()
        
        # Test basic functionality
        assert agent.agent_name == "DocumentationAgent"
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'create_documentation')
        
        print("✅ DocumentationAgent test passed")
        return True
    except Exception as e:
        print(f"❌ DocumentationAgent test failed: {e}")
        return False

def run_all_agent_tests():
    """Run all agent tests."""
    tests = [
        test_frontend_developer_agent,
        test_fullstack_developer_agent,
        test_architect_agent,
        test_ai_developer_agent,
        test_uxui_designer_agent,
        test_security_developer_agent,
        test_accessibility_agent,
        test_data_engineer_agent,
        test_devops_infra_agent,
        test_release_manager_agent,
        test_retrospective_agent,
        test_feedback_agent,
        test_rnd_agent,
        test_orchestrator_agent,
        test_mobile_developer_agent,
        test_documentation_agent
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    run_all_agent_tests() 