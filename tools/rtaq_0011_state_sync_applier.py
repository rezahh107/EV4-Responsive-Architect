#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS_PATH = ROOT / "STATUS.md"
CONTROL_STATE_PATH = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"
PLAN_CHECK = ROOT / "validation" / "e2e" / "run_rtaq_0011_state_sync_plan_check.py"

TARGET_TASK = "RTAQ-0010"
NEXT_TASK = "RTAQ-0011"
TARGET_PR = 84
RETIRED_QUEUE_STATUS = "retired_as_execution_driver"
CHECKPOINT_ONLY_POLICY = "bounded_checkpoints_only_not_append_every_merge"


class ApplyError(AssertionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ApplyError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def tasks_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list):
        raise ApplyError("planning/EV4_ROLLING_QUEUE.json tasks must be a list")
    return {task.get("task_id"): task for task in tasks if isinstance(task, dict)}


def is_retired_archive_control_state(control_state: dict[str, Any]) -> bool:
    return (
        control_state.get("rolling_queue_execution_status") == RETIRED_QUEUE_STATUS
        and control_state.get("rolling_queue_authority") == "historical_reconciled_archive"
        and control_state.get("checkpoint_only_loop_policy") == CHECKPOINT_ONLY_POLICY
        and control_state.get("queue_reconciliation_required_before_queue_driver") is False
    )


def is_retired_archive_state(queue: dict[str, Any], control_state: dict[str, Any], status_text: str) -> bool:
    tasks = tasks_by_id(queue)
    target = tasks.get(TARGET_TASK, {})
    next_task = tasks.get(NEXT_TASK, {})
    active_cycle = queue.get("active_cycle")
    return (
        is_retired_archive_control_state(control_state)
        and queue.get("queue_status") == "complete"
        and isinstance(active_cycle, dict)
        and active_cycle.get("cycle_status") == "complete"
        and target.get("status") == "merged"
        and target.get("completed_pr") == TARGET_PR
        and next_task.get("status") == "superseded"
        and "rolling_queue_reconciliation_required: false" in status_text
        and "checkpoint_only_loop_policy: bounded checkpoints only; not append every merged PR" in status_text
        and "real_submitted_packet_present: false" in status_text
        and "pilot_allowed_to_start: false" in status_text
        and "readiness_claims_upgraded: false" in status_text
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile or no-op the historical RTAQ-0011 state sync helper.")
    parser.add_argument("--write", action="store_true", help="Legacy flag retained for compatibility; ignored in retired queue state.")
    args = parser.parse_args()

    if not PLAN_CHECK.is_file():
        raise ApplyError("plan check is missing")

    queue = load_json(QUEUE_PATH)
    control_state = load_json(CONTROL_STATE_PATH)
    status_text = STATUS_PATH.read_text(encoding="utf-8")

    if is_retired_archive_state(queue, control_state, status_text):
        print(
            "RTAQ-0011 state sync already reconciled: rolling queue execution is retired, "
            "RTAQ-0010 is merged, and RTAQ-0011 is superseded. No --write changes are required."
        )
        return 0

    raise ApplyError(
        "RTAQ-0011 state sync applier found a non-retired or inconsistent state. "
        "Run validation/e2e/run_rtaq_0011_state_sync_plan_check.py and reconcile the current control model before writing state."
    )


if __name__ == "__main__":
    raise SystemExit(main())
