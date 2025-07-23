from bmad.agents.core.message_bus import publish, subscribe
from bmad.agents.core.supabase_context import save_context, get_context
from bmad.agents.core.llm_client import ask_openai
import logging

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("design_finalized", {"status": "success", "agent": "UXUIDesigner"})
        save_context("UXUIDesigner", {"design_status": "finalized"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("UXUIDesigner")
        print(f"Opgehaalde context: {context}")

def design_feedback(feedback_text):
    prompt = f"Analyseer de volgende design feedback en doe 2 concrete verbetervoorstellen:\n{feedback_text}"
    result = ask_openai(prompt)
    logging.info(f"[UXUIDesigner][LLM Design Feedback]: {result}")
    return result

def document_component(component_desc):
    prompt = f"Genereer een korte documentatie voor deze UI-component:\n{component_desc}"
    result = ask_openai(prompt)
    logging.info(f"[UXUIDesigner][LLM Component Doc]: {result}")
    return result

def on_design_feedback_requested(event):
    feedback_text = event.get("feedback_text", "")
    design_feedback(feedback_text)

def on_document_component(event):
    component_desc = event.get("component_desc", "")
    document_component(component_desc)

subscribe("design_feedback_requested", on_design_feedback_requested)
subscribe("document_component", on_document_component)
