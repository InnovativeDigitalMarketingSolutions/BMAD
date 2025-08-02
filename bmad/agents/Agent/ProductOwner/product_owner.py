#!/usr/bin/env python3
"""
Product Owner Agent voor BMAD
"""
import argparse
import logging
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from dotenv import load_dotenv

from bmad.agents.core.ai.confidence_scoring import (
    confidence_scoring,
    create_review_request,
    format_confidence_message,
)
from bmad.agents.core.ai.llm_client import ask_openai_with_confidence
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.projects.project_manager import project_manager
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager


load_dotenv()


class ProductOwnerAgent:
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        self.product_owner_template = self.framework_manager.get_template('product_owner')
        self.lessons_learned = []

        self.agent_name = "ProductOwnerAgent"
        self.story_history = []
        self.vision_history = []
        self._load_story_history()
        self._load_vision_history()

    def show_help(self):
        print("""
🎯 ProductOwner Agent - Beschikbare commando's:

  create-story [--input "requirement"]  - Maak een user story
  show-vision                           - Toon BMAD visie
  help                                  - Toon deze help

Voorbeelden:
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story --input "Dashboard voor agent monitoring"
""")

    def create_user_story(self, requirement):
        """Create a user story based on the requirement."""
        # Input validation
        if not isinstance(requirement, str):
            raise TypeError("Requirement must be a string")
        
        if not requirement or not requirement.strip():
            raise ValueError("Requirement must be a non-empty string")
        
        return create_user_story(requirement)

    def show_vision(self):
        """Show the BMAD vision."""
        return show_bmad_vision()

    def _load_story_history(self):
        """Load story history from file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "story-history.md")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse stories from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('- ') and 'Story:' in line:
                            self.story_history.append(line.strip())
        except FileNotFoundError:
            logging.info("Story history file not found, starting with empty history")
        except PermissionError as e:
            logging.error(f"Permission denied accessing story history: {e}")
        except UnicodeDecodeError as e:
            logging.error(f"Unicode decode error in story history: {e}")
        except OSError as e:
            logging.error(f"OS error loading story history: {e}")
        except Exception as e:
            logging.warning(f"Could not load story history: {e}")

    def _save_story_history(self):
        """Save story history to file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "story-history.md")
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("# Story History\n\n")
                for story in self.story_history:
                    f.write(f"{story}\n")
        except PermissionError as e:
            logging.error(f"Permission denied saving story history: {e}")
        except OSError as e:
            logging.error(f"OS error saving story history: {e}")
        except Exception as e:
            logging.error(f"Could not save story history: {e}")

    def _load_vision_history(self):
        """Load vision history from file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "vision-history.md")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse vision entries from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('- ') and 'Vision:' in line:
                            self.vision_history.append(line.strip())
        except FileNotFoundError:
            logging.info("Vision history file not found, starting with empty history")
        except PermissionError as e:
            logging.error(f"Permission denied accessing vision history: {e}")
        except UnicodeDecodeError as e:
            logging.error(f"Unicode decode error in vision history: {e}")
        except OSError as e:
            logging.error(f"OS error loading vision history: {e}")
        except Exception as e:
            logging.warning(f"Could not load vision history: {e}")

    def _save_vision_history(self):
        """Save vision history to file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "vision-history.md")
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("# Vision History\n\n")
                for vision in self.vision_history:
                    f.write(f"{vision}\n")
        except PermissionError as e:
            logging.error(f"Permission denied saving vision history: {e}")
        except OSError as e:
            logging.error(f"OS error saving vision history: {e}")
        except Exception as e:
            logging.error(f"Could not save vision history: {e}")

    def show_resource(self, resource_type="best_practices"):
        """Display available resources."""
        # Input validation
        if not isinstance(resource_type, str):
            print("Error: resource_type must be a string")
            return
        
        if not resource_type.strip():
            print("Error: resource_type cannot be empty")
            return
        
        try:
            resource_file = os.path.join(os.path.dirname(__file__), f"{resource_type}.md")
            if os.path.exists(resource_file):
                with open(resource_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print(f"Resource '{resource_type}' not found. Available: best_practices, templates")
        except FileNotFoundError:
            print(f"Resource file not found: {resource_type}")
        except PermissionError as e:
            print(f"Permission denied accessing resource {resource_type}: {e}")
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in resource {resource_type}: {e}")
        except Exception as e:
            logging.error(f"Error reading resource {resource_type}: {e}")

    def show_story_history(self):
        """Display story history."""
        if self.story_history:
            print("📚 Story History:")
            for i, story in enumerate(self.story_history, 1):
                print(f"{i}. {story}")
        else:
            print("No story history available.")

    def show_vision_history(self):
        """Display vision history."""
        if self.vision_history:
            print("👁️ Vision History:")
            for i, vision in enumerate(self.vision_history, 1):
                print(f"{i}. {vision}")
        else:
            print("No vision history available.")

    def export_report(self, format_type, data):
        """Export reports in various formats."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        
        if format_type not in ["md", "json"]:
            raise ValueError("format_type must be one of: md, json")
        
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"productowner_report_{timestamp}"
        
        try:
            if format_type == "md":
                filename += ".md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("# Product Owner Report\n\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Data: {data}\n")
            elif format_type == "json":
                filename += ".json"
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                print(f"Unsupported format: {format_type}")
                return
            
            print(f"Report export saved to: {filename}")
        except PermissionError as e:
            logging.error(f"Permission denied saving report: {e}")
        except OSError as e:
            logging.error(f"OS error saving report: {e}")
        except Exception as e:
            logging.error(f"Error saving report: {e}")

    def run(self):
        """Main event loop for the agent."""
        print("🎯 ProductOwner Agent is running...")
        print("Listening for events: user_story_requested, feedback_sentiment_analyzed, feature_planned")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 ProductOwner Agent stopped.")

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            publish("backlog_updated", {"status": "success", "agent": "ProductOwner"})
            save_context("ProductOwner", "status", {"backlog_status": "updated"})
            print("Event gepubliceerd en context opgeslagen.")
            context = get_context("ProductOwner")
            print(f"Opgehaalde context: {context}")
        except Exception as e:
            logging.error(f"Collaboration example failed: {e}")
            print(f"❌ Error in collaboration: {e}")


def main():
    parser = argparse.ArgumentParser(description="Product Owner Agent")
    parser.add_argument(
        "command", nargs="?", default="help", help="Commando voor de agent"
    )
    parser.add_argument("--input", "-i", help="Input voor het commando")
    args = parser.parse_args()

    if args.command == "help":
        show_help()
    elif args.command == "create-story":
        if args.input:
            create_user_story(args.input)
        else:
            create_bmad_frontend_story()
    elif args.command == "show-vision":
        show_bmad_vision()
    elif args.command == "collaborate":
        collaborate_example()
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)
        return

def show_help():
    print("""
🎯 ProductOwner Agent - Beschikbare commando's:

  create-story [--input "requirement"]  - Maak een user story
  show-vision                           - Toon BMAD visie
  help                                  - Toon deze help

Voorbeelden:
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story --input "Dashboard voor agent monitoring"
""")

def create_bmad_frontend_story():
    """Maak user stories voor het huidige project."""
    # Haal project context op
    project_context = project_manager.get_project_context()

    if not project_context:
        print("❌ Geen project geladen! Laad eerst een project met:")
        print("   python -m bmad.projects.cli load <project_name>")
        return

    project_name = project_context["project_name"]
    project_type = project_context["config"]["project_type"]
    requirements = project_context["requirements"]

    print(f"🎯 ProductOwner - User Stories voor '{project_name}' ({project_type})")
    print("=" * 60)

    # Toon huidige requirements
    if requirements:
        print("📋 Huidige Requirements:")
        for category, reqs in requirements.items():
            if reqs:
                print(f"  {category}:")
                for req in reqs:
                    print(f"    - {req['description']}")
        print()

    # Vraag gebruiker om input
    print("🤔 Wat wil je dat ik doe?")
    print("1. Genereer user stories voor alle requirements")
    print("2. Genereer user stories voor specifieke categorie")
    print("3. Genereer user stories voor nieuwe feature")
    print("4. Review en verbeter bestaande user stories")

    choice = input("\nKies een optie (1-4) of beschrijf je eigen opdracht: ").strip()

    if choice == "1":
        # Genereer user stories voor alle requirements
        all_requirements = []
        for category, reqs in requirements.items():
            for req in reqs:
                all_requirements.append(f"{category}: {req['description']}")

        requirements_text = "\n".join(all_requirements) if all_requirements else "Geen requirements gedefinieerd"

        prompt = f"""
        Schrijf gedetailleerde user stories in Gherkin-formaat voor het project '{project_name}' ({project_type}).
        
        Requirements:
        {requirements_text}
        
        Geef voor elke requirement een user story met acceptatiecriteria.
        Focus op functionaliteit die de gebruiker nodig heeft.
        """

    elif choice == "2":
        category = input("Welke categorie? (functional/non_functional/technical): ").strip()
        reqs = requirements.get(category, [])
        if reqs:
            requirements_text = "\n".join([req["description"] for req in reqs])
            prompt = f"""
            Schrijf user stories voor de {category} requirements van project '{project_name}':
            
            {requirements_text}
            
            Geef voor elke requirement een user story met acceptatiecriteria.
            """
        else:
            print(f"❌ Geen requirements gevonden in categorie '{category}'")
            return

    elif choice == "3":
        feature = input("Beschrijf de nieuwe feature: ").strip()
        prompt = f"""
        Schrijf user stories voor de nieuwe feature van project '{project_name}':
        
        Feature: {feature}
        
        Geef 3-5 user stories met acceptatiecriteria voor deze feature.
        """

    elif choice == "4":
        # Review bestaande user stories
        existing_stories = project_context.get("user_stories", [])
        if existing_stories:
            stories_text = "\n".join([f"{s['id']}. {s['story']}" for s in existing_stories])
            prompt = f"""
            Review en verbeter de bestaande user stories voor project '{project_name}':
            
            {stories_text}
            
            Geef verbeterde versies van deze user stories met betere acceptatiecriteria.
            """
        else:
            print("❌ Geen bestaande user stories gevonden")
            return

    else:
        # Custom opdracht
        prompt = f"""
        Opdracht: {choice}
        
        Project: {project_name} ({project_type})
        Requirements: {requirements}
        
        Schrijf user stories op basis van deze opdracht.
        """

    print("\n🔄 ProductOwner aan het werk...")
    result = ask_openai_with_confidence(prompt)

    print("\n🎯 User Stories:")
    print("=" * 50)
    print(result["answer"])
    print("=" * 50)

    # Sla de user stories op in project context
    project_manager.add_user_story(result["answer"], "high")

    # Publiceer event voor andere agents
    publish("user_stories_created", {
        "agent": "ProductOwner",
        "project": project_name,
        "status": "success"
    })

def create_user_story(requirement):
    """Maak een user story op basis van een specifieke requirement."""
    # Input validation
    if not isinstance(requirement, str):
        raise TypeError("Requirement must be a string")
    
    if not requirement or not requirement.strip():
        raise ValueError("Requirement must be a non-empty string")
    
    prompt = f"""
    Schrijf een user story in Gherkin-formaat voor de volgende requirement:
    
    {requirement}
    
    Geef een duidelijke user story met acceptatiecriteria.
    """

    # Context voor de LLM
    context = {
        "task": "create_user_story",
        "agent": "ProductOwner",
        "requirement": requirement
    }

    try:
        result = ask_openai_with_confidence(prompt, context=context)
        print(f"🎯 User Story voor: {requirement}")
        print("=" * 50)
        print(result["answer"])
        print("=" * 50)
        return result
    except Exception as e:
        logging.error(f"Failed to create user story: {e}")
        error_result = {"answer": f"Error creating user story: {e}", "confidence": 0.0}
        print(f"❌ Error: {e}")
        return error_result

def show_bmad_vision():
    """Toon de BMAD visie en strategie."""
    vision = """
    🚀 BMAD (Business Multi-Agent DevOps) Visie
    
    BMAD is een innovatief systeem dat AI-agents inzet voor DevOps en software development.
    
    Kernprincipes:
    - Multi-agent samenwerking
    - Human-in-the-loop workflows
    - Event-driven architectuur
    - Continuous feedback loops
    
    Doelstellingen:
    - Automatisering van repetitieve taken
    - Verbeterde code kwaliteit
    - Snellere development cycles
    - Betere team samenwerking
    
    Frontend Doel:
    - Centraal dashboard voor agent monitoring
    - Intuïtieve workflow management
    - Real-time insights en metrics
    - Eenvoudige API testing en debugging
    """

    print(vision)


def collaborate_example():
    """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
    publish("backlog_updated", {"status": "success", "agent": "ProductOwner"})
    save_context("ProductOwner", "status", {"backlog_status": "updated"})
    print("Event gepubliceerd en context opgeslagen.")
    context = get_context("ProductOwner")
    print(f"Opgehaalde context: {context}")


def ask_llm_user_story(requirement):
    """Vraag de LLM om een user story te genereren met confidence scoring."""
    # Input validation
    if not isinstance(requirement, str):
        raise TypeError("Requirement must be a string")
    
    if not requirement or not requirement.strip():
        raise ValueError("Requirement must be a non-empty string")
    
    prompt = f"""
    Schrijf een user story in Gherkin-formaat voor de volgende requirement:
    
    Requirement: {requirement}
    
    Geef een user story met:
    - Feature beschrijving
    - Scenario's met Given/When/Then
    - Acceptatiecriteria
    - Prioriteit (High/Medium/Low)
    """

    # Context voor confidence scoring
    context = {
        "task": "create_user_story",
        "agent": "ProductOwner",
        "requirement": requirement
    }

    try:
        # Gebruik confidence scoring
        result = ask_openai_with_confidence(prompt, context)

        # Enhance output met confidence scoring
        enhanced_output = confidence_scoring.enhance_agent_output(
            output=result["answer"],
            agent_name="ProductOwner",
            task_type="create_user_story",
            context=context
        )

        # Log confidence info
        print(f"🎯 Confidence Score: {enhanced_output['confidence']:.2f} ({enhanced_output['review_level']})")

        # Als review vereist is, maak review request
        if enhanced_output["review_required"]:
            create_review_request(enhanced_output)
            print("🔍 Review vereist - User story wordt ter goedkeuring voorgelegd")
            print(format_confidence_message(enhanced_output))

            # TODO: Stuur review request naar Slack of andere kanalen
            # publish("review_requested", review_request)

        return enhanced_output["output"]
    except Exception as e:
        logging.error(f"Failed to generate user story with LLM: {e}")
        error_output = f"Error generating user story: {e}"
        print(f"❌ Error: {e}")
        return error_output


def on_user_story_requested(event):
    """Handle user story requested event."""
    # Input validation
    if not isinstance(event, dict):
        logging.warning("Invalid event type for user story requested event")
        return
    
    print("📝 User story requested event received")
    requirement = event.get('requirement', 'Default requirement')
    story = ask_llm_user_story(requirement)
    print(f"Generated story: {story}")

def on_feedback_sentiment_analyzed(event):
    """Handle feedback sentiment analyzed event."""
    # Input validation
    if not isinstance(event, dict):
        logging.warning("Invalid event type for feedback sentiment analyzed event")
        return
    
    sentiment = event.get('sentiment', 'neutral')
    if sentiment == 'negative':
        print("😔 Negative feedback detected - prioritizing improvements")
        # Trigger improvement workflow
    else:
        print("😊 Positive feedback - continuing current direction")

def handle_feature_planned(event):
    """Handle feature planned event."""
    # Input validation
    if not isinstance(event, dict):
        logging.warning("Invalid event type for feature planned event")
        return
    
    feature = event.get('feature', 'Unknown feature')
    print(f"🎯 Feature planned: {feature}")
    time.sleep(1)  # Simulate processing
    publish("feature_prioritized", {"feature": feature, "priority": "high"})


if __name__ == "__main__":
    main()
    subscribe("user_story_requested", on_user_story_requested)
    subscribe("feedback_sentiment_analyzed", on_feedback_sentiment_analyzed)
    subscribe("feature_planned", handle_feature_planned)
