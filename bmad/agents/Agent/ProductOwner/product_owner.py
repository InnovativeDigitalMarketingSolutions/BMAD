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
    args = parser.parse_args()
    if args.command == "help":
        print("Beschikbare commando's: help, create-story, show-vision, ...")
    else:
        print(f"Commando '{args.command}' wordt uitgevoerd (stub)")


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
