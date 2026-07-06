#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS_PATH = ROOT / "STATUS.md"
CONTROL_STATE_PATH = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"

TARGET_TASK = "RTAQ-0010"
NEXT_TASK = "RTAQ-0011"
TARGET_PR = 84
RETIRED_QUEUE_STATUS = "retired_as_execution_driver"
CHECKPOINT_ONLY_POLICY = "bounded_checkpoints_only_not_append_every_merge"


class PlanError(AssertionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task.get("task_id"): task for task in queue.get("tasks", [])}


def assert_status_boundary(status_text: str) -> None:
    required = [
        "rolling_queue_execution_status: retired_as_execution_driver",
        "rolling_queue_reconciliation_required: false",
        "checkpoint_only_loop_policy: bounded checkpoints only; not append every merged PR",
        "real_submitted_packet_present: false",
        "pilot_allowed_to_start: false",
        "readiness_claims_upgraded: false",
        "ci_success_claim_boundary: repository checks only; not responsive correctness evidence",
    ]
    missing = [item for item in required if item not in status_text]
    if missing:
        raise PlanError("STATUS.md is missing expected retired-queue boundary text: " + ", ".join(missing))


def assert_control_state(control_state: dict[str, Any]) -> None:
    expected = {
        "rolling_queue_execution_status": RETIRED_QUEUE_STATUS,
        "rolling_queue_authority": "historical_reconciled_archive",
        "checkpoint_only_loop_policy": CHECKPOINT_ONLY_POLICY,
        "queue_reconciliation_required_before_queue_driver": False,
    }
    mismatches = [
        f"{key}={control_state.get(key)!r}"
        for key, expected_value in expected.items()
        if control_state.get(key) != expected_value
    ]
    if mismatches:
        raise PlanError("automation control state no longer matches the retired rolling-queue model: " + ", ".join(mismatches))


def build_plan(queue: dict[str, Any], control_state: dict[str, Any], status_text: str) -> dict[str, Any]:
    assert_control_state(control_state)
    assert_status_boundary(status_text)

    tasks = task_by_id(queue)
    target = tasks.get(TARGET_TASK)
    next_task = tasks.get(NEXT_TASK)
    if not isinstance(target, dict):
        raise PlanError(f"{TARGET_TASK} not found in queue")
    if not isinstance(next_task, dict):
        raise PlanError(f"{NEXT_TASK} not found in queue")
    if queue.get("queue_status") != "complete":
        raise PlanError("rolling queue must remain complete in retired archive state")
    if queue.get("active_cycle", {}).get("cycle_status") != "complete":
        raise PlanError("active cycle must remain complete in retired archive state")
    if target.get("status") != "merged" or target.get("completed_pr") != TARGET_PR:
        raise PlanError(f"{TARGET_TASK} must remain merged with completed_pr {TARGET_PR}")
    if next_task.get("status") != "superseded":
        raise PlanError(f"{NEXT_TASK} must remain superseded when rolling queue execution is retired")

    return {
        "mode": "already_reconciled_queue_retired",
        "target_task": TARGET_TASK,
        "target_task_status": target.get("status"),
        "target_completed_pr": target.get("completed_pr"),
        "next_task": NEXT_TASK,
        "next_task_status": next_task.get("status"),
        "rolling_queue_execution_status": RETIRED_QUEUE_STATUS,
        "checkpoint_only_loop_policy": CHECKPOINT_ONLY_POLICY,
        "ledger_record_required": False,
        "write_sync_required": False,
        "allowed_changes_remaining": [],
    }


def main() -> int:
    plan = build_plan(
        load_json(QUEUE_PATH),
        load_json(CONTROL_STATE_PATH),
        STATUS_PATH.read_text(encoding="utf-8"),
    )
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    print("RTAQ-0011 deterministic state-sync plan check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
