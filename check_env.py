import os
import sys

def check_env_var(name, required=True, secret=False):
    value = os.getenv(name)
    if value:
        if secret:
            print(f"[OK] {name} is ingesteld: {'*' * 8 + value[-4:]}")
        else:
            print(f"[OK] {name} is ingesteld: {value}")
    else:
        if required:
            print(f"[FOUT] {name} is NIET ingesteld!")
        else:
            print(f"[WAARSCHUWING] {name} is niet ingesteld (optioneel)")

def main():
    print("Controle van Slack environment variables:\n")
    check_env_var("SLACK_BOT_TOKEN", required=True, secret=True)
    check_env_var("SLACK_WEBHOOK_URL", required=True)
    check_env_var("SLACK_SIGNING_SECRET", required=True, secret=True)
    print("\nControle afgerond.")

if __name__ == "__main__":
    main() 