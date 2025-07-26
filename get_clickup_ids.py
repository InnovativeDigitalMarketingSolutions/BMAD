#!/usr/bin/env python3
"""
ClickUp ID Finder Script
========================

Dit script helpt bij het vinden van ClickUp IDs en het bijwerken van de .env file.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_clickup_data():
    """Haal ClickUp data op om IDs te vinden."""
    api_key = os.getenv("CLICKUP_API_KEY")
    space_id = os.getenv("CLICKUP_SPACE_ID")
    
    if not api_key:
        print("❌ CLICKUP_API_KEY niet gevonden in .env")
        return
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    print("🔍 ClickUp IDs Finder")
    print("=" * 50)
    
    # Haal spaces op
    try:
        print("📋 Beschikbare Spaces:")
        response = requests.get("https://api.clickup.com/api/v2/team", headers=headers)
        response.raise_for_status()
        teams = response.json()["teams"]
        
        for team in teams:
            print(f"   Team: {team['name']} (ID: {team['id']})")
            
            # Haal spaces op voor dit team
            spaces_response = requests.get(f"https://api.clickup.com/api/v2/team/{team['id']}/space", headers=headers)
            if spaces_response.status_code == 200:
                spaces = spaces_response.json()["spaces"]
                for space in spaces:
                    print(f"     └─ Space: {space['name']} (ID: {space['id']})")
                    
                    # Haal folders op voor deze space
                    folders_response = requests.get(f"https://api.clickup.com/api/v2/space/{space['id']}/folder", headers=headers)
                    if folders_response.status_code == 200:
                        folders = folders_response.json()["folders"]
                        for folder in folders:
                            print(f"       └─ Folder: {folder['name']} (ID: {folder['id']})")
                            
                            # Haal lists op voor deze folder
                            lists_response = requests.get(f"https://api.clickup.com/api/v2/folder/{folder['id']}/list", headers=headers)
                            if lists_response.status_code == 200:
                                lists = lists_response.json()["lists"]
                                for list_item in lists:
                                    print(f"         └─ List: {list_item['name']} (ID: {list_item['id']})")
                    
                    # Haal ook lists op die direct in de space staan (zonder folder)
                    lists_response = requests.get(f"https://api.clickup.com/api/v2/space/{space['id']}/list", headers=headers)
                    if lists_response.status_code == 200:
                        lists = lists_response.json()["lists"]
                        for list_item in lists:
                            print(f"       └─ List: {list_item['name']} (ID: {list_item['id']})")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    print("\n" + "=" * 50)
    print("📝 Volg deze stappen om je .env file bij te werken:")
    print("1. Kopieer de gewenste Folder ID en List ID uit bovenstaande output")
    print("2. Voeg deze toe aan je .env file:")
    print("   CLICKUP_FOLDER_ID=jouw_folder_id_hier")
    print("   CLICKUP_LIST_ID=jouw_list_id_hier")
    print("3. Run opnieuw: python test_clickup_integration.py")

if __name__ == "__main__":
    get_clickup_data() 