#!/usr/bin/env python3
"""Validate EV4 Responsive risk and priority semantics.

This runner intentionally does not produce numeric scores. It verifies that
risk/priority assessments cannot hide blockers behind a good-looking verdict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "ev4-responsive-risk-priority-assessment.schema.json"
VALID_FIXTURE = ROOT / "validation" / "fixtures" / "valid" / "risk_priority_assessment.valid.json"
SEMANTIC_INVALID_DIR = ROOT / "validation" / "risk_priority" / "invalid"

READY_STATUSES = {"ready_for_repair_planning", "ready_with_visible_flags"}
BLOCKED_STATUSES = {"blocked_by_hard_gate", "blocked_by_insufficient_evidence", "route_back_to_main_pipeline"}
SCORE_FORBIDDEN_KEYS = {"score", "numeric_score", "responsive_score", "readiness_score", "average_score"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def strip_fixture_schema_file(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    payload.pop("$schema_file", None)
    return payload


def walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(str(key))
            keys.extend(walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(walk_keys(nested))
    return keys


def validate_schema(payload: dict[str, Any], validator: Draft202012Validator, path: Path) -> None:
    errors = sorted(validator.iter_errors(payload), key=lambda error: [str(part) for part in error.path])
    if errors:
        raise AssertionError(f"{path} failed schema validation: {errors[0].message}")


def semantic_validate(payload: dict[str, Any], path: Path) -> None:
    forbidden_keys = SCORE_FORBIDDEN_KEYS.intersection(walk_keys(payload))
    if forbidden_keys:
        raise AssertionError(f"{path} contains forbidden score key(s): {sorted(forbidden_keys)}")

    forbidden_claims = payload.get("forbidden_claims", {})
    enabled_forbidden = [key for key, value in forbidden_claims.items() if value is not False]
    if enabled_forbidden:
        raise AssertionError(f"{path} enables forbidden claim(s): {enabled_forbidden}")

    hard_gates = payload.get("hard_gates", [])
    failed_blockers = [gate for gate in hard_gates if gate.get("status") == "fail" and gate.get("blocker") is True]
    verdict = payload.get("aggregate_verdict", {})
    verdict_status = verdict.get("status")
    blocking_refs = set(verdict.get("blocking_gate_refs", []))

    if failed_blockers and verdict_status in READY_STATUSES:
        raise AssertionError(f"{path} marks assessment ready while hard gate blocker(s) failed")

    if not failed_blockers and verdict_status in BLOCKED_STATUSES:
        raise AssertionError(f"{path} blocks assessment without a failed blocker gate")

    for gate in failed_blockers:
        if gate.get("gate_id") not in blocking_refs:
            raise AssertionError(f"{path} missing failed gate {gate.get('gate_id')} in blocking_gate_refs")

    for item in payload.get("failure_items", []):
        if item.get("severity") == "blocker":
            if item.get("priority") != "P0" or item.get("repair_urgency") != "immediate":
                raise AssertionError(f"{path} blocker failure must be P0 and immediate")
            if item.get("owner_route") == "no_action_note":
                raise AssertionError(f"{path} blocker failure cannot route to no_action_note")

        if item.get("architecture_mutation_risk") == "high" and item.get("owner_route") != "main_pipeline_reroute":
            raise AssertionError(f"{path} high architecture mutation risk must route back to main pipeline")

        if item.get("selected_for_repair") and item.get("evidence_confidence") == "low":
            raise AssertionError(f"{path} low-confidence failure cannot be selected for repair without more evidence")


def expect_valid(path: Path, validator: Draft202012Validator) -> None:
    payload = strip_fixture_schema_file(load_json(path))
    validate_schema(payload, validator, path)
    semantic_validate(payload, path)


def expect_invalid(path: Path, validator: Draft202012Validator) -> None:
    payload = strip_fixture_schema_file(load_json(path))
    try:
        validate_schema(payload, validator, path)
        semantic_validate(payload, path)
    except Exception:
        return
    raise AssertionError(f"{path} was expected to fail risk-priority validation but passed")


def main() -> int:
    try:
        schema = load_json(SCHEMA_PATH)
        validator = Draft202012Validator(schema)
        expect_valid(VALID_FIXTURE, validator)
        for invalid_path in sorted(SEMANTIC_INVALID_DIR.glob("*.json")):
            expect_invalid(invalid_path, validator)
    except Exception as exc:  # noqa: BLE001 - CLI should report compact failure
        print(f"risk priority validation failed: {exc}", file=sys.stderr)
        return 1
    print("risk priority validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
