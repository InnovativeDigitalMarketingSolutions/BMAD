import glob
import os
import yaml
from datetime import datetime

AGENT_YAMLS = glob.glob("bmad/agents/Agent/*/*.yaml")
REPORT = []

for yaml_path in AGENT_YAMLS:
    with open(yaml_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            REPORT.append(f"[ERROR] {yaml_path}: YAML parse error: {e}")
            continue
    agent = os.path.basename(os.path.dirname(yaml_path))
    if not data or 'dependencies' not in data:
        REPORT.append(f"[WARN] {agent}: geen dependencies-sectie gevonden in {yaml_path}.")
        continue
    for dtype in ('templates', 'data'):
        for dep in data['dependencies'].get(dtype, []):
            dep_path = os.path.join('bmad', dep) if not dep.startswith('bmad/') else dep
            if not os.path.exists(dep_path):
                REPORT.append(f"[MISSING] {agent}: {dep_path} bestaat niet.")
            elif os.path.getsize(dep_path) < 32:
                REPORT.append(f"[EMPTY] {agent}: {dep_path} is leeg of (bijna) leeg.")
            else:
                # Check op verouderde resources (>180 dagen oud)
                mtime = os.path.getmtime(dep_path)
                age_days = (datetime.now().timestamp() - mtime) / 86400
                if age_days > 180:
                    REPORT.append(f"[STALE] {agent}: {dep_path} is ouder dan 180 dagen.")

if not REPORT:
    print("Health check: alle agent resources zijn aanwezig, niet leeg en up-to-date.")
else:
    print("Health check rapport:")
    for line in REPORT:
        print(line) 