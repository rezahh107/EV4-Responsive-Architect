#!/usr/bin/env python3
"""Validate EV4 Responsive risk and priority semantics.

This runner intentionally does not produce numeric scores. It verifies that
risk/priority assessments cannot hide blockers behind a good-looking verdict.
It can also validate a submitted assessment and persist the validated report.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
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
GENERIC_MITIGATION_TEXT = {"be careful", "check later", "fix carefully", "manual review"}


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


def _contains_sample_marker(value: Any) -> bool:
    if isinstance(value, str):
        return "sample" in value.lower()
    if isinstance(value, dict):
        return any(_contains_sample_marker(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_sample_marker(item) for item in value)
    return False


def semantic_validate(payload: dict[str, Any], path: Path) -> None:
    forbidden_keys = SCORE_FORBIDDEN_KEYS.intersection(walk_keys(payload))
    if forbidden_keys:
        raise AssertionError(f"{path} contains forbidden score key(s): {sorted(forbidden_keys)}")

    forbidden_claims = payload.get("forbidden_claims", {})
    enabled_forbidden = [key for key, value in forbidden_claims.items() if value is not False]
    if enabled_forbidden:
        raise AssertionError(f"{path} enables forbidden claim(s): {enabled_forbidden}")

    evidence_basis = payload.get("evidence_basis", {})
    packet_origin = evidence_basis.get("packet_origin")
    run_mode = evidence_basis.get("run_mode")
    assessment_scope = payload.get("assessment_scope")
    issue_reference = evidence_basis.get("issue_reference", "")

    if packet_origin == "sample_contract_fixture":
        if run_mode != "sample_submitted_packet_dry_run":
            raise AssertionError(f"{path} sample packet may only use sample_submitted_packet_dry_run")
        if assessment_scope == "submitted_evidence_risk_priority":
            raise AssertionError(f"{path} sample packet cannot be used for submitted_evidence_risk_priority")
        if issue_reference != "not_applicable_sample_dry_run":
            raise AssertionError(f"{path} sample packet must use not_applicable_sample_dry_run issue reference")

    if packet_origin == "real_issue_submission":
        if run_mode != "submitted_packet_shadow_mode":
            raise AssertionError(f"{path} real submitted evidence must use submitted_packet_shadow_mode")
        if assessment_scope != "submitted_evidence_risk_priority":
            raise AssertionError(f"{path} real submitted evidence must use submitted_evidence_risk_priority")
        if not issue_reference.startswith("https://github.com/"):
            raise AssertionError(f"{path} real submitted evidence must link a GitHub issue")
        if _contains_sample_marker(evidence_basis):
            raise AssertionError(f"{path} real submitted evidence basis contains sample marker")

    known_evidence_refs = set(evidence_basis.get("evidence_refs", []))
    hard_gates = payload.get("hard_gates", [])
    gate_ids = {gate.get("gate_id") for gate in hard_gates}
    failed_blocking_gates = [
        gate for gate in hard_gates
        if gate.get("status") == "fail" and gate.get("blocking_if_failed") is True and gate.get("gate_weight") == "hard_blocker"
    ]

    for gate in hard_gates:
        if gate.get("blocking_if_failed") and gate.get("gate_weight") != "hard_blocker":
            raise AssertionError(f"{path} blocking_if_failed gates must use gate_weight=hard_blocker")
        if gate.get("gate_weight") == "hard_blocker" and not gate.get("blocking_if_failed"):
            raise AssertionError(f"{path} hard_blocker gates must set blocking_if_failed=true")

    verdict = payload.get("aggregate_verdict", {})
    verdict_status = verdict.get("status")
    blocking_refs = set(verdict.get("blocking_gate_refs", []))

    if not blocking_refs.issubset(gate_ids):
        raise AssertionError(f"{path} blocking_gate_refs contains unknown gate id(s): {sorted(blocking_refs - gate_ids)}")

    failed_blocking_gate_ids = {gate.get("gate_id") for gate in failed_blocking_gates}
    if failed_blocking_gates and verdict_status in READY_STATUSES:
        raise AssertionError(f"{path} marks assessment ready while hard gate blocker(s) failed")

    if failed_blocking_gates and not failed_blocking_gate_ids.issubset(blocking_refs):
        missing = sorted(failed_blocking_gate_ids - blocking_refs)
        raise AssertionError(f"{path} missing failed gate(s) in blocking_gate_refs: {missing}")

    if blocking_refs and not blocking_refs.issubset(failed_blocking_gate_ids):
        raise AssertionError(f"{path} blocking_gate_refs must point only to failed hard blocker gates")

    if not failed_blocking_gates and verdict_status in BLOCKED_STATUSES:
        raise AssertionError(f"{path} blocks assessment without a failed hard blocker gate")

    failure_items = payload.get("failure_items", [])
    failure_ids = {item.get("failure_id") for item in failure_items}
    if len(failure_ids) != len(failure_items):
        raise AssertionError(f"{path} failure_id values must be unique")

    for item in failure_items:
        missing_evidence_refs = set(item.get("evidence_refs", [])) - known_evidence_refs
        if missing_evidence_refs:
            raise AssertionError(f"{path} failure {item.get('failure_id')} references unknown evidence: {sorted(missing_evidence_refs)}")

        if item.get("severity") == "blocker":
            if verdict_status in READY_STATUSES:
                raise AssertionError(f"{path} blocker failure cannot produce a ready aggregate verdict")
            if item.get("priority") != "P0" or item.get("repair_urgency") != "immediate":
                raise AssertionError(f"{path} blocker failure must be P0 and immediate")
            if item.get("owner_route") == "no_action_note":
                raise AssertionError(f"{path} blocker failure cannot route to no_action_note")

        if item.get("architecture_mutation_risk") == "high":
            if item.get("owner_route") != "main_pipeline_reroute":
                raise AssertionError(f"{path} high architecture mutation risk must route back to main pipeline")
            if item.get("selected_for_repair"):
                raise AssertionError(f"{path} high architecture mutation risk cannot be selected for responsive repair")
            if verdict_status != "route_back_to_main_pipeline":
                raise AssertionError(f"{path} high architecture mutation risk requires aggregate route_back_to_main_pipeline")

        if item.get("evidence_confidence") == "low":
            if item.get("selected_for_repair"):
                raise AssertionError(f"{path} low-confidence failure cannot be selected for repair without more evidence")
            if item.get("owner_route") != "evidence_request":
                raise AssertionError(f"{path} low-confidence failure must route to evidence_request")
            if verdict_status != "blocked_by_insufficient_evidence":
                raise AssertionError(f"{path} low-confidence failure requires blocked_by_insufficient_evidence verdict")

    for repair in payload.get("repair_risks", []):
        missing_failure_refs = set(repair.get("failure_refs", [])) - failure_ids
        if missing_failure_refs:
            raise AssertionError(f"{path} repair {repair.get('repair_id')} references unknown failure(s): {sorted(missing_failure_refs)}")

        mitigation_text = repair.get("required_mitigation", "").strip().lower()
        if mitigation_text in GENERIC_MITIGATION_TEXT:
            raise AssertionError(f"{path} repair {repair.get('repair_id')} uses generic mitigation text")

        checks = set(repair.get("mitigation_checks", []))
        if repair.get("risk_level") == "high" and "rollback_plan_required" not in checks:
            raise AssertionError(f"{path} high repair risk requires rollback_plan_required")
        if repair.get("desktop_regression_risk") == "high" and "desktop_recheck_each_step" not in checks:
            raise AssertionError(f"{path} high desktop regression risk requires desktop_recheck_each_step")
        if repair.get("accessibility_risk") == "high" and "accessibility_gate_required" not in checks:
            raise AssertionError(f"{path} high accessibility risk requires accessibility_gate_required")
        if repair.get("architecture_mutation_risk") == "high" and "route_back_to_main_pipeline_required" not in checks:
            raise AssertionError(f"{path} high architecture mutation risk requires route_back_to_main_pipeline_required")


def read_and_validate(path: Path, validator: Draft202012Validator) -> dict[str, Any]:
    payload = strip_fixture_schema_file(load_json(path))
    validate_schema(payload, validator, path)
    semantic_validate(payload, path)
    return payload


def expect_valid(path: Path, validator: Draft202012Validator) -> None:
    read_and_validate(path, validator)


def expect_invalid(path: Path, validator: Draft202012Validator) -> None:
    try:
        read_and_validate(path, validator)
    except AssertionError:
        return
    raise AssertionError(f"{path} was expected to fail risk-priority validation but passed")


def write_report(payload: dict[str, Any], out_path: Path) -> None:
    if not out_path.name.endswith(".generated.json"):
        raise AssertionError("risk priority generated report path must end with .generated.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate EV4 Responsive risk-priority assessment semantics.")
    parser.add_argument("--assessment", type=Path, help="Assessment JSON to validate.")
    parser.add_argument("--out", type=Path, help="Optional .generated.json report output path.")
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        schema = load_json(SCHEMA_PATH)
        validator = Draft202012Validator(schema)

        if args.assessment:
            assessment_path = (ROOT / args.assessment).resolve() if not args.assessment.is_absolute() else args.assessment
            payload = read_and_validate(assessment_path, validator)
            if args.out:
                out_path = (ROOT / args.out).resolve() if not args.out.is_absolute() else args.out
                write_report(payload, out_path)
            print("risk priority assessment validation passed")
            return 0

        expect_valid(VALID_FIXTURE, validator)
        for invalid_path in sorted(SEMANTIC_INVALID_DIR.glob("*.json")):
            expect_invalid(invalid_path, validator)
    except AssertionError as exc:
        print(f"risk priority validation failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    print("risk priority validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
