#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS = ROOT / "STATUS.md"

EXPECTED_CONTROL = {
    "schema": "ev4-automation-control-state@1.0.0",
    "project": "EV4 Responsive Architect",
    "current_execution_driver": "bounded_material_checkpoint_guard",
    "rolling_queue_authority": "historical_non_authoritative_until_reconciled",
    "rolling_queue_path": "planning/EV4_ROLLING_QUEUE.json",
    "status_path": "STATUS.md",
    "latest_material_checkpoint": "PR #112 RTAQ-0029 responsive intake decision guard",
    "latest_checkpoint_guard": "PR #113 RTAQ-0030 bounded foundation checkpoint guard",
    "queue_drift_acknowledged": True,
    "queue_reconciliation_required_before_queue_driver": True,
    "checkpoint_only_loop_policy": "bounded_checkpoints_only_not_append_every_merge",
    "next_action_policy": "material_objective_only",
}

REQUIRED_FORBIDDEN_NEXT_ACTIONS = {
    "create_checkpoint_only_pr_for_every_merge",
    "treat_stale_rolling_queue_as_current_driver",
    "invent_rtaq_task_without_planning_contract",
    "upgrade_evidence_pilot_readiness_or_release_claims",
}

REQUIRED_BOUNDARY_CLAIMS = {
    "real_submitted_packet_present": False,
    "pilot_allowed_to_start": False,
    "readiness_claims_upgraded": False,
    "production_ready": False,
    "release_ready": False,
    "responsive_correctness_claim_upgraded": False,
}

REQUIRED_STATUS_MARKERS = {
    "foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR",
    "automation_control_state: planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver: bounded_material_checkpoint_guard",
    "rolling_queue_authority: historical_non_authoritative_until_reconciled",
    "rolling_queue_reconciliation_required: true",
    "checkpoint_only_loop_policy: bounded checkpoints only; not append every merged PR",
    "next_action_policy: material objectives only; checkpoint refresh only when material checkpoint changes",
    "validation/e2e/run_automation_control_state_check.py",
    "real_submitted_packet_present: false",
    "pilot_allowed_to_start: false",
    "readiness_claims_upgraded: false",
    "production_ready: false",
    "prompt_pack_release_ready: false",
    "pilot_execution_scope: not_allowed",
}

QUEUE_DRIFT_TASKS = {"RTAQ-0019", "RTAQ-0020", "RTAQ-0021", "RTAQ-0022"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing required JSON file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def task_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        fail("rolling queue tasks must be a list")
    result: dict[str, dict[str, Any]] = {}
    for task in tasks:
        task_id = task.get("task_id")
        if not isinstance(task_id, str):
            fail("rolling queue task is missing string task_id")
        if task_id in result:
            fail(f"duplicate rolling queue task_id: {task_id}")
        result[task_id] = task
    return result


def rolling_queue_has_known_drift(queue: dict[str, Any]) -> bool:
    if queue.get("queue_status") != "active":
        return False
    tasks = task_by_id(queue)
    return all(tasks.get(task_id, {}).get("status") == "pending" for task_id in QUEUE_DRIFT_TASKS)


def assert_control_state(control: dict[str, Any], queue: dict[str, Any]) -> None:
    for key, expected in EXPECTED_CONTROL.items():
        if control.get(key) != expected:
            fail(f"automation control state mismatch for {key}: {control.get(key)!r} != {expected!r}")

    forbidden = control.get("forbidden_next_actions")
    if not isinstance(forbidden, list):
        fail("forbidden_next_actions must be a list")
    missing_forbidden = REQUIRED_FORBIDDEN_NEXT_ACTIONS - set(forbidden)
    if missing_forbidden:
        fail("automation control state missing forbidden next actions: " + ", ".join(sorted(missing_forbidden)))

    boundary_claims = control.get("boundary_claims")
    if not isinstance(boundary_claims, dict):
        fail("boundary_claims must be an object")
    for key, expected in REQUIRED_BOUNDARY_CLAIMS.items():
        if boundary_claims.get(key) is not expected:
            fail(f"boundary claim mismatch for {key}: expected {expected!r}")

    if rolling_queue_has_known_drift(queue):
        if control["rolling_queue_authority"] != "historical_non_authoritative_until_reconciled":
            fail("stale active rolling queue cannot be the current execution authority")
        if control["current_execution_driver"] == "rolling_queue":
            fail("rolling queue cannot be current driver while RTAQ-0019..0022 remain pending")
        if control["queue_reconciliation_required_before_queue_driver"] is not True:
            fail("queue reconciliation must be required before restoring queue driver authority")


def assert_status_text(status_text: str) -> None:
    missing = [marker for marker in sorted(REQUIRED_STATUS_MARKERS) if marker not in status_text]
    if missing:
        fail("STATUS.md missing automation control markers: " + ", ".join(missing))

    forbidden_patterns = [
        r"current_execution_driver:\s*rolling_queue\b",
        r"rolling_queue_authority:\s*authoritative\b",
        r"checkpoint_only_loop_policy:\s*append every merged PR\b",
        r"pilot_allowed_to_start:\s*true\b",
        r"real_submitted_packet_present:\s*true\b",
        r"readiness_claims_upgraded:\s*true\b",
        r"production_ready:\s*true\b",
        r"prompt_pack_release_ready:\s*true\b",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, status_text):
            fail(f"STATUS.md contains forbidden automation/boundary marker matching {pattern}")


def run_self_tests() -> None:
    queue_with_drift = {
        "queue_status": "active",
        "tasks": [{"task_id": task_id, "status": "pending"} for task_id in sorted(QUEUE_DRIFT_TASKS)],
    }
    valid_control = dict(EXPECTED_CONTROL)
    valid_control["forbidden_next_actions"] = sorted(REQUIRED_FORBIDDEN_NEXT_ACTIONS)
    valid_control["boundary_claims"] = dict(REQUIRED_BOUNDARY_CLAIMS)
    assert_control_state(valid_control, queue_with_drift)

    invalid_control = dict(valid_control)
    invalid_control["rolling_queue_authority"] = "authoritative"
    try:
        assert_control_state(invalid_control, queue_with_drift)
    except AssertionError:
        pass
    else:
        fail("self-test failed: authoritative stale rolling queue was accepted")

    invalid_control = dict(valid_control)
    invalid_control["current_execution_driver"] = "rolling_queue"
    try:
        assert_control_state(invalid_control, queue_with_drift)
    except AssertionError:
        pass
    else:
        fail("self-test failed: stale rolling queue driver was accepted")

    valid_status = "\n".join(sorted(REQUIRED_STATUS_MARKERS))
    assert_status_text(valid_status)

    invalid_status = valid_status + "\npilot_allowed_to_start: true\n"
    try:
        assert_status_text(invalid_status)
    except AssertionError:
        pass
    else:
        fail("self-test failed: pilot_allowed_to_start true was accepted")


def main() -> int:
    run_self_tests()
    control = load_json(CONTROL)
    queue = load_json(QUEUE)
    if not STATUS.is_file():
        fail("missing STATUS.md")
    assert_control_state(control, queue)
    assert_status_text(STATUS.read_text(encoding="utf-8"))
    print("automation control state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
