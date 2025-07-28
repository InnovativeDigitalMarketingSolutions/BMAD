#!/usr/bin/env python3
"""
ClickUp Template Implementatie Script

Dit script implementeert het gegenereerde template in ClickUp via de API.
"""

import os
import sys
import json
import requests

# Add bmad to path
sys.path.append('.')

def load_template_config(template_file="bmad_clickup_template.json"):
    """Laad de template configuratie."""
    try:
        with open(template_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Template bestand niet gevonden: {template_file}")
        return None

def get_clickup_headers():
    """Haal ClickUp headers op uit environment."""
    api_key = os.getenv('CLICKUP_API_KEY')
    if not api_key:
        print("❌ CLICKUP_API_KEY niet gevonden in environment")
        return None
    
    return {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

def test_clickup_connection(headers):
    """Test de ClickUp API verbinding."""
    print("🔗 Testen van ClickUp API verbinding...")
    
    try:
        response = requests.get('https://api.clickup.com/api/v2/user', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Verbinding succesvol - User: {user_data.get('user', {}).get('username', 'Unknown')}")
            return True
        else:
            print(f"❌ API verbinding mislukt: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fout bij API verbinding: {e}")
        return False

def get_workspace_info(headers):
    """Haal workspace informatie op."""
    print("🏢 Ophalen van workspace informatie...")
    
    try:
        response = requests.get('https://api.clickup.com/api/v2/team', headers=headers)
        if response.status_code == 200:
            teams = response.json().get('teams', [])
            if teams:
                workspace = teams[0]  # Gebruik eerste workspace
                print(f"✅ Workspace gevonden: {workspace.get('name', 'Unknown')}")
                return workspace
            else:
                print("❌ Geen workspaces gevonden")
                return None
        else:
            print(f"❌ Fout bij ophalen workspaces: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Fout bij ophalen workspace: {e}")
        return None

def create_space(headers, workspace_id, space_config):
    """Maak een nieuwe space aan."""
    print(f"📁 Aanmaken van space: {space_config['name']}")
    
    space_data = {
        "name": space_config['name'],
        "private": False,
        "features": {
            "due_dates": {
                "enabled": True,
                "start_date": True,
                "remap_due_dates": True,
                "remap_closed_due_date": False
            },
            "time_tracking": {
                "enabled": True
            },
            "tags": {
                "enabled": True
            },
            "time_estimates": {
                "enabled": True
            },
            "checklists": {
                "enabled": True
            },
            "custom_fields": {
                "enabled": True
            },
            "remap_dependencies": {
                "enabled": True
            },
            "dependency_warning": {
                "enabled": True
            },
            "portfolios": {
                "enabled": True
            }
        }
    }
    
    try:
        response = requests.post(
            f'https://api.clickup.com/api/v2/team/{workspace_id}/space',
            headers=headers,
            json=space_data
        )
        
        if response.status_code == 200:
            space = response.json()
            print(f"✅ Space aangemaakt: {space.get('name')} (ID: {space.get('id')})")
            return space
        else:
            print(f"❌ Fout bij aanmaken space: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Fout bij aanmaken space: {e}")
        return None

def create_folder(headers, space_id, folder_config):
    """Maak een nieuwe folder aan."""
    print(f"📂 Aanmaken van folder: {folder_config['name']}")
    
    folder_data = {
        "name": folder_config['name']
    }
    
    try:
        response = requests.post(
            f'https://api.clickup.com/api/v2/space/{space_id}/folder',
            headers=headers,
            json=folder_data
        )
        
        if response.status_code == 200:
            folder = response.json()
            print(f"✅ Folder aangemaakt: {folder.get('name')} (ID: {folder.get('id')})")
            return folder
        else:
            print(f"❌ Fout bij aanmaken folder: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Fout bij aanmaken folder: {e}")
        return None

def create_list(headers, folder_id, list_config):
    """Maak een nieuwe list aan."""
    print(f"📋 Aanmaken van list: {list_config['name']}")
    
    list_data = {
        "name": list_config['name'],
        "content": f"List voor {list_config['name']}",
        "due_date": None,
        "due_date_time": False,
        "priority": 2,
        "assignee": None,
        "status": list_config.get('default_status', 'Backlog')
    }
    
    try:
        response = requests.post(
            f'https://api.clickup.com/api/v2/folder/{folder_id}/list',
            headers=headers,
            json=list_data
        )
        
        if response.status_code == 200:
            list_obj = response.json()
            print(f"✅ List aangemaakt: {list_obj.get('name')} (ID: {list_obj.get('id')})")
            return list_obj
        else:
            print(f"❌ Fout bij aanmaken list: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Fout bij aanmaken list: {e}")
        return None

def create_custom_fields(headers, list_id, custom_fields_config):
    """Maak custom fields aan."""
    print(f"🏷️ Aanmaken van custom fields voor list {list_id}")
    
    for field_name, field_values in custom_fields_config.items():
        print(f"   📝 Aanmaken van field: {field_name}")
        
        # Bepaal field type op basis van naam
        if field_name == "story_points":
            field_type = "number"
        elif field_name in ["priority", "status", "sprint"]:
            field_type = "drop_down"
        else:
            field_type = "text"
        
        field_data = {
            "name": field_name.replace("_", " ").title(),
            "type": field_type,
            "type_config": {}
        }
        
        # Voeg dropdown opties toe
        if field_type == "drop_down":
            field_data["type_config"]["options"] = [
                {"name": value, "orderindex": idx}
                for idx, value in enumerate(field_values)
            ]
        
        try:
            response = requests.post(
                f'https://api.clickup.com/api/v2/list/{list_id}/field',
                headers=headers,
                json=field_data
            )
            
            if response.status_code == 200:
                field = response.json()
                print(f"   ✅ Field aangemaakt: {field.get('name')}")
            else:
                print(f"   ❌ Fout bij aanmaken field: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Fout bij aanmaken field: {e}")

def implement_template(template_config, workspace_id):
    """Implementeer het volledige template."""
    print("\n🚀 Implementeren van ClickUp template...")
    print("=" * 50)
    
    headers = get_clickup_headers()
    if not headers:
        return False
    
    # Test verbinding
    if not test_clickup_connection(headers):
        return False
    
    # Haal workspace info op
    workspace = get_workspace_info(headers)
    if not workspace:
        return False
    
    # Maak space aan
    space = create_space(headers, workspace_id, template_config['clickup_config']['space_config'])
    if not space:
        return False
    
    space_id = space['id']
    created_items = {
        'space': space,
        'folders': [],
        'lists': []
    }
    
    # Maak folders en lists aan
    for folder_config in template_config['clickup_config']['folders']:
        folder = create_folder(headers, space_id, folder_config)
        if folder:
            created_items['folders'].append(folder)
            
            # Maak lists aan in deze folder
            for list_config in folder_config['lists']:
                list_obj = create_list(headers, folder['id'], list_config)
                if list_obj:
                    created_items['lists'].append(list_obj)
                    
                    # Voeg custom fields toe aan deze list
                    create_custom_fields(headers, list_obj['id'], template_config['clickup_config']['custom_fields'])
    
    return created_items

def main():
    """Main function."""
    print("🎯 ClickUp Template Implementatie")
    print("=" * 40)
    
    # Laad template configuratie
    template_config = load_template_config()
    if not template_config:
        return
    
    print(f"📋 Template geladen: {template_config['template_name']}")
    print(f"📝 Beschrijving: {template_config['description']}")
    
    # Haal workspace ID op uit environment of gebruik default
    workspace_id = os.getenv('CLICKUP_WORKSPACE_ID', 'default_workspace_id')
    
    # Implementeer template
    result = implement_template(template_config, workspace_id)
    
    if result:
        print("\n🎉 Template succesvol geïmplementeerd!")
        print(f"📁 Space: {result['space']['name']} (ID: {result['space']['id']})")
        print(f"📂 Folders: {len(result['folders'])}")
        print(f"📋 Lists: {len(result['lists'])}")
        
        print("\n📊 Samenvatting:")
        for folder in result['folders']:
            print(f"   📂 {folder['name']}")
            # Toon lists in deze folder
            for list_obj in result['lists']:
                if list_obj.get('folder', {}).get('id') == folder['id']:
                    print(f"      📋 {list_obj['name']}")
    else:
        print("\n❌ Template implementatie mislukt")

if __name__ == "__main__":
    main() 