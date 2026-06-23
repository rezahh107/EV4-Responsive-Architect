#!/usr/bin/env python3
"""Run E2E-001 textual fixture contract validation.

E2E-001 is intentionally limited to repository-backed contract validation.
It does not validate live Elementor rendering, export JSON, Playwright visual
regression, accessibility pass, or production readiness.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "validation" / "e2e" / "e2e_001_manifest.json"
VALIDATOR = ROOT / "validation" / "schema_validator" / "validate_schemas.py"

REQUIRED_STAGE_ORDER = [
    "/main-pipeline-handoff-ingest",
    "/responsive-evidence-ingest-ledger",
    "/repair-option-analysis",
    "/responsive-repair-plan",
    "/accessibility-reading-order-gate",
    "/css-selector-safety-check",
]

FORBIDDEN_RELEASE_CLAIMS = {
    "live_elementor_validation",
    "export_json_validation",
    "playwright_visual_regression",
    "production_ready",
    "accessibility_passed",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return payload


def run_schema_validator() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "schema validator failed\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def validate_manifest_shape(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("schema") != "ev4-responsive-e2e-001@1.0.0":
        raise AssertionError("E2E manifest schema discriminator mismatch")
    if manifest.get("status") != "contract_validation_only":
        raise AssertionError("E2E-001 must remain contract_validation_only")

    boundary = manifest.get("validation_boundary")
    if not isinstance(boundary, dict):
        raise AssertionError("validation_boundary must be an object")
    forbidden_claims = set(boundary.get("forbidden_claims", []))
    missing_forbidden = FORBIDDEN_RELEASE_CLAIMS - forbidden_claims
    if missing_forbidden:
        raise AssertionError(f"E2E-001 boundary missing forbidden claims: {sorted(missing_forbidden)}")

    sequence = manifest.get("required_sequence")
    if not isinstance(sequence, list) or not sequence:
        raise AssertionError("required_sequence must be a non-empty array")
    return sequence


def validate_sequence(sequence: list[dict[str, Any]]) -> None:
    seen_stages: list[str] = []
    expected_indexes = list(range(1, len(sequence) + 1))
    actual_indexes = [step.get("sequence_index") for step in sequence]
    if actual_indexes != expected_indexes:
        raise AssertionError(f"sequence_index values must be contiguous: {actual_indexes}")

    for step in sequence:
        stage = step.get("stage")
        fixture_path = step.get("fixture_path")
        expected_outcome = step.get("expected_outcome")
        if stage not in REQUIRED_STAGE_ORDER:
            raise AssertionError(f"Unexpected stage in E2E-001 sequence: {stage}")
        if expected_outcome not in {"valid", "invalid"}:
            raise AssertionError(f"Invalid expected_outcome for {stage}: {expected_outcome}")
        if not isinstance(fixture_path, str) or not fixture_path:
            raise AssertionError(f"Missing fixture_path for {stage}")
        full_fixture_path = ROOT / fixture_path
        if not full_fixture_path.exists():
            raise AssertionError(f"Referenced fixture does not exist: {fixture_path}")
        if expected_outcome == "valid" and "/valid/" not in fixture_path:
            raise AssertionError(f"Valid fixture must live under validation/fixtures/valid: {fixture_path}")
        if expected_outcome == "invalid" and "/invalid/" not in fixture_path:
            raise AssertionError(f"Invalid fixture must live under validation/fixtures/invalid: {fixture_path}")
        seen_stages.append(stage)

    for required_stage in REQUIRED_STAGE_ORDER:
        if required_stage not in seen_stages:
            raise AssertionError(f"E2E-001 missing required stage: {required_stage}")


def main() -> int:
    try:
        run_schema_validator()
        manifest = load_json(MANIFEST_PATH)
        sequence = validate_manifest_shape(manifest)
        validate_sequence(sequence)
    except Exception as exc:  # noqa: BLE001 - compact CLI failure
        print(f"E2E-001 failed: {exc}", file=sys.stderr)
        return 1
    print("E2E-001 passed: textual fixture contract validation succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
