#!/usr/bin/env python3
"""
Eenvoudige ClickUp integratie test
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_clickup_simple():
    """Test ClickUp integratie zonder complexe dependencies."""
    print("🧪 Simple ClickUp Integration Test")
    print("=" * 50)
    
    # Get environment variables
    api_key = os.getenv("CLICKUP_API_KEY")
    space_id = os.getenv("CLICKUP_SPACE_ID")
    folder_id = os.getenv("CLICKUP_FOLDER_ID")
    list_id = os.getenv("CLICKUP_LIST_ID")
    
    print(f"✅ API Key: {api_key[:8]}...{api_key[-4:] if api_key else 'None'}")
    print(f"✅ Space ID: {space_id}")
    print(f"✅ Folder ID: {folder_id}")
    print(f"✅ List ID: {list_id}")
    
    if not all([api_key, space_id, folder_id, list_id]):
        print("❌ Missing environment variables")
        return False
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Get space info
    print("\n1️⃣ Testing space info...")
    try:
        response = requests.get(f"https://api.clickup.com/api/v2/space/{space_id}", headers=headers)
        if response.status_code == 200:
            space_data = response.json()
            print(f"✅ Space: {space_data.get('name', 'Unknown')}")
        else:
            print(f"❌ Space error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Space error: {e}")
        return False
    
    # Test 2: Get list info
    print("\n2️⃣ Testing list info...")
    try:
        response = requests.get(f"https://api.clickup.com/api/v2/list/{list_id}", headers=headers)
        if response.status_code == 200:
            list_data = response.json()
            print(f"✅ List: {list_data.get('name', 'Unknown')}")
        else:
            print(f"❌ List error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ List error: {e}")
        return False
    
    # Test 3: Create a test task
    print("\n3️⃣ Testing task creation...")
    try:
        task_data = {
            "name": "BMAD Test Task",
            "content": "This is a test task created by BMAD integration",
            "status": "Open",
            "priority": 3
        }
        
        response = requests.post(f"https://api.clickup.com/api/v2/list/{list_id}/task", 
                               headers=headers, json=task_data)
        
        if response.status_code == 200:
            task_response = response.json()
            task_id = task_response.get('id')
            print(f"✅ Task created: {task_id}")
            
            # Clean up: delete the test task
            delete_response = requests.delete(f"https://api.clickup.com/api/v2/task/{task_id}", 
                                            headers=headers)
            if delete_response.status_code == 200:
                print("✅ Test task cleaned up")
            else:
                print(f"⚠️  Could not clean up test task: {delete_response.status_code}")
                
        else:
            print(f"❌ Task creation error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return False
    
    print("\n🎉 All tests passed! ClickUp integration is working correctly.")
    return True

if __name__ == "__main__":
    test_clickup_simple() 