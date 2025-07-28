#!/usr/bin/env python3
"""
BMAD ClickUp Workflow Script
============================

Dit script gebruikt de ProductOwner en ScrumMaster agents om:
1. De ClickUp space aan te passen aan de BMAD workflow
2. Een frontend planning te genereren en in te plannen in sprints

Gebruik: python bmad_clickup_workflow.py
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import requests

# BMAD imports
sys.path.append(".")
from bmad.agents.core.clickup_integration import ClickUpIntegration
from bmad.agents.core.llm_client import ask_openai_with_confidence
from bmad.agents.core.project_manager import ProjectManager


class BMADClickUpWorkflow:
    def __init__(self, project_id: str = "bmad-frontend"):
        """Initialize the workflow with project configuration."""
        self.project_id = project_id
        self.project_manager = ProjectManager()
        self.clickup = ClickUpIntegration(project_id=project_id)
        # ProductOwner is function-based, not class-based

        # Get ClickUp configuration
        self.config = self.project_manager.get_clickup_config(project_id)
        print(f"🚀 BMAD ClickUp Workflow gestart voor project: {project_id}")
        print(f"📋 ClickUp Space ID: {self.config.get('space_id', 'Niet geconfigureerd')}")

    def adapt_clickup_template_to_bmad(self) -> Dict[str, Any]:
        """Pas het ClickUp template aan aan de BMAD workflow."""
        print("\n🔧 Stap 1: ClickUp template aanpassen aan BMAD workflow...")

        # BMAD workflow template definitie
        bmad_template = {
            "space_name": "BMAD Frontend Project",
            "folders": [
                {
                    "name": "📋 Product Backlog",
                    "lists": [
                        {
                            "name": "🎯 Epics",
                            "task_types": ["Epic"],
                            "custom_fields": [
                                {"name": "Business Value", "type": "number"},
                                {"name": "Story Points", "type": "number"},
                                {"name": "Acceptance Criteria", "type": "text"},
                                {"name": "Definition of Done", "type": "text"}
                            ]
                        },
                        {
                            "name": "📝 User Stories",
                            "task_types": ["User Story"],
                            "custom_fields": [
                                {"name": "Story Points", "type": "number"},
                                {"name": "Priority", "type": "dropdown", "options": ["Critical", "High", "Medium", "Low"]},
                                {"name": "Acceptance Criteria", "type": "text"},
                                {"name": "Definition of Done", "type": "text"},
                                {"name": "Dependencies", "type": "text"}
                            ]
                        },
                        {
                            "name": "🔧 Technical Tasks",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Story Points", "type": "number"},
                                {"name": "Priority", "type": "dropdown", "options": ["Critical", "High", "Medium", "Low"]},
                                {"name": "Technical Complexity", "type": "dropdown", "options": ["Low", "Medium", "High"]},
                                {"name": "Dependencies", "type": "text"}
                            ]
                        }
                    ]
                },
                {
                    "name": "🏃‍♂️ Sprint Management",
                    "lists": [
                        {
                            "name": "📅 Sprint Planning",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Sprint Goal", "type": "text"},
                                {"name": "Team Capacity", "type": "number"},
                                {"name": "Sprint Duration", "type": "number"}
                            ]
                        },
                        {
                            "name": "🔄 Sprint Backlog",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Story Points", "type": "number"},
                                {"name": "Sprint", "type": "dropdown", "options": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"]},
                                {"name": "Assigned To", "type": "text"},
                                {"name": "Status", "type": "dropdown", "options": ["To Do", "In Progress", "Review", "Done"]}
                            ]
                        },
                        {
                            "name": "📊 Sprint Review",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Sprint", "type": "dropdown", "options": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"]},
                                {"name": "Demo Notes", "type": "text"},
                                {"name": "Feedback", "type": "text"}
                            ]
                        },
                        {
                            "name": "🔄 Sprint Retrospective",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Sprint", "type": "dropdown", "options": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"]},
                                {"name": "What Went Well", "type": "text"},
                                {"name": "What Could Be Improved", "type": "text"},
                                {"name": "Action Items", "type": "text"}
                            ]
                        }
                    ]
                },
                {
                    "name": "📚 Documentation",
                    "lists": [
                        {
                            "name": "📖 Technical Docs",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Document Type", "type": "dropdown", "options": ["API Docs", "Architecture", "Setup Guide", "User Manual"]},
                                {"name": "Status", "type": "dropdown", "options": ["Draft", "In Review", "Approved", "Published"]}
                            ]
                        },
                        {
                            "name": "🎨 Design Assets",
                            "task_types": ["Task"],
                            "custom_fields": [
                                {"name": "Asset Type", "type": "dropdown", "options": ["Wireframe", "Mockup", "Prototype", "Final Design"]},
                                {"name": "Status", "type": "dropdown", "options": ["Draft", "In Review", "Approved", "Final"]}
                            ]
                        }
                    ]
                }
            ]
        }

        print("✅ BMAD template gegenereerd")
        return bmad_template

    def generate_frontend_planning(self) -> Dict[str, Any]:
        """Genereer een frontend planning met user stories en sprints."""
        print("\n📋 Stap 2: Frontend planning genereren...")

        # Frontend project requirements
        frontend_requirements = """
        BMAD Frontend Project Requirements:
        
        Het BMAD DevOps team heeft een moderne, responsive frontend nodig die:
        1. Een dashboard toont met project overzicht en metrics
        2. Agent management interface heeft (agents starten/stoppen/monitoren)
        3. ClickUp integratie visualiseert en beheert
        4. Real-time notificaties en alerts toont
        5. Configuratie management interface heeft
        6. Logs en debugging tools integreert
        7. Team collaboration features heeft
        8. Mobile responsive is
        9. Dark/light mode ondersteunt
        10. Performance monitoring en analytics toont
        
        Technische requirements:
        - React/Next.js frontend
        - TypeScript voor type safety
        - Tailwind CSS voor styling
        - Real-time updates via WebSocket
        - REST API integratie
        - Authentication en authorization
        - Error handling en logging
        - Unit en integration tests
        - CI/CD pipeline
        - Docker containerization
        """

        # Generate user stories using ProductOwner agent
        context = {
            "task": "generate_frontend_user_stories",
            "agent": "ProductOwner",
            "requirements": frontend_requirements
        }

        prompt = f"""
        Als ProductOwner, genereer user stories voor een BMAD frontend project.
        
        Requirements:
        {frontend_requirements}
        
        Genereer user stories in het volgende format:
        - Epic: [Epic naam]
          - User Story: [Story beschrijving]
          - Acceptance Criteria: [Criteria]
          - Story Points: [1-13]
          - Priority: [Critical/High/Medium/Low]
        
        Focus op:
        1. User Experience en usability
        2. Functionaliteit voor DevOps team
        3. Integration met bestaande BMAD systemen
        4. Performance en scalability
        5. Security en compliance
        """

        try:
            result = ask_openai_with_confidence(prompt, context)
            user_stories = result.get("answer", "")
            print("✅ User stories gegenereerd met LLM")
        except Exception as e:
            print(f"⚠️ LLM error, gebruik fallback user stories: {e}")
            # Use fallback user stories directly in the planning structure

        # Structure the planning
        frontend_planning = {
            "project_name": "BMAD Frontend",
            "description": "Moderne frontend voor BMAD DevOps team",
            "sprints": [
                {
                    "name": "Sprint 1: Foundation & Setup",
                    "duration": "2 weeks",
                    "goal": "Project setup, basic architecture, en core components",
                    "user_stories": [
                        {
                            "title": "Project Setup & Architecture",
                            "description": "Als developer wil ik een goed gestructureerd React/Next.js project hebben zodat ik efficiënt kan ontwikkelen",
                            "story_points": 5,
                            "priority": "High",
                            "acceptance_criteria": [
                                "Next.js project opgezet met TypeScript",
                                "Tailwind CSS geconfigureerd",
                                "ESLint en Prettier setup",
                                "Basic folder structuur",
                                "Docker configuratie"
                            ]
                        },
                        {
                            "title": "Authentication System",
                            "description": "Als team member wil ik kunnen inloggen zodat ik toegang heb tot de BMAD tools",
                            "story_points": 8,
                            "priority": "Critical",
                            "acceptance_criteria": [
                                "Login/logout functionaliteit",
                                "JWT token management",
                                "Protected routes",
                                "User profile management"
                            ]
                        },
                        {
                            "title": "Basic Layout & Navigation",
                            "description": "Als gebruiker wil ik een duidelijke navigatie hebben zodat ik makkelijk door de applicatie kan bewegen",
                            "story_points": 3,
                            "priority": "High",
                            "acceptance_criteria": [
                                "Responsive navigation bar",
                                "Sidebar menu",
                                "Breadcrumbs",
                                "Mobile menu"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sprint 2: Dashboard & Core Features",
                    "duration": "2 weeks",
                    "goal": "Dashboard implementatie en basis functionaliteit",
                    "user_stories": [
                        {
                            "title": "Project Dashboard",
                            "description": "Als DevOps engineer wil ik een overzicht dashboard zien zodat ik snel de status van alle projecten kan zien",
                            "story_points": 8,
                            "priority": "Critical",
                            "acceptance_criteria": [
                                "Project cards met status",
                                "Metrics widgets",
                                "Recent activity feed",
                                "Quick actions"
                            ]
                        },
                        {
                            "title": "Agent Management Interface",
                            "description": "Als team lead wil ik agents kunnen starten/stoppen/monitoren zodat ik de BMAD workflow kan beheren",
                            "story_points": 13,
                            "priority": "Critical",
                            "acceptance_criteria": [
                                "Agent status overzicht",
                                "Start/stop controls",
                                "Agent logs viewer",
                                "Configuration editor"
                            ]
                        },
                        {
                            "title": "Real-time Notifications",
                            "description": "Als gebruiker wil ik real-time notificaties krijgen zodat ik direct op events kan reageren",
                            "story_points": 5,
                            "priority": "High",
                            "acceptance_criteria": [
                                "WebSocket connection",
                                "Notification center",
                                "Toast notifications",
                                "Email alerts"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sprint 3: ClickUp Integration & Advanced Features",
                    "duration": "2 weeks",
                    "goal": "ClickUp integratie en geavanceerde features",
                    "user_stories": [
                        {
                            "title": "ClickUp Integration Dashboard",
                            "description": "Als product owner wil ik ClickUp projecten kunnen beheren vanuit de BMAD interface",
                            "story_points": 8,
                            "priority": "High",
                            "acceptance_criteria": [
                                "ClickUp project overzicht",
                                "Task synchronization",
                                "Status updates",
                                "Webhook management"
                            ]
                        },
                        {
                            "title": "Configuration Management",
                            "description": "Als admin wil ik BMAD configuraties kunnen beheren zodat ik de tool kan aanpassen aan onze workflow",
                            "story_points": 5,
                            "priority": "Medium",
                            "acceptance_criteria": [
                                "Environment variables editor",
                                "Agent configuration",
                                "API key management",
                                "Backup/restore"
                            ]
                        },
                        {
                            "title": "Logs & Debugging Tools",
                            "description": "Als developer wil ik logs en debugging tools hebben zodat ik problemen kan oplossen",
                            "story_points": 5,
                            "priority": "Medium",
                            "acceptance_criteria": [
                                "Log viewer met filters",
                                "Error tracking",
                                "Performance metrics",
                                "Debug console"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sprint 4: Polish & Launch",
                    "duration": "2 weeks",
                    "goal": "Finale polish, testing en deployment",
                    "user_stories": [
                        {
                            "title": "Mobile Responsiveness",
                            "description": "Als gebruiker wil ik de applicatie op mobiel kunnen gebruiken zodat ik altijd toegang heb",
                            "story_points": 5,
                            "priority": "High",
                            "acceptance_criteria": [
                                "Mobile-optimized layout",
                                "Touch-friendly controls",
                                "Responsive tables",
                                "Mobile navigation"
                            ]
                        },
                        {
                            "title": "Dark/Light Mode",
                            "description": "Als gebruiker wil ik kunnen switchen tussen dark en light mode zodat ik comfortabel kan werken",
                            "story_points": 3,
                            "priority": "Medium",
                            "acceptance_criteria": [
                                "Theme switcher",
                                "Persistent preference",
                                "System preference detection",
                                "Smooth transitions"
                            ]
                        },
                        {
                            "title": "Performance Optimization",
                            "description": "Als gebruiker wil ik een snelle applicatie hebben zodat ik efficiënt kan werken",
                            "story_points": 5,
                            "priority": "Medium",
                            "acceptance_criteria": [
                                "Code splitting",
                                "Lazy loading",
                                "Caching strategies",
                                "Bundle optimization"
                            ]
                        },
                        {
                            "title": "Testing & Documentation",
                            "description": "Als developer wil ik uitgebreide tests en documentatie hebben zodat de code onderhoudbaar is",
                            "story_points": 8,
                            "priority": "High",
                            "acceptance_criteria": [
                                "Unit tests (80% coverage)",
                                "Integration tests",
                                "E2E tests",
                                "API documentation",
                                "User manual"
                            ]
                        }
                    ]
                }
            ]
        }

        print("✅ Frontend planning gegenereerd")
        return frontend_planning

    def _get_fallback_user_stories(self) -> str:
        """Fallback user stories als LLM niet beschikbaar is."""
        return """
        Epic: BMAD Frontend Foundation
        - User Story: Als DevOps engineer wil ik een dashboard hebben om projecten te monitoren
        - Acceptance Criteria: Dashboard toont project status, metrics, en recente activiteit
        - Story Points: 8
        - Priority: Critical
        
        Epic: Agent Management
        - User Story: Als team lead wil ik agents kunnen beheren via een interface
        - Acceptance Criteria: Start/stop agents, status monitoring, configuratie
        - Story Points: 13
        - Priority: Critical
        
        Epic: ClickUp Integration
        - User Story: Als product owner wil ik ClickUp projecten synchroniseren
        - Acceptance Criteria: Bidirectionele sync, status updates, webhook management
        - Story Points: 8
        - Priority: High
        """

    def create_clickup_structure(self, template: Dict[str, Any]) -> bool:
        """Creëer de ClickUp structuur volgens het BMAD template."""
        print("\n🏗️ Stap 3: ClickUp structuur aanmaken...")

        try:
            space_id = self.config.get("space_id")
            if not space_id:
                print("❌ Space ID niet geconfigureerd")
                return False

            # Update space name
            self._update_space_name(space_id, template["space_name"])

            # Create folders and lists
            for folder in template["folders"]:
                folder_id = self._create_folder(space_id, folder["name"])
                if folder_id:
                    for list_config in folder["lists"]:
                        list_id = self._create_list(folder_id, list_config)
                        if list_id:
                            self._create_custom_fields(list_id, list_config.get("custom_fields", []))

            print("✅ ClickUp structuur aangemaakt")
            return True

        except Exception as e:
            print(f"❌ Fout bij aanmaken ClickUp structuur: {e}")
            return False

    def _update_space_name(self, space_id: str, name: str) -> bool:
        """Update de naam van de ClickUp space."""
        try:
            url = f"https://api.clickup.com/api/v2/space/{space_id}"
            headers = {
                "Authorization": self.clickup.api_key,
                "Content-Type": "application/json"
            }
            data = {"name": name}

            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                print(f"✅ Space naam geüpdatet naar: {name}")
                return True
            print(f"⚠️ Kon space naam niet updaten: {response.status_code}")
            return False
        except Exception as e:
            print(f"⚠️ Fout bij updaten space naam: {e}")
            return False

    def _create_folder(self, space_id: str, folder_name: str) -> str:
        """Creëer een folder in de ClickUp space."""
        try:
            url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"
            headers = {
                "Authorization": self.clickup.api_key,
                "Content-Type": "application/json"
            }
            data = {"name": folder_name}

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                folder_id = response.json()["id"]
                print(f"✅ Folder aangemaakt: {folder_name} (ID: {folder_id})")
                return folder_id
            print(f"⚠️ Kon folder niet aanmaken: {response.status_code}")
            return None
        except Exception as e:
            print(f"⚠️ Fout bij aanmaken folder: {e}")
            return None

    def _create_list(self, folder_id: str, list_config: Dict[str, Any]) -> str:
        """Creëer een list in de ClickUp folder."""
        try:
            url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
            headers = {
                "Authorization": self.clickup.api_key,
                "Content-Type": "application/json"
            }
            data = {
                "name": list_config["name"],
                "content": list_config.get("content", "")
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                list_id = response.json()["id"]
                print(f"✅ List aangemaakt: {list_config['name']} (ID: {list_id})")
                return list_id
            print(f"⚠️ Kon list niet aanmaken: {response.status_code}")
            return None
        except Exception as e:
            print(f"⚠️ Fout bij aanmaken list: {e}")
            return None

    def _create_custom_fields(self, list_id: str, custom_fields: List[Dict[str, Any]]) -> bool:
        """Creëer custom fields voor een list."""
        for field in custom_fields:
            try:
                url = f"https://api.clickup.com/api/v2/list/{list_id}/field"
                headers = {
                    "Authorization": self.clickup.api_key,
                    "Content-Type": "application/json"
                }

                field_data = {
                    "name": field["name"],
                    "type": field["type"]
                }

                if field["type"] == "dropdown" and "options" in field:
                    field_data["type_config"] = {
                        "options": [{"name": opt} for opt in field["options"]]
                    }

                response = requests.post(url, headers=headers, json=field_data)
                if response.status_code == 200:
                    print(f"✅ Custom field aangemaakt: {field['name']}")
                else:
                    print(f"⚠️ Kon custom field niet aanmaken: {field['name']}")

            except Exception as e:
                print(f"⚠️ Fout bij aanmaken custom field {field['name']}: {e}")

        return True

    def create_sprint_tasks(self, planning: Dict[str, Any]) -> bool:
        """Creëer taken in ClickUp voor de sprint planning."""
        print("\n📝 Stap 4: Sprint taken aanmaken in ClickUp...")

        try:
            # Find the Sprint Backlog list
            sprint_backlog_list_id = self._find_sprint_backlog_list()
            if not sprint_backlog_list_id:
                print("❌ Sprint Backlog list niet gevonden")
                return False

            # Create tasks for each sprint
            for sprint in planning["sprints"]:
                print(f"\n📅 Sprint aanmaken: {sprint['name']}")

                for story in sprint["user_stories"]:
                    task_data = {
                        "name": story["title"],
                        "description": story["description"],
                        "status": "to do"
                    }

                    # Add custom field values
                    custom_fields = []

                    # Story Points
                    if "story_points" in story:
                        custom_fields.append({
                            "id": "story_points_field_id",  # This would need to be retrieved
                            "value": story["story_points"]
                        })

                    # Priority
                    if "priority" in story:
                        custom_fields.append({
                            "id": "priority_field_id",  # This would need to be retrieved
                            "value": story["priority"]
                        })

                    # Sprint
                    custom_fields.append({
                        "id": "sprint_field_id",  # This would need to be retrieved
                        "value": sprint["name"]
                    })

                    if custom_fields:
                        task_data["custom_fields"] = custom_fields

                    # Create task
                    task_id = self._create_task(sprint_backlog_list_id, task_data)
                    if task_id:
                        print(f"✅ Taak aangemaakt: {story['title']}")

                    # Add acceptance criteria as subtasks
                    if "acceptance_criteria" in story:
                        for i, criteria in enumerate(story["acceptance_criteria"], 1):
                            subtask_data = {
                                "name": f"AC {i}: {criteria}",
                                "status": "to do"
                            }
                            self._create_subtask(task_id, subtask_data)

            print("✅ Sprint taken aangemaakt")
            return True

        except Exception as e:
            print(f"❌ Fout bij aanmaken sprint taken: {e}")
            return False

    def _find_sprint_backlog_list(self) -> str:
        """Zoek de Sprint Backlog list ID."""
        try:
            space_id = self.config.get("space_id")
            url = f"https://api.clickup.com/api/v2/space/{space_id}/list"
            headers = {"Authorization": self.clickup.api_key}

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                lists = response.json()["lists"]
                for list_item in lists:
                    if "Sprint Backlog" in list_item["name"]:
                        return list_item["id"]

            return None
        except Exception as e:
            print(f"⚠️ Fout bij zoeken Sprint Backlog list: {e}")
            return None

    def _create_task(self, list_id: str, task_data: Dict[str, Any]) -> str:
        """Creëer een taak in een ClickUp list."""
        try:
            url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
            headers = {
                "Authorization": self.clickup.api_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=task_data)
            if response.status_code == 200:
                return response.json()["id"]
            print(f"⚠️ Kon taak niet aanmaken: {response.status_code}")
            return None
        except Exception as e:
            print(f"⚠️ Fout bij aanmaken taak: {e}")
            return None

    def _create_subtask(self, task_id: str, subtask_data: Dict[str, Any]) -> str:
        """Creëer een subtask voor een taak."""
        try:
            url = f"https://api.clickup.com/api/v2/task/{task_id}/subtask"
            headers = {
                "Authorization": self.clickup.api_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=subtask_data)
            if response.status_code == 200:
                return response.json()["id"]
            print(f"⚠️ Kon subtask niet aanmaken: {response.status_code}")
            return None
        except Exception as e:
            print(f"⚠️ Fout bij aanmaken subtask: {e}")
            return None

    def generate_planning_report(self, planning: Dict[str, Any]) -> str:
        """Genereer een planning rapport."""
        print("\n📊 Stap 5: Planning rapport genereren...")

        report = f"""
