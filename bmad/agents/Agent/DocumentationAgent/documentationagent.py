import glob
import logging
from bmad.agents.core.slack_notify import send_slack_message
from bmad.agents.core.llm import ask_openai
from bmad.agents.core.message_bus import subscribe

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def summarize_changelogs():
    changelogs = glob.glob("bmad/agents/Agent/*/changelog.md")
    for log_path in changelogs:
        with open(log_path, encoding="utf-8") as f:
            content = f.read(256)  # Alleen eerste 256 tekens voor samenvatting
        logging.info(f"[DocumentationAgent] Samenvatting {log_path}: {content}")
        send_slack_message(f"[DocumentationAgent] Samenvatting {log_path}: {content}")

def summarize_changelogs_llm(changelog_texts):
    prompt = f"Vat de volgende changelogs samen in maximaal 5 bullets:\n" + "\n".join(changelog_texts)
    result = ask_openai(prompt)
    logging.info(f"[DocumentationAgent][LLM Changelog-samenvatting]: {result}")
    return result

def on_summarize_changelogs(event):
    changelog_texts = event.get("changelog_texts", [])
    summarize_changelogs_llm(changelog_texts)

subscribe("summarize_changelogs", on_summarize_changelogs)
