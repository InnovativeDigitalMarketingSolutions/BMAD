import logging
import os
import sys
import time
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager

# MCP Integration
from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

RESOURCE_BASE = Path(__file__).parent.parent / "resources"
TEMPLATE_PATHS = {
    "design-api": RESOURCE_BASE / "templates/api/design-api.md",
    "microservices": RESOURCE_BASE / "templates/architecture/microservices.md",
    "event-flow": RESOURCE_BASE / "templates/architecture/event-flow.md",
    "memory-design": RESOURCE_BASE / "templates/architecture/memory-design.md",
    "nfrs": RESOURCE_BASE / "templates/architecture/nfrs.md",
    "adr": RESOURCE_BASE / "templates/general/adr.md",
    "risk-analysis": RESOURCE_BASE / "templates/general/risk-analysis.md",
    "review": RESOURCE_BASE / "templates/general/review.md",
    "refactor": RESOURCE_BASE / "templates/general/refactor.md",
    "infra-as-code": RESOURCE_BASE / "templates/devops/infra-as-code.md",
    "release-strategy": RESOURCE_BASE / "templates/devops/release-strategy.md",
    "poc": RESOURCE_BASE / "templates/general/poc.md",
    "security-review": RESOURCE_BASE / "templates/security/security-review.md",
    "tech-stack-eval": RESOURCE_BASE / "templates/general/tech-stack-eval.md",
    "checklist": RESOURCE_BASE / "templates/general/checklist.md",
    "api-contract": RESOURCE_BASE / "templates/api/api-contract.md",
    "test-strategy": RESOURCE_BASE / "templates/testing/test-strategy.md",
    "best-practices": RESOURCE_BASE / "templates/general/best-practices.md",
    "export": RESOURCE_BASE / "data/architect/architecture-examples.md",
    "changelog": RESOURCE_BASE / "data/general/changelog.md",
}


class ArchitectAgent:
    """
    Architect Agent voor BMAD.
    Gespecialiseerd in software architectuur, API design, en system design.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.architecture_template = self.framework_manager.get_framework_template('architecture')
        except:
            self.architecture_template = None
        self.lessons_learned = []

        """Initialize Architect agent met MCP integration."""
        self.agent_name = "Architect"
        self.architecture_history = []
        self.design_patterns = []
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "design-api": self.resource_base / "templates/api/design-api.md",
            "microservices": self.resource_base / "templates/architecture/microservices.md",
            "event-flow": self.resource_base / "templates/architecture/event-flow.md",
            "memory-design": self.resource_base / "templates/architecture/memory-design.md",
            "nfrs": self.resource_base / "templates/architecture/nfrs.md",
            "adr": self.resource_base / "templates/general/adr.md",
            "risk-analysis": self.resource_base / "templates/general/risk-analysis.md",
            "review": self.resource_base / "templates/general/review.md",
            "refactor": self.resource_base / "templates/general/refactor.md",
            "infra-as-code": self.resource_base / "templates/devops/infra-as-code.md",
            "release-strategy": self.resource_base / "templates/devops/release-strategy.md",
            "poc": self.resource_base / "templates/general/poc.md",
            "security-review": self.resource_base / "templates/security/security-review.md",
            "tech-stack-eval": self.resource_base / "templates/general/tech-stack-eval.md",
            "checklist": self.resource_base / "templates/general/checklist.md",
            "api-contract": self.resource_base / "templates/api/api-contract.md",
            "test-strategy": self.resource_base / "templates/testing/test-strategy.md",
            "best-practices": self.resource_base / "templates/general/best-practices.md",
            "export": self.resource_base / "data/architect/architecture-examples.md",
            "changelog": self.resource_base / "data/general/changelog.md",
        }
        
        logging.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced architecture design capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logging.info("MCP client initialized successfully for Architect")
        except Exception as e:
            logging.warning(f"MCP initialization failed for Architect: {e}")
            self.mcp_enabled = False
    
    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced architecture design functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logging.warning("MCP not available, using local architecture design tools")
            return None
        
        try:
            # Create a context for the tool call
            context = await self.mcp_client.create_context(agent_id=self.agent_name)
            response = await self.mcp_client.call_tool(tool_name, parameters, context)
            
            if response.success:
                result = response.data
            else:
                logger.error(f"MCP tool {tool_name} failed: {response.error}")
                result = None
            logging.info(f"MCP tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logging.error(f"MCP tool {tool_name} execution failed: {e}")
            return None
    
    async def use_architecture_specific_mcp_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use architecture-specific MCP tools voor design enhancement."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Architecture analysis
            if "architecture_analysis" in self.mcp_config.custom_tools:
                analysis_result = await self.use_mcp_tool("architecture_analysis", {
                    "design": design_data.get("design", ""),
                    "patterns": design_data.get("patterns", []),
                    "analysis_type": "quality"
                })
                if analysis_result:
                    enhanced_data["architecture_analysis"] = analysis_result
            
            # Performance analysis
            if "performance_analysis" in self.mcp_config.custom_tools:
                performance_result = await self.use_mcp_tool("performance_analysis", {
                    "architecture": design_data.get("architecture", ""),
                    "metrics": design_data.get("performance_metrics", {})
                })
                if performance_result:
                    enhanced_data["performance_analysis"] = performance_result
            
            # Security review
            security_result = await self.use_mcp_tool("security_review", {
                "design": design_data.get("design", ""),
                "security_requirements": design_data.get("security_requirements", [])
            })
            if security_result:
                enhanced_data["security_review"] = security_result
            
            logging.info(f"Architecture-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logging.error(f"Error in architecture-specific MCP tools: {e}")
        
        return enhanced_data

    def show_help(self):
        print(
            """
