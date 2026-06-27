#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "planning" / "EV4_RTAQ_SSOT_GUARD_POLICY.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
LEDGER = ROOT / "planning" / "EV4_RUN_LEDGER.json"
STATUS = ROOT / "STATUS.md"

REQUIRED_GATES = {
    "full_untruncated_source_required",
    "no_mutation_from_partial_or_truncated_snippets",
    "allowlisted_semantic_patch_required",
    "completed_historical_tasks_preserved",
    "old_ledger_records_append_only",
    "json_state_files_must_remain_pretty_printed",
    "diff_budget_required_before_pr_creation",
    "transient_pr_lifecycle_state_forbidden_on_main",
    "status_queue_ledger_consistency_checked",
    "issue_8_evidence_pilot_boundaries_preserved",
    "ci_success_not_responsive_correctness_evidence",
}

REQUIRED_BLOCKED_PATCH_CLASSES = {
    "rewrite_completed_task_title_or_objective",
    "rewrite_completed_task_allowed_or_forbidden_work",
    "rewrite_existing_ledger_records",
    "minify_json_state_file",
    "synthesize_state_file_from_memory",
    "synthesize_state_file_from_truncated_tool_output",
    "merge_transient_in_pr_or_executing_status_to_main",
    "treat_green_ci_as_responsive_correctness_evidence",
}

REQUIRED_BOUNDARIES = {
    "may_create_submitted_evidence": False,
    "may_modify_issue_8": False,
    "may_run_real_pilot": False,
    "may_upgrade_readiness_or_release_claims": False,
    "may_claim_live_render_export_accessibility_or_pixel_validation": False,
}

STATE_JSON_FILES = [QUEUE, LEDGER, POLICY]


