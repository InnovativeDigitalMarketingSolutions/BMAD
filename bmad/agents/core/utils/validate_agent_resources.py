import glob
import os

import yaml

AGENT_YAMLS = glob.glob("bmad/agents/Agent/*/*.yaml")
REPORT = []

for yaml_path in AGENT_YAMLS:
    with open(yaml_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            REPORT.append(f"[ERROR] {yaml_path}: YAML parse error: {e}")
            continue
    if not data or "dependencies" not in data:
        REPORT.append(f"[WARN] {yaml_path}: geen dependencies-sectie gevonden.")
        continue
    for dtype in ("templates", "data"):
        for dep in data["dependencies"].get(dtype, []):
            dep_path = os.path.join("bmad", dep) if not dep.startswith("bmad/") else dep
            if not os.path.exists(dep_path):
                REPORT.append(f"[MISSING] {yaml_path}: {dep_path} bestaat niet.")
            elif os.path.getsize(dep_path) < 32:
                REPORT.append(f"[EMPTY] {yaml_path}: {dep_path} is leeg of (bijna) leeg.")

if not REPORT:
    print("Alle agent dependencies zijn aanwezig en niet leeg.")
else:
    print("Resource validatie rapport:")
    for line in REPORT:
        print(line)
