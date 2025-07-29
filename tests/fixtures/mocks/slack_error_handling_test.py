from bmad.agents.core.slack_notify import send_slack_message

def test_slack_error_handling():
    try:
        send_slack_message("Dit zou moeten falen (ongeldige channel)", "INVALID_CHANNEL_ID", use_api=True)
    except Exception as e:
        assert "channel_not_found" in str(e)
    else:
        assert False, "Geen fout opgetreden bij ongeldig kanaal" 