#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
LEDGER_PATH = ROOT / "planning" / "EV4_RUN_LEDGER.json"
STATUS_PATH = ROOT / "STATUS.md"
PLAN_CHECK = ROOT / "validation" / "e2e" / "run_rtaq_0011_state_sync_plan_check.py"

TARGET_TASK = "RTAQ-0010"
NEXT_TASK = "RTAQ-0011"
NEW_PENDING_TASK = "RTAQ-0014"
TARGET_PR = 84
TARGET_MERGE_SHA = "83a6487b07853219b39d20a08ef03c062941aa14"
TARGET_LEDGER_RECORD = "LEDGER-0021"
TARGET_CREATED_AT_UTC = "2026-06-27T14:26:36Z"
MIN_PENDING_DEPTH = 4


class ApplyError(AssertionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tasks_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task.get("task_id"): task for task in queue.get("tasks", [])}


def pending_task_ids(queue: dict[str, Any]) -> list[str]:
    return [
        task.get("task_id")
        for task in queue.get("tasks", [])
        if task.get("status") == "pending"
    ]


def assert_expected_prestate(queue: dict[str, Any], ledger: dict[str, Any], status_text: str) -> None:
    tasks = tasks_by_id(queue)
    if TARGET_TASK not in tasks:
        raise ApplyError(f"{TARGET_TASK} missing from queue")
    if tasks[TARGET_TASK].get("status") != "pending":
        raise ApplyError(f"{TARGET_TASK} must be pending before this sync")
    if tasks[TARGET_TASK].get("completed_pr") is not None:
        raise ApplyError(f"{TARGET_TASK} already has completed_pr")

    if NEW_PENDING_TASK in tasks:
        raise ApplyError(f"{NEW_PENDING_TASK} already exists before this sync")

    ledger_records = ledger.get("ledger_records", [])
    if any(record.get("record_id") == TARGET_LEDGER_RECORD for record in ledger_records):
        raise ApplyError(f"{TARGET_LEDGER_RECORD} already exists")
    if any(record.get("task_ref") == TARGET_TASK for record in ledger_records):
        raise ApplyError(f"ledger already contains {TARGET_TASK}")

    required_status = [
        f"latest_completed_task: {TARGET_TASK}",
        f"latest_completed_pr: {TARGET_PR}",
        f"latest_completed_merge_sha: {TARGET_MERGE_SHA}",
        f"next_executable_task: {NEXT_TASK}",
        "real_submitted_packet_present: false",
        "pilot_allowed_to_start: false",
        "readiness_claims_upgraded: false",
        "ci_success_claim_boundary: repository checks only",
    ]
    missing = [item for item in required_status if item not in status_text]
    if missing:
        raise ApplyError("STATUS.md missing required boundary/prestate text: " + ", ".join(missing))


