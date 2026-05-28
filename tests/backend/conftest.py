import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2] / "src" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
