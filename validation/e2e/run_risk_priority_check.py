#!/usr/bin/env python3
"""Validate EV4 Responsive risk-priority assessments without numeric scores."""

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
INVALID_DIR = ROOT / "validation" / "risk_priority" / "invalid"

READY = {"ready_for_repair_planning", "ready_with_visible_flags"}
BLOCKED = {"blocked_by_hard_gate", "blocked_by_insufficient_evidence", "route_back_to_main_pipeline"}
SCORE_KEYS = {"score", "numeric_score", "responsive_score", "readiness_score", "average_score"}
GENERIC_MITIGATION = {"be careful", "check later", "fix carefully", "manual review"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_fixture(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    payload.pop("$schema_file", None)
    return payload


def walk_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for key, nested in value.items():
            out.append(str(key))
            out.extend(walk_keys(nested))
        return out
    if isinstance(value, list):
        out = []
        for nested in value:
            out.extend(walk_keys(nested))
        return out
    return []


def validate_schema(payload: dict[str, Any], validator: Draft202012Validator, path: Path) -> None:
    errors = sorted(validator.iter_errors(payload), key=lambda error: [str(part) for part in error.path])
    if errors:
        raise AssertionError(f"{path} failed schema validation: {errors[0].message}")


def contains_sample(value: Any) -> bool:
    if isinstance(value, str):
        return "sample" in value.lower()
    if isinstance(value, dict):
        return any(contains_sample(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_sample(item) for item in value)
    return False


def semantic_validate(payload: dict[str, Any], path: Path) -> None:
    forbidden_keys = SCORE_KEYS.intersection(walk_keys(payload))
    if forbidden_keys:
        raise AssertionError(f"{path} contains forbidden score key(s): {sorted(forbidden_keys)}")

    enabled_claims = [key for key, value in payload.get("forbidden_claims", {}).items() if value is not False]
    if enabled_claims:
        raise AssertionError(f"{path} enables forbidden claim(s): {enabled_claims}")

    basis = payload.get("evidence_basis", {})
    origin = basis.get("packet_origin")
    run_mode = basis.get("run_mode")
    scope = payload.get("assessment_scope")
    issue_ref = basis.get("issue_reference", "")

    if origin == "sample_contract_fixture":
        if run_mode != "sample_submitted_packet_dry_run":
            raise AssertionError(f"{path} sample packet may only use sample_submitted_packet_dry_run")
        if scope == "submitted_evidence_risk_priority":
            raise AssertionError(f"{path} sample packet cannot be used for submitted evidence assessment")
        if issue_ref != "not_applicable_sample_dry_run":
            raise AssertionError(f"{path} sample packet must use not_applicable_sample_dry_run issue reference")

    if origin == "real_issue_submission":
        if run_mode != "submitted_packet_shadow_mode":
            raise AssertionError(f"{path} real submitted evidence must use submitted_packet_shadow_mode")
        if scope != "submitted_evidence_risk_priority":
            raise AssertionError(f"{path} real submitted evidence must use submitted_evidence_risk_priority")
        if not issue_ref.startswith("https://github.com/"):
            raise AssertionError(f"{path} real submitted evidence must link a GitHub issue")
        if contains_sample(basis):
            raise AssertionError(f"{path} real submitted evidence basis contains sample marker")

    gates = payload.get("hard_gates", [])
    gate_ids = {gate.get("gate_id") for gate in gates}
    failed = [
        gate for gate in gates
        if gate.get("status") == "fail"
        and gate.get("blocking_if_failed") is True
        and gate.get("gate_weight") == "hard_blocker"
    ]

    for gate in gates:
        if gate.get("blocking_if_failed") and gate.get("gate_weight") != "hard_blocker":
            raise AssertionError(f"{path} blocking_if_failed gates must use gate_weight=hard_blocker")
        if gate.get("gate_weight") == "hard_blocker" and not gate.get("blocking_if_failed"):
            raise AssertionError(f"{path} hard_blocker gates must set blocking_if_failed=true")

    verdict = payload.get("aggregate_verdict", {})
    status = verdict.get("status")
    blocking_refs = set(verdict.get("blocking_gate_refs", []))
    failed_ids = {gate.get("gate_id") for gate in failed}

    if not blocking_refs.issubset(gate_ids):
        raise AssertionError(f"{path} blocking_gate_refs contains unknown gate id(s): {sorted(blocking_refs - gate_ids)}")
    if failed and status in READY:
        raise AssertionError(f"{path} marks assessment ready while hard gate blocker(s) failed")
    if failed and not failed_ids.issubset(blocking_refs):
        raise AssertionError(f"{path} missing failed gate(s) in blocking_gate_refs: {sorted(failed_ids - blocking_refs)}")
    if blocking_refs and not blocking_refs.issubset(failed_ids):
        raise AssertionError(f"{path} blocking_gate_refs must point only to failed hard blocker gates")
    if not failed and status in BLOCKED:
        raise AssertionError(f"{path} blocks assessment without a failed hard blocker gate")

    known_evidence = set(basis.get("evidence_refs", []))
    failures = payload.get("failure_items", [])
    failure_ids = {item.get("failure_id") for item in failures}
    if len(failure_ids) != len(failures):
        raise AssertionError(f"{path} failure_id values must be unique")

    for item in failures:
        missing_evidence = set(item.get("evidence_refs", [])) - known_evidence
        if missing_evidence:
            raise AssertionError(f"{path} failure {item.get('failure_id')} references unknown evidence: {sorted(missing_evidence)}")

        if item.get("severity") == "blocker":
            if status in READY:
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
            if status != "route_back_to_main_pipeline":
                raise AssertionError(f"{path} high architecture mutation risk requires route_back_to_main_pipeline")

        if item.get("evidence_confidence") == "low":
            if item.get("selected_for_repair"):
                raise AssertionError(f"{path} low-confidence failure cannot be selected for repair")
            if item.get("owner_route") != "evidence_request":
                raise AssertionError(f"{path} low-confidence failure must route to evidence_request")
            if status != "blocked_by_insufficient_evidence":
                raise AssertionError(f"{path} low-confidence failure requires blocked_by_insufficient_evidence")

    for repair in payload.get("repair_risks", []):
        missing_failures = set(repair.get("failure_refs", [])) - failure_ids
        if missing_failures:
            raise AssertionError(f"{path} repair {repair.get('repair_id')} references unknown failure(s): {sorted(missing_failures)}")

        if repair.get("required_mitigation", "").strip().lower() in GENERIC_MITIGATION:
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


def read_validated(path: Path, validator: Draft202012Validator) -> dict[str, Any]:
    payload = strip_fixture(load_json(path))
    validate_schema(payload, validator, path)
    semantic_validate(payload, path)
    return payload


def expect_invalid_payload(name: str, payload: dict[str, Any], validator: Draft202012Validator) -> None:
    try:
        validate_schema(payload, validator, Path(f"<case:{name}>"))
        semantic_validate(payload, Path(f"<case:{name}>"))
    except AssertionError:
        return
    raise AssertionError(f"case {name} was expected to fail risk-priority validation but passed")


def run_negative_case_suite(base: dict[str, Any], validator: Draft202012Validator) -> None:
    def clone() -> dict[str, Any]:
        return json.loads(json.dumps(base))

    cases: dict[str, dict[str, Any]] = {}

    case = clone()
    case["hard_gates"][0]["status"] = "fail"
    case["aggregate_verdict"] = {"status": "ready_for_repair_planning", "required_next_action": "plan_repair_batch", "blocking_gate_refs": [], "carry_forward_flags": []}
    cases["failed_hard_gate_ready"] = case

    case = clone()
    case["hard_gates"][0]["status"] = "fail"
    case["aggregate_verdict"] = {"status": "blocked_by_hard_gate", "required_next_action": "resolve_hard_gate_failure", "blocking_gate_refs": ["HG-NOT-REAL"], "carry_forward_flags": []}
    cases["unknown_blocking_ref"] = case

    case = clone()
    case["failure_items"][0].update({"severity": "blocker", "priority": "P0", "repair_urgency": "immediate"})
    case["aggregate_verdict"] = {"status": "ready_for_repair_planning", "required_next_action": "plan_repair_batch", "blocking_gate_refs": [], "carry_forward_flags": []}
    cases["blocker_ready_verdict"] = case

    case = clone()
    case["failure_items"][0].update({"severity": "blocker", "priority": "P2", "repair_urgency": "later"})
    cases["blocker_wrong_priority"] = case

    case = clone()
    case["failure_items"][0].update({"architecture_mutation_risk": "high", "owner_route": "responsive_repair", "selected_for_repair": True})
    cases["architecture_mutation_not_rerouted"] = case

    case = clone()
    case["failure_items"][0].update({"evidence_confidence": "low", "selected_for_repair": False, "owner_route": "evidence_request"})
    cases["low_confidence_ready"] = case

    case = clone()
    case["failure_items"][0]["evidence_refs"] = ["EVD-NOT-REAL"]
    cases["unknown_evidence_ref"] = case

    case = clone()
    case["repair_risks"][0]["failure_refs"] = ["FAIL-NOT-REAL"]
    cases["unknown_failure_ref"] = case

    case = clone()
    case["repair_risks"][0].update({"risk_level": "high", "mitigation_checks": ["desktop_recheck_each_step"]})
    cases["high_repair_missing_rollback"] = case

    case = clone()
    case["repair_risks"][0].update({"desktop_regression_risk": "high", "mitigation_checks": ["rollback_plan_required"]})
    cases["high_desktop_missing_recheck"] = case

    case = clone()
    case["repair_risks"][0].update({"accessibility_risk": "high", "mitigation_checks": ["rollback_plan_required"]})
    cases["high_accessibility_missing_gate"] = case

    case = clone()
    case["repair_risks"][0].update({"architecture_mutation_risk": "high", "mitigation_checks": ["rollback_plan_required"]})
    cases["high_architecture_missing_reroute_check"] = case

    case = clone()
    case["assessment_scope"] = "submitted_evidence_risk_priority"
    cases["sample_used_as_submitted"] = case

    for name, payload in cases.items():
        expect_invalid_payload(name, payload, validator)


def expect_invalid_file(path: Path, validator: Draft202012Validator) -> None:
    try:
        read_validated(path, validator)
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
        validator = Draft202012Validator(load_json(SCHEMA_PATH))

        if args.assessment:
            assessment_path = (ROOT / args.assessment).resolve() if not args.assessment.is_absolute() else args.assessment
            payload = read_validated(assessment_path, validator)
            if args.out:
                out_path = (ROOT / args.out).resolve() if not args.out.is_absolute() else args.out
                write_report(payload, out_path)
            print("risk priority assessment validation passed")
            return 0

        base = read_validated(VALID_FIXTURE, validator)
        run_negative_case_suite(base, validator)
        for invalid_path in sorted(INVALID_DIR.glob("*.json")):
            expect_invalid_file(invalid_path, validator)
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
