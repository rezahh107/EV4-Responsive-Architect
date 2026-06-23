#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
SCHEMA = ROOT / "schemas" / "ev4-responsive-rolling-queue.schema.json"
TERMINAL_STATUSES = {"completed", "merged", "skipped", "superseded", "cancelled"}
NON_TERMINAL_STATUSES = {"pending", "in_progress", "blocked", "stale_in_progress"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise AssertionError(message)


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.path])]


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = schema_errors(payload, schema)
    if errors:
        fail(f"queue must validate against rolling queue schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_errors(payload, schema):
        fail(f"malformed queue unexpectedly passed schema validation: {label}")


def assert_schema_negative_paths(queue: dict[str, Any], schema: dict[str, Any]) -> None:
    pending_with_completion = copy.deepcopy(queue)
    pending_task = next(task for task in pending_with_completion["tasks"] if task["status"] == "pending")
    pending_task["completion"] = {
        "run_id": "negative-test",
        "status": "completed",
        "artifacts": ["invalid"],
        "critique_findings": ["pending task must not carry completion evidence"],
        "boundary": "invalid"
    }
    assert_schema_invalid(pending_with_completion, schema, "pending task with completion")

    completed_without_completion = copy.deepcopy(queue)
    completed_task = next(task for task in completed_without_completion["tasks"] if task["status"] in TERMINAL_STATUSES)
    completed_task.pop("completion", None)
    assert_schema_invalid(completed_without_completion, schema, "terminal task without completion")

    malformed_refresh = copy.deepcopy(queue)
    fifth_task = next(task for task in malformed_refresh["tasks"] if task["cycle_position"] == 5)
    fifth_task["task_type"] = "validator_hardening"
    assert_schema_invalid(malformed_refresh, schema, "fifth task is not queue_refresh")


def expected_task_id(position: int) -> str:
    return f"RQ-{position:04d}"


def main() -> None:
    queue = load(QUEUE)
    schema = load(SCHEMA)
    assert_schema_valid(queue, schema)
    assert_schema_negative_paths(queue, schema)

    policy = queue["controller_policy"]
    tasks = queue["tasks"]
    ids = [task["task_id"] for task in tasks]

    if len(ids) != len(set(ids)):
        fail("task IDs must be unique")

    for position, task_id in enumerate(ids, start=1):
        if task_id != expected_task_id(position):
            fail(f"task IDs must be contiguous and monotonic; expected {expected_task_id(position)}, got {task_id}")

    task_order = queue["active_cycle"]["task_order"]
    if task_order != ids:
        fail("active cycle order must match the complete task sequence")

    for expected_position, task in enumerate(tasks, start=1):
        if task["cycle_position"] != expected_position:
            fail(f"{task['task_id']} cycle_position must be {expected_position}")

    refresh_n = policy["refresh_every_nth_task"]
    for task in tasks:
        if task["cycle_position"] % refresh_n == 0 and task["task_type"] != "queue_refresh":
            fail(f"{task['task_id']} is every {refresh_n}th task and must refresh the queue")

    if len([task for task in tasks if task["status"] == "in_progress"]) > 1:
        fail("only one task may be in progress")

    if queue["queue_status"] == "active":
        pending = [task for task in tasks if task["status"] == "pending"]
        if len(pending) < policy["minimum_pending_tasks"]:
            fail("active queue must keep four pending tasks")

    by_id = {task["task_id"]: task for task in tasks}
    for task in tasks:
        status = task["status"]
        completion = task.get("completion")

        if task["critique_required"] is not True:
            fail(f"{task['task_id']} must require critique")
        if status == "blocked" and not task.get("blocker_reason"):
            fail(f"{task['task_id']} is blocked without reason")
        if status in TERMINAL_STATUSES and not completion:
            fail(f"{task['task_id']} is terminal without completion evidence")
        if status in NON_TERMINAL_STATUSES and completion:
            fail(f"{task['task_id']} is non-terminal but carries completion evidence")
        if completion:
            if completion.get("status") not in TERMINAL_STATUSES:
                fail(f"{task['task_id']} completion status must be terminal")
            if not completion.get("artifacts"):
                fail(f"{task['task_id']} completion must list artifacts")
            if not completion.get("critique_findings"):
                fail(f"{task['task_id']} completion must list critique findings")
            if not completion.get("boundary"):
                fail(f"{task['task_id']} completion must preserve boundary notes")
        if task["task_type"] == "real_evidence_execution" and not task["requires_real_evidence"]:
            fail(f"{task['task_id']} real evidence task must require evidence")
        for dep in task["dependencies"]:
            if dep not in by_id:
                fail(f"{task['task_id']} has unknown dependency {dep}")
            if ids.index(dep) >= ids.index(task["task_id"]):
                fail(f"{task['task_id']} dependency order is invalid")
            if status in TERMINAL_STATUSES and by_id[dep]["status"] not in TERMINAL_STATUSES:
                fail(f"{task['task_id']} completed with non-terminal dependency {dep}")

    required_claims = {
        "production_ready",
        "release_ready",
        "live_render_validated",
        "export_json_validated",
        "accessibility_passed",
        "sample_packet_used_as_real_evidence",
    }
    missing = required_claims - set(queue["forbidden_claims"])
    if missing:
        fail("queue missing required boundary claims")

    print("Rolling queue validation passed")


if __name__ == "__main__":
    main()