🏗️ Architect Agent - Beschikbare commando's:

Frontend Design:
- design-frontend: Ontwerp BMAD frontend architectuur
- design-system: Maak component diagram en API koppeling
- tech-stack: Evalueer frontend tech stack

API & Backend:
- design-api: Ontwerp API endpoints en specs
- microservices: Stel microservices structuur voor
- event-flow: Ontwerp event-driven flows
- memory-design: Adviseer over memory/context architectuur

Infrastructure:
- infra-as-code: Adviseer over infra-as-code en CI/CD
- release-strategy: Adviseer over release/rollback strategieën

Quality & Security:
- nfrs: Adviseer over non-functional requirements
- security-review: Voer security review uit
- test-strategy: Stel teststrategie voor

Documentation:
- adr: Maak of update Architecture Decision Record
- best-practices: Toon architectuur best practices
- checklist: Genereer architectuur review checklist

Development & Analysis:
- risk-analysis: Voer risicoanalyse uit
- review: Review bestaande architectuur of code
- refactor: Stel refactorings voor
- poc: Begeleid proof-of-concept trajecten
- tech-stack-eval: Evalueer alternatieven in de stack
- api-contract: Genereer OpenAPI/Swagger snippet

Utilities:
- export: Exporteer architectuur artefacten
- changelog: Toon changelog van architectuurwijzigingen
- test: Test resource completeness
- list-resources: Toon alle beschikbare resource-bestanden
- help: Toon deze help

