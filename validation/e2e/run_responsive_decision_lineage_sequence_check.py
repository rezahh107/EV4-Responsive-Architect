#!/usr/bin/env python3
"""Validate Wave 4 Responsive intake-to-output decision lineage preservation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALID_INTAKE = ROOT / "validation" / "fixtures" / "valid" / "builder_responsive_input.valid.json"
VALID_OUTPUT = ROOT / "validation" / "fixtures" / "valid" / "responsive_output_same_tree.valid.json"
NEGATIVE_INTAKE = ROOT / "validation" / "fixtures" / "invalid" / "builder_responsive_input_missing_decision_lineage.invalid.json"
NEGATIVE_OUTPUTS = (
    ROOT / "validation" / "fixtures" / "invalid" / "responsive_output_dropped_decision_lineage.invalid.json",
    ROOT / "validation" / "fixtures" / "invalid" / "responsive_output_replaced_decision_lineage.invalid.json",
    ROOT / "validation" / "fixtures" / "invalid" / "responsive_output_runtime_conflict_redesign.invalid.json",
)
STABLE_DIAGNOSTIC = "EV4_RESPONSIVE_DECISION_LINEAGE_SEQUENCE_BREAK"
UPSTREAM_FIELDS = (
    "decision_family",
    "decision_card_ref",
    "selected_option",
    "rejected_options",
)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def lineage(payload: dict[str, object], path: Path) -> dict[str, object]:
    value = payload.get("decision_lineage")
    if not isinstance(value, dict):
        raise ValueError(f"{STABLE_DIAGNOSTIC}: missing decision_lineage in {rel(path)}")
    for field in (*UPSTREAM_FIELDS, "evidence_refs", "evidence_state", "consumer_stage"):
        if field not in value:
            raise ValueError(f"{STABLE_DIAGNOSTIC}: missing {field} in {rel(path)}")
    return value


def assert_sequence_preserved(intake: dict[str, object], output: dict[str, object]) -> None:
    intake_lineage = lineage(intake, VALID_INTAKE)
    output_lineage = lineage(output, VALID_OUTPUT)
    for field in UPSTREAM_FIELDS:
        if output_lineage.get(field) != intake_lineage.get(field):
            raise ValueError(f"{STABLE_DIAGNOSTIC}: output changed upstream {field}")
    intake_refs = set(intake_lineage.get("evidence_refs", []))
    output_refs = set(output_lineage.get("evidence_refs", []))
    if not intake_refs.issubset(output_refs):
        raise ValueError(f"{STABLE_DIAGNOSTIC}: output dropped upstream evidence_refs")
    if output_lineage.get("consumer_stage") != "responsive_validation_output":
        raise ValueError(f"{STABLE_DIAGNOSTIC}: output did not advance to responsive_validation_output")


def assert_negative_fixture_fails(path: Path) -> None:
    try:
        payload = load(path)
        candidate_lineage = lineage(payload, path)
        if path.name == "responsive_output_replaced_decision_lineage.invalid.json":
            baseline = lineage(load(VALID_INTAKE), VALID_INTAKE)
            for field in UPSTREAM_FIELDS:
                if candidate_lineage.get(field) != baseline.get(field):
                    raise ValueError(f"{STABLE_DIAGNOSTIC}: output changed upstream {field}")
        if path.name == "responsive_output_runtime_conflict_redesign.invalid.json":
            if candidate_lineage.get("consumer_stage") == "runtime_evidence_conflict" and payload.get("selected_route") != "blocked_pending_input":
                raise ValueError(f"{STABLE_DIAGNOSTIC}: runtime mismatch converted into redesign")
    except ValueError as err:
        if STABLE_DIAGNOSTIC not in str(err):
            raise
        return
    raise ValueError(f"{rel(path)} unexpectedly passed lineage sequence guard")


def main() -> int:
    try:
        assert_sequence_preserved(load(VALID_INTAKE), load(VALID_OUTPUT))
        assert_negative_fixture_fails(NEGATIVE_INTAKE)
        for path in NEGATIVE_OUTPUTS:
            assert_negative_fixture_fails(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Responsive decision lineage sequence check failed: {exc}", file=sys.stderr)
        return 1
    print("Responsive decision lineage sequence check passed: intake lineage is preserved through validation output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
