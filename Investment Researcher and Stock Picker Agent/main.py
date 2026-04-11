from __future__ import annotations

import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Make direct Windows/local execution work from project root:
# python src\investment_research_and_stock_picker_agent\main.py
CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parents[1]
PROJECT_ROOT = CURRENT_FILE.parents[2]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(PROJECT_ROOT / ".env")

from investment_research_and_stock_picker_agent.crew import (  # noqa: E402
    InvestmentResearchAndStockPickerAgent,
)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run() -> None:
    os.makedirs(PROJECT_ROOT / "output", exist_ok=True)
    os.makedirs(PROJECT_ROOT / "memory", exist_ok=True)

    inputs = {
        "sector": "Technology",
        "current_date": datetime.now().isoformat(),
    }

    result = InvestmentResearchAndStockPickerAgent().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL INVESTMENT DECISION ===\n")
    print(result.raw)
    print("\nArtifacts saved under ./output")


if __name__ == "__main__":
    run()
