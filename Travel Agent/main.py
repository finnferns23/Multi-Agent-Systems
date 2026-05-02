"""Launcher for the Streamlit travel agent app.

Run with:
    python main.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Start Streamlit using the local app.py file."""
    app_path = Path(__file__).with_name("app.py")
    if not app_path.exists():
        print("app.py was not found next to main.py", file=sys.stderr)
        return 1
    command = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
