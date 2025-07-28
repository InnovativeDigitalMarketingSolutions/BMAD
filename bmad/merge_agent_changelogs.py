import glob
import os
from datetime import datetime

CENTRAL_CHANGELOG = "bmad/resources/data/general/changelog.md"
AGENT_CHANGELOGS = glob.glob("bmad/agents/Agent/*/changelog.md")

def read_changelog(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()

def main():
    merged = []
    merged.append("# Centrale Changelog (samengesteld)\n")
    merged.append(f"> Laatst samengevoegd op {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    for agent_log in sorted(AGENT_CHANGELOGS):
        agent = os.path.basename(os.path.dirname(agent_log))
        content = read_changelog(agent_log)
        if content:
            merged.append(f"\n## {agent}\n")
            merged.append(content)

    with open(CENTRAL_CHANGELOG, "w", encoding="utf-8") as f:
        f.write("\n".join(merged))

    print(f"Samengevoegd changelog geschreven naar {CENTRAL_CHANGELOG}")

if __name__ == "__main__":
    main()

"""
Automatisch dagelijks mergen? Voeg deze regel toe aan je crontab (via `crontab -e`):

0 2 * * * cd /Users/yannickmacgillavry/Projects/BMAD && /usr/bin/python3 merge_agent_changelogs.py

Dit draait het script elke dag om 02:00 uur. Pas het pad aan indien nodig.
"""