class SSOTGuardError(AssertionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def assert_pretty_printed_json(path: Path) -> None:
    path_label = display_path(path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 10:
        raise SSOTGuardError(f"{path_label} looks minified or truncated")
    if lines[0].strip() != "{":
        raise SSOTGuardError(f"{path_label} must start with an opening object line")
    if not any(line.startswith("  ") for line in lines[1:]):
        raise SSOTGuardError(f"{path_label} must keep readable indentation")
    if not text.endswith("\n"):
        raise SSOTGuardError(f"{path_label} must end with a newline")


def assert_policy(policy: dict[str, Any]) -> None:
    if policy.get("schema") != "ev4-rtaq-ssot-guard-policy@1.0.0":
        raise SSOTGuardError("unexpected SSOT guard policy schema")
    if policy.get("status") != "active":
        raise SSOTGuardError("SSOT guard policy must remain active")

    gates = policy.get("mandatory_gates", {})
    missing_gates = [name for name in REQUIRED_GATES if gates.get(name) is not True]
    if missing_gates:
        raise SSOTGuardError("missing enabled mandatory gates: " + ", ".join(sorted(missing_gates)))

    diff_budget = policy.get("diff_budget", {})
    if diff_budget.get("default_max_deleted_lines_for_state_sync", 0) > 20:
        raise SSOTGuardError("state sync deletion budget must remain <= 20 lines")
    if diff_budget.get("queue_historical_completed_task_rewrites_allowed") is not False:
        raise SSOTGuardError("completed historical queue rewrites must stay forbidden")
    if diff_budget.get("ledger_existing_record_rewrites_allowed") is not False:
        raise SSOTGuardError("existing ledger record rewrites must stay forbidden")
    if diff_budget.get("ledger_append_only_required") is not True:
        raise SSOTGuardError("ledger append-only policy must stay enabled")
    if diff_budget.get("status_transient_fields_allowed_on_main") is not False:
        raise SSOTGuardError("transient status fields must not be mergeable to main")

    blocked = set(policy.get("blocked_state_patch_classes", []))
    missing_blockers = REQUIRED_BLOCKED_PATCH_CLASSES - blocked
    if missing_blockers:
        raise SSOTGuardError("missing blocked patch classes: " + ", ".join(sorted(missing_blockers)))

    boundaries = policy.get("evidence_boundaries", {})
    for key, expected in REQUIRED_BOUNDARIES.items():
        if boundaries.get(key) is not expected:
            raise SSOTGuardError(f"evidence boundary changed: {key}")


def assert_queue_shape(queue: dict[str, Any], forbidden_transient: set[str]) -> None:
    tasks = queue.get("tasks", [])
    task_ids = [task.get("task_id") for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        raise SSOTGuardError("queue task IDs must be unique")

    order = queue.get("active_cycle", {}).get("task_order", [])
    if len(order) != len(set(order)):
        raise SSOTGuardError("active_cycle.task_order must not contain duplicates")
    missing_from_order = sorted(set(task_ids) - set(order))
    if missing_from_order:
        raise SSOTGuardError("tasks missing from task_order: " + ", ".join(missing_from_order))

    for task in tasks:
        status = task.get("status")
        if status in forbidden_transient:
            raise SSOTGuardError(f"transient queue status is not mergeable to main: {task.get('task_id')}={status}")
        if status == "merged" and not task.get("completed_pr"):
            raise SSOTGuardError(f"merged task is missing completed_pr: {task.get('task_id')}")

    required_forbidden_claims = {
        "production_ready",
        "release_ready",
        "pixel_perfect",
        "live_render_validated",
        "export_json_validated",
        "accessibility_passed",
        "sample_packet_used_as_real_evidence",
        "numeric_score_overrides_gate",
    }
    if not required_forbidden_claims.issubset(set(queue.get("forbidden_claims", []))):
        raise SSOTGuardError("queue is missing required forbidden claims")


def assert_ledger_shape(ledger: dict[str, Any]) -> None:
    records = ledger.get("ledger_records", [])
    record_ids = [record.get("record_id") for record in records]
    run_ids = [record.get("run_id") for record in records]
    if len(record_ids) != len(set(record_ids)):
        raise SSOTGuardError("ledger record IDs must be unique")
    if len(run_ids) != len(set(run_ids)):
        raise SSOTGuardError("ledger run IDs must be unique")

    for record in records:
        if not record.get("boundary_assertions"):
            raise SSOTGuardError(f"ledger record is missing boundary assertions: {record.get('record_id')}")
        if not record.get("critique_summary"):
            raise SSOTGuardError(f"ledger record is missing critique summary: {record.get('record_id')}")
        if record.get("ci_conclusion") == "success" and "responsive correctness" in record.get("next_queue_effect", "").lower():
            raise SSOTGuardError("ledger must not treat CI success as responsive correctness evidence")


def assert_status_text(status_text: str, forbidden_transient: set[str]) -> None:
    for value in forbidden_transient:
        if f"status: {value}" in status_text or f"_status: {value}" in status_text:
            raise SSOTGuardError(f"transient status value is not mergeable to main: {value}")
    required_boundaries = [
        "real_submitted_packet_present: false",
        "pilot_allowed_to_start: false",
        "ci_success_claim_boundary: repository checks only",
        "readiness_claims_upgraded: false",
    ]
    missing = [item for item in required_boundaries if item not in status_text]
    if missing:
        raise SSOTGuardError("STATUS.md is missing evidence boundary text: " + ", ".join(missing))


def count_deleted_lines(base: str, head: str) -> int:
    diff = difflib.unified_diff(base.splitlines(), head.splitlines(), lineterm="")
    return sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))


def assert_append_only_ledger(base: dict[str, Any], head: dict[str, Any]) -> None:
    base_records = base.get("ledger_records", [])
    head_records = head.get("ledger_records", [])
    if len(head_records) < len(base_records):
        raise SSOTGuardError("ledger records must be append-only; head has fewer records than base")
    for index, base_record in enumerate(base_records):
        if head_records[index] != base_record:
            raise SSOTGuardError(f"existing ledger record was rewritten at index {index}")


def assert_completed_tasks_preserved(base: dict[str, Any], head: dict[str, Any], allowed_task_ids: set[str]) -> None:
    head_by_id = {task.get("task_id"): task for task in head.get("tasks", [])}
    for base_task in base.get("tasks", []):
        task_id = base_task.get("task_id")
        if task_id in allowed_task_ids:
            continue
        if base_task.get("status") == "merged" and head_by_id.get(task_id) != base_task:
            raise SSOTGuardError(f"completed historical task was rewritten: {task_id}")


def assert_pairwise_patch(base_dir: Path, head_dir: Path, allowed_task_ids: set[str], max_deleted: int) -> None:
    pairs = [
        ("planning/EV4_ROLLING_QUEUE.json", "queue"),
        ("planning/EV4_RUN_LEDGER.json", "ledger"),
    ]
    for rel_path, label in pairs:
        base_path = base_dir / rel_path
        head_path = head_dir / rel_path
        base_text = base_path.read_text(encoding="utf-8")
        head_text = head_path.read_text(encoding="utf-8")
        deleted = count_deleted_lines(base_text, head_text)
        if deleted > max_deleted:
            raise SSOTGuardError(f"{label} deletion budget exceeded: {deleted} > {max_deleted}")
        assert_pretty_printed_json(head_path)

    base_queue = load_json(base_dir / "planning/EV4_ROLLING_QUEUE.json")
    head_queue = load_json(head_dir / "planning/EV4_ROLLING_QUEUE.json")
    assert_completed_tasks_preserved(base_queue, head_queue, allowed_task_ids)

    base_ledger = load_json(base_dir / "planning/EV4_RUN_LEDGER.json")
    head_ledger = load_json(head_dir / "planning/EV4_RUN_LEDGER.json")
    assert_append_only_ledger(base_ledger, head_ledger)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RTAQ SSOT state-preservation guardrails.")
    parser.add_argument("--base-dir", type=Path, default=None, help="Optional base checkout for pairwise PR diff validation.")
    parser.add_argument("--head-dir", type=Path, default=ROOT, help="Head checkout for pairwise PR diff validation.")
    parser.add_argument("--allow-task", action="append", default=[], help="Task ID allowed to change during pairwise validation.")
    args = parser.parse_args()

    try:
        policy = load_json(POLICY)
        assert_policy(policy)
        forbidden_transient = set(policy.get("forbidden_transient_status_values_on_main", []))

        for path in STATE_JSON_FILES:
            assert_pretty_printed_json(path)

        assert_queue_shape(load_json(QUEUE), forbidden_transient)
        assert_ledger_shape(load_json(LEDGER))
        assert_status_text(STATUS.read_text(encoding="utf-8"), forbidden_transient)

        if args.base_dir is not None:
            max_deleted = int(policy["diff_budget"]["default_max_deleted_lines_for_state_sync"])
            assert_pairwise_patch(args.base_dir, args.head_dir, set(args.allow_task), max_deleted)
    except SSOTGuardError as exc:
        print(f"RTAQ SSOT guard failed: {exc}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    print("RTAQ SSOT guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
