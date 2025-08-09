#!/usr/bin/env python3
import sys
from pathlib import Path
import re

AGENTS_DIR = Path(__file__).resolve().parents[1] / "bmad" / "agents" / "Agent"
PATTERN = re.compile(r"\bpublish\(")

ALLOWLIST = {
    # Legacy test-compat publish calls (best-effort) toegestaan
    # Relatieve paden tov project root
    "bmad/agents/Agent/Architect/architect.py",
    "bmad/agents/Agent/DocumentationAgent/documentationagent.py",
    "bmad/agents/Agent/ProductOwner/product_owner.py",
}

def main() -> int:
    failed = False
    project_root = Path(__file__).resolve().parents[1]
    for py in AGENTS_DIR.rglob("*.py"):
        rel = str(py.relative_to(project_root))
        text = py.read_text(encoding="utf-8", errors="ignore")
        if PATTERN.search(text):
            # Heuristiek: als bestand zelf een wrapper `publish_agent_event` bevat is directe publish verdacht
            if rel in ALLOWLIST:
                continue
            if "def publish_agent_event(" in text:
                print(f"Direct publish() found in {py}")
                failed = True
    if failed:
        print("Found direct publish() calls in agents. Use publish_agent_event wrapper.")
        return 1
    print("No direct publish() calls found in agents.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 