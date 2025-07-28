#!/usr/bin/env python3
"""
BMAD Project CLI
Command-line interface voor project management
"""

import argparse
import sys
from pathlib import Path

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

from bmad.projects.project_manager import project_manager

def main():
    parser = argparse.ArgumentParser(description="BMAD Project Manager")
    subparsers = parser.add_subparsers(dest="command", help="Beschikbare commando's")
    
    # List projects
    subparsers.add_parser("list", help="Toon alle projecten")
    
    # Create project
    create_parser = subparsers.add_parser("create", help="Maak nieuw project aan")
    create_parser.add_argument("project_id", help="Unieke project identifier")
    create_parser.add_argument("name", help="Project naam")
    create_parser.add_argument("--description", "-d", default="", help="Project beschrijving")
    
    # Add requirement
    req_parser = subparsers.add_parser("requirement", help="Voeg requirement toe")
    req_parser.add_argument("project_id", help="Project ID")
    req_parser.add_argument("requirement", help="Requirement tekst")
    req_parser.add_argument("--category", "-c", default="general", help="Requirement categorie")
    
    # Add user story
    story_parser = subparsers.add_parser("story", help="Voeg user story toe")
    story_parser.add_argument("project_id", help="Project ID")
    story_parser.add_argument("story", help="User story tekst")
    story_parser.add_argument("--priority", "-p", default="medium", help="Prioriteit (low/medium/high)")
    
    # Show project info
    subparsers.add_parser("info", help="Toon project informatie")
    
    # Add requirement
    req_parser = subparsers.add_parser("requirement", help="Voeg requirement toe")
    req_parser.add_argument("project_id", help="Project ID")
    req_parser.add_argument("requirement", help="Requirement tekst")
    req_parser.add_argument("--category", "-c", default="general", help="Requirement categorie")
    
    # Add user story
    story_parser = subparsers.add_parser("story", help="Voeg user story toe")
    story_parser.add_argument("project_id", help="Project ID")
    story_parser.add_argument("story", help="User story tekst")
    story_parser.add_argument("--priority", "-p", default="medium", help="Prioriteit (low/medium/high)")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactieve modus")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            projects = project_manager.list_projects()
            if projects:
                print("📁 Beschikbare projecten:")
                for project in projects:
                    print(f"  - {project}")
            else:
                print("📁 Geen projecten gevonden. Maak er een aan met 'create'.")
        
        elif args.command == "create":
            config = project_manager.create_project(args.name, args.type)
            print(f"✅ Project '{args.name}' aangemaakt als {args.type}")
            print(f"📋 Beschrijving: {config['description']}")
        
        elif args.command == "load":
            config = project_manager.load_project(args.name)
            print(f"📁 Project '{args.name}' geladen!")
            print(f"📋 Type: {config['project_type']}")
            print(f"📋 Beschrijving: {config['description']}")
        
        elif args.command == "info":
            config = project_manager.get_current_project()
            if not config:
                print("❌ Geen project geladen. Gebruik 'load <project_name>' eerst.")
                return
            
            print(f"📁 Project: {config['project_name']}")
            print(f"📋 Type: {config['project_type']}")
            print(f"📋 Beschrijving: {config['description']}")
            print(f"📋 Status: {config['status']}")
            
            # Requirements
            requirements = config.get('requirements', {})
            if requirements:
                print("\n📋 Requirements:")
                for category, reqs in requirements.items():
                    print(f"  {category}: {len(reqs)} items")
            
            # User stories
            stories = config.get('user_stories', [])
            if stories:
                print(f"\n📖 User Stories: {len(stories)} items")
            
            # Tech stack
            tech_stack = config.get('tech_stack', {})
            if tech_stack:
                print("\n🛠️ Tech Stack:")
                for area, techs in tech_stack.items():
                    print(f"  {area}: {', '.join(techs)}")
        
        elif args.command == "add-requirement":
            project_manager.add_requirement(args.requirement, args.category)
            print(f"✅ Requirement toegevoegd aan categorie '{args.category}'")
        
        elif args.command == "add-story":
            project_manager.add_user_story(args.story, args.priority)
            print(f"✅ User story toegevoegd met prioriteit '{args.priority}'")
        
        elif args.command == "interactive":
            start_interactive_mode()
    
    except Exception as e:
        print(f"❌ Fout: {e}")
        sys.exit(1)

def start_interactive_mode():
    """Start interactieve project management modus."""
    print("🚀 BMAD Project Manager - Interactieve Modus")
    print("=" * 50)
    print("Type 'help' voor commando's, 'quit' om te stoppen.")
    print()
    
    while True:
        try:
            command = input("📁 BMAD Project > ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Tot ziens! 👋")
                break
            elif command.lower() == 'help':
                show_interactive_help()
            elif command.lower() == 'list':
                projects = project_manager.list_projects()
                if projects:
                    print("📁 Beschikbare projecten:")
                    for project in projects:
                        print(f"  - {project}")
                else:
                    print("📁 Geen projecten gevonden.")
            elif command.lower().startswith('create '):
                parts = command.split(' ', 2)
                if len(parts) >= 2:
                    project_name = parts[1]
                    project_type = parts[2] if len(parts) > 2 else "web_app"
                    project_manager.create_project(project_name, project_type)
                else:
                    print("❌ Gebruik: create <project_name> [project_type]")
            elif command.lower().startswith('load '):
                parts = command.split(' ', 1)
                if len(parts) >= 2:
                    project_name = parts[1]
                    project_manager.load_project(project_name)
                else:
                    print("❌ Gebruik: load <project_name>")
            elif command.lower() == 'info':
                config = project_manager.get_current_project()
                if config:
                    print(f"📁 Huidig project: {config['project_name']}")
                    print(f"📋 Type: {config['project_type']}")
                else:
                    print("❌ Geen project geladen.")
            elif command.lower().startswith('add-req '):
                parts = command.split(' ', 2)
                if len(parts) >= 3:
                    category = parts[1]
                    requirement = parts[2]
                    project_manager.add_requirement(requirement, category)
                else:
                    print("❌ Gebruik: add-req <category> <requirement>")
            elif command.lower().startswith('add-story '):
                parts = command.split(' ', 2)
                if len(parts) >= 2:
                    story = parts[1]
                    priority = parts[2] if len(parts) > 2 else "medium"
                    project_manager.add_user_story(story, priority)
                else:
                    print("❌ Gebruik: add-story <story> [priority]")
            elif command:
                print(f"❌ Onbekend commando: {command}")
                print("Type 'help' voor beschikbare commando's.")
                
        except KeyboardInterrupt:
            print("\nTot ziens! 👋")
            break
        except Exception as e:
            print(f"❌ Fout: {e}")

def show_interactive_help():
    """Toon help voor interactieve modus."""
    print("""
📁 BMAD Project Manager - Beschikbare commando's:

Project Management:
  list                    - Toon alle projecten
  create <name> [type]    - Maak nieuw project (web_app/mobile_app/api_service)
  load <name>             - Laad een project
  info                    - Toon huidig project info

Content Management:
  add-req <cat> <req>     - Voeg requirement toe (functional/non_functional/technical)
  add-story <story> [pri] - Voeg user story toe (low/medium/high)

Utilities:
  help                    - Toon deze help
  quit                    - Stop interactieve modus
""")

if __name__ == "__main__":
    main() 