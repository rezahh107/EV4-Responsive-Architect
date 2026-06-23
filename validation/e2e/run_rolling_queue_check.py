#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
SCHEMA = ROOT / "schemas" / "ev4-responsive-rolling-queue.schema.json"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    queue = load(QUEUE)
    schema = load(SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(queue)

    tasks = queue["tasks"]
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        fail("task IDs must be unique")

    if queue["active_cycle"]["task_order"] != ids[:5]:
        fail("active cycle order must match first five tasks")

    if [task["cycle_position"] for task in tasks[:5]] != [1, 2, 3, 4, 5]:
        fail("first five tasks must have positions 1..5")

    if tasks[4]["task_type"] != "queue_refresh":
        fail("fifth task must refresh the queue")

    if len([task for task in tasks if task["status"] == "in_progress"]) > 1:
        fail("only one task may be in progress")

    if queue["queue_status"] == "active":
        pending = [task for task in tasks if task["status"] == "pending"]
        if len(pending) < queue["controller_policy"]["minimum_pending_tasks"]:
            fail("active queue must keep four pending tasks")

    by_id = {task["task_id"]: task for task in tasks}
    for task in tasks:
        if task["critique_required"] is not True:
            fail(f"{task['task_id']} must require critique")
        if task["status"] == "blocked" and not task.get("blocker_reason"):
            fail(f"{task['task_id']} is blocked without reason")
        if task["task_type"] == "real_evidence_execution" and not task["requires_real_evidence"]:
            fail(f"{task['task_id']} real evidence task must require evidence")
        for dep in task["dependencies"]:
            if dep not in by_id:
                fail(f"{task['task_id']} has unknown dependency {dep}")
            if ids.index(dep) >= ids.index(task["task_id"]):
                fail(f"{task['task_id']} dependency order is invalid")

    required_claims = {
        "production_ready",
        "release_ready",
        "live_render_validated",
        "export_json_validated",
        "accessibility_passed",
        "sample_packet_used_as_real_evidence"
    }
    missing = required_claims - set(queue["forbidden_claims"])
    if missing:
        fail("queue missing required boundary claims")

    print("Rolling queue validation passed")


if __name__ == "__main__":
    main()
