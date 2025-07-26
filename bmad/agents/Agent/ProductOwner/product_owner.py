#!/usr/bin/env python3
"""
Product Owner Agent voor BMAD
"""
import argparse
import logging
import time
from bmad.agents.core.message_bus import publish, subscribe
from bmad.agents.core.supabase_context import save_context, get_context
from bmad.agents.core.llm_client import ask_openai
from dotenv import load_dotenv
load_dotenv()


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
    else:
        print(f"Commando '{args.command}' wordt uitgevoerd (stub)")

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
    """Maak user stories voor de BMAD frontend."""
    requirement = """
    BMAD Frontend Dashboard Requirements:
    
    1. Agent Status Monitoring
       - Real-time status van alle agents
       - Agent logs en error handling
       - Agent performance metrics
    
    2. Workflow Management
       - Workflows starten/bekijken
       - Workflow status tracking
       - Human-in-the-loop (HITL) alerts
    
    3. API Testing Interface
       - Swagger UI integratie
       - API endpoint testing
       - Response logging
    
    4. Slack Integration Status
       - Bot status monitoring
       - Channel membership
       - Message history
    
    5. Metrics Dashboard
       - Workflow metrics
       - Agent performance
       - System health
    
    6. Configuration Management
       - Environment variables
       - Agent settings
       - System configuration
    """
    
    prompt = f"""
    Schrijf gedetailleerde user stories in Gherkin-formaat voor de volgende BMAD frontend requirements:
    
    {requirement}
    
    Geef voor elk onderdeel (1-6) een user story met acceptatiecriteria.
    Focus op functionaliteit die het team nodig heeft om BMAD effectief te gebruiken.
    """
    
    result = ask_openai(prompt)
    print("🎯 BMAD Frontend User Stories:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # Sla de user stories op in context
    save_context("ProductOwner", "frontend_stories", {
        "timestamp": time.time(),
        "stories": result,
        "status": "created"
    })
    
    # Publiceer event voor andere agents
    publish("frontend_stories_created", {
        "agent": "ProductOwner",
        "status": "success",
        "stories_count": 6
    })

def create_user_story(requirement):
    """Maak een user story op basis van een specifieke requirement."""
    prompt = f"""
    Schrijf een user story in Gherkin-formaat voor de volgende requirement:
    
    {requirement}
    
    Geef een duidelijke user story met acceptatiecriteria.
    """
    
    result = ask_openai(prompt)
    print(f"🎯 User Story voor: {requirement}")
    print("=" * 50)
    print(result)
    print("=" * 50)

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
    save_context("ProductOwner", {"backlog_status": "updated"})
    print("Event gepubliceerd en context opgeslagen.")
    context = get_context("ProductOwner")
    print(f"Opgehaalde context: {context}")


def ask_llm_user_story(requirement):
    """Vraag de LLM om een user story te genereren op basis van een requirement, als JSON."""
    prompt = f"Schrijf een user story in Gherkin-formaat voor de volgende requirement: {requirement}. Geef alleen de user story en acceptatiecriteria, geen uitleg."
    structured_output = '{"user_story": "Als ... wil ik ... zodat ...", "acceptatiecriteria": ["...", "..."]}'
    result = ask_openai(prompt, structured_output=structured_output)
    print(f"[LLM User Story]: {result}")


def on_user_story_requested(event):
    requirement = event.get("requirement", "Onbekende requirement")
    context = event.get("context", "")
    prompt = f"Schrijf een user story in Gherkin-formaat voor de volgende requirement: {requirement}. Context: {context}."
    result = ask_openai(prompt)
    print(f"[ProductOwner][LLM User Story automatisch]: {result}")


def on_feedback_sentiment_analyzed(event):
    sentiment = event.get("sentiment", "")
    motivatie = event.get("motivatie", "")
    feedback = event.get("feedback", "")
    if sentiment == "negatief":
        prompt = f"Schrijf een user story voor een verbetering op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen de user story en acceptatiecriteria, geen uitleg."
        structured_output = '{"user_story": "Als ... wil ik ... zodat ...", "acceptatiecriteria": ["...", "..."]}'
        result = ask_openai(prompt, structured_output=structured_output)
        print(f"[ProductOwner][LLM Verbeteruserstory]: {result}")


def handle_feature_planned(event):
    logging.info("[ProductOwner] Feature gepland, taken worden toegewezen...")
    # Simuleer taaktoewijzing
    time.sleep(1)
    publish("tasks_assigned", {"desc": "Taken toegewezen"})
    logging.info("[ProductOwner] Taken toegewezen, tasks_assigned gepubliceerd.")


if __name__ == "__main__":
    main()
    subscribe("user_story_requested", on_user_story_requested)
    subscribe("feedback_sentiment_analyzed", on_feedback_sentiment_analyzed)
    subscribe("feature_planned", handle_feature_planned)