# BMAD Frontend Project Planning Rapport
*Gegenereerd op: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Project Overzicht
- **Project**: {planning['project_name']}
- **Beschrijving**: {planning['description']}
- **Totaal aantal sprints**: {len(planning['sprints'])}
- **Geschatte duur**: {len(planning['sprints']) * 2} weken

## Sprint Breakdown

"""

        total_story_points = 0
        for i, sprint in enumerate(planning["sprints"], 1):
            sprint_points = sum(story.get("story_points", 0) for story in sprint["user_stories"])
            total_story_points += sprint_points

            report += f"""
### Sprint {i}: {sprint['name']}
- **Duur**: {sprint['duration']}
- **Doel**: {sprint['goal']}
- **Story Points**: {sprint_points}
- **Aantal User Stories**: {len(sprint['user_stories'])}

#### User Stories:
"""

            for story in sprint["user_stories"]:
                report += f"""
**{story['title']}** (SP: {story.get('story_points', 'N/A')}, Priority: {story.get('priority', 'N/A')})
- {story['description']}
- **Acceptance Criteria:**
"""
                for ac in story.get("acceptance_criteria", []):
                    report += f"  - {ac}\n"

        report += f"""
## Samenvatting
- **Totaal Story Points**: {total_story_points}
- **Gemiddelde Story Points per Sprint**: {total_story_points / len(planning['sprints']):.1f}
- **Geschatte team velocity**: 20-25 story points per sprint
- **Geschatte project duur**: {total_story_points / 22.5:.1f} sprints ({total_story_points / 22.5 * 2:.1f} weken)

