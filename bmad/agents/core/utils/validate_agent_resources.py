import glob
import os

import yaml

AGENT_YAMLS = glob.glob("bmad/agents/Agent/*/*.yaml")
REPORT = []

def validate_agent_resources(agent_name: str = None) -> dict:
    """
    Validate agent resources and dependencies.
    
    :param agent_name: Optional agent name to validate specific agent
    :return: Dictionary with validation results
    """
    global REPORT
    REPORT = []
    
    yaml_files = AGENT_YAMLS
    if agent_name:
        yaml_files = [f for f in AGENT_YAMLS if agent_name.lower() in f.lower()]
    
    for yaml_path in yaml_files:
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

    result = {
        "status": "success" if not REPORT else "issues_found",
        "missing_files": [line for line in REPORT if "[MISSING]" in line],
        "missing_directories": [line for line in REPORT if "[EMPTY]" in line],
        "warnings": [line for line in REPORT if "[WARN]" in line],
        "errors": [line for line in REPORT if "[ERROR]" in line],
        "total_issues": len(REPORT)
    }
    
    if not REPORT:
        print("Alle agent dependencies zijn aanwezig en niet leeg.")
    else:
        print("Resource validatie rapport:")
        for line in REPORT:
            print(line)
    
    return result

# Run validation on import for backward compatibility
if __name__ != "__main__":
    validate_agent_resources()
