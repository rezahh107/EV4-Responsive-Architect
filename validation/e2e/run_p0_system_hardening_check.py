#!/usr/bin/env python3
"""Run P0 system hardening regression checks.

This runner verifies that P0 invalid fixtures are schema-valid but semantically
invalid for the intended gate. It prevents fake coverage where a fixture fails
only because of an unrelated unknown-field sentinel.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.schema_validator.validate_schemas import (  # noqa: E402
    SemanticValidationError,
    load_json,
    semantic_validate_payload,
    validate_schema_files,
)


SEMANTIC_INVALID_CASES = {
    "validation/fixtures/invalid/conflict_resolution.unresolved_continue.invalid.json":
        "unresolved_blocking conflict must use block_downstream_until_resolved",
    "validation/fixtures/invalid/responsive_failure_map.unresolved_unknown.invalid.json":
        "repair-critical unresolved unknowns must set map_verdict.status=blocked_by_unknowns",
    "validation/fixtures/invalid/responsive_final_audit.blocking_allowed.invalid.json":
        "handoff_allowed=true must not have blocking_reasons",
    "validation/fixtures/invalid/handoff_ingest_decision.invalid_continue.invalid.json":
        "blocked handoff status must set downstream_allowed=false",
    "validation/fixtures/invalid/fast_path_eligibility.false_eligible.invalid.json":
        "eligible fast-path requires every fast-path criterion to be safe",
}


def run_ok(args: list[str]) -> None:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"Expected pass: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def run_fail(args: list[str], label: str) -> None:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        raise AssertionError(f"{label} unexpectedly passed: {' '.join(args)}")


def assert_schema_valid_semantic_invalid(path: str, expected_message: str) -> None:
    schemas = validate_schema_files()
    fixture_path = ROOT / path
    payload = load_json(fixture_path)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must be a JSON object")

    payload = dict(payload)
    schema_file = payload.pop("$schema_file", None)
    if not schema_file:
        raise AssertionError(f"{path} is missing $schema_file")
    if schema_file not in schemas:
        raise AssertionError(f"{path} references missing schema {schema_file}")

    schema_errors = sorted(
        Draft202012Validator(schemas[schema_file]).iter_errors(payload),
        key=lambda e: [str(p) for p in e.path],
    )
    if schema_errors:
        raise AssertionError(
            f"{path} must be schema-valid so the intended semantic gate is tested. "
            f"First schema error: {schema_errors[0].message}"
        )

    try:
        semantic_validate_payload(payload)
    except SemanticValidationError as exc:
        message = str(exc)
        if expected_message not in message:
            raise AssertionError(
                f"{path} failed for the wrong semantic reason.\n"
                f"Expected substring: {expected_message}\n"
                f"Actual: {message}"
            ) from exc
        return

    raise AssertionError(f"{path} unexpectedly passed semantic validation")


def main() -> int:
    try:
        run_ok([sys.executable, "validation/schema_validator/validate_schemas.py"])
        run_ok([sys.executable, "validation/e2e/run_evidence_intake_check.py", "--skip-schema-suite"])
        run_fail(
            [
                sys.executable,
                "validation/e2e/run_evidence_intake_check.py",
                "--packet",
                "validation/p0/invalid/evidence_intake_screenshot_computed.invalid.json",
                "--skip-schema-suite",
            ],
            "visual evidence capability semantic gate",
        )
        for path, expected_message in SEMANTIC_INVALID_CASES.items():
            assert_schema_valid_semantic_invalid(path, expected_message)
    except Exception as exc:
        print(f"P0 system hardening check failed: {exc}", file=sys.stderr)
        return 1
    print("P0 system hardening check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
