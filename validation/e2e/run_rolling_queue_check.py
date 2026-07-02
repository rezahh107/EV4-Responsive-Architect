#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from run_task_quality_gate_check import main as run_task_quality_gate
from run_cross_critique_stub_check import main as run_cross_critique_stub

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
QUEUE_SCHEMA = ROOT / "schemas" / "ev4-responsive-rolling-queue.schema.json"
CONTROL = ROOT / "planning" / "EV4_QUEUE_CONTROL_PLANE.json"
CONTROL_SCHEMA = ROOT / "schemas" / "ev4-responsive-queue-control-plane.schema.json"
TERMINAL_STATUSES = {"completed", "merged", "skipped", "superseded", "cancelled"}
NON_TERMINAL_STATUSES = {"pending", "in_progress", "blocked", "stale_in_progress"}
ARTIFICIAL_TERMS = (
    "pending depth reserve",
    "keepalive",
    "status-only",
    "merge-final sync",
    "artificial reserve",
    "bookkeeping-only",
    "merge-final-only",
)


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise AssertionError(message)


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.path])]


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = schema_errors(payload, schema)
    if errors:
        fail(f"{label} must validate against schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_errors(payload, schema):
        fail(f"malformed payload unexpectedly passed schema validation: {label}")


def assert_schema_negative_paths(queue: dict[str, Any], schema: dict[str, Any]) -> None:
    pending_with_completion = copy.deepcopy(queue)
    pending_task = next(task for task in pending_with_completion["tasks"] if task["status"] == "pending")
    pending_task["completion"] = {
        "run_id": "negative-test",
        "status": "completed",
        "artifacts": ["invalid"],
        "critique_findings": ["pending task must not carry completion evidence"],
        "boundary": "invalid",
    }
    assert_schema_invalid(pending_with_completion, schema, "pending task with completion")

    terminal_tasks = [task for task in queue["tasks"] if task["status"] in TERMINAL_STATUSES]
    if terminal_tasks:
        completed_without_completion = copy.deepcopy(queue)
        completed_task = next(task for task in completed_without_completion["tasks"] if task["status"] in TERMINAL_STATUSES)
        completed_task.pop("completion", None)
        assert_schema_invalid(completed_without_completion, schema, "terminal task without completion")

    old_policy = copy.deepcopy(queue)
    old_policy["controller_policy"] = {
        "one_task_per_run": True,
        "critique_same_task": True,
        "small_in_scope_fixes_allowed": True,
        "ci_required_for_repo_changes": True,
        "minimum_pending_tasks": 4,
        "refresh_every_nth_task": 5,
        "real_pilot_requires_submitted_packet_and_readiness_pass": True,
    }
    assert_schema_invalid(old_policy, schema, "old one-task-per-run policy")


def expected_task_id(prefix: str, position: int) -> str:
    return f"{prefix}-{position:04d}"


def task_prefix(task_id: str) -> str:
    return task_id.split("-", 1)[0]


def assert_control_plane(control: dict[str, Any], control_schema: dict[str, Any]) -> None:
    assert_schema_valid(control, control_schema, "queue control plane")
    truth = control["truth_boundary"]
    if not all(truth.values()):
        fail("queue truth boundary values must all remain true")
    runtime = control["runtime_state_policy"]
    if runtime["queue_file"] != "planning/EV4_ROLLING_QUEUE.json":
        fail("control plane queue_file must reference the active queue")
    if runtime["ledger_file"] != "planning/EV4_RUN_LEDGER.json":
        fail("control plane ledger_file must reference the active run ledger")
    lease = control["lease_policy"]
    if lease["max_active_leases"] != 1:
        fail("lease policy must allow only one active lease")
    if not lease["optimistic_locking_required"]:
        fail("lease policy must require optimistic locking")
    transitions = control["transition_policy"]
    allowed = {(item["from"], item["to"]) for item in transitions["allowed_transitions"]}
    forbidden = {(item["from"], item["to"]) for item in transitions["forbidden_transitions"]}
    required_forbidden = {("pending", "completed"), ("awaiting_external", "completed"), ("blocked", "completed")}
    if required_forbidden - forbidden:
        fail("control plane missing required forbidden transitions")
    if allowed & forbidden:
        fail("a transition cannot be both allowed and forbidden")
    codes = {item["code"] for item in control["diagnostic_registry"]}
    required_codes = {"RQ_SCHEMA_INVALID", "RQ_ILLEGAL_TRANSITION", "RQ_LEASE_CONFLICT", "RQ_PR_STATE_DRIFT", "RQ_CI_ACTION_REQUIRED", "RQ_EVIDENCE_STATE_MISMATCH"}
    if required_codes - codes:
        fail("control plane missing required diagnostics")
    if not all(control["implementation_boundary"].values()):
        fail("implementation boundary values must remain true")


def assert_objective_policy(policy: dict[str, Any]) -> None:
    if policy["run_granularity"] != "primary_objective":
        fail("runs must be scoped to a primary objective")
    for key in [
        "same_scope_completion_allowed",
        "critique_same_objective",
        "small_in_scope_fixes_allowed",
        "ci_required_for_repo_changes",
        "fixed_ordinal_refresh_forbidden",
        "artificial_reserve_tasks_forbidden",
        "status_only_prs_forbidden",
        "same_head_ci_recovery_required",
        "real_pilot_requires_submitted_packet_and_readiness_pass",
    ]:
        if policy[key] is not True:
            fail(f"controller policy must enforce {key}")
    if policy["minimum_actionable_tasks"] != 4 or policy["refresh_when_actionable_below"] != 4:
        fail("actionable planning horizon must refresh below four real tasks")


def main() -> None:
    queue = load(QUEUE)
    queue_schema = load(QUEUE_SCHEMA)
    control = load(CONTROL)
    control_schema = load(CONTROL_SCHEMA)

    assert_schema_valid(queue, queue_schema, "rolling queue")
    assert_schema_negative_paths(queue, queue_schema)
    assert_control_plane(control, control_schema)
    if run_task_quality_gate() != 0:
        fail("task quality gate validation failed")
    if run_cross_critique_stub() != 0:
        fail("cross-critique stub validation failed")

    policy = queue["controller_policy"]
    assert_objective_policy(policy)
    tasks = queue["tasks"]
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        fail("task IDs must be unique")
    prefixes = {task_prefix(task_id) for task_id in ids}
    if len(prefixes) != 1:
        fail("active queue must use a single task-id prefix")
    prefix = prefixes.pop()
    if prefix not in {"RQ", "RTAQ"}:
        fail("active queue task-id prefix must be RQ or RTAQ")
    for position, task_id in enumerate(ids, start=1):
        expected = expected_task_id(prefix, position)
        if task_id != expected:
            fail(f"task IDs must be contiguous and monotonic; expected {expected}, got {task_id}")
    if queue["active_cycle"]["task_order"] != ids:
        fail("active cycle order must match the complete task sequence")
    for expected_position, task in enumerate(tasks, start=1):
        if task["cycle_position"] != expected_position:
            fail(f"{task['task_id']} cycle_position must be {expected_position}")
    if len([task for task in tasks if task["status"] == "in_progress"]) > 1:
        fail("only one task may be in progress")
    if queue["queue_status"] == "active":
        actionable = [task for task in tasks if task["status"] in {"pending", "in_progress", "blocked", "stale_in_progress"}]
        if len(actionable) < policy["minimum_actionable_tasks"]:
            fail("active queue must keep four actionable bounded objectives")
    by_id = {task["task_id"]: task for task in tasks}
    for task in tasks:
        status = task["status"]
        completion = task.get("completion")
        title_objective = f"{task['title']} {task['objective']}".lower()
        if status in {"pending", "in_progress", "blocked", "stale_in_progress"} and any(term in title_objective for term in ARTIFICIAL_TERMS):
            fail(f"{task['task_id']} is an executable artificial bookkeeping task")
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
            if completion.get("status") != status:
                fail(f"{task['task_id']} completion status '{completion.get('status')}' must match task status '{status}'")
        if task["task_type"] == "real_evidence_execution" and not task["requires_real_evidence"]:
            fail(f"{task['task_id']} real evidence task must require evidence")
        for dep in task["dependencies"]:
            if dep not in by_id:
                fail(f"{task['task_id']} has unknown dependency {dep}")
            if ids.index(dep) >= ids.index(task["task_id"]):
                fail(f"{task['task_id']} dependency order is invalid")
            if status in TERMINAL_STATUSES and by_id[dep]["status"] not in TERMINAL_STATUSES:
                fail(f"{task['task_id']} completed with non-terminal dependency {dep}")
    required_claims = {"production_ready", "release_ready", "live_render_validated", "export_json_validated", "accessibility_passed", "sample_packet_used_as_real_evidence"}
    missing = required_claims - set(queue["forbidden_claims"])
    if missing:
        fail("queue missing required boundary claims")
    print("Rolling queue validation passed")


if __name__ == "__main__":
    main()
