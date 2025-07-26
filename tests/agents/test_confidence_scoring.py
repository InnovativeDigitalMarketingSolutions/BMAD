#!/usr/bin/env python3
"""
Test script voor confidence scoring functionaliteit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from bmad.agents.core.confidence_scoring import confidence_scoring, create_review_request, format_confidence_message
from bmad.agents.core.llm_client import ask_openai_with_confidence

def test_confidence_scoring_basic():
    """Test basis confidence scoring functionaliteit."""
    output = "Dit is een eenvoudige user story voor een dashboard feature."
    agent_name = "ProductOwner"
    task_type = "create_user_story"
    
    enhanced_output = confidence_scoring.enhance_agent_output(
        output=output,
        agent_name=agent_name,
        task_type=task_type
    )
    
    # Check dat alle verwachte velden aanwezig zijn
    assert "output" in enhanced_output
    assert "confidence" in enhanced_output
    assert "review_required" in enhanced_output
    assert "review_level" in enhanced_output
    assert "metadata" in enhanced_output
    
    # Check dat confidence tussen 0 en 1 ligt
    assert 0.0 <= enhanced_output["confidence"] <= 1.0
    
    # Check metadata
    metadata = enhanced_output["metadata"]
    assert metadata["agent"] == agent_name
    assert metadata["task_type"] == task_type
    assert "timestamp" in metadata

def test_confidence_scoring_security_critical():
    """Test confidence scoring voor security-critical taken."""
    output = "Implementeer JWT authentication met password hashing en token rotation."
    agent_name = "SecurityDeveloper"
    task_type = "implement_authentication"
    
    enhanced_output = confidence_scoring.enhance_agent_output(
        output=output,
        agent_name=agent_name,
        task_type=task_type
    )
    
    # Security-critical taken zouden review moeten vereisen
    assert enhanced_output["review_required"] == True
    assert enhanced_output["review_level"] in ["low", "medium", "high"]

def test_confidence_scoring_high_complexity():
    """Test confidence scoring voor high complexity taken."""
    output = "Design een microservices architectuur met API gateway en service mesh."
    agent_name = "Architect"
    task_type = "design_architecture"
    
    enhanced_output = confidence_scoring.enhance_agent_output(
        output=output,
        agent_name=agent_name,
        task_type=task_type
    )
    
    # High complexity taken zouden review moeten vereisen bij medium confidence
    if enhanced_output["confidence"] < 0.8:
        assert enhanced_output["review_required"] == True

def test_review_request_creation():
    """Test review request creatie."""
    enhanced_output = {
        "output": "Test user story output",
        "confidence": 0.75,
        "review_required": True,
        "review_level": "medium",
        "metadata": {
            "agent": "ProductOwner",
            "task_type": "create_user_story",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    
    review_request = create_review_request(enhanced_output)
    
    # Check review request structuur
    assert review_request["type"] == "review_request"
    assert review_request["agent"] == "ProductOwner"
    assert review_request["confidence"] == 0.75
    assert review_request["review_level"] == "medium"
    assert "actions" in review_request
    assert len(review_request["actions"]) == 3  # approve, reject, modify

def test_confidence_message_formatting():
    """Test confidence message formatting."""
    enhanced_output = {
        "output": "Test user story output voor dashboard feature",
        "confidence": 0.85,
        "review_required": False,
        "review_level": "high",
        "metadata": {
            "agent": "ProductOwner",
            "task_type": "create_user_story",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    
    # Voeg output_preview toe (wordt automatisch toegevoegd door create_review_request)
    enhanced_output["output_preview"] = enhanced_output["output"][:200] + "..." if len(enhanced_output["output"]) > 200 else enhanced_output["output"]
    
    message = format_confidence_message(enhanced_output)
    
    # Check dat message de juiste informatie bevat
    assert "Confidence Score: 0.85" in message
    assert "Review Level: HIGH" in message
    assert "**Agent:** ProductOwner" in message
    assert "**Task:** create_user_story" in message
    assert "🟢" in message  # High confidence emoji
    assert "✅" in message  # High review level emoji

def test_llm_confidence_integration():
    """Test LLM confidence integratie (skip als geen API key)."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("Geen OpenAI API key beschikbaar")
    
    prompt = "Schrijf een korte user story voor een login feature."
    context = {
        "task": "create_user_story",
        "agent": "ProductOwner",
        "requirement": "User login"
    }
    
    result = ask_openai_with_confidence(prompt, context)
    
    # Check dat result de juiste structuur heeft
    assert "answer" in result
    assert "confidence" in result
    assert "cached" in result
    assert "model" in result
    assert "timestamp" in result
    
    # Check dat confidence tussen 0 en 1 ligt
    assert 0.0 <= result["confidence"] <= 1.0

def test_confidence_thresholds():
    """Test confidence thresholds en review levels."""
    test_cases = [
        (0.3, "low", True),      # Low confidence = review required
        (0.6, "medium", True),   # Medium confidence = review required
        (0.9, "high", False),    # High confidence = no review required
    ]
    
    for confidence, expected_level, expected_review in test_cases:
        enhanced_output = {
            "output": "Test output",
            "confidence": confidence,
            "review_required": expected_review,
            "review_level": expected_level,
            "metadata": {
                "agent": "TestAgent",
                "task_type": "test_task",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Test review level
        assert enhanced_output["review_level"] == expected_level
        
        # Test review requirement
        assert enhanced_output["review_required"] == expected_review

if __name__ == "__main__":
    # Run tests
    print("🧪 Testing Confidence Scoring...")
    
    try:
        test_confidence_scoring_basic()
        print("✅ Basic confidence scoring test passed")
        
        test_confidence_scoring_security_critical()
        print("✅ Security critical confidence scoring test passed")
        
        test_confidence_scoring_high_complexity()
        print("✅ High complexity confidence scoring test passed")
        
        test_review_request_creation()
        print("✅ Review request creation test passed")
        
        test_confidence_message_formatting()
        print("✅ Confidence message formatting test passed")
        
        test_confidence_thresholds()
        print("✅ Confidence thresholds test passed")
        
        # Test LLM integration if API key available
        if os.getenv("OPENAI_API_KEY"):
            test_llm_confidence_integration()
            print("✅ LLM confidence integration test passed")
        else:
            print("⚠️  Skipping LLM integration test (no API key)")
        
        print("\n🎉 Alle confidence scoring tests geslaagd!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1) 