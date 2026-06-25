#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "validation" / "e2e" / "run_submitted_packet_issue_reference_check.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
