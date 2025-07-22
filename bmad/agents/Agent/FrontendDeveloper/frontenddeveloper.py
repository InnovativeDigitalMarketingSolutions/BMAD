from bmad.agents.core.llm_client import ask_openai
from bmad.agents.core.message_bus import subscribe
import logging

def code_review(code_snippet):
    prompt = f"Geef een korte code review van de volgende code:\n{code_snippet}"
    result = ask_openai(prompt)
    logging.info(f"[FrontendDeveloper][LLM Code Review]: {result}")
    return result

def bug_root_cause(error_log):
    prompt = f"Analyseer deze foutmelding/log en geef een mogelijke oorzaak en oplossing:\n{error_log}"
    result = ask_openai(prompt)
    logging.info(f"[FrontendDeveloper][LLM Bug Analyse]: {result}")
    return result

def on_code_review_requested(event):
    code_snippet = event.get("code_snippet", "")
    code_review(code_snippet)

def on_bug_analysis_requested(event):
    error_log = event.get("error_log", "")
    bug_root_cause(error_log)

subscribe("code_review_requested", on_code_review_requested)
subscribe("bug_analysis_requested", on_bug_analysis_requested)
