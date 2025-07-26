#!/usr/bin/env python3
"""
BMAD Frontend Demo Generator
===========================

Dit script demonstreert hoe BMAD agents een lichte frontend kunnen bouwen.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def generate_frontend_demo():
    """Genereer een demo frontend met BMAD agents."""
    print("🚀 BMAD Frontend Demo Generator")
    print("=" * 50)
    
    try:
        # Import de benodigde modules
        sys.path.append('bmad')
        from agents.core.llm_client import ask_openai
        
        print("✅ Modules imported successfully")
        
        # Stap 1: ProductOwner genereert requirements
        print("\n1️⃣ ProductOwner - Requirements Generatie")
        print("-" * 40)
        
        requirements_prompt = """
        Genereer een lijst van 5 requirements voor een BMAD dashboard frontend.
        Focus op:
        - Agent monitoring
        - Project management
        - Real-time notifications
        - User management
        - Analytics
        
        Geef het antwoord als JSON array:
        [
            {"id": "REQ-001", "title": "Requirement Title", "description": "Detailed description", "priority": "High/Medium/Low", "category": "Monitoring/Management/Notifications/Users/Analytics"}
        ]
        """
        
        requirements_response = ask_openai(requirements_prompt, model="gpt-4o-mini")
        print("✅ Requirements gegenereerd")
        
        # Parse requirements
        try:
            start = requirements_response.find('[')
            end = requirements_response.rfind(']') + 1
            if start != -1 and end != -1:
                requirements_json = requirements_response[start:end]
                requirements = json.loads(requirements_json)
            else:
                # Fallback requirements
                requirements = [
                    {"id": "REQ-001", "title": "Agent Dashboard", "description": "Real-time monitoring van alle BMAD agents", "priority": "High", "category": "Monitoring"},
                    {"id": "REQ-002", "title": "Project Management", "description": "Interface voor project configuratie en status", "priority": "High", "category": "Management"},
                    {"id": "REQ-003", "title": "Notification Center", "description": "Real-time notificaties van agent events", "priority": "Medium", "category": "Notifications"},
                    {"id": "REQ-004", "title": "User Management", "description": "Gebruiker authenticatie en autorisatie", "priority": "Medium", "category": "Users"},
                    {"id": "REQ-005", "title": "Analytics Dashboard", "description": "Metrics en performance analytics", "priority": "Low", "category": "Analytics"}
                ]
        except:
            # Fallback requirements
            requirements = [
                {"id": "REQ-001", "title": "Agent Dashboard", "description": "Real-time monitoring van alle BMAD agents", "priority": "High", "category": "Monitoring"},
                {"id": "REQ-002", "title": "Project Management", "description": "Interface voor project configuratie en status", "priority": "High", "category": "Management"},
                {"id": "REQ-003", "title": "Notification Center", "description": "Real-time notificaties van agent events", "priority": "Medium", "category": "Notifications"},
                {"id": "REQ-004", "title": "User Management", "description": "Gebruiker authenticatie en autorisatie", "priority": "Medium", "category": "Users"},
                {"id": "REQ-005", "title": "Analytics Dashboard", "description": "Metrics en performance analytics", "priority": "Low", "category": "Analytics"}
            ]
        
        print(f"📋 {len(requirements)} requirements gegenereerd:")
        for req in requirements:
            print(f"   • {req['id']}: {req['title']} ({req['priority']})")
        
        # Stap 2: Architect genereert component structuur
        print("\n2️⃣ Architect - Component Structuur")
        print("-" * 40)
        
        architect_prompt = f"""
        Genereer een React/Next.js component structuur voor een BMAD dashboard.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Maak een component hiërarchie met:
        - Layout componenten
        - Feature componenten
        - Shared componenten
        - Styling (Tailwind CSS)
        
        Geef het antwoord als JSON:
        {{
            "components": [
                {{
                    "name": "ComponentName",
                    "type": "layout/feature/shared",
                    "description": "Component description",
                    "props": ["prop1", "prop2"],
                    "children": ["ChildComponent1", "ChildComponent2"]
                }}
            ],
            "file_structure": [
                "src/components/layout/Header.tsx",
                "src/components/features/Dashboard.tsx"
            ]
        }}
        """
        
        architect_response = ask_openai(architect_prompt, model="gpt-4o-mini")
        print("✅ Component structuur gegenereerd")
        
        # Parse architect response
        try:
            start = architect_response.find('{')
            end = architect_response.rfind('}') + 1
            if start != -1 and end != -1:
                architect_json = architect_response[start:end]
                architect_data = json.loads(architect_json)
            else:
                # Fallback architect data
                architect_data = {
                    "components": [
                        {"name": "Layout", "type": "layout", "description": "Main layout wrapper", "props": [], "children": ["Header", "Sidebar", "MainContent"]},
                        {"name": "Header", "type": "layout", "description": "Top navigation bar", "props": ["user"], "children": []},
                        {"name": "Sidebar", "type": "layout", "description": "Navigation sidebar", "props": ["menuItems"], "children": []},
                        {"name": "Dashboard", "type": "feature", "description": "Main dashboard view", "props": ["agents", "projects"], "children": ["AgentGrid", "ProjectList"]},
                        {"name": "AgentGrid", "type": "feature", "description": "Agent monitoring grid", "props": ["agents"], "children": ["AgentCard"]},
                        {"name": "AgentCard", "type": "shared", "description": "Individual agent card", "props": ["agent"], "children": []}
                    ],
                    "file_structure": [
                        "src/components/layout/Layout.tsx",
                        "src/components/layout/Header.tsx",
                        "src/components/layout/Sidebar.tsx",
                        "src/components/features/Dashboard.tsx",
                        "src/components/features/AgentGrid.tsx",
                        "src/components/shared/AgentCard.tsx"
                    ]
                }
        except:
            # Fallback architect data
            architect_data = {
                "components": [
                    {"name": "Layout", "type": "layout", "description": "Main layout wrapper", "props": [], "children": ["Header", "Sidebar", "MainContent"]},
                    {"name": "Header", "type": "layout", "description": "Top navigation bar", "props": ["user"], "children": []},
                    {"name": "Sidebar", "type": "layout", "description": "Navigation sidebar", "props": ["menuItems"], "children": []},
                    {"name": "Dashboard", "type": "feature", "description": "Main dashboard view", "props": ["agents", "projects"], "children": ["AgentGrid", "ProjectList"]},
                    {"name": "AgentGrid", "type": "feature", "description": "Agent monitoring grid", "props": ["agents"], "children": ["AgentCard"]},
                    {"name": "AgentCard", "type": "shared", "description": "Individual agent card", "props": ["agent"], "children": []}
                ],
                "file_structure": [
                    "src/components/layout/Layout.tsx",
                    "src/components/layout/Header.tsx",
                    "src/components/layout/Sidebar.tsx",
                    "src/components/features/Dashboard.tsx",
                    "src/components/features/AgentGrid.tsx",
                    "src/components/shared/AgentCard.tsx"
                ]
            }
        
        print(f"🏗️  {len(architect_data['components'])} componenten gedefinieerd:")
        for comp in architect_data['components']:
            print(f"   • {comp['name']} ({comp['type']}): {comp['description']}")
        
        # Stap 3: FrontendDeveloper genereert component code
        print("\n3️⃣ FrontendDeveloper - Component Code")
        print("-" * 40)
        
        # Genereer een voorbeeld component
        component_prompt = f"""
        Genereer React/TypeScript code voor de AgentCard component.
        
        Component info:
        {json.dumps(architect_data['components'][-1], indent=2)}
        
        Requirements:
        {json.dumps([r for r in requirements if r['category'] == 'Monitoring'], indent=2)}
        
        Gebruik:
        - TypeScript
        - Tailwind CSS
        - Modern React patterns (hooks, functional components)
        - BMAD theming (blauw/groen kleurenschema)
        
        Genereer alleen de component code, geen uitleg.
        """
        
        component_response = ask_openai(component_prompt, model="gpt-4o-mini")
        print("✅ Component code gegenereerd")
        
        # Stap 4: TestEngineer genereert test code
        print("\n4️⃣ TestEngineer - Test Code")
        print("-" * 40)
        
        test_prompt = f"""
        Genereer Jest/React Testing Library test code voor de AgentCard component.
        
        Component:
        {json.dumps(architect_data['components'][-1], indent=2)}
        
        Test requirements:
        - Component rendering
        - Props validation
        - User interactions
        - Accessibility
        - Error states
        
        Genereer alleen de test code, geen uitleg.
        """
        
        test_response = ask_openai(test_prompt, model="gpt-4o-mini")
        print("✅ Test code gegenereerd")
        
        # Stap 5: DocumentationAgent genereert documentatie
        print("\n5️⃣ DocumentationAgent - Documentatie")
        print("-" * 40)
        
        docs_prompt = f"""
        Genereer markdown documentatie voor de BMAD Frontend.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Components:
        {json.dumps(architect_data['components'], indent=2)}
        
        Maak documentatie met:
        - Project overzicht
        - Component API
        - Setup instructies
        - Usage voorbeelden
        """
        
        docs_response = ask_openai(docs_prompt, model="gpt-4o-mini")
        print("✅ Documentatie gegenereerd")
        
        # Stap 6: Sla alles op in bestanden
        print("\n6️⃣ File Generation")
        print("-" * 40)
        
        # Maak demo directory
        demo_dir = "demo_frontend"
        os.makedirs(demo_dir, exist_ok=True)
        os.makedirs(f"{demo_dir}/src/components/layout", exist_ok=True)
        os.makedirs(f"{demo_dir}/src/components/features", exist_ok=True)
        os.makedirs(f"{demo_dir}/src/components/shared", exist_ok=True)
        os.makedirs(f"{demo_dir}/src/tests", exist_ok=True)
        os.makedirs(f"{demo_dir}/docs", exist_ok=True)
        
        # Sla requirements op
        with open(f"{demo_dir}/requirements.json", "w") as f:
            json.dump(requirements, f, indent=2)
        
        # Sla architect data op
        with open(f"{demo_dir}/architecture.json", "w") as f:
            json.dump(architect_data, f, indent=2)
        
        # Sla component code op
        with open(f"{demo_dir}/src/components/shared/AgentCard.tsx", "w") as f:
            f.write(component_response)
        
        # Sla test code op
        with open(f"{demo_dir}/src/tests/AgentCard.test.tsx", "w") as f:
            f.write(test_response)
        
        # Sla documentatie op
        with open(f"{demo_dir}/docs/README.md", "w") as f:
            f.write(docs_response)
        
        # Maak package.json
        package_json = {
            "name": "bmad-frontend-demo",
            "version": "1.0.0",
            "description": "BMAD Frontend Demo - Generated by BMAD Agents",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "test": "jest",
                "lint": "eslint ."
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "typescript": "^5.0.0",
                "tailwindcss": "^3.0.0"
            },
            "devDependencies": {
                "@testing-library/react": "^14.0.0",
                "@testing-library/jest-dom": "^6.0.0",
                "jest": "^29.0.0",
                "eslint": "^8.0.0"
            }
        }
        
        with open(f"{demo_dir}/package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        print(f"✅ Demo frontend gegenereerd in: {demo_dir}/")
        print(f"📁 Bestanden:")
        print(f"   • requirements.json - {len(requirements)} requirements")
        print(f"   • architecture.json - {len(architect_data['components'])} componenten")
        print(f"   • src/components/shared/AgentCard.tsx - Component code")
        print(f"   • src/tests/AgentCard.test.tsx - Test code")
        print(f"   • docs/README.md - Documentatie")
        print(f"   • package.json - Project configuratie")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo generation error: {e}")
        return False

if __name__ == "__main__":
    success = generate_frontend_demo()
    
    if success:
        print("\n🎉 Demo frontend succesvol gegenereerd!")
        print("\n🚀 Volgende stappen:")
        print("1. cd demo_frontend")
        print("2. npm install")
        print("3. npm run dev")
        print("4. Open http://localhost:3000")
    else:
        print("\n❌ Demo generation failed") 