#!/usr/bin/env python3
"""
BMAD Project Management CLI

Beheer BMAD projecten en ClickUp configuraties.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add bmad to path
sys.path.append(str(Path(__file__).parent.parent))

from bmad.agents.core.project_manager import project_manager

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="BMAD Project Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Beschikbare commando's")
    
    # List projects command
    subparsers.add_parser("list", help="Toon alle projecten")
    
    # Create project command
    create_parser = subparsers.add_parser("create", help="Maak nieuw project aan")
    create_parser.add_argument("project_id", help="Unieke project identifier")
    create_parser.add_argument("name", help="Project naam")
    create_parser.add_argument("--description", "-d", default="", help="Project beschrijving")
    create_parser.add_argument("--folder-id", help="ClickUp folder ID")
    create_parser.add_argument("--list-id", help="ClickUp list ID")
    
    # Set active project command
    active_parser = subparsers.add_parser("active", help="Stel actief project in")
    active_parser.add_argument("project_id", help="Project ID om actief te maken")
    
    # Show project command
    show_parser = subparsers.add_parser("show", help="Toon project details")
    show_parser.add_argument("project_id", nargs="?", help="Project ID (gebruikt actief project als niet opgegeven)")
    
    # Update project command
    update_parser = subparsers.add_parser("update", help="Update project configuratie")
    update_parser.add_argument("project_id", help="Project ID")
    update_parser.add_argument("--name", help="Nieuwe project naam")
    update_parser.add_argument("--description", "-d", help="Nieuwe project beschrijving")
    update_parser.add_argument("--folder-id", help="Nieuwe ClickUp folder ID")
    update_parser.add_argument("--list-id", help="Nieuwe ClickUp list ID")
    
    # Delete project command
    delete_parser = subparsers.add_parser("delete", help="Verwijder project")
    delete_parser.add_argument("project_id", help="Project ID om te verwijderen")
    
    # Test ClickUp command
    test_parser = subparsers.add_parser("test-clickup", help="Test ClickUp integratie voor project")
    test_parser.add_argument("project_id", nargs="?", help="Project ID (gebruikt actief project als niet opgegeven)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            list_projects()
        elif args.command == "create":
            create_project(args)
        elif args.command == "active":
            set_active_project(args)
        elif args.command == "show":
            show_project(args)
        elif args.command == "update":
            update_project(args)
        elif args.command == "delete":
            delete_project(args)
        elif args.command == "test-clickup":
            test_clickup(args)
        else:
            print(f"Onbekend commando: {args.command}")
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Fout: {e}")
        sys.exit(1)

def list_projects():
    """Toon alle projecten."""
    print("📋 BMAD Projecten")
    print("=" * 50)
    
    projects = project_manager.list_projects()
    
    if not projects:
        print("Geen projecten gevonden.")
        return
    
    for project in projects:
        status = "🟢 ACTIEF" if project["active"] else "⚪"
        print(f"{status} {project['id']:15} - {project['name']}")
        if project["description"]:
            print(f"              {project['description']}")
        print(f"              Gemaakt: {project['created_at']}")
        print()

def create_project(args):
    """Maak nieuw project aan."""
    print(f"🚀 Nieuw project aanmaken: {args.project_id}")
    print("=" * 50)
    
    success = project_manager.create_project(
        project_id=args.project_id,
        name=args.name,
        description=args.description,
        clickup_folder_id=args.folder_id,
        clickup_list_id=args.list_id
    )
    
    if success:
        print(f"\n✅ Project '{args.name}' succesvol aangemaakt!")
        print(f"   ID: {args.project_id}")
        if args.folder_id:
            print(f"   ClickUp Folder ID: {args.folder_id}")
        if args.list_id:
            print(f"   ClickUp List ID: {args.list_id}")
    else:
        print("\n❌ Fout bij aanmaken project")
        sys.exit(1)

def set_active_project(args):
    """Stel actief project in."""
    print(f"🔄 Actief project instellen: {args.project_id}")
    print("=" * 50)
    
    success = project_manager.set_active_project(args.project_id)
    
    if success:
        print(f"✅ Actief project ingesteld op: {args.project_id}")
    else:
        print(f"❌ Kon project '{args.project_id}' niet actief maken")
        sys.exit(1)

def show_project(args):
    """Toon project details."""
    project_id = args.project_id or project_manager.active_project
    print(f"📊 Project Details: {project_id}")
    print("=" * 50)
    
    config = project_manager.get_project_config(project_id)
    
    print(f"Naam: {config.get('name', 'Unknown')}")
    print(f"Beschrijving: {config.get('description', 'Geen beschrijving')}")
    print(f"Actief: {'Ja' if project_id == project_manager.active_project else 'Nee'}")
    print(f"Gemaakt: {config.get('created_at', 'Unknown')}")
    
    if "updated_at" in config:
        print(f"Bijgewerkt: {config['updated_at']}")
    
    print("\n📋 ClickUp Configuratie:")
    clickup_config = config.get("clickup", {})
    print(f"  Folder ID: {clickup_config.get('folder_id', 'Niet ingesteld')}")
    print(f"  List ID: {clickup_config.get('list_id', 'Niet ingesteld')}")
    
    print("\n🤖 Agent Configuratie:")
    agents_config = config.get("agents", {})
    for agent_type, agent_id in agents_config.items():
        print(f"  {agent_type}: {agent_id}")
    
    print("\n⚙️ Instellingen:")
    settings = config.get("settings", {})
    for setting, value in settings.items():
        print(f"  {setting}: {value}")

def update_project(args):
    """Update project configuratie."""
    print(f"🔄 Project bijwerken: {args.project_id}")
    print("=" * 50)
    
    updates = {}
    
    if args.name:
        updates["name"] = args.name
    if args.description:
        updates["description"] = args.description
    if args.folder_id:
        updates["clickup"] = {"folder_id": args.folder_id}
    if args.list_id:
        if "clickup" not in updates:
            updates["clickup"] = {}
        updates["clickup"]["list_id"] = args.list_id
    
    if not updates:
        print("❌ Geen updates opgegeven")
        return
    
    success = project_manager.update_project_config(args.project_id, updates)
    
    if success:
        print(f"✅ Project '{args.project_id}' succesvol bijgewerkt!")
    else:
        print(f"❌ Fout bij bijwerken project '{args.project_id}'")
        sys.exit(1)

def delete_project(args):
    """Verwijder project."""
    print(f"🗑️ Project verwijderen: {args.project_id}")
    print("=" * 50)
    
    # Bevestiging vragen
    confirm = input(f"Weet je zeker dat je project '{args.project_id}' wilt verwijderen? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Verwijdering geannuleerd")
        return
    
    success = project_manager.delete_project(args.project_id)
    
    if success:
        print(f"✅ Project '{args.project_id}' succesvol verwijderd!")
    else:
        print(f"❌ Fout bij verwijderen project '{args.project_id}'")
        sys.exit(1)

def test_clickup(args):
    """Test ClickUp integratie voor project."""
    project_id = args.project_id or project_manager.active_project
    print(f"🧪 ClickUp integratie testen voor project: {project_id}")
    print("=" * 50)
    
    try:
        from agents.core.clickup_integration import ClickUpIntegration
        
        # Test met project-specifieke configuratie
        clickup = ClickUpIntegration(project_id=project_id)
        
        if not clickup.enabled:
            print("❌ ClickUp integratie uitgeschakeld")
            return
        
        print("✅ ClickUp integratie geïnitialiseerd")
        
        # Test API connectivity
        import requests
        url = f"{clickup.base_url}/space/{clickup.space_id}"
        response = requests.get(url, headers=clickup.headers)
        
        if response.status_code == 200:
            print("✅ API verbinding succesvol")
            space_data = response.json()
            print(f"   Space: {space_data.get('space', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ API verbinding mislukt: {response.status_code}")
            return
        
        # Toon project configuratie
        config = project_manager.get_project_config(project_id)
        clickup_config = config.get("clickup", {})
        
        print(f"\n📋 Project ClickUp Configuratie:")
        print(f"  Folder ID: {clickup_config.get('folder_id', 'Niet ingesteld')}")
        print(f"  List ID: {clickup_config.get('list_id', 'Niet ingesteld')}")
        
        print("\n✅ ClickUp integratie test succesvol!")
        
    except Exception as e:
        print(f"❌ ClickUp test fout: {e}")

if __name__ == "__main__":
    main() 