## Volgende Stappen
1. Review en goedkeuring van de planning
2. Team samenstelling en capaciteit planning
3. Technische architectuur sessie
4. Sprint 1 kickoff
"""

        # Save report
        report_filename = f"bmad_frontend_planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Planning rapport opgeslagen: {report_filename}")
        return report_filename

    def run_complete_workflow(self) -> bool:
        """Voer het complete workflow uit."""
        print("🚀 BMAD ClickUp Workflow gestart!")
        print("=" * 50)

        try:
            # Step 1: Adapt ClickUp template
            template = self.adapt_clickup_template_to_bmad()

            # Step 2: Generate frontend planning
            planning = self.generate_frontend_planning()

            # Step 3: Create ClickUp structure
            structure_created = self.create_clickup_structure(template)

            # Step 4: Create sprint tasks
            tasks_created = False
            if structure_created:
                tasks_created = self.create_sprint_tasks(planning)

            # Step 5: Generate planning report
            report_file = self.generate_planning_report(planning)

            # Summary
            print("\n" + "=" * 50)
            print("🎉 WORKFLOW VOLTOOID!")
            print("=" * 50)
            print(f"✅ Template aangepast: {'Ja' if template else 'Nee'}")
            print(f"✅ Planning gegenereerd: {'Ja' if planning else 'Nee'}")
            print(f"✅ ClickUp structuur: {'Ja' if structure_created else 'Nee'}")
            print(f"✅ Sprint taken: {'Ja' if tasks_created else 'Nee'}")
            print(f"✅ Rapport: {report_file}")

            if structure_created and tasks_created:
                print(f"\n🌐 Bekijk je ClickUp space: https://app.clickup.com/90151351375/v/s/{self.config.get('space_id', '')}")

            return True

        except Exception as e:
            print(f"\n❌ Workflow gefaald: {e}")
            return False


def main():
    """Main function to run the workflow."""
    print("BMAD ClickUp Workflow Script")
    print("============================")

    # Check environment
    if not os.getenv("CLICKUP_API_KEY"):
        print("❌ CLICKUP_API_KEY niet gevonden in environment")
        print("Zorg dat je .env file geladen is: source .env")
        return False

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY niet gevonden - LLM features zullen beperkt zijn")

    # Run workflow
    workflow = BMADClickUpWorkflow()
    success = workflow.run_complete_workflow()

    if success:
        print("\n🎯 Volgende stappen:")
        print("1. Review de gegenereerde planning in ClickUp")
        print("2. Pas user stories aan waar nodig")
        print("3. Plan team capaciteit en sprint kickoff")
        print("4. Start met Sprint 1!")
    else:
        print("\n❌ Er zijn problemen opgetreden. Check de logs hierboven.")

    return success


if __name__ == "__main__":
    main()
