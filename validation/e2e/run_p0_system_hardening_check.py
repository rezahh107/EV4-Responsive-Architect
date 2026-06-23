#!/usr/bin/env python3
"""Run P0 system hardening regression checks."""
from __future__ import annotations

import subprocess
import sys


def run_ok(args: list[str]) -> None:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"Expected pass: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def run_fail(args: list[str], label: str) -> None:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        raise AssertionError(f"{label} unexpectedly passed: {' '.join(args)}")


def main() -> int:
    try:
        run_ok([sys.executable, "validation/schema_validator/validate_schemas.py"])
        run_ok([sys.executable, "validation/e2e/run_evidence_intake_check.py", "--skip-schema-suite"])
        run_fail([sys.executable, "validation/e2e/run_evidence_intake_check.py", "--packet", "validation/p0/invalid/evidence_intake_screenshot_computed.invalid.json", "--skip-schema-suite"], "visual evidence capability semantic gate")
    except Exception as exc:
        print(f"P0 system hardening check failed: {exc}", file=sys.stderr)
        return 1
    print("P0 system hardening check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
