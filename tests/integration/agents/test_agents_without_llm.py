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
    from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
    
    agent = FrontendDeveloperAgent()
    
    # Test basic functionality
    assert agent.agent_name == "FrontendDeveloper"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'build_component')
    
    print("✅ FrontendDeveloper agent test passed")

def test_fullstack_developer_agent():
    """Test FullstackDeveloper agent without LLM."""
    from bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper import FullstackDeveloperAgent
    
    agent = FullstackDeveloperAgent()
    
    # Test basic functionality
    assert agent.agent_name == "FullstackDeveloper"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'build_shadcn_component')
    
    print("✅ FullstackDeveloper agent test passed")

def test_architect_agent():
    """Test Architect agent without LLM."""
    from bmad.agents.Agent.Architect.architect import ArchitectAgent
    
    agent = ArchitectAgent()
    
    # Test basic functionality
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'design_frontend')
    
    print("✅ Architect agent test passed")

def test_ai_developer_agent():
    """Test AiDeveloper agent without LLM."""
    from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent
    
    agent = AiDeveloperAgent()
    
    # Test basic functionality
    assert agent.agent_name == "AiDeveloper"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'experiment_log')
    
    print("✅ AiDeveloper agent test passed")

def test_uxui_designer_agent():
    """Test UXUIDesigner agent without LLM."""
    from bmad.agents.Agent.UXUIDesigner.uxuidesigner import UXUIDesignerAgent
    
    agent = UXUIDesignerAgent()
    
    # Test basic functionality
    assert agent.agent_name == "UXUIDesigner"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'create_component_spec')
    
    print("✅ UXUIDesigner agent test passed")

def test_security_developer_agent():
    """Test SecurityDeveloper agent without LLM."""
    from bmad.agents.Agent.SecurityDeveloper.securitydeveloper import SecurityDeveloperAgent
    
    agent = SecurityDeveloperAgent()
    
    # Test basic functionality
    assert agent.agent_name == "SecurityDeveloper"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'security_review')
    
    print("✅ SecurityDeveloper agent test passed")

def test_accessibility_agent():
    """Test AccessibilityAgent without LLM."""
    from bmad.agents.Agent.AccessibilityAgent.accessibilityagent import AccessibilityAgent
    
    agent = AccessibilityAgent()
    
    # Test basic functionality
    assert agent.agent_name == "AccessibilityAgent"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'run_accessibility_audit')
    
    print("✅ AccessibilityAgent test passed")

def test_data_engineer_agent():
    """Test DataEngineer agent without LLM."""
    from bmad.agents.Agent.DataEngineer.dataengineer import DataEngineerAgent
    
    agent = DataEngineerAgent()
    
    # Test basic functionality
    assert agent.agent_name == "DataEngineer"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'build_pipeline')
    
    print("✅ DataEngineer agent test passed")

def test_devops_infra_agent():
    """Test DevOpsInfra agent without LLM."""
    from bmad.agents.Agent.DevOpsInfra.devopsinfra import DevOpsInfraAgent
    
    agent = DevOpsInfraAgent()
    
    # Test basic functionality
    assert agent.agent_name == "DevOpsInfra"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'deploy_infrastructure')
    
    print("✅ DevOpsInfra agent test passed")

def test_release_manager_agent():
    """Test ReleaseManager agent without LLM."""
    from bmad.agents.Agent.ReleaseManager.releasemanager import ReleaseManagerAgent
    
    agent = ReleaseManagerAgent()
    
    # Test basic functionality
    assert agent.agent_name == "ReleaseManager"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'create_release')
    
    print("✅ ReleaseManager agent test passed")

def test_retrospective_agent():
    """Test Retrospective agent without LLM."""
    from bmad.agents.Agent.Retrospective.retrospective import RetrospectiveAgent
    
    agent = RetrospectiveAgent()
    
    # Test basic functionality
    assert agent.agent_name == "Retrospective"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'conduct_retrospective')
    
    print("✅ Retrospective agent test passed")

def test_feedback_agent():
    """Test FeedbackAgent without LLM."""
    from bmad.agents.Agent.FeedbackAgent.feedbackagent import FeedbackAgent
    
    agent = FeedbackAgent()
    
    # Test basic functionality
    assert agent.agent_name == "FeedbackAgent"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'analyze_sentiment')
    
    print("✅ FeedbackAgent test passed")

def test_rnd_agent():
    """Test RnD agent without LLM."""
    from bmad.agents.Agent.RnD.rnd import RnDAgent
    
    agent = RnDAgent()
    
    # Test basic functionality
    assert agent.agent_name == "RnD"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'conduct_research')
    
    print("✅ RnD agent test passed")

def test_orchestrator_agent():
    """Test Orchestrator agent without LLM."""
    from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent
    
    agent = OrchestratorAgent()
    
    # Test basic functionality
    assert agent.agent_name == "Orchestrator"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'orchestrate_agents')
    
    print("✅ Orchestrator agent test passed")

def test_mobile_developer_agent():
    """Test MobileDeveloper agent without LLM."""
    from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent
    
    agent = MobileDeveloperAgent()
    
    # Test basic functionality
    assert agent.agent_name == "MobileDeveloper"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'create_app')
    
    print("✅ MobileDeveloper agent test passed")

def test_documentation_agent():
    """Test DocumentationAgent without LLM."""
    from bmad.agents.Agent.DocumentationAgent.documentationagent import DocumentationAgent
    
    agent = DocumentationAgent()
    
    # Test basic functionality
    assert agent.agent_name == "DocumentationAgent"
    assert hasattr(agent, 'show_help')
    assert hasattr(agent, 'create_api_docs')
    
    print("✅ DocumentationAgent test passed")

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
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    run_all_agent_tests() 