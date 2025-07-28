#!/usr/bin/env python3
"""
BMAD (Business Multi-Agent DevOps) Launcher
Centrale launcher voor alle BMAD agents
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Agent directory
AGENTS_DIR = Path(__file__).parent / "agents"

# Beschikbare agents (voorbeeld, kan later uitgebreid worden)
AVAILABLE_AGENTS = {
    "product-owner": "Product Owner/product_owner.py",
    "scrummaster": "Scrummaster/scrummaster.py",
    "architect": "Architect/architect.py",
    "fullstack": "Fullstack Developer/fullstackdeveloper.py",
    "frontend": "FrontendDeveloper/frontenddeveloper.py",
    "backend": "BackendDeveloper/backenddeveloper.py",
    "ai": "Ai Developer/aideveloper.py",
    "test": "TestEngineer/testengineer.py",
    "security": "SecurityDeveloper/securitydeveloper.py",
    "uxui": "UXUIDesigner/uxuidesigner.py",
    "accessibility": "AccessibilityAgent/accessibilityagent.py",
    "documentation": "DocumentationAgent/documentationagent.py",
    "devops": "DevOpsInfra/devopsinfra.py",
    "release": "ReleaseManager/releasemanager.py",
    "strategy": "StrategiePartner/strategiepartner.py",
    "retrospective": "Retrospective/retrospective.py",
    "feedback": "FeedbackAgent/feedbackagent.py",
    "data": "DataEngineer/dataengineer.py",
    "rnd": "RnD/rnd.py"
}

def show_help():
    print("🚀 BMAD (Business Multi-Agent DevOps) Launcher")
    print("=" * 50)
    print("\nBeschikbare agents:")
    for agent_id, agent_path in AVAILABLE_AGENTS.items():
        agent_name = agent_path.split("/")[0]
        print(f"  {agent_id:15} -> {agent_name}")
    print("\nGebruik:")
    print("  python3 bmad.py <agent> <command> [args...]")
    print("  python3 bmad.py <agent> help")
    print("\nVoorbeelden:")
    print("  python3 bmad.py product-owner help")
    print("  python3 bmad.py backend build-api")
    print("  python3 bmad.py scrummaster plan-sprint")
    print("  python3 bmad.py architect design-system")

def run_agent(agent_id, *args):
    if agent_id not in AVAILABLE_AGENTS:
        print(f"❌ Agent '{agent_id}' niet gevonden!")
        print("Gebruik 'python3 bmad.py help' voor beschikbare agents.")
        return 1
    agent_path = AGENTS_DIR / AVAILABLE_AGENTS[agent_id]
    if not agent_path.exists():
        print(f"❌ Agent bestand niet gevonden: {agent_path}")
        return 1
    try:
        cmd = [sys.executable, str(agent_path)] + list(args)
        result = subprocess.run(cmd, check=False, cwd=agent_path.parent)
        return result.returncode
    except Exception as e:
        print(f"❌ Fout bij uitvoeren van agent: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="BMAD Multi-Agent DevOps Launcher", add_help=False)
    parser.add_argument("agent", nargs="?", help="Agent ID")
    parser.add_argument("command", nargs="*", help="Agent command en argumenten")
    args = parser.parse_args()
    if not args.agent:
        show_help()
        return 0
    if args.agent in ["help", "-h", "--help"]:
        show_help()
        return 0
    return run_agent(args.agent, *args.command)

if __name__ == "__main__":
    sys.exit(main())
