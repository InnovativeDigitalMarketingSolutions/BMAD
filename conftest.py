import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# Ensure the tests directory is also importable as a top-level package
tests_dir = project_root / "tests"
if tests_dir.exists():
    tests_dir_str = str(tests_dir)
    if tests_dir_str not in sys.path:
        sys.path.insert(0, tests_dir_str)

# No fixtures here; this file stabilizes import path for pytest collection 