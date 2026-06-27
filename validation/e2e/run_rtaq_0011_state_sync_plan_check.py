#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
LEDGER_PATH = ROOT / "planning" / "EV4_RUN_LEDGER.json"
STATUS_PATH = ROOT / "STATUS.md"
POLICY_PATH = ROOT / "planning" / "EV4_RTAQ_SSOT_GUARD_POLICY.json"

TARGET_TASK = "RTAQ-0010"
NEXT_TASK = "RTAQ-0011"
TARGET_PR = 84
TARGET_LEDGER_RECORD = "LEDGER-0021"
MIN_PENDING_DEPTH = 4


class PlanError(AssertionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task.get("task_id"): task for task in queue.get("tasks", [])}


def pending_tasks(queue: dict[str, Any]) -> list[str]:
    return [
        task.get("task_id")
        for task in queue.get("tasks", [])
        if task.get("status") == "pending"
    ]


def ledger_task_refs(ledger: dict[str, Any]) -> set[str]:
    return {record.get("task_ref") for record in ledger.get("ledger_records", [])}


def ledger_record_ids(ledger: dict[str, Any]) -> set[str]:
    return {record.get("record_id") for record in ledger.get("ledger_records", [])}


def assert_policy_boundary(policy: dict[str, Any]) -> None:
    if policy.get("status") != "active":
        raise PlanError("RTAQ SSOT guard policy must be active before state sync")
    gates = policy.get("mandatory_gates", {})
    required = [
        "full_untruncated_source_required",
        "no_mutation_from_partial_or_truncated_snippets",
        "allowlisted_semantic_patch_required",
        "completed_historical_tasks_preserved",
        "old_ledger_records_append_only",
        "json_state_files_must_remain_pretty_printed",
        "diff_budget_required_before_pr_creation",
    ]
    missing = [name for name in required if gates.get(name) is not True]
    if missing:
        raise PlanError("missing required SSOT gates: " + ", ".join(missing))


def assert_status_boundary(status_text: str) -> None:
    required = [
        f"latest_completed_task: {TARGET_TASK}",
        f"latest_completed_pr: {TARGET_PR}",
        f"next_executable_task: {NEXT_TASK}",
        "real_submitted_packet_present: false",
        "pilot_allowed_to_start: false",
        "readiness_claims_upgraded: false",
        "ci_success_claim_boundary: repository checks only",
    ]
    missing = [item for item in required if item not in status_text]
    if missing:
        raise PlanError("STATUS.md is missing expected RTAQ-0011 boundary text: " + ", ".join(missing))


def build_plan(queue: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    tasks = task_by_id(queue)
    if TARGET_TASK not in tasks:
        raise PlanError(f"{TARGET_TASK} not found in queue")
    if NEXT_TASK not in tasks:
        raise PlanError(f"{NEXT_TASK} not found in queue")

    target = tasks[TARGET_TASK]
    refs = ledger_task_refs(ledger)
    record_ids = ledger_record_ids(ledger)
    pending = pending_tasks(queue)

    if target.get("status") == "merged":
        if target.get("completed_pr") != TARGET_PR:
            raise PlanError(f"{TARGET_TASK} is merged but completed_pr is not {TARGET_PR}")
        if TARGET_TASK not in refs:
            raise PlanError(f"{TARGET_TASK} is merged but ledger record is missing")
        if len(pending) < MIN_PENDING_DEPTH:
            raise PlanError("pending depth is below policy minimum after sync")
        return {
            "mode": "already_synced",
            "target_task": TARGET_TASK,
            "next_task": NEXT_TASK,
            "pending_depth": len(pending),
            "allowed_changes_remaining": [],
        }

    if target.get("status") != "pending":
        raise PlanError(f"unexpected {TARGET_TASK} status: {target.get('status')}")

    if TARGET_TASK in refs:
        raise PlanError(f"ledger already records {TARGET_TASK} while queue still marks it pending")
    if TARGET_LEDGER_RECORD in record_ids:
        raise PlanError(f"{TARGET_LEDGER_RECORD} already exists while queue still marks {TARGET_TASK} pending")

    planned_pending = [task_id for task_id in pending if task_id != TARGET_TASK]
    if len(planned_pending) < MIN_PENDING_DEPTH:
        planned_pending.append("RTAQ-0014")

    return {
        "mode": "sync_required",
        "target_task": TARGET_TASK,
        "next_task": NEXT_TASK,
        "allowed_changes": [
            "mark RTAQ-0010 merged with completed_pr 84",
            "append LEDGER-0021 for RTAQ-0010 / PR #84",
            "restore pending depth with RTAQ-0014 if still below four",
            "update STATUS.md only with stable final state",
            "add reconciliation note only if needed",
        ],
        "blocked_changes": [
            "rewrite completed historical queue tasks outside RTAQ-0010",
            "rewrite existing ledger records instead of append-only update",
            "synthesize queue or ledger from truncated tool output",
            "merge transient in_pr/executing state to main",
            "treat CI success as responsive correctness evidence",
        ],
        "current_pending_depth_after_target_completion": len([task_id for task_id in pending if task_id != TARGET_TASK]),
        "planned_pending_tasks": planned_pending,
    }


def main() -> int:
    queue = load_json(QUEUE_PATH)
    ledger = load_json(LEDGER_PATH)
    policy = load_json(POLICY_PATH)
    status_text = STATUS_PATH.read_text(encoding="utf-8")

    assert_policy_boundary(policy)
    assert_status_boundary(status_text)
    plan = build_plan(queue, ledger)

    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    print("RTAQ-0011 deterministic state-sync plan check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
