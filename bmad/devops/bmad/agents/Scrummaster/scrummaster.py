#!/usr/bin/env python3
"""
Scrummaster Agent voor CoPilot AI Business Suite
Technische projectcoördinator gespecialiseerd in Agile planning en projectstructuur.
"""

import argparse
import csv
import json
import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "sprint-planning": RESOURCE_BASE / "templates/general/sprint-planning-template.md",
    "epic-breakdown": RESOURCE_BASE / "templates/general/epic-breakdown-template.md",
    "story-point-estimation": RESOURCE_BASE / "templates/general/story-point-estimation-guide.md",
    "dependency-matrix": RESOURCE_BASE / "templates/general/dependency-matrix-template.md",
    "best-practices": RESOURCE_BASE / "templates/general/best-practices.md",
    "changelog": RESOURCE_BASE / "data/general/changelog.md"
}

class ScrummasterAgent:
    def __init__(self):
        self.config = self.load_config()
        self.task_counter = {
            'epic': 1,
            'pbi': 1,
            'task': 1
        }
        
    def load_config(self):
        """Load Scrummaster configuration"""
        config_path = Path(__file__).parent / "scrummaster.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: {config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing {config_path}: {e}")
            sys.exit(1)

    def show_help(self):
        print("""
🎯 Scrummaster Agent - Available Commands
--------------------------------------------------
create-sprint         - Maak nieuwe sprint planning
breakdown-epic        - Breek epic op in PBIs en tasks
estimate-story-points - Schat story points voor tasks
identify-dependencies - Identificeer afhankelijkheden
sprint-review         - Review sprint progress
velocity-report       - Genereer velocity rapport
export-sprint         - Exporteer sprint data (csv/json)
changelog             - Toon changelog van sprintbeslissingen
test                  - Test resource completeness
help                  - Show this help

Samenwerking: Werkt nauw samen met Product Owner, Developer agents, Test Engineer en andere agents voor optimale sprintplanning en projectcoördinatie.
        """)

    def show_changelog(self):
        path = TEMPLATE_PATHS.get("changelog")
        if path and path.exists():
            logging.info(f"Changelog geladen: {path}")
            print(path.read_text())
        else:
            print("Geen changelog gevonden.")

    def test_resources(self):
        missing = []
        for key, path in TEMPLATE_PATHS.items():
            if not path.exists():
                missing.append((key, str(path)))
        if missing:
            print("[FOUT] Ontbrekende resource-bestanden:")
            for key, path in missing:
                print(f"- {key}: {path}")
        else:
            print("[OK] Alle resource-bestanden zijn aanwezig.")

    def export_sprint(self, sprint_data, format="csv"):
        """Export sprint data in specified format"""
        if format == "json":
            return json.dumps(sprint_data, indent=2)
        else:
            return self.generate_csv(sprint_data)

    # ... bestaande methodes blijven hetzelfde ...