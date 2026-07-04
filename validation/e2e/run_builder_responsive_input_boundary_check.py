#!/usr/bin/env python3
"""Validate the Builder to Responsive input boundary schema and fixtures.

This check covers repository-controlled schema/fixture contracts only. Passing it
means a Builder handoff packet is structurally eligible for Responsive intake;
it does not create submitted evidence, run a pilot, or prove responsive
correctness.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "ev4-builder-responsive-input.schema.json"
VALID_FIXTURES = (ROOT / "validation" / "fixtures" / "valid" / "builder_responsive_input.valid.json",)
INVALID_FIXTURES = (
    ROOT
    / "validation"
    / "fixtures"
    / "invalid"
    / "builder_responsive_input_missing_mobile_evidence.invalid.json",
    ROOT
    / "validation"
    / "fixtures"
    / "invalid"
    / "builder_responsive_input_blocked_project_gate_allows_intake.invalid.json",
    ROOT
    / "validation"
    / "fixtures"
    / "invalid"
    / "builder_responsive_input_blocked_viewport_allows_intake.invalid.json",
    ROOT
    / "validation"
    / "fixtures"
    / "invalid"
    / "builder_responsive_input_forbidden_claim_subset.invalid.json",
)
REQUIRED_FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "pixel_perfect",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "responsive_correctness_validated",
    "ci_success_as_frontend_evidence",
}
CANONICAL_BOUNDARY = "input eligibility only; not responsive correctness evidence"


def _load_json(path: Path) -> object:
    if not path.exists():
        raise AssertionError(f"missing required fixture or schema: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_valid_fixture(data: dict[str, object], path: Path) -> None:
    decision = data.get("responsive_intake_decision")
    if not isinstance(decision, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} missing responsive_intake_decision object")
    if decision.get("claim_boundary") != CANONICAL_BOUNDARY:
        raise AssertionError(f"{path.relative_to(ROOT)} has non-canonical claim boundary")
    if decision.get("intake_allowed") is not True:
        raise AssertionError(f"{path.relative_to(ROOT)} valid fixture must exercise allowed intake")

    project_gate = data.get("project_gate_ref")
    if not isinstance(project_gate, dict) or project_gate.get("gate_status") != "verified":
        raise AssertionError(f"{path.relative_to(ROOT)} allowed intake must use a verified project gate")

    viewport_evidence = data.get("viewport_evidence")
    if not isinstance(viewport_evidence, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} missing viewport_evidence object")
    for viewport in ("desktop", "tablet", "mobile"):
        evidence = viewport_evidence.get(viewport)
        if not isinstance(evidence, dict) or evidence.get("evidence_status") != "provided":
            raise AssertionError(f"{path.relative_to(ROOT)} allowed intake must provide {viewport} evidence")

    claims = data.get("forbidden_claims")
    if not isinstance(claims, list):
        raise AssertionError(f"{path.relative_to(ROOT)} missing forbidden_claims list")
    if len(claims) != len(set(claims)):
        raise AssertionError(f"{path.relative_to(ROOT)} contains duplicate forbidden claims")
    if set(claims) != REQUIRED_FORBIDDEN_CLAIMS:
        missing = REQUIRED_FORBIDDEN_CLAIMS.difference(claims)
        extra = set(claims).difference(REQUIRED_FORBIDDEN_CLAIMS)
        raise AssertionError(
            f"{path.relative_to(ROOT)} forbidden claims mismatch. Missing: {sorted(missing)}, Extra: {sorted(extra)}"
        )


def main() -> int:
    try:
        schema = _load_json(SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)

        for fixture in VALID_FIXTURES:
            data = _load_json(fixture)
            validator.validate(data)
            if not isinstance(data, dict):
                raise AssertionError(f"{fixture.relative_to(ROOT)} must be a JSON object")
            _assert_valid_fixture(data, fixture)

        for fixture in INVALID_FIXTURES:
            data = _load_json(fixture)
            try:
                validator.validate(data)
            except jsonschema.exceptions.ValidationError:
                continue
            raise AssertionError(f"invalid fixture unexpectedly passed schema validation: {fixture.relative_to(ROOT)}")
    except (AssertionError, OSError, json.JSONDecodeError, jsonschema.exceptions.SchemaError, jsonschema.exceptions.ValidationError) as exc:
        print(f"Builder responsive input boundary check failed: {exc}", file=sys.stderr)
        return 1

    print("Builder responsive input boundary check passed: intake eligibility is schema-bound and evidence-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
