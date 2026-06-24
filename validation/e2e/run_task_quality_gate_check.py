#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "planning" / "EV4_AUTOMATION_QUALITY_GATE.json"
POLICY_SCHEMA = ROOT / "schemas" / "ev4-responsive-automation-quality-gate.schema.json"
REVIEW_SCHEMA = ROOT / "schemas" / "ev4-responsive-task-quality-review.schema.json"
VALID_REVIEW = ROOT / "validation" / "fixtures" / "valid" / "task_quality_review.valid.json"
INVALID_DIR = ROOT / "validation" / "task_quality" / "invalid"
SENSITIVE_TYPES = {
    "schema_hardening",
    "automation_control",
    "readiness_gate",
    "sample_vs_real_safety",
    "risk_priority_engine",
    "evidence_boundary",
    "ci_workflow",
}


class QualityGateError(AssertionError):
    pass


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def strip_schema_file(payload: dict[str, Any]) -> dict[str, Any]:
    clean = dict(payload)
    clean.pop("$schema_file", None)
    return clean


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda err: [str(p) for p in err.path])
    if errors:
        raise QualityGateError(f"{label} schema validation failed: {errors[0].message}")


def assert_policy(policy: dict[str, Any], schema: dict[str, Any]) -> None:
    assert_schema_valid(policy, schema, "automation quality policy")
    principles = policy["quality_principles"]
    if not principles["self_critique_is_insufficient"]:
        raise QualityGateError("self critique must remain insufficient by policy")
    if not principles["cross_critique_required_for_sensitive_tasks"]:
        raise QualityGateError("sensitive tasks must require cross critique")
    if "self_critique_only_completion" not in policy["forbidden_quality_shortcuts"]:
        raise QualityGateError("policy must forbid self-critique-only completion")
    if set(policy["sensitive_task_types"]) < SENSITIVE_TYPES:
        raise QualityGateError("policy is missing required sensitive task types")


def semantic_validate_review(review: dict[str, Any]) -> None:
    checks = review["deterministic_checks"]
    failed_checks = [name for name, value in checks.items() if value is not True]
    sensitive = review["task_sensitivity"] in {"sensitive", "critical"} or review["task_type"] in SENSITIVE_TYPES
    cross = review["cross_critique"]
    findings = review.get("findings", [])
    boundary = set(review.get("boundary_assertions", []))

    if not review["self_critique"]["recorded"]:
        raise QualityGateError("self critique record is required but not sufficient")

    if failed_checks:
        if review["completion_allowed"]:
            raise QualityGateError("completion cannot be allowed when deterministic checks failed")
        if review["final_verdict"] == "pass":
            raise QualityGateError("pass verdict is forbidden when deterministic checks failed")

    if sensitive:
        if not cross["required"]:
            raise QualityGateError("sensitive task must require cross critique")
        if cross["status"] != "completed":
            if review["completion_allowed"]:
                raise QualityGateError("completion cannot be allowed without completed cross critique")
            if review["final_verdict"] == "pass":
                raise QualityGateError("pass verdict is forbidden without completed cross critique")
        if cross["reviewer_role"] != "strict_pessimistic_reviewer":
            raise QualityGateError("cross critique must use strict_pessimistic_reviewer role")
        if not cross["prompt_separation"]:
            raise QualityGateError("cross critique requires prompt separation")

    unfixed_major = [
        item for item in findings
        if item["severity"] in {"P0", "P1"} and not item["fixed"] and not item["follow_up_task_required"]
    ]
    if unfixed_major:
        raise QualityGateError("unfixed P0/P1 findings require a follow-up task or a fix")

    if review["completion_allowed"]:
        if review["final_verdict"] != "pass":
            raise QualityGateError("completion_allowed=true requires final_verdict=pass")
        required_boundary = {
            "no_self_critique_only_completion",
            "deterministic_checks_passed",
            "no_production_claim",
            "no_unrelated_task",
        }
        if sensitive:
            required_boundary.add("cross_critique_completed_when_required")
        missing = required_boundary - boundary
        if missing:
            raise QualityGateError("completion_allowed=true is missing quality boundary assertions")


def assert_valid_review(path: Path, schema: dict[str, Any]) -> None:
    payload = strip_schema_file(load(path))
    assert_schema_valid(payload, schema, path.name)
    semantic_validate_review(payload)


def assert_invalid_review(path: Path, schema: dict[str, Any]) -> None:
    payload = strip_schema_file(load(path))
    assert_schema_valid(payload, schema, path.name)
    try:
        semantic_validate_review(payload)
    except QualityGateError:
        return
    raise QualityGateError(f"{path.name} unexpectedly passed semantic quality validation")


def main() -> int:
    try:
        assert_policy(load(POLICY), load(POLICY_SCHEMA))
        review_schema = load(REVIEW_SCHEMA)
        assert_valid_review(VALID_REVIEW, review_schema)
        for path in sorted(INVALID_DIR.glob("*.invalid.json")):
            assert_invalid_review(path, review_schema)
    except Exception as exc:
        print(f"task quality gate validation failed: {exc}")
        return 1
    print("Task quality gate validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
