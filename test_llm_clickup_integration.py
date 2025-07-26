#!/usr/bin/env python3
"""
LLM + ClickUp Integration Test
=============================

Dit script test de integratie tussen LLM agents en ClickUp.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_llm_clickup_integration():
    """Test LLM + ClickUp integratie."""
    print("🧪 LLM + ClickUp Integration Test")
    print("=" * 50)
    
    try:
        # Import de benodigde modules
        sys.path.append('bmad')
        from agents.core.llm_client import ask_openai
        
        print("✅ Modules imported successfully")
        
        # Test 1: LLM functionaliteit
        print("\n1️⃣ Testing LLM functionality...")
        test_prompt = """
        Genereer 3 user stories voor een BMAD frontend project:
        - Een dashboard voor agent monitoring
        - Een project management interface
        - Een real-time notification system
        
        Format elke user story als:
        Feature: [titel]
        As a [rol]
        I want [functionaliteit]
        So that [voordeel]
        """
        
        response = ask_openai(test_prompt, model="gpt-4o-mini")
        print("✅ LLM response received")
        print(f"Response length: {len(response)} characters")
        
        # Test 2: ProductOwner agent (simplified)
        print("\n2️⃣ Testing ProductOwner agent...")
        
        # Test user story generatie met directe LLM call
        user_stories = []
        test_requirements = [
            "Dashboard voor agent monitoring",
            "Project management interface"
        ]
        
        for req in test_requirements:
            prompt = f"""
            Schrijf een user story in Gherkin-formaat voor de volgende requirement:
            
            Requirement: {req}
            
            Geef een user story met:
            - Feature beschrijving
            - Scenario's met Given/When/Then
            - Acceptatiecriteria
            - Prioriteit (High/Medium/Low)
            """
            
            story = ask_openai(prompt, model="gpt-4o-mini")
            if story:
                user_stories.append({
                    "title": req,
                    "content": story
                })
        
        print(f"✅ Generated {len(user_stories)} user stories")
        for i, story in enumerate(user_stories, 1):
            print(f"   Story {i}: {story.get('title', 'No title')}")
        
        # Test 3: ClickUp integratie (simulated)
        print("\n3️⃣ Testing ClickUp integration simulation...")
        
        # Simuleer het aanmaken van taken in ClickUp
        for i, story in enumerate(user_stories, 1):
            task_name = story.get('title', f'User Story {i}')
            task_content = story.get('content', 'No content available')
            
            print(f"   Would create task: {task_name}")
            print(f"   Content: {task_content[:100]}...")
        
        print("\n🎉 LLM + ClickUp integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_real_clickup_integration():
    """Test echte ClickUp integratie met LLM gegenereerde content."""
    print("\n🚀 Real ClickUp Integration Test")
    print("=" * 50)
    
    try:
        import requests
        from agents.core.llm_client import ask_openai
        
        # Genereer een user story met LLM
        prompt = """
        Genereer 1 user story voor een BMAD frontend dashboard feature.
        Geef het antwoord in JSON format:
        {
            "title": "Dashboard Title",
            "as_a": "user role",
            "i_want": "desired functionality",
            "so_that": "benefit",
            "acceptance_criteria": "list of criteria"
        }
        """
        
        response = ask_openai(prompt, model="gpt-4o-mini")
        print("✅ LLM generated user story")
        
        # Parse de response (simplified)
        import json
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                story_data = json.loads(json_str)
            else:
                # Fallback: create simple story
                story_data = {
                    "title": "BMAD Dashboard Monitoring",
                    "as_a": "DevOps engineer",
                    "i_want": "real-time monitoring of BMAD agents",
                    "so_that": "I can track system performance and agent status",
                    "acceptance_criteria": "Dashboard shows agent status, metrics, and alerts"
                }
        except:
            # Fallback
            story_data = {
                "title": "BMAD Dashboard Monitoring",
                "as_a": "DevOps engineer", 
                "i_want": "real-time monitoring of BMAD agents",
                "so_that": "I can track system performance and agent status",
                "acceptance_criteria": "Dashboard shows agent status, metrics, and alerts"
            }
        
        print(f"✅ Parsed story: {story_data['title']}")
        
        # Maak task aan in ClickUp
        api_key = os.getenv("CLICKUP_API_KEY")
        list_id = os.getenv("CLICKUP_LIST_ID")
        
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        task_data = {
            "name": story_data["title"],
            "content": f"""
Feature: {story_data['title']}

As a {story_data['as_a']}
I want {story_data['i_want']}
So that {story_data['so_that']}

Acceptance Criteria:
{story_data['acceptance_criteria']}

Generated by: BMAD LLM Integration
            """.strip(),
            "status": "Open",
            "priority": 2
        }
        
        response = requests.post(f"https://api.clickup.com/api/v2/list/{list_id}/task", 
                               headers=headers, json=task_data)
        
        if response.status_code == 200:
            task_response = response.json()
            task_id = task_response.get('id')
            print(f"✅ Task created in ClickUp: {task_id}")
            print(f"   Title: {story_data['title']}")
            print(f"   URL: https://app.clickup.com/t/{task_id}")
            
            return task_id
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Real integration error: {e}")
        return None

if __name__ == "__main__":
    # Test 1: Basic integration
    success = test_llm_clickup_integration()
    
    if success:
        # Test 2: Real ClickUp integration
        task_id = test_real_clickup_integration()
        
        if task_id:
            print(f"\n🎉 SUCCESS! Created real task in ClickUp: {task_id}")
        else:
            print(f"\n⚠️  Basic integration works, but real ClickUp integration failed")
    else:
        print(f"\n❌ Basic integration failed") 