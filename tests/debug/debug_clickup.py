#!/usr/bin/env python3
"""
Debug script voor ClickUp API
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_clickup_api():
    """Test ClickUp API direct."""
    api_key = os.getenv("CLICKUP_API_KEY")
    space_id = os.getenv("CLICKUP_SPACE_ID")
    
    print(f"🔍 Testing ClickUp API directly")
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if api_key else 'None'}")
    print(f"Space ID: {space_id}")
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Get teams
    print("\n1️⃣ Testing /team endpoint...")
    try:
        response = requests.get("https://api.clickup.com/api/v2/team", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            teams = data["teams"]
            print(f"✅ Found {len(teams)} teams")
            for team in teams:
                print(f"   - {team['name']} (ID: {team['id']})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Get specific space
    print(f"\n2️⃣ Testing /space/{space_id} endpoint...")
    try:
        response = requests.get(f"https://api.clickup.com/api/v2/space/{space_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Get list
    list_id = os.getenv("CLICKUP_LIST_ID")
    print(f"\n3️⃣ Testing /list/{list_id} endpoint...")
    try:
        response = requests.get(f"https://api.clickup.com/api/v2/list/{list_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_clickup_api() 