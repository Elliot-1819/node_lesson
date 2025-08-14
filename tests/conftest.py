import sys
from pathlib import Path


# Ensure project root and src are on sys.path so imports work reliably
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
for p in (PROJECT_ROOT, SRC_DIR):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


