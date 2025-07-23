from bmad.agents.core.message_bus import publish, subscribe
from bmad.agents.core.supabase_context import save_context, get_context
from bmad.agents.core.slack_notify import send_slack_message
from bmad.agents.core.llm_client import ask_openai

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("tests_passed", {"status": "success", "agent": "TestEngineer"})
        save_context("TestEngineer", {"test_status": "passed"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("TestEngineer")
        print(f"Opgehaalde context: {context}")

def notify_test_result(result):
    send_slack_message(f"[TestEngineer] Testresultaat: {result}")

def ask_llm_generate_tests(function_description):
    """Vraag de LLM om unittests te genereren voor een gegeven functieomschrijving, als JSON."""
    prompt = f"Schrijf Python unittests voor de volgende functie: {function_description}. Gebruik pytest. Geef alleen de testcases, geen uitleg."
    structured_output = '{"tests": ["test_example_1", "test_example_2"]}'
    result = ask_openai(prompt, structured_output=structured_output)
    print(f"[LLM Tests]: {result}")

def on_test_generation_requested(event):
    function_description = event.get("function_description", "Onbekende functie")
    context = event.get("context", "")
    prompt = f"Schrijf Python unittests voor de volgende functie: {function_description}. Context: {context}. Gebruik pytest."
    result = ask_openai(prompt)
    print(f"[TestEngineer][LLM Tests automatisch]: {result}")

from bmad.agents.core.message_bus import subscribe
subscribe("test_generation_requested", on_test_generation_requested)