Samenwerking: Werkt nauw samen met Fullstack, Backend, DevOps, Product Owner, AI/MLOps, Test en Security agents. Output is direct bruikbaar voor devs, testers en business.
        """
        )

    # ... bestaande fallback-methodes ...
    def best_practices(self):
        path = TEMPLATE_PATHS.get("best-practices")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen best practices resource gevonden.")

    def export(self):
        path = TEMPLATE_PATHS.get("export")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen export resource gevonden.")

    def changelog(self):
        path = TEMPLATE_PATHS.get("changelog")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen changelog resource gevonden.")

    def list_resources(self):
        print("Beschikbare resource-bestanden:")
        for key, path in TEMPLATE_PATHS.items():
            print(f"- {key}: {path}")

    def test(self):
        missing = []
        for key, path in TEMPLATE_PATHS.items():
            if not path.exists():
                missing.append((key, str(path)))
        if missing:
            print("[FOUT] Ontbrekende resource-bestanden:")
            for key, path in missing:
                print(f"- {key}: {path}")
        else:
            print("[OK] Alle resource-bestanden zijn aanwezig.")

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("architecture_reviewed", {"status": "success", "agent": "Architect"})
        save_context("Architect", "review_status", {"review_status": "completed"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("Architect")
        print(f"Opgehaalde context: {context}")

    def ask_llm_api_design(self, use_case):
        """Vraag de LLM om een API-design voorstel op basis van een use case."""
        prompt = f"Ontwerp een REST API endpoint voor de volgende use case: {use_case}. Geef een korte beschrijving en een voorbeeld van de JSON input/output."
        result = ask_openai(prompt)
        print(f"[LLM API-design]: {result}")
        return result

    async def design_frontend(self):
        """Ontwerp de BMAD frontend architectuur met MCP enhancement."""
        print("🏗️ Architect Agent - Frontend Design")
        print("=" * 50)

        # Haal de user stories op van de ProductOwner
        context = get_context("ProductOwner", "frontend_stories")

        # Handle context data properly
        if isinstance(context, list) and len(context) > 0:
            stories = context[0].get("stories", "Geen user stories gevonden")
        elif isinstance(context, dict):
            stories = context.get("stories", "Geen user stories gevonden")
        else:
            stories = "Geen user stories gevonden"

        print("📋 Beschikbare user stories:")
        print(stories[:500] + "..." if len(stories) > 500 else stories)
        print()

        # Vraag gebruiker om input
        print("🤔 Wat wil je dat ik ontwerp?")
        print("1. Complete frontend architectuur")
        print("2. Component structuur en hiërarchie")
        print("3. State management strategie")
        print("4. API integratie patronen")
        print("5. Custom opdracht")

        choice = input("\nKies een optie (1-5) of beschrijf je eigen opdracht: ").strip()

        if choice == "1":
            prompt = f"""
            Ontwerp een complete frontend architectuur voor de BMAD dashboard op basis van deze user stories:
            
            {stories}
            
            Geef een gedetailleerd architectuurontwerp met:
            1. Component structuur en hiërarchie
            2. State management strategie
            3. API integratie patronen
            4. Routing en navigatie
            5. Real-time updates (WebSocket/SSE)
            6. Error handling en loading states
            7. Responsive design approach
            8. Performance optimalisaties
            
            Focus op een moderne, schaalbare architectuur die de user stories ondersteunt.
            """
        elif choice == "2":
            prompt = f"Ontwerp een gedetailleerde component structuur en hiërarchie voor de BMAD frontend op basis van: {stories}"
        elif choice == "3":
            prompt = f"Ontwerp een state management strategie voor de BMAD frontend op basis van: {stories}"
        elif choice == "4":
            prompt = f"Ontwerp API integratie patronen voor de BMAD frontend op basis van: {stories}"
        elif choice == "5":
            custom_prompt = input("Beschrijf je opdracht: ")
            prompt = f"Opdracht: {custom_prompt}\n\nContext: {stories}"
        else:
            # Gebruiker heeft direct een opdracht ingevoerd
            prompt = f"Opdracht: {choice}\n\nContext: {stories}"

        print("\n🔄 Architect aan het werk...")
        
        # Try MCP-enhanced architecture design first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("design_architecture", {
                    "prompt": prompt,
                    "architecture_type": "frontend",
                    "framework": "react/nextjs",
                    "include_performance": True,
                    "include_security": True
                })
                
                if mcp_result:
                    logging.info("MCP-enhanced architecture design completed")
                    result = mcp_result.get("architecture", "")
                    result += "\n\n[MCP Enhanced] - Architecture design enhanced with MCP tools"
                else:
                    logging.warning("MCP architecture design failed, using local design")
                    result = ask_openai(prompt)
            except Exception as e:
                logging.warning(f"MCP architecture design failed: {e}, using local design")
                result = ask_openai(prompt)
        else:
            result = ask_openai(prompt)

        print("\n🏗️ BMAD Frontend Architectuur:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Use architecture-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                design_data = {
                    "design": result,
                    "architecture_type": "frontend",
                    "patterns": ["component-based", "state-management", "api-integration"],
                    "performance_metrics": {"load_time": "target_2s", "bundle_size": "target_500kb"}
                }
                architecture_enhanced = await self.use_architecture_specific_mcp_tools(design_data)
                if architecture_enhanced:
                    print("\n🔧 Architecture Enhancements:")
                    for key, value in architecture_enhanced.items():
                        print(f"- {key}: {value}")
            except Exception as e:
                logging.warning(f"Architecture-specific MCP tools failed: {e}")

        # Sla het ontwerp op
        save_context("Architect", "frontend_architecture", {
            "timestamp": time.time(),
            "architecture": result,
            "status": "designed",
            "prompt": prompt,
            "mcp_enhanced": self.mcp_enabled
        })

        # Publiceer event
        publish("frontend_architecture_created", {
            "agent": "Architect",
            "status": "success"
        })

    async def design_system(self):
        """Maak een component diagram en API koppeling."""
        if self.mcp_enabled and self.mcp_client:
            # Try MCP first
            result = await self.use_mcp_tool("design_system", {
                "component_hierarchy": True,
                "api_integration": True,
                "state_management": True,
                "data_flow": True
            })
            if result:
                print("🏗️ BMAD Component Diagram & API Koppeling (MCP Enhanced):")
                print("=" * 60)
                print(result.get("design", result))
                print("=" * 60)
                return result
        
        # Fallback naar lokale implementatie
        return await asyncio.to_thread(self._design_system_sync)

    def _design_system_sync(self):
        """Sync fallback voor design_system."""
        prompt = """
        Maak een gedetailleerd component diagram voor de BMAD frontend met:
        
        1. Component hiërarchie:
           - Layout components (Header, Sidebar, Main, Footer)
           - Page components (Dashboard, AgentStatus, WorkflowManager, APITester)
           - Feature components (AgentCard, WorkflowCard, MetricChart, StatusIndicator)
           - Shared components (Button, Modal, Table, Chart, LoadingSpinner)
        
        2. API integratie:
           - REST API calls naar BMAD backend
           - WebSocket/SSE voor real-time updates
           - Error handling en retry logic
           - Caching strategie
        
        3. State management:
           - Global state (user, agents, workflows)
           - Local state (forms, UI state)
           - Server state (API data, real-time data)
        
        4. Data flow:
           - User interactions
           - API calls
           - Real-time updates
           - Error propagation
        
        Geef een visueel diagram in ASCII art en gedetailleerde beschrijvingen.
        """

        result = ask_openai(prompt)
        print("🏗️ BMAD Component Diagram & API Koppeling:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        return {"design": result, "status": "completed"}

    async def tech_stack(self):
        """Evalueer de frontend tech stack."""
        if self.mcp_enabled and self.mcp_client:
            # Try MCP first
            result = await self.use_mcp_tool("tech_stack_evaluation", {
                "requirements": [
                    "real-time updates",
                    "rich UI with charts",
                    "API testing interface",
                    "responsive design",
                    "type safety",
                    "developer experience",
                    "performance and scalability"
                ],
                "options": [
                    "React + TypeScript + Vite + TanStack Query + Tailwind CSS",
                    "Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS",
                    "SvelteKit + TypeScript + Tailwind CSS",
                    "Next.js + TypeScript + Tailwind CSS"
                ]
            })
            if result:
                print("🏗️ Frontend Tech Stack Evaluatie (MCP Enhanced):")
                print("=" * 60)
                print(result.get("evaluation", result))
                print("=" * 60)
                return result
        
        # Fallback naar lokale implementatie
        return await asyncio.to_thread(self._tech_stack_sync)

    def _tech_stack_sync(self):
        """Sync fallback voor tech_stack."""
        prompt = """
        Evalueer en beveel een moderne frontend tech stack aan voor de BMAD dashboard:
        
        Requirements:
        - Real-time updates (agent status, workflow progress)
        - Rich UI met charts en dashboards
        - API testing interface
        - Responsive design
        - Type safety
        - Good developer experience
        - Performance en scalability
        
        Beoordeel de volgende opties:
        1. React + TypeScript + Vite + TanStack Query + Tailwind CSS
        2. Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
        3. SvelteKit + TypeScript + Tailwind CSS
        4. Next.js + TypeScript + Tailwind CSS
        
        Geef een gedetailleerde vergelijking en aanbeveling met motivatie.
        """

        result = ask_openai(prompt)
        print("🏗️ Frontend Tech Stack Evaluatie:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        return {"evaluation": result, "status": "completed"}

    def start_conversation(self):
        """Start een interactieve conversatie met de Architect agent."""
        print("🏗️ Architect Agent - Interactieve Modus")
        print("=" * 50)
        print("Hallo! Ik ben de Architect agent. Ik kan je helpen met:")
        print("- Frontend architectuur ontwerpen")
        print("- API design en integratie")
        print("- Tech stack evaluatie")
        print("- System design en componenten")
        print("- Performance en security advies")
        print()
        print("Type 'help' voor commando's, 'quit' om te stoppen.")
        print()

        while True:
            try:
                user_input = input("🏗️ Architect > ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Tot ziens! 👋")
                    break
                if user_input.lower() == "help":
                    self.show_help()
                elif user_input.lower() == "clear":
                    # Clear screen securely
                    import subprocess
                    import platform
                    
                    if platform.system() == "Windows":
                        subprocess.run(["cls"], shell=False, check=False)
                    else:
                        subprocess.run(["clear"], shell=False, check=False)
                elif user_input:
                    # Probeer het als commando uit te voeren
                    self.run(user_input)
                else:
                    continue

            except KeyboardInterrupt:
                print("\nTot ziens! 👋")
                break
            except Exception as e:
                print(f"❌ Fout: {e}")
                print("Probeer 'help' voor beschikbare commando's.")

    async def run(self, command):
        """Run the Architect agent met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        if command == "help" or command is None:
            self.show_help()
            return
        path = self.template_paths.get(command)
        if path and path.exists():
            logging.info(f"Resource-bestand geladen: {path}")
            print(path.read_text())
            return
        # Fallback naar Python-functie
        func = getattr(self, command.replace("-", "_"), None)
        if callable(func):
            logging.info(f"Fallback Python-methode aangeroepen: {command}")
            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                func()
        else:
            logging.error(
                f"Onbekend commando of ontbrekend resource-bestand: {command}"
            )
            self.show_help()
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the Architect agent met MCP integration."""
        agent = cls()
        await agent.initialize_mcp()
        print("Architect agent started with MCP integration")


def on_api_design_requested(event):
    use_case = event.get("use_case", "Onbekende use case")
    context = event.get("context", "")
    prompt = f"Ontwerp een REST API endpoint voor de volgende use case: {use_case}. Context: {context}. Geef een korte beschrijving en een voorbeeld van de JSON input/output."
    result = ask_openai(prompt)
    logging.info(f"[Architect][LLM API-design automatisch]: {result}")
    return result

subscribe("api_design_requested", on_api_design_requested)

def on_pipeline_advice_requested(event):
    pipeline_config = event.get("pipeline_config", "")
    prompt = f"Geef een architectuuradvies voor deze CI/CD pipeline config:\n{pipeline_config}. Geef het antwoord als JSON met een korte samenvatting en 2 adviezen."
    structured_output = '{"samenvatting": "...", "adviezen": ["advies 1", "advies 2"]}'
    result = ask_openai(prompt, structured_output=structured_output)
    logging.info(f"[Architect][LLM Pipeline Advies]: {result}")
    return result

subscribe("pipeline_advice_requested", on_pipeline_advice_requested)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Architect Agent")
    parser.add_argument(
        "command", nargs="?", default="help", help="Commando voor de agent"
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactieve modus")
    args = parser.parse_args()

    agent = ArchitectAgent()

    if args.interactive:
        agent.start_conversation()
    else:
        asyncio.run(agent.run(args.command))

if __name__ == "__main__":
    main()
