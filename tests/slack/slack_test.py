from bmad.agents.core.slack_notify import send_slack_message
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    print("Verstuur testbericht naar Slack...")
    send_slack_message("Test van BMAD!", channel="#bmad", use_api=True)
    print("Testbericht verstuurd. Controleer de terminal-output en Slack.") 