def complete_target_task(task: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(task)
    updated["status"] = "merged"
    updated["completed_pr"] = TARGET_PR
    updated["completion"] = {
        "run_id": "merge-final-rtaq-0010-pr-84",
        "status": "merged",
        "artifacts": [
            "docs/25_QUEUE_REFRESH_AUDIT_RTAQ_0010.md",
            "STATUS.md",
            "planning/RTAQ_0010_MERGE_FINAL_SYNC_NOTE.md",
        ],
        "critique_findings": [
            "RTAQ-0010 completed the second bounded-batch queue refresh audit in PR #84.",
            "The PR intentionally preserved evidence, pilot, readiness, production, release, live-render, export, accessibility, and pixel-validation boundaries.",
            "CI success remains repository-check evidence only, not responsive correctness evidence.",
        ],
        "boundary": "No submitted evidence, Issue #8 mutation, real pilot execution, readiness claim upgrade, production/release claim upgrade, live-render claim, export validation claim, accessibility pass claim, or pixel-validation claim.",
    }
    return updated


def new_pending_task() -> dict[str, Any]:
    return {
        "task_id": NEW_PENDING_TASK,
        "cycle_position": 14,
        "task_type": "repo_sync",
        "status": "pending",
        "title": "Pending depth reserve after RTAQ-0010 sync",
        "objective": "Maintain minimum pending depth after RTAQ-0010 merge-final sync without starting evidence, pilot, readiness, release, production, live-render, export, accessibility, or pixel-validation work.",
        "allowed_work": [
            "Audit post-sync queue depth after RTAQ-0011 through RTAQ-0013 remain pending.",
            "Patch queue, ledger, status, or docs only if bounded synchronization drift is found.",
            "Use branch, PR, CI, and critique workflow before merge.",
        ],
        "forbidden_work": [
            "Do not create submitted evidence.",
            "Do not modify Issue #8.",
            "Do not run or authorize the real pilot.",
            "Do not upgrade readiness, production, release, live-render, export, accessibility, or pixel claims.",
        ],
        "requires_real_evidence": False,
        "expected_artifacts": [
            "Bounded queue/status sync patch if drift is found",
            "CI result",
        ],
        "acceptance_criteria": [
            "Minimum pending depth remains visible.",
            "RTAQ-0011 remains the next executable task until started in a later run.",
            "Evidence-pending and pilot-blocked boundaries remain visible.",
        ],
        "critique_required": True,
        "dependencies": [
            TARGET_TASK,
        ],
    }


def sync_queue(queue: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(queue)
    order = updated["active_cycle"]["task_order"]
    if NEW_PENDING_TASK not in order:
        order.append(NEW_PENDING_TASK)

    updated_tasks = []
    for task in updated["tasks"]:
        if task.get("task_id") == TARGET_TASK:
            updated_tasks.append(complete_target_task(task))
        else:
            updated_tasks.append(task)
    updated_tasks.append(new_pending_task())
    updated["tasks"] = updated_tasks

    pending_after = pending_task_ids(updated)
    if len(pending_after) < MIN_PENDING_DEPTH:
        raise ApplyError(f"pending depth after queue sync is {len(pending_after)} < {MIN_PENDING_DEPTH}")
    if pending_after[:4] != ["RTAQ-0011", "RTAQ-0012", "RTAQ-0013", "RTAQ-0014"]:
        raise ApplyError("unexpected pending order after queue sync: " + ", ".join(pending_after))
    return updated


def sync_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(ledger)
    updated["ledger_records"].append(
        {
            "record_id": TARGET_LEDGER_RECORD,
            "run_id": "merge-final-rtaq-0010-pr-84",
            "task_ref": TARGET_TASK,
            "run_type": "queue_refresh",
            "status": "merged",
            "pr_number": TARGET_PR,
            "merge_sha": TARGET_MERGE_SHA,
            "ci_conclusion": "success",
            "created_at_utc": TARGET_CREATED_AT_UTC,
            "artifacts": [
                {"path": "docs/25_QUEUE_REFRESH_AUDIT_RTAQ_0010.md", "artifact_type": "doc", "status": "created"},
                {"path": "STATUS.md", "artifact_type": "status", "status": "updated"},
                {"path": "planning/RTAQ_0010_MERGE_FINAL_SYNC_NOTE.md", "artifact_type": "doc", "status": "created"},
            ],
            "critique_summary": [
                "PR #84 completed the second bounded-batch queue refresh audit without creating submitted evidence or changing Issue #8.",
                "The audit preserved pilot, readiness, release, production, live-render, export, accessibility, and pixel-validation boundaries.",
                "This sync records merge-final state only and does not start RTAQ-0011.",
                "CI success is repository-check evidence only, not responsive correctness evidence.",
            ],
            "boundary_assertions": [
                "no_real_evidence_created",
                "no_real_pilot_run",
                "no_production_claim",
                "no_release_claim",
                "no_live_render_claim",
                "no_export_validation_claim",
                "no_accessibility_pass_claim",
                "sample_not_used_as_real",
                "no_issue_8_mutation",
                "no_readiness_claim_upgrade",
            ],
            "next_queue_effect": "RTAQ-0011 is next executable and remains pending; RTAQ-0014 restores minimum pending depth.",
        }
    )
    return updated


def sync_status(status_text: str) -> str:
    replacements = {
        "  - validation/e2e/run_rtaq_ssot_guard_check.py\n": "  - validation/e2e/run_rtaq_ssot_guard_check.py\n  - validation/e2e/run_rtaq_0011_state_sync_plan_check.py\n",
        "pending_tasks:\n  - RTAQ-0011\n  - RTAQ-0012\n  - RTAQ-0013\n": "pending_tasks:\n  - RTAQ-0011\n  - RTAQ-0012\n  - RTAQ-0013\n  - RTAQ-0014\n",
        "pending_depth_exception: \"RTAQ-0010 audit PR #84 intentionally preserved existing queue IDs and moved replacement proposals to non-authoritative backlog candidates; next bounded task must reconcile pending-depth reserve placeholders before starting evidence or pilot work.\"\n": "pending_depth_status: restored_to_minimum_four_after_rtaq_0010_sync\n",
        "reason: \"RTAQ-0010 PR #84 is merge-final synced in STATUS. RTAQ-0011 is next executable and must reconcile queue-depth drift before any new evidence, pilot, readiness, or production work.\"\n": "reason: \"RTAQ-0010 PR #84 is merge-final synced in queue, ledger, and STATUS. RTAQ-0011 is next executable and remains pending; no evidence, pilot, readiness, or production work has started.\"\n",
    }
    updated = status_text
    for old, new in replacements.items():
        if old not in updated:
            raise ApplyError("STATUS.md expected text not found for replacement")
        updated = updated.replace(old, new, 1)
    return updated


def assert_no_historical_queue_rewrite(original: dict[str, Any], updated: dict[str, Any]) -> None:
    original_tasks = tasks_by_id(original)
    updated_tasks = tasks_by_id(updated)
    allowed = {TARGET_TASK, NEW_PENDING_TASK}
    for task_id, original_task in original_tasks.items():
        if task_id in allowed:
            continue
        if updated_tasks.get(task_id) != original_task:
            raise ApplyError(f"unexpected historical queue rewrite: {task_id}")


def assert_append_only_ledger(original: dict[str, Any], updated: dict[str, Any]) -> None:
    original_records = original.get("ledger_records", [])
    updated_records = updated.get("ledger_records", [])
    if updated_records[: len(original_records)] != original_records:
        raise ApplyError("ledger is not append-only")
    if len(updated_records) != len(original_records) + 1:
        raise ApplyError("ledger must append exactly one record")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the deterministic RTAQ-0011 state sync from a full checkout.")
    parser.add_argument("--write", action="store_true", help="Write queue, ledger, and STATUS changes. Default is read-only dry-run.")
    args = parser.parse_args()

    if not PLAN_CHECK.is_file():
        raise ApplyError("plan check is missing")

    queue = load_json(QUEUE_PATH)
    ledger = load_json(LEDGER_PATH)
    status_text = STATUS_PATH.read_text(encoding="utf-8")

    assert_expected_prestate(queue, ledger, status_text)

    updated_queue = sync_queue(queue)
    updated_ledger = sync_ledger(ledger)
    updated_status = sync_status(status_text)

    assert_no_historical_queue_rewrite(queue, updated_queue)
    assert_append_only_ledger(ledger, updated_ledger)

    changed_paths = [
        str(QUEUE_PATH.relative_to(ROOT)),
        str(LEDGER_PATH.relative_to(ROOT)),
        str(STATUS_PATH.relative_to(ROOT)),
    ]

    if args.write:
        dump_json(QUEUE_PATH, updated_queue)
        dump_json(LEDGER_PATH, updated_ledger)
        STATUS_PATH.write_text(updated_status, encoding="utf-8")
        print("RTAQ-0011 state sync written:")
    else:
        print("RTAQ-0011 state sync dry-run passed. Would update:")
    for path in changed_paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
