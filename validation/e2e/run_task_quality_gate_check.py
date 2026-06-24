#!/usr/bin/env python3
from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "planning" / "EV4_AUTOMATION_QUALITY_GATE.json"
POLICY_SCHEMA = ROOT / "schemas" / "ev4-responsive-automation-quality-gate.schema.json"
REVIEW_SCHEMA = ROOT / "schemas" / "ev4-responsive-task-quality-review.schema.json"
VALID_REVIEW = ROOT / "validation" / "fixtures" / "valid" / "task_quality_review.valid.json"
INVALID_DIR = ROOT / "validation" / "task_quality" / "invalid"

REQUIRED_SENSITIVE_TYPES = {
    "schema_hardening",
    "automation_control",
    "readiness_gate",
    "sample_vs_real_safety",
    "risk_priority_engine",
    "evidence_boundary",
    "production_boundary",
    "ci_workflow",
}

EXPECTED_PR_RECONCILIATION_ORDER = [
    "inspect_open_automation_prs",
    "check_ci_status",
    "check_mergeability_and_head_sha",
    "read_pr_comments_and_review_comments",
    "evaluate_gemini_or_reviewer_feedback",
    "fix_small_in_scope_feedback_on_same_pr",
    "rerun_ci_after_fixes",
    "merge_when_green_mergeable_and_no_unresolved_feedback",
    "stop_after_merge_unless_next_task_is_trivial_and_no_state_drift",
]

REQUIRED_FORBIDDEN_DURING_OPEN_PR = {
    "start_new_queue_task",
    "create_parallel_automation_pr",
    "overwrite_queue_from_stale_snapshot",
    "merge_without_comment_check",
    "treat_review_comment_as_domain_evidence",
}

REQUIRED_FORBIDDEN_QUALITY_SHORTCUTS = {
    "self_critique_only_completion",
    "green_ci_as_quality_proof",
    "merged_pr_as_evidence_truth",
    "unstructured_reviewer_opinion_as_gate",
    "silent_follow_up_omission",
    "parallel_automation_prs_without_reconciliation",
    "gemini_review_as_independent_queue_task",
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
    if not REQUIRED_FORBIDDEN_QUALITY_SHORTCUTS.issubset(set(policy["forbidden_quality_shortcuts"])):
        raise QualityGateError("policy is missing required forbidden quality shortcuts")
    if not REQUIRED_SENSITIVE_TYPES.issubset(set(policy["sensitive_task_types"])):
        raise QualityGateError("policy is missing required sensitive task types")

    delayed = policy["delayed_review_policy"]
    if delayed["enabled"] is not True:
        raise QualityGateError("delayed reviewer window must remain enabled")
    if delayed["minimum_wait_minutes_before_merge"] < 10:
        raise QualityGateError("delayed reviewer window must be at least 10 minutes")
    if not delayed["block_merge_on_unresolved_high_priority_review"]:
        raise QualityGateError("high-priority external review feedback must block merge until resolved")

    reconciliation = policy["pr_reconciliation_policy"]
    if reconciliation["enabled"] is not True:
        raise QualityGateError("PR reconciliation preflight must remain enabled")
    if reconciliation["runs_before_new_task_selection"] is not True:
        raise QualityGateError("PR reconciliation must run before selecting a new queue task")
    if reconciliation["single_active_automation_pr"] is not True:
        raise QualityGateError("policy must enforce a single active automation PR")
    if reconciliation["review_handling_counts_as_queue_task"] is not False:
        raise QualityGateError("review handling must remain a PR lifecycle step, not a queue task")
    if reconciliation["open_automation_pr_effect"] != "block_new_queue_task_until_reconciled":
        raise QualityGateError("an open automation PR must block new queue task execution")
    if reconciliation["previous_pr_resolution_order"] != EXPECTED_PR_RECONCILIATION_ORDER:
        raise QualityGateError("PR reconciliation resolution order is invalid or missing steps")
    if not REQUIRED_FORBIDDEN_DURING_OPEN_PR.issubset(set(reconciliation["forbidden_during_open_pr"])):
        raise QualityGateError("policy is missing required forbidden actions during open PR")
    if "open_automation_pr_unreconciled" not in policy["completion_policy"]["blocked_if"]:
        raise QualityGateError("completion policy must block unresolved open automation PRs")


def semantic_validate_review(review: dict[str, Any]) -> None:
    checks = review["deterministic_checks"]
    failed_checks = [name for name, value in checks.items() if value is not True]
    sensitive = review["task_sensitivity"] in {"sensitive", "critical"} or review["task_type"] in REQUIRED_SENSITIVE_TYPES
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
            "bot_review_window_checked",
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
    except QualityGateError as exc:
        print(f"task quality gate validation failed: {exc}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("Task quality gate validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
