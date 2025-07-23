import logging
from bmad.agents.core.message_bus import publish, get_events, clear_events
from bmad.agents.core.supabase_context import save_context, get_context

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def test_context_sharing():
    logging.info("[TEST] Start contextdeling test tussen AiDeveloper en FullstackDeveloper")
    clear_events()

    # AiDeveloper publiceert event en slaat context op
    try:
        publish("ai_pipeline_ready", {"status": "success", "agent": "AiDeveloper", "version": 1})
        save_context(
            agent_name="AiDeveloper",
            context_type="pipeline_status",
            payload={"pipeline_status": "ready", "version": 1},
            updated_by="AiDeveloper"
        )
        logging.info("[AiDeveloper] Event gepubliceerd en context opgeslagen.")
    except Exception as e:
        logging.error(f"[AiDeveloper] Fout bij publiceren/saven: {e}")

    # FullstackDeveloper leest context van AiDeveloper
    try:
        context = get_context("AiDeveloper", context_type="pipeline_status")
        if context:
            logging.info(f"[FullstackDeveloper] Opgehaalde context van AiDeveloper: {context}")
        else:
            logging.warning("[FullstackDeveloper] Geen context gevonden voor AiDeveloper.")
    except Exception as e:
        logging.error(f"[FullstackDeveloper] Fout bij ophalen context: {e}")

    # FullstackDeveloper leest events
    try:
        events = get_events("ai_pipeline_ready")
        if events:
            logging.info(f"[FullstackDeveloper] Opgehaalde events: {events}")
        else:
            logging.warning("[FullstackDeveloper] Geen events gevonden van AiDeveloper.")
    except Exception as e:
        logging.error(f"[FullstackDeveloper] Fout bij ophalen events: {e}")

if __name__ == "__main__":
    test_context_sharing() 