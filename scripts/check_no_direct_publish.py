#!/usr/bin/env python3
import os
import re
import sys

AGENTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'bmad', 'agents', 'Agent')
AGENTS_DIR = os.path.abspath(AGENTS_DIR)

pattern = re.compile(r"[^\w]publish\(")

violations = []
for root, _, files in os.walk(AGENTS_DIR):
    for fname in files:
        if not fname.endswith('.py'):
            continue
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        # Ignore occurrences in comments/docstrings by a simple heuristic
        for i, line in enumerate(content.splitlines(), 1):
            if 'publish_agent_event(' in line:
                continue
            if 'publish_event(' in line:
                continue
            if pattern.search(' ' + line):
                violations.append(f"{path}:{i}:{line.strip()}")

if violations:
    print("Direct publish() calls detected in agent code (use publish_agent_event instead):", file=sys.stderr)
    for v in violations:
        print(v, file=sys.stderr)
    sys.exit(1)

print("No direct publish() calls detected in agents.")
sys.exit(0) 